from functions import readfile, log_event

def History():
    hashes = readfile('usb_hashes.txt')
    logs = readfile('usb_log.txt')
    meta = readfile('usb_metadata.txt')
    log_event("User viewed history.")
    return f"Hashes:\n{hashes}\n\nLogs:\n{logs}\n\nMetadata:\n{meta}"
