import tkinter as tk
from tkinter import font as tkfont
import keyboard
import threading
import json
import os
import pystray
from PIL import Image, ImageDraw

CONFIG_FILE = "config.json"
keybind = "f8"
overlay_on = False
hotkey_ref = None
tray_icon = None

def load():
    global keybind
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                keybind = json.load(f).get("keybind", "f8")
        except:
            pass

def save():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"keybind": keybind}, f)

def make_tray_image():
    img = Image.new("RGB", (64, 64), color="#111111")
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, 56, 56], fill="#333333", outline="#888888", width=2)
    return img

root = tk.Tk()
root.title("Blackout")
root.resizable(False, False)
root.attributes("-topmost", True)
root.configure(bg="#f0f0f0")

def on_close():
    root.withdraw()

root.protocol("WM_DELETE_WINDOW", on_close)

overlay = tk.Toplevel(root)
overlay.withdraw()
overlay.attributes("-fullscreen", True)
overlay.configure(bg="black")
overlay.attributes("-topmost", True)
overlay.bind("<Escape>", lambda e: toggle())

def toggle():
    global overlay_on
    if not root.winfo_exists():
        return
    overlay_on = not overlay_on
    if overlay_on:
        overlay.deiconify()
        blackout_label.config(text="Restore", fg="#2a7a2a")
        blackout_frame.config(bg="#dff0d8")
        blackout_label.config(bg="#dff0d8")
        blackout_icon_lbl.config(bg="#dff0d8")
    else:
        overlay.withdraw()
        blackout_label.config(text="Blackout", fg="#222222")
        blackout_frame.config(bg="#f0f0f0")
        blackout_label.config(bg="#f0f0f0")
        blackout_icon_lbl.config(bg="#f0f0f0")

def apply_keybind(k):
    global keybind, hotkey_ref
    try:
        if hotkey_ref:
            keyboard.remove_hotkey(hotkey_ref)
    except:
        pass
    keybind = k
    hotkey_ref = keyboard.add_hotkey(keybind, toggle)
    save()
    status_label.config(text=f"Hotkey: {keybind.upper()}")

def tray_show(icon, item):
    root.after(0, root.deiconify)

def tray_toggle(icon, item):
    root.after(0, toggle)

def tray_quit(icon, item):
    icon.stop()
    root.after(0, root.destroy)

def start_tray():
    global tray_icon
    image = make_tray_image()
    menu = pystray.Menu(
        pystray.MenuItem("Open Blackout", tray_show, default=True),
        pystray.MenuItem("Toggle Blackout", tray_toggle),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", tray_quit)
    )
    tray_icon = pystray.Icon("Blackout", image, "Blackout", menu)
    tray_icon.run()

def open_settings():
    win = tk.Toplevel(root)
    win.title("Preferences")
    win.geometry("220x110")
    win.configure(bg="#f5f5f5")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    tk.Label(win, text="Change hotkey:", bg="#f5f5f5",
             fg="#444", font=("Segoe UI", 9)).pack(pady=(12, 2))
    entry = tk.Entry(win, justify="center", font=("Courier New", 11),
                     bg="white", fg="#222", relief="solid", bd=1)
    entry.insert(0, keybind.upper())
    entry.pack(pady=4, padx=20, fill="x")
    def do_save():
        val = entry.get().lower().strip()
        if val:
            apply_keybind(val)
        win.destroy()
    tk.Button(win, text="Save", command=do_save,
              bg="#4a90d9", fg="white", relief="flat",
              font=("Segoe UI", 9), padx=16, pady=3,
              activebackground="#3070c0", activeforeground="white",
              cursor="hand2").pack(pady=6)

def open_about():
    win = tk.Toplevel(root)
    win.title("About Blackout")
    win.geometry("240x130")
    win.configure(bg="#f5f5f5")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    tk.Label(win, text="Blackout", bg="#f5f5f5",
             fg="#1a1a1a", font=("Segoe UI", 13, "bold")).pack(pady=(16, 2))
    tk.Label(win, text="Instant fullscreen blackout utility",
             bg="#f5f5f5", fg="#555", font=("Segoe UI", 9)).pack()
    tk.Label(win, text="Press your hotkey or click Blackout\nPress hotkey or Esc to restore",
             bg="#f5f5f5", fg="#777", font=("Segoe UI", 8), justify="center").pack(pady=8)

def on_enter(frame, widgets):
    frame.config(bg="#dde8f5")
    for w in widgets: w.config(bg="#dde8f5")

def on_leave(frame, widgets):
    frame.config(bg="#f0f0f0")
    for w in widgets: w.config(bg="#f0f0f0")

def on_press(frame, widgets):
    frame.config(bg="#c5d8ee")
    for w in widgets: w.config(bg="#c5d8ee")

toolbar = tk.Frame(root, bg="#f0f0f0", bd=0)
toolbar.pack(side="top", fill="x", padx=6, pady=6)

def make_tool(parent, icon_text, label_text, command):
    frame = tk.Frame(parent, bg="#f0f0f0", cursor="hand2", padx=6, pady=4)
    frame.pack(side="left")
    icon = tk.Label(frame, text=icon_text, bg="#f0f0f0",
                    font=("Segoe UI Symbol", 22), fg="#333333")
    icon.pack()
    lbl = tk.Label(frame, text=label_text, bg="#f0f0f0",
                   font=("Segoe UI", 8), fg="#222222")
    lbl.pack()
    widgets = [icon, lbl]
    frame.bind("<Enter>",    lambda e, f=frame, w=widgets: on_enter(f, w))
    frame.bind("<Leave>",    lambda e, f=frame, w=widgets: on_leave(f, w))
    frame.bind("<Button-1>", lambda e, f=frame, w=widgets: (on_press(f, w), command()))
    icon.bind("<Enter>",     lambda e, f=frame, w=widgets: on_enter(f, w))
    icon.bind("<Leave>",     lambda e, f=frame, w=widgets: on_leave(f, w))
    icon.bind("<Button-1>",  lambda e, f=frame, w=widgets: (on_press(f, w), command()))
    lbl.bind("<Enter>",      lambda e, f=frame, w=widgets: on_enter(f, w))
    lbl.bind("<Leave>",      lambda e, f=frame, w=widgets: on_leave(f, w))
    lbl.bind("<Button-1>",   lambda e, f=frame, w=widgets: (on_press(f, w), command()))
    return frame, icon, lbl

blackout_frame, blackout_icon_lbl, blackout_label = make_tool(toolbar, "🌑", "Blackout", toggle)
tk.Frame(toolbar, bg="#cccccc", width=1).pack(side="left", fill="y", padx=4, pady=4)
make_tool(toolbar, "⚙", "Prefs", open_settings)
tk.Frame(toolbar, bg="#cccccc", width=1).pack(side="left", fill="y", padx=4, pady=4)
make_tool(toolbar, "ℹ", "About", open_about)

tk.Frame(root, bg="#cccccc", height=1).pack(fill="x")

status_label = tk.Label(
    root, text=f"Hotkey: {keybind.upper()}",
    bg="#f5f5f5", fg="#555555",
    font=("Segoe UI", 8), anchor="w", padx=6, pady=3
)
status_label.pack(fill="x")

def hotkeys():
    global hotkey_ref
    try:
        hotkey_ref = keyboard.add_hotkey(keybind, toggle)
        keyboard.wait()
    except:
        pass

threading.Thread(target=hotkeys, daemon=True).start()
threading.Thread(target=start_tray, daemon=True).start()

load()
status_label.config(text=f"Hotkey: {keybind.upper()}")
root.mainloop()
