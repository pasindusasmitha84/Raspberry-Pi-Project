import subprocess
import datetime
import os
import psutil

def log_event(message):
    with open("usb_log.txt", "a") as log:
        timestamp = datetime.datetime.now().isoformat()
        log.write(f"{timestamp}: {message}\n")

def system_safe():
    temp = get_temp()
    ram = psutil.virtual_memory().percent
    if temp > 60 or ram > 85:
        log_event("Scan aborted due to unsafe system state.")
        return False, f"Unsafe system state: Temp={temp} C, RAM={ram}%"
    return True, ""

def get_temp():
    try:
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return float(output.replace("temp=", "").replace("'C\n", ""))
    except:
        return 0.0

def get_usb_mount_path():
    media_root = "/media/pasindu"
    if not os.path.exists(media_root):
        return None
    for item in os.listdir(media_root):
        path = os.path.join(media_root, item)
        if os.path.ismount(path):
            return path
    return None

def mount_read_only():
    mount_point = get_usb_mount_path()
    if not mount_point:
        log_event("No USB mount point found.")
        return "No external device detected."
    try:
        subprocess.run(["sudo", "mount", "-o", "remount,ro", mount_point], check=True)
        log_event(f"Remounted USB read-only at {mount_point}")
        return f"Mounted read-only at {mount_point}"
    except Exception as e:
        log_event(f"Mount failed: {e}")
        return f"Mount error: {e}"

def readfile(filename):
    try:
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        log_event(f"Read error on {filename}: {e}")
        return f"Failed to read: {e}"

def clear(filename):
    try:
        with open(filename, 'w') as file:
            file.truncate(0)
        log_event(f"Cleared content of {filename}")
        return 'Successfully cleared content.'
    except Exception as e:
        log_event(f"Clear error on {filename}: {e}")
        return f'Failed to clear: {e}'

def scan_usb_for_viruses():
    usb_path = get_usb_mount_path()
    if not usb_path:
        log_event("No mounted USB or microSD found.")
        return "No external device detected."

    safe, msg = system_safe()
    if not safe:
        return msg

    try:
        log_event(f"Starting virus scan on {usb_path}.")
        result = subprocess.run(["timeout", "300", "clamscan", "-r", usb_path], capture_output=True, text=True)
        log_event("Virus scan completed.")
        return result.stdout
    except Exception as e:
        log_event(f"Virus scan failed: {e}")
        return f"Scan error: {e}"

def list_usb_devices():
    try:
        output = subprocess.check_output(["lsusb"]).decode()
        timestamp = datetime.datetime.now().isoformat()
        with open("usb_metadata.txt", "a") as meta:
            info = f"{timestamp}:\n{output}\n"
            meta.write(info)
        log_event("USB metadata captured.")
        return info
    except Exception as e:
        log_event(f"Error capturing USB metadata: {e}")
        return 'Error capturing metadata.'

def hash_files():
    usb_path = get_usb_mount_path()
    if not usb_path or not os.path.exists(usb_path):
        log_event("USB mount point not found.")
        return "USB mount point not found."

    safe, msg = system_safe()
    if not safe:
        return msg

    target_extensions = ('.exe', '.dll', '.sh', '.py', '.bat', '.bin')  # ← Customize this list
    results = []

    for root, dirs, files in os.walk(usb_path):
        for file in files:
            if file.lower().endswith(target_extensions):
                path = os.path.join(root, file)
                try:
                    hash_output = subprocess.check_output(["sha256sum", path]).decode()
                    with open("usb_hashes.txt", "a") as hash_log:
                        hash_log.write(f"{datetime.datetime.now()}: {hash_output}")
                    results.append(hash_output)
                except Exception as e:
                    log_event(f"Failed to hash {path}: {e}")

    if results:
        return "\n".join(results)
    else:
        return "No target files found for hashing."


def diagnose_storage():
    usb_path = get_usb_mount_path()
    if not usb_path:
        log_event("Storage diagnosis failed: no USB mounted.")
        return "No USB device mounted."
    try:
        stat = os.statvfs(usb_path)
        total = stat.f_frsize * stat.f_blocks / (1024**3)
        free = stat.f_frsize * stat.f_bfree / (1024**3)
        used = total - free
        log_event(f"Storage diagnosis complete: {used:.2f}GB used, {free:.2f}GB free.")
        return f"Diagnosing storage at: {usb_path}\nTotal Size: {total:.2f} GB\nUsed Space: {used:.2f} GB\nFree Space: {free:.2f} GB"
    except Exception as e:
        log_event(f"Storage diagnosis error: {e}")
        return f"Storage diagnosis failed: {e}"
