import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import time
import threading
from datetime import datetime
from .common import DB_FILE, get_settings, center_window, get_all_group_names, apply_striped_rows
from services import email_utils


def show_email_campaigns(parent):
    # Clear existing content
    for widget in parent.winfo_children():
        widget.destroy()
    toolbar = ttk.Frame(parent)
    toolbar.pack(fill=tk.X, pady=(0, 10))
    btn_group = ttk.Frame(toolbar)
    btn_group.pack(side=tk.LEFT)
    add_btn = ttk.Button(btn_group, text="➕ Add Email Campaign", command=lambda: add_email_campaign(email_tree))
    add_btn.pack(side=tk.LEFT, padx=(0, 2))
    edit_btn = ttk.Button(btn_group, text="✏️ Edit Email Campaign", command=lambda: edit_email_campaign(email_tree))
    edit_btn.pack(side=tk.LEFT, padx=2)
    delete_btn = ttk.Button(btn_group, text="🗑️ Delete Email Campaign", command=lambda: delete_email_campaign(email_tree))
    delete_btn.pack(side=tk.LEFT, padx=2)
    send_btn = ttk.Button(btn_group, text="✉️ Send Email Campaign", command=lambda: send_selected_email_campaign(email_tree))
    send_btn.pack(side=tk.LEFT, padx=2)
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
    count_var = tk.StringVar(value="Total: 0 | Selected: 0")
    count_label = ttk.Label(parent, textvariable=count_var)
    count_label.pack(anchor="w", pady=(5, 0))

    def update_counts(event=None):
        total = len(email_tree.get_children())
        selected = len(email_tree.selection())
        count_var.set(f"Total: {total} | Selected: {selected}")

    email_tree.update_counts = update_counts
    load_email_campaigns(email_tree)
    update_counts()
    email_tree.bind("<<TreeviewSelect>>", update_counts)

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
    apply_striped_rows(tree)
    if hasattr(tree, 'update_counts'):
        tree.update_counts()

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
    c.execute("SELECT id FROM email_campaigns WHERE name=?", (name,))
    row = c.fetchone()
    campaign_id = row[0] if row else None
    if campaign_id:
        c.execute("DELETE FROM email_campaign_contacts WHERE campaign_id=?", (campaign_id,))
        c.execute("DELETE FROM email_campaigns WHERE id=?", (campaign_id,))
    else:
        conn.close()
        load_email_campaigns(tree)
        return
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
        # Filter out contact IDs that no longer exist in the database
        all_contact_ids = {cid for cid, _, _, _ in all_contacts}
        valid_contact_ids = [cid for cid in campaign['contact_ids'] if cid in all_contact_ids]
        sel_contact_ids = valid_contact_ids
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
        # Filter out contact IDs that no longer exist
        valid_contact_ids = []
        for cid in sel_contact_ids:
            if cid in contact_display_map:
                sel_list.insert(tk.END, contact_display_map[cid])
                valid_contact_ids.append(cid)
        # Update the list to only include valid contacts
        sel_contact_ids[:] = valid_contact_ids
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
    prev_btn = ttk.Button(nav_frame, text="⬅️ Previous")
    next_btn = ttk.Button(nav_frame, text="Next ➡️")
    save_btn = ttk.Button(nav_frame, text="💾 Save for Later")
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
            apply_striped_rows(send_tree)
            progress['value'] = 0
            progress['maximum'] = len(sel_contact_ids)
            counter_var.set(f"Total: {len(sel_contact_ids)} | Success: 0 | Failed: 0")
            timer_var.set("Elapsed: 0s")
            next_btn.config(text="Send Emails")
        else:
            next_btn.config(text="Next ➡️")
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

