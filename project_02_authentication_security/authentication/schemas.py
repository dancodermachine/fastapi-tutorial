from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    # Unique constraint to the email column to ensure we can't have duplicate emails in our database
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    hashed_password: str

class UserRead(UserBase):
    id: int