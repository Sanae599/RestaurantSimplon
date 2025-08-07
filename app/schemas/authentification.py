from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

# test
class TokenUser(BaseModel):
    email: str
    role: str

class AuthRequest(BaseModel):
    email: EmailStr
    password: str