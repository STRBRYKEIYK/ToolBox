import pymysql
from pymysql import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_database():
    """
    Creates the WorkBox database and tables if they don't already exist.
    """
    # MySQL credentials from environment variables
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    port = int(os.getenv("DB_PORT", "3306"))
    database = os.getenv("DB_NAME", "workbox")

    # Connect to MySQL server (without selecting a database)
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
        )

        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            print(f"Database '{database}' created or already exists")

        # Reconnect to the specific database
        connection.close()
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database,
            cursorclass=pymysql.cursors.DictCursor,
        )

        # Create tables
        with connection.cursor() as cursor:
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    role ENUM('admin', 'manager', 'employee') NOT NULL DEFAULT 'employee',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            print("Table 'users' created or already exists")

            # Create Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    sku VARCHAR(50) UNIQUE,
                    category VARCHAR(100),
                    price DECIMAL(10, 2) NOT NULL,
                    cost DECIMAL(10, 2),
                    stock_quantity INT NOT NULL DEFAULT 0,
                    low_stock_threshold INT DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            print("Table 'products' created or already exists")

            # Create Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    customer_name VARCHAR(200) NOT NULL,
                    status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    total_amount DECIMAL(10, 2) NOT NULL,
                    shipping_address TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("Table 'orders' created or already exists")

            # Create Order Items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            print("Table 'order_items' created or already exists")

            # Create Inventory Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    type ENUM('received', 'shipped', 'adjusted', 'damaged') NOT NULL,
                    reference_id INT,
                    notes TEXT,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            print("Table 'inventory_transactions' created or already exists")

            # Create Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("Table 'notifications' created or already exists")

            # Create a default admin user if none exists
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            result = cursor.fetchone()
            if result['count'] == 0:
                # Insert default admin (username: admin, password: admin123)
                cursor.execute("""
                    INSERT INTO users (username, password, email, role) 
                    VALUES ('admin', SHA2('admin123', 256), 'admin@workbox.local', 'admin')
                """)
                connection.commit()
                print("Default admin user created")

            # Insert some sample products
            cursor.execute("SELECT COUNT(*) as count FROM products")
            result = cursor.fetchone()
            if result['count'] == 0:
                products = [
                    ("Laptop", "High-performance laptop", "LP001", "Electronics", 1200.00, 900.00, 15, 5),
                    ("Office Chair", "Ergonomic office chair", "OC001", "Furniture", 250.00, 150.00, 20, 5),
                    ("Wireless Mouse", "Bluetooth wireless mouse", "WM001", "Electronics", 35.00, 20.00, 50, 10),
                    ("Notebook", "Lined notebook, 100 pages", "NB001", "Stationery", 4.99, 2.50, 100, 20),
                    ("Desk Lamp", "LED desk lamp", "DL001", "Lighting", 29.99, 15.00, 30, 5),
                ]
                for product in products:
                    cursor.execute("""
                        INSERT INTO products (name, description, sku, category, price, cost, stock_quantity, low_stock_threshold)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, product)
                connection.commit()
                print(f"{len(products)} sample products inserted")

        print("\nDatabase initialization completed successfully!")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    print("\n===== WorkBox Database Initialization =====\n")
    create_database()
