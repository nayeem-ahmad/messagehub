import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, Toplevel, Listbox, MULTIPLE, Button, Label, END
import sqlite3
from datetime import datetime
import pandas as pd
import inspect
from contact_dialog import AddContactDialog
from .common import DB_FILE, load_column_widths, save_column_widths, get_settings, get_all_group_names


def show_contacts(parent):
    # Clear existing content
    for widget in parent.winfo_children():
        widget.destroy()

    # Toolbar
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, pady=(0, 10))

    # Button group: Add, Edit, Delete
    btn_group = ttk.Frame(toolbar)
    btn_group.pack(side=tk.LEFT)
    add_btn = ttk.Button(btn_group, text="Add Contact", command=lambda: add_contact(tree))
    add_btn.pack(side=tk.LEFT, padx=(0, 2))
    edit_btn = ttk.Button(btn_group, text="Edit Contact", command=lambda: edit_contact(tree))
    edit_btn.pack(side=tk.LEFT, padx=2)
    delete_btn = ttk.Button(btn_group, text="Delete Contact(s)", command=lambda: delete_contacts(tree))
    delete_btn.pack(side=tk.LEFT, padx=2)

    # Select/Unselect button above the checkbox column
    select_btn_frame = ttk.Frame(toolbar)
    select_btn_frame.pack(side=tk.LEFT, padx=(20, 0))
    select_btn = ttk.Button(select_btn_frame, text="Select", width=8)
    select_btn.pack()

    def toggle_selected_contacts():
        selected = tree.selection()
        if not selected:
            return
        all_checked = all("checked" in tree.item(iid, "tags") for iid in selected)
        for iid in selected:
            if all_checked:
                tree.item(iid, tags=("unchecked",))
                tree.set(iid, "Select", " ")
            else:
                tree.item(iid, tags=("checked",))
                tree.set(iid, "Select", "✔")
        update_select_btn()

    def update_select_btn():
        selected = tree.selection()
        if not selected:
            select_btn.config(text="Select")
            return
        all_checked = all("checked" in tree.item(iid, "tags") for iid in selected)
        select_btn.config(text="Unselect" if all_checked else "Select")

    select_btn.config(command=toggle_selected_contacts)

    # Import button at the right
    import_btn = ttk.Button(toolbar, text="Import Contacts from CSV", command=lambda: import_contacts_dialog(tree))
    import_btn.pack(side=tk.RIGHT, padx=5)

    # Group filter dropdown
    filter_frame = ttk.Frame(parent)
    filter_frame.pack(fill=tk.X, pady=(0, 5))
    ttk.Label(filter_frame, text="Filter by Group:").pack(side=tk.LEFT, padx=(0, 5))
    group_var = tk.StringVar()
    group_dropdown = ttk.Combobox(filter_frame, textvariable=group_var, state="readonly", width=25)
    group_dropdown.pack(side=tk.LEFT)
    group_dropdown['values'] = ("All",) + tuple(get_all_group_names())
    group_dropdown.current(0)
    def on_group_filter_change(event=None):
        load_contacts_with_checkboxes(tree, insert_with_checkbox, group=group_var.get())
    group_dropdown.bind("<<ComboboxSelected>>", on_group_filter_change)

    # Treeview with checkboxes and serial number
    columns = ("Select", "S.No.", "Name", "Email", "Mobile", "Groups")
    tree_frame = ttk.Frame(parent)
    tree_frame.pack(fill=tk.BOTH, expand=True)
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    # Load saved widths
    col_widths = load_column_widths("contacts", columns)
    tree.heading("Select", text="✔")
    tree.column("Select", width=col_widths.get("Select") or 20, minwidth=15, anchor="center")
    tree.heading("S.No.", text="S.No.")
    tree.column("S.No.", width=col_widths.get("S.No.") or 35, minwidth=20, anchor="center")
    for col in columns[2:5]:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col) or 120)
    tree.heading("Groups", text="Groups")
    tree.column("Groups", width=col_widths.get("Groups") or 180)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar (vertical, to the right of the tree)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Add checkboxes and serial number to each row
    def insert_with_checkbox(values, sn):
        iid = tree.insert("", tk.END, values=("", sn) + values)
        tree.set(iid, "Select", " ")  # Placeholder for checkbox
        tree.item(iid, tags=("unchecked",))
        return iid

    # Load contacts
    load_contacts_with_checkboxes(tree, insert_with_checkbox, group="All")

    # Checkbox click handler
    def on_treeview_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            col = tree.identify_column(event.x)
            if col == "#1":  # Select column
                row = tree.identify_row(event.y)
                if row:
                    tags = tree.item(row, "tags")
                    if "checked" in tags:
                        tree.item(row, tags=("unchecked",))
                        tree.set(row, "Select", " ")
                    else:
                        tree.item(row, tags=("checked",))
                        tree.set(row, "Select", "✔")
                    update_select_btn()
    tree.bind("<Button-1>", on_treeview_click)
    tree.bind("<<TreeviewSelect>>", lambda e: update_select_btn())

    def on_column_resize(event):
        save_column_widths("contacts", tree)
    tree.bind("<ButtonRelease-1>", on_column_resize)

