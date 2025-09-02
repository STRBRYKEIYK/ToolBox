"""
WorkBox API Server
=================

This module initializes the FastAPI server and integrates all routes.
"""

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from typing import List, Dict

from . import models
from .database import get_db, check_connection
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
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict) -> None:
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
async def startup_db_client() -> None:
    """Run on application startup - verify database connection"""
    if not check_connection():
        print("Failed to connect to the database. Please check your configuration.")
        # In production, you might want to fail startup instead of continuing
        # import sys
        # sys.exit(1)


# API Routes
@app.get("/")
async def root() -> Dict:
    """Root endpoint - API status check"""
    return {
        "message": "WorkBox API is running",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> Dict:
    """Health check endpoint for monitoring"""
    db_status = "online" if check_connection() else "offline"
    
    from datetime import datetime
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
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
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> models.User:
    """Create a new user"""
    # Simple salt/hash generation (in production, use a proper password hashing library)
    import hashlib
    import secrets
    
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + user.password).encode()).hexdigest()
    
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        access_level=user.access_level,
        password_salt=salt,
        password_hash=password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Notify connected clients about new user
    await manager.broadcast({
        "event": "user_created",
        "data": {
            "id": db_user.user_id,
            "username": db_user.username,
            "full_name": db_user.full_name
        }
    })
    
    return db_user


@app.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[models.User]:
    """Get all users with pagination"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)) -> models.User:
    """Get a specific user by ID"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Inventory
@app.post("/inventory/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)) -> models.Inventory:
    """Create a new inventory item"""
    db_inventory = models.Inventory(
        item_name=inventory.item_name,
        brand=inventory.brand,
        category=inventory.category,
        location=inventory.location,
        unit=inventory.unit,
        min_stock=inventory.min_stock,
        price_per_unit=inventory.price_per_unit,
        supplier=inventory.supplier,
        stock_in=inventory.stock_in,
        stock_out=0,
        current_stock=inventory.stock_in
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    
    # Notify connected clients about new inventory
    await manager.broadcast({
        "event": "inventory_created",
        "data": {
            "id": db_inventory.item_id,
            "name": db_inventory.item_name,
            "current_stock": db_inventory.current_stock,
            "status": db_inventory.status
        }
    })
    
    return db_inventory


@app.get("/inventory/", response_model=List[InventoryResponse])
async def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[models.Inventory]:
    """Get all inventory items with pagination"""
    inventory = db.query(models.Inventory).offset(skip).limit(limit).all()
    return inventory


@app.get("/inventory/{inventory_id}", response_model=InventoryResponse)
async def read_inventory_item(inventory_id: int, db: Session = Depends(get_db)) -> models.Inventory:
    """Get a specific inventory item by ID"""
    db_inventory = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory
