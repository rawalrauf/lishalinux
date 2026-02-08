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
# satty-git \
# gpu-screen-recorder \
# waybar-active-last \
# xdg-terminal-exec \
# yaru-icon-theme

#Install via yay
yay -S --needed --noconfirm \
  waybar-active-last \
  brave-bin

# Install via pacman instead of yay
sudo pacman -S --needed --noconfirm \
  localsend \
  wayfreeze \
  satty \
  gpu-screen-recorder \
  xdg-terminal-exec \
  yaru-icon-theme
