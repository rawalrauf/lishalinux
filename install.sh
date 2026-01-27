#!/bin/bash
# Arch Linux + Hyprland Personalized Setup
# Installation Script
# Created: 2025-12-03
# System: Arch Linux with Hyprland

set -e

echo -e "\n\n\e[1;38;2;162;221;157m<========== Lishalinux Installation Script ==========>\e[0m\n\n"

# Keep sudo alive throughout the script
sudo -v
while true; do
  sudo -n true
  sleep 60
  kill -0 "$$" || exit
done 2>/dev/null &

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing AUR Dependencies ==========>\e[0m\n\n"
sleep 2

sudo pacman -S --noconfirm base-devel git unzip

if ! command -v yay &>/dev/null; then

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing AUR Helper YAY ==========>\e[0m\n\n"
  sleep 2

  cd /tmp
  git clone https://aur.archlinux.org/yay.git
  cd yay
  makepkg -si --noconfirm
  cd ~
fi

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing Required Pacman Packages ==========>\e[0m\n\n"
sleep 2

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
  yaru-icon-theme \
  lazygit \
  evince \
  eza \
  bat \
  zoxide \
  starship \
  ffmpeg

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing Neovim(LazyVim) Editor ==========>\e[0m\n\n"
sleep 2

sudo pacman -S --noconfirm neovim

# Setup LazyVim configuration for neovim
[ -d ~/.config/nvim ] && mv ~/.config/nvim ~/.config/nvim.backup.$(date +%s)

git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing Required AUR Packages With YAY ==========>\e[0m\n\n"

yay -S --noconfirm \
  brave-bin \
  localsend-bin \
  wayfreeze-git \
  satty-git \
  gpu-screen-recorder \
  waybar-active-last \
  xdg-terminal-exec

echo -e "\n\n\e[1;38;2;162;221;157m<========== Detecting Limine Bootloader, Btrfs File System & UEFI ==========>\e[0m\n\n"
sleep 2

if (pacman -Q limine &>/dev/null || find /boot -name 'limine.conf' 2>/dev/null | grep -q .) && findmnt -n -o FSTYPE / | grep -q btrfs && [[ -d /sys/firmware/efi ]]; then

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Limine, Btrfs & UEFI Detected, Installing Dependencies ==========>\e[0m\n\n"
  sleep 2

  # Install snapper and dependencies
  sudo pacman -S --noconfirm snapper btrfs-progs inotify-tools libnotify snap-pac rsync jre-openjdk-headless

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing limine-snapper-sync For Easy Rollbacks ==========>\e[0m\n\n"

  # Remove/backup conflicting /boot/limine/limine.conf, cause /boot/limine.conf already available
  [ -f /boot/limine.conf ] && [ -f /boot/limine/limine.conf ] && sudo mv /boot/limine/limine.conf /boot/limine/limine.conf.backup.$(date +%s)

  # Install limine-mkinitcpio-hook and limine-snapper-sync
  yay -S --noconfirm limine-mkinitcpio-hook limine-snapper-sync

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Configuring Limine and Snapper ==========>\e[0m\n\n"
  sleep 2

  # Configure snapshot limits
  sudo snapper -c root set-config "NUMBER_LIMIT=5"
  sudo snapper -c root set-config "NUMBER_LIMIT_IMPORTANT=3"

  # Disable timeline snapshots
  sudo snapper -c root set-config "TIMELINE_CREATE=no"
  sudo systemctl disable --now snapper-timeline.timer

  # Enable limine-snapper-sync service
  sudo systemctl enable --now limine-snapper-sync.service

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Snapshots Rollbacks Setup Complete ==========>\e[0m\n\n"

else
  echo "Limine bootloader, Btrfs or UEFI not detected. Skipping snapper setup."
  echo -e "\n\n\e[1;38;2;162;221;157m<========== Limine Bootloader, Btrfs or UEFI not Detected, Skipping Snapper Setup ==========>\e[0m\n\n"
  sleep 2

fi

echo -e "\n\n\e[1;38;2;162;221;157m<========== Adding Stable Repository for Walker ==========>\e[0m\n\n"
sleep 2

if ! grep -q "\[omarchy\]" /etc/pacman.conf; then
  echo -e "\n[omarchy]\nSigLevel = Optional TrustAll\nInclude = /etc/pacman.d/omarchy-mirrorlist" | sudo tee -a /etc/pacman.conf
fi

if [ ! -f /etc/pacman.d/omarchy-mirrorlist ]; then
  echo "Server = https://pkgs.omarchy.org/stable/\$arch" | sudo tee /etc/pacman.d/omarchy-mirrorlist
fi

sudo pacman -Sy

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installing Walker and its Dependencies ==========>\e[0m\n\n"
sleep 2
sudo pacman -S --noconfirm omarchy-walker

echo -e "\n\n\e[1;38;2;162;221;157m<========== Autostart Walker and Run Elephant as Systemd Service  ==========>\e[0m\n\n"
sleep 2

pkill elephant || echo "elephant is not running, starting it now"
elephant service enable
systemctl --user start elephant.service
pkill walker || echo "walker is not running, starting it now"
setsid walker --gapplication-service &

echo -e "\n\n\e[1;38;2;162;221;157m<========== Creating Backup For Existing Configs ==========>\e[0m\n\n"
sleep 2

cd ~/lishalinux

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

echo -e "\n\n\e[1;38;2;162;221;157m<========== Copying Lishalinux Configs To Desired Locations ==========>\e[0m\n\n"
sleep 2

cp -r ghostty swayosd elephant mako walker waybar uwsm autostart hypr ~/.config/
cp mimeapps.list ~/.config/
cp starship.toml ~/.config/
cp bashrc ~/.bashrc
cp xdg-terminals.list ~/.config/

# Copy browser flags
[ -f ~/.config/brave-flags.conf ] && mv ~/.config/brave-flags.conf ~/.config/brave-flags.conf.backup.$(date +%s)
cp brave-flags.conf ~/.config/

# Copy desktop applications
cp -r applications ~/.local/share/

# Copy lishalinux scripts
cp -r lishalinux ~/.local/share/

echo -e "\n\n\e[1;38;2;162;221;157m<========== Making Scripts Executable ==========>\e[0m\n\n"
sleep 2

chmod +x ~/.local/share/lishalinux/bin/*
chmod +x ~/.local/share/lishalinux/default/waybar/indicators/screen-recording.sh
sleep 2

echo -e "\n\n\e[1;38;2;162;221;157m<========== Reloading Bashrc for Changes to Work ==========>\e[0m\n\n"
sleep 2

source ~/.bashrc

echo -e "\n\n\e[1;38;2;162;221;157m<========== Enable Darkmode for Gnome Applications ==========>\e[0m\n\n"
sleep 2

gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'
gsettings set org.gnome.desktop.interface icon-theme 'Yaru-purple'

echo -e "\n\n\e[1;38;2;162;221;157m<========== Installation Complete, Reboot for Changes to Work ==========>\e[0m\n\n"
sleep 2

# Ask for reboot
read -p "Would you like to reboot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Rebooting in 2 Seconds ==========>\e[0m\n\n"
  sleep 2

  sudo reboot
else

  echo -e "\n\n\e[1;38;2;162;221;157m<========== Please Reboot for Changes to Work ==========>\e[0m\n\n"
  sleep 2

fi
