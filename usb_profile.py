import os
import subprocess
from functions import log_event

def detect_hid_threads():
    devices = []
    hid_paths = sorted([f for f in os.listdir("/dev") if f.startswith("hidraw")])
    thread_id = 1

    for hid in hid_paths:
        dev_path = f"/dev/{hid}"
        try:
            # Get udev info
            udev_info = subprocess.check_output(["udevadm", "info", "--query=all", "--name", dev_path]).decode()
            name = "Unknown HID Device"
            for line in udev_info.splitlines():
                if "ID_MODEL=" in line:
                    name = line.split("ID_MODEL=")[-1].strip()
                elif "ID_VENDOR=" in line and name == "Unknown HID Device":
                    name = line.split("ID_VENDOR=")[-1].strip()

            # Get device handle (mocked as 00000000000000 for now)
            handle = "00000000000000"

            # Check if device is active in /proc/bus/input/devices
            status = "Inactive"
            with open("/proc/bus/input/devices", "r") as f:
                if dev_path in f.read():
                    status = "Running"

            devices.append({
                "Thread ID": f"{thread_id:04}",
                "Device Handle": handle,
                "Device Path": dev_path,
                "Device Name": name,
                "Thread Status": status
            })
            thread_id += 1
        except Exception as e:
            log_event(f"HID thread scan error on {dev_path}: {e}")

    return devices
