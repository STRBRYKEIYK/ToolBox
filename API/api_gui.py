"""
api_gui.py
GUI application for API connection management
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from datetime import datetime
from api_connection import APIConnection

class APIConnectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("API Connection Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize API connection handler
        self.api_connection = APIConnection()
        
        # Store the current API URL
        self.current_url = tk.StringVar()
        
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
                                text="Enter your API endpoint URL below to establish a connection:",
                                font=('Arial', 10))
        instructions.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # URL Input Section
        url_label = ttk.Label(main_frame, text="API URL:", font=('Arial', 10, 'bold'))
        url_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        self.url_entry = ttk.Entry(main_frame, 
                                  textvariable=self.current_url,
                                  font=('Arial', 10),
                                  width=50)
        self.url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        # Add placeholder text
        self.url_entry.insert(0, "https://api.example.com/endpoint")
        self.url_entry.bind('<FocusIn>', self.on_entry_click)
        self.url_entry.bind('<FocusOut>', self.on_focus_out)
        
        # Test Connection Button
        self.test_button = ttk.Button(main_frame,
                                     text="Test Connection",
                                     command=self.test_connection,
                                     style='Test.TButton')
        self.test_button.grid(row=2, column=2, padx=(10, 0), pady=10)
        
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
        
        self.example_urls = [
            "Select an example...",
            "https://jsonplaceholder.typicode.com/posts",
            "https://jsonplaceholder.typicode.com/users",
            "https://api.github.com/users/github",
            "https://httpbin.org/get",
            "https://pokeapi.co/api/v2/pokemon/ditto"
        ]
        
        self.example_combo = ttk.Combobox(button_frame, 
                                         values=self.example_urls,
                                         state='readonly',
                                         width=40)
        self.example_combo.current(0)
        self.example_combo.grid(row=0, column=3, padx=5)
        self.example_combo.bind('<<ComboboxSelected>>', self.on_example_selected)
    
    def on_entry_click(self, event):
        """Handle entry field click - clear placeholder"""
        if self.url_entry.get() == "https://api.example.com/endpoint":
            self.url_entry.delete(0, tk.END)
    
    def on_focus_out(self, event):
        """Handle entry field focus out - restore placeholder if empty"""
        if self.url_entry.get() == "":
            self.url_entry.insert(0, "https://api.example.com/endpoint")
    
    def on_example_selected(self, event):
        """Handle example URL selection"""
        selected = self.example_combo.get()
        if selected != "Select an example...":
            self.current_url.set(selected)
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, selected)
    
    def test_connection(self):
        """Test the API connection in a separate thread"""
        url = self.current_url.get().strip()
        
        # Check if URL is empty or is placeholder
        if not url or url == "https://api.example.com/endpoint":
            messagebox.showwarning("Input Required", "Please enter a valid API URL")
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
        self.log_debug(f"Target URL: {url}")
        
        # Run test in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.test_connection_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def test_connection_thread(self, url):
        """Thread function to test connection"""
        try:
            # Set the URL in the API connection
            self.api_connection.set_url(url)
            
            # Test the connection
            success, message, data = self.api_connection.test_connection(url)
            
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
        url = self.current_url.get().strip()
        
        if url and self.api_connection.last_response:
            # Here you can save the URL to a config file or pass it to the next screen
            messagebox.showinfo("Success", 
                              f"API connection saved!\n\nURL: {url}\n\n"
                              "You can now proceed to use the API in your application.")
            
            # You can add code here to:
            # 1. Save URL to a configuration file
            # 2. Open the main application window
            # 3. Pass the API connection object to other modules
            
            self.log_debug("\n" + "="*50)
            self.log_debug("CONNECTION SAVED SUCCESSFULLY")
            self.log_debug("="*50)
            self.log_debug(f"Saved URL: {url}")
            self.log_debug("Ready to proceed with main application")
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