import tkinter as tk
from tkinter import ttk, messagebox
from contact_dialog import AddContactDialog
import sqlite3
import threading
import time
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import tkinter.simpledialog as simpledialog
import json
import os
import email_utils

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

# --- Main UI Setup ---
def setup_main_ui(root):
    """Set up the main application UI."""
    # Create main container
    main_container = ttk.Frame(root)
    main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Sidebar (30% width)
    sidebar = ttk.Frame(main_container, width=200)
    sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

    # Main content (70% width)
    content = ttk.Frame(main_container)
    content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Sidebar buttons
    sidebar_buttons = [
        ("Contacts", lambda: show_contacts(content)),
        ("Groups", lambda: show_groups(content)),
        ("Email Campaigns", lambda: show_email_campaigns(content)),
        ("SMS Campaign", lambda: show_sms_campaigns(content)),
    ]

    for text, command in sidebar_buttons:
        btn = ttk.Button(sidebar, text=text, command=command, width=20)
        btn.pack(pady=5)

    # Settings button below SMS Campaign
    settings_btn = ttk.Button(sidebar, text="Settings", command=lambda: open_settings_dialog(root), width=20)
    settings_btn.pack(pady=5)

    # Move History button to the bottom of the sidebar
    sidebar.pack_propagate(False)
    history_btn = ttk.Button(sidebar, text="History", command=show_history_dialog, width=20)
    history_btn.pack(side=tk.BOTTOM, pady=10)

    # Set up the contacts view by default
    show_contacts(content)

