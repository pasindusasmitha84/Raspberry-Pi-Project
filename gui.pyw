import tkinter as tk
from tkinter import messagebox, scrolledtext
from functions import scan_usb_for_viruses, list_usb_devices, hash_files, diagnose_storage
from data import ClearData
from history import History

# 🆕 Newly added
import threading
from tkinter import ttk

def show_output(title, content):
    win = tk.Toplevel(root)
    win.title(title)
    text = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=80, height=30)
    text.insert(tk.END, content)
    text.pack(padx=10, pady=10)

def run_normal_scan():
    info = list_usb_devices()
    hashes = hash_files()
    show_output("Normal Scan", f"{info}\n\n{hashes}")

# 🆕 Newly added: virus scan with progress bar
def run_virus_scan():
    progress_win = tk.Toplevel(root)
    progress_win.title("Scanning...")

    label = tk.Label(progress_win, text="Running ClamAV scan. Please wait...")
    label.pack(pady=10)

    progress = ttk.Progressbar(progress_win, mode='indeterminate', length=300)
    progress.pack(pady=10)
    progress.start()

    def scan_and_show():
        result = scan_usb_for_viruses()
        progress.stop()
        progress_win.destroy()
        show_output("Virus Scan Results", result)

    threading.Thread(target=scan_and_show).start()

def run_storage_diagnosis():
    result = diagnose_storage()
    show_output("Storage Diagnosis", result)

def run_clear_data():
    result = ClearData()
    messagebox.showinfo("Clear Data", result)

def run_history():
    result = History()
    show_output("History", result)

root = tk.Tk()
root.title("USB Forensic Analyzer GUI")

tk.Button(root, text="Normal Scan", command=run_normal_scan, width=30).pack(pady=5)
tk.Button(root, text="Virus Scan", command=run_virus_scan, width=30).pack(pady=5)
tk.Button(root, text="Storage Diagnosis", command=run_storage_diagnosis, width=30).pack(pady=5)
tk.Button(root, text="Clear Data", command=run_clear_data, width=30).pack(pady=5)
tk.Button(root, text="View History", command=run_history, width=30).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit, width=30).pack(pady=5)

root.mainloop()
