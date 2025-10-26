import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from functions import scan_usb_for_viruses, list_usb_devices, detect_potential_threats, diagnose_storage, readfile, ClearData, History
from performance import test_sequential_speed, test_random_speed
import threading
import os

def show_output(title, content):
    win = tk.Toplevel(root)
    win.title(title)
    text = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=80, height=30)
    text.insert(tk.END, content)
    text.pack(padx=10, pady=10)

def progress_bar(title,label_text,func,output):
    progress_win = tk.Toplevel(root)
    progress_win.title(title)

    label = tk.Label(progress_win, text=label_text)
    label.pack(pady=10)

    progress = ttk.Progressbar(progress_win, mode='indeterminate', length=300)
    progress.pack(pady=10)
    progress.start()
    def test_and_show():
        result = func()
        progress.stop()
        progress_win.destroy()
        show_output(output, result)

    threading.Thread(target=test_and_show).start()

def run_normal_scan():
    info = list_usb_devices()
    threats = detect_potential_threats()
    show_output("Normal Scan", f"{info}\n\nPotential Threats:\n{threats}")

def run_virus_scan():
    progress_bar("Virus Scan","Running ClamAV scan. Please wait...",scan_usb_for_viruses,"Virus Scan Results")

def run_storage_diagnosis():
    result = diagnose_storage()
    show_output("Storage Diagnosis", result)

def run_clear_data():
    result = ClearData()
    messagebox.showinfo("Clear Data", result)

def run_history():
    result = History()
    show_output("History", result)

def run_performance_test():
    progress_bar("Testing Performance","Running sequential read/write tests. Please wait...",test_sequential_speed,"Performance Test")

def run_random_test():
    progress_bar("Testing Random I/O","Running random read/write tests. Please wait...",test_random_speed,"Random I/O Test")


def readinfo():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    info_path = os.path.join(base_dir, "info.txt")
    show_output("USB Forensic Analyzer Info", readfile(info_path))
    
#main window

root = tk.Tk()
root.title("USB Forensic Analyzer GUI")
root.geometry("300x450")
label=tk.Label(root,text="WELCOME",font=("Arial",14))
label.pack(pady=10)
tk.Button(root, text="About Tool", command=readinfo, width=30).pack(pady=5)
tk.Button(root, text="Normal Scan", command=run_normal_scan, width=30).pack(pady=5)
tk.Button(root, text="Virus Scan", command=run_virus_scan, width=30).pack(pady=5)
tk.Button(root, text="Storage Diagnosis", command=run_storage_diagnosis, width=30).pack(pady=5)
tk.Button(root, text="Sequential I/O Test", command=run_performance_test, width=30).pack(pady=5)
tk.Button(root, text="Random I/O Test", command=run_random_test, width=30).pack(pady=5)
tk.Button(root, text="View History", command=run_history, width=30).pack(pady=5)
tk.Button(root, text="Clear Data", command=run_clear_data, width=30).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit, width=30).pack(pady=5)

root.mainloop()
