#!/bin/bash
# Install base dependencies required for everything
# 2025-12-03

set -e

# Print step-specific banner
print_banner "Installing Base Dependencies"

# Install essential development tools
sudo pacman -S --needed --noconfirm base-devel git unzip
