from typing import Optional
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator
from enumerations import Status
from datetime import datetime

#Création d'une commande (POST)
class OrderCreate(SQLModel):
    user_id: int
    total_amount: float
    status: Status
    delivery_id: Optional[int] = None

    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True
    )

class OrderRead(SQLModel):
    id: int
    user_id: int
    total_amount: float
    status: Status
    created_at: datetime
    delivery_id: Optional[int] = None

    model_config = ConfigDict(str_strip_whitespace=True,use_enum_values=True)

class OrderUpdate(SQLModel):
    total_amount: Optional[float] = None
    status: Optional[Status] = None
    delivery_id: Optional[int] = None