#!/bin/bash
# Install required AUR packages using yay
# 2025-12-03

set -e

print_banner "Installing Required AUR Packages"

# Install via yay ( depricated )
# yay -S --needed --noconfirm \
# brave-bin \
# localsend-bin \
# wayfreeze-git \
# waybar-active-last \
# xdg-terminal-exec \
# yaru-icon-theme

#Install via yay
yay -S --needed --noconfirm \
  brave-bin

# Install via pacman instead of yay
sudo pacman -S --needed --noconfirm \
  localsend \
  waybar \
  wayfreeze \
  xdg-terminal-exec \
  yaru-icon-theme
