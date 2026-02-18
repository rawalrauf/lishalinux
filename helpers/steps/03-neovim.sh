#!/bin/bash
# Install Neovim and setup LazyVim configuration
# 2025-12-03

set -e

print_banner "Installing Neovim and LazyVim"

# Install Neovim
sudo pacman -S --needed --noconfirm neovim

# Setup LazyVim only if not already installed
if [ -f $HOME/.config/nvim/lazyvim.json ]; then
  print_banner "LazyVim already configured, skipping backup and clone..."
else
  # Backup existing nvim config if it exists
  if [ -d $HOME/.config/nvim ]; then
    print_banner "Backing up existing Neovim config..."
    mv $HOME/.config/nvim $HOME/.config/nvim.backup.$(date +%s)
  fi

  print_banner "Cloning LazyVim starter config..."
  git clone https://github.com/LazyVim/starter $HOME/.config/nvim
  rm -rf $HOME/.config/nvim/.git
fi
