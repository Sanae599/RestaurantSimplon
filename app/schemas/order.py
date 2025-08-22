from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import SQLModel

from app.enumerations import Status


class OrderRead(SQLModel):
    """
    Schéma utilisé pour lire une commande.

    Attributs :
    - id (int) : Identifiant unique de la commande.
    - user_id (int) : Identifiant de l’utilisateur ayant passé la commande.
    - total_amount (float) : Montant total de la commande.
    - status (Status) : Statut de la commande.
    - created_at (datetime) : Date de création de la commande.
    """
    id: int
    user_id: int
    total_amount: float
    status: Status
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItemInOrderRead(SQLModel):
    """
    Schéma utilisé pour lire un article dans une commande.

    Attributs :
    - product_id (int) : Identifiant du produit.
    - quantity (int) : Quantité commandée.
    """
    product_id: int
    quantity: int


class OrderReadWithItems(OrderRead):
    """
    Schéma utilisé pour lire une commande avec ses articles associés.

    Hérite de OrderRead et ajoute :
    - items (list[OrderItemInOrderRead]) : Liste des articles de la commande.
    """
    items: List[OrderItemInOrderRead] = []
    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(SQLModel):
    """
    Schéma utilisé pour mettre à jour le statut d’une commande (PATCH).

    Attributs optionnels :
    - status (Status | None) : Nouveau statut de la commande.
    """
    status: Optional[Status] = None


class OrderItemCreateInOrder(SQLModel):
    """
    Schéma utilisé pour créer un article dans une commande.

    Attributs :
    - product_id (int) : Identifiant du produit.
    - quantity (int) : Quantité commandée (doit être ≥ 1).
    """
    product_id: int
    quantity: int

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True,
    )

    @field_validator("quantity")
    def validate_quantity(cls, v: int) -> int:
        """
        Valide que la quantité est strictement positive.
        """
        if v <= 0:
            raise ValueError("La quantité doit être ≥ 1.")
        return v


class OrderCreateWithItems(SQLModel):
    """
    Schéma utilisé pour créer une commande avec ses articles.

    Attributs :
    - user_id (int | None) : Identifiant de l’utilisateur (optionnel, forcé depuis le token si client).
    - items (list[OrderItemCreateInOrder]) : Liste des articles de la commande.
    """
    user_id: Optional[int] = None
    items: List[OrderItemCreateInOrder]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    @field_validator("items")
    def validate_items_not_empty(cls, v):
        """
        Valide que la commande contient au moins un article.
        """
        if not v:
            raise ValueError("La commande doit contenir au moins un article.")
        return v


class OrderPatchWithItems(SQLModel):
    """
    Schéma utilisé pour mettre à jour partiellement une commande avec ses articles.

    Attributs optionnels :
    - user_id (int | None) : Identifiant de l’utilisateur associé.
    - status (Status | None) : Nouveau statut de la commande.
    - items (list[OrderItemInOrderRead] | None) : Nouvelle liste d’articles.
    """
    user_id: Optional[int] = None
    status: Optional[Status] = None
    items: Optional[List[OrderItemInOrderRead]] = None
