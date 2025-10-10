import subprocess
import datetime
from functions import get_usb_mount_path, log_event

def extract_dd_speed(output):
    for line in output.splitlines():
        if "bytes" in line and "s," in line:
            return line.split(",")[-1].strip()
    return "Unknown"

def extract_fio_speeds(output):
    read_speed = write_speed = "Unknown"
    for line in output.splitlines():
        if "read:" in line and "IOPS=" in line:
            parts = line.split(",")
            for part in parts:
                if "BW=" in part:
                    read_speed = part.strip().split("BW=")[-1]
        elif "write:" in line and "IOPS=" in line:
            parts = line.split(",")
            for part in parts:
                if "BW=" in part:
                    write_speed = part.strip().split("BW=")[-1]
    return read_speed, write_speed

def test_sequential_speed():
    mount_path = get_usb_mount_path()
    if not mount_path:
        log_event("Sequential test failed: no USB mounted.")
        return "No USB device detected."

    test_file = f"{mount_path}/testfile"
    try:
        write_cmd = ["dd", "if=/dev/zero", f"of={test_file}", "bs=4M", "count=64", "conv=fdatasync"]
        write_result = subprocess.run(write_cmd, capture_output=True, text=True)
        write_speed = extract_dd_speed(write_result.stderr)

        read_cmd = ["dd", f"if={test_file}", "of=/dev/null", "bs=4M"]
        read_result = subprocess.run(read_cmd, capture_output=True, text=True)
        read_speed = extract_dd_speed(read_result.stderr)

        subprocess.run(["rm", "-f", test_file])

        log_event(f"Sequential test: Write={write_speed}, Read={read_speed}")
        with open("performance_log.txt", "a") as log:
            timestamp = datetime.datetime.now().isoformat()
            log.write(f"{timestamp}: Sequential Write={write_speed}, Read={read_speed}\n")

        return f"Sequential Write Speed: {write_speed}\nSequential Read Speed: {read_speed}"
    except Exception as e:
        log_event(f"Sequential test error: {e}")
        return f"Sequential test failed: {e}"

def test_random_speed():
    mount_path = get_usb_mount_path()
    if not mount_path:
        log_event("Random I/O test failed: no USB mounted.")
        return "No USB device detected."

    try:
        fio_cmd = [
            "fio",
            "--name=randtest",
            f"--directory={mount_path}",
            "--rw=randrw",
            "--size=100M",
            "--bs=4k",
            "--numjobs=1",
            "--runtime=30",
            "--group_reporting"
        ]
        result = subprocess.run(fio_cmd, capture_output=True, text=True)
        read_speed, write_speed = extract_fio_speeds(result.stdout)

        log_event(f"Random I/O test: Read={read_speed}, Write={write_speed}")
        with open("performance_log.txt", "a") as log:
            timestamp = datetime.datetime.now().isoformat()
            log.write(f"{timestamp}: Random Read={read_speed}, Write={write_speed}\n")

        return f"Random Read Speed: {read_speed}\nRandom Write Speed: {write_speed}"
    except Exception as e:
        log_event(f"Random I/O test error: {e}")
        return f"Random I/O test failed: {e}"
