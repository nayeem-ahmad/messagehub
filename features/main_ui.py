import tkinter as tk
from tkinter import ttk
from .contacts_ui import show_contacts, show_groups
from .email import show_email_campaigns
from .sms import show_sms_campaigns
from .settings import open_settings_dialog
from .history import show_history_dialog


def setup_main_ui(root):
    """Set up the main application UI."""
    # Global button style for a slightly larger look
    style = ttk.Style(root)
    style.configure("TButton", font=("Segoe UI", 11), padding=6)

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
        ("👥 Contacts", lambda: show_contacts(content)),
        ("🗂️ Groups", lambda: show_groups(content)),
        ("✉️ Email Campaigns", lambda: show_email_campaigns(content)),
        ("📱 SMS Campaign", lambda: show_sms_campaigns(content)),
    ]

    for text, command in sidebar_buttons:
        btn = ttk.Button(sidebar, text=text, command=command, width=24)
        btn.pack(pady=5)

    # Settings button below SMS Campaign
    settings_btn = ttk.Button(sidebar, text="⚙️ Settings", command=lambda: open_settings_dialog(root), width=24)
    settings_btn.pack(pady=5)

    # Background campaigns manager
    from .background_manager import show_background_campaign_manager
    background_btn = ttk.Button(sidebar, text="🖥️ Background Jobs", command=lambda: show_background_campaign_manager(root), width=24)
    background_btn.pack(pady=5)

    # Move History button to the bottom of the sidebar
    sidebar.pack_propagate(False)
    history_btn = ttk.Button(sidebar, text="📜 History", command=show_history_dialog, width=24)
    history_btn.pack(side=tk.BOTTOM, pady=10)

    # Set up the contacts view by default
    show_contacts(content)


