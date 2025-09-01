"""
WorkBox Database Connection Updater
==================================

This script helps update the database connection URL in the .env file
to make sure it's properly configured for network access.
"""

import os
import re
import socket
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

# ANSI color codes
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{text}{Colors.ENDC}")
    print("-" * len(text))

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        # This doesn't actually send any data, just creates a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback method
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip

def find_env_file():
    """Find the .env file"""
    env_path = find_dotenv()
    if env_path:
        return env_path
    
    # Check in common locations
    common_paths = [
        '.env',
        '../.env',
        '../../.env',
    ]
    
    for path in common_paths:
        if os.path.isfile(path):
            return os.path.abspath(path)
    
    return None

def update_connection_settings(env_path):
    """Update the database connection settings in .env file"""
    if not env_path or not os.path.isfile(env_path):
        print_error(f"Could not find .env file at {env_path}")
        return False
    
    # Load current settings
    load_dotenv(env_path)
    
    # Get current settings
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "workbox")
    
    print_header("Current Database Settings")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password) if password else '(not set)'}")
    print(f"Database: {database}")
    
    # Check if host is set to localhost
    local_ip = get_local_ip()
    if host in ["localhost", "127.0.0.1"]:
        print_warning("Host is set to localhost, which only allows connections from this computer.")
        print_info(f"Consider changing it to your IP address ({local_ip}) for network access.")
        change = input("Update host to your IP address? (y/n): ").lower() == 'y'
        
        if change:
            # Update the host setting
            set_key(env_path, "DB_HOST", local_ip)
            print_success(f"Updated DB_HOST from '{host}' to '{local_ip}'")
            return True
    else:
        print_success(f"Host is already set to {host}, which should allow network connections.")
    
    return False

def main():
    """Main function"""
    print_header("WorkBox Database Connection Updater")
    
    # Find .env file
    env_path = find_env_file()
    if not env_path:
        print_error("Could not find .env file. Please create one first.")
        print_info("You can run setup_mysql.py to create the .env file.")
        return
    
    print_info(f"Found .env file at: {env_path}")
    
    # Update connection settings
    updated = update_connection_settings(env_path)
    
    if updated:
        print_header("Connection Updated")
        print_info("Your database connection settings have been updated for network access.")
        print_info("If you're still having connection issues:")
        print_info("1. Make sure your MySQL server is configured to accept remote connections")
        print_info("2. Check that your firewall allows connections on the MySQL port (usually 3306)")
        print_info("3. Verify that the user has permissions to connect from other hosts")
    else:
        print_header("No Changes Made")
        print_info("Your database connection settings were not changed.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
