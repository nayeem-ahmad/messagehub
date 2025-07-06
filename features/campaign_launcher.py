"""
Campaign Launcher UI - Hybrid Background/Foreground Processing
Provides options for running campaigns in background or foreground mode
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from services.background_jobs import get_job_manager
from features.common import center_window

class CampaignLauncher:
    def __init__(self, parent, campaign_id, campaign_type, campaign_name):
        self.parent = parent
        self.campaign_id = campaign_id
        self.campaign_type = campaign_type
        self.campaign_name = campaign_name
        self.job_manager = get_job_manager()
        
        self.dialog = None
        self.progress_var = None
        self.status_var = None
        self.running = False
        
    def show_launch_dialog(self):
        """Show the campaign launch options dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Launch {self.campaign_type.title()} Campaign")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        center_window(self.dialog, 500, 400)
        
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campaign info
        info_frame = ttk.LabelFrame(main_frame, text="Campaign Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text="Campaign:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.campaign_name).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(info_frame, text="Type:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.campaign_type.title()).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Check current status
        current_status = self.job_manager.get_campaign_status(self.campaign_id, self.campaign_type)
        is_running = current_status.get('is_running', False)
        
        if is_running:
            ttk.Label(info_frame, text="Status:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(info_frame, text="Currently Running in Background", foreground="green").grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Launch Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Option selection
        self.launch_mode = tk.StringVar(value="background" if not is_running else "monitor")
        
        if not is_running:
            ttk.Radiobutton(
                options_frame, 
                text="🚀 Run in Background", 
                variable=self.launch_mode, 
                value="background"
            ).pack(anchor=tk.W, pady=5)
            
            ttk.Label(
                options_frame, 
                text="  • Campaign runs independently\n  • You can close the app\n  • Logs are saved to files\n  • Check status anytime",
                foreground="gray"
            ).pack(anchor=tk.W, padx=20)
            
            ttk.Radiobutton(
                options_frame, 
                text="👀 Run in Foreground", 
                variable=self.launch_mode, 
                value="foreground"
            ).pack(anchor=tk.W, pady=(15, 5))
            
            ttk.Label(
                options_frame, 
                text="  • Real-time progress display\n  • Keep app open during processing\n  • Interactive monitoring\n  • Immediate feedback",
                foreground="gray"
            ).pack(anchor=tk.W, padx=20)
        else:
            ttk.Label(
                options_frame,
                text="Campaign is currently running in background.",
                font=("Segoe UI", 10, "bold")
            ).pack(anchor=tk.W, pady=5)
            
            ttk.Radiobutton(
                options_frame, 
                text="📊 Monitor Progress", 
                variable=self.launch_mode, 
                value="monitor"
            ).pack(anchor=tk.W, pady=5)
            
            ttk.Radiobutton(
                options_frame, 
                text="⏹️ Stop Campaign", 
                variable=self.launch_mode, 
                value="stop"
            ).pack(anchor=tk.W, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        if not is_running:
            ttk.Button(
                button_frame, 
                text="Launch Campaign", 
                command=self._launch_campaign
            ).pack(side=tk.RIGHT)
        else:
            ttk.Button(
                button_frame, 
                text="Execute", 
                command=self._execute_action
            ).pack(side=tk.RIGHT)
    
    def _launch_campaign(self):
        """Launch the campaign based on selected mode"""
        mode = self.launch_mode.get()
        
        if mode == "background":
            self._launch_background()
        elif mode == "foreground":
            self._launch_foreground()
    
    def _execute_action(self):
        """Execute action for running campaign"""
        action = self.launch_mode.get()
        
        if action == "monitor":
            self._show_monitor()
        elif action == "stop":
            self._stop_campaign()
    
    def _launch_background(self):
        """Launch campaign in background mode"""
        success = self.job_manager.start_campaign_background(self.campaign_id, self.campaign_type)
        
        if success:
            messagebox.showinfo(
                "Campaign Started",
                f"Campaign '{self.campaign_name}' has been started in background.\n\n"
                f"You can:\n"
                f"• Close the application safely\n"
                f"• Monitor progress from the Campaign menu\n"
                f"• Check logs in the logs/ directory",
                parent=self.dialog
            )
            self.dialog.destroy()
        else:
            messagebox.showerror(
                "Launch Failed",
                f"Failed to start campaign in background.\n"
                f"The campaign may already be running or there was a system error.",
                parent=self.dialog
            )
    
    def _launch_foreground(self):
        """Launch campaign in foreground mode with real-time monitoring"""
        self.dialog.destroy()
        
        # Import the original foreground campaign functions
        if self.campaign_type == 'email':
            from features.email import send_email_campaign
            # This would need to be integrated with the existing foreground UI
            messagebox.showinfo(
                "Foreground Mode",
                "Foreground mode will use the existing campaign wizard interface.\n"
                "Please use the standard 'Send Campaign' option from the campaign list."
            )
        else:
            messagebox.showinfo(
                "Not Implemented",
                "Foreground SMS campaigns are not yet implemented.\n"
                "Please use background mode for now."
            )
    
    def _show_monitor(self):
        """Show monitoring dialog for running campaign"""
        self.dialog.destroy()
        monitor = CampaignMonitor(self.parent, self.campaign_id, self.campaign_type, self.campaign_name)
        monitor.show()
    
    def _stop_campaign(self):
        """Stop the running background campaign"""
        if messagebox.askyesno(
            "Stop Campaign",
            f"Are you sure you want to stop the running campaign '{self.campaign_name}'?\n\n"
            f"This will interrupt the current processing.",
            parent=self.dialog
        ):
            success = self.job_manager.stop_campaign(self.campaign_id, self.campaign_type)
            
            if success:
                messagebox.showinfo(
                    "Campaign Stopped",
                    f"Campaign '{self.campaign_name}' has been stopped.",
                    parent=self.dialog
                )
                self.dialog.destroy()
            else:
                messagebox.showerror(
                    "Stop Failed",
                    f"Failed to stop the campaign. It may have already completed.",
                    parent=self.dialog
                )

class CampaignMonitor:
    def __init__(self, parent, campaign_id, campaign_type, campaign_name):
        self.parent = parent
        self.campaign_id = campaign_id
        self.campaign_type = campaign_type
        self.campaign_name = campaign_name
        self.job_manager = get_job_manager()
        
        self.dialog = None
        self.monitoring = False
        
    def show(self):
        """Show the campaign monitoring dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Monitor {self.campaign_type.title()} Campaign")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        center_window(self.dialog, 600, 500)
        
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campaign info
        info_frame = ttk.LabelFrame(main_frame, text="Campaign Information", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text="Campaign:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(info_frame, text=self.campaign_name).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Status variables
        self.status_var = tk.StringVar(value="Loading...")
        self.details_var = tk.StringVar(value="")
        self.updated_var = tk.StringVar(value="")
        
        ttk.Label(status_frame, text="Status:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Last Updated:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(status_frame, textvariable=self.updated_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(status_frame, text="Details:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.NW, pady=2)
        self.details_text = tk.Text(status_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 9))
        self.details_text.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=2)
        
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_rowconfigure(2, weight=1)
        
        # Scrollbar for details
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        scrollbar.grid(row=2, column=2, sticky="ns", pady=2)
        self.details_text.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.refresh_button = ttk.Button(button_frame, text="Refresh", command=self._refresh_status)
        self.refresh_button.pack(side=tk.LEFT)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Campaign", command=self._stop_campaign)
        self.stop_button.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(button_frame, text="Close", command=self._close_monitor).pack(side=tk.RIGHT)
        
        # Start monitoring
        self.monitoring = True
        self._start_monitoring()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_monitor)
    
    def _start_monitoring(self):
        """Start the monitoring loop"""
        self._refresh_status()
        if self.monitoring:
            self.dialog.after(3000, self._start_monitoring)  # Refresh every 3 seconds
    
    def _refresh_status(self):
        """Refresh the campaign status"""
        try:
            status = self.job_manager.get_campaign_status(self.campaign_id, self.campaign_type)
            
            # Update status display
            campaign_status = status.get('campaign_status', 'unknown')
            is_running = status.get('is_running', False)
            
            if is_running:
                self.status_var.set(f"🟢 Running ({campaign_status})")
                self.status_label.configure(foreground="green")
            elif campaign_status == 'completed':
                self.status_var.set("✅ Completed")
                self.status_label.configure(foreground="blue")
            elif campaign_status == 'failed':
                self.status_var.set("❌ Failed")
                self.status_label.configure(foreground="red")
            elif campaign_status == 'stopped':
                self.status_var.set("⏹️ Stopped")
                self.status_label.configure(foreground="orange")
            else:
                self.status_var.set(f"⚪ {campaign_status}")
                self.status_label.configure(foreground="gray")
            
            # Update last updated
            last_updated = status.get('last_updated')
            if last_updated:
                try:
                    dt = datetime.fromisoformat(last_updated)
                    self.updated_var.set(dt.strftime("%Y-%m-%d %H:%M:%S"))
                except:
                    self.updated_var.set(last_updated)
            else:
                self.updated_var.set("Never")
            
            # Update details
            details = status.get('processing_details', '')
            if details:
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, details)
                # Auto-scroll to bottom
                self.details_text.see(tk.END)
            
            # Enable/disable stop button
            self.stop_button.configure(state=tk.NORMAL if is_running else tk.DISABLED)
            
        except Exception as e:
            self.status_var.set(f"❌ Error: {e}")
            self.status_label.configure(foreground="red")
    
    def _stop_campaign(self):
        """Stop the campaign"""
        if messagebox.askyesno(
            "Stop Campaign",
            f"Are you sure you want to stop campaign '{self.campaign_name}'?",
            parent=self.dialog
        ):
            success = self.job_manager.stop_campaign(self.campaign_id, self.campaign_type)
            if success:
                messagebox.showinfo("Stopped", "Campaign has been stopped.", parent=self.dialog)
                self._refresh_status()
            else:
                messagebox.showerror("Error", "Failed to stop campaign.", parent=self.dialog)
    
    def _close_monitor(self):
        """Close the monitoring dialog"""
        self.monitoring = False
        self.dialog.destroy()

def launch_campaign(parent, campaign_id, campaign_type, campaign_name):
    """Main entry point for launching campaigns"""
    launcher = CampaignLauncher(parent, campaign_id, campaign_type, campaign_name)
    launcher.show_launch_dialog()

def monitor_campaign(parent, campaign_id, campaign_type, campaign_name):
    """Main entry point for monitoring campaigns"""
    monitor = CampaignMonitor(parent, campaign_id, campaign_type, campaign_name)
    monitor.show()
