import tkinter as tk
from tkinter import ttk
import sqlite3
from .common import DB_FILE, apply_striped_rows, center_window

def show_history_dialog():
    hist_win = tk.Toplevel()
    hist_win.title("History")
    center_window(hist_win, 900, 500)
    hist_win.transient()
    hist_win.grab_set()

    option_var = tk.StringVar(value="Email")
    search_var = tk.StringVar()

    top_frame = ttk.Frame(hist_win)
    top_frame.pack(fill=tk.X, padx=10, pady=10)

    ttk.Radiobutton(top_frame, text="Email", variable=option_var, value="Email", command=lambda: load_history()).pack(side=tk.LEFT)
    ttk.Radiobutton(top_frame, text="SMS", variable=option_var, value="SMS", command=lambda: load_history()).pack(side=tk.LEFT, padx=(10,0))

    search_entry = ttk.Entry(top_frame, textvariable=search_var, width=50)
    search_entry.pack(side=tk.RIGHT)

    tree = ttk.Treeview(hist_win, columns=(), show="headings")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    count_var = tk.StringVar(value="Total: 0 | Selected: 0")
    ttk.Label(hist_win, textvariable=count_var).pack(anchor="w", padx=10, pady=(0,5))

    def update_counts(event=None):
        total = len(tree.get_children())
        selected = len(tree.selection())
        count_var.set(f"Total: {total} | Selected: {selected}")

    tree.bind("<<TreeviewSelect>>", update_counts)

    def load_history():
        for col in tree["columns"]:
            tree.heading(col, text="")
        tree.configure(columns=())
        for item in tree.get_children():
            tree.delete(item)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        if option_var.get() == "Email":
            c.execute("""CREATE TABLE IF NOT EXISTS email_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                subject TEXT,
                body TEXT,
                email TEXT,
                status TEXT
            )""")
            columns = ("Timestamp", "Recipient", "Subject", "Body", "Status")
            tree.configure(columns=columns)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            query = search_var.get().strip().lower()
            if query:
                c.execute("SELECT timestamp, email, subject, body, status FROM email_history")
                rows = [row for row in c.fetchall() if any(query in str(field).lower() for field in row)]
            else:
                c.execute("SELECT timestamp, email, subject, body, status FROM email_history ORDER BY id DESC LIMIT 500")
                rows = c.fetchall()
        else:
            c.execute("""CREATE TABLE IF NOT EXISTS sms_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                body TEXT,
                recipient TEXT,
                status TEXT
            )""")
            columns = ("Timestamp", "Recipient", "Body", "Status")
            tree.configure(columns=columns)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            query = search_var.get().strip().lower()
            if query:
                c.execute("SELECT timestamp, recipient, body, status FROM sms_history")
                rows = [row for row in c.fetchall() if any(query in str(field).lower() for field in row)]
            else:
                c.execute("SELECT timestamp, recipient, body, status FROM sms_history ORDER BY id DESC LIMIT 500")
                rows = c.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
        apply_striped_rows(tree)
        conn.close()
        update_counts()

    search_entry.bind("<KeyRelease>", lambda e: load_history())
    load_history()

