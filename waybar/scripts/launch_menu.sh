#!/usr/bin/env python3
import os
import subprocess

# Set the required environment variable and run the script directly
os.environ['LD_PRELOAD'] = '/usr/lib/libgtk4-layer-shell.so'
subprocess.run(['python3', '/home/raw/.config/waybar/scripts/menu_working.py'])
