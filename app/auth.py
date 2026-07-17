from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "change-this-to-a-long-random-string-later"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")