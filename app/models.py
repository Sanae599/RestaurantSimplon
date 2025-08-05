from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

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
    
    orders: List["Order"] = Relationship(back_populates="user")

# PRODUCT
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    unit_price: float
    category: str
    description: Optional[str] = None
    stock: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    order_items: List["OrderItem"] = Relationship(back_populates="product")

# DELIVERY
class Delivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    address_delivery: str
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    
    orders: List["Order"] = Relationship(back_populates="delivery")

# ORDER
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total_amount: float
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    delivery_id: Optional[int] = Field(default=None, foreign_key="delivery.id")
    
    user: Optional[User] = Relationship(back_populates="orders")
    delivery: Optional[Delivery] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")

# ORDER ITEMS
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float
    
    order: Optional[Order] = Relationship(back_populates="order_items")
    product: Optional[Product] = Relationship(back_populates="order_items")
