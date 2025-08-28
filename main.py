"""
WorkBox - Real-time Inventory Management System
===============================================

A FastAPI-based WebSocket application for real-time inventory management
with MySQL database backend.

Features:
- REST API for CRUD operations on users, inventory, and orders
- WebSocket support for real-time updates
- Automatic inventory updates when orders are placed
- Broadcast notifications to all connected clients

Usage:
    python main.py

The server will start on http://localhost:8000
WebSocket endpoint: ws://localhost:8000/ws
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting WorkBox Inventory Management Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("📖 API documentation: http://localhost:8000/docs")
    print("🔄 Realtime updates enabled")
    print("\nPress Ctrl+C to stop the server\n")

    # When using `reload=True` uvicorn requires an import string like
    # "module:app" instead of the app object. Use the module path so
    # the reload/watchdog machinery works correctly during development.
    uvicorn.run(
        "WorkBox.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
