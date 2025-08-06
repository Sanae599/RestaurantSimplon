from typing import Optional, Annotated
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator, StringConstraints
from datetime import datetime
from enumerations import StatusDelivery

#Création d'une livraison (POST)
class DeliveryCreate(SQLModel):
    order_id: int
    address_delivery: Annotated[str, StringConstraints(max_length=200)]
    status: StatusDelivery


    model_config = ConfigDict(
        # vire espace avant après
        str_strip_whitespace=True,
        # validation à l'init du model et à l'affectation des valeurs
        validate_assignment=True,
        # use enum
        use_enum_values=True
    )

class DeliveryRead(SQLModel):
    id: int
    address_delivery: str
    status: StatusDelivery
    created_at: datetime
    order_id: int

class DeliveryUpdate(SQLModel):
    address_delivery: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    status: Optional[StatusDelivery] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
