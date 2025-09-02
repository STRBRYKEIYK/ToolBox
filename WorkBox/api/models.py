"""
WorkBox Database Models
======================

This module defines the SQLAlchemy ORM models for all database tables.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    """User model represents employees and administrators in the system."""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    access_level = Column(String(20), nullable=False, default="user")  # admin, user, etc.
    password_salt = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    twofa_salt = Column(String(100), nullable=True)
    twofa_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")


class Inventory(Base):
    """Inventory model represents materials and products for metal fabrication."""
    __tablename__ = "inventory"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_name = Column(String(100), index=True, nullable=False)
    brand = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)  # consumables, equipment, etc.
    location = Column(String(100), nullable=True)  # storage area
    unit = Column(String(20), nullable=True)  # pcs, kg, lengths, etc.
    stock_in = Column(Integer, default=0)
    stock_out = Column(Integer, default=0)
    current_stock = Column(Integer, default=0)  # Calculated as stock_in - stock_out
    min_stock = Column(Integer, default=0)
    deficit = Column(Integer, default=0)  # Calculated as current_stock - min_stock
    status = Column(String(20), default="In Stock")  # Out of Stock, Low in Stock, In Stock
    price_per_unit = Column(Float, nullable=True)
    total_cost = Column(Float, default=0.0)  # Calculated as current_stock × price_per_unit
    last_po_date = Column(DateTime, nullable=True)  # Date of last purchase order
    supplier = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="inventory")


class Order(Base):
    """Order model represents material orders and requisitions."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending, processing, shipped, delivered, cancelled
    total_amount = Column(Float, nullable=False)
    supplier = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """OrderItem model represents individual items within an order."""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of order
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    inventory = relationship("Inventory", back_populates="order_items")


class UserActivity(Base):
    """UserActivity model tracks user actions for audit purposes."""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # login, logout, create, update, delete
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    affected_item = Column(Integer, nullable=True)  # ID of affected inventory item if relevant
    
    # Relationships
    user = relationship("User", back_populates="activities")


class Settings(Base):
    """Settings model for application configuration."""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
