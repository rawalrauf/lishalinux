#!/usr/bin/env python3
import time

start_time = time.time()

import gi
import sys
import subprocess
import signal
import os
import re

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gtk4LayerShell

signal.signal(signal.SIGINT, lambda *a: sys.exit(0))


def get_bluetooth_status():
    """Get bluetooth power status"""
    try:
        result = subprocess.run(
            ["bluetoothctl", "show"], capture_output=True, text=True, timeout=1
        )
        return "Powered: yes" in result.stdout
    except:
        return False


def get_bluetooth_devices():
    """Get all paired Bluetooth devices (connected and disconnected)"""
    try:
        devices = []

        # Get all paired devices first
        paired_result = subprocess.run(
            ["bluetoothctl", "devices", "Paired"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        # Get connected devices to mark connection status
        connected_result = subprocess.run(
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        connected_macs = set()
        for line in connected_result.stdout.strip().split("\n"):
            if line.startswith("Device"):
                parts = line.split(" ", 2)
                if len(parts) >= 2:
                    connected_macs.add(parts[1])

        # Process all paired devices
        for line in paired_result.stdout.strip().split("\n"):
            if line.startswith("Device"):
                parts = line.split(" ", 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    is_connected = mac in connected_macs

                    devices.append(
                        {
                            "mac": mac,
                            "name": name,
                            "connected": is_connected,
                            "paired": True,
                        }
                    )

        return devices[:10]  # Show up to 10 devices
    except:
        return []


def get_network_connections():
    """Get all available WiFi networks and active connections"""
    try:
        connections = []

        # Get active connections first
        active_result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        active_connections = {}
        for line in active_result.stdout.strip().split("\n"):
            if line and ":" in line:
                parts = line.split(":")
                if len(parts) >= 3:
                    name = parts[0]
                    conn_type = parts[1]
                    device = parts[2]
                    active_connections[name] = {"type": conn_type, "device": device}

        # Add active wired connections first (ethernet, USB tethering, etc.)
        for name, info in active_connections.items():
            if any(
                wired_type in info["type"].lower()
                for wired_type in [
                    "802-3-ethernet",
                    "ethernet",
                    "tethering",
                    "usb",
                    "gsm",
                    "cdma",
                ]
            ):
                # Determine display name based on connection type
                if "tethering" in info["type"].lower() or "usb" in info["type"].lower():
                    display_name = "USB Tethering"
                elif "gsm" in info["type"].lower() or "cdma" in info["type"].lower():
                    display_name = "Mobile Data"
                else:
                    display_name = "Wired"

                connections.append(
                    {
                        "name": display_name,
                        "real_name": name,
                        "type": "wired",
                        "connected": True,
                        "device": info["device"],
                    }
                )

        # Get ALL available WiFi networks (not just connected)
        try:
            wifi_result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            seen_networks = set()

            for line in wifi_result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(":")
                    if len(parts) >= 2 and parts[0] and parts[0] not in seen_networks:
                        network_name = parts[0]
                        is_connected = (
                            network_name in active_connections
                            and "802-11-wireless"
                            in active_connections[network_name]["type"]
                        )

                        connections.append(
                            {
                                "name": network_name,
                                "type": "wifi",
                                "signal": parts[1] if len(parts) > 1 else "0",
                                "secure": "secured"
                                if len(parts) > 2 and parts[2]
                                else "open",
                                "connected": is_connected,
                                "device": active_connections.get(network_name, {}).get(
                                    "device", ""
                                ),
                            }
                        )
                        seen_networks.add(network_name)
        except:
            pass

        return connections[:15]  # Show up to 15 networks
    except:
        return []


def get_network_status():
    """Get current network status - shows enabled/disabled state based on WiFi radio"""
    try:
        # Check WiFi radio state as main indicator
        wifi_result = subprocess.run(
            ["nmcli", "radio", "wifi"], capture_output=True, text=True, timeout=1
        )
        wifi_enabled = "enabled" in wifi_result.stdout

        if not wifi_enabled:
            return {
                "connected": False,
                "name": "Disabled",
                "type": "disabled",
                "icon": "󰤭",
            }

        # WiFi radio is enabled, check for active connections
        active_result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show", "--active"],
            capture_output=True,
            text=True,
            timeout=1,
        )

        for line in active_result.stdout.strip().split("\n"):
            if line and ":" in line:
                parts = line.split(":")
                if len(parts) >= 3:
                    conn_type = parts[1]
                    conn_name = parts[0]
                    # Check for wired connections (ethernet, USB tethering, mobile data)
                    if any(
                        wired_type in conn_type.lower()
                        for wired_type in [
                            "802-3-ethernet",
                            "ethernet",
                            "tethering",
                            "usb",
                            "gsm",
                            "cdma",
                        ]
                    ):
                        # Determine display name and icon based on connection type
                        if (
                            "tethering" in conn_type.lower()
                            or "usb" in conn_type.lower()
                        ):
                            return {
                                "connected": True,
                                "name": "USB Tethering",
                                "type": "wired",
                                "icon": "󰑐",
                            }
                        elif "gsm" in conn_type.lower() or "cdma" in conn_type.lower():
                            return {
                                "connected": True,
                                "name": "Mobile Data",
                                "type": "wired",
                                "icon": "󰑴",
                            }
                        else:
                            return {
                                "connected": True,
                                "name": "Wired",
                                "type": "wired",
                                "icon": "󰈀",
                            }
                    elif "802-11-wireless" in conn_type:
                        return {
                            "connected": True,
                            "name": conn_name,
                            "type": "wifi",
                            "icon": "󰖩",
                        }

        # WiFi radio enabled but no active connections
        return {"connected": True, "name": "Network", "type": "enabled", "icon": "󰖩"}
    except:
        return {"connected": False, "name": "Unknown", "type": "none", "icon": "󰤭"}


# Inline module configuration for no import overhead
MODULES_CONFIG = {
    "header_modules": [
        {
            "id": "settings",
            "icon": "󰒓",
            "command": "gnome-control-center",
            "position": "right",
        },
        {"id": "lock", "icon": "󰌾", "command": "hyprlock", "position": "right"},
        {
            "id": "power",
            "icon": "󰐥",
            "command": "systemctl poweroff",
            "position": "right",
            "css_class": "power-button",
            "expandable": True,
            "expand_data": {
                "type": "static_options",
                "options": [
                    {"icon": "󰜉", "label": "Restart", "command": "systemctl reboot"},
                    {"icon": "󰒲", "label": "Sleep", "command": "systemctl suspend"},
                    {
                        "icon": "󰍃",
                        "label": "Logout",
                        "command": "hyprctl dispatch exit",
                    },
                ],
            },
        },
    ],
    "capsule_modules": [
        {
            "row": 1,
            "modules": [
                {
                    "id": "wifi",
                    "icon": "󰢿",
                    "title": "Network",
                    "subtitle": "",
                    "get_active": lambda: get_network_status()["connected"],
                    "expandable": True,
                    "expand_data": {
                        "type": "dynamic_list",
                        "get_data": get_network_connections,
                        "template": "network_list",
                    },
                },
                {
                    "id": "bluetooth",
                    "icon": "󰂯",
                    "title": "Bluetooth",
                    "subtitle": "",
                    "get_active": lambda: get_bluetooth_status(),
                    "expandable": True,
                    "expand_data": {
                        "type": "dynamic_list",
                        "get_data": get_bluetooth_devices,
                        "template": "device_list",
                    },
                },
            ],
        },
        {
            "row": 2,
            "modules": [
                {
                    "id": "power_saver",
                    "icon": "󰁹",
                    "title": "Power Saver",
                    "subtitle": "",
                    "get_active": lambda: "power-saver"
                    in subprocess.run(
                        ["powerprofilesctl", "get"],
                        capture_output=True,
                        text=True,
                        timeout=1,
                    ).stdout.strip(),
                },
                {
                    "id": "night_light",
                    "icon": "󰖔",
                    "title": "Night Light",
                    "subtitle": "",
                    "get_active": lambda: subprocess.run(
                        ["pgrep", "hyprsunset"], capture_output=True, timeout=1
                    ).returncode
                    == 0,
                },
            ],
        },
    ],
}


class WaybarMenu:
    def __init__(self):
        self.app = Gtk.Application(application_id="com.waybar.menu")
        self.app.connect("activate", self.on_activate)
        self.expanded_sections = set()
        self.refresh_states()
        self.load_config()
        self.window = None
        self.main_box = None
        self.refresh_timer_id = None

    def start_refresh_timer(self):
        """Start periodic refresh for real-time updates"""
        if self.refresh_timer_id:
            GLib.source_remove(self.refresh_timer_id)
        # Refresh every 5 seconds for real-time updates
        # No auto-refresh timer - completely manual updates only

    def stop_refresh_timer(self):
        """Stop periodic refresh"""
        if self.refresh_timer_id:
            GLib.source_remove(self.refresh_timer_id)
            self.refresh_timer_id = None

    def periodic_refresh(self):
        """Simple periodic refresh - just rebuild UI with fresh data"""
        try:
            self.rebuild_ui()
            return True  # Continue the timer
        except:
            return True  # Continue even if there's an error

    def load_config(self):
        """Load module configuration from Python file"""
        self.config = MODULES_CONFIG

    def refresh_states(self):
        # No cached states - all data is fetched fresh from system calls
        pass

    def handle_slider_toggle(self, module_id, active):
        """Handle toggle slider changes"""
        try:
            if module_id == "wifi":
                if active:
                    subprocess.run(["nmcli", "radio", "wifi", "on"], timeout=2)
                else:
                    subprocess.run(["nmcli", "radio", "wifi", "off"], timeout=2)
            elif module_id == "bluetooth":
                if active:
                    subprocess.run(["bluetoothctl", "power", "on"], timeout=2)
                else:
                    subprocess.run(["bluetoothctl", "power", "off"], timeout=2)

            # Immediately rebuild UI to reflect slider change
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def toggle_expand_section(self, module_id):
        """Toggle expand section - always show fresh data"""
        if module_id in self.expanded_sections:
            self.expanded_sections.remove(module_id)
        else:
            self.expanded_sections.clear()
            self.expanded_sections.add(module_id)

        self.rebuild_ui()

    def refresh_expand_section(self, module_id):
        """Refresh expand section with fresh data"""
        self.rebuild_ui()

    def on_activate(self, app):
        self.create_main_window()

    def create_main_window(self):
        self.window = Gtk.ApplicationWindow(application=self.app)
        self.window.set_title("waybar-menu")
        self.window.set_default_size(-1, -1)  # Fixed height to prevent bounce
        self.window.set_resizable(False)
        self.window.set_decorated(False)

        # Make window background transparent
        self.window.add_css_class("main-container-window")

        Gtk4LayerShell.init_for_window(self.window)
        Gtk4LayerShell.set_layer(self.window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.RIGHT, True)
        # Don't anchor bottom - allow downward expansion
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.BOTTOM, False)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.TOP, 10)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.RIGHT, 10)
        Gtk4LayerShell.set_keyboard_mode(
            self.window, Gtk4LayerShell.KeyboardMode.ON_DEMAND
        )

        self.load_css()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.add_css_class("main-container")

        self.rebuild_ui()
        self.window.set_child(self.main_box)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.window.add_controller(key_controller)

        self.create_click_overlay()

        # Connect close event to stop timer
        self.window.connect("close-request", self.on_window_close)

        # Start real-time refresh timer
        self.start_refresh_timer()

        GLib.idle_add(self.present_and_focus)

    def on_window_close(self, window):
        """Handle window close event"""
        self.stop_refresh_timer()
        return False  # Allow window to close

    def rebuild_ui(self):
        """Full rebuild for initial setup"""
        self.refresh_states()

        child = self.main_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.main_box.remove(child)
            child = next_child

        header = self.create_header()
        self.main_box.append(header)

        sliders = self.create_sliders_section()
        self.main_box.append(sliders)

        modules = self.create_modules_section()
        self.main_box.append(modules)

    def update_modules_only(self):
        """Update only the modules section without rebuilding everything"""
        self.refresh_states()

        # Find and remove only the modules section
        child = self.main_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            css_classes = (
                child.get_css_classes() if hasattr(child, "get_css_classes") else []
            )
            if "modules-section" in css_classes:
                self.main_box.remove(child)
                break
            child = next_child

        # Add new modules section
        modules = self.create_modules_section()
        self.main_box.append(modules)

    def create_capsule_module(
        self,
        icon,
        title,
        subtitle,
        active,
        module_id,
        has_submenu=False,
        expandable_id=None,
    ):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        # Single button - whole button clickable
        button = Gtk.Button()
        button.add_css_class("capsule-module")

        # DEBUG: Print active state
        print(f"DEBUG: Module {module_id} - Active: {active}")

        if active:
            button.add_css_class("active-module")
            print(f"DEBUG: Added active-module class to {module_id}")

        # Button content
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.START)
        button_box.set_valign(Gtk.Align.CENTER)

        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("module-icon")
        button_box.append(icon_label)

        # Title
        if title:
            title_label = Gtk.Label(label=title)
            title_label.add_css_class("module-title")
            title_label.set_hexpand(True)
            title_label.set_halign(Gtk.Align.START)
            button_box.append(title_label)

        button.set_child(button_box)

        # Click handler
        button.connect("clicked", lambda b: self.handle_module_click(module_id))

        container.append(button)

        return container

    def create_modules_section(self):
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section_box.add_css_class("modules-section")

        # Create rows from JSON config
        for row_config in self.config.get("capsule_modules", []):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.set_homogeneous(True)

            for module_config in row_config.get("modules", []):
                module_widget = self.create_module_from_config(module_config)
                row.append(module_widget)

            section_box.append(row)

            # Add expanded sections for this row (lazy loading)
            for module_config in row_config.get("modules", []):
                if (
                    module_config.get("expandable")
                    and module_config["id"] in self.expanded_sections
                ):
                    # Always create fresh expand section - no caching
                    expand_section = self.create_expanded_from_config(module_config)
                    section_box.append(expand_section)

        return section_box

    def create_module_from_config(self, config):
        """Create a module widget from config"""
        # Get dynamic values
        subtitle = ""
        if "get_subtitle" in config:
            try:
                subtitle = config["get_subtitle"]()
            except:
                subtitle = config.get("subtitle", "")
        else:
            subtitle = config.get("subtitle", "")

        active = False
        if "get_active" in config:
            try:
                active = config["get_active"]()
            except:
                active = config.get("active", False)
        else:
            active = config.get("active", False)

        # Get dynamic icon
        icon = config.get("icon", "󰋙")
        if "get_icon" in config:
            try:
                icon = config["get_icon"]()
            except:
                icon = config.get("icon", "󰋙")

        return self.create_capsule_module(
            icon,
            config["title"],
            subtitle,
            active,
            config["id"],
            config.get("expandable", False),
            config.get("expand_id", config["id"]),
        )

    def create_expanded_from_config(self, config):
        """Create clean expanded section matching reference design"""
        expanded_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        expanded_box.add_css_class("expanded-section")
        expanded_box.add_css_class(f"{config['id']}-section")

        # Top header row: Round icon + title on left, toggle slider on right
        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_row.add_css_class("expand-header-row")

        # Left side: Round icon + title
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        # Round icon container
        icon_container = Gtk.Box()
        icon_container.add_css_class("round-icon-container")

        module_id = config["id"]
        if module_id == "wifi":
            icon_label = Gtk.Label(label="")  # WiFi icon
        elif module_id == "bluetooth":
            icon_label = Gtk.Label(label="󰂯")  # Bluetooth icon
        else:
            icon_label = Gtk.Label(label="󰋙")  # Default icon

        icon_label.add_css_class("round-icon")
        icon_container.append(icon_label)
        left_box.append(icon_container)

        # Title
        title_label = Gtk.Label(label=config["title"])
        title_label.add_css_class("expand-title")
        left_box.append(title_label)

        header_row.append(left_box)

        # Right side: Toggle slider
        toggle_slider = Gtk.Switch()
        toggle_slider.add_css_class("toggle-slider")

        # Set initial state
        if module_id == "wifi":
            toggle_slider.set_active(get_network_status()["connected"])
        elif module_id == "bluetooth":
            toggle_slider.set_active(get_bluetooth_status())

        toggle_slider.connect(
            "notify::active",
            lambda s, p: self.handle_slider_toggle(module_id, s.get_active()),
        )
        header_row.append(toggle_slider)

        expanded_box.append(header_row)

        # Device list section
        expand_data = config.get("expand_data", {})
        expand_type = expand_data.get("type", "static")

        if expand_type == "dynamic_list":
            try:
                data_list = expand_data["get_data"]()
                for item in data_list:
                    item_widget = self.create_clean_list_item(item, config["id"])
                    expanded_box.append(item_widget)
            except Exception:
                pass  # Silently handle errors

        elif expand_type == "static_options":
            # Power menu options
            for option in expand_data.get("options", []):
                option_widget = self.create_clean_power_item(option)
                expanded_box.append(option_widget)

        # Bottom footer row: Settings button on left, refresh icon on right
        if config["id"] in ["bluetooth", "wifi"]:
            footer_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            footer_row.add_css_class("expand-footer-row")

            # Settings button
            settings_btn = Gtk.Button()
            settings_btn.add_css_class("settings-button")

            if module_id == "bluetooth":
                settings_label = Gtk.Label(label="Bluetooth Settings")
                settings_btn.connect("clicked", lambda b: self.open_blueberry())
            else:
                settings_label = Gtk.Label(label="Network Settings")
                settings_btn.connect("clicked", lambda b: self.open_nmtui())

            settings_label.add_css_class("settings-label")
            settings_btn.set_child(settings_label)
            footer_row.append(settings_btn)

            # Spacer to push refresh to right
            spacer = Gtk.Box()
            spacer.set_hexpand(True)
            footer_row.append(spacer)

            # Refresh icon button
            refresh_btn = Gtk.Button()
            refresh_btn.add_css_class("refresh-icon-button")

            refresh_icon = Gtk.Label(label="󰑐")  # Nerd font refresh icon
            refresh_icon.add_css_class("refresh-icon")
            refresh_btn.set_child(refresh_icon)
            refresh_btn.connect(
                "clicked", lambda b: self.refresh_expand_section(module_id)
            )

            footer_row.append(refresh_btn)
            expanded_box.append(footer_row)

        return expanded_box

    def create_clean_list_item(self, item, module_id):
        """Create clean list item with dynamic connect/disconnect buttons"""
        item_btn = Gtk.Button()
        item_btn.add_css_class("clean-list-item")
        print(f"DEBUG: Created button with classes: {item_btn.get_css_classes()}")

        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        if module_id == "wifi":
            # Network name with type indicator
            conn_type = item.get("type", "unknown")
            name = item.get("name", "Unknown")

            # Just show the network name without icon or signal strength
            display_name = name

            name_label = Gtk.Label(label=display_name)
            name_label.set_halign(Gtk.Align.START)
            name_label.set_hexpand(True)
            name_label.add_css_class("device-name")
            item_box.append(name_label)

            # Dynamic connect/disconnect button
            if item.get("connected", False):
                connect_label = Gtk.Label(label="Disconnect")
                connect_label.add_css_class("disconnect-button")
                # Add click handler for disconnect
                if conn_type == "wired":
                    real_name = item.get("real_name", item["name"])
                    item_btn.connect(
                        "clicked", lambda b: self.disconnect_wired(real_name)
                    )
                else:
                    item_btn.connect(
                        "clicked", lambda b: self.disconnect_wifi(item["name"])
                    )
            else:
                connect_label = Gtk.Label(label="Connect")
                connect_label.add_css_class("connect-button")
                # Add click handler for connect
                if conn_type == "wired":
                    real_name = item.get("real_name", item["name"])
                    item_btn.connect("clicked", lambda b: self.connect_wired(real_name))
                else:
                    item_btn.connect(
                        "clicked",
                        lambda b: self.connect_wifi_with_fallback(item["name"]),
                    )

            item_box.append(connect_label)

        elif module_id == "bluetooth":
            # Device name on left (no icon)
            name_label = Gtk.Label(label=item.get("name", "Unknown Device"))
            name_label.set_halign(Gtk.Align.START)
            name_label.set_hexpand(True)
            name_label.add_css_class("device-name")
            item_box.append(name_label)

            # Dynamic connect/disconnect/pair button
            if item.get("connected", False):
                connect_label = Gtk.Label(label="Disconnect")
                connect_label.add_css_class("disconnect-button")
                # Add click handler for disconnect
                item_btn.connect(
                    "clicked", lambda b: self.disconnect_bluetooth(item["mac"])
                )
            elif item.get("paired", True):
                connect_label = Gtk.Label(label="Connect")
                connect_label.add_css_class("connect-button")
                # Add click handler for connect
                item_btn.connect(
                    "clicked", lambda b: self.connect_bluetooth(item["mac"])
                )
            else:
                connect_label = Gtk.Label(label="Pair")
                connect_label.add_css_class("pair-button")
                # Add click handler for pair & connect
                item_btn.connect(
                    "clicked", lambda b: self.connect_bluetooth(item["mac"])
                )

            item_box.append(connect_label)

        item_btn.set_child(item_box)
        return item_btn

    def connect_wired(self, connection_name):
        """Connect to wired network"""
        try:
            subprocess.run(["nmcli", "connection", "up", connection_name], check=True)
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def disconnect_wired(self, connection_name):
        """Disconnect from wired network"""
        try:
            subprocess.run(["nmcli", "connection", "down", connection_name], check=True)
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def connect_wifi_with_fallback(self, network_name):
        """Connect to WiFi network with fallback to nmtui for password issues"""
        try:
            result = subprocess.run(
                ["nmcli", "device", "wifi", "connect", network_name],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                self.rebuild_ui()
            else:
                # Check if it's a password/authentication error
                error_output = result.stderr.lower()
                if any(
                    keyword in error_output
                    for keyword in ["password", "authentication", "secret", "key"]
                ):
                    self.open_nmtui()
        except subprocess.TimeoutExpired:
            self.open_nmtui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def open_nmtui(self):
        """Open nmtui in ghostty terminal"""
        try:
            subprocess.Popen(["ghostty", "-e", "nmtui"])
        except FileNotFoundError:
            # Fallback to other terminals if ghostty not available
            try:
                subprocess.Popen(["gnome-terminal", "--", "nmtui"])
            except FileNotFoundError:
                subprocess.Popen(["xterm", "-e", "nmtui"])

    def open_blueberry(self):
        """Open blueberry bluetooth manager"""
        try:
            subprocess.Popen(
                ["blueberry"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            try:
                subprocess.Popen(
                    ["blueman-manager"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass  # Silently handle errors

    def connect_wifi(self, network_name):
        """Connect to WiFi network"""
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "connect", network_name], check=True
            )
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def disconnect_wifi(self, network_name):
        """Disconnect from WiFi network"""
        try:
            subprocess.run(["nmcli", "connection", "down", network_name], check=True)
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def connect_bluetooth(self, mac_address):
        """Connect to Bluetooth device (pair first if needed)"""
        try:
            # Check if device is paired
            info_result = subprocess.run(
                ["bluetoothctl", "info", mac_address], capture_output=True, text=True
            )

            if "Paired: yes" not in info_result.stdout:
                # Device not paired, pair it first
                pair_result = subprocess.run(
                    ["bluetoothctl", "pair", mac_address],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if pair_result.returncode != 0:
                    self.open_blueberry()
                    return

                # Trust the device
                subprocess.run(
                    ["bluetoothctl", "trust", mac_address],
                    capture_output=True,
                    timeout=2,
                )

            # Now connect
            connect_result = subprocess.run(
                ["bluetoothctl", "connect", mac_address],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if connect_result.returncode == 0:
                self.rebuild_ui()
            else:
                self.open_blueberry()

        except subprocess.TimeoutExpired:
            self.open_blueberry()
        except subprocess.CalledProcessError:
            self.open_blueberry()

    def disconnect_bluetooth(self, mac_address):
        """Disconnect from Bluetooth device"""
        try:
            subprocess.run(
                ["bluetoothctl", "disconnect", mac_address],
                capture_output=True,
                text=True,
                timeout=2,
            )
            self.rebuild_ui()
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass  # Silently handle errors

    def create_clean_option_item(self, option, expand_data):
        """Create clean option item for power profiles"""
        option_btn = Gtk.Button()
        option_btn.add_css_class("clean-list-item")

        option_label = Gtk.Label(label=option["name"].capitalize())
        option_label.add_css_class("device-name")
        option_label.set_halign(Gtk.Align.START)

        if option.get("active", False):
            option_label.add_css_class("active-option")

        option_btn.set_child(option_label)

        # Add click handler
        if "action_command" in expand_data:
            cmd = expand_data["action_command"].format(**option)
            option_btn.connect("clicked", lambda b: self.execute_system_command(cmd))

        return option_btn

    def create_clean_power_item(self, option):
        """Create clean power menu item like in inspiration"""
        option_btn = Gtk.Button()
        option_btn.add_css_class("power-option")

        option_label = Gtk.Label(label=option["label"])
        option_label.add_css_class("power-label")
        option_label.set_halign(Gtk.Align.START)

        option_btn.set_child(option_label)
        option_btn.connect(
            "clicked", lambda b: self.execute_system_command(option["command"])
        )
        return option_btn

    def create_static_option_item(self, option):
        """Create static option item"""
        option_btn = Gtk.Button()
        option_btn.add_css_class("network-option")

        option_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        option_icon = Gtk.Label(label=option["icon"])
        option_icon.add_css_class("network-icon")
        option_box.append(option_icon)

        option_label = Gtk.Label(label=option["label"])
        option_label.add_css_class("network-name")
        option_label.set_halign(Gtk.Align.START)
        option_label.set_hexpand(True)
        option_box.append(option_label)

        option_btn.connect(
            "clicked", lambda b: self.execute_system_command(option["command"])
        )
        option_btn.set_child(option_box)
        return option_btn

    def create_action_button(self, action, config):
        """Create action button"""
        action_btn = Gtk.Button()
        action_btn.add_css_class("action-button")

        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        if "icon" in action:
            icon = Gtk.Label(label=action["icon"])
            icon.add_css_class("action-icon")
            action_box.append(icon)

        label = Gtk.Label(label=action["label"])
        label.add_css_class("action-label")
        action_box.append(label)

        # Handle command execution
        if action["command"] == "refresh":
            action_btn.connect("clicked", lambda b: self.rebuild_ui())
        else:
            action_btn.connect(
                "clicked", lambda b: self.execute_system_command(action["command"])
            )

        action_btn.set_child(action_box)
        return action_btn

    def execute_system_command(self, command):
        """Execute system command and refresh UI"""
        try:
            subprocess.run(command, shell=True, check=True)
            self.rebuild_ui()
        except (subprocess.CalledProcessError, Exception):
            pass  # Silently handle errors

    def handle_module_click(self, module_id):
        """Unified click handler - checks if module is expandable, otherwise toggles state"""
        # Find module config
        module_config = None
        for row in self.config["capsule_modules"]:
            for mod in row["modules"]:
                if mod["id"] == module_id:
                    module_config = mod
                    break

        # Also check header modules
        if not module_config:
            for mod in self.config.get("header_modules", []):
                if mod["id"] == module_id:
                    module_config = mod
                    break

        if not module_config:
            return

        # Check if module has expand functionality
        if module_config.get("expandable", False):
            # Module has expand section - toggle it
            self.toggle_expand_section(module_id)
        else:
            # Module is just a toggle - handle state change
            if module_id == "power_saver":
                self.toggle_power_saver()
            elif module_id == "night_light":
                self.toggle_night_light()
            elif module_id == "bluetooth":
                self.toggle_bluetooth()
            elif module_id == "wifi":
                self.toggle_network()
            else:
                # For header modules, execute command
                command = module_config.get("command")
                if command:
                    self.execute_system_command(command)

            # Rebuild UI to show state changes (only for non-expandable modules)
            if not module_config.get("expandable", False):
                self.rebuild_ui()

    def complete_section_hide(self, section_widget):
        """Complete hiding animation"""
        section_widget.remove_css_class("hiding-section")
        section_widget.set_visible(False)
        return False

    def find_section_by_id(self, section_id):
        """Find section widget by section ID"""
        class_name = f"{section_id}-section"
        return self.find_section_widget_by_class(class_name)

    def toggle_section_visibility(self, section_id, show):
        """Toggle section visibility with smooth animation"""
        section_widget = self.find_section_widget_by_class(f"{section_id}-section")
        if section_widget:
            if show:
                section_widget.remove_css_class("hidden-section")
                section_widget.add_css_class("showing-section")
            else:
                section_widget.add_css_class("hiding-section")
                # Remove hiding class after animation
                GLib.timeout_add(
                    400, lambda: self.complete_hide_section(section_widget)
                )

            # Remove from expanded_sections after animation completes
            GLib.timeout_add(400, lambda: self.complete_section_close(section_id))
        else:
            # Fallback if widget not found
            self.expanded_sections.discard(section_id)
            self.rebuild_ui()

    def complete_hide_section(self, section_widget):
        """Complete hiding animation by adding hidden class"""
        section_widget.remove_css_class("hiding-section")
        section_widget.add_css_class("hidden-section")
        return False

    def find_section_widget(self, section_id):
        """Find the expanded section widget to animate"""
        return self.find_section_widget_by_class("expanded-section")

    def find_section_widget_by_class(self, css_class):
        """Find widget by CSS class"""

        def find_in_container(container):
            child = container.get_first_child()
            while child:
                if (
                    hasattr(child, "get_css_classes")
                    and css_class in child.get_css_classes()
                ):
                    return child
                # Check if child is a container with children
                if hasattr(child, "get_first_child"):
                    result = find_in_container(child)
                    if result:
                        return result
                child = child.get_next_sibling()
            return None

        return find_in_container(self.main_box)

    def toggle_network(self):
        """Toggle all networking (WiFi + Ethernet) on/off"""
        try:
            # Check WiFi radio state as the main indicator
            wifi_result = subprocess.run(
                ["nmcli", "radio", "wifi"], capture_output=True, text=True
            )
            wifi_enabled = "enabled" in wifi_result.stdout

            if wifi_enabled:
                # Turn off WiFi radio
                subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
                # Disconnect all wired connections (ethernet, USB tethering, etc.)
                result = subprocess.run(
                    [
                        "nmcli",
                        "-t",
                        "-f",
                        "NAME,TYPE",
                        "connection",
                        "show",
                        "--active",
                    ],
                    capture_output=True,
                    text=True,
                )
                for line in result.stdout.strip().split("\n"):
                    if line and ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            conn_name = parts[0]
                            conn_type = parts[1]
                            # Disconnect wired connections (ethernet, tethering, etc.)
                            if any(
                                wired_type in conn_type.lower()
                                for wired_type in [
                                    "ethernet",
                                    "tethering",
                                    "usb",
                                    "gsm",
                                    "cdma",
                                ]
                            ):
                                subprocess.run(
                                    ["nmcli", "connection", "down", conn_name],
                                    check=True,
                                )
            else:
                # Turn on WiFi radio
                subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
                # Bring up wired connections that were previously active
                subprocess.run(["nmcli", "connection", "up", "--all"], check=True)

            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def toggle_bluetooth(self):
        """Toggle Bluetooth on/off"""
        try:
            # Check current state
            result = subprocess.run(
                ["bluetoothctl", "show"], capture_output=True, text=True
            )

            if "Powered: yes" in result.stdout:
                subprocess.run(["bluetoothctl", "power", "off"], check=True)
                new_state = False
            else:
                subprocess.run(["bluetoothctl", "power", "on"], check=True)
                new_state = True

            # Just rebuild modules to get fresh state
            self.rebuild_ui()
        except subprocess.CalledProcessError:
            pass  # Silently handle errors

    def toggle_power_saver(self):
        """Toggle between power-saver and performance mode"""
        try:
            current = subprocess.run(
                ["powerprofilesctl", "get"], capture_output=True, text=True
            ).stdout.strip()

            if current == "power-saver":
                subprocess.run(["powerprofilesctl", "set", "performance"], check=True)
                new_state = False
            else:
                subprocess.run(["powerprofilesctl", "set", "power-saver"], check=True)
                new_state = True

            # Just rebuild modules to get fresh state
            self.rebuild_ui()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # Silently handle errors

    def toggle_night_light(self):
        try:
            # Check if hyprsunset is running
            result = subprocess.run(["pgrep", "hyprsunset"], capture_output=True)
            if result.returncode == 0:
                subprocess.run(["pkill", "hyprsunset"], capture_output=True)
            else:
                subprocess.Popen(["hyprsunset", "--temperature", "4000"])
            self.rebuild_ui()
        except:
            pass  # Silently handle errors

    def update_module_css_class(self, module_id, active):
        """Update module CSS class immediately for visual feedback"""

        def find_and_update_module(widget):
            if not widget:
                return False

            # Check if this widget has CSS classes
            if hasattr(widget, "get_css_classes"):
                css_classes = widget.get_css_classes()
                # Look for module-specific class
                for css_class in css_classes:
                    if module_id in css_class and "module" in css_class:
                        if active:
                            widget.add_css_class("active")
                        else:
                            widget.remove_css_class("active")
                        return True

            # Recursively search children
            if hasattr(widget, "get_first_child"):
                child = widget.get_first_child()
                while child:
                    if find_and_update_module(child):
                        return True
                    child = child.get_next_sibling()

            return False

        find_and_update_module(self.main_box)

    # System state functions
    def create_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        header_box.add_css_class("header-section")

        # Top row with battery and controls
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        top_row.set_size_request(-1, 50)

        # Color picker button on left
        picker_btn = self.create_header_button("", "hyprpicker -a")

        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        controls_box.set_halign(Gtk.Align.END)
        controls_box.set_hexpand(True)

        settings_btn = self.create_header_button("󰓦", "gnome-control-center")
        controls_box.append(settings_btn)

        lock_btn = self.create_header_button("󰌾", "hyprlock")
        controls_box.append(lock_btn)

        # Power button - expandable with power options
        power_btn = self.create_header_button(
            "󰐥", "systemctl poweroff", expandable_id="power"
        )
        power_btn.add_css_class("power-button")
        controls_box.append(power_btn)

        top_row.append(picker_btn)
        top_row.append(controls_box)
        header_box.append(top_row)

        # Pre-create header power section but keep collapsed
        power_expanded = self.create_header_power_expanded()
        if "power" not in self.expanded_sections:
            power_expanded.set_visible(False)
        else:
            power_expanded.set_visible(True)
        header_box.append(power_expanded)

        return header_box

    def create_header_power_expanded(self):
        expanded_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        expanded_box.add_css_class("expanded-section")
        expanded_box.add_css_class("header_power-section")

        power_options = ["Suspend", "Restart", "Power Off", "Log Out"]

        power_commands = [
            "systemctl suspend",
            "systemctl reboot",
            "systemctl poweroff",
            "hyprctl dispatch exit",
        ]

        for i, option in enumerate(power_options):
            option_btn = Gtk.Button()
            option_btn.add_css_class("power-option")

            option_label = Gtk.Label(label=option)
            option_label.add_css_class("power-label")
            option_label.set_halign(Gtk.Align.START)

            option_btn.set_child(option_label)
            option_btn.connect(
                "clicked", lambda b, cmd=power_commands[i]: self.execute_command(cmd)
            )
            expanded_box.append(option_btn)

        return expanded_box

    def create_header_button(self, icon, command, expandable_id=None):
        # Use Button with proper sizing for circular buttons
        button = Gtk.Button()
        button.add_css_class("header-button")
        button.set_size_request(30, 30)
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.CENTER)

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("header-icon")
        icon_label.set_halign(Gtk.Align.CENTER)
        icon_label.set_valign(Gtk.Align.CENTER)
        button.set_child(icon_label)

        # Connect click handler
        if expandable_id:
            button.connect(
                "clicked", lambda *args: self.handle_module_click(expandable_id)
            )
        else:
            button.connect("clicked", lambda *args: self.execute_command(command))

        return button

    def create_sliders_section(self):
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        section_box.add_css_class("sliders-section")

        volume_box = self.create_slider(
            "󰕾", self.get_volume_value, self.set_volume_value
        )
        section_box.append(volume_box)

        brightness_box = self.create_slider(
            "󰃞", self.get_brightness_value, self.set_brightness_value
        )
        section_box.append(brightness_box)

        return section_box

    def get_volume_value(self):
        try:
            result = subprocess.run(
                ["pamixer", "--get-volume"], capture_output=True, text=True
            )
            return int(result.stdout.strip())
        except:
            return 50

    def set_volume_value(self, value):
        try:
            subprocess.run(["pamixer", "--set-volume", str(value)], check=True)
        except:
            pass

    def get_brightness_value(self):
        try:
            current = subprocess.run(
                ["brightnessctl", "get"], capture_output=True, text=True
            )
            max_val = subprocess.run(
                ["brightnessctl", "max"], capture_output=True, text=True
            )
            return int(
                (int(current.stdout.strip()) / int(max_val.stdout.strip())) * 100
            )
        except:
            return 50

    def set_brightness_value(self, value):
        try:
            subprocess.run(["brightnessctl", "set", f"{value}%"], check=True)
        except:
            pass

    def create_slider(self, icon, get_func, set_func):
        slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        slider_box.add_css_class("slider-container")

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("slider-icon")
        slider_box.append(icon_label)

        current_value = get_func()
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(current_value)
        slider.add_css_class("modern-slider")
        slider.set_hexpand(True)
        slider.set_draw_value(False)
        slider.connect("value-changed", lambda s: set_func(int(s.get_value())))
        slider_box.append(slider)

        return slider_box

    def execute_command(self, command):
        try:
            subprocess.Popen(command, shell=True)
            self.close_application()
        except Exception:
            pass  # Silently handle errors

    def create_click_overlay(self):
        self.overlay_window = Gtk.ApplicationWindow(application=self.app)
        self.overlay_window.set_title("click-overlay")
        self.overlay_window.set_decorated(False)

        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0)
        geometry = monitor.get_geometry()

        self.overlay_window.set_default_size(geometry.width, geometry.height)

        Gtk4LayerShell.init_for_window(self.overlay_window)
        Gtk4LayerShell.set_layer(self.overlay_window, Gtk4LayerShell.Layer.TOP)

        for edge in [
            Gtk4LayerShell.Edge.TOP,
            Gtk4LayerShell.Edge.BOTTOM,
            Gtk4LayerShell.Edge.LEFT,
            Gtk4LayerShell.Edge.RIGHT,
        ]:
            Gtk4LayerShell.set_anchor(self.overlay_window, edge, True)
            Gtk4LayerShell.set_margin(self.overlay_window, edge, 0)

        Gtk4LayerShell.set_exclusive_zone(self.overlay_window, 0)

        overlay_box = Gtk.Box()
        overlay_box.set_hexpand(True)
        overlay_box.set_vexpand(True)
        self.overlay_window.set_child(overlay_box)
        self.overlay_window.set_opacity(0.01)

        click_controller = Gtk.GestureClick()
        click_controller.connect("pressed", lambda *args: self.close_application())
        self.overlay_window.add_controller(click_controller)

        GLib.idle_add(lambda: self.overlay_window.present())

    def present_and_focus(self):
        self.window.present()
        self.window.set_can_focus(True)
        self.window.grab_focus()
        return False

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close_application()
            return True
        return False

    def close_application(self):
        if hasattr(self, "overlay_window") and self.overlay_window:
            self.overlay_window.close()
        if self.window:
            self.window.close()
        self.app.quit()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .main-container-window {
        padding: 0 0 1px 0;



        background: transparent;


        }

        .main-container {
            padding: 10px 20px 20px 20px;
            border-radius: 12px;
            background: #3D3D4B;
            color: white;

            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .modules-section {
            /* Ensure sections expand downward */
        }

        .header-section {

        }



        .header-button {
            background: rgba(255, 255, 255, 0.15);
            border: none;
            border-radius: 50%;
            padding: 0;
            margin: 0;
            outline: none;
        }

        .header-button:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        .header-button:focus {
            outline: none;
            box-shadow: none;
        }



        .header-icon {
            font-size: 16px;
            color: white;
            padding: 0;
            margin: 0;
        }

        .sliders-section {
            margin-bottom: 10px;
        }

        .slider-icon {
            font-size: 16px;
            color: white;
        }

        .modern-slider trough {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            min-height: 2px;
            border: none;
        }

        .modern-slider highlight {
            background: #007AFF;
            border-radius: 12px;
        }

        .modern-slider slider {
            background: white;
            border: none;
            border-radius: 50%;
            min-width: 15px;
            min-height: 15px;
            margin: -3px;
        }

        .capsule-module {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 25px;
            padding: 8px 16px;
            margin: 0;
            margin-top: 5px;
            outline: none;

        }

        .capsule-module.active-module {
            background: #007AFF;
        }

        .module-icon {
            font-size: 16px;
            color: white;
        }

        .module-title {
            font-size: 14px;
            font-weight: 600;
            color: white;
        }

        .module-subtitle {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }

        .module-arrow {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.6);
        }

        .expanded-section {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 16px;
            padding: 16px;
            margin: 8px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .expand-header-row {
            padding: 0 0 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 12px;
        }

        .round-icon-container {
            background: #007AFF;
                border: none;
                border-radius: 50%;

                margin: 0;
                outline: none;

        }

        .round-icon {
            padding: 0 8px;

            color: white;
        }

        .expand-title {
            font-size: 16px;
            font-weight: 600;
            color: white;
        }

        .expand-footer-row {
            padding: 12px 0 0 0;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 12px;
        }

        .settings-button {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 8px 0;
        }

        .settings-button:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .settings-label {
            font-size: 14px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.8);
        }

        .refresh-icon-button {
            background: transparent;
            border: none;
            border-radius: 50%;
            padding: 8px;
            min-width: 32px;
            min-height: 32px;
        }

        .refresh-icon-button:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .refresh-icon {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.8);
        }

        .toggle-slider {
            margin: 0 0 0 90px;
            transform: scale(0.7);
        }

        .refresh-button {
            background: rgba(0, 122, 255, 0.8);
            border: none;
            border-radius: 6px;
            padding: 4px 8px;
            color: white;
            font-size: 12px;
            min-width: 30px;
        }

        .refresh-button:hover {
            background: rgba(0, 122, 255, 1.0);
        }

        .hidden-section {
            opacity: 0;
            min-height: 0;
            padding: 0;
            margin: 0;
            border: none;
            transform: scaleY(0);
        }

        .showing-section {
            animation: showSection 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }

        /* COMMENTED OUT FOR TESTING
        .hiding-section {
            animation: hideSection 0.4s cubic-bezier(0.55, 0.06, 0.68, 0.19) forwards;
        }
        */

        /* @keyframes showSection {
            0% {
                opacity: 0;
                transform: scaleY(0) translateY(-10px);
                padding: 0;
                margin: 0;
            }
            100% {
                opacity: 1;
                transform: scaleY(1) translateY(0);
                padding: 12px;
                margin: 8px 0;
            }
        } */

        /* @keyframes hideSection {
            0% {
                opacity: 1;
                transform: scaleY(1) translateY(0);
                padding: 12px;
                margin: 8px 0;
            }
            100% {
                opacity: 0;
                transform: scaleY(0) translateY(-20px);
                padding: 0;
                margin: 0;
            }
        } */

        .clean-list-item {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 1px 0;
        }

        .clean-list-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .device-name {
            font-size: 14px;
            font-weight: 500;
            color: white;
        }

        .device-icon {
            font-size: 16px;
            color: #007AFF;
        }

        .connect-button {
            font-size: 14px;
            font-weight: 500;
            color: #007AFF;
            padding: 4px 12px;
            border-radius: 6px;
            background: transparent;
        }

        .disconnect-button {
            font-size: 14px;
            font-weight: 500;
            color: #FF3B30;
            padding: 4px 12px;
            border-radius: 6px;
            background: transparent;
        }

        .clean-list-item:hover .connect-button {
            background: rgba(0, 122, 255, 0.15);
        }

        .clean-list-item:hover .disconnect-button {
            background: rgba(255, 59, 48, 0.15);
        }

        .pair-button {
            font-size: 14px;
            font-weight: 500;
            color: #FF9500;
            padding: 4px 12px;
            border-radius: 6px;
            background: transparent;
        }

        .clean-list-item:hover .pair-button {
            background: rgba(255, 149, 0, 0.15);
        }

        .settings-option {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .settings-option:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .settings-label {
            font-size: 14px;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.8);
        }

        .power-option {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 1px 0;
        }

        .power-option:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .power-label {
            font-size: 14px;
            font-weight: 500;
            color: white;
        }

        .active-option {
            color: #007AFF;
        }

        .network-signal {
            font-size: 13px;
            color: white;
        }

        .network-name {
            font-weight: 500;
        }

        .network-check {
            font-size: 14px;
            color: #007AFF;
            font-weight: bold;
        }
        """)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def run(self):
        return self.app.run(sys.argv)


if __name__ == "__main__":
    menu = WaybarMenu()
    menu.run()