def load_contacts_with_checkboxes(tree, insert_with_checkbox, group="All"):
    for item in tree.get_children():
        tree.delete(item)
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if group == "All":
        c.execute("""
            SELECT contacts.id, contacts.name, contacts.email, contacts.mobile,
                   GROUP_CONCAT(groups.short_name, ', ') as groupnames
            FROM contacts
            LEFT JOIN group_members ON contacts.id = group_members.contact_id
            LEFT JOIN groups ON group_members.group_id = groups.id
            GROUP BY contacts.id, contacts.name, contacts.email, contacts.mobile
            ORDER BY contacts.id
        """)
    else:
        c.execute("""
            SELECT contacts.id, contacts.name, contacts.email, contacts.mobile,
                   GROUP_CONCAT(groups.short_name, ', ') as groupnames
            FROM contacts
            LEFT JOIN group_members ON contacts.id = group_members.contact_id
            LEFT JOIN groups ON group_members.group_id = groups.id
            WHERE contacts.id IN (
                SELECT contact_id FROM group_members WHERE group_id = (SELECT id FROM groups WHERE short_name=?)
            )
            GROUP BY contacts.id, contacts.name, contacts.email, contacts.mobile
            ORDER BY contacts.id
        """, (group,))
    rows = c.fetchall()
    conn.close()
    for idx, row in enumerate(rows, 1):
        # row: (id, name, email, mobile, groupnames)
        insert_with_checkbox((row[1], row[2], row[3], row[4] or ""), idx)

def add_contact(tree):
    dialog = AddContactDialog(tree.master)
    if dialog.result:
        name, email, mobile, selected_groups = dialog.result
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO contacts (name, email, mobile) VALUES (?, ?, ?)", 
                     (name, email, mobile))
            conn.commit()
            # Get the new contact's id
            c.execute("SELECT id FROM contacts WHERE email=?", (email,))
            row = c.fetchone()
            contact_id = row[0] if row else None
            # Assign to groups
            if contact_id and selected_groups:
                for group_name in selected_groups:
                    c.execute("SELECT id FROM groups WHERE short_name=?", (group_name,))
                    group_row = c.fetchone()
                    if group_row:
                        group_id = group_row[0]
                        c.execute("INSERT OR IGNORE INTO group_members (group_id, contact_id) VALUES (?, ?)", (group_id, contact_id))
            conn.commit()
            # Fetch group names for display
            groupnames = ", ".join(selected_groups) if selected_groups else ""
            sn = len(tree.get_children()) + 1
            tree.insert("", tk.END, values=("", sn, name, email, mobile, groupnames), tags=("unchecked",))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email address already exists!")
        finally:
            conn.close()

