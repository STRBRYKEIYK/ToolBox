"""
WorkBox API Server
=================

This module initializes the FastAPI server and integrates all routes.
"""

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import asyncio
from typing import List, Dict

from . import models
from .database import get_db, engine, check_connection
from .schemas import UserCreate, UserResponse, InventoryCreate, InventoryResponse

# Create FastAPI app
app = FastAPI(
    title="WorkBox API",
    description="WorkBox Inventory Management System API",
    version="1.0.0",
)

# Configure CORS for frontend access from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You may want to restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections store
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        """Send a message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, assume connection is dead
                pass


# Initialize connection manager
manager = ConnectionManager()

# Test database connection on startup
@app.on_event("startup")
async def startup_db_client():
    """Run on application startup - verify database connection"""
    if not check_connection():
        print("Failed to connect to the database. Please check your configuration.")
        # In production, you might want to fail startup instead of continuing
        # import sys
        # sys.exit(1)


# API Routes
@app.get("/")
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "WorkBox API is running",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    db_status = "online" if check_connection() else "offline"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": asyncio.datetime.datetime.utcnow().isoformat(),
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                # Parse client message
                message = json.loads(data)
                
                # Process message - you would add your own logic here
                response = {
                    "event": "echo",
                    "data": message
                }
                
                # Broadcast to all clients
                await manager.broadcast(response)
                
            except json.JSONDecodeError:
                # Send error if message isn't valid JSON
                await websocket.send_json({"error": "Invalid JSON format"})
    
    except WebSocketDisconnect:
        # Handle client disconnection
        manager.disconnect(websocket)
        
        # Notify remaining clients about disconnection
        await manager.broadcast({
            "event": "client_disconnected",
            "count": len(manager.active_connections)
        })


# Include API route modules
# These would typically be imported from other files
# from .routes import users, inventory, orders
# app.include_router(users.router)
# app.include_router(inventory.router)
# app.include_router(orders.router)

# For now, let's add some basic routes directly here

# Users
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password="placeholder_hash",  # In a real app, you'd hash the password
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Notify connected clients about new user
    await manager.broadcast({
        "event": "user_created",
        "data": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    })
    
    return db_user


@app.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Inventory
@app.post("/inventory/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    db_inventory = models.Inventory(
        name=inventory.name,
        description=inventory.description,
        price=inventory.price,
        stock_quantity=inventory.stock_quantity
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    
    # Notify connected clients about new inventory
    await manager.broadcast({
        "event": "inventory_created",
        "data": {
            "id": db_inventory.id,
            "name": db_inventory.name,
            "stock_quantity": db_inventory.stock_quantity
        }
    })
    
    return db_inventory


@app.get("/inventory/", response_model=List[InventoryResponse])
async def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all inventory items with pagination"""
    inventory = db.query(models.Inventory).offset(skip).limit(limit).all()
    return inventory


@app.get("/inventory/{inventory_id}", response_model=InventoryResponse)
async def read_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item by ID"""
    db_inventory = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory
