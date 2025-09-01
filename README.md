# WorkBox - Real-time Inventory Management System

A FastAPI-based WebSocket application for real-time inventory management with MySQL database backend, designed for multiple users across different networks.

## Features

- **REST API** for CRUD operations on users, inventory, and orders
- **WebSocket support** for real-time updates
- **Automatic inventory updates** when orders are placed
- **Broadcast notifications** to all connected clients
- **Multi-user access** from different networks
- **Connection pooling** for efficient database connections
- **Database migration system** for schema evolution
- **MySQL database** with SQLAlchemy ORM
- **Production-ready** with proper error handling and logging
- **Utility scripts** for setup, testing, and maintenance

## System Requirements

- Python 3.8+
- MySQL Server 5.7+ or 8.0+
- Network connectivity between application and database servers
- pip (Python package manager)

## Network Setup for Multi-User Access

### Database Server Configuration

1. **Configure MySQL for remote access:**

   Edit your MySQL configuration file (my.cnf or my.ini):

   ```ini
   [mysqld]
   bind-address = 0.0.0.0  # Listen on all interfaces
   ```

2. **Create users with network privileges:**

   ```sql
   CREATE USER 'workbox_user'@'%' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON workbox_db.* TO 'workbox_user'@'%';
   FLUSH PRIVILEGES;
   ```

3. **Configure firewall to allow MySQL connections:**
   For Linux (using ufw):

   ```bash
   sudo ufw allow 3306/tcp
   ```

   For Windows:
   - Open Windows Firewall with Advanced Security
   - Create a new inbound rule for port 3306 (TCP)

### Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database configuration:**

   ```bash
   python setup_mysql.py
   ```

   When prompted, enter your database server details:
   - For local development: Use `localhost` as the host
   - For network access: Use the database server's IP address or hostname

4. **Initialize the database:**

   ```bash
   python scripts/init_db.py
   ```

5. **Access the utility tools menu:**

   ```bash
   # On Windows:
   tools.bat
   
   # On any platform:
   python scripts/tools.py
   ```

## Configuration

The application uses a `.env` file for configuration, which is created by the `scripts/setup_mysql.py` script:

```bash
# Database Configuration
DB_HOST=your_db_server_hostname_or_ip
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=workbox_db

# Database connection URL (includes connection pooling parameters)
DATABASE_URL=mysql+pymysql://your_username:your_password@your_db_server:3306/workbox_db?charset=utf8mb4

# API Server Configuration
API_HOST=0.0.0.0  # Listen on all network interfaces
API_PORT=8000
API_WORKERS=4     # Number of worker processes
DEBUG=False       # Set to True for development

# Security Settings
SECRET_KEY=changethissecretkey  # Change this to a secure random string
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database Schema and Migration System

The application uses the SQLAlchemy ORM with a robust schema design and migration support:

### Database Migration

To manage database schema changes:

```bash
# Set up migration system (first time only)
python migrations.py setup

# Create a new migration
python migrations.py create "description_of_changes"

# Apply all pending migrations
python migrations.py apply

# Roll back the last migration
python migrations.py rollback

# View migration history
python migrations.py history
```

### Core Database Tables

#### Users Table

- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `hashed_password`: Securely stored password hash
- `is_admin`: Boolean flag for admin permissions
- `is_active`: Boolean flag for account status
- `created_at`: Timestamp
- `last_login`: Last login timestamp

#### Inventory Table

- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `stock_quantity`: Available stock
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Orders Table

- `id`: Primary key
- `user_id`: Foreign key to Users
- `total_amount`: Order total
- `status`: Order status (pending, processing, shipped, delivered, cancelled)
- `order_date`: Creation timestamp
- `shipping_address`: Shipping address

#### Order Items Table

- `id`: Primary key
- `order_id`: Foreign key to Orders
- `inventory_id`: Foreign key to Inventory
- `quantity`: Ordered quantity
- `price`: Price at time of order

#### User Activity Table

- `id`: Primary key
- `user_id`: Foreign key to Users
- `activity_type`: Type of activity (login, logout, create, update, delete)
- `description`: Activity description
- `timestamp`: Activity timestamp
- `ip_address`: User's IP address

#### Settings Table

- `id`: Primary key
- `key`: Setting key
- `value`: Setting value
- `description`: Setting description
- `updated_at`: Last update timestamp

## Running the Server

Start the FastAPI server with multi-user support:

```bash
python main.py
```

The server will start with the following endpoints:

- API Endpoint: `http://server_ip:8000`
- API Documentation: `http://server_ip:8000/docs`
- WebSocket Endpoint: `ws://server_ip:8000/ws`

## Connection Pooling Details

The application is configured with optimized database connection pooling:

- **Pool size**: 20 connections (configurable)
- **Maximum overflow**: 10 additional connections
- **Pool timeout**: 30 seconds
- **Connection recycling**: Every 3600 seconds (1 hour)
- **Connection validation**: Pre-ping enabled to avoid stale connections
- **Character set**: UTF-8MB4 (full Unicode support)

These settings ensure:

1. Efficient handling of multiple simultaneous users
2. Automatic recovery from connection failures
3. Optimal database server resource utilization
4. Protection against connection leaks

## Troubleshooting Network Connectivity

If clients cannot connect to the database:

1. **Verify MySQL network configuration:**

   ```bash
   # On the database server
   sudo netstat -tulpn | grep mysql
   ```

   Should show MySQL listening on 0.0.0.0:3306 or similar

2. **Check firewall settings:**

   ```bash
   # On the database server (Linux)
   sudo iptables -L | grep 3306
   ```

3. **Test connectivity from client:**

   ```bash
   # From any client machine
   telnet database_server_ip 3306
   ```

4. **Verify user permissions in MySQL:**

   ```sql
   SELECT user, host FROM mysql.user WHERE user = 'your_db_user';
   ```

   Should show an entry with host '%' for network access

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
- Verify database credentials using `scripts/manage_connection.py`
- Check if database exists (run `scripts/init_db.py` or use the tools menu)

### WebSocket Connection Issues

- Ensure server is running on the correct port
- Check firewall settings
- Verify WebSocket URL format
- Use `scripts/network_test.py` to diagnose connectivity issues

### Utility Scripts

The project includes several utility scripts in the `scripts/` directory:

- **tools.py**: Main menu for accessing all utility scripts
- **init_db.py**: Initialize the database schema and sample data
- **setup_mysql.py**: Configure MySQL connection settings
- **manage_connection.py**: Interactive tool to manage database connections
- **network_test.py**: Diagnose network connectivity issues
- **test_system.py**: Run system tests to verify functionality
- **client.py**: Test client for WebSocket connections
- **update_db_connection.py**: Update database connection for network access

Run these scripts directly or use the tools menu (`tools.bat` on Windows)

### Import Errors

- Install all dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct Python environment

## License

This project is open source and available under the MIT License.
