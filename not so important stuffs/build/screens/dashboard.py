from pathlib import Path
import threading

# from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox

# Import the Item_container class
from item_container import Item_container
# Import the API utilities
from api_utils import fetch_items_data


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets/frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1920x1080")
window.attributes('-fullscreen', True)  # Set to fullscreen mode
window.configure(bg = "#426076")


canvas = Canvas(
    window,
    bg = "#426076",
    height = 1080,
    width = 1920,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    1129.0,
    603.0,
    image=image_image_1
)

# Create an instance of the Item_container class
# Using the dimensions and position of image_1
item_container = Item_container(
    parent_window=window,
    center_x=1129.0,    # Image 1's center x position
    center_y=603.0,     # Image 1's center y position
    image_width=1509,   # Image 1's width (1509px)
    image_height=868    # Image 1's height (868px)
)

# Function to handle "View" button clicks
def on_view_item(item_name):
    print(f"Viewing details for: {item_name}")
    messagebox.showinfo("Item Details", f"Viewing details for: {item_name}")
    # Here you would typically open a detail view or perform other actions

# Status text for loading
loading_text = canvas.create_text(
    1129.0, 
    603.0,
    text="Loading items...",
    fill="white",
    font=("Inter Bold", 20)
)

# Function to fetch data and populate the container
def load_items_data():
    # Fetch data from the API - now returns a tuple with (items_data, full_response)
    items_data, full_response = fetch_items_data()
    
    # Remove loading text once data is fetched
    canvas.delete(loading_text)
    
    # Check if we got any data
    if not items_data:
        error_text = canvas.create_text(
            1129.0, 
            603.0,
            text="Failed to load items. Please try again later.",
            fill="white",
            font=("Inter Bold", 20)
        )
        return
    
    # Update the items count
    items_count_text = canvas.find_withtag("items_count")
    if items_count_text:
        canvas.itemconfig(items_count_text[0], text=f"{len(items_data)} Items")
        
    # Update the "All Items" text with the total count from statistics if available
    all_items_text = canvas.find_withtag("all_items_text")
    if all_items_text:
        total_items = len(items_data)
        # Check if we have statistics in the full response
        if isinstance(full_response, dict):
            # Check if statistics is directly in the response
            if 'statistics' in full_response:
                total_items = full_response['statistics'].get('total_items', len(items_data))
            # Check if it's nested under pagination
            elif 'pagination' in full_response and 'total' in full_response['pagination']:
                total_items = full_response['pagination']['total']
                
        canvas.itemconfig(all_items_text[0], text=f"All Items ({total_items})")
    
    # Populate the container with the fetched items
    for item in items_data:
        # Handle case where item might be a string or other format
        if isinstance(item, dict):
            item_name = item.get("item_name", "Unnamed Item")
            item_desc = f"Brand: {item.get('brand', 'Unknown')}"
            if item.get("supplier"):
                item_desc += f" | Supplier: {item.get('supplier')}"
            
            item_category = f"Location: {item.get('location', 'Unknown')}"
            item_type = item.get("item_type", "Unknown Type")
            balance = str(item.get("balance", "0"))
            
            # Add price info if available
            price = item.get("price_per_unit", 0)
            if price:
                item_desc += f" | Price: ${price}"
                
            # Add status info
            status = item.get("item_status", "")
            if status:
                item_desc += f" | Status: {status}"
        elif isinstance(item, str):
            item_name = item
            item_desc = "No description available"
            item_category = "Uncategorized"
            item_type = "Unknown Type"
            balance = "0"
        else:
            item_name = str(item)
            item_desc = "No description available"
            item_category = "Uncategorized"
            item_type = "Unknown Type"
            balance = "0"
            
        item_container.add_item_card(
            item_name=item_name,
            item_desc=item_desc,
            item_category=item_category,
            item_type=item_type,
            balance=balance,
            on_view_click=on_view_item
        )

# Start loading data in a separate thread to keep UI responsive
threading.Thread(target=load_items_data, daemon=True).start()

button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_1 clicked"),
    relief="flat"
)
button_1.place(
    x=1845.0,
    y=107.0,
    width=40.0,
    height=40.0
)

