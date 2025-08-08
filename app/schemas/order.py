from typing import Optional, List
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator
from enumerations import Status
from datetime import datetime

class OrderRead(SQLModel):
    id: int
    user_id: int
    total_amount: float
    status: Status
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 

class OrderItemInOrderRead(SQLModel):
    product_id: int
    quantity: int

class OrderReadWithItems(OrderRead):
    items: List[OrderItemInOrderRead] = []
    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(SQLModel):
    status: Optional[Status] = None

class OrderItemCreateInOrder(SQLModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True,
        from_attributes=True,
    )
    

    @field_validator('quantity')
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La quantité doit être ≥ 1.")
        return v

class OrderCreateWithItems(SQLModel):
    # staff peut préciser user_id ; pour un client on l’ignorera et on forcera depuis le token
    user_id: Optional[int] = None
    items: List[OrderItemCreateInOrder]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    @field_validator('items')
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError("La commande doit contenir au moins un article.")
        return v

class OrderPatchWithItems(SQLModel):
    user_id: Optional[int] = None
    status: Optional[Status] = None
    items: Optional[List[OrderItemInOrderRead]] = None
