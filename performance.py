import subprocess
import datetime
from functions import get_usb_mount_path, log_event

def flush_caches():
    subprocess.run("sync", shell=True)
    subprocess.run(["sudo", "tee", "/proc/sys/vm/drop_caches"], input="3", text=True, stdout=subprocess.DEVNULL)

def normalize_speed(speed_str):
    try:
        if "KiB/s" in speed_str:
            value = float(speed_str.replace("KiB/s", "").strip())
            return round(value / 1024, 2)
        elif "MiB/s" in speed_str:
            return round(float(speed_str.replace("MiB/s", "").strip()), 2)
        elif "MB/s" in speed_str:
            return round(float(speed_str.replace("MB/s", "").strip()), 2)
    except:
        return 0.0
    return 0.0

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
                    raw = part.strip().split("BW=")[-1].split()[0]
                    read_speed = raw
        elif "write:" in line and "IOPS=" in line:
            parts = line.split(",")
            for part in parts:
                if "BW=" in part:
                    raw = part.strip().split("BW=")[-1].split()[0]
                    write_speed = raw
    return read_speed, write_speed

def test_sequential_speed():
    mount_path = get_usb_mount_path()
    if not mount_path:
        log_event("Sequential test failed: no USB mounted.")
        return "No USB device detected."

    test_file = f"{mount_path}/testfile"
    try:
        flush_caches()

        write_cmd = ["dd", "if=/dev/zero", f"of={test_file}", "bs=1M", "count=100", "conv=fdatasync"]
        write_result = subprocess.run(write_cmd, capture_output=True, text=True)
        write_speed = extract_dd_speed(write_result.stderr or write_result.stdout)

        flush_caches()

        read_cmd = ["dd", f"if={test_file}", "of=/dev/null", "bs=1M"]
        read_result = subprocess.run(read_cmd, capture_output=True, text=True)
        read_speed = extract_dd_speed(read_result.stderr or read_result.stdout)

        subprocess.run(["rm", "-f", test_file])

        pi_read = normalize_speed(read_speed)
        pi_write = normalize_speed(write_speed)

        log_event(f"Sequential test: Write={pi_write} MB/s, Read={pi_read} MB/s")
        with open("performance_log.txt", "a") as log:
            timestamp = datetime.datetime.now().isoformat()
            log.write(f"{timestamp}: Sequential Write={pi_write} MB/s, Read={pi_read} MB/s\n")

        return f"Sequential Write Speed: {pi_write} MB/s\nSequential Read Speed: {pi_read} MB/s"
    except Exception as e:
        log_event(f"Sequential test error: {e}")
        return f"Sequential test failed: {e}"

def test_random_speed():
    mount_path = get_usb_mount_path()
    if not mount_path:
        log_event("Random I/O test failed: no USB mounted.")
        return "No USB device detected."

    try:
        flush_caches()

        fio_cmd = [
            "fio",
            "--name=randtest",
            f"--directory={mount_path}",
            "--rw=randrw",
            "--size=100M",
            "--bs=4k",
            "--numjobs=1",
            "--iodepth=32",
            "--runtime=30",
            "--group_reporting"
        ]
        result = subprocess.run(fio_cmd, capture_output=True, text=True)
        read_speed, write_speed = extract_fio_speeds(result.stdout)

        pi_read = normalize_speed(read_speed)
        pi_write = normalize_speed(write_speed)

        log_event(f"Random I/O test: Read={pi_read} MB/s, Write={pi_write} MB/s")
        with open("performance_log.txt", "a") as log:
            timestamp = datetime.datetime.now().isoformat()
            log.write(f"{timestamp}: Random Read={pi_read} MB/s, Write={pi_write} MB/s\n")

        return f"Random Read Speed: {pi_read} MB/s\nRandom Write Speed: {pi_write} MB/s"
    except Exception as e:
        log_event(f"Random I/O test error: {e}")
        return f"Random I/O test failed: {e}"
