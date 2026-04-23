try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None

def scan_frame(frame):
    """
    Scans a numpy frame/image for QR codes.
    Returns the decoded text of the first QR code found, or None.
    """
    if pyzbar is None:
        return None
        
    try:
        # pyzbar works best with grayscale or RGB
        decoded_objs = pyzbar.decode(frame)
        for obj in decoded_objs:
            if obj.type == 'QRCODE':
                return obj.data.decode('utf-8')
    except Exception as e:
        print(f"[ERROR] QR Scan: {e}")
        
    return None
