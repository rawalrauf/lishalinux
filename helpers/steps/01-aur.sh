#!/bin/bash
# Install AUR Helper yay if not already installed
# 2025-12-03

set -e

print_banner "Installing AUR Helper: yay"

# Check if yay is already installed
if ! command -v yay &>/dev/null; then
  print_banner "Cloning yay from AUR and building..."

  cd /tmp
  git clone https://aur.archlinux.org/yay.git
  cd yay
  makepkg -si --noconfirm
  cd ~
else
  print_banner "yay is already installed. Skipping..."
fi
