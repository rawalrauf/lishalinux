#!/bin/bash
# Install required AUR packages using yay
# 2025-12-03

set -e

print_banner "Installing Required AUR Packages"

yay -S --needed --noconfirm \
  brave-bin \
  localsend-bin \
  wayfreeze-git \
  satty-git \
  gpu-screen-recorder \
  waybar-active-last \
  xdg-terminal-exec \
  yaru-icon-theme
