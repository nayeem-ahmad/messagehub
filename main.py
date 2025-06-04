import sys
import os

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRIVATE_DIR = os.path.join(BASE_DIR, "private")
SETTINGS_FILE = os.path.join(PRIVATE_DIR, "settings.json")
COLUMN_WIDTHS_FILE = os.path.join(PRIVATE_DIR, "column_widths.json")
DB_FILE = os.path.join(PRIVATE_DIR, "contacts.db")

from tkinter import Tk
import tkinter as tk
from ui import setup_main_ui
from services.db import init_db

if __name__ == "__main__":
    # Ensure private folder exists
    if not os.path.exists(PRIVATE_DIR):
        os.makedirs(PRIVATE_DIR)
    # Ensure settings.json exists
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
    # Ensure column_widths.json exists
    if not os.path.exists(COLUMN_WIDTHS_FILE):
        with open(COLUMN_WIDTHS_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
    # Ensure contacts.db exists (init_db should handle creation, but double-check)
    if not os.path.exists(DB_FILE):
        init_db()
    # Always initialize the database (creates tables if missing)
    init_db()
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
    setup_main_ui(root)
    root.mainloop()