#!/usr/bin/env python3
"""
Verify that the history functionality is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.history import show_history_dialog
import tkinter as tk

def test_history_dialog():
    print("🧪 Testing History Dialog")
    print("=" * 30)
    
    # Create a minimal tkinter root for testing
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # This should open the history dialog
        print("📋 Opening history dialog...")
        show_history_dialog()
        print("✅ History dialog opened successfully!")
        
        # Keep the window open for a few seconds to see if it loads data
        root.after(3000, root.quit)  # Close after 3 seconds
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error opening history dialog: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_history_dialog()
