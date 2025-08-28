from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import asyncio
from datetime import datetime

from .database import get_db, create_tables
from .models import (
    User as UserModel,
    Inventory as InventoryModel,
    Order as OrderModel,
    OrderItem as OrderItemModel,
)
from .schemas import (
    User,
    UserCreate,
    Inventory,
    InventoryCreate,
    InventoryUpdate,
    Order,
    OrderCreate,
    InventoryUpdateMessage,
    OrderPlacedMessage,
)

# Initialize FastAPI app
app = FastAPI(title="WorkBox Inventory Management", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove dead connections
                self.active_connections.remove(connection)


# Initialize connection manager
manager = ConnectionManager()


# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


# REST API Endpoints


# Users
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = UserModel(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Inventory
@app.post("/inventory/", response_model=Inventory)
def create_inventory_item(item: InventoryCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    db_item = Inventory(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/inventory/", response_model=List[Inventory])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all inventory items"""
    items = db.query(InventoryModel).offset(skip).limit(limit).all()
    return items


@app.get("/inventory/{item_id}", response_model=Inventory)
def read_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Get inventory item by ID"""
    db_item = db.query(InventoryModel).filter(InventoryModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_item


@app.put("/inventory/{item_id}", response_model=Inventory)
def update_inventory_item(
    item_id: int, item_update: InventoryUpdate, db: Session = Depends(get_db)
):
    """Update inventory item"""
    db_item = db.query(InventoryModel).filter(InventoryModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    for field, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)

    # Broadcast inventory update
    update_message = InventoryUpdateMessage(
        inventory_id=int(db_item.id),
        name=str(db_item.name),
        stock_quantity=int(db_item.stock_quantity),
        price=float(db_item.price),
    )
    asyncio.create_task(manager.broadcast(update_message.dict()))

    return db_item


# Orders
@app.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order and update inventory"""
    # Verify user exists
    db_user = db.query(UserModel).filter(UserModel.id == order.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    total_amount = 0.0
    order_items = []

    # Verify inventory and calculate total
    for item in order.items:
        db_inventory = (
            db.query(InventoryModel)
            .filter(InventoryModel.id == item.inventory_id)
            .first()
        )
        if not db_inventory:
            raise HTTPException(
                status_code=404, detail=f"Inventory item {item.inventory_id} not found"
            )

        if db_inventory.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {db_inventory.name}. Available: {db_inventory.stock_quantity}",
            )

        total_amount += float(db_inventory.price) * item.quantity

        # Create order item
        order_item = OrderItemModel(
            inventory_id=item.inventory_id,
            quantity=item.quantity,
            unit_price=db_inventory.price,
        )
        order_items.append(order_item)

    # Create order
    db_order = OrderModel(
        user_id=order.user_id,
        total_amount=total_amount,
        status="confirmed",
        items=order_items,
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Update inventory stock
    for item in order.items:
        db_inventory = (
            db.query(InventoryModel)
            .filter(InventoryModel.id == item.inventory_id)
            .first()
        )
        if db_inventory:
            # Update stock quantity using direct SQL update
            new_stock = int(db_inventory.stock_quantity) - item.quantity
            db.query(InventoryModel).filter(
                InventoryModel.id == item.inventory_id
            ).update({"stock_quantity": new_stock})
            db.commit()

            # Refresh the object to get updated values
            db.refresh(db_inventory)

            # Broadcast inventory update
            update_message = InventoryUpdateMessage(
                inventory_id=int(db_inventory.id),
                name=str(db_inventory.name),
                stock_quantity=int(db_inventory.stock_quantity),
                price=float(db_inventory.price),
            )
            await manager.broadcast(update_message.dict())

    # Broadcast order placed message
    order_message = OrderPlacedMessage(
        order_id=int(db_order.id),
        user_id=int(db_order.user_id),
        total_amount=float(db_order.total_amount),
        items=[
            {
                "inventory_id": item.inventory_id,
                "name": item.inventory.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in db_order.items
        ],
    )
    await manager.broadcast(order_message.dict())

    return db_order


@app.get("/orders/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(OrderModel).offset(skip).limit(limit).all()
    return orders


@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client (optional)
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
