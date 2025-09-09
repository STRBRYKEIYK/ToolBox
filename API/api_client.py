"""
api_client.py
Comprehensive API client for handling connections and data operations
Manages changing base URLs, multiple routes, and HTTP methods
"""

import requests
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List, Union

class APIClient:
    def __init__(self, base_url: str = None, route: str = "/api/items", config_file: str = "api_config.json"):
        """
        Initialize API client
        
        Args:
            base_url: The base API URL (changes daily)
            route: The API route/endpoint (default is /api/items)
            config_file: Path to configuration file to store/retrieve API settings
        """
        self.base_url = base_url
        self.current_route = route
        self.timeout = 10  # Default timeout in seconds
        self.last_response = None
        self.last_error = None
        self.config_file = config_file
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Try to load config if file exists
        self._load_config()
    
    def _build_full_url(self, route: str = None) -> str:
        """
        Build the complete URL from base URL and route
        
        Args:
            route: The API route/endpoint (if different from current route)
        
        Returns:
            The complete API URL
        """
        if not self.base_url:
            return None
        
        use_route = route if route is not None else self.current_route
        
        # Ensure base URL doesn't end with / and route starts with /
        base = self.base_url.rstrip('/')
        route_path = use_route if use_route.startswith('/') else f'/{use_route}'
        
        return f"{base}{route_path}"
    
    def _load_config(self) -> bool:
        """
        Load API configuration from file
        
        Returns:
            True if config was loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Update properties from config
                    self.base_url = config.get('base_url', self.base_url)
                    self.current_route = config.get('route', self.current_route)
                    
                    # Optional: load custom headers if present
                    if 'headers' in config:
                        self.headers.update(config['headers'])
                    
                    print(f"Config loaded from {self.config_file}")
                    return True
            return False
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current API configuration to file
        
        Returns:
            True if config was saved successfully, False otherwise
        """
        try:
            config = {
                'base_url': self.base_url,
                'route': self.current_route,
                'headers': self.headers,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Config saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
    
    def set_base_url(self, url: str) -> None:
        """
        Set or update the base API URL
        
        Args:
            url: The new base URL
        """
        self.base_url = url.strip()
    
    def get_base_url(self) -> str:
        """
        Get the current base API URL
        
        Returns:
            The base URL
        """
        return self.base_url
    
    def set_route(self, route: str) -> None:
        """
        Set or update the API route/endpoint
        
        Args:
            route: The API route (e.g., '/api/items', '/api/employees')
        """
        self.current_route = route.strip()
    
    def get_route(self) -> str:
        """
        Get the current API route
        
        Returns:
            The current route
        """
        return self.current_route
    
    def get_api_url(self, route: str = None) -> str:
        """
        Get the complete API URL (base URL + route)
        
        Args:
            route: Optional route override
            
        Returns:
            The complete API URL
        """
        return self._build_full_url(route)
    
    def set_url(self, url: str) -> None:
        """
        Set the complete API URL (parses into base_url and route)
        
        Args:
            url: The complete API URL
        """
        self.api_url = url.strip()
        # Try to split into base and route
        if '/api/' in url:
            parts = url.split('/api/')
            self.base_url = parts[0]
            self.current_route = '/api/' + parts[1]
        else:
            # If we can't parse, just set the base_url
            self.base_url = url
    
    def validate_url(self, url: str = None) -> Tuple[bool, str]:
        """
        Validate if the URL format is correct
        
        Args:
            url: URL to validate (uses current URL if None)
            
        Returns:
            Tuple of (is_valid, message)
        """
        check_url = url or self._build_full_url()
        
        if not check_url:
            return False, "No URL provided"
        
        if not check_url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        # Basic URL format validation
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
    
    def request(self, method: str, route: str = None, data: Dict = None, params: Dict = None, 
              headers: Dict = None) -> Tuple[bool, Any, Dict]:
        """
        Make an API request with specified method
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            route: API route/endpoint (uses current_route if None)
            data: Data to send in the request body (for POST, PUT, etc.)
            params: URL parameters to include
            headers: Additional headers to include
            
        Returns:
            Tuple of (success, data, response_info)
        """
        url = self._build_full_url(route)
        if not url:
            return False, None, {"error": "No valid URL available"}
        
        # Merge headers
        request_headers = dict(self.headers)
        if headers:
            request_headers.update(headers)
        
        try:
            print(f"[API] {method} request to: {url}")
            
            # Make the request based on method
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=request_headers, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, params=params, headers=request_headers, timeout=self.timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, params=params, headers=request_headers, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=request_headers, timeout=self.timeout)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, params=params, headers=request_headers, timeout=self.timeout)
            else:
                return False, None, {"error": f"Unsupported HTTP method: {method}"}
            
            # Check response status
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # Return text content if not JSON
                response_data = response.text
            
            # Save as last response
            self.last_response = response_data
            
            # Create response info dict
            response_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": response.url,
                "elapsed": str(response.elapsed),
                "content_type": response.headers.get('Content-Type', '')
            }
            
            return True, response_data, response_info
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            self.last_error = error_msg
            
            error_info = {
                "error": error_msg,
                "error_type": type(e).__name__,
                "url": url
            }
            
            # Add response info if available
            if hasattr(e, 'response') and e.response:
                error_info.update({
                    "status_code": e.response.status_code,
                    "reason": e.response.reason
                })
                
                # Try to get error details from JSON response if available
                try:
                    error_info["response_body"] = e.response.json()
                except:
                    error_info["response_body"] = e.response.text[:200] + "..." if len(e.response.text) > 200 else e.response.text
            
            print(f"[API] Request error: {error_msg}")
            return False, None, error_info
    
    def test_connection(self, url: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Test the API connection
        
        Args:
            url: Optional specific URL to test (uses current URL if None)
            
        Returns:
            Tuple of (success, message, data)
        """
        # If a specific URL is provided, use it directly
        if url:
            # First validate URL format
            is_valid, validation_msg = self.validate_url(url)
            if not is_valid:
                return False, validation_msg, None
                
            try:
                print(f"[DEBUG] Testing connection to: {url}")
                
                # Make the GET request
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                print(f"[DEBUG] Response Status Code: {response.status_code}")
                
                # Check if request was successful
                response.raise_for_status()
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    self.last_response = data
                    return True, f"Connection successful! Status: {response.status_code}", data
                except json.JSONDecodeError:
                    # If not JSON, return text content
                    data = {"raw_response": response.text}
                    self.last_response = data
                    return True, f"Connection successful (non-JSON response). Status: {response.status_code}", data
            
            except Exception as e:
                error_msg = f"Connection failed: {str(e)}"
                self.last_error = error_msg
                return False, error_msg, None
        
        # Otherwise, use the current route
        else:
            test_route = self.current_route
            test_url = self._build_full_url(test_route)
            
            if not test_url:
                return False, "No valid URL configured", None
            
            success, data, response_info = self.request('GET', test_route)
            
            if success:
                status_code = response_info.get('status_code')
                return True, f"Connection successful! Status: {status_code}", data
            else:
                error_msg = response_info.get('error', 'Unknown error')
                status_code = response_info.get('status_code', 'N/A')
                return False, f"Connection failed: {error_msg} (Status: {status_code})", None
    
    def fetch_items_data(self, route: str = None) -> Tuple[List[Dict], Dict]:
        """
        Fetch items data from the API
        
        Args:
            route: Optional route override (default uses current_route)
            
        Returns:
            tuple: A tuple containing (items_data, full_response)
            - items_data: A list of item dictionaries
            - full_response: The full API response for accessing metadata
        """
        all_items = []
        latest_response = None
        
        # Use provided route or default to items route
        api_route = route or self.current_route
        
        # Make the initial request
        success, data, response_info = self.request('GET', api_route)
        
        if not success:
            print(f"Error fetching data from API: {response_info.get('error')}")
            # Return sample data as fallback
            sample_data = [
                {"item_name": "Sample Item 1", "brand": "Sample Brand", "item_type": "Demo", "balance": 5},
                {"item_name": "Sample Item 2", "brand": "Another Brand", "item_type": "Demo", "balance": 10}
            ]
            return sample_data, {'data': sample_data}
        
        latest_response = data
        
        # Debug the response format
        print(f"API Response: {json.dumps(data, indent=2) if isinstance(data, (dict, list)) else data}")
        
        # Check if we have pagination info
        if isinstance(data, dict) and 'success' in data and data['success'] and 'pagination' in data:
            pagination = data['pagination']
            total_pages = pagination.get('pages', 1)
            
            # Extract items from the first page
            if 'data' in data:
                all_items.extend(data['data'])
            
            # Fetch remaining pages
            for page in range(2, total_pages + 1):
                page_params = {"page": page}
                page_success, page_data, page_info = self.request('GET', api_route, params=page_params)
                
                if page_success and isinstance(page_data, dict) and 'success' in page_data and page_data['success'] and 'data' in page_data:
                    all_items.extend(page_data['data'])
                else:
                    print(f"Error fetching page {page}: {page_info.get('error', 'Unknown error')}")
        
        # If we didn't get multiple pages but have data in standard format
        elif isinstance(data, dict) and 'success' in data and data['success'] and 'data' in data and not all_items:
            all_items = data['data']
        elif isinstance(data, dict) and 'items' in data and not all_items:
            all_items = data['items']
        elif isinstance(data, list) and not all_items:
            all_items = data
            
        if all_items:
            return all_items, latest_response
        else:
            print("Unexpected data format or no items found")
            # Return sample data as fallback
            sample_data = [
                {"item_name": "Sample Item 1", "brand": "Sample Brand", "item_type": "Demo", "balance": 5},
                {"item_name": "Sample Item 2", "brand": "Another Brand", "item_type": "Demo", "balance": 10}
            ]
            return sample_data, {'data': sample_data}
    
    def get_data(self, route: str = None, params: Dict = None) -> Tuple[bool, Any, Dict]:
        """
        Make a GET request to fetch data
        
        Args:
            route: The API route/endpoint
            params: URL parameters
            
        Returns:
            Tuple of (success, data, response_info)
        """
        return self.request('GET', route, params=params)
    
    def create_item(self, data: Dict, route: str = None) -> Tuple[bool, Any, Dict]:
        """
        Make a POST request to create a new item
        
        Args:
            data: The data for the new item
            route: The API route/endpoint
            
        Returns:
            Tuple of (success, data, response_info)
        """
        return self.request('POST', route, data=data)
    
    def update_item(self, data: Dict, route: str = None) -> Tuple[bool, Any, Dict]:
        """
        Make a PUT request to update an item
        
        Args:
            data: The updated data
            route: The API route/endpoint
            
        Returns:
            Tuple of (success, data, response_info)
        """
        return self.request('PUT', route, data=data)
    
    def patch_item(self, data: Dict, route: str = None) -> Tuple[bool, Any, Dict]:
        """
        Make a PATCH request to partially update an item
        
        Args:
            data: The fields to update
            route: The API route/endpoint
            
        Returns:
            Tuple of (success, data, response_info)
        """
        return self.request('PATCH', route, data=data)
    
    def delete_item(self, route: str = None, item_id: str = None) -> Tuple[bool, Any, Dict]:
        """
        Make a DELETE request to remove an item
        
        Args:
            route: The API route/endpoint
            item_id: The ID of the item to delete
            
        Returns:
            Tuple of (success, data, response_info)
        """
        if item_id and not route:
            # If only item_id is provided, append to current route
            full_route = f"{self.current_route}/{item_id}"
            return self.request('DELETE', full_route)
        else:
            return self.request('DELETE', route)
    
    def get_last_response(self) -> Optional[Dict]:
        """Get the last successful response"""
        return self.last_response
    
    def get_last_error(self) -> Optional[str]:
        """Get the last error message"""
        return self.last_error
    
    def format_json(self, data: Any) -> str:
        """
        Format data as a pretty-printed JSON string
        
        Args:
            data: The data to format
            
        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    
    def fetch_employees(self) -> Tuple[List[Dict], Dict]:
        """
        Fetch employees data from the API
        
        Returns:
            tuple: A tuple containing (employees_data, full_response)
        """
        # Temporarily switch to employees route
        original_route = self.current_route
        self.set_route('/api/employees')
        
        try:
            employees, response = self.fetch_items_data()
            return employees, response
        finally:
            # Restore original route
            self.set_route(original_route)


# Example usage
if __name__ == "__main__":
    # Example API URLs for testing
    base_url = "https://api.example.com"
    
    # Initialize API client
    api = APIClient(base_url)
    api.set_route('/api/items')  # Set default route
    
    print(f"Base URL: {api.get_base_url()}")
    print(f"Current Route: {api.get_route()}")
    print(f"Full API URL: {api.get_api_url()}")
    
    # Test connection
    print("\nTesting API connection...")
    success, message, data = api.test_connection()
    print(f"Connection test result: {'✓' if success else '✗'} {message}")
    
    if success:
        # Fetch items
        print("\nFetching items data...")
        items, response = api.fetch_items_data()
        print(f"Fetched {len(items)} items")
        
        # Display a few items
        for i, item in enumerate(items[:3]):
            print(f"Item {i+1}: {item}")
        
        if len(items) > 3:
            print(f"... and {len(items)-3} more items")
