#!/bin/bash
# Enable Dark Mode and set GTK/Icon themes for Gnome Applications
# 2025-12-03

set -e

print_banner "Enabling Dark Mode for Gnome Applications"

# Enable dark mode
gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"

# Set GTK theme
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'

# Set icon theme
gsettings set org.gnome.desktop.interface icon-theme 'Yaru-purple'

print_banner "Gnome Dark Mode and Themes applied successfully."
