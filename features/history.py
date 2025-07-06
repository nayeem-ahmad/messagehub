import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import calendar
from .common import DB_FILE, apply_striped_rows, center_window

class DateTimePicker(tk.Toplevel):
    """Custom date and time picker dialog"""
    def __init__(self, parent, initial_datetime=None, title="Select Date and Time"):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.result = None
        
        # Set initial datetime
        if initial_datetime:
            self.selected_date = initial_datetime.date()
            self.selected_time = initial_datetime.time()
        else:
            now = datetime.now()
            self.selected_date = now.date()
            self.selected_time = now.time()
        
        self.setup_ui()
        center_window(self, 400, 350)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Calendar frame
        cal_frame = ttk.LabelFrame(main_frame, text="Date", padding=10)
        cal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create calendar
        self.create_calendar(cal_frame)
        
        # Time frame
        time_frame = ttk.LabelFrame(main_frame, text="Time", padding=10)
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.create_time_selector(time_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Now", command=self.set_now).pack(side=tk.LEFT)
        
    def create_calendar(self, parent):
        # Year and month selection
        year_month_frame = ttk.Frame(parent)
        year_month_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.year_var = tk.IntVar(value=self.selected_date.year)
        self.month_var = tk.IntVar(value=self.selected_date.month)
        
        ttk.Button(year_month_frame, text="◀", width=3, command=self.prev_month).pack(side=tk.LEFT)
        
        month_label = ttk.Label(year_month_frame, text="")
        month_label.pack(side=tk.LEFT, expand=True)
        self.month_label = month_label
        
        ttk.Button(year_month_frame, text="▶", width=3, command=self.next_month).pack(side=tk.RIGHT)
        
        # Calendar grid
        self.cal_frame = ttk.Frame(parent)
        self.cal_frame.pack()
        
        self.update_calendar()
        
    def create_time_selector(self, parent):
        time_controls = ttk.Frame(parent)
        time_controls.pack()
        
        # Hour
        ttk.Label(time_controls, text="Hour:").grid(row=0, column=0, padx=(0, 5))
        self.hour_var = tk.IntVar(value=self.selected_time.hour)
        hour_spin = ttk.Spinbox(time_controls, from_=0, to=23, textvariable=self.hour_var, width=5, format="%02.0f")
        hour_spin.grid(row=0, column=1, padx=(0, 10))
        
        # Minute
        ttk.Label(time_controls, text="Minute:").grid(row=0, column=2, padx=(0, 5))
        self.minute_var = tk.IntVar(value=self.selected_time.minute)
        minute_spin = ttk.Spinbox(time_controls, from_=0, to=59, textvariable=self.minute_var, width=5, format="%02.0f")
        minute_spin.grid(row=0, column=3)
        
    def update_calendar(self):
        # Clear existing calendar
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
            
        # Update month label
        month_name = calendar.month_name[self.month_var.get()]
        self.month_label.config(text=f"{month_name} {self.year_var.get()}")
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            ttk.Label(self.cal_frame, text=day, font=("Segoe UI", 8, "bold")).grid(row=0, column=i, padx=1, pady=1)
        
        # Calendar days
        cal = calendar.monthcalendar(self.year_var.get(), self.month_var.get())
        self.day_buttons = {}
        
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                    
                btn = tk.Button(self.cal_frame, text=str(day), width=3, height=1,
                               command=lambda d=day: self.select_day(d))
                btn.grid(row=week_num, column=day_num, padx=1, pady=1)
                
                # Highlight selected day
                if (day == self.selected_date.day and 
                    self.month_var.get() == self.selected_date.month and 
                    self.year_var.get() == self.selected_date.year):
                    btn.config(bg="#007ACC", fg="white")
                    
                self.day_buttons[day] = btn
    
    def prev_month(self):
        if self.month_var.get() == 1:
            self.month_var.set(12)
            self.year_var.set(self.year_var.get() - 1)
        else:
            self.month_var.set(self.month_var.get() - 1)
        self.update_calendar()
        
    def next_month(self):
        if self.month_var.get() == 12:
            self.month_var.set(1)
            self.year_var.set(self.year_var.get() + 1)
        else:
            self.month_var.set(self.month_var.get() + 1)
        self.update_calendar()
        
    def select_day(self, day):
        self.selected_date = datetime(self.year_var.get(), self.month_var.get(), day).date()
        self.update_calendar()
        
    def set_now(self):
        now = datetime.now()
        self.selected_date = now.date()
        self.selected_time = now.time()
        self.year_var.set(now.year)
        self.month_var.set(now.month)
        self.hour_var.set(now.hour)
        self.minute_var.set(now.minute)
        self.update_calendar()
        
    def ok_clicked(self):
        # Combine date and time
        self.result = datetime.combine(
            self.selected_date,
            datetime.min.time().replace(hour=self.hour_var.get(), minute=self.minute_var.get())
        )
        self.destroy()
        
    def cancel_clicked(self):
        self.result = None
        self.destroy()

def show_history_dialog():
    hist_win = tk.Toplevel()
    hist_win.title("Email & SMS History")
    
    # Make window full-screen
    hist_win.state('zoomed')  # Windows full-screen
    hist_win.transient()
    hist_win.grab_set()

    # Main container with horizontal layout
    main_container = ttk.Frame(hist_win)
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Left panel for list view
    left_panel = ttk.Frame(main_container)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    # Right panel for details
    right_panel = ttk.LabelFrame(main_container, text="Details", padding=10)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
    right_panel.configure(width=400)  # Fixed width for details panel

    # Top controls in left panel
    option_var = tk.StringVar(value="Email")
    search_var = tk.StringVar()
    
    # Date/time range variables (default to today's full day)
    today = datetime.now()
    start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    from_datetime_var = tk.StringVar(value=start_of_today.strftime("%Y-%m-%d %H:%M"))
    to_datetime_var = tk.StringVar(value=end_of_today.strftime("%Y-%m-%d %H:%M"))
    date_filter_enabled = tk.BooleanVar(value=True)  # Enable date filter by default

    top_frame = ttk.Frame(left_panel)
    top_frame.pack(fill=tk.X, pady=(0, 10))

    # First row: Radio buttons and date filter controls
    first_row = ttk.Frame(top_frame)
    first_row.pack(fill=tk.X, pady=(0, 5))
    
    # Radio buttons
    controls_left = ttk.Frame(first_row)
    controls_left.pack(side=tk.LEFT)
    
    ttk.Radiobutton(controls_left, text="Email", variable=option_var, value="Email", command=lambda: load_history()).pack(side=tk.LEFT)
    ttk.Radiobutton(controls_left, text="SMS", variable=option_var, value="SMS", command=lambda: load_history()).pack(side=tk.LEFT, padx=(10,0))

    # Date filter controls
    date_controls = ttk.Frame(first_row)
    date_controls.pack(side=tk.RIGHT)
    
    ttk.Checkbutton(date_controls, text="DateTime Filter:", variable=date_filter_enabled, command=lambda: load_history()).pack(side=tk.LEFT, padx=(0, 5))
    
    # From datetime controls
    from_frame = ttk.Frame(date_controls)
    from_frame.pack(side=tk.LEFT, padx=(5, 0))
    ttk.Label(from_frame, text="From:").pack(side=tk.TOP, anchor="w")
    
    # From input container with entry and button side by side
    from_input_frame = ttk.Frame(from_frame)
    from_input_frame.pack(side=tk.TOP, fill=tk.X)
    from_datetime_entry = ttk.Entry(from_input_frame, textvariable=from_datetime_var, width=20, font=("Segoe UI", 9))
    from_datetime_entry.pack(side=tk.LEFT, padx=(0, 2))
    ttk.Button(from_input_frame, text="📅", width=3, command=lambda: open_datetime_picker("from")).pack(side=tk.LEFT)
    
    # To datetime controls  
    to_frame = ttk.Frame(date_controls)
    to_frame.pack(side=tk.LEFT, padx=(5, 0))
    ttk.Label(to_frame, text="To:").pack(side=tk.TOP, anchor="w")
    
    # To input container with entry and button side by side
    to_input_frame = ttk.Frame(to_frame)
    to_input_frame.pack(side=tk.TOP, fill=tk.X)
    to_datetime_entry = ttk.Entry(to_input_frame, textvariable=to_datetime_var, width=20, font=("Segoe UI", 9))
    to_datetime_entry.pack(side=tk.LEFT, padx=(0, 2))
    ttk.Button(to_input_frame, text="📅", width=3, command=lambda: open_datetime_picker("to")).pack(side=tk.LEFT)
    
    def open_datetime_picker(field_type):
        """Open the custom datetime picker"""
        current_value = from_datetime_var.get() if field_type == "from" else to_datetime_var.get()
        try:
            initial_dt = datetime.strptime(current_value, "%Y-%m-%d %H:%M")
        except ValueError:
            initial_dt = datetime.now()
            
        picker = DateTimePicker(hist_win, initial_dt, f"Select {field_type.title()} DateTime")
        hist_win.wait_window(picker)
        
        if picker.result:
            formatted_dt = picker.result.strftime("%Y-%m-%d %H:%M")
            if field_type == "from":
                from_datetime_var.set(formatted_dt)
            else:
                to_datetime_var.set(formatted_dt)
            load_history()
    
    # Quick date buttons
    quick_dates = ttk.Frame(date_controls)
    quick_dates.pack(side=tk.LEFT, padx=(10, 0))
    
    def set_today():
        today = datetime.now()
        start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        from_datetime_var.set(start_of_today.strftime("%Y-%m-%d %H:%M"))
        to_datetime_var.set(end_of_today.strftime("%Y-%m-%d %H:%M"))
        date_filter_enabled.set(True)
        load_history()
    
    def set_last_24_hours():
        now = datetime.now()
        day_ago = now - timedelta(hours=24)
        from_datetime_var.set(day_ago.strftime("%Y-%m-%d %H:%M"))
        to_datetime_var.set(now.strftime("%Y-%m-%d %H:%M"))
        date_filter_enabled.set(True)
        load_history()
    
    def set_last_7_days():
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        from_datetime_var.set(week_ago.replace(hour=0, minute=0).strftime("%Y-%m-%d %H:%M"))
        to_datetime_var.set(today.replace(hour=23, minute=59).strftime("%Y-%m-%d %H:%M"))
        date_filter_enabled.set(True)
        load_history()
    
    def set_last_30_days():
        today = datetime.now()
        month_ago = today - timedelta(days=30)
        from_datetime_var.set(month_ago.replace(hour=0, minute=0).strftime("%Y-%m-%d %H:%M"))
        to_datetime_var.set(today.replace(hour=23, minute=59).strftime("%Y-%m-%d %H:%M"))
        date_filter_enabled.set(True)
        load_history()
    
    def set_all_records():
        date_filter_enabled.set(False)
        load_history()
    
    ttk.Button(quick_dates, text="Today", command=set_today, width=8).pack(side=tk.LEFT, padx=1)
    ttk.Button(quick_dates, text="24hrs", command=set_last_24_hours, width=8).pack(side=tk.LEFT, padx=1)
    ttk.Button(quick_dates, text="7 Days", command=set_last_7_days, width=8).pack(side=tk.LEFT, padx=1)
    ttk.Button(quick_dates, text="30 Days", command=set_last_30_days, width=8).pack(side=tk.LEFT, padx=1)
    ttk.Button(quick_dates, text="All", command=set_all_records, width=8).pack(side=tk.LEFT, padx=1)

    # Second row: Search controls
    second_row = ttk.Frame(top_frame)
    second_row.pack(fill=tk.X)
    
    ttk.Label(second_row, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
    search_entry = ttk.Entry(second_row, textvariable=search_var, width=40)
    search_entry.pack(side=tk.LEFT)
    
    # Bind datetime entry changes to load_history
    from_datetime_entry.bind("<KeyRelease>", lambda e: load_history())
    to_datetime_entry.bind("<KeyRelease>", lambda e: load_history())

    # Treeview with scrollbars in left panel
    tree_frame = ttk.Frame(left_panel)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(tree_frame, columns=(), show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbars for treeview
    v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=v_scrollbar.set)

    h_scrollbar = ttk.Scrollbar(left_panel, orient=tk.HORIZONTAL, command=tree.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
    tree.configure(xscrollcommand=h_scrollbar.set)

    # Count label
    count_var = tk.StringVar(value="Total: 0 | Selected: 0")
    ttk.Label(left_panel, textvariable=count_var).pack(anchor="w", pady=(5, 0))

    # Details panel widgets
    details_widgets = {}
    
    # Create detail display widgets
    def create_detail_widgets():
        # Timestamp
        ttk.Label(right_panel, text="Timestamp:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        details_widgets['timestamp'] = ttk.Label(right_panel, text="", foreground="#333")
        details_widgets['timestamp'].pack(anchor="w", pady=(0, 10))
        
        # Recipient
        ttk.Label(right_panel, text="Recipient:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        details_widgets['recipient'] = ttk.Label(right_panel, text="", foreground="#333")
        details_widgets['recipient'].pack(anchor="w", pady=(0, 10))
        
        # Subject
        ttk.Label(right_panel, text="Subject:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        details_widgets['subject'] = ttk.Label(right_panel, text="", foreground="#333", wraplength=350)
        details_widgets['subject'].pack(anchor="w", pady=(0, 10))
        
        # Status
        ttk.Label(right_panel, text="Status:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        details_widgets['status'] = ttk.Label(right_panel, text="", foreground="#333")
        details_widgets['status'].pack(anchor="w", pady=(0, 10))
        
        # Type
        ttk.Label(right_panel, text="Type:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        details_widgets['type'] = ttk.Label(right_panel, text="", foreground="#333")
        details_widgets['type'].pack(anchor="w", pady=(0, 10))
        
        # Body/Message
        ttk.Label(right_panel, text="Content:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        
        # Scrollable text widget for content
        content_frame = ttk.Frame(right_panel)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        details_widgets['content'] = tk.Text(content_frame, wrap=tk.WORD, height=15, width=45, 
                                           font=("Segoe UI", 9), relief=tk.SUNKEN, borderwidth=1)
        details_widgets['content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        content_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=details_widgets['content'].yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_widgets['content'].configure(yscrollcommand=content_scrollbar.set)
        details_widgets['content'].configure(state=tk.DISABLED)  # Read-only

    create_detail_widgets()

    # Store full content data for details panel
    full_content_data = {}

    def update_details():
        selection = tree.selection()
        if not selection:
            # Clear details when no selection
            details_widgets['timestamp'].config(text="")
            details_widgets['recipient'].config(text="")
            details_widgets['subject'].config(text="")
            details_widgets['status'].config(text="")
            details_widgets['type'].config(text="")
            details_widgets['content'].configure(state=tk.NORMAL)
            details_widgets['content'].delete(1.0, tk.END)
            details_widgets['content'].configure(state=tk.DISABLED)
            return
        
        # Get selected item data
        item = selection[0]
        values = tree.item(item, 'values')
        
        # Get full content from stored data
        full_content = full_content_data.get(item, "")
        
        if len(values) >= 6:  # Email format
            timestamp, recipient, subject, body_preview, status, type_info = values
            
            # Update detail widgets
            details_widgets['timestamp'].config(text=timestamp)
            details_widgets['recipient'].config(text=recipient)
            details_widgets['subject'].config(text=subject)
            details_widgets['status'].config(text=status)
            details_widgets['type'].config(text=type_info)
            
            # Update content with full content
            details_widgets['content'].configure(state=tk.NORMAL)
            details_widgets['content'].delete(1.0, tk.END)
            details_widgets['content'].insert(1.0, full_content or "No content available")
            details_widgets['content'].configure(state=tk.DISABLED)
            
        elif len(values) >= 4:  # SMS format
            timestamp, recipient, body_preview, status = values
            
            # Update detail widgets
            details_widgets['timestamp'].config(text=timestamp)
            details_widgets['recipient'].config(text=recipient)
            details_widgets['subject'].config(text="N/A (SMS)")
            details_widgets['status'].config(text=status)
            details_widgets['type'].config(text="SMS")
            
            # Update content with full content
            details_widgets['content'].configure(state=tk.NORMAL)
            details_widgets['content'].delete(1.0, tk.END)
            details_widgets['content'].insert(1.0, full_content or "No message content")
            details_widgets['content'].configure(state=tk.DISABLED)

    def update_counts(event=None):
        total = len(tree.get_children())
        selected = len(tree.selection())
        count_var.set(f"Total: {total} | Selected: {selected}")
        update_details()

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
            # Ensure email_history table exists
            c.execute("""CREATE TABLE IF NOT EXISTS email_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                subject TEXT,
                body TEXT,
                email TEXT,
                status TEXT
            )""")
            # Note: email_campaign_history table already exists with schema:
            # id, campaign_id, contact_id, timestamp, status, error
            
            columns = ("Timestamp", "Recipient", "Subject", "Body", "Status", "Type")
            tree.configure(columns=columns)
            for col in columns:
                tree.heading(col, text=col)
                if col == "Timestamp":
                    tree.column(col, width=150)
                elif col == "Recipient":
                    tree.column(col, width=250)  # Wider for email addresses
                elif col == "Subject":
                    tree.column(col, width=300)  # Much wider for subject
                elif col == "Body":
                    tree.column(col, width=200)  # Preview only, details in right panel
                elif col == "Status":
                    tree.column(col, width=80)
                elif col == "Type":
                    tree.column(col, width=80)
            
            query = search_var.get().strip().lower()
            
            # Build datetime filter conditions
            date_conditions = ""
            date_params = []
            if date_filter_enabled.get():
                try:
                    from_datetime_str = from_datetime_var.get()
                    to_datetime_str = to_datetime_var.get()
                    # Validate datetime format
                    from_dt = datetime.strptime(from_datetime_str, "%Y-%m-%d %H:%M")
                    to_dt = datetime.strptime(to_datetime_str, "%Y-%m-%d %H:%M")
                    # Convert to strings for SQL comparison
                    from_timestamp = from_dt.strftime("%Y-%m-%d %H:%M:%S")
                    to_timestamp = to_dt.strftime("%Y-%m-%d %H:%M:%S")
                    date_conditions = " AND timestamp BETWEEN ? AND ?"
                    date_params = [from_timestamp, to_timestamp]
                except ValueError:
                    # Invalid datetime format, ignore date filter
                    date_conditions = ""
                    date_params = []
            
            # Get data from both tables and combine them
            if query:
                # Direct emails with date filter
                direct_query = f"SELECT timestamp, email, subject, body, status FROM email_history WHERE 1=1{date_conditions}"
                c.execute(direct_query, date_params)
                direct_data = c.fetchall()
                direct_rows = []
                for row in direct_data:
                    if any(query in str(field).lower() for field in row):
                        timestamp, email, subject, body, status = row
                        # Truncate body for list view
                        body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                        direct_rows.append((timestamp, email, subject, body_preview, status, "Direct", body))  # Store full body
                
                # Campaign emails with JOIN and date filter
                campaign_query = f"""
                    SELECT h.timestamp, ct.email, c.name, 
                           COALESCE(h.personalized_body, c.body) as body_content, 
                           h.status 
                    FROM email_campaign_history h
                    LEFT JOIN email_campaigns c ON h.campaign_id = c.id
                    LEFT JOIN contacts ct ON h.contact_id = ct.id
                    WHERE 1=1{date_conditions}
                """
                c.execute(campaign_query, date_params)
                campaign_data = c.fetchall()
                campaign_rows = []
                for row in campaign_data:
                    if any(query in str(field).lower() for field in row):
                        timestamp, email, campaign_name, body, status = row
                        # Truncate body for list view
                        body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                        campaign_rows.append((timestamp, email, f"Campaign: {campaign_name}", body_preview, status, "Campaign", body))  # Store full body
                
                rows = direct_rows + campaign_rows
            else:
                # Direct emails with date filter
                direct_query = f"SELECT timestamp, email, subject, body, status FROM email_history WHERE 1=1{date_conditions} ORDER BY timestamp DESC"
                c.execute(direct_query, date_params)
                direct_data = c.fetchall()
                direct_rows = []
                for row in direct_data:
                    timestamp, email, subject, body, status = row
                    # Truncate body for list view
                    body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                    direct_rows.append((timestamp, email, subject, body_preview, status, "Direct", body))  # Store full body
                
                # Campaign emails with JOIN and date filter
                campaign_query = f"""
                    SELECT h.timestamp, ct.email, c.name, 
                           COALESCE(h.personalized_body, c.body) as body_content, 
                           h.status 
                    FROM email_campaign_history h
                    LEFT JOIN email_campaigns c ON h.campaign_id = c.id
                    LEFT JOIN contacts ct ON h.contact_id = ct.id
                    WHERE 1=1{date_conditions}
                    ORDER BY h.timestamp DESC
                """
                c.execute(campaign_query, date_params)
                campaign_data = c.fetchall()
                campaign_rows = []
                for row in campaign_data:
                    timestamp, email, campaign_name, body, status = row
                    # Truncate body for list view
                    body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                    campaign_rows.append((timestamp, email, f"Campaign: {campaign_name}", body_preview, status, "Campaign", body))  # Store full body
                
                # Combine and sort by timestamp (newest first)
                all_rows = direct_rows + campaign_rows
                rows = sorted(all_rows, key=lambda x: x[0], reverse=True)[:500]
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
                if col == "Timestamp":
                    tree.column(col, width=150)
                elif col == "Recipient":
                    tree.column(col, width=250)
                elif col == "Body":
                    tree.column(col, width=400)  # Larger preview for SMS
                elif col == "Status":
                    tree.column(col, width=100)
            query = search_var.get().strip().lower()
            
            # Build datetime filter conditions for SMS
            sms_date_conditions = ""
            sms_date_params = []
            if date_filter_enabled.get():
                try:
                    from_datetime_str = from_datetime_var.get()
                    to_datetime_str = to_datetime_var.get()
                    # Validate datetime format
                    from_dt = datetime.strptime(from_datetime_str, "%Y-%m-%d %H:%M")
                    to_dt = datetime.strptime(to_datetime_str, "%Y-%m-%d %H:%M")
                    # Convert to strings for SQL comparison
                    from_timestamp = from_dt.strftime("%Y-%m-%d %H:%M:%S")
                    to_timestamp = to_dt.strftime("%Y-%m-%d %H:%M:%S")
                    sms_date_conditions = " AND timestamp BETWEEN ? AND ?"
                    sms_date_params = [from_timestamp, to_timestamp]
                except ValueError:
                    # Invalid datetime format, ignore date filter
                    sms_date_conditions = ""
                    sms_date_params = []
            
            if query:
                sms_query = f"SELECT timestamp, recipient, body, status FROM sms_history WHERE 1=1{sms_date_conditions}"
                c.execute(sms_query, sms_date_params)
                sms_data = c.fetchall()
                rows = []
                for row in sms_data:
                    if any(query in str(field).lower() for field in row):
                        timestamp, recipient, body, status = row
                        # Truncate body for list view
                        body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                        rows.append((timestamp, recipient, body_preview, status, body))  # Store full body
            else:
                sms_query = f"SELECT timestamp, recipient, body, status FROM sms_history WHERE 1=1{sms_date_conditions} ORDER BY id DESC LIMIT 500"
                c.execute(sms_query, sms_date_params)
                sms_data = c.fetchall()
                rows = []
                for row in sms_data:
                    timestamp, recipient, body, status = row
                    # Truncate body for list view
                    body_preview = (body[:50] + "...") if body and len(body) > 50 else (body or "")
                    rows.append((timestamp, recipient, body_preview, status, body))  # Store full body
        
        # Clear previous data and insert new rows
        full_content_data.clear()
        for row in rows:
            if len(row) > 6:  # Email with full content
                display_row = row[:6]  # First 6 elements for display
                full_content = row[6]  # Full content
                item = tree.insert("", tk.END, values=display_row)
                full_content_data[item] = full_content
            elif len(row) > 4:  # SMS with full content
                display_row = row[:4]  # First 4 elements for display
                full_content = row[4]  # Full content
                item = tree.insert("", tk.END, values=display_row)
                full_content_data[item] = full_content
            else:
                # Fallback for any other format
                item = tree.insert("", tk.END, values=row)
                full_content_data[item] = ""
        apply_striped_rows(tree)
        conn.close()
        update_counts()

    search_entry.bind("<KeyRelease>", lambda e: load_history())
    load_history()

