# LishaLinux

A personalized Arch Linux + Hyprland setup with curated dotfiles.

## Requirements

- **Works Best With Fresh Arch Install (via archinstall sript)**
- **Boost System** - UEFI
- **Hyprland** installed
- **SDDM** display manager
- **UWSM-managed Hyprland session** (Already configured if you select hyprland+SSDM during archinstall script)
- **Audio** pipewire

### Optional (If You Want Snapshot Rollbacks)
- **Limine bootloader** - For snapshot boot menu integration
- **UKI** (Unified Kernal Image) Enabled
- **Btrfs filesystem** - For automatic snapshots and system recovery
- **Snapshots** Snapper
  
## Installation

```bash
git clone https://github.com/rawalrauf/lishalinux.git
cd lishalinux
chmod +x install.sh
./install.sh
```

## Post-Installation

After reboot:
- Log in to Hyprland (UWSM) session from SDDM
- `Super + Alt + Space` - Main Menu
- `Super + Return` - Open terminal
- `Super + K` - Open KeyBindings



