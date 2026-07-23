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
    
    print(f"[SYSTEM] Attempting to connect to {ssid}...")
    
    try:
        # Check if nmcli is available
        subprocess.check_output(["which", "nmcli"])
        
        # 1. Purge any stale/incomplete connection profile for this SSID
        subprocess.run(["nmcli", "connection", "delete", "id", ssid], capture_output=True, text=True)
        
        # 2. Try standard wifi connect
        cmd = ["nmcli", "device", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            return True, f"Connected to {ssid}"
            
        # 3. Fallback: If key-mgmt or direct connect failed, build explicit profile with wpa-psk key-mgmt
        print(f"[SYSTEM] Direct connect note: {result.stderr.strip()}. Retrying with explicit WPA profile...")
        subprocess.run(["nmcli", "connection", "delete", "id", ssid], capture_output=True, text=True)
        
        add_cmd = ["nmcli", "connection", "add", "type", "wifi", "con-name", ssid, "ifname", "wlan0", "ssid", ssid]
        subprocess.run(add_cmd, capture_output=True, text=True)
        
        if password:
            sec_cmd = ["nmcli", "connection", "modify", ssid, "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password]
            subprocess.run(sec_cmd, capture_output=True, text=True)
            
        up_result = subprocess.run(["nmcli", "connection", "up", ssid], capture_output=True, text=True, timeout=20)
        
        if up_result.returncode == 0:
            return True, f"Connected to {ssid}"
        else:
            err = up_result.stderr.strip() or result.stderr.strip() or "Connection failed"
            return False, f"Failed: {err}"
            
    except subprocess.CalledProcessError:
        # fallback or nmcli missing
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
