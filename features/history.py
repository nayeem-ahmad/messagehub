import tkinter as tk
from tkinter import ttk
import sqlite3
from .common import DB_FILE

def show_history_dialog():
    hist_win = tk.Toplevel()
    hist_win.title("Email History")
    hist_win.geometry("900x500")
    hist_win.transient()
    hist_win.grab_set()

    search_var = tk.StringVar()
    search_entry = ttk.Entry(hist_win, textvariable=search_var, width=50)
    search_entry.pack(padx=10, pady=10, anchor="w")

    columns = ("Timestamp", "Subject", "Body", "Email", "Status")
    tree = ttk.Treeview(hist_win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_history():
        for item in tree.get_children():
            tree.delete(item)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS email_history (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, subject TEXT, body TEXT, email TEXT, status TEXT)")
        query = search_var.get().strip().lower()
        if query:
            c.execute("SELECT timestamp, subject, body, email, status FROM email_history")
            rows = [row for row in c.fetchall() if any(query in str(field).lower() for field in row)]
        else:
            c.execute("SELECT timestamp, subject, body, email, status FROM email_history ORDER BY id DESC LIMIT 500")
            rows = c.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
        conn.close()

    search_entry.bind("<KeyRelease>", lambda e: load_history())
    load_history()

