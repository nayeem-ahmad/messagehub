#!/usr/bin/env python3
"""
Simple test for the improved datetime input layout
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from features.history import show_history_dialog

def main():
    """Test the improved datetime input layout"""
    print("Testing Improved DateTime Input Layout...")
    print("=" * 50)
    print("Opening history dialog with improved layout:")
    print("- Bigger datetime input boxes (width=20, larger font)")
    print("- Calendar icons (📅) positioned on the right of each input field")
    print("- Better visual alignment and spacing")
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    def show_dialog():
        show_history_dialog()
        root.quit()
    
    root.after(100, show_dialog)
    root.mainloop()
    
    print("\nThe dialog should show:")
    print("- DateTime Filter checkbox")
    print("- From: [larger input box] [📅]")
    print("- To:   [larger input box] [📅]")
    print("- Quick filter buttons")
    print("- Calendar icons should be immediately to the right of input boxes")

if __name__ == "__main__":
    main()
