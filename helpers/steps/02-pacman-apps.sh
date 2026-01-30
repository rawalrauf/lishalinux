#!/bin/bash
# Install required Pacman packages for a fresh Hyprland system
# 2025-12-03

set -e

print_banner "Installing Required Pacman Packages"

sudo pacman -S --needed --noconfirm \
  playerctl \
  pqiv \
  mpv \
  ghostty \
  jq \
  gum \
  nautilus \
  gvfs \
  gvfs-mtp \
  udisks2 \
  polkit-gnome \
  android-udev \
  bluetui \
  mako \
  wl-clipboard \
  hyprlock \
  swayosd \
  wiremix \
  gnome-calculator \
  btop \
  hypridle \
  hyprpaper \
  uwsm \
  fzf \
  ttf-cascadia-mono-nerd \
  brightnessctl \
  impala \
  hyprsunset \
  hyprpicker \
  power-profiles-daemon \
  pamixer \
  gnome-disk-utility \
  xdg-desktop-portal-gtk \
  gnome-themes-extra \
  lazygit \
  evince \
  eza \
  bat \
  zoxide \
  starship \
  ffmpeg
