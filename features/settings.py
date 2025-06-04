import tkinter as tk
from .common import get_settings, save_settings, center_window

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
    ttk.Button(btn_frame, text="💾 Save", command=on_save).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    center_window(dialog, 800, 700)

