import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from functions import scan_usb_for_viruses, list_usb_devices, detect_potential_threats, diagnose_storage, readfile, ClearData, History
from performance import test_sequential_speed, test_random_speed
from usb_profile import detect_hid_threads
import threading
import os

def show_output(title, content):
    win = tk.Toplevel(root)
    win.configure(bg="lightblue")
    win.title(title)
    text = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=100, height=45,font=("Roboto",12))
    text.insert(tk.END, content)
    text.pack(padx=10, pady=10)

def progress_bar(title,label_text,func,output):
    progress_win = tk.Toplevel(root)
    progress_win.configure(bg="lightblue")
    progress_win.title(title)

    label = tk.Label(progress_win, text=label_text,font=("Roboto",12),bg="lightblue")
    label.pack(pady=10)

    progress = ttk.Progressbar(progress_win, mode='indeterminate', length=400)
    progress.pack(pady=10)
    progress.start()
    def test_and_show():
        result = func()
        progress.stop()
        progress_win.destroy()
        show_output(output, result.replace('\n','\n\n'))

    threading.Thread(target=test_and_show).start()

def run_normal_scan():
    info = list_usb_devices().replace('\n','\n\n')
    threats = detect_potential_threats().replace('\n','\n\n')
    show_output("Normal Scan", f"{info}\nPotential Threats:\n{threats}")

def run_virus_scan():
    progress_bar("Virus Scan","Running ClamAV scan. Please wait...",scan_usb_for_viruses,"Virus Scan Results")

def run_storage_diagnosis():
    result = diagnose_storage()
    show_output("Storage Diagnosis", result.replace('\n','\n\n'))

def run_clear_data():
    result = ClearData()
    messagebox.showinfo("Clear Data", result)

def run_history():
    result = History()
    show_output("History", result.replace('\n','\n\n'))

def run_performance_test():
    progress_bar("Testing Performance","Running sequential read/write tests. Please wait...",test_sequential_speed,"Performance Test")

def run_random_test():
    progress_bar("Testing Random I/O","Running random read/write tests. Please wait...",test_random_speed,"Random I/O Test")

def readinfo():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    info_path = os.path.join(base_dir, "info.txt")
    show_output("USB Forensic Analyzer Info", readfile(info_path))

def run_hid_scan():
    threads = detect_hid_threads()
    if not threads:
        messagebox.showinfo("HID Scan", "No HID threads detected.")
        return

    output = "Thread ID    Device Handle    Device Path           Device Name         Thread Status\n"
    output += "-" * 80 + "\n"
    for d in threads:
        output += f"{d['Thread ID']}    {d['Device Handle']}    {d['Device Path']}    {d['Device Name']}    {d['Thread Status']}\n"

    show_output("HID Threads", output)

 
#main window
root = tk.Tk()
root.configure(bg="grey")
root.title("USB Forensic Analyzer GUI")
root.geometry("400x800")
label=tk.Label(root,text="WELCOME",font=("Roboto",20,"bold"),fg="lightgreen",bg="grey")
label.pack(pady=20)
tk.Button(root, text="About Tool",font=("Roboto",12,"bold"),command=readinfo, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Normal Scan",font=("Roboto",12,"bold"),command=run_normal_scan, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Virus Scan",font=("Roboto",12,"bold"),command=run_virus_scan, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Storage Diagnosis",font=("Roboto",12,"bold"),command=run_storage_diagnosis, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Sequential I/O Test", font=("Roboto",12,"bold"),command=run_performance_test, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Random I/O Test",font=("Roboto",12,"bold"), command=run_random_test, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Scan for HID Injection",font=("Roboto",12,"bold"), command=run_hid_scan, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="View History", font=("Roboto",12,"bold"),command=run_history, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Clear Data", font=("Roboto",12,"bold"),command=run_clear_data, width=30,activebackground="lightblue").pack(pady=15)
tk.Button(root, text="Exit", font=("Roboto",12,"bold"),command=root.quit, width=30,activebackground="red").pack(pady=15)

root.mainloop()
