import requests
import json

def fetch_items_data():
    """
    Fetch items data from the API
    
    Returns:
        tuple: A tuple containing (items_data, full_response)
        - items_data: A list of item dictionaries
        - full_response: The full API response for accessing metadata
    """
    api_url = "https://specialists-reuters-kay-catalogue.trycloudflare.com/api/items"
    all_items = []
    latest_response = None
    
    try:
        # First request to get pagination info
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_response = data
        
        # Debug the response format
        print(f"API Response: {json.dumps(data, indent=2)}")
        
        # Check if we have pagination info
        if isinstance(data, dict) and 'success' in data and data['success'] and 'pagination' in data:
            pagination = data['pagination']
            total_pages = pagination.get('pages', 1)
            
            # Extract items from the first page
            if 'data' in data:
                all_items.extend(data['data'])
            
            # Fetch remaining pages
            for page in range(2, total_pages + 1):
                try:
                    page_url = f"{api_url}?page={page}"
                    page_response = requests.get(page_url, timeout=10)
                    page_response.raise_for_status()
                    
                    page_data = page_response.json()
                    if isinstance(page_data, dict) and 'success' in page_data and page_data['success'] and 'data' in page_data:
                        all_items.extend(page_data['data'])
                        
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching page {page}: {e}")
                    # Continue with what we have
        
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
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        # Return sample data as fallback
        sample_data = [
            {"item_name": "Sample Item 1", "brand": "Sample Brand", "item_type": "Demo", "balance": 5},
            {"item_name": "Sample Item 2", "brand": "Another Brand", "item_type": "Demo", "balance": 10}
        ]
        return sample_data, {'data': sample_data}
