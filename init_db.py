import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying a database)
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "password"),
        )

        if connection:
            cursor = connection.cursor()

            # Create database if it doesn't exist
            db_name = os.getenv("DB_NAME", "workbox_db")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' created successfully or already exists.")

            cursor.close()
            connection.close()
            print("MySQL connection closed.")

    except Error as e:
        print(f"Error creating database: {e}")
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