def edit_contact(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Edit Contact", "Please select exactly one contact to edit.")
        return
    iid = selected[0]
    values = tree.item(iid, "values")
    sn = values[1]
    name = values[2]
    email = values[3]
    mobile = values[4]
    import sqlite3, inspect
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM contacts WHERE email=?", (email,))
    row = c.fetchone()
    contact_id = row[0] if row else None
    conn.close()
    dialog = AddContactDialog(tree.master, name=name, email=email, mobile=mobile, contact_id=contact_id)
    if dialog.result and contact_id is not None:
        new_name, new_email, new_mobile, selected_groups = dialog.result
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("UPDATE contacts SET name=?, email=?, mobile=? WHERE id=?", (new_name, new_email, new_mobile, contact_id))
            c.execute("DELETE FROM group_members WHERE contact_id=?", (contact_id,))
            for group_name in selected_groups:
                c.execute("SELECT id FROM groups WHERE short_name=?", (group_name,))
                grp_row = c.fetchone()
                if grp_row:
                    group_id = grp_row[0]
                    c.execute("INSERT OR IGNORE INTO group_members (group_id, contact_id) VALUES (?, ?)", (group_id, contact_id))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email address already exists!")
        finally:
            conn.close()
        try:
            for frame_info in inspect.stack():
                local_vars = frame_info.frame.f_locals
                if 'insert_with_checkbox' in local_vars:
                    load_contacts_with_checkboxes(tree, local_vars['insert_with_checkbox'], group='All')
                    break
            else:
                parent = tree.master
                while parent and not hasattr(parent, 'winfo_children'):
                    parent = getattr(parent, 'master', None)
                if parent:
                    show_contacts(parent)
        except Exception:
            parent = tree.master
            while parent and not hasattr(parent, 'winfo_children'):
                parent = getattr(parent, 'master', None)
            if parent:
                show_contacts(parent)

def delete_contacts(tree):
    selected = []
    for iid in tree.get_children():
        if "checked" in tree.item(iid, "tags"):
            selected.append(iid)
    if not selected:
        messagebox.showinfo("Delete Contact(s)", "Please select at least one contact to delete.")
        return
    if not messagebox.askyesno("Delete Contact(s)", f"Are you sure you want to delete {len(selected)} contact(s)?"):
        return
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for iid in selected:
        values = tree.item(iid, "values")
        # values layout: (Select, S.No., Name, Email, Mobile, Groups)
        # indexes 2,3,4 correspond to name, email and mobile respectively
        name, email, mobile = values[2], values[3], values[4]
        c.execute(
            "DELETE FROM contacts WHERE name=? AND email=? AND mobile=?",
            (name, email, mobile),
        )
        tree.delete(iid)
    conn.commit()
    conn.close()

def load_contacts(tree):
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)

    # Load from database
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for row in c.execute("SELECT name, email, mobile FROM contacts"):
        tree.insert("", tk.END, values=row)
    conn.close()

