#!/bin/bash
# Common Style and funtions go here
# 2025-12-03

set -e

print_banner() {
  local msg="$1"
  echo -e "\n\e[1;38;2;162;221;157m$msg\e[0m\n"
  sleep 2
}

# Keep sudo alive
keep_sudo_alive() {
  sudo -v
  while true; do
    sudo -n true
    sleep 60
    kill -0 "$$" || exit
  done 2>/dev/null &
}

customRepoAdd() {
  # Add repo block if missing
  if ! sudo grep -q "^\[omarchy\]" /etc/pacman.conf; then
    sudo tee -a /etc/pacman.conf >/dev/null <<'EOF'

[omarchy]
SigLevel = Optional TrustAll
Include = /etc/pacman.d/omarchy-mirrorlist
EOF
  fi

  # Create mirrorlist
  sudo tee /etc/pacman.d/omarchy-mirrorlist >/dev/null <<'EOF'
Server = https://pkgs.omarchy.org/stable/$arch
EOF

  # Sync pacman
  sudo pacman -Sy --noconfirm
}

customRepoRemove() {
  # Remove repo block safely
  if sudo grep -q "^\[omarchy\]" /etc/pacman.conf; then
    sudo sed -i '/^\[omarchy\]/,/^$/d' /etc/pacman.conf
  fi

  # Remove mirrorlist
  sudo rm -f /etc/pacman.d/omarchy-mirrorlist

  # Sync pacman
  sudo pacman -Sy --noconfirm
}
