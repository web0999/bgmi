# BGMI Match Server Stresser & Freeze Pro (Android & PC)

## 🚀 New Features & Upgrades
- **📱 Dedicated Android Mobile App (`android_app.py` / `main.py`):** Touch-optimized UI + Local Mobile Web Dashboard (`http://localhost:5000`) for Android devices.
- **⚡ Auto IP & Port Finder (`auto_finder.py`):** Automatically scans active game server UDP connections on Android (`/proc/net/udp`, `netstat`, `ss`) and fills the Target IP and Port with 1 click.
- **High-Performance UDP Engine:** Multi-socket thread pool with variable game MTU payloads (128B to 1400B).
- **Telegram Bot Support:** Run attacks via Telegram with `/attack`, `/autofind`, `/freeze`, or inline stop button.

---

## 📱 How to Run on Android

### Method 1: Using Pydroid 3 (Recommended - Easiest & Fast)
1. Install **Pydroid 3** from Google Play Store on your Android phone.
2. Transfer project files to your phone storage.
3. Open `android_app.py` or `main.py` in Pydroid 3.
4. Tap the **PLAY ▶️** button.
5. Tap **⚡ AUTO FIND IP & PORT** while in a BGMI match to automatically set the server IP & Port!
6. Tap **🚀 START ATTACK**.

### Method 2: Using Termux (Command Line & Web Dashboard)
1. Install **Termux** on Android.
2. Run the following setup commands:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python net-tools -y
   pip install customtkinter httpx psutil
   ```
3. Run the app:
   ```bash
   python android_app.py
   ```
4. Open your phone's browser and go to `http://localhost:5000` to control the tool via the Web Dashboard.

### Method 3: Compile Standalone `.apk` with Buildozer
To generate a `.apk` file for direct installation on Android:
```bash
pip install buildozer
buildozer init
buildozer -v android debug
```
The compiled APK will be in the `bin/` directory.

---

## 💻 Running on Windows / PC
```bash
python ddos_app.py
```
- Click **⚡ AUTO FIND IP & PORT** to auto-detect active game UDP endpoints.
- Click **START ATTACK**.

---

## 🤖 Running the Telegram Bot
```bash
python telegram_bot.py
```
- Send `/autofind` or `/find` in Telegram to auto-detect active game servers.
- Send `/attack <IP> <PORT> <SECONDS> [THREADS]` to launch match stress sessions.
