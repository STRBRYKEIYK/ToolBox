"""
WorkBox API Schemas
==================

This module defines the Pydantic models (schemas) for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime


# USER SCHEMAS
class UserBase(BaseModel):
    """Base schema for User data"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str  # In production, use EmailStr
    is_admin: bool = False
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new User"""
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    """Schema for User responses"""
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True


# INVENTORY SCHEMAS
class InventoryBase(BaseModel):
    """Base schema for Inventory data"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)


class InventoryCreate(InventoryBase):
    """Schema for creating a new Inventory item"""
    pass


class InventoryResponse(InventoryBase):
    """Schema for Inventory responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


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
    inventory: InventoryResponse

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
