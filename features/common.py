import os
import sys
import json
from tkinter import messagebox

if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PRIVATE_DIR = os.path.join(_BASE_DIR, "private")

DB_FILE = os.path.join(PRIVATE_DIR, "contacts.db")
SETTINGS_FILE = os.path.join(PRIVATE_DIR, "settings.json")
COLUMN_WIDTHS_FILE = os.path.join(PRIVATE_DIR, "column_widths.json")

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

# --- UI Helpers ---
def apply_striped_rows(tree):
    """Apply alternating background colors to a Treeview."""
    tree.tag_configure("evenrow", background="#f2f2f2")
    tree.tag_configure("oddrow", background="#ffffff")
    for idx, iid in enumerate(tree.get_children()):
        tags = list(tree.item(iid, "tags"))
        tags = [t for t in tags if t not in ("evenrow", "oddrow")]
        tags.append("evenrow" if idx % 2 == 0 else "oddrow")
        tree.item(iid, tags=tuple(tags))

