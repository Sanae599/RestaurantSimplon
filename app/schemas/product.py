from typing import Optional, Annotated
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator, StringConstraints
from datetime import datetime
from enumerations import Category

#Création d'un produit (POST)
class ProductCreate(SQLModel):
    name: Annotated[str, StringConstraints(max_length=50)]
    unit_price: float
    category: Category 
    description: Optional[Annotated[str, StringConstraints(max_length=200)]]
    stock: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True
    )

    @field_validator('unit_price')
    # cls pour accèder à l'attribut de la class
    def validate_unit_price(cls, value: float):
        if value <= 0:
            raise ValueError("Le prix doit être sup à 0€")
        return value
    
    @field_validator('stock')
    def validate_stock(cls, value: int):
        if value < 0:
            raise ValueError("Le stock ne peut pas être inf à 0.")
        return value
    
class ProductRead(SQLModel):
    id: int
    name: str
    unit_price: float
    category: Category
    description: str
    stock: int
    created_at: datetime

class ProductUpdate(SQLModel):
    name: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    unit_price: Optional[float] = None
    category: Optional[Category] = None
    description: Optional[Annotated[str, StringConstraints(max_length=200)]] = None
    stock: Optional[int] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )

    @field_validator('unit_price')
    # cls pour accèder à l'attribut de la class
    def validate_unit_price(cls, value: float):
        if value is not None and value <= 0:
            raise ValueError("Le prix doit être sup à 0€")
        return value
    
    @field_validator('stock')
    def validate_stock(cls, value: int):
        if value is not None and value < 0:
            raise ValueError("Le stock ne peut pas être inf à 0.")
        return value
    
