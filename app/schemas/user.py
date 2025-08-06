import re
from typing import Annotated, Optional
from sqlmodel import SQLModel
from pydantic import EmailStr, ConfigDict, field_validator, StringConstraints
from enumerations import Role
from datetime import datetime

#Création d'un utilisateur (POST)
class UserCreate(SQLModel):
    first_name: Annotated[str, StringConstraints(max_length=50)]
    last_name: Annotated[str, StringConstraints(max_length=50)]
    email: EmailStr
    role: Role
    password_hashed: str # = None ?
    address_user: str
    phone: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True
    )

    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        # le num commence par '0' + 9 chiffres
        if not re.match(r'^0[0-9](\d{2}){4}$', value):
            raise ValueError("Le numéro de téléphone doit être un numéro français valide.")
        return value

    
class UserRead(SQLModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    address_user: str
    phone: str
    created_at: datetime = datetime.now()

class UserUpdate(SQLModel):
    firstname:  Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    lastname:  Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    address_user: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        # le num commence par '0' + 9 chiffres
        if not re.match(r'^0[0-9](\d{2}){4}$', value):
            raise ValueError("Le numéro de téléphone doit être un numéro français valide.")
        return value