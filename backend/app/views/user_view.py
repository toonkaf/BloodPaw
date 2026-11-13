from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=1, max_length=128)  # ตรวจมาตรฐานรหัสผ่านใน controller
    full_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    full_name: str = Field(min_length=1)
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str


class TokenView(BaseModel):
    access_token: str
    token_type: str = "bearer"
