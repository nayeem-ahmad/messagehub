import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import threading
import time
import requests
from .common import DB_FILE, get_settings, center_window, get_all_group_names

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
            import sqlite3, time, threading, requests
            settings = get_settings()
            api_key = settings.get('sms_api_key', '')
            sender_id = settings.get('sms_sender_id', '')
            if not api_key or not sender_id:
                messagebox.showerror("SMS Settings Missing", "Please set SMS API Key and Sender ID in Settings.", parent=dialog)
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
                base_url = "http://bulksmsbd.net/api/smsapi"
                for idx, (cid, cname, cemail, cmobile) in enumerate(contacts):
                    scroll_to_row(idx)
                    send_tree.item(send_tree.get_children()[idx], tags=("current",))
                    dialog.update_idletasks()
                    personalized_msg = message_text.get("1.0", tk.END).replace("{{name}}", cname).replace("{{email}}", cemail).replace("{{mobile}}", cmobile)
                    params = {
                        "api_key": api_key,
                        "type": "text",
                        "number": cmobile,
                        "senderid": sender_id,
                        "message": personalized_msg
                    }
                    try:
                        resp = requests.get(base_url, params=params, timeout=10)
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
