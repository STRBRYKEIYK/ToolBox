#!/usr/bin/env python3
"""
WorkBox Connection Manager Script
================================

This script helps manage the database connections for the WorkBox application.
It allows you to test, update, and view database connection settings.
"""

import os
import sys
import re
import pymysql
import socket
import json
import subprocess
from getpass import getpass
from datetime import datetime
from dotenv import load_dotenv, set_key, find_dotenv

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'-' * len(text)}{Colors.ENDC}\n")

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def load_env_file():
    """Load environment variables from .env file"""
    dotenv_path = find_dotenv()
    if not dotenv_path:
        # If .env doesn't exist, create it
        with open('.env', 'w') as f:
            f.write("# WorkBox Environment Configuration\n")
            f.write("# Created: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
            f.write("# Database Settings\n")
            f.write("DB_HOST=localhost\n")
            f.write("DB_PORT=3306\n")
            f.write("DB_USER=root\n")
            f.write("DB_PASSWORD=\n")
            f.write("DB_NAME=workbox\n")
        dotenv_path = '.env'
    
    load_dotenv(dotenv_path)
    return dotenv_path

def get_current_settings():
    """Get the current database connection settings"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'workbox'),
    }

def update_env_file(key, value, dotenv_path):
    """Update a key in the .env file"""
    try:
        set_key(dotenv_path, key, value)
        return True
    except Exception as e:
        print_error(f"Failed to update .env file: {e}")
        return False

def test_connection(settings=None):
    """Test the database connection with the given settings"""
    if settings is None:
        settings = get_current_settings()
    
    try:
        conn = pymysql.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['database'],
            connect_timeout=5
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)

def display_current_settings():
    """Display the current database connection settings"""
    settings = get_current_settings()
    
    print_header("Current Database Connection Settings")
    print(f"Host:     {settings['host']}")
    print(f"Port:     {settings['port']}")
    print(f"User:     {settings['user']}")
    print(f"Password: {'*' * len(settings['password']) if settings['password'] else '(not set)'}")
    print(f"Database: {settings['database']}")
    
    success, message = test_connection(settings)
    if success:
        print_success(f"Connection successful! MySQL version: {message}")
    else:
        print_error(f"Connection failed: {message}")

def modify_settings():
    """Modify the database connection settings"""
    dotenv_path = load_env_file()
    current = get_current_settings()
    
    print_header("Modify Database Connection Settings")
    print("Enter new values (or press Enter to keep current value)")
    
    host = input(f"Host [{current['host']}]: ") or current['host']
    
    # Validate port
    while True:
        port_str = input(f"Port [{current['port']}]: ") or str(current['port'])
        if port_str.isdigit() and 1 <= int(port_str) <= 65535:
            port = int(port_str)
            break
        print_error("Port must be a number between 1 and 65535")
    
    user = input(f"User [{current['user']}]: ") or current['user']
    
    # For password, use getpass for security
    password_prompt = "(enter to keep current)" if current['password'] else "(empty)"
    password = getpass(f"Password {password_prompt}: ")
    if not password:
        password = current['password']
    
    database = input(f"Database [{current['database']}]: ") or current['database']
    
    # Create new settings
    new_settings = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    # Test new connection before saving
    print_info("Testing connection with new settings...")
    success, message = test_connection(new_settings)
    
    if success:
        print_success(f"Connection successful! MySQL version: {message}")
        
        # Confirm save
        save = input("\nSave these settings? (y/n): ").lower() == 'y'
        if save:
            update_env_file('DB_HOST', host, dotenv_path)
            update_env_file('DB_PORT', str(port), dotenv_path)
            update_env_file('DB_USER', user, dotenv_path)
            update_env_file('DB_PASSWORD', password, dotenv_path)
            update_env_file('DB_NAME', database, dotenv_path)
            print_success("Settings saved to .env file!")
        else:
            print_info("Settings not saved.")
    else:
        print_error(f"Connection failed: {message}")
        print_warning("Settings not saved due to failed connection test.")

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # This doesn't actually send any data, just creates a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip

def check_mysql_network_settings():
    """Check MySQL network settings to ensure it's accessible over the network"""
    print_header("MySQL Network Access Check")
    
    settings = get_current_settings()
    if settings['host'] not in ['localhost', '127.0.0.1']:
        print_info(f"MySQL host is set to {settings['host']}, which is not localhost.")
        print_info("This suggests you're connecting to a remote MySQL server.")
        return
    
    # Check if MySQL is accessible from other devices
    try:
        # Try to check the bind-address in MySQL configuration
        bind_address = None
        try:
            conn = pymysql.connect(
                host=settings['host'],
                port=settings['port'],
                user=settings['user'],
                password=settings['password'],
                database=settings['database']
            )
            with conn.cursor() as cursor:
                cursor.execute("SHOW VARIABLES LIKE 'bind_address'")
                result = cursor.fetchone()
                if result:
                    bind_address = result[1]
            conn.close()
        except Exception as e:
            print_error(f"Could not check MySQL bind-address: {e}")
        
        if bind_address:
            if bind_address in ['127.0.0.1', 'localhost']:
                print_warning("MySQL is configured to only accept connections from localhost")
                print_info("To allow connections from other devices, edit your MySQL configuration file:")
                print("1. Find your my.cnf or my.ini file")
                print("2. Change 'bind-address = 127.0.0.1' to 'bind-address = 0.0.0.0'")
                print("3. Restart MySQL server")
            elif bind_address == '0.0.0.0':
                print_success("MySQL is configured to accept connections from any IP")
            else:
                print_info(f"MySQL bind-address is set to: {bind_address}")
        else:
            print_warning("Could not determine MySQL bind-address configuration")
    
    except Exception as e:
        print_error(f"Error checking MySQL network settings: {e}")

def main_menu():
    """Display the main menu"""
    while True:
        print_header("WorkBox Connection Manager")
        print("1. View current connection settings")
        print("2. Modify connection settings")
        print("3. Test connection")
        print("4. Check MySQL network access")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            display_current_settings()
        elif choice == '2':
            modify_settings()
        elif choice == '3':
            success, message = test_connection()
            if success:
                print_success(f"Connection successful! MySQL version: {message}")
            else:
                print_error(f"Connection failed: {message}")
        elif choice == '4':
            check_mysql_network_settings()
        elif choice == '5':
            print_info("Exiting WorkBox Connection Manager. Goodbye!")
            break
        else:
            print_error("Invalid choice. Please enter a number from 1 to 5.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Load environment variables
    load_env_file()
    
    # Run the main menu
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt. Goodbye!")
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