def send_email_campaign(dialog, send_tree, contact_ids, campaign_name, subject, body, progress, counter_var, timer_var, scroll_to_row=None):
    """Send an email campaign to the provided contact IDs."""
    import sqlite3, time, threading
    settings = get_settings()
    email_method = settings.get('email_method', 'SMTP').lower()
    sender = settings.get('sender_email', '')
    sender_name = settings.get('sender_name', '')
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

    c.execute("SELECT id FROM email_campaigns WHERE name=?", (campaign_name,))
    row = c.fetchone()
    if row:
        campaign_id = row[0]
        c.execute(
            "UPDATE email_campaigns SET subject=?, body=? WHERE id=?",
            (subject, body, campaign_id),
        )
        c.execute("DELETE FROM email_campaign_contacts WHERE campaign_id=?", (campaign_id,))
    else:
        c.execute(
            "INSERT INTO email_campaigns (name, subject, body) VALUES (?, ?, ?)",
            (campaign_name, subject, body),
        )
        campaign_id = c.lastrowid

    for cid in contact_ids:
        c.execute(
            "INSERT OR IGNORE INTO email_campaign_contacts (campaign_id, contact_id) VALUES (?, ?)",
            (campaign_id, cid),
        )

    placeholders = ",".join(["?"] * len(contact_ids))
    c.execute(
        f"SELECT id, name, email, mobile FROM contacts WHERE id IN ({placeholders})",
        contact_ids,
    )
    contacts = c.fetchall()

    conn.commit()
    conn.close()

    success = 0
    failed = 0
    sending = [True]
    start_time = time.time()

    def update_timer():
        while sending[0]:
            elapsed = int(time.time() - start_time)
            timer_var.set(f"Elapsed: {elapsed}s")
            dialog.update_idletasks()
            time.sleep(1)

    def default_scroll(idx):
        children = send_tree.get_children()
        if 0 <= idx < len(children):
            send_tree.see(children[idx])
            send_tree.selection_set(children[idx])

    scroll = scroll_to_row or default_scroll

    def send_thread():
        nonlocal success, failed
        conn_th = sqlite3.connect(DB_FILE)
        c_th = conn_th.cursor()
        for idx, (cid, cname, cemail, cmobile) in enumerate(contacts):
            scroll(idx)
            iid = send_tree.get_children()[idx]
            tags = [t for t in send_tree.item(iid, "tags") if t not in ("evenrow", "oddrow", "current")]
            tags.append("current")
            tags.append("evenrow" if idx % 2 == 0 else "oddrow")
            send_tree.item(iid, tags=tuple(tags))
            dialog.update_idletasks()
            personalized_subject = subject.replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
            personalized_body = body.replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
            try:
                if email_method == 'smtp':
                    smtp_settings = {"server": smtp_server, "port": smtp_port}
                    email_utils.send_email('smtp', smtp_settings, sender, password, cemail, personalized_subject, personalized_body, sender_name)
                elif email_method == 'sendgrid':
                    email_utils.send_email('sendgrid', {"sendgrid_api_key": sendgrid_api_key}, sender, None, cemail, personalized_subject, personalized_body, sender_name)
                elif email_method == 'ses':
                    email_utils.send_email('ses', {"ses_access_key": ses_access_key, "ses_secret_key": ses_secret_key, "ses_region": ses_region}, sender, None, cemail, personalized_subject, personalized_body, sender_name)
                send_tree.set(send_tree.get_children()[idx], column="Status", value="✔️")
                c_th.execute(
                    "INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, error) VALUES (?, ?, datetime('now'), ?, '')",
                    (campaign_id, cid, 'Sent')
                )
                conn_th.commit()
                success += 1
            except Exception as e:
                send_tree.set(send_tree.get_children()[idx], column="Status", value=f"❌ {e}")
                c_th.execute(
                    "INSERT INTO email_campaign_history (campaign_id, contact_id, timestamp, status, error) VALUES (?, ?, datetime('now'), ?, ?)",
                    (campaign_id, cid, 'Failed', str(e))
                )
                conn_th.commit()
                failed += 1
            counter_var.set(f"Total: {success+failed} | Success: {success} | Failed: {failed}")
            dialog.update_idletasks()
            progress['value'] = idx + 1
            time.sleep(1.5)

        conn_th.commit()
        conn_th.close()
        sending[0] = False

    threading.Thread(target=update_timer, daemon=True).start()
    threading.Thread(target=send_thread, daemon=True).start()
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
    count_var = tk.StringVar(value="Total: 0 | Selected: 0")
    ttk.Label(hist_win, textvariable=count_var).pack(anchor="w", padx=10, pady=(0,5))

    def update_counts(event=None):
        total = len(treeview.get_children())
        selected = len(treeview.selection())
        count_var.set(f"Total: {total} | Selected: {selected}")

    treeview.bind("<<TreeviewSelect>>", update_counts)
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
    apply_striped_rows(treeview)
    update_counts()

