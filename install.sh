#!/bin/bash
# Lishalinux Full Installer (Modular)
# Sources modular scripts to install full system setup
# 2025-12-03

set -e

# Path to modular steps and lib
STEP_DIR="$HOME/lishalinux/helpers/steps"
LIB_DIR="$HOME/lishalinux/helpers/lib"

source "$LIB_DIR/common.sh"
print_banner "<========== Lishalinux Installer ==========>"
keep_sudo_alive

# Step 0: Install core dependencies
source "$STEP_DIR/00-base.sh"

# Step 1: Install AUR helper: yay
source "$STEP_DIR/01-aur.sh"

# Step 2: Install required Pacman packages
source "$STEP_DIR/02-pacman-apps.sh"

# Step 3: Install Neovim + LazyVim if not already setup
source "$STEP_DIR/03-neovim.sh"

# Step 4: Install AUR packages
source "$STEP_DIR/04-aur-apps.sh"

# Step 5: Limine + Snapper snapshot setup (optional based on UEFI/Btrfs detection)
source "$STEP_DIR/05-snapshots.sh"

# Step 6: Install Walker + Elephant packages and start services
source "$STEP_DIR/06-walker.sh"

# Step 7: Backup existing configs and copy Lishalinux custom configs
source "$STEP_DIR/07-configs.sh"

# Step 8: Make all scripts executable
source "$STEP_DIR/08-permissions.sh"

# Step 9: Set Gnome dark mode + GTK + icon themes
source "$STEP_DIR/09-theme.sh"

# Step 10: Prompt for reboot
source "$STEP_DIR/10-reboot.sh"
