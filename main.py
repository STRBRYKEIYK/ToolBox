from API.api_gui import APIConnectionGUI
import tkinter as tk

def main():
	root = tk.Tk()
	app = APIConnectionGUI(root)
	root.mainloop()

if __name__ == "__main__":
	main()
