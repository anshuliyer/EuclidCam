import os
import subprocess
import time

def parse_wifi_qr(text):
    """
    Parses a WiFi QR string: WIFI:S:<SSID>;T:<TYPE>;P:<PASS>;;
    Returns (ssid, password) or (None, None)
    """
    if not text.startswith("WIFI:"):
        return None, None
    
    parts = text[5:].split(";")
    ssid = None
    password = None
    
    for part in parts:
        if part.startswith("S:"):
            ssid = part[2:]
        elif part.startswith("P:"):
            password = part[2:]
            
    return ssid, password

def connect_to_wifi(ssid, password):
    """
    Attempts to connect to WiFi using nmcli.
    Returns (success, message)
    """
    if not ssid:
        return False, "No SSID provided"
    
    print(f"[SYSTEM] Attempting to connect to '{ssid}'...")
    
    try:
        # Check if nmcli is available
        subprocess.check_output(["which", "nmcli"])
        
        # 1. Bring down Hotspot if active so wlan0 can switch to client/station mode
        subprocess.run(["sudo", "nmcli", "connection", "down", "Hotspot"], capture_output=True, text=True)
        time.sleep(1)
        
        # 2. Trigger WiFi rescan
        subprocess.run(["sudo", "nmcli", "device", "wifi", "rescan"], capture_output=True, text=True)
        time.sleep(2)
        
        # 3. Direct wifi connect using nmcli
        cmd = ["sudo", "nmcli", "device", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        
        if result.returncode == 0:
            return True, f"Connected to {ssid}"
            
        # 4. Fallback: Create explicit profile with wpa-psk if direct connect failed
        err_msg = result.stderr.strip() or result.stdout.strip()
        print(f"[SYSTEM] Direct wifi connect note: {err_msg}. Retrying with explicit WPA profile...")
        
        subprocess.run(["sudo", "nmcli", "connection", "delete", "id", ssid], capture_output=True, text=True)
        
        add_cmd = ["sudo", "nmcli", "connection", "add", "type", "wifi", "con-name", ssid, "ifname", "wlan0", "ssid", ssid]
        if password:
            add_cmd.extend(["wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password])
            
        add_res = subprocess.run(add_cmd, capture_output=True, text=True)
        
        if add_res.returncode == 0:
            up_result = subprocess.run(["sudo", "nmcli", "connection", "up", ssid], capture_output=True, text=True, timeout=20)
            if up_result.returncode == 0:
                return True, f"Connected to {ssid}"
            else:
                return False, f"Failed: {up_result.stderr.strip() or err_msg}"
        else:
            return False, f"Failed: {add_res.stderr.strip() or err_msg}"
            
    except subprocess.CalledProcessError:
        return False, "nmcli not found or error"
    except Exception as e:
        return False, f"Error: {e}"

def is_online():
    """Checks if we have an IP address that isn't localhost"""
    try:
        output = subprocess.check_output(["hostname", "-I"]).decode().strip()
        return len(output.split()) > 0
    except:
        return False
