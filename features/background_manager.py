"""
Background Campaign Management UI
Shows all running background campaigns and provides management options
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from services.background_jobs import get_job_manager
from features.common import center_window, apply_striped_rows

class BackgroundCampaignManager:
    def __init__(self, parent):
        self.parent = parent
        self.job_manager = get_job_manager()
        self.dialog = None
        self.tree = None
        self.monitoring = False
        
    def show(self):
        """Show the background campaign manager"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Background Campaign Manager")
        self.dialog.geometry("800x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        center_window(self.dialog, 800, 500)
        
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Background Campaign Manager", font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="🔄 Refresh", command=self._refresh_campaigns).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="⏹️ Stop Selected", command=self._stop_selected).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(toolbar, text="📊 Monitor Selected", command=self._monitor_selected).pack(side=tk.LEFT, padx=(10, 0))
        
        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            toolbar, 
            text="Auto-refresh (5s)", 
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh
        ).pack(side=tk.RIGHT)
        
        # Campaign list
        columns = ("Campaign ID", "Type", "Name", "Status", "PID", "Started", "Last Update", "Details")
        
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.heading("Campaign ID", text="ID")
        self.tree.column("Campaign ID", width=50)
        
        self.tree.heading("Type", text="Type")
        self.tree.column("Type", width=60)
        
        self.tree.heading("Name", text="Campaign Name")
        self.tree.column("Name", width=150)
        
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=80)
        
        self.tree.heading("PID", text="PID")
        self.tree.column("PID", width=60)
        
        self.tree.heading("Started", text="Started")
        self.tree.column("Started", width=120)
        
        self.tree.heading("Last Update", text="Last Update")
        self.tree.column("Last Update", width=120)
        
        self.tree.heading("Details", text="Details")
        self.tree.column("Details", width=200)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(fill=tk.X, pady=(0, 10))
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Loading...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=self._close).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cleanup Old Jobs", command=self._cleanup_jobs).pack(side=tk.LEFT)
        
        # Load initial data
        self._refresh_campaigns()
        
        # Start auto-refresh if enabled
        self.monitoring = True
        self._auto_refresh_loop()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close)
    
    def _refresh_campaigns(self):
        """Refresh the campaign list"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get running campaigns
            running_campaigns = self.job_manager.get_running_campaigns()
            
            if not running_campaigns:
                self.status_var.set("No running background campaigns")
                return
            
            # Add campaigns to tree
            for campaign_info in running_campaigns:
                campaign_id = campaign_info['campaign_id']
                campaign_type = campaign_info['campaign_type']
                
                # Get detailed status
                status = self.job_manager.get_campaign_status(campaign_id, campaign_type)
                
                # Get campaign name from database
                campaign_name = self._get_campaign_name(campaign_id, campaign_type)
                
                # Format dates
                started_at = campaign_info.get('started_at', '')
                if started_at:
                    try:
                        dt = datetime.fromisoformat(started_at)
                        started_at = dt.strftime("%H:%M:%S")
                    except:
                        pass
                
                last_updated = status.get('last_updated', '')
                if last_updated:
                    try:
                        dt = datetime.fromisoformat(last_updated)
                        last_updated = dt.strftime("%H:%M:%S")
                    except:
                        pass
                
                # Truncate details for display
                details = status.get('processing_details', '')
                if len(details) > 50:
                    details = details[:47] + "..."
                
                # Add to tree
                values = (
                    campaign_id,
                    campaign_type.title(),
                    campaign_name,
                    "🟢 Running" if status.get('is_running') else "⏹️ Stopped",
                    campaign_info.get('pid', ''),
                    started_at,
                    last_updated,
                    details
                )
                
                self.tree.insert("", tk.END, values=values)
            
            apply_striped_rows(self.tree)
            self.status_var.set(f"Found {len(running_campaigns)} running campaigns")
            
        except Exception as e:
            self.status_var.set(f"Error loading campaigns: {e}")
    
    def _get_campaign_name(self, campaign_id, campaign_type):
        """Get campaign name from database"""
        try:
            import sqlite3
            from features.common import DB_FILE
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            table_name = f"{campaign_type}_campaigns"
            cursor.execute(f"SELECT name FROM {table_name} WHERE id = ?", (campaign_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else f"Campaign {campaign_id}"
            
        except Exception:
            return f"Campaign {campaign_id}"
    
    def _stop_selected(self):
        """Stop the selected campaign"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a campaign to stop.")
            return
        
        if len(selected) > 1:
            messagebox.showinfo("Multiple Selection", "Please select only one campaign to stop.")
            return
        
        item = selected[0]
        values = self.tree.item(item, "values")
        campaign_id = int(values[0])
        campaign_type = values[1].lower()
        campaign_name = values[2]
        
        if messagebox.askyesno(
            "Stop Campaign",
            f"Are you sure you want to stop campaign '{campaign_name}'?",
            parent=self.dialog
        ):
            success = self.job_manager.stop_campaign(campaign_id, campaign_type)
            if success:
                messagebox.showinfo("Stopped", f"Campaign '{campaign_name}' has been stopped.", parent=self.dialog)
                self._refresh_campaigns()
            else:
                messagebox.showerror("Error", f"Failed to stop campaign '{campaign_name}'.", parent=self.dialog)
    
    def _monitor_selected(self):
        """Monitor the selected campaign"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a campaign to monitor.")
            return
        
        if len(selected) > 1:
            messagebox.showinfo("Multiple Selection", "Please select only one campaign to monitor.")
            return
        
        item = selected[0]
        values = self.tree.item(item, "values")
        campaign_id = int(values[0])
        campaign_type = values[1].lower()
        campaign_name = values[2]
        
        # Open monitor in new window
        from .campaign_launcher import monitor_campaign
        monitor_campaign(self.dialog, campaign_id, campaign_type, campaign_name)
    
    def _cleanup_jobs(self):
        """Clean up old completed jobs"""
        if messagebox.askyesno(
            "Cleanup Old Jobs",
            "This will remove completed job records older than 7 days.\nContinue?",
            parent=self.dialog
        ):
            try:
                self.job_manager.cleanup_completed_jobs(7)
                messagebox.showinfo("Cleanup Complete", "Old job records have been cleaned up.", parent=self.dialog)
                self._refresh_campaigns()
            except Exception as e:
                messagebox.showerror("Cleanup Error", f"Failed to cleanup jobs: {e}", parent=self.dialog)
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        if not self.auto_refresh_var.get():
            self.status_var.set(self.status_var.get() + " (Auto-refresh disabled)")
    
    def _auto_refresh_loop(self):
        """Auto-refresh loop"""
        if self.monitoring and self.auto_refresh_var.get():
            self._refresh_campaigns()
        
        if self.monitoring:
            self.dialog.after(5000, self._auto_refresh_loop)  # Refresh every 5 seconds
    
    def _close(self):
        """Close the dialog"""
        self.monitoring = False
        self.dialog.destroy()

def show_background_campaign_manager(parent):
    """Show the background campaign manager"""
    manager = BackgroundCampaignManager(parent)
    manager.show()
