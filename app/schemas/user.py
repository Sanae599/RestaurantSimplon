import re
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr, ConfigDict, field_validator, constr
#from app.enumerations.all_enumerations import Role
from datetime import datetime

#Création d'un utilisateur (POST)
class UserCreate(SQLModel):
    firstname: constr(max_length=50)
    lastname: constr(max_length=50)
    email: EmailStr
    role: Role
    password_hashed: str
    address_user: str
    phone: str
    created_at: datetime


    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        pass
    #    if len(value) < 10:
    #        raise ValueError("Le mot de passe doit contenir au moins 10 caractères")
    #    if not any(c.isupper() for c in value):
    #        raise ValueError("Le mot de passe doit contenir au moins une majuscule")
    #    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
    #        raise ValueError("Le mot de passe doit contenir au moins un caractère spécial")
    #    return value