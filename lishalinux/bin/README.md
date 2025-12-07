# LishaLinux Setup Guide

## Overview
This guide explains how to set up the lishalinux configuration system after copying files from the source distro. The lishalinux system provides a comprehensive Hyprland desktop environment with session management through uwsm.

## Prerequisites / Required Packages

Install these packages before proceeding:

```bash
# Core packages
sudo pacman -S jq walker uwsm hyprland alacritty

# Additional dependencies (adjust for your distro)
sudo pacman -S sddm waybar hypridle hyprlock
```

## Initial Setup Steps

### 1. Copy Source Files
Ensure you have copied the lishalinux files to:
- `~/.local/share/lishalinux/bin/` - All lishalinux scripts
- `~/.local/share/lishalinux/config/` - Source configuration files  
- `~/.local/share/lishalinux/default/` - Default configurations

### 2. Make Scripts Executable
```bash
cd ~/.local/share/lishalinux/bin/
chmod +x *
```

### 3. Set Up uwsm Environment
Copy the uwsm configuration:
```bash
# Copy uwsm configs if not already present
cp ~/.local/share/lishalinux/config/uwsm/* ~/.config/uwsm/
```

### 4. Create uwsm-managed Hyprland Session
The key to making lishalinux work is using uwsm to manage the Hyprland session:

```bash
# Create the uwsm session file (if not already present)
sudo tee /usr/share/wayland-sessions/hyprland-uwsm.desktop > /dev/null << 'EOF'
[Desktop Entry]
Name=Hyprland (uwsm-managed)
Comment=An intelligent dynamic tiling Wayland compositor
Exec=uwsm start -- hyprland.desktop
TryExec=uwsm
DesktopNames=Hyprland
Type=Application
EOF
```

### 5. Switch to uwsm Session
1. **Logout** of your current session
2. **At login screen**, select session type
3. **Choose:** "Hyprland (uwsm-managed)" instead of regular "Hyprland"
4. **Login**

## How It Works

### The uwsm → bin Connection
The lishalinux system works through this flow:

1. **uwsm session** starts Hyprland with proper environment
2. **Environment variables** are set automatically:
   - `LISHALINUX_PATH=/home/$USER/.local/share/lishalinux`
   - `PATH` includes `$LISHALINUX_PATH/bin`
3. **All lishalinux scripts** become available globally in terminals
4. **Hyprland keybindings** use `uwsm-app --` for session management

### Key Environment Variables
```bash
# These are set automatically by uwsm
LISHALINUX_PATH=/home/$USER/.local/share/lishalinux
PATH=$LISHALINUX_PATH/bin:$PATH
TERMINAL=alacritty
```

## Testing the Setup

After logging into the uwsm-managed session:

```bash
# Test environment variables
echo "LISHALINUX_PATH: $LISHALINUX_PATH"
echo "TERMINAL: $TERMINAL"

# Test script availability
which lishalinux-menu-keybindings
lishalinux-menu-keybindings

# Test terminal keybinding
# Press SUPER + RETURN (should open alacritty via uwsm)
```

## Keybindings

Key terminal keybinding that should work:
- `SUPER + RETURN` - Opens terminal via uwsm session management

## Troubleshooting

### "Command not found" errors
- **Cause:** Not using uwsm-managed session
- **Solution:** Logout and select "Hyprland (uwsm-managed)" at login

### "linuxINAL" errors  
- **Cause:** Environment variables not available to Hyprland
- **Solution:** Ensure using uwsm-managed session, not direct Hyprland

### Scripts work with `./` but not globally
- **Cause:** PATH not set up correctly
- **Solution:** Verify uwsm environment with `echo $LISHALINUX_PATH`

## Architecture

```
Login Manager (SDDM) 
    ↓
uwsm start -- hyprland.desktop
    ↓ 
Hyprland (with uwsm environment)
    ↓
Applications via uwsm-app (inherit environment)
    ↓
All lishalinux scripts available globally
```

## Source vs Your Setup

- **Source Distro:** Uses uwsm-managed session by default
- **Your Setup:** Must manually select uwsm-managed session at login
- **Result:** Identical functionality once uwsm session is active

## Desktop Environment Integration

