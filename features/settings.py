import tkinter as tk
from tkinter import ttk, simpledialog
from .common import get_settings, save_settings, center_window

def open_settings_dialog(parent):
    settings = get_settings()
    dialog = tk.Toplevel(parent)
    dialog.title("Settings")
    dialog.geometry("900x600")  # Reduced height
    dialog.transient(parent)
    dialog.grab_set()

    # Create notebook for tabs
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Reduced padding

    # Email Settings Tab
    email_tab = ttk.Frame(notebook)
    notebook.add(email_tab, text="✉️ Email Settings")

    # Email Section Header
    email_header = ttk.Label(email_tab, text="Email Configuration", font=("Segoe UI", 14, "bold"))
    email_header.pack(anchor="w", pady=(0, 10))  # Reduced padding

    # Create two columns
    columns_frame = ttk.Frame(email_tab)
    columns_frame.pack(fill="both", expand=True)
    
    # Left column
    left_column = ttk.Frame(columns_frame)
    left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))  # Reduced padding
    
    # Right column
    right_column = ttk.Frame(columns_frame)
    right_column.pack(side="left", fill="both", expand=True, padx=(5, 0))  # Reduced padding

    # Email Method Section (Left Column)
    method_frame = ttk.LabelFrame(left_column, text="Email Sending Method", padding=10)  # Reduced padding
    method_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    email_method_var = tk.StringVar(value=settings.get('email_method', "SMTP"))
    methods = [
        ("SMTP", "Use your own SMTP server (e.g., Gmail, Outlook)"),
        ("SendGrid", "Use SendGrid's email service"),
        ("Amazon SES", "Use Amazon SES for high-volume sending")
    ]

    for i, (method, desc) in enumerate(methods):
        ttk.Radiobutton(
            method_frame, 
            text=method,
            value=method,
            variable=email_method_var,
            command=lambda m=method: update_email_fields(m)
        ).pack(anchor="w", pady=(5 if i > 0 else 0))  # Reduced padding
        ttk.Label(
            method_frame,
            text=desc,
            font=("Segoe UI", 8),  # Reduced font size
            foreground="#666"
        ).pack(anchor="w", padx=20)  # Reduced padding

    # SMTP Settings Section (Left Column)
    smtp_frame = ttk.LabelFrame(left_column, text="SMTP Settings", padding=10)  # Reduced padding
    smtp_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    smtp_fields = [
        ("Sender Email", 'sender_email', "Your email address"),
        ("Sender Password", 'sender_pwd', "Your email password or app password", True),
        ("SMTP Server", 'smtp_server', "e.g., smtp.gmail.com"),
        ("SMTP Port", 'smtp_port', "e.g., 587 for TLS")
    ]

    smtp_vars = {}
    for label, key, tooltip, *args in smtp_fields:
        frame = ttk.Frame(smtp_frame)
        frame.pack(fill="x", pady=2)  # Reduced padding
        ttk.Label(frame, text=label+":", width=12).pack(side="left")  # Reduced width
        if args and args[0]:  # Password field
            var = ttk.Entry(frame, show="*", width=35)  # Reduced width
        else:
            var = ttk.Entry(frame, width=35)  # Reduced width
        var.insert(0, settings.get(key, ''))
        var.pack(side="left", padx=2)  # Reduced padding
        smtp_vars[key] = var
        CreateToolTip(var, tooltip)

    # SendGrid Settings Section (Left Column)
    sendgrid_frame = ttk.LabelFrame(left_column, text="SendGrid Settings", padding=10)  # Reduced padding
    sendgrid_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    sendgrid_vars = {}
    frame = ttk.Frame(sendgrid_frame)
    frame.pack(fill="x", pady=2)  # Reduced padding
    ttk.Label(frame, text="API Key:", width=12).pack(side="left")  # Reduced width
    var = ttk.Entry(frame, width=35)  # Reduced width
    var.insert(0, settings.get('sendgrid_api_key', ''))
    var.pack(side="left", padx=2)  # Reduced padding
    sendgrid_vars['sendgrid_api_key'] = var
    CreateToolTip(var, "Your SendGrid API key")

    # Amazon SES Settings Section (Right Column)
    ses_frame = ttk.LabelFrame(right_column, text="Amazon SES Settings", padding=10)  # Reduced padding
    ses_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    ses_fields = [
        ("Access Key", 'ses_access_key', "Your AWS access key"),
        ("Secret Key", 'ses_secret_key', "Your AWS secret key", True),
        ("Region", 'ses_region', "e.g., us-east-1")
    ]

    ses_vars = {}
    for label, key, tooltip, *args in ses_fields:
        frame = ttk.Frame(ses_frame)
        frame.pack(fill="x", pady=2)  # Reduced padding
        ttk.Label(frame, text=label+":", width=12).pack(side="left")  # Reduced width
        if args and args[0]:  # Password field
            var = ttk.Entry(frame, show="*", width=35)  # Reduced width
        else:
            var = ttk.Entry(frame, width=35)  # Reduced width
        var.insert(0, settings.get(key, ''))
        var.pack(side="left", padx=2)  # Reduced padding
        ses_vars[key] = var
        CreateToolTip(var, tooltip)

    # Default Email Content Section (Right Column)
    content_frame = ttk.LabelFrame(right_column, text="Default Email Content", padding=10)  # Reduced padding
    content_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    # Default Subject
    frame = ttk.Frame(content_frame)
    frame.pack(fill="x", pady=2)  # Reduced padding
    ttk.Label(frame, text="Default Subject:", width=12).pack(side="left")  # Reduced width
    subject_var = ttk.Entry(frame, width=35)  # Reduced width
    subject_var.insert(0, settings.get('default_subject', ''))
    subject_var.pack(side="left", padx=2)  # Reduced padding
    CreateToolTip(subject_var, "Default subject line for new email campaigns")

    # Default Body
    frame = ttk.Frame(content_frame)
    frame.pack(fill="x", pady=2)  # Reduced padding
    ttk.Label(frame, text="Default Body:", width=12).pack(side="left")  # Reduced width
    body_text = tk.Text(frame, width=35, height=6)  # Reduced width and height
    body_text.insert("1.0", settings.get('default_body', ''))
    body_text.pack(side="left", padx=2)  # Reduced padding
    CreateToolTip(body_text, "Default body text for new email campaigns")

    # SMS Settings Tab
    sms_tab = ttk.Frame(notebook)
    notebook.add(sms_tab, text="📱 SMS Settings")

    # SMS Section Header
    sms_header = ttk.Label(sms_tab, text="SMS Configuration", font=("Segoe UI", 14, "bold"))
    sms_header.pack(anchor="w", pady=(0, 10))  # Reduced padding

    # SMS Settings Section
    sms_frame = ttk.LabelFrame(sms_tab, text="SMS Provider Settings", padding=10)  # Reduced padding
    sms_frame.pack(fill="x", pady=(0, 10))  # Reduced padding

    sms_fields = [
        ("API Key", 'sms_api_key', "Your SMS provider's API key"),
        ("Sender ID", 'sms_sender_id', "Your registered sender ID or name")
    ]

    sms_vars = {}
    for label, key, tooltip in sms_fields:
        frame = ttk.Frame(sms_frame)
        frame.pack(fill="x", pady=2)  # Reduced padding
        ttk.Label(frame, text=label+":", width=12).pack(side="left")  # Reduced width
        var = ttk.Entry(frame, width=35)  # Reduced width
        var.insert(0, settings.get(key, ''))
        var.pack(side="left", padx=2)  # Reduced padding
        sms_vars[key] = var
        CreateToolTip(var, tooltip)

    def update_email_fields(method):
        smtp_frame.pack(fill="x", pady=(0, 10)) if method == "SMTP" else smtp_frame.pack_forget()
        sendgrid_frame.pack(fill="x", pady=(0, 10)) if method == "SendGrid" else sendgrid_frame.pack_forget()
        ses_frame.pack(fill="x", pady=(0, 10)) if method == "Amazon SES" else ses_frame.pack_forget()

    # Initialize visible fields
    update_email_fields(email_method_var.get())

    def on_save():
        new_settings = {}
        # Email settings
        new_settings['email_method'] = email_method_var.get()
        
        # SMTP settings
        for key, var in smtp_vars.items():
            new_settings[key] = var.get().strip()
            
        # SendGrid settings
        for key, var in sendgrid_vars.items():
            new_settings[key] = var.get().strip()
            
        # SES settings
        for key, var in ses_vars.items():
            new_settings[key] = var.get().strip()
            
        # Default content
        new_settings['default_subject'] = subject_var.get().strip()
        new_settings['default_body'] = body_text.get("1.0", tk.END).strip()
        
        # SMS settings
        for key, var in sms_vars.items():
            new_settings[key] = var.get().strip()
            
        save_settings(new_settings)
        dialog.destroy()

    # Button Frame
    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))  # Reduced padding
    
    # Style for buttons
    style = ttk.Style()
    style.configure("Save.TButton", font=("Segoe UI", 9, "bold"))  # Reduced font size
    
    ttk.Button(btn_frame, text="Save Changes", command=on_save, style="Save.TButton").pack(side="right", padx=5)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)

    center_window(dialog, 900, 600)  # Reduced height

# Tooltip class
class CreateToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        try:
            # Try to get bbox for widgets that support "insert" (like Text widgets)
            bbox = self.widget.bbox("insert")
            if bbox is not None:
                x, y, _, _ = bbox
            else:
                # Fallback for widgets that don't support "insert"
                x, y = 0, 0
        except (tk.TclError, AttributeError):
            # Fallback for widgets that don't have bbox method or don't support "insert"
            x, y = 0, 0
        
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Segoe UI", "8", "normal"))
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

