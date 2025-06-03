<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk
import sqlite3
import os

DB_FILE = os.path.join("private", "contacts.db")

class AddContactDialog:
    def __init__(self, parent, name=None, email=None, mobile=None, contact_id=None):
        self.result = None
        self.selected_groups = []
        self.contact_id = contact_id
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Contact" if not name else "Edit Contact")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog_width = 400
        dialog_height = 350
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        center_x = int(screen_width/2 - dialog_width/2)
        center_y = int(screen_height/2 - dialog_height/2)
        self.dialog.geometry(f'{dialog_width}x{dialog_height}+{center_x}+{center_y}')
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create and pack the form elements
        ttk.Label(self.dialog, text=("Add New Contact" if not name else "Edit Contact"), font=("", 12, "bold")).pack(pady=10)
        
        form = ttk.Frame(self.dialog)
        form.pack(padx=20, pady=10, fill=tk.X)
        
        # Name field
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=name if name else "")
        ttk.Entry(form, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Email field
        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar(value=email if email else "")
        ttk.Entry(form, textvariable=self.email_var, width=40).grid(row=1, column=1, pady=5)
        
        # Mobile field
        ttk.Label(form, text="Mobile:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.mobile_var = tk.StringVar(value=mobile if mobile else "")
        ttk.Entry(form, textvariable=self.mobile_var, width=40).grid(row=2, column=1, pady=5)
        
        # Group selection
        ttk.Label(form, text="Groups:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.groups_listbox = tk.Listbox(form, selectmode=tk.MULTIPLE, width=30, height=5)
        self.groups_listbox.grid(row=3, column=1, pady=5, sticky=tk.W)
        self.populate_groups()
        
        # Pre-select groups if editing
        if contact_id is not None:
            self.preselect_groups(contact_id)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for the dialog to close
        self.dialog.wait_window()
    
    def populate_groups(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT short_name FROM groups ORDER BY short_name")
        self.group_names = [row[0] for row in c.fetchall()]
        for g in self.group_names:
            self.groups_listbox.insert(tk.END, g)
        conn.close()
    
    def preselect_groups(self, contact_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT groups.short_name FROM groups
            JOIN group_members ON groups.id = group_members.group_id
            WHERE group_members.contact_id=?
        """, (contact_id,))
        contact_groups = [row[0] for row in c.fetchall()]
        for idx, g in enumerate(self.group_names):
            if g in contact_groups:
                self.groups_listbox.selection_set(idx)
        conn.close()
    
    def save(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        mobile = self.mobile_var.get().strip()
        selected_indices = self.groups_listbox.curselection()
        self.selected_groups = [self.group_names[i] for i in selected_indices]
        
        if not name or not email:
            tk.messagebox.showerror("Error", "Name and Email are required!")
            return
        
        self.result = (name, email, mobile, self.selected_groups)
        self.dialog.destroy()
    
    def cancel(self):
=======
import tkinter as tk
from tkinter import ttk

class AddContactDialog:
    def __init__(self, parent, name=None, email=None, mobile=None):
        self.result = None
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Contact" if not name else "Edit Contact")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        
        # Center the dialog on screen
        dialog_width = 400
        dialog_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        center_x = int(screen_width/2 - dialog_width/2)
        center_y = int(screen_height/2 - dialog_height/2)
        self.dialog.geometry(f'{dialog_width}x{dialog_height}+{center_x}+{center_y}')
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create and pack the form elements
        ttk.Label(self.dialog, text=("Add New Contact" if not name else "Edit Contact"), font=("", 12, "bold")).pack(pady=10)
        
        form = ttk.Frame(self.dialog)
        form.pack(padx=20, pady=10, fill=tk.X)
        
        # Name field
        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=name if name else "")
        ttk.Entry(form, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Email field
        ttk.Label(form, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar(value=email if email else "")
        ttk.Entry(form, textvariable=self.email_var, width=40).grid(row=1, column=1, pady=5)
        
        # Mobile field
        ttk.Label(form, text="Mobile:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.mobile_var = tk.StringVar(value=mobile if mobile else "")
        ttk.Entry(form, textvariable=self.mobile_var, width=40).grid(row=2, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Wait for the dialog to close
        self.dialog.wait_window()
    
    def save(self):
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        mobile = self.mobile_var.get().strip()
        
        if not name or not email:
            tk.messagebox.showerror("Error", "Name and Email are required!")
            return
        
        self.result = (name, email, mobile)
        self.dialog.destroy()
    
    def cancel(self):
>>>>>>> e2ee965447c8d3386d8a8494b2af3542494551f9
        self.dialog.destroy()