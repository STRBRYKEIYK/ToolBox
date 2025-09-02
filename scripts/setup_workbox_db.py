#!/usr/bin/env python3
"""
WorkBox Database Setup Script
============================

This script sets up the WorkBox database for a metal fabrication company.
It creates the database and necessary tables according to the specified schema.
"""

import pymysql
import os
import sys
from getpass import getpass
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

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

def get_db_credentials():
    """Get database credentials from environment or user input"""
    host = os.getenv("DB_HOST") or input("MySQL Host [localhost]: ") or "localhost"
    port_str = os.getenv("DB_PORT") or input("MySQL Port [3306]: ") or "3306"
    try:
        port = int(port_str)
    except ValueError:
        print_warning(f"Invalid port: {port_str}. Using 3306.")
        port = 3306

    user = os.getenv("DB_USER") or input("MySQL Username [root]: ") or "root"
    password = os.getenv("DB_PASSWORD")
    if password is None:
        password = getpass("MySQL Password: ")
        
    db_name = os.getenv("DB_NAME") or input("Database Name [workbox_db]: ") or "workbox_db"
    
    return host, port, user, password, db_name

def save_env_file(host, port, user, password, db_name):
    """Save database credentials to .env file"""
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    # Create new .env file if it doesn't exist
    if not os.path.exists(dotenv_path):
        with open(dotenv_path, 'w') as f:
            f.write("# WorkBox Environment Variables\n\n")
    
    # Set environment variables
    set_key(dotenv_path, "DB_HOST", host)
    set_key(dotenv_path, "DB_PORT", str(port))
    set_key(dotenv_path, "DB_USER", user)
    set_key(dotenv_path, "DB_PASSWORD", password)
    set_key(dotenv_path, "DB_NAME", db_name)
    
    print_success(f"Environment variables saved to {dotenv_path}")

def test_connection(host, port, user, password, db_name=None):
    """Test MySQL connection with provided credentials"""
    try:
        conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'charset': 'utf8mb4',
            'connect_timeout': 5,
        }
        
        if db_name:
            conn_params['database'] = db_name
            
        conn = pymysql.connect(**conn_params)
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
        conn.close()
        return True, version
    except Exception as e:
        return False, str(e)

def create_database(host, port, user, password, db_name):
    """Create the WorkBox database"""
    try:
        # Connect to MySQL server (without database)
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        
        with conn.cursor() as cursor:
            # Create database with UTF8MB4 charset
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print_success(f"Database '{db_name}' created or already exists")
            
        conn.close()
        return True
    except Exception as e:
        print_error(f"Failed to create database: {str(e)}")
        return False