# --- SMS Campaigns UI ---
def show_sms_campaigns(parent):
    # Clear existing content
    for widget in parent.winfo_children():
        widget.destroy()

    # Toolbar for SMS campaigns
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, pady=(0, 10))
    btn_group = ttk.Frame(toolbar)
    btn_group.pack(side=tk.LEFT)
    add_btn = ttk.Button(btn_group, text="Add SMS Campaign", command=lambda: add_sms_campaign(sms_tree))
    add_btn.pack(side=tk.LEFT, padx=(0, 2))
    edit_btn = ttk.Button(btn_group, text="Edit SMS Campaign", command=lambda: edit_sms_campaign(sms_tree))
    edit_btn.pack(side=tk.LEFT, padx=2)
    delete_btn = ttk.Button(btn_group, text="Delete SMS Campaign", command=lambda: delete_sms_campaign(sms_tree))
    delete_btn.pack(side=tk.LEFT, padx=2)

    # SMS Campaigns list
    columns = ("Name", "Message")
    sms_frame = ttk.Frame(parent)
    sms_frame.pack(fill=tk.BOTH, expand=True)
    sms_tree = ttk.Treeview(sms_frame, columns=columns, show="headings", height=10)
    sms_tree.heading("Name", text="Campaign Name")
    sms_tree.column("Name", width=180)
    sms_tree.heading("Message", text="Message")
    sms_tree.column("Message", width=400)
    sms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(sms_frame, orient=tk.VERTICAL, command=sms_tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    sms_tree.configure(yscrollcommand=scrollbar.set)
    load_sms_campaigns(sms_tree)
    def on_column_resize(event):
        pass  # Optionally implement column width persistence
    sms_tree.bind("<ButtonRelease-1>", on_column_resize)

# --- SMS Campaigns CRUD and Dialogs ---
def load_sms_campaigns(tree):
    for item in tree.get_children():
        tree.delete(item)
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sms_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            message TEXT
        )
    """)
    for row in c.execute("SELECT name, message FROM sms_campaigns ORDER BY id DESC"):
        tree.insert("", tk.END, values=row)
    conn.close()

def add_sms_campaign(tree):
    open_sms_campaign_wizard(tree, mode="add")

def edit_sms_campaign(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Edit SMS Campaign", "Please select exactly one campaign to edit.")
        return
    iid = selected[0]
    old_name, old_message = tree.item(iid, "values")
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM sms_campaigns WHERE name=?", (old_name,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    campaign_id = row[0]
    c.execute("SELECT contact_id FROM sms_campaign_contacts WHERE campaign_id=?", (campaign_id,))
    contact_ids = [r[0] for r in c.fetchall()]
    conn.close()
    open_sms_campaign_wizard(tree, mode="edit", campaign={
        'id': campaign_id,
        'name': old_name,
        'message': old_message,
        'contact_ids': contact_ids
    })

def delete_sms_campaign(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Delete SMS Campaign", "Please select exactly one campaign to delete.")
        return
    iid = selected[0]
    name = tree.item(iid, "values")[0]
    if not messagebox.askyesno("Delete SMS Campaign", f"Are you sure you want to delete campaign '{name}'?"):
        return
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM sms_campaigns WHERE name=?", (name,))
    c.execute("DELETE FROM sms_campaign_contacts WHERE campaign_id IN (SELECT id FROM sms_campaigns WHERE name=?)", (name,))
    conn.commit()
    conn.close()
    load_sms_campaigns(tree)

# --- SMS Campaign Wizard ---
def open_sms_campaign_wizard(tree, mode="add", campaign=None):
    import tkinter as tk
    from tkinter import ttk, messagebox
    import sqlite3
    dialog = tk.Toplevel(tree.master)
    dialog.title("Add SMS Campaign" if mode=="add" else "Edit SMS Campaign")
    dialog.geometry("900x600")
    dialog.transient(tree.master)
    dialog.grab_set()
    center_window(dialog, 900, 600)
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    # Step 1: Details
    step1 = ttk.Frame(notebook)
    notebook.add(step1, text="1. Details")
    name_var = tk.StringVar(value=campaign['name'] if campaign else "")
    message_text = tk.Text(step1, width=80, height=8)
    message_text.insert(tk.END, campaign['message'] if campaign else "")
    details_header = ttk.Label(step1, text="SMS Campaign Details", font=("Segoe UI", 14, "bold"))
    details_header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(10, 0), padx=10)
    ttk.Label(step1, text="Campaign Name *", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
    name_entry = ttk.Entry(step1, textvariable=name_var, width=40, font=("Segoe UI", 10))
    name_entry.grid(row=1, column=1, pady=10, padx=10, sticky=tk.W)
    name_entry.focus_set()
    ttk.Label(step1, text="Message *", font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.NW, pady=10, padx=10)
    message_text.configure(font=("Segoe UI", 10))
    step1.grid_rowconfigure(2, weight=1)
    step1.grid_columnconfigure(1, weight=1)
    message_text.grid(row=2, column=1, pady=10, padx=10, sticky="nsew")
    body_tip = ttk.Label(step1, text="You can use {{name}}, {{mobile}}, {{email}} as placeholders.", font=("Segoe UI", 9, "italic"), foreground="#666")
    body_tip.grid(row=3, column=1, sticky=tk.W, padx=10, pady=(0, 10))
    # Step 2: Select Contacts
    step2 = ttk.Frame(notebook)
    notebook.add(step2, text="2. Select Contacts")
    search_var = tk.StringVar()
    group_var = tk.StringVar(value="All")
    ttk.Label(step2, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    search_entry = ttk.Entry(step2, textvariable=search_var, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(step2, text="Filter by Group:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    group_dropdown = ttk.Combobox(step2, textvariable=group_var, state="readonly", width=25)
    group_dropdown.grid(row=0, column=3, padx=5, pady=5)
    group_dropdown['values'] = ("All",) + tuple(get_all_group_names())
    group_dropdown.current(0)
    ttk.Label(step2, text="Available Contacts:").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10)
    avail_list = tk.Listbox(step2, selectmode=tk.MULTIPLE, width=40, height=18)
    avail_list.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.N)
    ttk.Label(step2, text="Selected Contacts:").grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=10)
    sel_list = tk.Listbox(step2, selectmode=tk.MULTIPLE, width=40, height=18)
    sel_list.grid(row=2, column=2, columnspan=2, padx=10, pady=5, sticky=tk.N)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, email, mobile FROM contacts ORDER BY name")
    all_contacts = c.fetchall()
    conn.close()
    contact_id_map = {idx: cid for idx, (cid, _, _, _) in enumerate(all_contacts)}
    contact_display_map = {cid: f"{name} <{mobile}>" for cid, name, _, mobile in all_contacts}
    sel_contact_ids = []
    if campaign and campaign.get('contact_ids'):
        sel_contact_ids = list(campaign['contact_ids'])
    def refresh_avail_list():
        avail_list.delete(0, tk.END)
        filter_text = search_var.get().lower()
        group_filter = group_var.get()
        selected_ids = set(sel_contact_ids)
        for idx, (cid, name, email, mobile) in enumerate(all_contacts):
            if cid in selected_ids:
                continue
            if (not filter_text or filter_text in name.lower() or filter_text in email.lower() or filter_text in (mobile or "")):
                if group_filter == "All" or contact_in_group(cid, group_filter):
                    avail_list.insert(tk.END, f"{name} <{mobile}>")
    def refresh_sel_list():
        sel_list.delete(0, tk.END)
        for cid in sel_contact_ids:
            sel_list.insert(tk.END, contact_display_map[cid])
    def contact_in_group(cid, group_short_name):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT 1 FROM group_members
            JOIN groups ON group_members.group_id = groups.id
            WHERE group_members.contact_id=? AND groups.short_name=?
        """, (cid, group_short_name))
        found = c.fetchone()
        conn.close()
        return bool(found)
    refresh_avail_list()
    refresh_sel_list()
    def add_selected():
        selected = avail_list.curselection()
        for idx in selected:
            display = avail_list.get(idx)
            for cid, disp in contact_display_map.items():
                if disp == display and cid not in sel_contact_ids:
                    sel_contact_ids.append(cid)
        refresh_avail_list()
        refresh_sel_list()
    def remove_selected():
        selected = sel_list.curselection()
        to_remove = [sel_contact_ids[idx] for idx in selected]
        for cid in to_remove:
            sel_contact_ids.remove(cid)
        refresh_avail_list()
        refresh_sel_list()
    add_btn = ttk.Button(step2, text=">>", command=add_selected)
    add_btn.grid(row=3, column=0, pady=5)
    remove_btn = ttk.Button(step2, text="<<", command=remove_selected)
    remove_btn.grid(row=3, column=2, pady=5)
    search_entry.bind("<KeyRelease>", lambda e: refresh_avail_list())
    group_dropdown.bind("<<ComboboxSelected>>", lambda e: refresh_avail_list())
    # Step 3: Send Preview
    step3 = ttk.Frame(notebook)
    notebook.add(step3, text="3. Send Preview")
    send_columns = ("S.No.", "Name", "Mobile", "Status")
    send_tree = ttk.Treeview(step3, columns=send_columns, show="headings", height=18)
    for col in send_columns:
        send_tree.heading(col, text=col)
        send_tree.column(col, width=180 if col!="S.No." else 60, anchor="center")
    send_tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    progress = ttk.Progressbar(step3, orient="horizontal", length=600, mode="determinate")
    progress.grid(row=1, column=0, columnspan=4, pady=5)
    counter_var = tk.StringVar(value="Total: 0 | Success: 0 | Failed: 0")
    timer_var = tk.StringVar(value="Elapsed: 0s")
    counter_label = ttk.Label(step3, textvariable=counter_var)
    counter_label.grid(row=2, column=0, sticky=tk.W, padx=10)
    timer_label = ttk.Label(step3, textvariable=timer_var)
    timer_label.grid(row=2, column=1, sticky=tk.W, padx=10)
    # Navigation buttons
    nav_frame = ttk.Frame(dialog)
    nav_frame.pack(fill=tk.X, pady=10)
    prev_btn = ttk.Button(nav_frame, text="<< Previous")
    next_btn = ttk.Button(nav_frame, text="Next >>")
    save_btn = ttk.Button(nav_frame, text="Save for Later")
    prev_btn.pack(side=tk.LEFT, padx=10)
    next_btn.pack(side=tk.RIGHT, padx=10)
    save_btn.pack(side=tk.RIGHT, padx=10)
    current_step = [0]
    def show_step(idx):
        notebook.select(idx)
        current_step[0] = idx
        prev_btn.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        if idx == 2:
            for item in send_tree.get_children():
                send_tree.delete(item)
            for i, cid in enumerate(sel_contact_ids, 1):
                name_mobile = contact_display_map.get(cid, "")
                name, mobile = name_mobile.split(" <")
                mobile = mobile.rstrip(">")
                send_tree.insert("", tk.END, values=(i, name, mobile, "Pending"))
            progress['value'] = 0
            progress['maximum'] = len(sel_contact_ids)
            counter_var.set(f"Total: {len(sel_contact_ids)} | Success: 0 | Failed: 0")
            timer_var.set("Elapsed: 0s")
            next_btn.config(text="Send SMS")
        else:
            next_btn.config(text="Next >>")
    def go_next():
        idx = current_step[0]
        if idx == 0:
            if not name_var.get().strip():
                messagebox.showerror("Error", "Campaign name is required!", parent=dialog)
                return
            if not message_text.get("1.0", tk.END).strip():
                messagebox.showerror("Error", "Message is required!", parent=dialog)
                return
            show_step(1)
        elif idx == 1:
            if not sel_contact_ids:
                messagebox.showerror("Error", "Please select at least one contact!", parent=dialog)
                return
            show_step(2)
        elif idx == 2:
            # Inline the send_email_campaign_wizard logic here
            import sqlite3, time, threading
            import email_utils
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
                messagebox.showerror("Email Settings Missing", "Sender email not set in settings.", parent=dialog)
                return
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(f"SELECT id, name, email, mobile FROM contacts WHERE id IN ({','.join(['?']*len(sel_contact_ids))})", sel_contact_ids)
            contacts = c.fetchall()
            conn.close()
            total = len(contacts)
            success = 0
            failed = 0
            start_time = time.time()
            def update_timer():
                while sending[0]:
                    elapsed = int(time.time() - start_time)
                    timer_var.set(f"Elapsed: {elapsed}s")
                    dialog.update_idletasks()
                    time.sleep(1)
            def scroll_to_row(idx):
                children = send_tree.get_children()
                if 0 <= idx < len(children):
                    send_tree.see(children[idx])
                    send_tree.selection_set(children[idx])
            def send_thread():
                nonlocal success, failed
                for idx, (cid, cname, cemail, cmobile) in enumerate(contacts):
                    scroll_to_row(idx)
                    send_tree.item(send_tree.get_children()[idx], tags=("current",))
                    dialog.update_idletasks()
                    personalized_subject = subject_var.get().replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
                    personalized_body = body_text.get("1.0", tk.END).replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
                    try:
                        if email_method == 'smtp':
                            smtp_settings = {"server": smtp_server, "port": smtp_port}
                            email_utils.send_email('smtp', smtp_settings, sender, password, cemail, personalized_subject, personalized_body)
                        elif email_method == 'sendgrid':
                            email_utils.send_email('sendgrid', {"sendgrid_api_key": sendgrid_api_key}, sender, None, cemail, personalized_subject, personalized_body)
                        elif email_method == 'ses':
                            email_utils.send_email('ses', {"ses_access_key": ses_access_key, "ses_secret_key": ses_secret_key, "ses_region": ses_region}, sender, None, cemail, personalized_subject, personalized_body)
                        send_tree.set(send_tree.get_children()[idx], column="Status", value="✔️")
                        success += 1
                    except Exception as e:
                        send_tree.set(send_tree.get_children()[idx], column="Status", value=f"❌ {e}")
                        failed += 1
                    counter_var.set(f"Total: {success+failed} | Success: {success} | Failed: {failed}")
                    dialog.update_idletasks()
                    progress['value'] = idx + 1
                    time.sleep(1.5)
                sending[0] = False
            sending = [True]
            threading.Thread(target=update_timer, daemon=True).start()
            threading.Thread(target=send_thread, daemon=True).start()
    def go_prev():
        idx = current_step[0]
        if idx > 0:
            show_step(idx-1)
    def save_campaign_for_later():
        cname = name_var.get().strip()
        cmessage = message_text.get("1.0", tk.END).strip()
        if not cname:
            messagebox.showerror("Error", "Campaign name is required!", parent=dialog)
            return
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS sms_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                message TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sms_campaign_contacts (
                campaign_id INTEGER,
                contact_id INTEGER,
                FOREIGN KEY(campaign_id) REFERENCES sms_campaigns(id),
                FOREIGN KEY(contact_id) REFERENCES contacts(id),
                UNIQUE(campaign_id, contact_id)
            )
        """)
        if mode == "add":
            c.execute("SELECT id FROM sms_campaigns WHERE name=?", (cname,))
            if c.fetchone():
                messagebox.showerror("Error", "A campaign with this name already exists!", parent=dialog)
                conn.close()
                return
            c.execute("INSERT INTO sms_campaigns (name, message) VALUES (?, ?)", (cname, cmessage))
            campaign_id = c.lastrowid
        else:
            campaign_id = campaign['id']
            c.execute("SELECT id FROM sms_campaigns WHERE name=? AND id!=?", (cname, campaign_id))
            if c.fetchone():
                messagebox.showerror("Error", "A campaign with this name already exists!", parent=dialog)
                conn.close()
                return
            c.execute("UPDATE sms_campaigns SET name=?, message=? WHERE id=?", (cname, cmessage, campaign_id))
            c.execute("DELETE FROM sms_campaign_contacts WHERE campaign_id=?", (campaign_id,))
        for cid in sel_contact_ids:
            c.execute("INSERT INTO sms_campaign_contacts (campaign_id, contact_id) VALUES (?, ?)", (campaign_id, cid))
        conn.commit()
        conn.close()
        load_sms_campaigns(tree)
        messagebox.showinfo("Saved", "SMS Campaign saved for later!", parent=dialog)
        dialog.destroy()
    prev_btn.config(command=go_prev)
    next_btn.config(command=go_next)
    save_btn.config(command=save_campaign_for_later)
    show_step(0)

# --- SMS Sending Logic ---
def send_sms_wizard(dialog, send_tree, contact_ids, campaign_name, message, progress, counter_var, timer_var):
    import sqlite3, time, threading, requests
    settings = get_settings()
    api_key = settings.get('sms_api_key', '')
    sender_id = settings.get('sms_sender_id', '')
    if not api_key or not sender_id:
        messagebox.showerror("SMS Settings Missing", "Please set SMS API Key and Sender ID in Settings.", parent=dialog)
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT id, name, email, mobile FROM contacts WHERE id IN ({','.join(['?']*len(contact_ids))})", contact_ids)
    contacts = c.fetchall()
    conn.close()
    total = len(contacts)
    success = 0
    failed = 0
    start_time = time.time()
    def update_timer():
        while sending[0]:
            elapsed = int(time.time() - start_time)
            timer_var.set(f"Elapsed: {elapsed}s")
            dialog.update_idletasks()
            time.sleep(1)
    def scroll_to_row(idx):
        children = send_tree.get_children()
        if 0 <= idx < len(children):
            send_tree.see(children[idx])
            send_tree.selection_set(children[idx])
    def send_thread():
        nonlocal success, failed
        base_url = "http://bulksmsbd.net/api/smsapi"
        for idx, (cid, cname, cemail, cmobile) in enumerate(contacts):
            scroll_to_row(idx)
            send_tree.item(send_tree.get_children()[idx], tags=("current",))
            dialog.update_idletasks()
            # Personalize message
            personalized_msg = message.replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
            params = {
                "api_key": api_key,
                "type": "text",
                "number": cmobile,
                "senderid": sender_id,
                "message": personalized_msg
            }
            try:
                resp = requests.get(base_url, params=params, timeout=10)
                # Debug: log response for troubleshooting
                print(f"SMS API response for {cmobile}: {resp.status_code} {resp.text}")
                if resp.status_code == 200 and ("SMS Send Success" in resp.text or 'success' in resp.text.lower()):
                    send_tree.set(send_tree.get_children()[idx], column="Status", value="✔️")
                    success += 1
                else:
                    send_tree.set(send_tree.get_children()[idx], column="Status", value="❌")
                    failed += 1
            except Exception as e:
                print(f"SMS API error for {cmobile}: {e}")
                send_tree.set(send_tree.get_children()[idx], column="Status", value="❌")
                failed += 1
            counter_var.set(f"Total: {success+failed} | Success: {success} | Failed: {failed}")
            dialog.update_idletasks()
            progress['value'] = idx + 1
            time.sleep(1.5)
        sending[0] = False
    sending = [True]
    threading.Thread(target=update_timer, daemon=True).start()
    threading.Thread(target=send_thread, daemon=True).start()
# --- Settings Dialog ---

def open_settings_dialog(parent):
    from tkinter import ttk, simpledialog
    settings = get_settings()
    dialog = tk.Toplevel(parent)
    dialog.title("Settings")
    dialog.geometry("800x700")
    dialog.transient(parent)
    dialog.grab_set()

    # Email Section Header
    email_header = ttk.Label(dialog, text="Email Settings", font=("Segoe UI", 13, "bold"))
    email_header.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(10, 0))

    email_fields = [
        ("Email Sending Method", 'email_method'),  # Dropdown: SMTP, SendGrid, SES
        ("Sender Email", 'sender_email'),
        ("Sender Password (for SMTP)", 'sender_pwd'),
        ("SMTP Server", 'smtp_server'),
        ("SMTP Port", 'smtp_port'),
        ("SendGrid API Key", 'sendgrid_api_key'),
        ("Amazon SES Access Key", 'ses_access_key'),
        ("Amazon SES Secret Key", 'ses_secret_key'),
        ("Amazon SES Region", 'ses_region'),
        ("Default Subject", 'default_subject'),
        ("Default Body", 'default_body'),
    ]
    vars = {}
    row_idx = 1
    for label, key in email_fields:
        ttk.Label(dialog, text=label+':').grid(row=row_idx, column=0, sticky=tk.W, padx=10, pady=5)
        if key == 'default_body':
            vars[key] = tk.Text(dialog, width=70, height=12)
            vars[key].insert(tk.END, settings.get(key, ''))
            vars[key].grid(row=row_idx, column=1, padx=10, pady=5)
        elif key == 'default_subject':
            vars[key] = tk.Entry(dialog, width=70)
            vars[key].insert(0, settings.get(key, ''))
            vars[key].grid(row=row_idx, column=1, padx=10, pady=5)
        elif key == 'sender_pwd' or key == 'ses_secret_key':
            vars[key] = tk.Entry(dialog, show='*', width=40)
            vars[key].insert(0, settings.get(key, ''))
            vars[key].grid(row=row_idx, column=1, padx=10, pady=5)
        elif key == 'email_method':
            vars[key] = ttk.Combobox(dialog, values=["SMTP", "SendGrid", "Amazon SES"], state="readonly", width=20)
            vars[key].set(settings.get(key, "SMTP"))
            vars[key].grid(row=row_idx, column=1, padx=10, pady=5, sticky=tk.W)
        else:
            vars[key] = tk.Entry(dialog, width=40)
            vars[key].insert(0, settings.get(key, ''))
            vars[key].grid(row=row_idx, column=1, padx=10, pady=5)
        row_idx += 1

    # SMS Section Header
    sms_header = ttk.Label(dialog, text="SMS Settings", font=("Segoe UI", 13, "bold"))
    sms_header.grid(row=row_idx, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(20, 0))
    row_idx += 1
    sms_fields = [
        ("SMS API Key", 'sms_api_key'),
        ("SMS Sender ID", 'sms_sender_id'),
    ]
    for label, key in sms_fields:
        ttk.Label(dialog, text=label+':').grid(row=row_idx, column=0, sticky=tk.W, padx=10, pady=5)
        vars[key] = tk.Entry(dialog, width=40)
        vars[key].insert(0, settings.get(key, ''))
        vars[key].grid(row=row_idx, column=1, padx=10, pady=5)
        row_idx += 1

    def on_save():
        new_settings = {}
        for label, key in email_fields + sms_fields:
            if key == 'default_body':
                new_settings[key] = vars[key].get("1.0", tk.END).strip()
            else:
                new_settings[key] = vars[key].get().strip()
        save_settings(new_settings)
        dialog.destroy()
    btn_frame = ttk.Frame(dialog)
    btn_frame.grid(row=row_idx, column=1, pady=15, sticky=tk.E)
    ttk.Button(btn_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    center_window(dialog, 800, 700)

# --- Other Dialogs and UI Sections ---

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

def get_all_group_names():
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT short_name FROM groups ORDER BY short_name")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    return groups

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
        name, email, mobile = values[1], values[2], values[3]
        c.execute("DELETE FROM contacts WHERE name=? AND email=? AND mobile=?", (name, email, mobile))
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
            self.dialog.update_idletasks()
            center_window(self.dialog, 400, 250)

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

def show_history_dialog():
    import tkinter as tk
    from tkinter import ttk
    import sqlite3
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

def show_email_campaigns(parent):
    # Clear existing content
    for widget in parent.winfo_children():
        widget.destroy()
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, pady=(0, 10))
    btn_group = ttk.Frame(toolbar)
    btn_group.pack(side=tk.LEFT)
    add_btn = ttk.Button(btn_group, text="Add Email Campaign", command=lambda: add_email_campaign(email_tree))
    add_btn.pack(side=tk.LEFT, padx=(0, 2))
    edit_btn = ttk.Button(btn_group, text="Edit Email Campaign", command=lambda: edit_email_campaign(email_tree))
    edit_btn.pack(side=tk.LEFT, padx=2)
    delete_btn = ttk.Button(btn_group, text="Delete Email Campaign", command=lambda: delete_email_campaign(email_tree))
    delete_btn.pack(side=tk.LEFT, padx=2)
    send_btn = ttk.Button(btn_group, text="Send Email Campaign", command=lambda: send_selected_email_campaign(email_tree))
    send_btn.pack(side=tk.LEFT, padx=2)
    history_btn = ttk.Button(toolbar, text="History", command=lambda: show_email_campaign_history(email_tree))
    history_btn.pack(side=tk.RIGHT, padx=5)
    columns = ("Name", "Subject", "Body")
    email_frame = ttk.Frame(parent)
    email_frame.pack(fill=tk.BOTH, expand=True)
    email_tree = ttk.Treeview(email_frame, columns=columns, show="headings", height=12)
    for col in columns:
        email_tree.heading(col, text=col)
        email_tree.column(col, width=220 if col!="Body" else 400)
    email_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(email_frame, orient=tk.VERTICAL, command=email_tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    email_tree.configure(yscrollcommand=scrollbar.set)
    load_email_campaigns(email_tree)

def load_email_campaigns(tree):
    for item in tree.get_children():
        tree.delete(item)
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            subject TEXT,
            body TEXT
        )
    """)
    for row in c.execute("SELECT name, subject, body FROM email_campaigns ORDER BY id DESC"):
        tree.insert("", tk.END, values=row)
    conn.close()

