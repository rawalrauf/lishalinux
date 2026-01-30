#!/bin/bash
# Prompt for optional system reboot
# 2025-12-03

set -e

print_banner "Installation finished! You may reboot to apply all changes"

read -p "Would you like to reboot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  print_banner "Rebooting Now..."
  sudo reboot
else
  print_banner "Please reboot manually for all changes to take effect."
fi
