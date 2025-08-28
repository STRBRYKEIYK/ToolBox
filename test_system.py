"""
Test script to demonstrate the WorkBox inventory management system.
This script creates sample data and tests the real-time WebSocket functionality.
"""

import asyncio
import websockets
import json
import requests
import time
import threading
from datetime import datetime

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


def test_rest_api():
    """Test REST API endpoints"""
    print("🧪 Testing REST API endpoints...")

    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Create a test user
    try:
        user_data = {"username": "test_user", "email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created: {user['username']}")
            return user["id"]
        else:
            print(f"❌ Failed to create user: {response.text}")
            return None
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return None


def create_inventory():
    """Create test inventory items"""
    print("📦 Creating test inventory...")

    items = [
        {
            "name": "Test Laptop",
            "description": "Test laptop for demonstration",
            "price": 899.99,
            "stock_quantity": 10,
        },
        {
            "name": "Test Mouse",
            "description": "Test wireless mouse",
            "price": 19.99,
            "stock_quantity": 50,
        },
    ]

    created_items = []
    for item in items:
        try:
            response = requests.post(f"{BASE_URL}/inventory/", json=item)
            if response.status_code == 200:
                inventory_item = response.json()
                created_items.append(inventory_item)
                print(f"✅ Inventory item created: {inventory_item['name']}")
            else:
                print(f"❌ Failed to create inventory: {response.text}")
        except Exception as e:
            print(f"❌ Inventory creation failed: {e}")

    return created_items


def place_test_order(user_id, inventory_items):
    """Place a test order to trigger real-time updates"""
    print("🛒 Placing test order...")

    if len(inventory_items) < 2:
        print("❌ Need at least 2 inventory items for test order")
        return

    order_data = {
        "user_id": user_id,
        "items": [
            {"inventory_id": inventory_items[0]["id"], "quantity": 2},
            {"inventory_id": inventory_items[1]["id"], "quantity": 1},
        ],
    }

    try:
        response = requests.post(f"{BASE_URL}/orders/", json=order_data)
        if response.status_code == 200:
            order = response.json()
            print(
                f"✅ Order placed successfully: ID {order['id']}, Total: ${order['total_amount']:.2f}"
            )
            return order
        else:
            print(f"❌ Failed to place order: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Order placement failed: {e}")
        return None


async def websocket_listener(client_id):
    """WebSocket client that listens for real-time updates"""
    print(f"🔌 WebSocket client {client_id} connecting...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"✅ WebSocket client {client_id} connected")

            # Listen for messages
            async for message in websocket:
                data = json.loads(message)
                timestamp = datetime.now().strftime("%H:%M:%S")

                if data.get("type") == "inventory_update":
                    print(f"📦 [{timestamp}] Client {client_id} - Inventory Update:")
                    print(f"   Item: {data['name']} (ID: {data['inventory_id']})")
                    print(
                        f"   Stock: {data['stock_quantity']} (was {data['stock_quantity'] + 2})"
                    )
                    print(f"   Price: ${data['price']:.2f}")

                elif data.get("type") == "order_placed":
                    print(f"🛒 [{timestamp}] Client {client_id} - Order Placed:")
                    print(f"   Order ID: {data['order_id']}")
                    print(f"   User ID: {data['user_id']}")
                    print(f"   Total: ${data['total_amount']:.2f}")

    except Exception as e:
        print(f"❌ WebSocket client {client_id} error: {e}")


async def run_websocket_clients():
    """Run multiple WebSocket clients to demonstrate real-time updates"""
    print("🚀 Starting WebSocket clients...")

    # Create multiple client tasks
    tasks = []
    for i in range(3):
        task = asyncio.create_task(websocket_listener(i + 1))
        tasks.append(task)

    # Let clients connect
    await asyncio.sleep(2)

    print("✅ All WebSocket clients connected and listening")
    print("📡 They will now receive real-time updates when orders are placed")

    # Keep clients running
    await asyncio.gather(*tasks)


def run_test():
    """Run the complete test suite"""
    print("🎯 Starting WorkBox Test Suite")
    print("=" * 50)

    # Test REST API
    user_id = test_rest_api()
    if not user_id:
        print("❌ REST API test failed, stopping...")
        return

    # Create inventory
    inventory_items = create_inventory()
    if len(inventory_items) < 2:
        print("❌ Inventory creation failed, stopping...")
        return

    # Start WebSocket clients in background
    async def start_clients():
        await run_websocket_clients()

    # Run WebSocket clients in a separate thread
    def run_async_clients():
        asyncio.run(start_clients())

    client_thread = threading.Thread(target=run_async_clients, daemon=True)
    client_thread.start()

    # Wait a moment for clients to connect
    time.sleep(3)

    # Place test orders
    print("\n📋 Placing test orders to trigger real-time updates...")
    for i in range(3):
        print(f"\n--- Test Order {i + 1} ---")
        place_test_order(user_id, inventory_items)
        time.sleep(2)  # Wait between orders

    print("\n✅ Test completed!")
    print("💡 Check the WebSocket client outputs above to see real-time updates")


if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
