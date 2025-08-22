import re
from datetime import datetime
from typing import Annotated, Optional

from pydantic import ConfigDict, EmailStr, StringConstraints, field_validator
from sqlmodel import SQLModel

from app.enumerations import Role

class UserCreate(SQLModel):
    """
    Schéma utilisé pour créer un utilisateur (POST).

    Attributs :
    - first_name (str) : Prénom de l’utilisateur (max. 50 caractères).
    - last_name (str) : Nom de l’utilisateur (max. 50 caractères).
    - email (EmailStr) : Adresse e-mail unique et valide.
    - password (str) : Mot de passe en clair (sera haché côté serveur).
    - address_user (str) : Adresse postale de l’utilisateur.
    - phone (str) : Numéro de téléphone (doit être un numéro français valide).
    - created_at (datetime | None) : Date de création (optionnelle).
    """
    first_name: Annotated[str, StringConstraints(max_length=50)]
    last_name: Annotated[str, StringConstraints(max_length=50)]
    email: EmailStr
    password: str  # = None ?
    address_user: str
    phone: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        """
        Valide que le numéro de téléphone est bien un numéro français.
        Format attendu : commence par 0 suivi de 9 chiffres.
        Exemple valide : 0612345678
        """
        if not re.match(r"^0[0-9](\d{2}){4}$", value):
            raise ValueError(
                "Le numéro de téléphone doit être un numéro français valide."
            )
        return value


class UserRead(SQLModel):
    """
    Schéma utilisé pour lire/retourner un utilisateur.

    Attributs :
    - id (int) : Identifiant unique de l’utilisateur.
    - first_name (str) : Prénom.
    - last_name (str) : Nom.
    - email (EmailStr) : Adresse e-mail.
    - role (Role) : Rôle de l’utilisateur (enum : client, employé, admin).
    - address_user (str) : Adresse postale.
    - phone (str) : Numéro de téléphone.
    - created_at (datetime) : Date de création.
    """
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    address_user: str
    phone: str
    created_at: datetime


class UserUpdate(SQLModel):
    """
    Schéma utilisé pour mettre à jour un utilisateur (PATCH).

    Attributs optionnels :
    - first_name (str | None) : Nouveau prénom (max. 50 caractères).
    - last_name (str | None) : Nouveau nom (max. 50 caractères).
    - email (EmailStr | None) : Nouvelle adresse e-mail.
    - role (Role | None) : Nouveau rôle (enum).
    - address_user (str | None) : Nouvelle adresse postale.
    - phone (str | None) : Nouveau numéro de téléphone (doit être un numéro français valide).
    - password (str | None) : Nouveau mot de passe en clair (sera haché côté serveur).
    """
    first_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    last_name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    address_user: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    @field_validator("phone")
    def validate_phone(cls, value: str) -> str:
        """
        Valide que le numéro de téléphone est bien un numéro français si fourni.
        Format attendu : commence par 0 suivi de 9 chiffres.
        Exemple valide : 0612345678
        """
        if not re.match(r"^0[0-9](\d{2}){4}$", value):
            raise ValueError(
                "Le numéro de téléphone doit être un numéro français valide."
            )
        return value
