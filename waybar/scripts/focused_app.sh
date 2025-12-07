#!/usr/bin/env bash

window="$(hyprctl -j activewindow)"

class=$(echo "$window" | jq -r '.class')
title=$(echo "$window" | jq -r '.title')

# Convert class to lowercase for icon lookup
appid=$(echo "$class" | tr '[:upper:]' '[:lower:]')

# Special cases (same ones Waybar handles)
case "$appid" in
firefoxdeveloperedition) appid="firefox-developer-edition" ;;
org.kde.konsole) appid="konsole" ;;
code-url-handler | code-insiders) appid="code" ;;
esac

echo "{\"text\": \"$appid\", \"tooltip\": \"$title\"}"