def show_groups(parent):
    # Clear existing content
    for widget in parent.winfo_children():
        widget.destroy()

    # Toolbar for groups
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, pady=(0, 10))

    btn_group = ttk.Frame(toolbar)
    btn_group.pack(side=tk.LEFT)
    add_btn = ttk.Button(btn_group, text="Add Group", command=lambda: add_group(groups_tree))
    add_btn.pack(side=tk.LEFT, padx=(0, 2))
    edit_btn = ttk.Button(btn_group, text="Edit Group", command=lambda: edit_group(groups_tree))
    edit_btn.pack(side=tk.LEFT, padx=2)
    delete_btn = ttk.Button(btn_group, text="Delete Group", command=lambda: delete_group(groups_tree))
    delete_btn.pack(side=tk.LEFT, padx=2)

    # Groups list
    columns = ("Short Name", "Name", "Description")
    groups_frame = ttk.Frame(parent)
    groups_frame.pack(fill=tk.BOTH, expand=True)
    groups_tree = ttk.Treeview(groups_frame, columns=columns, show="headings", height=15)
    # Load saved widths
    col_widths = load_column_widths("groups", columns)
    groups_tree.heading("Short Name", text="Short Name")
    groups_tree.column("Short Name", width=col_widths.get("Short Name", 100))
    groups_tree.heading("Name", text="Group Name")
    groups_tree.column("Name", width=col_widths.get("Name", 180))
    groups_tree.heading("Description", text="Description")
    groups_tree.column("Description", width=col_widths.get("Description", 250))
    groups_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar (vertical, to the right of the tree)
    scrollbar = ttk.Scrollbar(groups_frame, orient=tk.VERTICAL, command=groups_tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    groups_tree.configure(yscrollcommand=scrollbar.set)

    load_groups(groups_tree)

    def on_column_resize(event):
        save_column_widths("groups", groups_tree)
    groups_tree.bind("<ButtonRelease-1>", on_column_resize)

def load_groups(tree):
    for item in tree.get_children():
        tree.delete(item)
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for row in c.execute("SELECT short_name, name, description FROM groups ORDER BY short_name"):
        tree.insert("", tk.END, values=row)
    conn.close()

def add_group(tree):
    from tkinter import simpledialog, messagebox
    dialog = GroupDialog(tree.master)
    if dialog.result:
        short_name, name, description = dialog.result
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO groups (short_name, name, description) VALUES (?, ?, ?)", (short_name, name, description))
            conn.commit()
            load_groups(tree)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Short name must be unique and not empty!")
        finally:
            conn.close()

def edit_group(tree):
    from tkinter import simpledialog, messagebox
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Edit Group", "Please select exactly one group to edit.")
        return
    iid = selected[0]
    old_short_name, old_name, old_description = tree.item(iid, "values")
    dialog = GroupDialog(tree.master, short_name=old_short_name, name=old_name, description=old_description)
    if dialog.result:
        new_short_name, new_name, new_description = dialog.result
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("UPDATE groups SET short_name=?, name=?, description=? WHERE short_name=?", (new_short_name, new_name, new_description, old_short_name))
            conn.commit()
            load_groups(tree)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Short name must be unique and not empty!")
        finally:
            conn.close()

def delete_group(tree):
    from tkinter import messagebox
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Delete Group", "Please select exactly one group to delete.")
        return
    iid = selected[0]
    name = tree.item(iid, "values")[0]
    if not messagebox.askyesno("Delete Group", f"Are you sure you want to delete group '{name}'?"):
        return
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM groups WHERE name=?", (name,))
    c.execute("DELETE FROM group_members WHERE group_id IN (SELECT id FROM groups WHERE name=?)", (name,))
    conn.commit()
    conn.close()
    load_groups(tree)

# GroupDialog for add/edit group
class GroupDialog(simpledialog.Dialog):
    def __init__(self, parent, short_name='', name='', description=''):
        self.short_name = short_name
        self.name = name
        self.description = description
        self.result = None
        super().__init__(parent, title="Group Details")
    def body(self, master):
        import tkinter as tk
        ttk.Label(master, text="Short Name (required):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.short_name_var = tk.StringVar(value=self.short_name)
        ttk.Entry(master, textvariable=self.short_name_var, width=20).grid(row=0, column=1, pady=5)
        ttk.Label(master, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.name)
        ttk.Entry(master, textvariable=self.name_var, width=30).grid(row=1, column=1, pady=5)
        ttk.Label(master, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_var = tk.StringVar(value=self.description)
        ttk.Entry(master, textvariable=self.desc_var, width=40).grid(row=2, column=1, pady=5)
        return master
    def apply(self):
        short_name = self.short_name_var.get().strip()
        name = self.name_var.get().strip()
        desc = self.desc_var.get().strip()
        if not short_name:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", "Short name is required!")
            self.result = None
        else:
            self.result = (short_name, name, desc)
    def show(self):
        if not self._centered:
            self._centered = True
            self.update_idletasks()
            center_window(self, 400, 250)

# --- Send Emails Dialog ---
def send_emails_dialog(tree):
    checked_contacts = []
    for iid in tree.get_children():
        if "checked" in tree.item(iid, "tags"):
            values = tree.item(iid, "values")
            checked_contacts.append({
                "name": values[1],
                "email": values[2],
                "mobile": values[3]
            })
    if not checked_contacts:
        messagebox.showinfo("Send Emails", "Please select at least one contact to send emails.")
        return

    dialog = tk.Toplevel(tree.master)
    dialog.title("Send Emails")
    dialog.geometry("600x500")
    dialog.transient(tree.master)
    dialog.grab_set()
    center_window(dialog, 600, 500)

    # List of emails
    ttk.Label(dialog, text="Recipients:").pack(anchor="w", padx=10, pady=(10,0))
    recipients_list = tk.Listbox(dialog, height=6)
    for c in checked_contacts:
        recipients_list.insert(tk.END, f"{c['name']} <{c['email']}> ({c['mobile']})")
    recipients_list.pack(fill=tk.X, padx=10, pady=5)

    # Subject
    ttk.Label(dialog, text="Subject:").pack(anchor="w", padx=10, pady=(10,0))
    subject_var = tk.StringVar(value="Your Subject Here")
    subject_entry = ttk.Entry(dialog, textvariable=subject_var, width=80)
    subject_entry.pack(fill=tk.X, padx=10, pady=5)

    # Body
    ttk.Label(dialog, text="Body:").pack(anchor="w", padx=10, pady=(10,0))
    body_text = tk.Text(dialog, height=10, width=80)
    body_text.insert(tk.END, "Your email body here.")
    body_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

    # Status
    status_var = tk.StringVar(value="Ready to send.")
    status_label = ttk.Label(dialog, textvariable=status_var)
    status_label.pack(anchor="w", padx=10, pady=5)

    def send_all_emails():
        send_btn.config(state=tk.DISABLED)
        subject = subject_var.get()
        body = body_text.get("1.0", tk.END).strip()
        # Load settings
        settings = get_settings()
        email_method = settings.get('email_method', 'SMTP').lower()
        sender = settings.get('sender_email', '')
        password = settings.get('sender_pwd', '')
        smtp_server = settings.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(settings.get('smtp_port', '587'))
        sendgrid_api_key = settings.get('sendgrid_api_key', '')
        ses_access_key = settings.get('ses_access_key', '')
        ses_secret_key = settings.get('ses_secret_key', '')
        ses_region = settings.get('ses_region', '')
        if not sender:
            status_var.set("Sender email not set in settings.")
            send_btn.config(state=tk.NORMAL)
            return
        if email_method == 'smtp' and (not password or not smtp_server or not smtp_port):
            status_var.set("SMTP settings missing in Settings.")
            send_btn.config(state=tk.NORMAL)
            return
        if email_method == 'sendgrid' and not sendgrid_api_key:
            status_var.set("SendGrid API key missing in Settings.")
            send_btn.config(state=tk.NORMAL)
            return
        if email_method == 'ses' and (not ses_access_key or not ses_secret_key or not ses_region):
            status_var.set("Amazon SES credentials missing in Settings.")
            send_btn.config(state=tk.NORMAL)
            return
        import email_utils
        def send_thread():
            history_conn = sqlite3.connect(DB_FILE)
            hc = history_conn.cursor()
            hc.execute('''CREATE TABLE IF NOT EXISTS email_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                subject TEXT,
                body TEXT,
                email TEXT,
                status TEXT
            )''')
            history_conn.commit()
            sent_count = 0
            for idx, contact in enumerate(checked_contacts):
                personalized_subject = subject.replace("{{name}}", contact['name']).replace("{{email}}", contact['email']).replace("{{mobile}}", contact['mobile'])
                personalized_body = body.replace("{{name}}", contact['name']).replace("{{email}}", contact['email']).replace("{{mobile}}", contact['mobile'])
                try:
                    if email_method == 'smtp':
                        smtp_settings = {"server": smtp_server, "port": smtp_port}
                        email_utils.send_email('smtp', smtp_settings, sender, password, contact['email'], personalized_subject, personalized_body)
                    elif email_method == 'sendgrid':
                        email_utils.send_email('sendgrid', {"sendgrid_api_key": sendgrid_api_key}, sender, None, contact['email'], personalized_subject, personalized_body)
                    elif email_method == 'ses':
                        email_utils.send_email('ses', {"ses_access_key": ses_access_key, "ses_secret_key": ses_secret_key, "ses_region": ses_region}, sender, None, contact['email'], personalized_subject, personalized_body)
                    status_var.set(f"Sent to {contact['email']}")
                    hc.execute("INSERT INTO email_history (timestamp, subject, body, email, status) VALUES (?, ?, ?, ?, ?)",
                               (datetime.now().isoformat(), personalized_subject, personalized_body, contact['email'], "Sent"))
                    history_conn.commit()
                except Exception as e:
                    status_var.set(f"Failed to {contact['email']}: {e}")
                    hc.execute("INSERT INTO email_history (timestamp, subject, body, email, status) VALUES (?, ?, ?, ?, ?)",
                               (datetime.now().isoformat(), personalized_subject, personalized_body, contact['email'], f"Failed: {e}"))
                    history_conn.commit()
                sent_count += 1
                time.sleep(1.5)  # Delay between emails
                if sent_count % 50 == 0:
                    delay = random.randint(5, 60)
                    status_var.set(f"Batch delay: {delay} seconds...")
                    time.sleep(delay)
            history_conn.close()
            status_var.set("All emails processed.")
            send_btn.config(state=tk.NORMAL)
        threading.Thread(target=send_thread, daemon=True).start()

    send_btn = ttk.Button(dialog, text="Send", command=send_all_emails)
    send_btn.pack(pady=10)

def import_contacts_dialog(tree):
    from tkinter import filedialog, messagebox, simpledialog, Toplevel, Listbox, MULTIPLE, Button, Label, END
    from contacts import import_contacts_from_csv
    import sqlite3
    # Step 1: File selection
    filename = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*")]
    )
    if not filename:
        return
    # Step 2: Group selection dialog
    group_win = Toplevel()
    group_win.title("Select Groups for Imported Contacts")
    Label(group_win, text="Assign imported contacts to group(s):").pack(padx=10, pady=(10, 0))
    group_listbox = Listbox(group_win, selectmode=MULTIPLE, width=40, height=8)
    group_listbox.pack(padx=10, pady=10)
    # Fetch group names
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT short_name FROM groups ORDER BY short_name")
    group_names = [row[0] for row in c.fetchall()]
    conn.close()
    for g in group_names:
        group_listbox.insert(END, g)
    result = {'done': False}
    def on_ok():
        result['selected'] = [group_names[i] for i in group_listbox.curselection()]
        result['done'] = True
        group_win.destroy()
    def on_cancel():
        result['selected'] = []
        result['done'] = False
        group_win.destroy()
    btn_ok = Button(group_win, text="OK", command=on_ok)
    btn_ok.pack(side="left", padx=20, pady=10)
    btn_cancel = Button(group_win, text="Cancel", command=on_cancel)
    btn_cancel.pack(side="right", padx=20, pady=10)
    group_win.grab_set()
    group_win.wait_window()
    if not result.get('done'):
        return
    selected_groups = result.get('selected', [])
    # Step 3: Import and assign groups
    try:
        imported = import_contacts_from_csv(filename)
        # Assign to groups
        if selected_groups and imported > 0:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            # Get ids of imported contacts (assume new ones have no group assignment yet)
            c.execute("SELECT id, email FROM contacts")
            all_contacts = {row[1]: row[0] for row in c.fetchall()}
            import pandas as pd
            data = pd.read_csv(filename)
            for _, row in data.iterrows():
                email = row.get('email')
                if not email or email not in all_contacts:
                    continue
                contact_id = all_contacts[email]
                for group_name in selected_groups:
                    c.execute("SELECT id FROM groups WHERE short_name=?", (group_name,))
                    group_row = c.fetchone()
                    if group_row:
                        group_id = group_row[0]
                        c.execute("INSERT OR IGNORE INTO group_members (group_id, contact_id) VALUES (?, ?)", (group_id, contact_id))
            conn.commit()
            conn.close()
        messagebox.showinfo("Import Contacts", f"Imported {imported} contacts from CSV.")
        # Always refresh contacts list using loader to ensure correct columns
        try:
            import inspect
            for frame_info in inspect.stack():
                local_vars = frame_info.frame.f_locals
                if 'insert_with_checkbox' in local_vars:
                    load_contacts_with_checkboxes(tree, local_vars['insert_with_checkbox'], group="All")
                    break
            else:
                # Fallback: reload via show_contacts if loader not found
                parent = tree.master
                while parent and not hasattr(parent, 'winfo_children'):
                    parent = getattr(parent, 'master', None)
                if parent:
                    show_contacts(parent)
        except Exception:
            # Fallback: reload via show_contacts
            parent = tree.master
            while parent and not hasattr(parent, 'winfo_children'):
                parent = getattr(parent, 'master', None)
            if parent:
                show_contacts(parent)
    except Exception as e:
        messagebox.showerror("Import Contacts", f"Failed to import contacts: {e}")


