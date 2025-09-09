"""
api_connection.py
Handles API connections and data fetching
"""

import requests
import json
from typing import Dict, Any, Optional, Tuple
from requests.exceptions import RequestException, Timeout, ConnectionError

class APIConnection:
    def __init__(self, api_url: str = None):
        """
        Initialize API connection handler
        
        Args:
            api_url: The API endpoint URL
        """
        self.api_url = api_url
        self.timeout = 10  # Default timeout in seconds
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.last_response = None
        self.last_error = None
    
    def set_url(self, url: str) -> None:
        """Set or update the API URL"""
        self.api_url = url.strip()
    
    def validate_url(self, url: str = None) -> Tuple[bool, str]:
        """
        Validate if the URL format is correct
        
        Returns:
            Tuple of (is_valid, message)
        """
        check_url = url or self.api_url
        
        if not check_url:
            return False, "No URL provided"
        
        if not check_url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        # Basic URL format validation
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(check_url):
            return False, "Invalid URL format"
        
        return True, "URL format is valid"
    
    def test_connection(self, url: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Test the API connection
        
        Returns:
            Tuple of (success, message, data)
        """
        test_url = url or self.api_url
        
        # First validate URL format
        is_valid, validation_msg = self.validate_url(test_url)
        if not is_valid:
            return False, validation_msg, None
        
        try:
            print(f"[DEBUG] Testing connection to: {test_url}")
            print(f"[DEBUG] Headers: {self.headers}")
            
            # Make the GET request
            response = requests.get(
                test_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            print(f"[DEBUG] Response Status Code: {response.status_code}")
            print(f"[DEBUG] Response Headers: {dict(response.headers)}")
            
            # Check if request was successful
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                data = response.json()
                print(f"[DEBUG] Response Data Type: {type(data)}")
                print(f"[DEBUG] Response Data: {json.dumps(data, indent=2)}")
                self.last_response = data
                return True, f"Connection successful! Status: {response.status_code}", data
            except json.JSONDecodeError:
                # If not JSON, return text content
                data = {"raw_response": response.text}
                print(f"[DEBUG] Non-JSON Response: {response.text[:500]}")  # First 500 chars
                self.last_response = data
                return True, f"Connection successful (non-JSON response). Status: {response.status_code}", data
                
        except Timeout:
            error_msg = f"Connection timeout after {self.timeout} seconds"
            print(f"[DEBUG] Error: {error_msg}")
            self.last_error = error_msg
            return False, error_msg, None
            
        except ConnectionError as e:
            error_msg = f"Connection failed: {str(e)}"
            print(f"[DEBUG] Error: {error_msg}")
            self.last_error = error_msg
            return False, error_msg, None
            
        except requests.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code} - {e.response.reason}"
            print(f"[DEBUG] Error: {error_msg}")
            try:
                error_data = e.response.json()
                print(f"[DEBUG] Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"[DEBUG] Error Response Text: {e.response.text[:500]}")
            self.last_error = error_msg
            return False, error_msg, None
            
        except RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"[DEBUG] Error: {error_msg}")
            self.last_error = error_msg
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[DEBUG] Error: {error_msg}")
            self.last_error = error_msg
            return False, error_msg, None
    
    def fetch_all(self, url: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch all data from the API
        
        Returns:
            The fetched data or None if failed
        """
        fetch_url = url or self.api_url
        
        if not fetch_url:
            print("[DEBUG] No URL specified for fetch_all")
            return None
        
        success, message, data = self.test_connection(fetch_url)
        
        if success:
            print(f"[DEBUG] Successfully fetched data from {fetch_url}")
            return data
        else:
            print(f"[DEBUG] Failed to fetch data: {message}")
            return None
    
    def get_last_response(self) -> Optional[Dict]:
        """Get the last successful response"""
        return self.last_response
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error


# Example usage and testing
if __name__ == "__main__":
    # Example API URLs for testing
    test_urls = [
        "https://jsonplaceholder.typicode.com/posts",
        "https://api.github.com/users/github",
        "invalid-url",
        "http://invalid.domain.test"
    ]
    
    api = APIConnection()
    
    for url in test_urls:
        print(f"\n{'='*50}")
        print(f"Testing: {url}")
        print('='*50)
        
        success, message, data = api.test_connection(url)
        print(f"Result: {'✓' if success else '✗'} {message}")
        
        if success and data:
            print(f"Data preview: {str(data)[:200]}...")