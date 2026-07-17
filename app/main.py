import hashlib
import time
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app.models import User, RefreshToken
from app.schemas import UserCreate, UserOut, Token
from app.security import hash_password, verify_password
from app.auth import create_access_token, create_refresh_token, decode_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Auth API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# Rate limiting and lockout configuration
LOCKOUT_THRESHOLD = 5
BASE_LOCKOUT_SECONDS = 30

LOGIN_MAX_TOKENS = 10
LOGIN_REFILL_RATE = 0.2
login_buckets = defaultdict(lambda: {"tokens": 10, "last_refill": time.time()})


def is_locked(user: User) -> bool:
    return user.locked_until is not None and user.locked_until > datetime.utcnow()


def check_login_rate_limit(client_ip: str):
    bucket = login_buckets[client_ip]
    now = time.time()
    elapsed = now - bucket["last_refill"]

    bucket["tokens"] = min(LOGIN_MAX_TOKENS, bucket["tokens"] + elapsed * LOGIN_REFILL_RATE)
    bucket["last_refill"] = now

    if bucket["tokens"] < 1:
        raise HTTPException(status_code=429, detail="Too many login attempts from this address.")

    bucket["tokens"] -= 1


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/token", response_model=Token)
def login(
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    check_login_rate_limit(request.client.host)

    user = db.query(User).filter(User.email == form_data.username).first()

    if user and is_locked(user):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")

    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= LOCKOUT_THRESHOLD:
                extra_failures = user.failed_login_attempts - LOCKOUT_THRESHOLD
                lockout_seconds = BASE_LOCKOUT_SECONDS * (2 ** extra_failures)
                user.locked_until = datetime.utcnow() + timedelta(seconds=lockout_seconds)
            db.commit()
        
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Reset counters on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    access_token = create_access_token(user.id)
    refresh_token, expires_at = create_refresh_token(user.id)

    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=expires_at,
    ))
    db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


@app.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    token_hash = hash_token(refresh_token)
    stored_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if stored_token is None or stored_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token invalid or already used")

    # Revoke the old token and issue a new pair
    stored_token.revoked = True
    db.commit()

    user_id = int(payload["sub"])
    new_access_token = create_access_token(user_id)
    new_refresh_token, expires_at = create_refresh_token(user_id)

    db.add(RefreshToken(
        user_id=user_id,
        token_hash=hash_token(new_refresh_token),
        expires_at=expires_at,
    ))
    db.commit()

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)