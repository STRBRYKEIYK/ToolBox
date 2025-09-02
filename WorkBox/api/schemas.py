"""
WorkBox API Schemas
==================

This module defines the Pydantic models (schemas) for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# USER SCHEMAS
class UserBase(BaseModel):
    """Base schema for User data"""
    full_name: str = Field(..., min_length=3, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    access_level: str = "user"


class UserCreate(UserBase):
    """Schema for creating a new User"""
    password: str = Field(..., min_length=6)
    twofa_enabled: bool = False


class UserResponse(UserBase):
    """Schema for User responses"""
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# INVENTORY SCHEMAS
class InventoryBase(BaseModel):
    """Base schema for Inventory data"""
    item_name: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    unit: Optional[str] = None
    min_stock: int = Field(default=0, ge=0)
    price_per_unit: Optional[float] = Field(None, gt=0)
    supplier: Optional[str] = None


class InventoryCreate(InventoryBase):
    """Schema for creating a new Inventory item"""
    stock_in: int = Field(default=0, ge=0)
    

class InventoryUpdate(BaseModel):
    """Schema for updating an Inventory item"""
    item_name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    unit: Optional[str] = None
    stock_in: Optional[int] = None
    stock_out: Optional[int] = None
    min_stock: Optional[int] = None
    price_per_unit: Optional[float] = None
    supplier: Optional[str] = None


class InventoryResponse(InventoryBase):
    """Schema for Inventory responses"""
    item_id: int
    stock_in: int
    stock_out: int
    current_stock: int
    deficit: int
    status: str
    total_cost: float
    last_po_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Original InventoryResponse replaced with new one above


# ORDER SCHEMAS
class OrderItemBase(BaseModel):
    """Base schema for Order Item data"""
    inventory_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    """Schema for creating a new Order Item"""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for Order Item responses"""
    id: int
    order_id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    """Base schema for Order data"""
    user_id: int
    status: str = "pending"
    total_amount: float = Field(..., gt=0)
    shipping_address: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating a new Order"""
    items: List[OrderItemCreate]


class OrderResponse(OrderBase):
    """Schema for Order responses"""
    id: int
    order_date: datetime
    order_items: List[OrderItemResponse]

    class Config:
        orm_mode = True


# USER ACTIVITY SCHEMAS
class UserActivityBase(BaseModel):
    """Base schema for User Activity data"""
    user_id: int
    activity_type: str
    description: Optional[str] = None
    ip_address: Optional[str] = None


class UserActivityCreate(UserActivityBase):
    """Schema for creating a new User Activity"""
    pass


class UserActivityResponse(UserActivityBase):
    """Schema for User Activity responses"""
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


# SETTINGS SCHEMAS
class SettingsBase(BaseModel):
    """Base schema for Settings data"""
    key: str = Field(..., min_length=1, max_length=50)
    value: Optional[str] = None
    description: Optional[str] = None


class SettingsCreate(SettingsBase):
    """Schema for creating new Settings"""
    pass


class SettingsResponse(SettingsBase):
    """Schema for Settings responses"""
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True
