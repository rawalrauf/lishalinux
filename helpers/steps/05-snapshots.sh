#!/bin/bash
# Detect Limine, Btrfs, UEFI and setup Snapper with limine-snapper-sync
# 2025-12-03

set -e

print_banner "Detecting Limine, Btrfs & UEFI for Snapshots"

if (pacman -Q limine &>/dev/null || find /boot -name 'limine.conf' 2>/dev/null | grep -q .) &&
  findmnt -n -o FSTYPE / | grep -q btrfs && [[ -d /sys/firmware/efi ]]; then

  print_banner "Limine, Btrfs & UEFI Detected - Installing Snapshot Dependencies"

  sudo pacman -S --needed --noconfirm snapper btrfs-progs inotify-tools libnotify snap-pac rsync

  print_banner "Installing limine-snapper-sync and mkinitcpio hook..."

  # Backup existing conflicting limine.conf if detected to remove error
  [ -f /boot/limine.conf ] && [ -f /boot/limine/limine.conf ] && sudo mv /boot/limine/limine.conf /boot/limine/limine.conf.backup.$(date +%s)

  # Install via yay
  yay -S --needed --noconfirm limine-mkinitcpio-hook limine-snapper-sync

  print_banner "Configuring Snapper"

  # Configure snapshot limits
  sudo snapper -c root set-config "NUMBER_LIMIT=5"
  sudo snapper -c root set-config "NUMBER_LIMIT_IMPORTANT=3"

  # Disable timeline snapshots
  sudo snapper -c root set-config "TIMELINE_CREATE=no"
  sudo systemctl disable --now snapper-timeline.timer

  # Enable limine-snapper-sync service
  sudo systemctl enable --now limine-snapper-sync.service

  print_banner "Snapshots and Rollback Setup Complete"

else
  print_banner "Limine, Btrfs or UEFI not detected. Skipping Snapper setup..."
fi
