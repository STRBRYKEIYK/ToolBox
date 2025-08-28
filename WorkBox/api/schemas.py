from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Inventory schemas
class InventoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None


class Inventory(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order schemas
class OrderItemBase(BaseModel):
    inventory_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    inventory: Inventory

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderCreate(OrderBase):
    pass


class Order(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    user: User
    items: List[OrderItem]

    class Config:
        from_attributes = True


# WebSocket message schemas
class InventoryUpdateMessage(BaseModel):
    type: str = "inventory_update"
    inventory_id: int
    name: str
    stock_quantity: int
    price: float


class OrderPlacedMessage(BaseModel):
    type: str = "order_placed"
    order_id: int
    user_id: int
    total_amount: float
    items: List[dict]
