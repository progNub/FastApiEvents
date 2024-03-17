from pydantic import BaseModel, Field


class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(default=None, min_length=3, max_length=300)


class UserCreate(User):
    password: str = Field(..., min_length=3, max_length=100)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class TokenRefresh(BaseModel):
    access_token: str


class RefreshToken(BaseModel):
    refresh_token: str
