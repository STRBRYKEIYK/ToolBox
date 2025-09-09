"""
api_gui.py
GUI application for API connection management
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from datetime import datetime
from api_client import APIClient

class APIConnectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("API Connection Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize API client
        self.api_client = APIClient()
        
        # Store the current URL components
        self.current_base_url = tk.StringVar()
        self.current_route = tk.StringVar(value="/api/items")
        
        # Configure styles
        self.setup_styles()
        
        # Create the main interface
        self.create_widgets()
        
        # Center the window on screen
        self.center_window()
        
        # Bind Enter key to test connection
        self.root.bind('<Return>', lambda e: self.test_connection())
    
    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        bg_color = '#f0f0f0'
        self.root.configure(bg=bg_color)
        
        # Custom button style
        style.configure('Test.TButton', 
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.configure('Success.TLabel',
                       foreground='green',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Error.TLabel',
                       foreground='red',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Header.TLabel',
                       font=('Arial', 16, 'bold'))
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header
        header_label = ttk.Label(main_frame, 
                                text="API Connection Setup",
                                style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(main_frame,
                                text="Enter your API endpoint details below to establish a connection:",
                                font=('Arial', 10))
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Base URL Input Section
        base_url_label = ttk.Label(main_frame, text="Base URL:", font=('Arial', 10, 'bold'))
        base_url_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.base_url_entry = ttk.Entry(main_frame, 
                                      textvariable=self.current_base_url,
                                      font=('Arial', 10),
                                      width=50)
        self.base_url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Add placeholder text
        self.base_url_entry.insert(0, "https://api.example.com")
        self.base_url_entry.bind('<FocusIn>', self.on_base_url_click)
        self.base_url_entry.bind('<FocusOut>', self.on_base_url_focus_out)
        
        # Route Input Section
        route_label = ttk.Label(main_frame, text="API Route:", font=('Arial', 10, 'bold'))
        route_label.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        self.route_entry = ttk.Entry(main_frame, 
                                   textvariable=self.current_route,
                                   font=('Arial', 10),
                                   width=50)
        self.route_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Full URL preview
        url_preview_label = ttk.Label(main_frame, text="Full URL:", font=('Arial', 10, 'bold'))
        url_preview_label.grid(row=4, column=0, sticky=tk.W, pady=10)
        
        self.url_preview = ttk.Label(main_frame, 
                                   text="",
                                   font=('Arial', 10),
                                   wraplength=500)
        self.url_preview.grid(row=4, column=1, sticky=tk.W, pady=10, padx=(10, 0))
        
        # Bind to update preview
        self.current_base_url.trace("w", self.update_url_preview)
        self.current_route.trace("w", self.update_url_preview)
        
        # Test Connection Button
        self.test_button = ttk.Button(main_frame,
                                     text="Test Connection",
                                     command=self.test_connection,
                                     style='Test.TButton')
        self.test_button.grid(row=4, column=2, padx=(10, 0), pady=10)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        status_frame.columnconfigure(1, weight=1)
        
        # Status indicator
        self.status_label = ttk.Label(status_frame, text="Not Connected", font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status message
        self.status_message = ttk.Label(status_frame, text="", wraplength=600)
        self.status_message.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        
        # Response/Debug Section
        response_frame = ttk.LabelFrame(main_frame, text="Response / Debug Output", padding="10")
        response_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        
        # Response text area with scrollbar
        self.response_text = scrolledtext.ScrolledText(response_frame,
                                                      wrap=tk.WORD,
                                                      width=70,
                                                      height=15,
                                                      font=('Courier', 9))
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for response frame
        main_frame.rowconfigure(4, weight=1)
        
        # Button Frame for additional actions
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Clear button
        clear_button = ttk.Button(button_frame,
                                text="Clear Output",
                                command=self.clear_output)
        clear_button.grid(row=0, column=0, padx=5)
        
        # Save URL button
        self.save_button = ttk.Button(button_frame,
                                     text="Save & Continue",
                                     command=self.save_and_continue,
                                     state='disabled')
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Example URLs dropdown
        example_label = ttk.Label(button_frame, text="Examples:")
        example_label.grid(row=0, column=2, padx=(20, 5))
        # Route selection dropdown
        route_label = ttk.Label(button_frame, text="Common Routes:")
        route_label.grid(row=0, column=2, padx=(20, 5))
        
        self.routes = [
            "Select a route...",
            "/api/items",
            "/api/employees",
            "/api/users",
            "/api/orders",
            "/api/products"
        ]
        
        self.route_combo = ttk.Combobox(button_frame, 
                                      values=self.routes,
                                      state='readonly',
                                      width=20)
        self.route_combo.current(0)
        self.route_combo.grid(row=0, column=3, padx=5)
        self.route_combo.bind('<<ComboboxSelected>>', self.on_route_selected)
        
        # Example URLs dropdown
        example_label = ttk.Label(button_frame, text="Example URLs:")
        example_label.grid(row=0, column=4, padx=(20, 5))
        
        self.example_urls = [
            "Select an example...",
            "https://jsonplaceholder.typicode.com",
            "https://api.github.com",
            "https://httpbin.org",
            "https://pokeapi.co/api/v2"
        ]
        
        self.example_combo = ttk.Combobox(button_frame, 
                                         values=self.example_urls,
                                         state='readonly',
                                         width=30)
        self.example_combo.current(0)
        self.example_combo.grid(row=0, column=5, padx=5)
        self.example_combo.bind('<<ComboboxSelected>>', self.on_example_selected)
        
        # Initial URL preview update
        self.update_url_preview()
    
    def update_url_preview(self, *args):
        """Update the URL preview based on current base URL and route"""
        base = self.current_base_url.get().strip()
        route = self.current_route.get().strip()
        
        if not base:
            base = "https://api.example.com"
        
        if base and route:
            # Ensure base URL doesn't end with / and route starts with /
            base = base.rstrip('/')
            route = route if route.startswith('/') else f'/{route}'
            full_url = f"{base}{route}"
            self.url_preview.config(text=full_url)
        else:
            self.url_preview.config(text="")
    
    def on_base_url_click(self, event):
        """Handle base URL entry field click - clear placeholder"""
        if self.base_url_entry.get() == "https://api.example.com":
            self.base_url_entry.delete(0, tk.END)
    
    def on_base_url_focus_out(self, event):
        """Handle base URL entry field focus out - restore placeholder if empty"""
        if self.base_url_entry.get() == "":
            self.base_url_entry.insert(0, "https://api.example.com")
    
    def on_route_selected(self, event):
        """Handle route selection"""
        selected = self.route_combo.get()
        if selected != "Select a route...":
            self.current_route.set(selected)
            self.route_entry.delete(0, tk.END)
            self.route_entry.insert(0, selected)
            self.update_url_preview()
    
    def on_example_selected(self, event):
        """Handle example URL selection"""
        selected = self.example_combo.get()
        if selected != "Select an example...":
            self.current_base_url.set(selected)
            self.base_url_entry.delete(0, tk.END)
            self.base_url_entry.insert(0, selected)
            self.update_url_preview()
    
    def test_connection(self):
        """Test the API connection in a separate thread"""
        base_url = self.current_base_url.get().strip()
        route = self.current_route.get().strip()
        
        # Check if base URL is empty or is placeholder
        if not base_url or base_url == "https://api.example.com":
            messagebox.showwarning("Input Required", "Please enter a valid API base URL")
            return
        
        # Disable button and show progress
        self.test_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.progress.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        self.progress.start(10)
        
        # Update status
        self.status_label.config(text="Testing...", style='')
        self.status_message.config(text="Attempting to connect to the API...")
        
        # Clear previous output
        self.response_text.delete(1.0, tk.END)
        
        # Log to debug output
        self.log_debug(f"Starting connection test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_debug(f"Base URL: {base_url}")
        self.log_debug(f"Route: {route}")
        full_url = f"{base_url.rstrip('/')}{route if route.startswith('/') else '/' + route}"
        self.log_debug(f"Full URL: {full_url}")
        
        # Run test in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.test_connection_thread, args=(base_url, route))
        thread.daemon = True
        thread.start()
    
    def test_connection_thread(self, base_url, route):
        """Thread function to test connection"""
        try:
            # Configure the API client
            self.api_client.set_base_url(base_url)
            self.api_client.set_route(route)
            
            # Test the connection
            success, message, data = self.api_client.test_connection()
            
            # Update GUI in main thread
            self.root.after(0, self.update_connection_result, success, message, data)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.root.after(0, self.update_connection_result, False, error_msg, None)
    
    def update_connection_result(self, success, message, data):
        """Update GUI with connection test results"""
        # Stop progress bar
        self.progress.stop()
        self.progress.grid_remove()
        
        # Re-enable button
        self.test_button.config(state='normal')
        
        # Update status based on result
        if success:
            self.status_label.config(text="✓ Connected", style='Success.TLabel')
            self.status_message.config(text=message, style='Success.TLabel')
            self.save_button.config(state='normal')
            
            # Log success
            self.log_debug(f"SUCCESS: {message}")
            
            # Display response data
            if data:
                self.log_debug("\n" + "="*50)
                self.log_debug("RESPONSE DATA:")
                self.log_debug("="*50)
                
                try:
                    # Pretty print JSON data
                    formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
                    self.response_text.insert(tk.END, formatted_json)
                    
                    # Add data statistics
                    self.log_debug(f"\nData Statistics:")
                    if isinstance(data, list):
                        self.log_debug(f"  - Type: List")
                        self.log_debug(f"  - Items: {len(data)}")
                    elif isinstance(data, dict):
                        self.log_debug(f"  - Type: Dictionary")
                        self.log_debug(f"  - Keys: {len(data)}")
                        self.log_debug(f"  - Key names: {', '.join(data.keys())}")
                    
                except Exception as e:
                    self.log_debug(f"Error formatting response: {str(e)}")
                    self.response_text.insert(tk.END, str(data))
        else:
            self.status_label.config(text="✗ Not Connected", style='Error.TLabel')
            self.status_message.config(text=message, style='Error.TLabel')
            self.save_button.config(state='disabled')
            
            # Log error
            self.log_debug(f"ERROR: {message}")
            
            # Show troubleshooting tips
            self.log_debug("\n" + "="*50)
            self.log_debug("TROUBLESHOOTING TIPS:")
            self.log_debug("="*50)
            self.log_debug("1. Check if the URL is correct and complete")
            self.log_debug("2. Ensure you have an active internet connection")
            self.log_debug("3. Verify the API server is running and accessible")
            self.log_debug("4. Check if the API requires authentication")
            self.log_debug("5. Try the URL in a web browser to test accessibility")
    
    def log_debug(self, message):
        """Add debug message to the response text area"""
        self.response_text.insert(tk.END, f"\n{message}")
        self.response_text.see(tk.END)  # Auto-scroll to bottom
        self.root.update_idletasks()  # Force GUI update
    
    def clear_output(self):
        """Clear the response/debug output"""
        self.response_text.delete(1.0, tk.END)
        self.status_label.config(text="Not Connected", style='')
        self.status_message.config(text="", style='')
    
    def save_and_continue(self):
        """Save the validated URL and continue to main application"""
        base_url = self.current_base_url.get().strip()
        route = self.current_route.get().strip()
        
        if base_url and route and self.api_client.last_response:
            # Update API client config
            self.api_client.set_base_url(base_url)
            self.api_client.set_route(route)
            
            # Get the full URL for display
            full_url = self.api_client.get_api_url()
            
            # Here you can save the URL configuration
            messagebox.showinfo("Success", 
                              f"API connection saved!\n\n"
                              f"Base URL: {base_url}\n"
                              f"Route: {route}\n"
                              f"Full URL: {full_url}\n\n"
                              "The base URL can be updated daily while keeping the same route.")
            
            # Save config using the API client's built-in method
            try:
                success = self.api_client.save_config()
                
                if success:
                    self.log_debug("\n" + "="*50)
                    self.log_debug("CONFIGURATION SAVED")
                    self.log_debug("="*50)
                    self.log_debug(f"Config saved to: {self.api_client.config_file}")
                    self.log_debug(f"Base URL: {base_url}")
                    self.log_debug(f"Route: {route}")
                    self.log_debug("Ready to proceed with main application")
                else:
                    self.log_debug(f"Error saving config")
            except Exception as e:
                self.log_debug(f"Error saving config: {str(e)}")
        else:
            messagebox.showwarning("No Connection", 
                                  "Please test and validate the connection first.")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = APIConnectionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()