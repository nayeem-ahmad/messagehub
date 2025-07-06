import sys
import os
import json

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRIVATE_DIR = os.path.join(BASE_DIR, "private")
SETTINGS_FILE = os.path.join(PRIVATE_DIR, "settings.json")
COLUMN_WIDTHS_FILE = os.path.join(PRIVATE_DIR, "column_widths.json")
DB_FILE = os.path.join(PRIVATE_DIR, "contacts.db")

# Get application version
def get_app_version():
    version_file = os.path.join(BASE_DIR, "version.json")
    try:
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                return version_data.get('version', '1.0.0')
    except:
        pass
    return '1.0.0'

APP_VERSION = get_app_version()

def setup_default_files():
    """Setup default files from templates if they don't exist"""
    # Ensure private folder exists
    if not os.path.exists(PRIVATE_DIR):
        os.makedirs(PRIVATE_DIR)
    
    template_dir = os.path.join(BASE_DIR, "template", "private")
    
    # Setup default files from templates
    template_files = {
        "settings.json": "settings_template.json",
        "column_widths.json": "column_widths_template.json",
        "contacts.db": "contacts_sample.db"
    }
    
    for target_file, template_file in template_files.items():
        target_path = os.path.join(PRIVATE_DIR, target_file)
        template_path = os.path.join(template_dir, template_file)
        
        # Only create if target doesn't exist
        if not os.path.exists(target_path):
            if os.path.exists(template_path):
                # Copy template file
                import shutil
                shutil.copy2(template_path, target_path)
            else:
                # Create minimal default for critical files
                if target_file == "settings.json":
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write("{}")
                elif target_file == "column_widths.json":
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write("{}")

from tkinter import Tk
import tkinter as tk
from ui import setup_main_ui
from services.db import init_db

if __name__ == "__main__":
    # Setup default files from templates
    setup_default_files()
    # Ensure contacts.db exists (init_db should handle creation, but double-check)
    if not os.path.exists(DB_FILE):
        init_db()
    # Always initialize the database (creates tables if missing)
    init_db()
    root = Tk()
    root.title("NaCaZo MessageHub")
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