# WorkBox - Real-time Inventory Management System

A FastAPI-based WebSocket application for real-time inventory management with MySQL database backend.

## Features

- **REST API** for CRUD operations on users, inventory, and orders
- **WebSocket support** for real-time updates
- **Automatic inventory updates** when orders are placed
- **Broadcast notifications** to all connected clients
- **MySQL database** with SQLAlchemy ORM
- **Production-ready** with proper error handling and logging

## Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database:**
   - Create a MySQL database named `workbox_db`
   - Update database credentials in environment variables (see Configuration section)

4. **Initialize the database:**

   ```bash
   python init_db.py
   ```

## Configuration

Create a `.env` file in the project root or set environment variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=workbox_db

# Optional: Database URL (alternative to individual DB settings)
DATABASE_URL=mysql+pymysql://root:password@localhost/workbox_db
```

## Database Schema

The application uses three main tables:

### Users Table

- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `created_at`: Timestamp

### Inventory Table

- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `stock_quantity`: Available stock
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Orders Table

- `id`: Primary key
- `user_id`: Foreign key to Users
- `total_amount`: Order total
- `status`: Order status (pending, confirmed, shipped, delivered)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Order Items Table

- `id`: Primary key
- `order_id`: Foreign key to Orders
- `inventory_id`: Foreign key to Inventory
- `quantity`: Ordered quantity
- `unit_price`: Price at time of order

## Running the Server

Start the FastAPI server:

```bash
python main.py
```

The server will start on `http://localhost:8000` with the following endpoints:

- **REST API**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000/ws`
- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## API Endpoints

### User Endpoints

- `POST /users/` - Create user
- `GET /users/` - List users
- `GET /users/{user_id}` - Get user by ID

### Inventory Endpoints

- `POST /inventory/` - Create inventory item
- `GET /inventory/` - List inventory items
- `GET /inventory/{item_id}` - Get inventory item by ID
- `PUT /inventory/{item_id}` - Update inventory item

### Order Endpoints

- `POST /orders/` - Create order (updates inventory automatically)
- `GET /orders/` - List orders
- `GET /orders/{order_id}` - Get order by ID

### WebSocket Endpoint

- `WS /ws` - Real-time updates endpoint

### Health Check Endpoint

- `GET /health` - Server health status

## Testing with Multiple Clients

1. **Start the server:**

   ```bash
   python main.py
   ```

2. **Run multiple client instances:**

   ```bash
   # Terminal 1
   python client.py

   # Terminal 2
   python client.py

   # Terminal 3
   python client.py
   ```

3. **Test real-time updates:**
   - Use tools like curl, Postman, or the API docs to create orders
   - Watch all connected clients receive real-time updates

## Example Usage

### Create a User

```bash
curl -X POST "http://localhost:8000/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe", "email": "john@example.com"}'
```

### Create Inventory Item

```bash
curl -X POST "http://localhost:8000/inventory/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "High-performance laptop",
       "price": 999.99,
       "stock_quantity": 50
     }'
```

### Place an Order

```bash
curl -X POST "http://localhost:8000/orders/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "items": [
         {"inventory_id": 1, "quantity": 2},
         {"inventory_id": 2, "quantity": 1}
       ]
     }'
```

## WebSocket Message Types

### Inventory Update

```json
{
  "type": "inventory_update",
  "inventory_id": 1,
  "name": "Laptop",
  "stock_quantity": 48,
  "price": 999.99
}
```

### Order Placed

```json
{
  "type": "order_placed",
  "order_id": 1,
  "user_id": 1,
  "total_amount": 2029.98,
  "items": [
    {
      "inventory_id": 1,
      "name": "Laptop",
      "quantity": 2,
      "unit_price": 999.99
    }
  ]
}
```

## Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Clients   │◄──►│  FastAPI Server  │◄──►│   MySQL DB      │
│                 │    │                  │    │                 │
│ - REST API      │    │ - REST Endpoints │    │ - Users         │
│ - WebSocket     │    │ - WebSocket Hub  │    │ - Inventory     │
│ - Real-time     │    │ - Business Logic │    │ - Orders        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Production Deployment

For production deployment:

1. **Set environment variables** for database credentials
2. **Use a production WSGI server** like Gunicorn with Uvicorn workers
3. **Configure CORS** properly for your frontend domains
4. **Set up SSL/TLS** for secure WebSocket connections
5. **Use connection pooling** for database connections
6. **Implement authentication/authorization**
7. **Add rate limiting** and request validation
8. **Set up monitoring** and logging

## Troubleshooting

### Database Connection Issues

- Ensure MySQL server is running
- Verify database credentials
- Check if database exists (run `init_db.py`)

### WebSocket Connection Issues

- Ensure server is running on the correct port
- Check firewall settings
- Verify WebSocket URL format

### Import Errors

- Install all dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct Python environment

## License

This project is open source and available under the MIT License.
