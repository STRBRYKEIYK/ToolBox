#!/usr/bin/env python3
"""
WorkBox Connection Manager Script
================================

This script helps manage the database connections for the WorkBox application.
It allows you to test, update, and view database connection settings.
"""

import os
import sys
import json
import pymysql
from pymysql import Error
from dotenv import load_dotenv, set_key, dotenv_values

# Load environment variables from .env file
load_dotenv()


def test_connection(host=None, port=None, user=None, password=None, db_name=None):
    """Test connection to the database with given or current credentials"""
    # Use parameters if provided, otherwise use environment variables
    host = host or os.getenv("DB_HOST", "localhost")
    port = int(port or os.getenv("DB_PORT", "3306"))
    user = user or os.getenv("DB_USER", "root")
    password = password or os.getenv("DB_PASSWORD", "password")
    db_name = db_name or os.getenv("DB_NAME", "workbox_db")
    
    print(f"\n🔍 Testing connection to MySQL...")
    print(f"   Host: {host}:{port}")
    print(f"   User: {user}")
    print(f"   Database: {db_name}")
    
    try:
        # Try connecting to server
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=5
        )
        
        print("✅ Connected to MySQL server")
        
        # Check if database exists
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if db_name in databases:
            print(f"✅ Database '{db_name}' exists")
            # Try connecting to the specific database
            connection.select_db(db_name)
            print(f"✅ Successfully connected to database '{db_name}'")
            
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                print(f"✅ Database contains {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("ℹ️ Database exists but contains no tables")
        else:
            print(f"⚠️ Database '{db_name}' doesn't exist yet")
        
        cursor.close()
        connection.close()
        return True
    
    except Error as e:
        print(f"❌ Connection failed: {e}")
        
        # Provide helpful error messages
        if "Access denied" in str(e):
            print("\n🔑 MySQL Connection Error: Access Denied")
            print("Please ensure your MySQL credentials are correct.")
        elif "Can't connect" in str(e) or "Connection refused" in str(e):
            print("\n🔌 MySQL Connection Error: Cannot Connect to Server")
            print("Please ensure MySQL server is running and accessible.")
            print("For remote connections, check:")
            print("1. MySQL is configured to accept remote connections (bind-address = 0.0.0.0)")
            print("2. The server's firewall allows connections on port 3306")
        
        return False


def update_connection_settings():
    """Update the database connection settings in the .env file"""
    print("\n🔧 Update Database Connection Settings")
    print("=" * 40)
    
    # Read current settings
    try:
        config = dotenv_values(".env")
        current_host = config.get("DB_HOST", "localhost")
        current_port = config.get("DB_PORT", "3306")
        current_user = config.get("DB_USER", "root")
        current_db = config.get("DB_NAME", "workbox_db")
    except:
        current_host = "localhost"
        current_port = "3306"
        current_user = "root" 
        current_db = "workbox_db"
    
    # Get new settings from user
    print("\nPlease enter new database connection details (press Enter to keep current value):")
    
    host = input(f"MySQL Host (current: {current_host}): ").strip() or current_host
    port = input(f"MySQL Port (current: {current_port}): ").strip() or current_port
    user = input(f"MySQL Username (current: {current_user}): ").strip() or current_user
    password = input(f"MySQL Password: ").strip()
    db_name = input(f"Database Name (current: {current_db}): ").strip() or current_db
    
    # Test the new connection
    if test_connection(host, port, user, password, db_name):
        # Update .env file
        env_path = ".env"
        
        # Check if .env file exists
        if not os.path.exists(env_path):
            with open(env_path, "w") as f:
                f.write("# WorkBox Database Configuration\n")
        
        # Update values
        set_key(env_path, "DB_HOST", host)
        set_key(env_path, "DB_PORT", port)
        set_key(env_path, "DB_USER", user)
        
        # Only update password if provided
        if password:
            set_key(env_path, "DB_PASSWORD", password)
        
        set_key(env_path, "DB_NAME", db_name)
        
        # Update full URL
        if password:
            db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
            set_key(env_path, "DATABASE_URL", db_url)
        
        print("\n✅ Database connection settings updated successfully")
        print(f"📁 Settings saved to: {os.path.abspath(env_path)}")
    else:
        print("\n❌ Connection test failed. Settings not updated.")
        print("Please verify your connection details and try again.")


def show_connection_info():
    """Display the current connection settings"""
    print("\n🔍 Current Database Connection Settings")
    print("=" * 40)
    
    # Read from .env file
    try:
        config = dotenv_values(".env")
        
        # Create a redacted version for display
        display_config = config.copy()
        if "DB_PASSWORD" in display_config:
            display_config["DB_PASSWORD"] = "********"
        if "DATABASE_URL" in display_config:
            display_config["DATABASE_URL"] = display_config["DATABASE_URL"].replace(
                config.get("DB_PASSWORD", ""), "********"
            )
        
        # Print all database-related settings
        print("\nDatabase Configuration:")
        for key, value in display_config.items():
            if key.startswith("DB_") or key == "DATABASE_URL":
                print(f"{key} = {value}")
        
        # Test the current connection
        print("\nTesting connection with these settings...")
        test_connection()
        
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        print("Configuration file may be missing or corrupt.")


def check_multi_user_settings():
    """Check if the database is configured for multi-user access"""
    print("\n🔍 Checking Multi-User Configuration")
    print("=" * 40)
    
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "password")
    
    try:
        # Connect to the MySQL server
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=5
        )
        
        cursor = connection.cursor()
        
        # Check MySQL bind address
        print("\nChecking MySQL binding configuration...")
        try:
            cursor.execute("SHOW VARIABLES LIKE 'bind_address'")
            bind_result = cursor.fetchone()
            
            if bind_result:
                bind_address = bind_result[1]
                if bind_address == "0.0.0.0" or bind_address == "*":
                    print("✅ MySQL is configured to accept connections from any address")
                else:
                    print(f"⚠️ MySQL is only bound to {bind_address}")
                    print("   For multi-user access, consider setting bind_address = 0.0.0.0")
            else:
                print("ℹ️ Could not determine MySQL bind address")
        except:
            print("ℹ️ Could not check MySQL bind address (insufficient privileges)")
        
        # Check if the current user can connect from different hosts
        print("\nChecking user connection permissions...")
        try:
            cursor.execute(f"SELECT user, host FROM mysql.user WHERE user = '{user}'")
            user_hosts = cursor.fetchall()
            
            if user_hosts:
                remote_access = False
                for user_host in user_hosts:
                    if user_host[1] == "%" or user_host[1].find("%") >= 0:
                        remote_access = True
                        break
                
                if remote_access:
                    print(f"✅ User '{user}' is configured to connect from any host")
                else:
                    print(f"⚠️ User '{user}' might be restricted to specific hosts")
                    print("   For multi-user access, consider granting access from '%'")
            else:
                print(f"⚠️ Could not find user '{user}' in the database")
        except:
            print("ℹ️ Could not check user permissions (insufficient privileges)")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Could not check multi-user settings: {e}")


def main():
    """Main function"""
    print("🔧 WorkBox Connection Manager")
    print("=" * 40)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "test":
            test_connection()
        elif command == "update":
            update_connection_settings()
        elif command == "info":
            show_connection_info()
        elif command == "check":
            check_multi_user_settings()
        else:
            print("Unknown command. Available commands: test, update, info, check")
    else:
        # Interactive menu
        while True:
            print("\nPlease select an option:")
            print("1. Test database connection")
            print("2. Update connection settings")
            print("3. Show current connection information")
            print("4. Check multi-user configuration")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-4): ").strip()
            
            if choice == "1":
                test_connection()
            elif choice == "2":
                update_connection_settings()
            elif choice == "3":
                show_connection_info()
            elif choice == "4":
                check_multi_user_settings()
            elif choice == "0":
                print("\nExiting. Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
