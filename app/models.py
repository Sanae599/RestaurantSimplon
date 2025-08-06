from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey


# https://docs-sqlalchemy.readthedocs.io/ko/latest/orm/cascades.html
# https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
# https://github.com/fastapi/sqlmodel/issues/213?utm_source=chatgpt.com%3Futm_source%3Dchatgpt.com


# USER
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    role: str  # admin, employee, client
    password_hashed: str
    address_user: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    orders: List["Order"] = Relationship(back_populates="user", cascade_delete=True)

# PRODUCT
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    unit_price: float
    category: str
    description: Optional[str] = None
    stock: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    order_items: List["OrderItem"] = Relationship(back_populates="product", cascade_delete=True)

# ORDER
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_amount: float
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    user: Optional[User] = Relationship(back_populates="orders")

    delivery: Optional["Delivery"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            # delete all children 
            "cascade": "all, delete-orphan",
            # 1 delivery appartien à 1 seul order
            "single_parent": True,
            # relation one one
            "uselist": False
        }
    )

    order_items: List["OrderItem"] = Relationship(back_populates="order", cascade_delete=True)

# DELIVERY
class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(foreign_key="order.id", unique=True, nullable=False)
    address_delivery: str
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    order: Order = Relationship(back_populates="delivery")

# ORDER ITEMS 
class OrderItem(SQLModel, table=True):
    order_id: int = Field(
        sa_column=Column(ForeignKey("order.id", ondelete="CASCADE"), primary_key=True)
    )
    product_id: int = Field(
        sa_column=Column(ForeignKey("product.id", ondelete="CASCADE"), primary_key=True)
    )
    quantity: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    order: Optional[Order] = Relationship(back_populates="order_items")
    product: Optional[Product] = Relationship(back_populates="order_items")
