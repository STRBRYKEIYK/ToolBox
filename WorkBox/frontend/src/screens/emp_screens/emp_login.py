
"""
Employee Login Screen

This module provides the login interface for employees to access the WorkBox system.
"""

import sys
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox, StringVar

# Add parent directory to path to allow importing from src
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent
sys.path.insert(0, str(src_dir))

# Import local modules after adding to path
from backend.auth import AuthenticationManager  # noqa: E402
from utils.path_utils import get_relative_asset_path  # noqa: E402


class LoginScreen:
    """
    Employee login screen with UI and authentication handling.
    """
    
    def __init__(self, root=None, on_successful_login=None):
        """
        Initialize the login screen.
        
        Args:
            root (Tk, optional): The Tkinter root window. If None, a new one will be created.
            on_successful_login (function, optional): Callback function to call after successful login.
        """
        # Initialize authentication manager
        self.auth_manager = AuthenticationManager()
        
        # Setup the root window
        self.root = root or Tk()
        self.root.title("WorkBox - Employee Login")
        self.root.geometry("1920x1080")
        self.root.configure(bg="#FFFFFF")
        
        # Callback for after login
        self.on_successful_login = on_successful_login
        
        # Setup UI elements
        self.canvas = Canvas(
            self.root,
            bg="#FFFFFF",
            height=1080,
            width=1920,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)
        
        # Track login status variables
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.remember_password = False
        
        # Load UI assets and build the interface
        self._load_assets()
        self._build_ui()


    def _load_assets(self):
        """Load all image assets needed for the UI"""
        # Define the assets directory
        self.asset_path = get_relative_asset_path('emp_screens', 'login_assets', '')
        
        # Load all images
        self.image_1 = PhotoImage(file=self.asset_path / "image_1.png")
        self.image_2 = PhotoImage(file=self.asset_path / "image_2.png")
        self.image_3 = PhotoImage(file=self.asset_path / "image_3.png")
        self.image_4 = PhotoImage(file=self.asset_path / "image_4.png")
        
        self.button_1_img = PhotoImage(file=self.asset_path / "button_1.png")
        self.button_2_img = PhotoImage(file=self.asset_path / "button_2.png")
        
        self.entry_1_img = PhotoImage(file=self.asset_path / "entry_1.png")
        self.entry_2_img = PhotoImage(file=self.asset_path / "entry_2.png")
    
    def _build_ui(self):
        """Build the UI elements"""
        # Background images
        self.image_1_obj = self.canvas.create_image(433.0, 540.0, image=self.image_1)
        self.image_2_obj = self.canvas.create_image(1393.0, 540.0, image=self.image_2)
        self.image_4_obj = self.canvas.create_image(433.0, 540.0, image=self.image_4)
        
        # Create username entry
        self.username_entry_bg = self.canvas.create_image(1382.0, 339.0, image=self.entry_2_img)
        self.username_entry = Entry(
            self.root,
            textvariable=self.username_var,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0,
            font=("Arial", 25)
        )
        self.username_entry.place(x=1013.0, y=305.0, width=738.0, height=70.0)
        
        # Username label
        self.canvas.create_text(
            993.0, 245.0,
            anchor="nw",
            text="Username:",
            fill="#FFFFFF",
            font=("CormorantGaramond Bold", 36 * -1)
        )
        
        # Create password entry
        self.password_entry_bg = self.canvas.create_image(1382.0, 543.5, image=self.entry_1_img)
        self.password_entry = Entry(
            self.root,
            textvariable=self.password_var,
            bd=0,
            bg="#D9D9D9",
            fg="#000716",
            highlightthickness=0,
            font=("Arial", 25),
            show="●"  # Use bullet character for password
        )
        self.password_entry.place(x=1013.0, y=505.0, width=738.0, height=70.0)
        
        # Password label
        self.canvas.create_text(
            993.0, 449.0,
            anchor="nw",
            text="Password:",
            fill="#FFFFFF",
            font=("CormorantGaramond Bold", 36 * -1)
        )
        
        # Remember password checkbox (using an image instead of a real checkbox for design consistency)
        self.remember_img_obj = self.canvas.create_image(1010.0, 648.0, image=self.image_3)
        self.canvas.create_text(
            1060.0, 631.0,
            anchor="nw",
            text="Remember Password",
            fill="#FFFFFF",
            font=("CormorantGaramond Regular", 32 * -1)
        )
        
        # Make the checkbox clickable by adding a tag and binding to it
        self.canvas.tag_bind(self.remember_img_obj, "<Button-1>", self.toggle_remember)
        
        # Login button
        self.login_button = Button(
            self.root,
            image=self.button_2_img,
            borderwidth=0,
            highlightthickness=0,
            bg="#2B2B2B",
            activebackground="#2B2B2B",            
            command=self.handle_login,
            relief="flat"
        )
        self.login_button.place(
            x=993.0,
            y=707.998291015625,
            width=778.0,
            height=70.73445892333984
        )
        
        # Forgot password button
        self.forgot_button = Button(
            self.root,
            image=self.button_1_img,
            borderwidth=0,
            highlightthickness=0,
            bg="#2B2B2B",
            activebackground="#2B2B2B",
            command=self.handle_forgot_password,
            relief="flat"
        )
        self.forgot_button.place(
            x=1284.0,
            y=799.0,
            width=217.0,
            height=36.0
        )
        
        # Set window properties
        self.root.resizable(False, False)
        
        # Bind Enter key to login
        self.root.bind("<Return>", lambda event: self.handle_login())
    
    def toggle_remember(self, event=None):
        """Toggle the remember password setting"""
        self.remember_password = not self.remember_password
        # Could change the image here to show checked/unchecked state
        # For now, we'll just print the state
        print(f"Remember password: {self.remember_password}")
    
    def handle_login(self):
        """Handle the login button click"""
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        # Attempt to login
        success, message, user_data = self.auth_manager.login(username, password)
        
        if success:
            messagebox.showinfo("Success", f"Welcome back, {user_data.get('name', username)}!")
            
            # Call the callback function if provided
            if self.on_successful_login:
                self.on_successful_login(user_data)
            else:
                # For demonstration, just print the user data
                print(f"Logged in as: {user_data}")
                self.root.destroy()  # Close login window
                
        else:
            messagebox.showerror("Login Failed", message)
    
    def handle_forgot_password(self):
        """Handle the forgot password button click"""
        messagebox.showinfo("Forgot Password", 
                           "Please contact your administrator to reset your password.")
    
    def run(self):
        """Run the login screen"""
        self.root.mainloop()


# When run directly, create and show the login screen
if __name__ == "__main__":
    login_screen = LoginScreen()
    login_screen.run()
