# Arch Linux + Hyprland Personalized Setup
# Installation Documentation
# Created: 2025-12-03
# System: Arch Linux with Hyprland

## Setup initialized
# This file will document every package, configuration, and command
# for reproducing this setup on a fresh Arch + Hyprland installation

---

## Base Packages Installation
# Date: 2025-12-03

# Install essential base packages
sudo pacman -S --noconfirm git unzip alacritty

# Install yay AUR helper
cd /tmp
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si --noconfirm
cd ~

---

## Limine + Snapper Snapshot Setup (Optional)
# Date: 2025-12-03
# Only runs if Limine bootloader and Btrfs filesystem are detected

if [ -d /boot/limine ] && findmnt -n -o FSTYPE / | grep -q btrfs; then
  echo "Limine bootloader and Btrfs detected. Setting up snapper..."
  
  # Install snapper and required dependencies for limine-snapper-sync
  sudo pacman -S --noconfirm snapper btrfs-progs inotify-tools jre-openjdk-headless libnotify snap-pac rsync
  
  # Install limine-mkinitcpio-hook (automates kernel installation and Limine boot entries)
  yay -S --noconfirm limine-mkinitcpio-hook
  
  # Install limine-snapper-sync (syncs Limine snapshot entries with Snapper snapshots)
  yay -S --noconfirm limine-snapper-sync
  
  # Configure snapshot limits (only pacman update snapshots)
  sudo snapper -c root set-config "NUMBER_LIMIT=5"
  sudo snapper -c root set-config "NUMBER_LIMIT_IMPORTANT=3"
  
  # Disable timeline snapshots (only keep pacman update snapshots)
  sudo snapper -c root set-config "TIMELINE_CREATE=no"
  sudo systemctl disable --now snapper-timeline.timer
  
  # Enable and start limine-snapper-sync service
  sudo systemctl enable --now limine-snapper-sync.service
else
  echo "Limine bootloader or Btrfs not detected. Skipping snapper setup."
fi

---

## Essential Applications and Tools
# Date: 2025-12-03

# Install image viewer
sudo pacman -S --noconfirm imv

# Install media player
sudo pacman -S --noconfirm mpv

# Install terminal emulator
sudo pacman -S --noconfirm ghostty

# Install ebook reader
sudo pacman -S --noconfirm foliate

# Install neovim
sudo pacman -S --noconfirm neovim

# Install JSON processor
sudo pacman -S --noconfirm jq

# Install shell script tool
sudo pacman -S --noconfirm gum

# Install file manager
sudo pacman -S --noconfirm nautilus

# Install GVFS and MTP support
sudo pacman -S --noconfirm gvfs gvfs-mtp

# Install disk management
sudo pacman -S --noconfirm udisks2

# Install Android device support
sudo pacman -S --noconfirm android-udev

# Install bluetooth manager
sudo pacman -S --noconfirm blueberry

# Install clipboard utility
sudo pacman -S --noconfirm wl-clipboard

# Install Hyprland lock screen
sudo pacman -S --noconfirm hyprlock

# Install Hyprland idle daemon
sudo pacman -S --noconfirm hypridle

# Install Hyprland wallpaper manager
sudo pacman -S --noconfirm hyprpaper

# Install status bar (patched version with active-last feature)
# Using AUR package: waybar-active-last
# This version includes a patch that adds "active-last: true" config option
# to move the active window icon to the rightmost position in wlr-taskbar
yay -S --noconfirm waybar-active-last

# Install Wayland session manager
sudo pacman -S --noconfirm uwsm


# Install fuzzyFinder
sudo pacman -S --noconfirm fzf


# Install Cascadia Mono Nerd Font
sudo pacman -S --noconfirm ttf-cascadia-mono-nerd

# Install Brave browser from AUR
yay -S --noconfirm brave-bin

# Install LocalSend from AUR
yay -S --noconfirm localsend-bin

# Install Walker launcher and Elephant AI assistant from AUR
yay -S --noconfirm walker-bin elephant-bin elephant-providerlist-bin elephant-dektopapplicaions-bin

# Install screenshot dependencies from AUR
yay -S --noconfirm wayfreeze-git satty-git

# Setup LazyVim configuration for neovim
git clone https://github.com/LazyVim/starter ~/.config/nvim
rm -rf ~/.config/nvim/.git

---
## Additional System Utilities
# Date: 2025-12-04

# Install brightness control
sudo pacman -S --noconfirm brightnessctl

# Install color temperature adjustment
sudo pacman -S --noconfirm hyprsunset

# Install color picker
sudo pacman -S --noconfirm hyprpicker

# Install power profile management
sudo pacman -S --noconfirm power-profiles-daemon

# Install audio control
sudo pacman -S --noconfirm pamixer

## Install audio volume control GUI
sudo pacman -S --noconfirm pavucontrol

 Install Disk manager
sudo pacman -S --noconfirm gnome-disk-utility

---

## Configuration Files Setup
# Date: 2025-12-04

# Clone dotfiles repository
git clone https://github.com/USERNAME/dotfiles ~/dotfiles
cd ~/dotfiles

# Backup existing configs before replacing
[ -d ~/.config/alacritty ] && mv ~/.config/alacritty ~/.config/alacritty.backup.$(date +%s)
[ -d ~/.config/elephant ] && mv ~/.config/elephant ~/.config/elephant.backup.$(date +%s)
[ -d ~/.config/mako ] && mv ~/.config/mako ~/.config/mako.backup.$(date +%s)
[ -d ~/.config/walker ] && mv ~/.config/walker ~/.config/walker.backup.$(date +%s)
[ -d ~/.config/waybar ] && mv ~/.config/waybar ~/.config/waybar.backup.$(date +%s)
[ -d ~/.config/uwsm ] && mv ~/.config/uwsm ~/.config/uwsm.backup.$(date +%s)
[ -d ~/.config/hypr ] && mv ~/.config/hypr ~/.config/hypr.backup.$(date +%s)
[ -f ~/.config/mimeapps.list ] && mv ~/.config/mimeapps.list ~/.config/mimeapps.list.backup.$(date +%s)

# Copy configuration files to .config
cp -r alacritty elephant mako walker waybar uwsm hypr ~/.config/
cp mimeapps.list ~/.config/

# Copy desktop applications
cp -r applications/* ~/.local/share/applications/

# Copy lishalinux scripts
cp -r lishalinux ~/.local/share/

# Make lishalinux scripts executable
chmod +x ~/.local/share/lishalinux/bin/*.sh

# Install gpu-screen-recorder from AUR
yay -S --noconfirm gpu-screen-recorder

# Make waybar indicator script of gpu-screen-recorder executable
chmod +x ~/.local/share/lishalinux/default/waybar/indicators/screen-recording.sh


---
