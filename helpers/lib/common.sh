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
