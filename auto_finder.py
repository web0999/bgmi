import os
import re
import socket
import subprocess
import platform

def hex_to_ip(hex_str):
    """Convert hex string from /proc/net/udp to IP address string"""
    try:
        # Little-endian 8 hex chars (4 bytes)
        addr = bytes.fromhex(hex_str)
        if len(addr) == 4:
            return f"{addr[3]}.{addr[2]}.{addr[1]}.{addr[0]}"
    except Exception:
        pass
    return None

def hex_to_port(hex_str):
    """Convert hex string from /proc/net/udp to integer port"""
    try:
        return int(hex_str, 16)
    except Exception:
        return 0

def scan_proc_net_udp():
    """Scan /proc/net/udp and /proc/net/udp6 on Android/Linux for active game UDP sockets."""
    found = []
    paths = ['/proc/net/udp', '/proc/net/udp6']
    
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            with open(path, 'r') as f:
                lines = f.readlines()
                # Skip header
                for line in lines[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        rem_addr = parts[2]
                        if ':' in rem_addr:
                            ip_hex, port_hex = rem_addr.split(':')
                            ip = hex_to_ip(ip_hex)
                            port = hex_to_port(port_hex)
                            if ip and port > 0 and ip != "0.0.0.0" and ip != "127.0.0.1":
                                # Exclude common DNS / System ports
                                if port not in [53, 67, 68, 123, 1900, 5353]:
                                    found.append((ip, port))
        except Exception:
            pass
    return found

def scan_netstat():
    """Scan via netstat / ss command on Android (Termux/Pydroid) or Windows/Linux"""
    found = []
    system = platform.system().lower()
    
    cmd = []
    if system == 'windows':
        cmd = ['netstat', '-an', '-p', 'udp']
    else:
        cmd = ['netstat', '-an']
        
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=3)
        # Parse UDP lines
        for line in output.splitlines():
            line_str = line.strip().lower()
            if 'udp' in line_str:
                # Match IP:Port or IP.Port pattern
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[:\.](\d{1,5})', line)
                if match:
                    ip = match.group(1)
                    port = int(match.group(2))
                    if ip not in ["0.0.0.0", "127.0.0.1"] and port not in [0, 53, 67, 68, 123, 1900, 5353]:
                        found.append((ip, port))
    except Exception:
        pass
    return found

def scan_ss():
    """Scan via ss command (popular on Android/Linux)"""
    found = []
    try:
        output = subprocess.check_output(['ss', '-un', '-a'], stderr=subprocess.STDOUT, text=True, timeout=3)
        for line in output.splitlines():
            match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})', line)
            if match:
                ip = match.group(1)
                port = int(match.group(2))
                if ip not in ["0.0.0.0", "127.0.0.1"] and port not in [0, 53, 67, 68, 123, 1900, 5353]:
                    found.append((ip, port))
    except Exception:
        pass
    return found

def find_bgmi_ip_port():
    """
    Main auto-discovery function.
    Returns tuple (ip, port, description) or None if no active match server connection is detected.
    """
    results = scan_proc_net_udp()
    if not results:
        results = scan_ss()
    if not results:
        results = scan_netstat()
        
    if not results:
        return None, None, "No active match server connections detected."
        
    # Prioritize game ports range (BGMI/PUBG typically uses 10000 - 20000, 17000-18500, 8000-9000)
    game_ports = [r for r in results if 10000 <= r[1] <= 20000 or 8000 <= r[1] <= 9000]
    
    if game_ports:
        best_match = game_ports[0]
        return best_match[0], best_match[1], f"Auto-detected BGMI Server: {best_match[0]}:{best_match[1]}"
    else:
        best_match = results[0]
        return best_match[0], best_match[1], f"Auto-detected Active UDP: {best_match[0]}:{best_match[1]}"

if __name__ == "__main__":
    ip, port, msg = find_bgmi_ip_port()
    print(f"Status: {msg}")
    if ip and port:
        print(f"Target IP: {ip}")
        print(f"Target Port: {port}")
