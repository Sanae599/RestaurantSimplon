from datetime import datetime
from typing import Annotated, Optional

from pydantic import ConfigDict, StringConstraints, field_validator
from sqlmodel import SQLModel

from app.enumerations import Category

class ProductCreate(SQLModel):
    """
    Schéma utilisé pour créer un produit (POST).

    Attributs :
    - name (str) : Nom du produit (max. 50 caractères).
    - unit_price (float) : Prix unitaire (doit être > 0).
    - category (Category) : Catégorie du produit (enum).
    - description (str | None) : Description du produit (max. 200 caractères).
    - stock (int) : Stock disponible (doit être ≥ 0).
    - created_at (datetime | None) : Date de création (optionnelle).
    """
    name: Annotated[str, StringConstraints(max_length=50)]
    unit_price: float
    category: Category
    description: Optional[Annotated[str, StringConstraints(max_length=200)]]
    stock: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    @field_validator("unit_price")
    # cls pour accèder à l'attribut de la class
    def validate_unit_price(cls, value: float):
        """
        Valide que le prix unitaire est strictement supérieur à 0.
        """
        if value <= 0:
            raise ValueError("Le prix doit être sup. à 0€")
        return value

    @field_validator("stock")
    def validate_stock(cls, value: int):
        """
        Valide que le stock est supérieur ou égal à 0.
        """
        if value < 0:
            raise ValueError("Le stock ne peut pas être inf. à 0.")
        return value


class ProductRead(SQLModel):
    """
    Schéma utilisé pour lire un produit.

    Attributs :
    - id (int) : Identifiant unique du produit.
    - name (str) : Nom du produit.
    - unit_price (float) : Prix unitaire du produit.
    - category (Category) : Catégorie du produit (enum).
    - description (str) : Description du produit.
    - stock (int) : Stock disponible.
    - created_at (datetime) : Date de création du produit.
    """
    id: int
    name: str
    unit_price: float
    category: Category
    description: str
    stock: int
    created_at: datetime


class ProductUpdate(SQLModel):
    """
    Schéma utilisé pour mettre à jour un produit partiellement (PATCH).

    Attributs optionnels :
    - name (str | None) : Nouveau nom du produit (max. 50 caractères).
    - unit_price (float | None) : Nouveau prix unitaire (doit être > 0).
    - category (Category | None) : Nouvelle catégorie du produit.
    - description (str | None) : Nouvelle description (max. 200 caractères).
    - stock (int | None) : Nouveau stock (doit être ≥ 0).
    """
    name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    unit_price: Optional[float] = None
    category: Optional[Category] = None
    description: Optional[Annotated[str, StringConstraints(max_length=200)]] = None
    stock: Optional[int] = None

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )

    @field_validator("unit_price")
    def validate_unit_price(cls, value: float):
        """
        Valide que le prix unitaire est strictement supérieur à 0 si fourni.
        """
        if value is not None and value <= 0:
            raise ValueError("Le prix doit être sup à 0€")
        return value

    @field_validator("stock")
    def validate_stock(cls, value: int):
        """
        Valide que le stock est supérieur ou égal à 0 si fourni.
        """
        if value is not None and value < 0:
            raise ValueError("Le stock ne peut pas être inf à 0.")
        return value
