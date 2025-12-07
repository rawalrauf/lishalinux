#!/bin/bash

# Fast App Launcher for Hyprland
# Usage: ./fast_app_launcher.sh <app_class|new> <workspace> <launch_command> [app_parameters...]
# Special: Use "new" as app_class to always launch a new instance
# Examples: ./fast_app_launcher.sh firefox 2 firefox -new-tab https://youtube.com
#          ./fast_app_launcher.sh new 2 firefox --private-window

APP_CLASS="$1"
WORKSPACE="$2"
LAUNCH_CMD="$3"

# Shift to get all remaining parameters as app arguments
shift 3
APP_PARAMS="$@"

# Build full command with parameters
if [[ -n "$APP_PARAMS" ]]; then
    FULL_CMD="$LAUNCH_CMD $APP_PARAMS"
else
    FULL_CMD="$LAUNCH_CMD"
fi

# Function to wait for window and focus it
wait_and_focus() {
    local class_to_focus="$1"
    local max_attempts=10
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        sleep 0.5
        if hyprctl dispatch focuswindow "class:^${class_to_focus}$" 2>/dev/null; then
            echo "Window focused successfully"
            return 0
        fi
        ((attempt++))
    done

    echo "Could not focus window after $max_attempts attempts"
    return 1
}

# Check if user wants to force a new instance
if [[ "$APP_CLASS" == "new" ]]; then
    # Skip window detection, always launch new instance
    echo "Launching new instance: $FULL_CMD"
    nohup $FULL_CMD >/dev/null 2>&1 &

    # Wait for window to appear and focus it - try common class patterns
    wait_and_focus "$LAUNCH_CMD" || \
    wait_and_focus "${LAUNCH_CMD,,}" || \
    wait_and_focus "${LAUNCH_CMD^}"
else
    # Try to focus existing window first - check if window exists
    FOCUS_RESULT=$(hyprctl dispatch focuswindow "class:^${APP_CLASS}$" 2>&1)

    if [[ "$FOCUS_RESULT" == *"No such window found"* ]]; then
        # Window doesn't exist, launch app and switch to workspace
        echo "Launching $FULL_CMD"
        nohup $FULL_CMD >/dev/null 2>&1 &

        # Wait for window to appear and focus it
        wait_and_focus "$APP_CLASS"
    else
        # Window exists and was focused
        # If parameters are provided, execute them (useful for opening new tabs, etc.)
        if [[ -n "$APP_PARAMS" ]]; then
            echo "Executing with parameters: $FULL_CMD"
            nohup $FULL_CMD >/dev/null 2>&1 &
        fi
    fi
fi

# Always ensure we're on the correct workspace
hyprctl dispatch workspace "$WORKSPACE" >/dev/null 2>&1
