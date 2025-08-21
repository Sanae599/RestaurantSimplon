from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    """
    Représente un utilisateur de l'application.

    Attributs:
        id (int, optional): Identifiant unique de l'utilisateur.
        first_name (str): Prénom de l'utilisateur.
        last_name (str): Nom de l'utilisateur.
        email (str): Adresse email unique.
        role (str): Rôle de l'utilisateur ('admin', 'employee', 'client').
        password_hashed (str): Mot de passe hashé.
        address_user (str, optional): Adresse de l'utilisateur.
        phone (str, optional): Numéro de téléphone.
        created_at (datetime): Date de création de l'utilisateur.
        orders (List[Order]): Liste des commandes associées à l'utilisateur.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    role: str  # admin, employee, client
    password_hashed: str
    address_user: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    orders: List["Order"] = Relationship(back_populates="user", cascade_delete=True)


class Product(SQLModel, table=True):
    """
    Représente un produit disponible à la vente.

    Attributs:
        id (int, optional): Identifiant unique du produit.
        name (str): Nom du produit.
        unit_price (float): Prix unitaire.
        category (str): Catégorie du produit (entrée, plat, dessert, etc.).
        description (str, optional): Description du produit.
        stock (int): Quantité en stock.
        created_at (datetime): Date de création du produit.
        order_items (List[OrderItem]): Liste des lignes de commande associées.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    unit_price: float
    category: str
    description: Optional[str] = None
    stock: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    order_items: List["OrderItem"] = Relationship(
        back_populates="product", cascade_delete=True
    )

class Order(SQLModel, table=True):
    """
    Représente une commande effectuée par un utilisateur.

    Attributs:
        id (int, optional): Identifiant unique de la commande.
        user_id (int): Identifiant de l'utilisateur ayant passé la commande.
        total_amount (float): Montant total de la commande.
        status (str): Statut de la commande (en préparation, prête, servie).
        created_at (datetime): Date de création de la commande.
        user (User, optional): Utilisateur associé.
        delivery (Delivery, optional): Livraison associée.
        order_items (List[OrderItem]): Liste des produits commandés.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_amount: float
    status: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Optional[User] = Relationship(back_populates="orders")

    delivery: Optional["Delivery"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            # delete all children
            "cascade": "all, delete-orphan",
            # 1 delivery appartient à 1 seul order
            "single_parent": True,
            # relation one one
            "uselist": False,
        },
    )

    order_items: List["OrderItem"] = Relationship(
        back_populates="order", cascade_delete=True
    )

class Delivery(SQLModel, table=True):
    """
    Représente une livraison associée à une commande.

    Attributs:
        id (int, optional): Identifiant unique de la livraison.
        order_id (int, optional): Identifiant de la commande associée.
        address_delivery (str): Adresse de livraison.
        status (str): Statut de la livraison (en cours, délivrée).
        created_at (datetime): Date de création de la livraison.
        order (Order): Commande associée.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(foreign_key="order.id", unique=True, nullable=False)
    address_delivery: str
    status: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    order: Order = Relationship(back_populates="delivery")

class OrderItem(SQLModel, table=True):
    """
    Représente un produit spécifique dans une commande (ligne de commande).

    Attributs:
        order_id (int): Identifiant de la commande.
        product_id (int): Identifiant du produit.
        quantity (int): Quantité commandée.
        created_at (datetime): Date de création de la ligne de commande.
        order (Order, optional): Commande associée.
        product (Product, optional): Produit associé.
    """
    order_id: int = Field(
        sa_column=Column(ForeignKey("order.id", ondelete="CASCADE"), primary_key=True)
    )
    product_id: int = Field(
        sa_column=Column(ForeignKey("product.id", ondelete="CASCADE"), primary_key=True)
    )
    quantity: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    order: Optional[Order] = Relationship(back_populates="order_items")
    product: Optional[Product] = Relationship(back_populates="order_items")
