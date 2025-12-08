#!/bin/bash
# Arch Linux + Hyprland Personalized Setup
# Installation Script
# Created: 2025-12-03
# System: Arch Linux with Hyprland

set -e

echo "=========================================="
echo "  LishaLinux Installation Script"
echo "=========================================="
echo ""

# Keep sudo alive throughout the script
sudo -v
while true; do
  sudo -n true
  sleep 60
  kill -0 "$$" || exit
done 2>/dev/null &

## Base Packages Installation
echo "Installing base packages..."
sudo pacman -S --noconfirm git unzip

## Install yay AUR helper
if ! command -v yay &>/dev/null; then
  echo "Installing yay AUR helper..."
  cd /tmp
  git clone https://aur.archlinux.org/yay.git
  cd yay
  makepkg -si --noconfirm
  cd ~
fi

## Install all official repository packages
echo "Installing official repository packages..."

sudo pacman -S --noconfirm \
  alacritty \
  playerctl \
  pqiv \
  mpv \
  ghostty \
  foliate \
  jq \
  gum \
  nautilus \
  gvfs \
  gvfs-mtp \
  udisks2 \
  android-udev \
  blueberry \
  mako \
  wl-clipboard \
  hyprlock \
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
  pavucontrol \
  gnome-disk-utility \
  evince \
  eza \
  bat \
  zoxide \
  starship \
  ffmpeg

# Install neovim last
echo "Installing neovim..."
sudo pacman -S --noconfirm neovim

# Setup LazyVim configuration for neovim
echo "Setting up LazyVim..."
if [ -d ~/.config/nvim ]; then
  mv ~/.config/nvim ~/.config/nvim.backup.$(date +%s)
fi
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git

## Install AUR packages
echo "Installing AUR packages..."

yay -S --noconfirm \
  brave-bin \
  localsend-bin \
  walker-bin \
  elephant-bin \
  elephant-providerlist-bin \
  elephant-desktopapplications-bin \
  wayfreeze-git \
  satty-git \
  gpu-screen-recorder \
  waybar-active-last

## Limine + Snapper Snapshot Setup (Optional)
echo "Checking for Limine and Btrfs..."
if (pacman -Q limine &>/dev/null || find /boot -name 'limine.conf' 2>/dev/null | grep -q .) && findmnt -n -o FSTYPE / | grep -q btrfs; then
  echo "Limine bootloader and Btrfs detected. Setting up snapper..."

  # Install snapper and dependencies
  sudo pacman -S --noconfirm snapper btrfs-progs inotify-tools jre-openjdk-headless libnotify snap-pac rsync

  # Install limine-mkinitcpio-hook and limine-snapper-sync
  yay -S --noconfirm limine-mkinitcpio-hook limine-snapper-sync

  # Configure snapshot limits
  sudo snapper -c root set-config "NUMBER_LIMIT=5"
  sudo snapper -c root set-config "NUMBER_LIMIT_IMPORTANT=3"

  # Disable timeline snapshots
  sudo snapper -c root set-config "TIMELINE_CREATE=no"
  sudo systemctl disable --now snapper-timeline.timer

  # Enable limine-snapper-sync service
  sudo systemctl enable --now limine-snapper-sync.service

  echo "Snapper setup complete!"
else
  echo "Limine bootloader or Btrfs not detected. Skipping snapper setup."
fi

## Configuration Files Setup
echo "Setting up configuration files..."

cd ~/lishalinux

# Backup existing configs
echo "Backing up existing configurations..."
[ -d ~/.config/alacritty ] && mv ~/.config/alacritty ~/.config/alacritty.backup.$(date +%s)
[ -d ~/.config/elephant ] && mv ~/.config/elephant ~/.config/elephant.backup.$(date +%s)
[ -d ~/.config/mako ] && mv ~/.config/mako ~/.config/mako.backup.$(date +%s)
[ -d ~/.config/walker ] && mv ~/.config/walker ~/.config/walker.backup.$(date +%s)
[ -d ~/.config/waybar ] && mv ~/.config/waybar ~/.config/waybar.backup.$(date +%s)
[ -d ~/.config/uwsm ] && mv ~/.config/uwsm ~/.config/uwsm.backup.$(date +%s)
[ -d ~/.config/hypr ] && mv ~/.config/hypr ~/.config/hypr.backup.$(date +%s)
[ -d ~/.local/share/applications ] && mv ~/.local/share/applications ~/.local/share/applications.backup.$(date +%s)
[ -f ~/.config/mimeapps.list ] && mv ~/.config/mimeapps.list ~/.config/mimeapps.list.backup.$(date +%s)
[ -f ~/.bashrc ] && mv ~/.bashrc ~/.bashrc.backup.$(date +%s)

# Copy configuration files
echo "Copying configuration files..."
cp -r alacritty elephant mako walker waybar uwsm hypr ~/.config/
cp mimeapps.list ~/.config/
cp bashrc ~/.bashrc

# Copy browser flags
[ -f ~/.config/brave-flags.conf ] && mv ~/.config/brave-flags.conf ~/.config/brave-flags.conf.backup.$(date +%s)
[ -f ~/.config/chromium-flags.conf ] && mv ~/.config/chromium-flags.conf ~/.config/chromium-flags.conf.backup.$(date +%s)
cp brave-flags.conf ~/.config/
cp chromium-flags.conf ~/.config/

# Copy desktop applications
cp -r applications ~/.local/share/

# Copy lishalinux scripts
cp -r lishalinux ~/.local/share/

# Make scripts executable
chmod +x ~/.local/share/lishalinux/bin/*
chmod +x ~/.local/share/lishalinux/default/waybar/indicators/screen-recording.sh

# Reload bashrc to apply changes
echo "Reloading shell configuration..."
source ~/.bashrc

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""

# Ask for reboot
read -p "Would you like to reboot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Rebooting..."
  sudo reboot
else
  echo "Please reboot manually to apply all changes."
fi
