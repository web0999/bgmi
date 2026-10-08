"""
Buildozer / Kivy / Mobile Entry point for Android App
"""
from android_app import *

if __name__ == "__main__":
    try:
        import customtkinter as ctk
        # Run Android App with GUI & Local Web Dashboard
        t_web = threading.Thread(target=start_mobile_server, args=(5000,))
        t_web.daemon = True
        t_web.start()
        
        gui = AndroidTkApp()
        gui.mainloop()
    except Exception:
        # Fallback for headless Termux / Mobile Web server
        start_mobile_server(5000)
