import subprocess
import datetime
import os
import psutil

def get_timestamp():
    return datetime.datetime.now().isoformat()

def log_event(message):
    with open("usb_log.txt", "a") as log:
        timestamp = get_timestamp()
        log.write(f"{timestamp}: {message}\n")

def system_safe():
    temp = get_temp()
    ram = psutil.virtual_memory().percent
    if temp > 70 or ram > 85:
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
        timestamp = get_timestamp()
        with open("usb_metadata.txt", "a") as meta:
            info = f"{timestamp}:\n{output}\n"
            meta.write(info)
        log_event("USB metadata captured.")
        return info
    except Exception as e:
        log_event(f"Error capturing USB metadata: {e}")
        return 'Error capturing metadata.'

def detect_potential_threats():
    usb_path = get_usb_mount_path()
    if not usb_path or not os.path.exists(usb_path):
        log_event("USB mount point not found.")
        return "USB mount point not found."

    safe, msg = system_safe()
    if not safe:
        return msg

    suspicious_exts = ('.exe', '.dll', '.bat', '.sh', '.py', '.bin')
    suspicious_files = []

    for root, dirs, files in os.walk(usb_path):
        for file in files:
            path = os.path.join(root, file)
            try:
                size = os.path.getsize(path)
                is_hidden = file.startswith('.') or '/.' in path
                if file.lower().endswith(suspicious_exts) or is_hidden or size > 10 * 1024 * 1024:
                    suspicious_files.append(f"{path} — Size: {size} bytes — Hidden: {is_hidden}")
            except Exception as e:
                log_event(f"Error analyzing {path}: {e}")

    if suspicious_files:
        with open("potential_threats.txt", "a") as threat_log:
            for entry in suspicious_files:
                threat_log.write(f"{get_timestamp()}: {entry}\n")
        log_event("Potential threats detected and logged.")
        return "\n".join(suspicious_files)
    else:
        return "No suspicious files detected."

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

def ClearData():
    msg1 = clear('potential_threats.txt')
    msg2 = clear('usb_log.txt')
    msg3 = clear('usb_metadata.txt')
    msg4 = clear('performance_log.txt')
    log_event("User cleared all data.")
    return f"{msg1}\n{msg2}\n{msg3}\n{msg4}"

def History():
    threats = readfile('potential_threats.txt')
    logs = readfile('usb_log.txt')
    meta = readfile('usb_metadata.txt')
    perf = readfile('performance_log.txt')
    log_event("User viewed history.")
    return f"Potential Threats:\n{threats}\n\nLogs:\n{logs}\n\nMetadata:\n{meta}\n\nPerformance:\n{perf}"