def create_tables(host, port, user, password, db_name):
    """Create all required tables for the WorkBox application"""
    try:
        # Connect to the database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            # Create users table
            print_info("Creating users table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `users` (
                    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
                    `full_name` VARCHAR(100) NOT NULL,
                    `username` VARCHAR(50) NOT NULL UNIQUE,
                    `access_level` VARCHAR(20) NOT NULL DEFAULT 'user',
                    `password_salt` VARCHAR(100) NOT NULL,
                    `password_hash` VARCHAR(255) NOT NULL,
                    `twofa_salt` VARCHAR(100) NULL,
                    `twofa_hash` VARCHAR(255) NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_username` (`username`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print_success("Users table created")
            
            # Create inventory table
            print_info("Creating inventory table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `inventory` (
                    `item_id` INT AUTO_INCREMENT PRIMARY KEY,
                    `item_name` VARCHAR(100) NOT NULL,
                    `brand` VARCHAR(100) NULL,
                    `category` VARCHAR(50) NULL,
                    `location` VARCHAR(100) NULL,
                    `unit` VARCHAR(20) NULL,
                    `stock_in` INT NOT NULL DEFAULT 0,
                    `stock_out` INT NOT NULL DEFAULT 0,
                    `current_stock` INT NOT NULL DEFAULT 0,
                    `min_stock` INT NOT NULL DEFAULT 0,
                    `deficit` INT NOT NULL DEFAULT 0,
                    `status` VARCHAR(20) NOT NULL DEFAULT 'In Stock',
                    `price_per_unit` DECIMAL(10, 2) NULL,
                    `total_cost` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    `last_po_date` DATETIME NULL,
                    `supplier` VARCHAR(100) NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX `idx_item_name` (`item_name`),
                    INDEX `idx_category` (`category`),
                    INDEX `idx_status` (`status`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print_success("Inventory table created")
            
            # Create orders table
            print_info("Creating orders table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `orders` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user_id` INT NOT NULL,
                    `order_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
                    `total_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    `supplier` VARCHAR(100) NULL,
                    `notes` TEXT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE RESTRICT,
                    INDEX `idx_order_date` (`order_date`),
                    INDEX `idx_status` (`status`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print_success("Orders table created")
            
            # Create order items table
            print_info("Creating order_items table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `order_items` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `order_id` INT NOT NULL,
                    `inventory_id` INT NOT NULL,
                    `quantity` INT NOT NULL,
                    `price` DECIMAL(10, 2) NOT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`inventory_id`) REFERENCES `inventory`(`item_id`) ON DELETE RESTRICT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print_success("Order items table created")
            
            # Create activity report table
            print_info("Creating user_activities table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `user_activities` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `user_id` INT NOT NULL,
                    `activity_type` VARCHAR(50) NOT NULL,
                    `description` TEXT NULL,
                    `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
                    `ip_address` VARCHAR(50) NULL,
                    `affected_item` INT NULL,
                    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE RESTRICT,
                    INDEX `idx_timestamp` (`timestamp`),
                    INDEX `idx_activity_type` (`activity_type`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print_success("User activities table created")
            
            # Create triggers for inventory management
            print_info("Creating triggers for inventory management...")
            
            # Trigger to update current_stock, deficit, and status BEFORE the update
            cursor.execute("""
                DROP TRIGGER IF EXISTS `inventory_before_update`;
            """)
            
            cursor.execute("""
                CREATE TRIGGER `inventory_before_update` BEFORE UPDATE ON `inventory`
                FOR EACH ROW
                BEGIN
                    -- Update status based on stock levels
                    IF NEW.current_stock <= 0 THEN
                        SET NEW.status = 'Out of Stock';
                    ELSEIF NEW.current_stock < NEW.min_stock THEN
                        SET NEW.status = 'Low in Stock';
                    ELSE
                        SET NEW.status = 'In Stock';
                    END IF;
                    
                    -- Update deficit calculation
                    SET NEW.deficit = NEW.current_stock - NEW.min_stock;
                    
                    -- Update total cost
                    IF NEW.price_per_unit IS NOT NULL THEN
                        SET NEW.total_cost = NEW.current_stock * NEW.price_per_unit;
                    ELSE
                        SET NEW.total_cost = 0;
                    END IF;
                END;
            """)
            
            # Also add a trigger for new inventory items
            cursor.execute("""
                DROP TRIGGER IF EXISTS `inventory_before_insert`;
            """)
            
            cursor.execute("""
                CREATE TRIGGER `inventory_before_insert` BEFORE INSERT ON `inventory`
                FOR EACH ROW
                BEGIN
                    -- Set current_stock if not explicitly provided
                    IF NEW.current_stock IS NULL THEN
                        SET NEW.current_stock = NEW.stock_in - NEW.stock_out;
                    END IF;
                    
                    -- Update status based on stock levels
                    IF NEW.current_stock <= 0 THEN
                        SET NEW.status = 'Out of Stock';
                    ELSEIF NEW.current_stock < NEW.min_stock THEN
                        SET NEW.status = 'Low in Stock';
                    ELSE
                        SET NEW.status = 'In Stock';
                    END IF;
                    
                    -- Update deficit calculation
                    SET NEW.deficit = NEW.current_stock - NEW.min_stock;
                    
                    -- Update total cost
                    IF NEW.price_per_unit IS NOT NULL THEN
                        SET NEW.total_cost = NEW.current_stock * NEW.price_per_unit;
                    ELSE
                        SET NEW.total_cost = 0;
                    END IF;
                END;
            """)
            print_success("Inventory management triggers created")
            
            # Create default admin user
            print_info("Creating default admin user...")
            cursor.execute("SELECT COUNT(*) FROM `users`")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Simple default password hash - in production you'd use proper hashing
                salt = "defaultsalt123"
                hashed_password = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918" # 'admin' hashed with SHA-256
                
                cursor.execute("""
                    INSERT INTO `users` 
                    (`full_name`, `username`, `access_level`, `password_salt`, `password_hash`) 
                    VALUES 
                    ('System Administrator', 'admin', 'admin', %s, %s)
                """, (salt, hashed_password))
                print_success("Default admin user created (Username: admin, Password: admin)")
                
                # Log the user creation in activity report
                cursor.execute("""
                    INSERT INTO `user_activities` 
                    (`user_id`, `activity_type`, `description`) 
                    VALUES 
                    (1, 'system', 'Default admin user created during system initialization')
                """)
            
            # Sample inventory items for metal fabrication
            print_info("Adding sample inventory items...")
            cursor.execute("SELECT COUNT(*) FROM `inventory`")
            inventory_count = cursor.fetchone()[0]
            
            if inventory_count == 0:
                # Sample items for a metal fabrication company
                sample_items = [
                    ('Steel Sheet 3mm', 'MetalCorp', 'Raw Material', 'Warehouse A', 'sheet', 50, 10, 40, 20, 'In Stock', 75.50),
                    ('Aluminum Rod 10mm', 'AlumaCorp', 'Raw Material', 'Warehouse B', 'meter', 200, 50, 150, 50, 'In Stock', 12.25),
                    ('Welding Rod E6013', 'WeldMaster', 'Consumable', 'Supply Room', 'kg', 100, 30, 70, 40, 'In Stock', 8.50),
                    ('Grinding Disc 4.5"', 'Abrasico', 'Consumable', 'Tool Room', 'pcs', 75, 25, 50, 30, 'In Stock', 3.75),
                    ('Cutting Fluid', 'CoolCut', 'Consumable', 'Chemical Storage', 'liter', 20, 5, 15, 10, 'In Stock', 15.00),
                    ('Welding Gloves', 'SafetyFirst', 'Safety Equipment', 'PPE Cabinet', 'pair', 30, 5, 25, 10, 'In Stock', 12.00),
                    ('Drill Bit Set', 'DrillTech', 'Tool', 'Tool Room', 'set', 10, 0, 10, 3, 'In Stock', 45.00),
                    ('Steel Tube 2"', 'TubeCo', 'Raw Material', 'Warehouse A', 'meter', 120, 70, 50, 40, 'In Stock', 18.75),
                    ('Stainless Sheet 2mm', 'SteelPro', 'Raw Material', 'Warehouse C', 'sheet', 30, 10, 20, 10, 'In Stock', 125.00),
                    ('Coper Wire 12AWG', 'WireCo', 'Raw Material', 'Electrical Room', 'meter', 500, 200, 300, 150, 'In Stock', 2.25)
                ]
                
                for item in sample_items:
                    name, brand, category, location, unit, stock_in, stock_out, current, min_stock, status, price = item
                    total_cost = current * price
                    deficit = current - min_stock
                    
                    cursor.execute("""
                        INSERT INTO `inventory`
                        (`item_name`, `brand`, `category`, `location`, `unit`, `stock_in`, `stock_out`, 
                        `current_stock`, `min_stock`, `deficit`, `status`, `price_per_unit`, `total_cost`) 
                        VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, brand, category, location, unit, stock_in, stock_out, current, 
                           min_stock, deficit, status, price, total_cost))
                
                print_success(f"Added {len(sample_items)} sample inventory items")
            
            conn.commit()
            print_success("All tables created successfully!")
        
        conn.close()
        return True
    except Exception as e:
        print_error(f"Failed to create tables: {str(e)}")
        return False

def main():
    """Main execution function"""
    print_header("WorkBox Database Setup for Metal Fabrication")
    
    # Get database credentials
    host, port, user, password, db_name = get_db_credentials()
    
    # Test MySQL server connection (without database)
    print_info("Testing MySQL server connection...")
    success, version = test_connection(host, port, user, password)
    
    if success:
        print_success(f"Connected to MySQL server (version: {version})")
    else:
        print_error(f"Failed to connect to MySQL server: {version}")
        sys.exit(1)
    
    # Create the database
    if create_database(host, port, user, password, db_name):
        # Test connection to the new database
        success, _ = test_connection(host, port, user, password, db_name)
        
        if success:
            print_success(f"Connected to database '{db_name}'")
            
            # Create tables
            if create_tables(host, port, user, password, db_name):
                print_header("Database Setup Complete")
                print_info("The WorkBox database has been set up successfully with the following details:")
                print(f"  Host: {host}")
                print(f"  Port: {port}")
                print(f"  User: {user}")
                print(f"  Database: {db_name}")
                
                # Save to .env file
                save = input("\nSave these credentials to .env file? (Y/n): ").lower() != 'n'
                if save:
                    save_env_file(host, port, user, password, db_name)
                    print_info("You can now start the application with these database settings.")
            else:
                print_error("Failed to create necessary tables.")
                sys.exit(1)
        else:
            print_error(f"Failed to connect to the database '{db_name}'.")
            sys.exit(1)
    else:
        print_error("Failed to create database.")
        sys.exit(1)

if __name__ == "__main__":
    main()
