#!/bin/bash
# Backup existing configs and copy Lishalinux custom configs
# 2025-12-03

set -e

print_banner "Backing Up Existing Configs"

cd $HOME/lishalinux

# Directories to backup
dirs=(ghostty swayosd elephant mako walker waybar uwsm hypr autostart applications lishalinux)
for dir in "${dirs[@]}"; do
  if [ -d $HOME/.config/"$dir" ] || [ -d $HOME/.local/share/"$dir" ]; then
    print_banner "Backing up $dir..."
    if [ -d $HOME/.config/"$dir" ]; then
      mv $HOME/.config/"$dir" $HOME/.config/"$dir".backup.$(date +%s)
    fi
    if [ -d $HOME/.local/share/"$dir" ]; then
      mv $HOME/.local/share/"$dir" $HOME/.local/share/"$dir".backup.$(date +%s)
    fi
  fi
done

# Files to backup
files=(mimeapps.list bashrc starship.toml xdg-terminals.list brave-flags.conf)
for file in "${files[@]}"; do
  if [ -f $HOME/.config/"$file" ]; then
    print_banner "Backing up $file..."
    mv $HOME/.config/"$file" $HOME/.config/"$file".backup.$(date +%s)
  elif [ -f $HOME/"$file" ]; then
    print_banner "Backing up $file..."
    mv $HOME/"$file" $HOME/"$file".backup.$(date +%s)
  fi
done

print_banner "Copying Lishalinux Custom Configs"

# Copy config directories
cp -r ghostty swayosd elephant mako walker waybar uwsm autostart hypr ~/.config/

# Copy files
cp mimeapps.list $HOME/.config/
cp starship.toml $HOME/.config/
cp bashrc $HOME/.bashrc
cp xdg-terminals.list $HOME/.config/

# Browser flags
cp brave-flags.conf $HOME/.config/

# Copy desktop applications
cp -r applications $HOME/.local/share/

# Copy Lishalinux scripts
cp -r lishalinux $HOME/.local/share/

cd $HOME
print_banner "Configs backup and copy complete."
