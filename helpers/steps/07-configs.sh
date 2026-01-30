#!/bin/bash
# Backup existing configs and copy Lishalinux custom configs
# 2025-12-03

set -e

print_banner "Backing Up Existing Configs"

cd ~/lishalinux

# Directories to backup
dirs=(ghostty swayosd elephant mako walker waybar uwsm hypr autostart applications lishalinux)
for dir in "${dirs[@]}"; do
  if [ -d ~/.config/"$dir" ] || [ -d ~/.local/share/"$dir" ]; then
    print_banner "Backing up $dir..."
    if [ -d ~/.config/"$dir" ]; then
      mv ~/.config/"$dir" ~/.config/"$dir".backup.$(date +%s)
    fi
    if [ -d ~/.local/share/"$dir" ]; then
      mv ~/.local/share/"$dir" ~/.local/share/"$dir".backup.$(date +%s)
    fi
  fi
done

# Files to backup
files=(mimeapps.list bashrc starship.toml xdg-terminals.list brave-flags.conf)
for file in "${files[@]}"; do
  if [ -f ~/.config/"$file" ]; then
    print_banner "Backing up $file..."
    mv ~/.config/"$file" ~/.config/"$file".backup.$(date +%s)
  elif [ -f ~/"$file" ]; then
    print_banner "Backing up $file..."
    mv ~/"$file" ~/"$file".backup.$(date +%s)
  fi
done

print_banner "Copying Lishalinux Custom Configs"

# Copy config directories
cp -r ghostty swayosd elephant mako walker waybar uwsm autostart hypr ~/.config/

# Copy files
cp mimeapps.list ~/.config/
cp starship.toml ~/.config/
cp bashrc ~/.bashrc
cp xdg-terminals.list ~/.config/

# Browser flags
cp brave-flags.conf ~/.config/

# Copy desktop applications
cp -r applications ~/.local/share/

# Copy Lishalinux scripts
cp -r lishalinux ~/.local/share/

cd ~
print_banner "Configs backup and copy complete."
