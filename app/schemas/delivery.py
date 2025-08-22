from datetime import datetime
from typing import Annotated, Optional

from pydantic import ConfigDict, StringConstraints
from sqlmodel import SQLModel

from app.enumerations import StatusDelivery

class DeliveryCreate(SQLModel):
    """
    Schéma utilisé lors de la création d'une livraison (POST).

    Attributs :
    - order_id (int) : Identifiant de la commande associée.
    - address_delivery (str) : Adresse de livraison (max 200 caractères).
    - status (StatusDelivery) : Statut de la livraison.
    - created_at (datetime | None) : Date de création (optionnelle, peut être définie automatiquement).
    """
    order_id: int
    address_delivery: Annotated[str, StringConstraints(max_length=200)]
    status: StatusDelivery
    created_at: Optional[datetime] = None

    model_config = ConfigDict(
        # supprime espaces
        str_strip_whitespace=True,
        # validation à l'assignation
        validate_assignment=True,
        # use valeurs enum
        use_enum_values=True,
    )


class DeliveryRead(SQLModel):
    """
    Schéma utilisé pour lire/retourner une livraison.

    Attributs :
    - id (int) : Identifiant unique de la livraison.
    - address_delivery (str) : Adresse de livraison.
    - status (StatusDelivery) : Statut de la livraison.
    - created_at (datetime) : Date de création.
    - order_id (int) : Identifiant de la commande associée.
    """
    id: int
    address_delivery: str
    status: StatusDelivery
    created_at: datetime
    order_id: int


class DeliveryUpdate(SQLModel):
    """
    Schéma utilisé pour la mise à jour partielle (PATCH) d'une livraison.

    Attributs optionnels :
    - address_delivery (str | None) : Nouvelle adresse de livraison (max 50 caractères).
    - status (StatusDelivery | None) : Nouveau statut de la livraison.
    """
    address_delivery: Optional[Annotated[str, StringConstraints(max_length=50)]] = None
    status: Optional[StatusDelivery] = None

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, use_enum_values=True
    )