def add_email_campaign(tree):
    open_email_campaign_wizard(tree, mode="add")

def edit_email_campaign(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Edit Email Campaign", "Please select exactly one campaign to edit.")
        return
    iid = selected[0]
    old_name, old_subject, old_body = tree.item(iid, "values")
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM email_campaigns WHERE name=?", (old_name,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    campaign_id = row[0]
    c.execute("SELECT contact_id FROM email_campaign_contacts WHERE campaign_id=?", (campaign_id,))
    contact_ids = [r[0] for r in c.fetchall()]
    conn.close()
    open_email_campaign_wizard(tree, mode="edit", campaign={
        'id': campaign_id,
        'name': old_name,
        'subject': old_subject,
        'body': old_body,
        'contact_ids': contact_ids
    })

def send_selected_email_campaign(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Send Email Campaign", "Please select exactly one campaign to send.")
        return
    iid = selected[0]
    name, subject, body = tree.item(iid, "values")
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM email_campaigns WHERE name=?", (name,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    campaign_id = row[0]
    c.execute("SELECT contact_id FROM email_campaign_contacts WHERE campaign_id=?", (campaign_id,))
    contact_ids = [r[0] for r in c.fetchall()]
    conn.close()
    open_email_campaign_wizard(tree, mode="edit", campaign={
        'id': campaign_id,
        'name': name,
        'subject': subject,
        'body': body,
        'contact_ids': contact_ids
    })

def delete_email_campaign(tree):
    selected = tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Delete Email Campaign", "Please select exactly one campaign to delete.")
        return
    iid = selected[0]
    name = tree.item(iid, "values")[0]
    if not messagebox.askyesno("Delete Email Campaign", f"Are you sure you want to delete campaign '{name}'?"):
        return
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM email_campaigns WHERE name=?", (name,))
    c.execute("DELETE FROM email_campaign_contacts WHERE campaign_id IN (SELECT id FROM email_campaigns WHERE name=?)", (name,))
    conn.commit()
    conn.close()
    load_email_campaigns(tree)

def open_email_campaign_wizard(tree, mode="add", campaign=None):
    import tkinter as tk
    from tkinter import ttk, messagebox
    import sqlite3
    dialog = tk.Toplevel(tree.master)
    dialog.title("Add Email Campaign" if mode=="add" else "Edit Email Campaign")
    dialog.geometry("900x600")
    dialog.transient(tree.master)
    dialog.grab_set()
    center_window(dialog, 900, 600)
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    # Step 1: Details
    step1 = ttk.Frame(notebook)
    notebook.add(step1, text="1. Details")
    name_var = tk.StringVar(value=campaign['name'] if campaign else "")
    subject_var = tk.StringVar(value=campaign['subject'] if campaign else "")
    body_text = tk.Text(step1, width=80, height=8)
    body_text.insert(tk.END, campaign['body'] if campaign else "")
    details_header = ttk.Label(step1, text="Email Campaign Details", font=("Segoe UI", 14, "bold"))
    details_header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(10, 0), padx=10)
    ttk.Label(step1, text="Campaign Name *", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
    name_entry = ttk.Entry(step1, textvariable=name_var, width=40, font=("Segoe UI", 10))
    name_entry.grid(row=1, column=1, pady=10, padx=10, sticky=tk.W)
    name_entry.focus_set()
    ttk.Label(step1, text="Subject *", font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.W, pady=10, padx=10)
    subject_entry = ttk.Entry(step1, textvariable=subject_var, width=60, font=("Segoe UI", 10))
    subject_entry.grid(row=2, column=1, pady=10, padx=10, sticky=tk.W)
    ttk.Label(step1, text="Body *", font=("Segoe UI", 10)).grid(row=3, column=0, sticky=tk.NW, pady=10, padx=10)
    body_text.configure(font=("Segoe UI", 10))
    step1.grid_rowconfigure(3, weight=1)
    step1.grid_columnconfigure(1, weight=1)
    body_text.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")
    body_tip = ttk.Label(step1, text="You can use {{name}}, {{mobile}}, {{email}} as placeholders.", font=("Segoe UI", 9, "italic"), foreground="#666")
    body_tip.grid(row=4, column=1, sticky=tk.W, padx=10, pady=(0, 10))
    # Step 2: Select Contacts
    step2 = ttk.Frame(notebook)
    notebook.add(step2, text="2. Select Contacts")
    search_var = tk.StringVar()
    group_var = tk.StringVar(value="All")
    ttk.Label(step2, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    search_entry = ttk.Entry(step2, textvariable=search_var, width=30)
    search_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(step2, text="Filter by Group:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
    group_dropdown = ttk.Combobox(step2, textvariable=group_var, state="readonly", width=25)
    group_dropdown.grid(row=0, column=3, padx=5, pady=5)
    group_dropdown['values'] = ("All",) + tuple(get_all_group_names())
    group_dropdown.current(0)
    ttk.Label(step2, text="Available Contacts:").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10)
    avail_list = tk.Listbox(step2, selectmode=tk.MULTIPLE, width=40, height=18)
    avail_list.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.N)
    ttk.Label(step2, text="Selected Contacts:").grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=10)
    sel_list = tk.Listbox(step2, selectmode=tk.MULTIPLE, width=40, height=18)
    sel_list.grid(row=2, column=2, columnspan=2, padx=10, pady=5, sticky=tk.N)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, email, mobile FROM contacts ORDER BY name")
    all_contacts = c.fetchall()
    conn.close()
    contact_id_map = {idx: cid for idx, (cid, _, _, _) in enumerate(all_contacts)}
    contact_display_map = {cid: f"{name} <{email}>" for cid, name, email, _ in all_contacts}
    sel_contact_ids = []
    if campaign and campaign.get('contact_ids'):
        sel_contact_ids = list(campaign['contact_ids'])
    def refresh_avail_list():
        avail_list.delete(0, tk.END)
        filter_text = search_var.get().lower()
        group_filter = group_var.get()
        selected_ids = set(sel_contact_ids)
        for idx, (cid, name, email, mobile) in enumerate(all_contacts):
            if cid in selected_ids:
                continue
            if (not filter_text or filter_text in name.lower() or filter_text in email.lower() or filter_text in (mobile or "")):
                if group_filter == "All" or contact_in_group(cid, group_filter):
                    avail_list.insert(tk.END, f"{name} <{email}>")
    def refresh_sel_list():
        sel_list.delete(0, tk.END)
        for cid in sel_contact_ids:
            sel_list.insert(tk.END, contact_display_map[cid])
    def contact_in_group(cid, group_short_name):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT 1 FROM group_members
            JOIN groups ON group_members.group_id = groups.id
            WHERE group_members.contact_id=? AND groups.short_name=?
        """, (cid, group_short_name))
        found = c.fetchone()
        conn.close()
        return bool(found)
    refresh_avail_list()
    refresh_sel_list()
    def add_selected():
        selected = avail_list.curselection()
        for idx in selected:
            display = avail_list.get(idx)
            for cid, disp in contact_display_map.items():
                if disp == display and cid not in sel_contact_ids:
                    sel_contact_ids.append(cid)
        refresh_avail_list()
        refresh_sel_list()
    def remove_selected():
        selected = sel_list.curselection()
        to_remove = [sel_contact_ids[idx] for idx in selected]
        for cid in to_remove:
            sel_contact_ids.remove(cid)
        refresh_avail_list()
        refresh_sel_list()
    add_btn = ttk.Button(step2, text=">>", command=add_selected)
    add_btn.grid(row=3, column=0, pady=5)
    remove_btn = ttk.Button(step2, text="<<", command=remove_selected)
    remove_btn.grid(row=3, column=2, pady=5)
    search_entry.bind("<KeyRelease>", lambda e: refresh_avail_list())
    group_dropdown.bind("<<ComboboxSelected>>", lambda e: refresh_avail_list())
    # Step 3: Send Preview
    step3 = ttk.Frame(notebook)
    notebook.add(step3, text="3. Send Preview")
    send_columns = ("S.No.", "Name", "Email", "Status")
    send_tree = ttk.Treeview(step3, columns=send_columns, show="headings", height=18)
    for col in send_columns:
        send_tree.heading(col, text=col)
        send_tree.column(col, width=180 if col!="S.No." else 60, anchor="center")
    send_tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    progress = ttk.Progressbar(step3, orient="horizontal", length=600, mode="determinate")
    progress.grid(row=1, column=0, columnspan=4, pady=5)
    counter_var = tk.StringVar(value="Total: 0 | Success: 0 | Failed: 0")
    timer_var = tk.StringVar(value="Elapsed: 0s")
    counter_label = ttk.Label(step3, textvariable=counter_var)
    counter_label.grid(row=2, column=0, sticky=tk.W, padx=10)
    timer_label = ttk.Label(step3, textvariable=timer_var)
    timer_label.grid(row=2, column=1, sticky=tk.W, padx=10)
    # Navigation buttons
    nav_frame = ttk.Frame(dialog)
    nav_frame.pack(fill=tk.X, pady=10)
    prev_btn = ttk.Button(nav_frame, text="<< Previous")
    next_btn = ttk.Button(nav_frame, text="Next >>")
    save_btn = ttk.Button(nav_frame, text="Save for Later")
    prev_btn.pack(side=tk.LEFT, padx=10)
    next_btn.pack(side=tk.RIGHT, padx=10)
    save_btn.pack(side=tk.RIGHT, padx=10)
    current_step = [0]
    def show_step(idx):
        notebook.select(idx)
        current_step[0] = idx
        prev_btn.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        if idx == 2:
            for item in send_tree.get_children():
                send_tree.delete(item)
            for i, cid in enumerate(sel_contact_ids, 1):
                name_mobile = contact_display_map.get(cid, "")
                if "<" in name_mobile:
                    name, mobile = name_mobile.split(" <")
                    mobile = mobile.rstrip(">")
                else:
                    name, mobile = name_mobile, ""
                send_tree.insert("", tk.END, values=(i, name, mobile, "Pending"))
            progress['value'] = 0
            progress['maximum'] = len(sel_contact_ids)
            counter_var.set(f"Total: {len(sel_contact_ids)} | Success: 0 | Failed: 0")
            timer_var.set("Elapsed: 0s")
            next_btn.config(text="Send Emails")
        else:
            next_btn.config(text="Next >>")
    def go_next():
        idx = current_step[0]
        if idx == 0:
            if not name_var.get().strip():
                messagebox.showerror("Error", "Campaign name is required!", parent=dialog)
                return
            if not subject_var.get().strip():
                messagebox.showerror("Error", "Subject is required!", parent=dialog)
                return
            if not body_text.get("1.0", tk.END).strip():
                messagebox.showerror("Error", "Body is required!", parent=dialog)
                return
            show_step(1)
        elif idx == 1:
            if not sel_contact_ids:
                messagebox.showerror("Error", "Please select at least one contact!", parent=dialog)
                return
            show_step(2)
        elif idx == 2:
            send_email_campaign(dialog, send_tree, sel_contact_ids, name_var.get(), subject_var.get(), body_text.get("1.0", tk.END), progress, counter_var, timer_var)
    def go_prev():
        idx = current_step[0]
        if idx > 0:
            show_step(idx-1)
    def save_campaign_for_later():
        cname = name_var.get().strip()
        csubject = subject_var.get().strip()
        cbody = body_text.get("1.0", tk.END).strip()
        if not cname:
            messagebox.showerror("Error", "Campaign name is required!", parent=dialog)
            return
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS email_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                subject TEXT,
                body TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS email_campaign_contacts (
                campaign_id INTEGER,
                contact_id INTEGER,
                FOREIGN KEY(campaign_id) REFERENCES email_campaigns(id),
                FOREIGN KEY(contact_id) REFERENCES contacts(id),
                UNIQUE(campaign_id, contact_id)
            )
        """)
        if mode == "add":
            c.execute("SELECT id FROM email_campaigns WHERE name=?", (cname,))
            if c.fetchone():
                messagebox.showerror("Error", "A campaign with this name already exists!", parent=dialog)
                conn.close()
                return
            c.execute("INSERT INTO email_campaigns (name, subject, body) VALUES (?, ?, ?)", (cname, csubject, cbody))
            campaign_id = c.lastrowid
        else:
            campaign_id = campaign['id']
            c.execute("SELECT id FROM email_campaigns WHERE name=? AND id!=?", (cname, campaign_id))
            if c.fetchone():
                messagebox.showerror("Error", "A campaign with this name already exists!", parent=dialog)
                conn.close()
                return
            c.execute("UPDATE email_campaigns SET name=?, subject=?, body=? WHERE id=?", (cname, csubject, cbody, campaign_id))
            c.execute("DELETE FROM email_campaign_contacts WHERE campaign_id=?", (campaign_id,))
        for cid in sel_contact_ids:
            c.execute("INSERT OR IGNORE INTO email_campaign_contacts (campaign_id, contact_id) VALUES (?, ?)", (campaign_id, cid))
        conn.commit()
        conn.close()
        load_email_campaigns(tree)
        messagebox.showinfo("Saved", "Email Campaign saved for later!", parent=dialog)
        dialog.destroy()
    prev_btn.config(command=go_prev)
    next_btn.config(command=go_next)
    save_btn.config(command=save_campaign_for_later)
    show_step(0)

