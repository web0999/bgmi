#!/usr/bin/env bash
# BGMI MATCH FREEZE PRO - ANDROID ONE-TAP LAUNCHER
echo "=================================================="
echo "🚀 Starting BGMI Match Freeze Pro (Android Edition)"
echo "=================================================="

# Install missing requirements if needed
python -m pip install customtkinter httpx psutil > /dev/null 2>&1

# Launch Python Mobile Engine & Web Interface
python android_app.py
