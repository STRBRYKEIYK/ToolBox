# Multi-User Deployment Guide

This guide provides step-by-step instructions for deploying the WorkBox application in a multi-user environment where the application can be accessed from different computers and networks.

## Architecture Overview

The multi-user deployment consists of:

1. **MySQL Database Server** - Centralized database accessible from all clients
2. **FastAPI Application Server** - Serving the API and WebSocket endpoints
3. **Client Workstations** - Computers accessing the application

## Step 1: Setting Up the Database Server

### 1.1 Install MySQL Server

On your designated database server:

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install mysql-server
```

**CentOS/RHEL:**

```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

**Windows:**

- Download and install MySQL from [mysql.com](https://dev.mysql.com/downloads/installer/)

### 1.2 Configure MySQL for Remote Access

Edit the MySQL configuration file:

**Linux (Ubuntu/Debian):**

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

Find the line with `bind-address` and change it to:

```cnf
bind-address = 0.0.0.0
```

**Windows:**

- Edit `my.ini` in the MySQL installation directory
- Set `bind-address = 0.0.0.0`

Restart MySQL:

```bash
sudo systemctl restart mysql
```

### 1.3 Create Database and User

```bash
sudo mysql
```

```sql
CREATE DATABASE workbox_db;
CREATE USER 'workbox_user'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON workbox_db.* TO 'workbox_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

### 1.4 Configure Firewall

Allow MySQL port (3306):

**Ubuntu/Debian:**

```bash
sudo ufw allow 3306/tcp
```

**CentOS/RHEL:**

```bash
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

**Windows:**

- Open Windows Firewall with Advanced Security
- Create a new Inbound Rule for TCP port 3306

## Step 2: Deploying the FastAPI Application Server

### 2.1 Install Python and Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2.2 Set Up the Application

```bash
# Clone or copy the application files
git clone <repository-url> workbox
cd workbox

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Configure Database Connection

Run the connection manager script:

```bash
python manage_connection.py update
```

Enter your database server details when prompted:

- Host: [Your MySQL server IP address]
- Port: 3306 (default)
- Username: workbox_user
- Password: [The password you set]
- Database: workbox_db

### 2.4 Initialize the Database

```bash
python init_db.py
```

### 2.5 Configure API Server to Listen on All Interfaces

The application is already configured to listen on all network interfaces (`0.0.0.0`) in `main.py`.

### 2.6 Allow API Port in Firewall

```bash
sudo ufw allow 8000/tcp
```

### 2.7 Start the Application Server

For testing:

```bash
python main.py
```

For production (using Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 "WorkBox.api.server:app"
```

To run as a service (systemd):

1. Create a service file:

```bash
sudo nano /etc/systemd/system/workbox.service
```

1. Add the following content:

``` info
[Unit]
Description=WorkBox Inventory Management System
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/workbox
ExecStart=/path/to/workbox/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 "WorkBox.api.server:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

1. Start the service:

```bash
sudo systemctl start workbox
sudo systemctl enable workbox
```

## Step 3: Client Setup

For each client machine that needs to access the WorkBox application:

1. Access the API via HTTP:
   - Open a web browser and navigate to `http://[server-ip]:8000/docs`
   - Use the interactive API documentation to interact with the system

2. Access the WebSocket endpoints:
   - Connect to `ws://[server-ip]:8000/ws` from your client applications

## Step 4: Verify Multi-User Functionality

1. Run the connection test from each client:

```bash
python manage_connection.py test
```

   Check multi-user configuration:

```bash
python manage_connection.py check
```

## Troubleshooting

If clients can't connect to the database:

1. Verify MySQL is listening on all interfaces:

```bash
sudo netstat -tulpn | grep mysql
```

Should show: `0.0.0.0:3306`

   Test network connectivity:

```bash
telnet [database-server-ip] 3306
```

   Check user permissions:

```sql
SELECT user, host FROM mysql.user WHERE user = 'workbox_user';
```

Should include an entry with host '%'

1. Check database server logs:

```bash
sudo tail -f /var/log/mysql/error.log
```

1. Use the connection manager to diagnose issues:

```bash
python manage_connection.py
```
