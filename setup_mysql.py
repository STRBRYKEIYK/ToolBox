#!/usr/bin/env python3
"""
MySQL Setup Helper for WorkBox
============================

This script helps you set up your MySQL credentials for the WorkBox application.
Run this script to test your MySQL connection and create the .env file.

Usage:
    # On Windows with Python in PATH:
    python setup_mysql.py
    
    # On Windows if Python is not in PATH:
    "C:/Program Files/Python313/python.exe" setup_mysql.py
    
    # On Linux/Mac:
    ./setup_mysql.py
"""

import pymysql
from pymysql import Error


def test_mysql_connection(host, port, user, password):
    """Test MySQL connection with provided credentials"""
    try:
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
        )
        if connection:
            print("✅ MySQL connection successful!")
            connection.close()
            return True
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False


def create_env_file(host, port, user, password, db_name):
    """Create .env file with database credentials"""
    env_content = f"""# WorkBox Database Configuration
DB_HOST={host}
DB_PORT={port}
DB_USER={user}
DB_PASSWORD={password}
DB_NAME={db_name}

# Database connection URL (includes connection pooling parameters)
DATABASE_URL=mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4

# API Server Configuration
API_HOST=0.0.0.0  # Listen on all network interfaces
API_PORT=8000
API_WORKERS=4     # Number of worker processes (set to CPU cores)
DEBUG=False       # Set to True for development

# Security Settings
SECRET_KEY=changethissecretkey  # Change this to a secure random string
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("✅ Created .env file with your database credentials")
    print("📁 File location: .env")


def main():
    print("🔧 WorkBox MySQL Setup Helper")
    print("=" * 40)

    # Get MySQL credentials from user
    print("\nPlease enter your MySQL connection details:")

    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port = input("MySQL Port (default: 3306): ").strip() or "3306"
    user = input("MySQL Username (default: root): ").strip() or "root"
    password = input("MySQL Password: ").strip()
    db_name = input("Database Name (default: workbox_db): ").strip() or "workbox_db"

    print("\n🔍 Testing connection to MySQL...")
    print(f"   Host: {host}")
    print(f"   User: {user}")
    print(f"   Database: {db_name}")

    if test_mysql_connection(host, port, user, password):
        create_env_file(host, port, user, password, db_name)
        print("\n🎉 Setup complete! You can now run:")
        print("   python init_db.py")
        print("   python main.py")
    else:
        print("\n❌ Please check your MySQL credentials and try again.")
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your username and password")
        print("3. Check if you need to create the database first")
        print("4. Try connecting with MySQL Workbench or command line first")


if __name__ == "__main__":
    main()
