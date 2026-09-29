import ctypes
import os

def set_title_bar_theme(window, dark=True):
    if os.name != "nt": return
    try:
        window.update_idletasks(); hwnd=ctypes.windll.user32.GetParent(window.winfo_id()); value=ctypes.c_int(1 if dark else 0)
        for attr in (20,19):
            try:
                if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd,attr,ctypes.byref(value),ctypes.sizeof(value))==0: break
            except Exception: pass
    except Exception: pass

def enable_dark_title_bar(window):
    set_title_bar_theme(window, True)
