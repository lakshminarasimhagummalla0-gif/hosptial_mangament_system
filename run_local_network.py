# -*- coding: utf-8 -*-
# CareSync - One-Click Local Network Sharing Script
# This script starts the app and makes it accessible on your local network
# so other devices (phones, other computers) can access it
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import subprocess
import socket
import os

def get_local_ip():
    """Get the local network IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 5000
    
    print("=" * 60)
    print("[HOSPITAL] CareSync Hospital Management System")
    print("=" * 60)
    print(f"\n[OK] Starting server...")
    print(f"\n[PC]   Access from THIS computer:  http://localhost:{port}")
    print(f"[NET]  Access from OTHER devices:  http://{local_ip}:{port}")
    print(f"\n[TIP]  Share the second URL with phones/tablets on same WiFi!")
    print(f"\n[KEY]  Login Credentials:")
    print(f"   Admin   -> username: admin                          | password: admin123")
    print(f"   Doctor  -> username: sarah.jenkins@hospital.com    | password: doctor123")
    print(f"   Patient -> username: john.doe@email.com            | password: patient123")
    print(f"\n[STOP] Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Use the venv python if available
    venv_python = os.path.join('.venv', 'Scripts', 'python.exe')
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    # Set environment variable to bind to all interfaces
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    
    subprocess.run([
        python_exe, '-c',
        f'import app; app.app.run(host="0.0.0.0", port={port}, debug=False)'
    ], env=env)
