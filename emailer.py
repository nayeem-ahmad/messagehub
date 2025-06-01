from tkinter import Tk
import tkinter as tk
from ui import setup_main_ui
from db import init_db
import os

SETTINGS_FILE = os.path.join("private", "settings.json")
COLUMN_WIDTHS_FILE = os.path.join("private", "column_widths.json")

if __name__ == "__main__":
    root = Tk()
    root.title("NaCaZo Emailer")
    # Set window size and center it
    window_width = 1024
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_height = int(screen_height * 0.8)
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.state('zoomed')  # Start maximized
    init_db()
    setup_main_ui(root)
    root.mainloop()