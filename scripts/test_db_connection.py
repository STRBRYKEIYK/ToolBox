#!/usr/bin/env python3
"""
WorkBox Database Connection Test Script
======================================

This script tests the connection to a WorkBox database and performs
basic CRUD operations to verify functionality.
"""

import pymysql
import sys
import getpass

# Connection parameters
HOST = "localhost"  # Change to server IP if connecting remotely
PORT = 3306
USER = input("Enter MySQL username [root]: ") or "root"
PASSWORD = getpass.getpass(f"Enter MySQL password for '{USER}': ")
DB = "workbox_db"

def test_connection():
    """Test connection to the database"""
    try:
        conn = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DB,
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ Successfully connected to MySQL (version: {version})")
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✓ Users table accessible ({user_count} records)")
            
            cursor.execute("SELECT COUNT(*) FROM inventory")
            inventory_count = cursor.fetchone()[0]
            print(f"✓ Inventory table accessible ({inventory_count} records)")
            
            # Test read operations
            print("\n=== Sample Inventory Items ===")
            cursor.execute("SELECT item_id, item_name, current_stock, status FROM inventory LIMIT 5")
            items = cursor.fetchall()
            for item in items:
                print(f"ID: {item[0]}, Name: {item[1]}, Stock: {item[2]}, Status: {item[3]}")
            
            # Test if user has write permissions by inserting a test activity
            try:
                # Get the first user ID to use for the activity
                cursor.execute("SELECT user_id FROM users LIMIT 1")
                user_id = cursor.fetchone()[0]
                
                # Insert a test activity
                cursor.execute("""
                    INSERT INTO user_activities (user_id, activity_type, description, ip_address)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, 'test', 'Database connection test', '127.0.0.1'))
                conn.commit()
                print("\n✓ Write access confirmed - added test activity record")
                
                # Clean up the test record
                cursor.execute("DELETE FROM user_activities WHERE activity_type = 'test' AND description = 'Database connection test'")
                conn.commit()
                print("✓ Test record cleaned up")
            except pymysql.Error as e:
                print(f"\n⚠ Write operations failed: {str(e)}")
                print("⚠ User has read-only access or lacks permissions")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("WorkBox Database Connection Test")
    print("================================")
    
    success = test_connection()
    if success:
        print("\n✓ Database test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Database test failed")
        sys.exit(1)
