"""
Authentication Module

This module handles employee authentication and login functionality.
"""

import hashlib
import json
import os
import requests
from pathlib import Path


class AuthenticationManager:
    """
    Handles user authentication and session management.
    """
    
    def __init__(self, api_url=None):
        """
        Initialize the authentication manager.
        
        Args:
            api_url (str, optional): The URL of the backend API. If None, will use local authentication.
        """
        self.api_url = api_url
        self.current_user = None
        self.session_token = None
    
    def login(self, username, password):
        """
        Authenticate a user with username and password.
        
        Args:
            username (str): The username
            password (str): The password
            
        Returns:
            tuple: (success, message, user_data)
                - success (bool): True if login was successful
                - message (str): Success or error message
                - user_data (dict): User data if login successful, None otherwise
        """
        # Check if we're using API or local authentication
        if self.api_url:
            return self._api_login(username, password)
        else:
            return self._local_login(username, password)
    
    def _api_login(self, username, password):
        """
        Authenticate using the backend API.
        """
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("access_token")
                self.current_user = data.get("user")
                return True, "Login successful", self.current_user
            else:
                error_msg = response.json().get("detail", "Invalid credentials")
                return False, error_msg, None
                
        except Exception as e:
            return False, f"Connection error: {str(e)}", None
    
    def _local_login(self, username, password):
        """
        Authenticate using a local users database (for development/testing).
        """
        try:
            # Hash the password (simple SHA-256 for demo purposes)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Load users from JSON file (just for demonstration)
            current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
            users_file = current_dir / "users.json"
            
            # If the file doesn't exist, create a demo file with one user
            if not users_file.exists():
                demo_users = {
                    "users": [
                        {
                            "username": "employee",
                            "password": hashlib.sha256("password123".encode()).hexdigest(),
                            "role": "employee",
                            "name": "Demo Employee"
                        }
                    ]
                }
                os.makedirs(users_file.parent, exist_ok=True)
                with open(users_file, 'w') as f:
                    json.dump(demo_users, f, indent=2)
            
            # Now read the file
            with open(users_file, 'r') as f:
                users_data = json.load(f)
            
            # Find the user
            for user in users_data.get("users", []):
                if user["username"] == username and user["password"] == hashed_password:
                    self.current_user = user
                    return True, "Login successful", user
            
            return False, "Invalid username or password", None
            
        except Exception as e:
            return False, f"Authentication error: {str(e)}", None
    
    def logout(self):
        """
        Log out the current user.
        
        Returns:
            bool: True if logout was successful
        """
        self.current_user = None
        self.session_token = None
        return True
    
    def is_authenticated(self):
        """
        Check if the user is currently authenticated.
        
        Returns:
            bool: True if authenticated
        """
        return self.current_user is not None
    
    def get_current_user(self):
        """
        Get the current authenticated user.
        
        Returns:
            dict: User data or None if not authenticated
        """
        return self.current_user
