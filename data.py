from functions import clear, log_event

def ClearData():
    msg1 = clear('usb_hashes.txt')
    msg2 = clear('usb_log.txt')
    msg3 = clear('usb_metadata.txt')
    log_event("User cleared all data.")
    return f"{msg1}\n{msg2}\n{msg3}"
