#!/bin/bash
# Make Lishalinux scripts and binaries executable
# 2025-12-03

set -e

print_banner "Setting Executable Permissions for Lishalinux Scripts"

# Make all scripts in ~/.local/share/lishalinux/bin executable
if [ -d ~/.local/share/lishalinux/bin ]; then
  print_banner "Making bin scripts executable..."
  chmod +x ~/.local/share/lishalinux/bin/*
fi

# Make specific waybar indicator scripts executable
WAYBAR_SCRIPT=~/.local/share/lishalinux/default/waybar/indicators/screen-recording.sh
if [ -f "$WAYBAR_SCRIPT" ]; then
  print_banner "Making waybar indicator scripts executable..."
  chmod +x "$WAYBAR_SCRIPT"
fi

print_banner "Permissions setup complete."
