#!/usr/bin/env python3
"""
WorkBox API Test Script
======================

This script tests the WorkBox API by making requests to various endpoints.
"""

import requests
import sys

API_BASE_URL = "http://localhost:8000"

def test_get_users():
    """Test GET /users/ endpoint"""
    print("\nTesting GET /users/ endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/users/")
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Print status and data
        print(f"Status Code: {response.status_code}")
        users = response.json()
        print(f"Number of users: {len(users)}")
        
        for user in users:
            print(f"- User ID: {user['user_id']}, Username: {user['username']}, Access: {user['access_level']}")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False
        
def test_get_inventory():
    """Test GET /inventory/ endpoint"""
    print("\nTesting GET /inventory/ endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/inventory/")
        response.raise_for_status()
        
        # Print status and data
        print(f"Status Code: {response.status_code}")
        items = response.json()
        print(f"Number of inventory items: {len(items)}")
        
        for item in items[:5]:  # Show just the first 5
            print(f"- Item ID: {item['item_id']}, Name: {item['item_name']}, Stock: {item['current_stock']}")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False

def test_create_user():
    """Test POST /users/ endpoint"""
    print("\nTesting POST /users/ endpoint...")
    
    # Test user data
    new_user = {
        "full_name": "API Test User",
        "username": f"apitest_{int(__import__('time').time())}",  # Unique username
        "password": "testpassword",
        "access_level": "user"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/users/", 
            json=new_user
        )
        response.raise_for_status()
        
        # Print status and data
        print(f"Status Code: {response.status_code}")
        user = response.json()
        print("Created new user:")
        print(f"- User ID: {user['user_id']}, Username: {user['username']}, Access: {user['access_level']}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("WorkBox API Test Script")
    print("======================")
    
    # Get API health check
    print("\nChecking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        health_data = response.json()
        print(f"API Status: {health_data.get('status')}")
        print(f"Database Status: {health_data.get('database')}")
        print(f"Timestamp: {health_data.get('timestamp')}")
    except requests.exceptions.RequestException as e:
        print(f"API Health Check Failed: {str(e)}")
        print("Make sure the API server is running on http://localhost:8000")
        sys.exit(1)
    
    # Run tests
    success_count = 0
    total_tests = 3  # Update this if you add more tests
    
    if test_get_users():
        success_count += 1
        
    if test_get_inventory():
        success_count += 1
    
    if test_create_user():
        success_count += 1
    
    # Print summary
    print("\nTest Summary:")
    print(f"Passed: {success_count}/{total_tests} tests")
    
    if success_count == total_tests:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
