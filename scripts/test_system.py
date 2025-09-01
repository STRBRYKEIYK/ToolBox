"""
Test script to demonstrate the WorkBox inventory management system.
This script creates sample data and tests the real-time WebSocket functionality.
"""

import asyncio
import websockets
import json
import requests
import time
import random
import os
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init()

# API base URL
API_URL = "http://localhost:8000"

# WebSocket URL
WS_URL = "ws://localhost:8000/ws"

# Test user credentials
TEST_USER = {
    "username": "test_user",
    "password": "test_password",
    "email": "test@example.com",
    "role": "admin"
}

# Sample products
SAMPLE_PRODUCTS = [
    {
        "name": "Ergonomic Chair",
        "description": "Comfortable office chair with lumbar support",
        "sku": "CHAIR001",
        "category": "Furniture",
        "price": 199.99,
        "cost": 120.00,
        "stock_quantity": 50
    },
    {
        "name": "Standing Desk",
        "description": "Height-adjustable desk for better ergonomics",
        "sku": "DESK001",
        "category": "Furniture",
        "price": 349.99,
        "cost": 200.00,
        "stock_quantity": 30
    },
    {
        "name": "Wireless Keyboard",
        "description": "Bluetooth keyboard with numeric keypad",
        "sku": "KB001",
        "category": "Electronics",
        "price": 59.99,
        "cost": 35.00,
        "stock_quantity": 100
    },
    {
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse",
        "sku": "MOUSE001",
        "category": "Electronics",
        "price": 39.99,
        "cost": 20.00,
        "stock_quantity": 120
    }
]

# Custom print functions
def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * len(text)}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_json(data):
    print(f"{Fore.MAGENTA}{json.dumps(data, indent=2)}{Style.RESET_ALL}")

# API Helper Functions
def create_user():
    """Create a test user if it doesn't exist"""
    try:
        response = requests.post(f"{API_URL}/users/", json=TEST_USER)
        if response.status_code == 200 or response.status_code == 201:
            print_success(f"Created test user: {TEST_USER['username']}")
            return response.json()
        else:
            print_warning(f"User may already exist: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating user: {e}")
        return None

def login_user():
    """Login the test user and get an access token"""
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        response = requests.post(f"{API_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print_success("Login successful")
            return token
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error during login: {e}")
        return None

def create_products(token):
    """Create sample products"""
    created_products = []
    headers = {"Authorization": f"Bearer {token}"}
    
    for product in SAMPLE_PRODUCTS:
        try:
            response = requests.post(f"{API_URL}/products/", json=product, headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                created = response.json()
                created_products.append(created)
                print_success(f"Created product: {product['name']}")
            else:
                print_warning(f"Could not create product {product['name']}: {response.text}")
        except Exception as e:
            print_error(f"Error creating product {product['name']}: {e}")
    
    return created_products

def create_order(token, products):
    """Create a sample order"""
    if not products:
        print_error("No products available to create an order")
        return None
    
    # Create a random order with 1-3 products
    order_items = []
    for _ in range(random.randint(1, min(3, len(products)))):
        product = random.choice(products)
        quantity = random.randint(1, 5)
        order_items.append({
            "product_id": product["id"],
            "quantity": quantity
        })
    
    order_data = {
        "customer_name": "Test Customer",
        "shipping_address": "123 Test St, Test City, 12345",
        "items": order_items
    }
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            print_success("Created order successfully")
            return response.json()
        else:
            print_error(f"Failed to create order: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating order: {e}")
        return None

# WebSocket Client
async def websocket_client(token):
    """Connect to WebSocket and listen for messages"""
    print_header("WebSocket Connection")
    print_info(f"Connecting to {WS_URL}...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            # Send authentication message
            auth_message = {
                "type": "authenticate",
                "token": token
            }
            await websocket.send(json.dumps(auth_message))
            print_success("Connected to WebSocket server")
            
            # Subscribe to inventory updates
            subscribe_message = {
                "type": "subscribe",
                "channel": "inventory_updates"
            }
            await websocket.send(json.dumps(subscribe_message))
            print_info("Subscribed to inventory updates")
            
            # Listen for messages for 30 seconds
            print_info("Listening for real-time updates (30 seconds)...")
            end_time = time.time() + 30
            
            while time.time() < end_time:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    print_header(f"Received WebSocket Message ({datetime.now().strftime('%H:%M:%S')})")
                    print_json(data)
                except asyncio.TimeoutError:
                    # No message received, continue waiting
                    pass
                except Exception as e:
                    print_error(f"Error receiving message: {e}")
                    break
    
    except Exception as e:
        print_error(f"WebSocket connection error: {e}")

# Main test function
async def run_tests():
    """Run the full system test"""
    print_header("WorkBox System Test")
    
    # Create test user
    create_user()
    
    # Login and get token
    token = login_user()
    if not token:
        print_error("Cannot continue without authentication")
        return
    
    # Create sample products
    print_header("Creating Sample Products")
    products = create_products(token)
    
    # Create sample order
    print_header("Creating Sample Order")
    order = create_order(token, products)
    
    # Start WebSocket client
    await websocket_client(token)
    
    print_header("Test Completed")
    print_info("The WorkBox system is working correctly if:")
    print_info("1. Products were created successfully")
    print_info("2. Order was created successfully")
    print_info("3. WebSocket connection was established")
    print_info("4. Real-time updates were received when inventory changed")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