button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_2 clicked"),
    relief="flat"
)
button_2.place(
    x=1783.0,
    y=107.0,
    width=40.0,
    height=40.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_3 clicked"),
    relief="flat"
)
button_3.place(
    x=1535.0,
    y=108.0,
    width=226.0,
    height=37.0
)

image_image_2 = PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    656.0,
    123.0,
    image=image_image_2
)

canvas.create_text(
    609.3927001953125,
    105.0,
    anchor="nw",
    text="0 Items",
    fill="#000000",
    font=("Inter SemiBold", 16 * -1),
    tags="items_count"
)

canvas.create_text(
    364.0,
    106.0,
    anchor="nw",
    text="All Items",
    fill="#FFFFFF",
    font=("Inter Black", 32 * -1),
    tags="all_items_text"
)

image_image_3 = PhotoImage(
    file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    174.0,
    574.0,
    image=image_image_3
)

image_image_4 = PhotoImage(
    file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    174.0,
    900.0,
    image=image_image_4
)

button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_4 clicked"),
    relief="flat"
)
button_4.place(
    x=49.0,
    y=936.7060546875,
    width=250.0,
    height=35.0
)

entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    174.0,
    892.0,
    image=entry_image_1
)
entry_1 = Entry(
    bd=0,
    bg="#FFFFFF",
    fg="#000716",
    highlightthickness=0
)
entry_1.place(
    x=59.0,
    y=872.0,
    width=230.0,
    height=38.0
)

image_image_5 = PhotoImage(
    file=relative_to_assets("image_5.png"))
image_5 = canvas.create_image(
    174.0,
    695.0,
    image=image_image_5
)

button_image_5 = PhotoImage(
    file=relative_to_assets("button_5.png"))
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_5 clicked"),
    relief="flat"
)
button_5.place(
    x=39.0,
    y=724.0,
    width=275.0,
    height=19.0
)

button_image_6 = PhotoImage(
    file=relative_to_assets("button_6.png"))
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: print("button_6 clicked"),
    relief="flat"
)
button_6.place(
    x=39.0,
    y=685.0,
    width=275.0,
    height=19.0
)

image_image_6 = PhotoImage(
    file=relative_to_assets("image_6.png"))
image_6 = canvas.create_image(
    174.0,
    385.0,
    image=image_image_6
)

image_image_7 = PhotoImage(
    file=relative_to_assets("image_7.png"))
image_7 = canvas.create_image(
    960.0,
    45.0,
    image=image_image_7
)

button_image_7 = PhotoImage(
    file=relative_to_assets("button_7.png"))
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    bg="#4D4C4D",
    activebackground="#4D4C4D",
    command=lambda: print("button_7 clicked"),
    relief="flat"
)
button_7.place(
    x=1648.0,
    y=10.0,
    width=60.0,
    height=60.0
)

button_image_8 = PhotoImage(
    file=relative_to_assets("button_8.png"))
button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    bg="#4D4C4D",
    activebackground="#4D4C4D",
    command=lambda: print("button_8 clicked"),
    relief="flat"
)
button_8.place(
    x=1562.0,
    y=11.0,
    width=60.0,
    height=60.0
)

button_image_9 = PhotoImage(
    file=relative_to_assets("button_9.png"))
button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    bg="#4D4C4D",
    activebackground="#4D4C4D",
    command=lambda: print("button_9 clicked"),
    relief="flat"
)
button_9.place(
    x=1476.0,
    y=15.0,
    width=60.0,
    height=50.0
)

entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    920.0,
    40.0,
    image=entry_image_2
)
entry_2 = Entry(
    bd=0,
    bg="#D9D9D9",
    fg="#000716",
    font=("Inter Medium", 28),
    highlightthickness=0
)
entry_2.place(
    x=370.0,
    y=24.0,
    width=1000.0,
    height=40.0
)

image_image_8 = PhotoImage(
    file=relative_to_assets("image_8.png"))
image_8 = canvas.create_image(
    174.0,
    40.0,
    image=image_image_8
)
# Add a function to toggle fullscreen with Escape key
def toggle_fullscreen(event=None):
    window.attributes("-fullscreen", not window.attributes("-fullscreen"))
    return "break"

# Bind Escape key to exit fullscreen
window.bind("<Escape>", toggle_fullscreen)

window.resizable(False, False)
window.mainloop()
