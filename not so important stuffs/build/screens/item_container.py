from tkinter import Frame, Canvas, Scrollbar, Label

class Item_container:
    def __init__(self, parent_window, center_x, center_y, image_width, image_height, bg_color="#426076"):
        """
        Initialize a scrollable container for item cards.
        
        Parameters:
        - parent_window: The parent window/widget
        - center_x, center_y: The center position for the container
        - image_width, image_height: The dimensions of the background image
        - bg_color: Background color for the container
        """
        self.parent = parent_window
        self.bg_color = bg_color
        
        # Add consistent padding (30px on all sides)
        self.padding = 30
        self.container_width = image_width - (self.padding * 2)
        self.container_height = image_height - (self.padding * 2)
        
        # Calculate position based on center coordinates
        self.x = center_x - (self.container_width // 2)
        self.y = center_y - (self.container_height // 2)
        
        # Create the main container frame
        self.container_frame = Frame(self.parent, bg=self.bg_color, 
                                    width=self.container_width, 
                                    height=self.container_height)
        self.container_frame.place(x=self.x, y=self.y)
        self.container_frame.pack_propagate(False)  # Prevent auto-resizing
        
        # Create scrolling canvas
        self.scroll_canvas = Canvas(self.container_frame, 
                                   bg=self.bg_color, 
                                   width=self.container_width-20, 
                                   height=self.container_height,
                                   highlightthickness=0, 
                                   bd=0)
        
        # Create scrollbar
        self.scrollbar = Scrollbar(self.container_frame, 
                                  orient="vertical", 
                                  command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Position scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        
        # Ensure canvas responds to size changes
        self.container_frame.update_idletasks()
        
        # Create a frame to hold the item cards
        self.items_frame = Frame(self.scroll_canvas, 
                               bg=self.bg_color, 
                               width=self.container_width-20)
        
        # Add the items_frame to the canvas
        self.canvas_window = self.scroll_canvas.create_window(
            (0, 0), 
            window=self.items_frame, 
            anchor="nw"
        )
        
        # Configure scrolling
        self.items_frame.bind("<Configure>", self._configure_scroll_region)
        
        # Set initial scroll region
        self.parent.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
    
    def _configure_scroll_region(self, event):
        """Configure the scroll region whenever the items_frame changes size"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        # Force items_frame to be the correct width
        self.scroll_canvas.itemconfig(
            self.canvas_window, 
            width=self.container_width-20
        )
    
    def add_item_card(self, item_name, item_desc, item_category, item_type, balance, on_view_click=None):
        """
        Add an item card to the scrollable container.
        
        Parameters:
        - item_name: The name of the item
        - item_desc: Item description
        - item_category: Category of the item
        - item_type: Type of the item
        - balance: Balance/stock of the item
        - on_view_click: Callback function for the view button click
        """
        # Calculate card dimensions
        card_width = self.container_width - 30
        card_height = 250
        
        # Create card frame
        card_frame = Frame(self.items_frame, bg="#D9D9D9", width=card_width, height=card_height)
        card_frame.pack(pady=10, padx=10, fill="x", expand=False)
        card_frame.pack_propagate(False)
        
        # Left side: Image placeholder
        img_placeholder = Frame(card_frame, bg="white", width=200, height=200)
        img_placeholder.place(x=25, y=(card_height - 200) // 2)
        
        # Add "Image here" label to placeholder
        Label(img_placeholder, text="Image here", bg="white").place(
            relx=0.5, 
            rely=0.5, 
            anchor="center"
        )
        
        # Right side: Info frame
        info_width = card_width - 275
        info_frame = Frame(card_frame, bg="#666666", width=info_width, height=200)
        info_frame.place(x=250, y=(card_height - 200) // 2)
        
        # Add text information
        Label(info_frame, text=f"Item Name: {item_name}", 
             bg="#666666", fg="white", anchor="w", 
             font=("Inter", 12, "bold")).place(
            x=10, 
            y=10, 
            width=min(900, info_width - 150)
        )
        
        Label(info_frame, text=f"{item_desc}", 
             bg="#666666", fg="white", anchor="w", 
             font=("Inter", 10)).place(
            x=10, 
            y=40, 
            width=min(900, info_width - 150)
        )
        
        Label(info_frame, text=f"Balance: {balance}", 
             bg="#666666", fg="white", anchor="e", 
             font=("Inter", 12, "bold")).place(
            x=min(info_width - 140, 900), 
            y=10, 
            width=100
        )
        
        Label(info_frame, text=f"Category: {item_category}", 
             bg="#666666", fg="white", anchor="w", 
             font=("Inter", 10)).place(
            x=10, 
            y=120, 
            width=min(300, info_width - 20)
        )
        
        Label(info_frame, text=f"Item Type: {item_type}", 
             bg="#666666", fg="white", anchor="w", 
             font=("Inter", 10)).place(
            x=10, 
            y=150, 
            width=min(300, info_width - 20)
        )
        
        # Add view button
        button_size = 50
        button_x = max(20, min(info_width - button_size - 20, info_width - button_size - 20))
        
        button_frame = Frame(info_frame, bg="#3498db", width=button_size, height=button_size)
        button_frame.place(x=button_x, y=(200 - button_size) // 2)
        
        # Add ">" symbol
        view_label = Label(button_frame, text=">", bg="#3498db", fg="white", 
                          font=("Inter", 24, "bold"))
        view_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add click functionality if provided
        if on_view_click:
            view_label.bind("<Button-1>", lambda e: on_view_click(item_name))
            button_frame.bind("<Button-1>", lambda e: on_view_click(item_name))
        
        return card_frame
    
    def clear_items(self):
        """Remove all item cards from the container"""
        for widget in self.items_frame.winfo_children():
            widget.destroy()
