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
sudo pacman -S --noconfirm base-devel git unzip

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
  hyprpolkitagent \
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
[ -d ~/.config/nvim ] && mv ~/.config/nvim ~/.config/nvim.backup.$(date +%s)

git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git

## Install AUR packages
echo "Installing AUR packages..."

yay -S --noconfirm \
  brave-bin \
  localsend-bin \
  wayfreeze-git \
  satty-git \
  gpu-screen-recorder \
  waybar-active-last \
  xdg-terminal-exec

## Limine + Snapper Snapshot Setup (Optional)
echo "Checking for Limine and Btrfs..."
if (pacman -Q limine &>/dev/null || find /boot -name 'limine.conf' 2>/dev/null | grep -q .) && findmnt -n -o FSTYPE / | grep -q btrfs; then
  echo "Limine bootloader and Btrfs detected. Setting up snapper..."

  # Install snapper and dependencies
  sudo pacman -S --noconfirm snapper btrfs-progs inotify-tools libnotify snap-pac rsync

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

## Add Omarchy repository for walker
echo "Adding Omarchy repository for walker..."
if ! grep -q "\[omarchy\]" /etc/pacman.conf; then
  echo -e "\n[omarchy]\nSigLevel = Optional TrustAll\nInclude = /etc/pacman.d/omarchy-mirrorlist" | sudo tee -a /etc/pacman.conf
fi

if [ ! -f /etc/pacman.d/omarchy-mirrorlist ]; then
  echo "Server = https://pkgs.omarchy.org/stable/\$arch" | sudo tee /etc/pacman.d/omarchy-mirrorlist
fi

sudo pacman -Sy
sudo pacman -S --noconfirm omarchy-walker

## Configuration Files Setup
echo "Setting up configuration files..."

cd ~/lishalinux

# Backup existing configs
echo "Backing up existing configurations..."
[ -d ~/.config/ghostty ] && mv ~/.config/ghostty ~/.config/ghostty.backup.$(date +%s)
[ -d ~/.config/autostart ] && mv ~/.config/autostart ~/.config/autostart.backup.$(date +%s)
[ -d ~/.config/swayosd ] && mv ~/.config/swayosd ~/.config/swayosd.backup.$(date +%s)
[ -d ~/.config/elephant ] && mv ~/.config/elephant ~/.config/elephant.backup.$(date +%s)
[ -d ~/.config/mako ] && mv ~/.config/mako ~/.config/mako.backup.$(date +%s)
[ -d ~/.config/walker ] && mv ~/.config/walker ~/.config/walker.backup.$(date +%s)
[ -d ~/.config/waybar ] && mv ~/.config/waybar ~/.config/waybar.backup.$(date +%s)
[ -d ~/.config/uwsm ] && mv ~/.config/uwsm ~/.config/uwsm.backup.$(date +%s)
[ -d ~/.config/hypr ] && mv ~/.config/hypr ~/.config/hypr.backup.$(date +%s)
[ -d ~/.local/share/applications ] && mv ~/.local/share/applications ~/.local/share/applications.backup.$(date +%s)
[ -d ~/.local/share/lishalinux ] && mv ~/.local/share/lishalinux ~/.local/share/lishalinux.backup.$(date +%s)

[ -f ~/.config/mimeapps.list ] && mv ~/.config/mimeapps.list ~/.config/mimeapps.list.backup.$(date +%s)
[ -f ~/.bashrc ] && mv ~/.bashrc ~/.bashrc.backup.$(date +%s)
[ -f ~/.config/starship.toml ] && mv ~/.config/starship.toml ~/.config/starship.toml.backup.$(date +%s)
[ -f ~/.config/xdg-terminals.list ] && mv ~/.config/xdg-terminals.list ~/.config/xdg-terminals.list.backup.$(date +%s)

# Copy configuration files
echo "Copying configuration files..."
cp -r ghostty swayosd elephant mako walker waybar uwsm autostart hypr ~/.config/
cp mimeapps.list ~/.config/
cp starship.toml ~/.config/
cp bashrc ~/.bashrc
cp xdg-terminals.list ~/.config/

# Copy browser flags
[ -f ~/.config/brave-flags.conf ] && mv ~/.config/brave-flags.conf ~/.config/brave-flags.conf.backup.$(date +%s)
[ -f ~/.config/chromium-flags.conf ] && mv ~/.config/chromium-flags.conf ~/.config/chromium-flags.conf.backup.$(date +%s)
cp brave-flags.conf ~/.config/
cp chromium-flags.conf ~/.config/

# Copy desktop applications
cp -r applications ~/.local/share/

# Copy lishalinux scripts
cp -r lishalinux ~/.local/share/

# Run elephant as systemd service and walker autostart on login
elephant service enable
systemctl --user start elephant.service
setsid walker --gapplication-service &

# Make scripts executable
chmod +x ~/.local/share/lishalinux/bin/*
chmod +x ~/.local/share/lishalinux/default/waybar/indicators/screen-recording.sh

# Reload bashrc to apply changes
echo "Reloading shell configuration..."
source ~/.bashrc

# Enable darkmode for gnome applications
gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"

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
