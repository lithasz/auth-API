from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr   # EmailStr automatically validates it looks like a real email
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"