def send_email_campaign(dialog, send_tree, contact_ids, campaign_name, subject, body, progress, counter_var, timer_var):
    import sqlite3, time, threading
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
        messagebox.showerror("Email Settings Missing", "Sender email not set in settings.", parent=dialog)
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_campaign_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            contact_id INTEGER,
            timestamp TEXT,
            status TEXT,
            error TEXT
        )
    """)
    # Get campaign_id from campaign_name
    c.execute("SELECT id FROM email_campaigns WHERE name=?", (campaign_name,))
    row = c.fetchone()
    campaign_id = row[0] if row else None
    for idx, (cid, cname, cemail, cmobile) in enumerate(contacts):
        scroll_to_row(idx)
        send_tree.item(send_tree.get_children()[idx], tags=("current",))
        dialog.update_idletasks()
        personalized_subject = subject.replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
        personalized_body = body.replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
        try:
            if email_method == 'smtp':
                smtp_settings = {"server": smtp_server, "port": smtp_port}
                email_utils.send_email('smtp', smtp_settings, sender, password, cemail, personalized_subject, personalized_body)
            elif email_method == 'sendgrid':
                email_utils.send_email('sendgrid', {"sendgrid_api_key": sendgrid_api_key}, sender, None, cemail, personalized_subject, personalized_body)
            elif email_method == 'ses':
                email_utils.send_email('ses', {"ses_access_key": ses_access_key, "ses_secret_key": ses_secret_key, "ses_region": ses_region}, sender, None, cemail, personalized_subject, personalized_body)
            send_tree.set(send_tree.get_children()[idx], column="Status", value="✔️")
            c.execute("INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, error) VALUES (?, ?, datetime('now'), ?, '')", (campaign_id, cid, 'Sent'))
            success += 1
        except Exception as e:
            send_tree.set(send_tree.get_children()[idx], column="Status", value=f"❌ {e}")
            c.execute("INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, error) VALUES (?, ?, datetime('now'), ?, ?)", (campaign_id, cid, 'Failed', str(e)))
            failed += 1
        counter_var.set(f"Total: {success+failed} | Success: {success} | Failed: {failed}")
        dialog.update_idletasks()
        progress['value'] = idx + 1
        time.sleep(1.5)
    conn.commit()
    conn.close()
    sending[0] = False
    # --- Email Campaign History Dialog ---
def show_email_campaign_history(tree):
    import tkinter as tk
    from tkinter import ttk
    import sqlite3
    hist_win = tk.Toplevel()
    hist_win.title("Email Campaign History")
    hist_win.geometry("900x500")
    hist_win.transient()
    hist_win.grab_set()
    columns = ("Timestamp", "Campaign Name", "Contact Name", "Email", "Status", "Error")
    treeview = ttk.Treeview(hist_win, columns=columns, show="headings")
    for col in columns:
        treeview.heading(col, text=col)
        treeview.column(col, width=150)
    treeview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS email_campaign_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            contact_id INTEGER,
            timestamp TEXT,
            status TEXT,
            error TEXT
        )
    """)
    c.execute("""
        SELECT h.timestamp, ec.name, ct.name, ct.email, h.status, h.error
        FROM email_campaign_history h
        JOIN email_campaigns ec ON h.campaign_id = ec.id
        JOIN contacts ct ON h.contact_id = ct.id
        ORDER BY h.id DESC LIMIT 500
    """)
    for row in c.fetchall():
        treeview.insert("", tk.END, values=row)
    conn.close()