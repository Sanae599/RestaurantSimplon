from typing import Optional
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator
#from app.enumerations import Category

#Création d'une commande (POST)
class OrderItemCreate(SQLModel):
    quantity: int

    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True
    )
    @field_validator('quantity')
    def validate_quantity(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("La quantité doit être égal ou sup à 1.")
        return value

class OrderItemRead(SQLModel):
    order_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(str_strip_whitespace=True,use_enum_values=True)

class OrderItemUpdate(SQLModel):
    quantity: Optional[int] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    @field_validator('quantity')
    def validate_quantity(cls, value: int) -> int:
        if value is not None and value <= 0:
            raise ValueError("La quantité doit être égal ou sup à 1.")
        return value
