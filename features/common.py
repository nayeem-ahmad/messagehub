import os
import json
from tkinter import messagebox
DB_FILE = os.path.join("private", "contacts.db")
SETTINGS_FILE = os.path.join("private", "settings.json")
COLUMN_WIDTHS_FILE = os.path.join("private", "column_widths.json")

# --- Settings Management ---
def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")

# --- Utility Functions ---
def center_window(window, width, height):
    """Center a Tkinter window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def load_column_widths(list_name, columns):
    if not os.path.exists(COLUMN_WIDTHS_FILE):
        return {col: None for col in columns}
    try:
        with open(COLUMN_WIDTHS_FILE, "r") as f:
            data = json.load(f)
        # Ensure all widths are int or None
        result = {}
        for col in columns:
            val = data.get(list_name, {}).get(col, None)
            try:
                result[col] = int(val) if val is not None else None
            except Exception:
                result[col] = None
        return result
    except Exception:
        return {col: None for col in columns}

def save_column_widths(list_name, tree):
    widths = {tree.heading(col)['text']: tree.column(col)['width'] for col in tree['columns']}
    data = {}
    if os.path.exists(COLUMN_WIDTHS_FILE):
        try:
            with open(COLUMN_WIDTHS_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
    data[list_name] = widths
    with open(COLUMN_WIDTHS_FILE, "w") as f:
        json.dump(data, f)

def get_all_group_names():
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT short_name FROM groups ORDER BY short_name")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    return groups

