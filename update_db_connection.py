"""
WorkBox Database Connection Updater
==================================

This script helps update the database connection URL in the .env file
to make sure it's properly configured for network access.
"""

import os
import re
import socket

def get_local_ip():
    """Get the local IP address of this machine"""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def update_env_file():
    """Update the .env file with the proper database URL"""
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found. Run setup_mysql.py first.")
        return False
    
    # Read the current .env file
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Check if DATABASE_URL exists
    db_url_match = re.search(r'DATABASE_URL=(.+)', env_content)
    if not db_url_match:
        print("Error: DATABASE_URL not found in .env file.")
        return False
    
    current_url = db_url_match.group(1)
    print(f"Current database URL: {current_url}")
    
    # Ask for host configuration
    print("\nHow should the database be configured?")
    print("1. Local only (localhost)")
    print("2. This computer's IP address (for network access)")
    print("3. Custom hostname or IP")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == '1':
        new_host = 'localhost'
    elif choice == '2':
        new_host = get_local_ip()
    elif choice == '3':
        new_host = input("Enter hostname or IP address: ")
    else:
        print("Invalid choice. Using localhost.")
        new_host = 'localhost'
    
    # Extract components from current URL
    url_pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:/]+):(\d+)/([^?]+)(\?.*)?'
    match = re.match(url_pattern, current_url)
    
    if not match:
        print("Error: Unable to parse DATABASE_URL format.")
        return False
    
    user, password, host, port, db_name, query_params = match.groups()
    query_params = query_params or ''
    
    # Create new URL with updated host
    new_url = f'mysql+pymysql://{user}:{password}@{new_host}:{port}/{db_name}{query_params}'
    print(f"New database URL: {new_url}")
    
    # Update DB_HOST separately
    updated_env = re.sub(r'DB_HOST=.*', f'DB_HOST={new_host}', env_content)
    
    # Update DATABASE_URL
    updated_env = re.sub(r'DATABASE_URL=.*', f'DATABASE_URL={new_url}', updated_env)
    
    # Write updated .env file
    with open('.env', 'w') as f:
        f.write(updated_env)
    
    print("\n.env file updated successfully!")
    print("Remember to restart the WorkBox server for changes to take effect.")
    return True

def check_mysql_access():
    """Check if MySQL is accessible from the network"""
    try:
        import pymysql
        from dotenv import load_dotenv
        
        load_dotenv()
        
        host = os.getenv('DB_HOST')
        port = int(os.getenv('DB_PORT', 3306))
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        db_name = os.getenv('DB_NAME')
        
        print(f"\nTesting connection to MySQL at {host}:{port}...")
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
        
        connection.close()
        
        print(f"✅ Connection successful! MySQL version: {version}")
        return True
        
    except ImportError:
        print("❌ Error: Required packages missing. Run 'pip install pymysql python-dotenv'")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nPossible issues:")
        print("1. MySQL server might not be running")
        print("2. MySQL server might not be configured for remote access")
        print("3. Firewall might be blocking port 3306")
        print("4. Database credentials in .env might be incorrect")
        return False

if __name__ == "__main__":
    print("="*50)
    print("WorkBox Database Connection Updater")
    print("="*50)
    print("\nThis tool helps configure database connections for network access.")
    
    if update_env_file():
        print("\nTesting new connection settings...")
        check_mysql_access()
    
    print("\nDone!")
    input("Press Enter to exit...")
