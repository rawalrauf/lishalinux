#!/bin/bash
# Install Walker and required Elephant packages without pulling in elephant-all
# 2025-12-03

set -e

print_banner "Installing Walker and Elephant Packages"

# List of Elephant packages we want explicitly
ELEPHANT_PKGS=(
  elephant
  elephant-bluetooth
  elephant-calc
  elephant-clipboard
  elephant-desktopapplications
  elephant-files
  elephant-menus
  elephant-providerlist
  elephant-runner
  elephant-symbols
  elephant-todo
  elephant-unicode
  elephant-websearch
)

# Install walker + Elephant subpackages, ignoring elephant-all packages
yay -S --needed --noconfirm walker "${ELEPHANT_PKGS[@]}" \
  --ignore elephant-all --ignore elephant-all-bin --ignore elephant-all-git

# Start Elephant service if not running
if ! pgrep -x elephant &>/dev/null; then
  print_banner "Starting Elephant service..."
  elephant service enable
  systemctl --user start elephant.service
fi

# Start Walker if not running
if ! pgrep -x walker &>/dev/null; then
  print_banner "Starting Walker application..."
  setsid walker --gapplication-service &
fi

print_banner "Walker and Elephant setup complete."
