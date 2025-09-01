import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Get database connection info from environment
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "password")
        db_name = os.getenv("DB_NAME", "workbox_db")
        
        print(f"\n🔌 Connecting to MySQL server...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {user}")
        
        # Connect to MySQL server (without specifying a database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=10,  # 10 seconds timeout for connection
        )

        if connection:
            print("✅ Connected to MySQL server")
            cursor = connection.cursor()

            # Check if database already exists
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if db_name in databases:
                print(f"✅ Database '{db_name}' already exists")
            else:
                # Create database if it doesn't exist
                print(f"🔧 Creating database '{db_name}'...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                print(f"✅ Database '{db_name}' created successfully")
                
                # Set character set and collation for proper UTF-8 support
                cursor.execute(f"ALTER DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("✅ Database configured with UTF-8 support")

            # Grant privileges to the user (useful for remote connections)
            try:
                # Create the user if doesn't exist (MySQL 8+)
                if user != "root":
                    cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}'")
                    # Grant privileges
                    cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user}'@'%'")
                    cursor.execute("FLUSH PRIVILEGES")
                    print(f"✅ Database privileges granted to user '{user}'")
            except Error as e:
                print(f"Note: {e}")
                print("ℹ️ You may need to manually grant privileges if using a restricted MySQL account")

            cursor.close()
            connection.close()
            print("✅ MySQL configuration completed")

    except Error as e:
        print(f"❌ Error during database setup: {e}")
        
        if "Access denied" in str(e):
            print("\n🔑 MySQL Connection Error: Access Denied")
            print("Please ensure your MySQL credentials are correct and the user has appropriate privileges.")
            print("You might need to run this command in MySQL as root:")
            print(f"    CREATE USER '{user}'@'%' IDENTIFIED BY 'your_password';")
            print(f"    GRANT ALL PRIVILEGES ON {db_name}.* TO '{user}'@'%';")
            print(f"    FLUSH PRIVILEGES;")
        elif "Can't connect" in str(e) or "Connection refused" in str(e):
            print("\n🔌 MySQL Connection Error: Cannot Connect to Server")
            print("Please ensure MySQL server is running and accessible.")
            print("If using a remote server, check that:")
            print("1. MySQL is configured to accept remote connections (bind-address = 0.0.0.0)")
            print("2. The server's firewall allows connections on port 3306")
            print("3. Your database user is allowed to connect from your IP address")
        
        return False

    return True


def initialize_sample_data():
    """Initialize the database with sample data"""
    from WorkBox.api.database import SessionLocal, create_tables
    from WorkBox.api.models import User, Inventory

    # Create tables
    create_tables()
    print("Database tables created successfully.")

    # Create sample data
    db = SessionLocal()
    try:
        # Check if sample data already exists
        if db.query(User).first() is None:
            # Create sample users
            users = [
                User(username="john_doe", email="john@example.com"),
                User(username="jane_smith", email="jane@example.com"),
                User(username="bob_wilson", email="bob@example.com"),
            ]

            for user in users:
                db.add(user)
            db.commit()
            print("Sample users created.")

        if db.query(Inventory).first() is None:
            # Create sample inventory
            inventory_items = [
                Inventory(
                    name="Laptop",
                    description="High-performance laptop",
                    price=999.99,
                    stock_quantity=50,
                ),
                Inventory(
                    name="Mouse",
                    description="Wireless optical mouse",
                    price=29.99,
                    stock_quantity=200,
                ),
                Inventory(
                    name="Keyboard",
                    description="Mechanical gaming keyboard",
                    price=79.99,
                    stock_quantity=100,
                ),
                Inventory(
                    name="Monitor",
                    description="27-inch 4K monitor",
                    price=399.99,
                    stock_quantity=30,
                ),
                Inventory(
                    name="Headphones",
                    description="Noise-cancelling headphones",
                    price=149.99,
                    stock_quantity=75,
                ),
            ]

            for item in inventory_items:
                db.add(item)
            db.commit()
            print("Sample inventory created.")

        print("Database initialized with sample data successfully!")

    except Exception as e:
        print(f"Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")

    if create_database():
        initialize_sample_data()
    else:
        print("Failed to create database. Please check your MySQL configuration.")
