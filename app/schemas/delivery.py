from typing import Optional, Annotated
from sqlmodel import SQLModel
from pydantic import ConfigDict, field_validator, StringConstraints
from datetime import datetime

#Création d'une livraison (POST)
class DeliveryCreate(SQLModel):
    address_delivery: Annotated[str, StringConstraints(max_length=50)]
    status: str # enum ?
    created_at: datetime

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
    address_delivery: Annotated[str, StringConstraints(max_length=50)]
    status: str # enum ?
    created_at: datetime

    model_config = ConfigDict(str_strip_whitespace=True,use_enum_values=True)

class DeliveryUpdate(SQLModel):
    address_delivery: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    status: Optional[str] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
