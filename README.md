# LishaLinux

A personalized Arch Linux + Hyprland setup with curated dotfiles and automated installation.

## What is LishaLinux?

LishaLinux is a complete desktop environment configuration for **Arch Linux + Hyprland** with UWSM session management. It provides a modern, efficient Wayland desktop experience with custom scripts and optimized configurations.

**Note:** More features are being added regularly!

## Requirements

- **Fresh Arch Linux installation**
- **Hyprland** installed
- **SDDM** display manager
- **UWSM-managed Hyprland session** (required)

### Optional (Recommended)
- **Limine bootloader** - For snapshot boot menu integration
- **Btrfs filesystem** - For automatic snapshots and system recovery

## Verify UWSM Session

Check if you're running UWSM-managed Hyprland:
```bash
echo $WAYLAND_DISPLAY
uwsm check may-start
```

If you're running plain Hyprland session (not UWSM), add UWSM-managed session:
```bash
sudo pacman -S uwsm
uwsm select
```

Then select "Hyprland" from SDDM login screen.

## Installation

```bash
git clone https://github.com/rawalrauf/lishalinux.git
cd lishalinux
chmod +x install.sh
./install.sh
```

The script will:
- Install all packages (official repos + AUR)
- Setup Snapper snapshots (if Limine + Btrfs detected)
- Copy configuration files
- Prompt for reboot

**Note:** You'll only enter sudo password once.

## What Gets Installed?

- **Core**: Hyprland ecosystem, terminals, editors, browsers
- **System**: Audio, Bluetooth, network, power management tools
- **Productivity**: Screenshot, screen recording, file sharing tools
- **AUR**: yay, brave-bin, walker-bin, elephant-bin, localsend-bin, gpu-screen-recorder, and more

### Waybar Patch

We use `waybar-active-last` (patched version) which adds the `"active-last": true` config option to move the active window icon to the rightmost position in wlr-taskbar. This will be used until the official Waybar includes this feature.

## Snapper Snapshots (Optional)

If you have **Limine + Btrfs**, the script automatically sets up:
- Automatic snapshots on package updates
- Boot menu integration for easy system recovery
- Snapshot limits: 5 regular + 3 important

## Post-Installation

After reboot:
- Log in to Hyprland (UWSM) session from SDDM
- `Super + Return` - Open terminal
- `Super + Space` - Open Walker launcher
- Check keybindings: `~/.config/hypr/bindings.conf`

## Updating

```bash
cd ~/lishalinux
git pull
./install.sh
```

## Credits

Created by Rawal Rauf
