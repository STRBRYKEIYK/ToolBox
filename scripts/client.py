import asyncio
import websockets
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkBoxClient:
    """
    Client class for interacting with the WorkBox WebSocket API.
    
    This client connects to the WorkBox server and maintains a WebSocket connection
    for real-time updates.
    """
    
    def __init__(self, url="ws://localhost:8000/ws"):
        """Initialize the client with the WebSocket URL."""
        self.url = url
        self.websocket = None
        self.connected = False
        self.user_id = None
        self.message_callbacks = []
    
    def add_message_callback(self, callback):
        """Add a callback function to be called when messages are received."""
        self.message_callbacks.append(callback)
    
    async def connect(self, user_id=None):
        """Connect to the WebSocket server."""
        self.user_id = user_id
        
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            logger.info(f"Connected to WebSocket server at {self.url}")
            
            # Send authentication if user_id is provided
            if self.user_id:
                await self.authenticate(self.user_id)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self.connected = False
            return False
    
    async def authenticate(self, user_id):
        """Authenticate with the server using a user ID."""
        if not self.connected:
            logger.error("Not connected to server. Cannot authenticate.")
            return False
        
        auth_message = {
            "type": "authenticate",
            "user_id": user_id
        }
        
        await self.websocket.send(json.dumps(auth_message))
        logger.info(f"Sent authentication for user {user_id}")
        return True
    
    async def send_message(self, message_type, data):
        """Send a message to the server."""
        if not self.connected:
            logger.error("Not connected to server. Cannot send message.")
            return False
        
        message = {
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.websocket.send(json.dumps(message))
        logger.info(f"Sent message: {message_type}")
        return True
    
    async def receive_messages(self):
        """Listen for messages from the server."""
        if not self.connected:
            logger.error("Not connected to server. Cannot receive messages.")
            return
        
        try:
            while True:
                message = await self.websocket.recv()
                logger.info(f"Received message: {message}")
                
                # Parse message
                try:
                    parsed = json.loads(message)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse message: {message}")
                    continue
                
                # Call all registered callbacks
                for callback in self.message_callbacks:
                    callback(parsed)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error in receive_messages: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.connected and self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from WebSocket server")
    
    def is_connected(self):
        """Check if the client is connected to the server."""
        return self.connected

# Example usage
async def main():
    client = WorkBoxClient(url="ws://localhost:8000/ws")
    
    # Define a callback for received messages
    def message_callback(message):
        print(f"Received: {message}")
    
    # Register the callback
    client.add_message_callback(message_callback)
    
    # Connect to the server
    await client.connect(user_id="test_user")
    
    # Start listening for messages in the background
    asyncio.create_task(client.receive_messages())
    
    # Send a test message
    await client.send_message("ping", {"message": "Hello from client!"})
    
    # Keep the connection open for a while
    await asyncio.sleep(30)
    
    # Disconnect
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
