import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InventoryClient:
    def __init__(self, server_url: str = "ws://localhost:8000/ws"):
        self.server_url = server_url
        self.websocket = None

    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"Connected to {self.server_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def listen_for_updates(self):
        """Listen for real-time updates from the server"""
        if not self.websocket:
            logger.error("Not connected to server")
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if data.get("type") == "inventory_update":
                    logger.info(f"[{timestamp}] 📦 Inventory Update:")
                    logger.info(f"   Item: {data['name']} (ID: {data['inventory_id']})")
                    logger.info(f"   Stock: {data['stock_quantity']}")
                    logger.info(f"   Price: ${data['price']:.2f}")

                elif data.get("type") == "order_placed":
                    logger.info(f"[{timestamp}] 🛒 Order Placed:")
                    logger.info(f"   Order ID: {data['order_id']}")
                    logger.info(f"   User ID: {data['user_id']}")
                    logger.info(f"   Total: ${data['total_amount']:.2f}")
                    logger.info("   Items:")
                    for item in data["items"]:
                        logger.info(
                            f"     - {item['name']} (x{item['quantity']}) @ ${item['unit_price']:.2f}"
                        )

                else:
                    logger.info(f"[{timestamp}] Unknown message: {data}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
        except Exception as e:
            logger.error(f"Error receiving message: {e}")

    async def send_message(self, message: str):
        """Send a message to the server (optional)"""
        if self.websocket:
            try:
                await self.websocket.send(message)
                logger.info(f"Sent message: {message}")
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")


async def main():
    """Main function to run the client"""
    client = InventoryClient()

    # Connect to server
    if await client.connect():
        logger.info("Starting to listen for updates... (Press Ctrl+C to stop)")

        try:
            # Listen for updates
            await client.listen_for_updates()
        except KeyboardInterrupt:
            logger.info("Stopping client...")
        finally:
            await client.disconnect()
    else:
        logger.error("Could not connect to server")


if __name__ == "__main__":
    # Run the client
    asyncio.run(main())
