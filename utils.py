<<<<<<< HEAD
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
from contacts import import_contacts_from_csv, get_contacts_for_group
from datetime import datetime

def setup_main_ui(root):
    # Place your main window widgets here
    # Example:
    Label(root, text="CSV File:").grid(row=0, column=0, sticky="e")
    # ... rest of your UI setup ...
    # Bind buttons to functions from contacts.py, email_utils.py, etc.

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    else:
=======
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
from contacts import import_contacts_from_csv, get_contacts_for_group
from datetime import datetime

def setup_main_ui(root):
    # Place your main window widgets here
    # Example:
    Label(root, text="CSV File:").grid(row=0, column=0, sticky="e")
    # ... rest of your UI setup ...
    # Bind buttons to functions from contacts.py, email_utils.py, etc.

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    else:
>>>>>>> e2ee965447c8d3386d8a8494b2af3542494551f9
        return f"{s}s"