### Critical: Application Desktop Files
After setting up the uwsm session, you MUST copy the lishalinux application files to get proper desktop integration:

```bash
# Copy all lishalinux application files
cp ~/Downloads/lishalinux_file/lishalinux/applications/*.desktop ~/.local/share/applications/
cp ~/Downloads/lishalinux_file/lishalinux/applications/hidden/*.desktop ~/.local/share/applications/
cp -r ~/Downloads/lishalinux_file/lishalinux/applications/icons ~/.local/share/applications/

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

**Why This is Critical:**
- **nvim.desktop** uses `lishalinux-launch-editor` instead of system terminal selection
- **Fixes terminal issues:** nvim opens in correct terminal (alacritty) not random terminal (ghostty)
- **Proper uwsm integration:** Uses lishalinux scripts for launching applications
- **Same behavior as source:** Exact same desktop experience

### Common Desktop Integration Issues

#### Issue: nvim/vim Opens in Wrong Terminal
**Symptoms:**
- nvim opens in ghostty instead of alacritty when launched from file manager
- System ignores `$TERMINAL` environment variable
- gsettings terminal preferences don't work

**Root Cause:**
- Missing custom `nvim.desktop` file that uses `lishalinux-launch-editor`
- System uses default nvim.desktop with `Terminal=true` which picks arbitrary terminal

**Solution:**
```bash
# Copy the lishalinux nvim.desktop file
cp ~/Downloads/lishalinux_file/lishalinux/applications/nvim.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

**The lishalinux nvim.desktop uses:**
- `Exec=lishalinux-launch-editor %F` (not `nvim %F`)
- `Terminal=false` (handles terminal internally)
- `lishalinux-launch-editor` detects terminal-based editors and launches them via uwsm

#### Issue: Application Files Not Working
**Symptoms:**
- lishalinux scripts not found globally
- Terminal keybindings not working
- Environment variables not set

**Root Cause:**
- Not using uwsm-managed Hyprland session
- Using regular Hyprland instead of `Hyprland (uwsm-managed)`

**Solution:**
- Always login with "Hyprland (uwsm-managed)" session
- Logout and select correct session at login screen

## File Structure

Your final structure should match:

```
~/.local/share/lishalinux/
├── bin/                    # All lishalinux scripts (executable)
├── config/                 # Source configuration files
└── default/               # Default configurations

~/.local/share/applications/
├── *.desktop              # All application files (including hidden)
└── icons/                 # Web application icons

~/.config/
├── hypr/                  # Your Hyprland configuration
├── uwsm/                  # uwsm configuration (copied from source)
└── mimeapps.list          # Application associations
```

## Troubleshooting Desktop Issues

### Problem: Wrong Terminal Application
1. Check if using uwsm session: `echo $LISHALINUX_PATH`
2. Verify custom desktop files: `ls ~/.local/share/applications/nvim.desktop`
3. Test lishalinux-launch-editor: `lishalinux-launch-editor /tmp/test.txt`

### Problem: Applications Not in Menu
1. Update desktop database: `update-desktop-database ~/.local/share/applications/`
2. Check desktop file syntax
3. Restart desktop environment

### Important Lessons Learned

1. **Always check lishalinux/bin first** - Don't create custom scripts, use existing lishalinux infrastructure
2. **Desktop files are critical** - Copy ALL application files from source, not just configs
3. **Directory structure matters** - Icons go in `applications/icons/`, not separate `icons/` directory
4. **uwsm session is required** - Regular Hyprland session won't work properly
5. **Use lishalinux scripts** - `lishalinux-launch-editor`, `lishalinux-launch-terminal`, etc.

## Next Steps

With the complete setup working:
1. **Clean up applications:** Remove unwanted `.desktop` files from `~/.local/share/applications/`
2. **Customize lishalinux scripts:** Keep only the scripts you need from `~/.local/share/lishalinux/bin/`
3. **Modify keybindings:** Adjust `~/.config/hypr/binds.conf` as needed
4. **Configure defaults:** Modify `~/.config/uwsm/default` for your preferences

---

**Important:** Always use the "Hyprland (uwsm-managed)" session and copy ALL lishalinux application files for full functionality!