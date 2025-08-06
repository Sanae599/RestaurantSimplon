from pydantic import EmailStr, BaseModel

# Données envoyées par l'utilisateur pour se connecter
class AuthRequest(BaseModel):
    email: EmailStr
    password: str