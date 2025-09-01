#!/usr/bin/env python3
"""
MySQL Setup Helper for WorkBox
============================

This script helps you set up your MySQL credentials for the WorkBox application.
Run this script to test your MySQL connection and create the .env file.

Usage:
    # On Windows with Python in PATH:
    python setup_mysql.py

    # On Linux/macOS:
    ./setup_mysql.py
"""

import os
import pymysql
import platform
import socket
from getpass import getpass
from dotenv import load_dotenv, find_dotenv, set_key

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
    print(f"{Colors.HEADER}{'-' * len(text)}{Colors.ENDC}")

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

def test_mysql_connection(host, port, user, password, database=None):
    """Test the MySQL connection with the given credentials"""
    try:
        # Create connection object
        conn_args = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'connect_timeout': 5,
        }
        if database:
            conn_args['database'] = database
            
        # Attempt to connect
        conn = pymysql.connect(**conn_args)
        
        # Check if successful
        with conn.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            version = cursor.fetchone()[0]
        
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)

def setup_database():
    """Interactively set up the MySQL connection"""
    print_header("MySQL Connection Setup")
    
    # Get MySQL connection details
    print_info("Please enter your MySQL connection details:")
    
    host = input("Host [localhost]: ") or "localhost"
    
    port_input = input("Port [3306]: ") or "3306"
    try:
        port = int(port_input)
    except ValueError:
        print_error(f"Invalid port number: {port_input}. Using default: 3306")
        port = 3306
    
    user = input("Username [root]: ") or "root"
    password = getpass("Password [leave blank for none]: ")
    
    # Test the connection
    print_info("Testing MySQL connection...")
    success, message = test_mysql_connection(host, port, user, password)
    
    if success:
        print_success(f"Connection successful! MySQL version: {message}")
        
        # Ask for the database name
        database = input("Database name [workbox]: ") or "workbox"
        
        # Check if database exists
        success, _ = test_mysql_connection(host, port, user, password, database)
        if not success:
            print_warning(f"Database '{database}' does not exist yet.")
            create_db = input("Create it now? (y/n): ").lower() == 'y'
            
            if create_db:
                try:
                    conn = pymysql.connect(
                        host=host,
                        port=port,
                        user=user,
                        password=password
                    )
                    with conn.cursor() as cursor:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                    conn.close()
                    print_success(f"Database '{database}' created successfully!")
                except Exception as e:
                    print_error(f"Failed to create database: {e}")
                    return False
        
        # Create/update .env file
        dotenv_path = find_dotenv()
        if not dotenv_path:
            dotenv_path = '.env'
            with open(dotenv_path, 'w') as f:
                f.write("# WorkBox Environment Configuration\n\n")
        
        set_key(dotenv_path, "DB_HOST", host)
        set_key(dotenv_path, "DB_PORT", str(port))
        set_key(dotenv_path, "DB_USER", user)
        set_key(dotenv_path, "DB_PASSWORD", password)
        set_key(dotenv_path, "DB_NAME", database)
        
        print_success(f"Database configuration saved to {dotenv_path}")
        return True
    else:
        print_error(f"Connection failed: {message}")
        return False

if __name__ == "__main__":
    print("\n====== WorkBox MySQL Setup ======\n")
    setup_database()
