#!/usr/bin/env python3
import gi
import sys
import subprocess
import signal
import json
import os
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gtk4LayerShell

signal.signal(signal.SIGINT, lambda *a: sys.exit(0))

class WaybarMenu:
    def __init__(self):
        self.app = Gtk.Application(application_id='com.waybar.menu')
        self.app.connect('activate', self.on_activate)
        
        # Expanded sections tracking
        self.expanded_sections = set()
        
        # Real-time state refresh
        self.refresh_states()
        
        self.window = None
        self.main_box = None

    def refresh_states(self):
        """Refresh all system states"""
        self.wifi_state = self.get_wifi_state()
        self.bluetooth_state = self.get_bluetooth_state()
        self.power_mode = self.get_power_mode()
        self.dark_mode = self.get_dark_mode_state()
        self.night_light_active = self.get_night_light_state()
        self.airplane_mode = self.get_airplane_mode()

    def on_activate(self, app):
        self.create_main_window()

    def create_main_window(self):
        self.window = Gtk.ApplicationWindow(application=self.app)
        self.window.set_title("waybar-menu")
        self.window.set_default_size(300, 400)
        self.window.set_resizable(False)
        self.window.set_decorated(False)

        # Layer Shell setup
        Gtk4LayerShell.init_for_window(self.window)
        Gtk4LayerShell.set_layer(self.window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.TOP, 10)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.RIGHT, 10)
        Gtk4LayerShell.set_keyboard_mode(self.window, Gtk4LayerShell.KeyboardMode.ON_DEMAND)

        self.load_css()
        
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.add_css_class('main-container')
        
        self.rebuild_ui()
        self.window.set_child(self.main_box)
        
        # Event handlers
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_key_pressed)
        self.window.add_controller(key_controller)
        
        self.create_click_overlay()
        GLib.idle_add(self.present_and_focus)

    def rebuild_ui(self):
        """Rebuild the entire UI - useful for dynamic updates"""
        # Refresh system states first
        self.refresh_states()
        
        # Clear existing children
        child = self.main_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.main_box.remove(child)
            child = next_child
        
        # Header with battery and controls
        header = self.create_header()
        self.main_box.append(header)
        
        # Sliders section
        sliders = self.create_sliders_section()
        self.main_box.append(sliders)
        
    def create_header(self):
        """Create header with battery and controls"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header_box.add_css_class('header-section')
        header_box.set_size_request(-1, 50)
        
        # Battery info
        battery_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        battery_box.set_halign(Gtk.Align.START)
        battery_box.set_hexpand(True)
        
        battery_icon = Gtk.Label(label="🔋")
        battery_icon.add_css_class('battery-icon')
        battery_box.append(battery_icon)
        
        battery_percent = Gtk.Label(label=f"{self.get_battery_level()}%")
        battery_percent.add_css_class('battery-text')
        battery_box.append(battery_percent)
        
        # Control buttons
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        controls_box.set_halign(Gtk.Align.END)
        
        # Settings button
        settings_btn = self.create_header_button("⚙️", "gnome-control-center")
        controls_box.append(settings_btn)
        
        # Lock button  
        lock_btn = self.create_header_button("🔒", "hyprlock")
        controls_box.append(lock_btn)
        
        # Power button
        power_btn = self.create_header_button("⏻", "systemctl poweroff")
        power_btn.add_css_class('power-button')
        controls_box.append(power_btn)
        
        header_box.append(battery_box)
        header_box.append(controls_box)
        
        return header_box

    def create_header_button(self, icon, command):
        """Create a circular header button"""
        button = Gtk.Button()
        button.add_css_class('header-button')
        button.set_size_request(36, 36)
        
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('header-icon')
        button.set_child(icon_label)
        
        button.connect('clicked', lambda b: self.execute_command(command))
        return button

    def create_sliders_section(self):
        """Create volume and brightness sliders"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        section_box.add_css_class('sliders-section')
        
        # Volume slider
        volume_box = self.create_slider("🔊", self.get_volume_value, self.set_volume_value)
        section_box.append(volume_box)
        
        # Brightness slider
        brightness_box = self.create_slider("☀️", self.get_brightness_value, self.set_brightness_value)
        section_box.append(brightness_box)
        
        return section_box

    def create_slider(self, icon, get_func, set_func):
        """Create a modern slider with icon"""
        slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        slider_box.add_css_class('slider-container')
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('slider-icon')
        slider_box.append(icon_label)
        
        # Slider
        current_value = get_func()
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_value(current_value)
        slider.add_css_class('modern-slider')
        slider.set_hexpand(True)
        slider.set_draw_value(False)
        slider.connect('value-changed', lambda s: set_func(int(s.get_value())))
        slider_box.append(slider)
        
        return slider_box

    def create_modules_section(self):
        """Create the main modules grid with expandable sections"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section_box.add_css_class('modules-section')
        
        # Row 1: WiFi and Bluetooth
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row1.set_homogeneous(True)
        
        wifi_module = self.create_capsule_module(
            "📶", "Wi-Fi", self.wifi_state['name'], 
            self.wifi_state['active'], "wifi", has_submenu=True
        )
        bluetooth_module = self.create_capsule_module(
            "🔵", "Bluetooth", "On" if self.bluetooth_state else "Off",
            self.bluetooth_state, "bluetooth", has_submenu=True
        )
        
        row1.append(wifi_module)
        row1.append(bluetooth_module)
        section_box.append(row1)
        
        # WiFi expanded section
        if "wifi" in self.expanded_sections:
            wifi_expanded = self.create_wifi_expanded()
            section_box.append(wifi_expanded)
        
        # Bluetooth expanded section
        if "bluetooth" in self.expanded_sections:
            bluetooth_expanded = self.create_bluetooth_expanded()
            section_box.append(bluetooth_expanded)
        
        # Row 2: Power Mode and Night Light
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row2.set_homogeneous(True)
        
        power_module = self.create_capsule_module(
            "🔋", "Power Mode", self.power_mode,
            True, "power", has_submenu=True
        )
        night_light_module = self.create_capsule_module(
            "🌙", "Night Light", "",
            self.night_light_active, "night_light"
        )
        
        row2.append(power_module)
        row2.append(night_light_module)
        section_box.append(row2)
        
        # Power Mode expanded section
        if "power" in self.expanded_sections:
            power_expanded = self.create_power_expanded()
            section_box.append(power_expanded)
        
        # Row 3: Dark Style and Keyboard
        row3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row3.set_homogeneous(True)
        
        dark_style_module = self.create_capsule_module(
            "🌙", "Dark Style", "", self.dark_mode, "dark_style"
        )
        keyboard_module = self.create_capsule_module(
            "⌨️", "Keyboard", "", False, "keyboard"
        )
        
        row3.append(dark_style_module)
        row3.append(keyboard_module)
        section_box.append(row3)
        
        # Row 4: Airplane Mode and Tiling
        row4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row4.set_homogeneous(True)
        
        airplane_module = self.create_capsule_module(
            "✈️", "Airplane Mode", "", self.airplane_mode, "airplane"
        )
        tiling_module = self.create_capsule_module(
            "🪟", "Tiling", "", True, "tiling"
        )
        
        row4.append(airplane_module)
        row4.append(tiling_module)
        section_box.append(row4)
        
        return section_box

    def create_modules_section(self):
        """Create the main modules grid with expandable sections"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section_box.add_css_class('modules-section')
        
        # Row 1: WiFi and Bluetooth
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row1.set_homogeneous(True)
        
        wifi_module = self.create_capsule_module(
            "📶", "Wi-Fi", self.wifi_state['name'], 
            self.wifi_state['active'], "wifi", has_submenu=True
        )
        bluetooth_module = self.create_capsule_module(
            "🔵", "Bluetooth", "On" if self.bluetooth_state else "Off",
            self.bluetooth_state, "bluetooth", has_submenu=True
        )
        
        row1.append(wifi_module)
        row1.append(bluetooth_module)
        section_box.append(row1)
        
        # WiFi expanded section
        if "wifi" in self.expanded_sections:
            wifi_expanded = self.create_wifi_expanded()
            section_box.append(wifi_expanded)
        
        # Bluetooth expanded section
        if "bluetooth" in self.expanded_sections:
            bluetooth_expanded = self.create_bluetooth_expanded()
            section_box.append(bluetooth_expanded)
        
        # Row 2: Power Mode and Night Light
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row2.set_homogeneous(True)
        
        power_module = self.create_capsule_module(
            "🔋", "Power Mode", self.power_mode,
            True, "power", has_submenu=True
        )
        night_light_module = self.create_capsule_module(
            "🌙", "Night Light", "",
            self.night_light_active, "night_light"
        )
        
        row2.append(power_module)
        row2.append(night_light_module)
        section_box.append(row2)
        
        # Power Mode expanded section
        if "power" in self.expanded_sections:
            power_expanded = self.create_power_expanded()
            section_box.append(power_expanded)
        
        # Row 3: Dark Style and Keyboard
        row3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row3.set_homogeneous(True)
        
        dark_style_module = self.create_capsule_module(
            "🌙", "Dark Style", "", self.dark_mode, "dark_style"
        )
        keyboard_module = self.create_capsule_module(
            "⌨️", "Keyboard", "", False, "keyboard"
        )
        
        row3.append(dark_style_module)
        row3.append(keyboard_module)
        section_box.append(row3)
        
        # Row 4: Airplane Mode and Tiling
        row4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row4.set_homogeneous(True)
        
        airplane_module = self.create_capsule_module(
            "✈️", "Airplane Mode", "", self.airplane_mode, "airplane"
        )
        tiling_module = self.create_capsule_module(
            "🪟", "Tiling", "", True, "tiling"
        )
        
        row4.append(airplane_module)
        row4.append(tiling_module)
        section_box.append(row4)
        
        return section_box

    def create_capsule_module(self, icon, title, subtitle, active, module_id, has_submenu=False):
        """Create a capsule-shaped module button"""
        button = Gtk.Button()
        button.add_css_class('capsule-module')
        if active:
            button.add_css_class('active-module')
        
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        content_box.set_halign(Gtk.Align.START)
        content_box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('module-icon')
        content_box.append(icon_label)
        
        # Text content
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        text_box.set_halign(Gtk.Align.START)
        
        title_label = Gtk.Label(label=title)
        title_label.add_css_class('module-title')
        title_label.set_halign(Gtk.Align.START)
        text_box.append(title_label)
        
        if subtitle:
            subtitle_label = Gtk.Label(label=subtitle)
            subtitle_label.add_css_class('module-subtitle')
            subtitle_label.set_halign(Gtk.Align.START)
            text_box.append(subtitle_label)
        
        content_box.append(text_box)
        
        # Arrow for expandable modules
        if has_submenu:
            arrow = Gtk.Label(label="›")
            arrow.add_css_class('module-arrow')
            arrow.set_halign(Gtk.Align.END)
            arrow.set_hexpand(True)
            content_box.append(arrow)
        
        button.set_child(content_box)
        button.connect('clicked', lambda b: self.handle_module_click(module_id, has_submenu))
        
        return button
    def create_wifi_expanded(self):
        expanded_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        expanded_box.add_css_class('expanded-section')
        
        networks = ["Vista", "Home-WiFi", "Office-5G"]
        for network in networks:
            network_btn = Gtk.Button()
            network_btn.add_css_class('network-option')
            
            network_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            signal_icon = Gtk.Label(label="📶")
            signal_icon.add_css_class('network-icon')
            network_box.append(signal_icon)
            
            network_label = Gtk.Label(label=network)
            network_label.add_css_class('network-name')
            network_label.set_halign(Gtk.Align.START)
            network_label.set_hexpand(True)
            network_box.append(network_label)
            
            if network == self.wifi_state['name']:
                check_icon = Gtk.Label(label="✓")
                check_icon.add_css_class('network-check')
                network_box.append(check_icon)
            
            network_btn.set_child(network_box)
            network_btn.connect('clicked', lambda b, n=network: self.connect_wifi(n))
            expanded_box.append(network_btn)
        
        return expanded_box

    def create_bluetooth_expanded(self):
        expanded_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        expanded_box.add_css_class('expanded-section')
        
        devices = self.get_bluetooth_devices()
        if devices:
            for device in devices:
                device_btn = Gtk.Button()
                device_btn.add_css_class('network-option')
                
                device_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                bt_icon = Gtk.Label(label="🔵")
                bt_icon.add_css_class('network-icon')
                device_box.append(bt_icon)
                
                device_label = Gtk.Label(label=device['name'])
                device_label.add_css_class('network-name')
                device_label.set_halign(Gtk.Align.START)
                device_label.set_hexpand(True)
                device_box.append(device_label)
                
                if device['connected']:
                    check_icon = Gtk.Label(label="✓")
                    check_icon.add_css_class('network-check')
                    device_box.append(check_icon)
                
                device_btn.set_child(device_box)
                expanded_box.append(device_btn)
        else:
            no_devices = Gtk.Label(label="No devices found")
            no_devices.add_css_class('network-name')
            expanded_box.append(no_devices)
        
        return expanded_box

    def create_power_expanded(self):
        expanded_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        expanded_box.add_css_class('expanded-section')
        
        power_modes = ["Performance", "Balanced", "Power-saver"]
        for mode in power_modes:
            mode_btn = Gtk.Button()
            mode_btn.add_css_class('network-option')
            
            mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            power_icon = Gtk.Label(label="🔋")
            power_icon.add_css_class('network-icon')
            mode_box.append(power_icon)
            
            mode_label = Gtk.Label(label=mode)
            mode_label.add_css_class('network-name')
            mode_label.set_halign(Gtk.Align.START)
            mode_label.set_hexpand(True)
            mode_box.append(mode_label)
            
            if mode.lower() == self.power_mode.lower():
                check_icon = Gtk.Label(label="✓")
                check_icon.add_css_class('network-check')
                mode_box.append(check_icon)
            
            mode_btn.set_child(mode_box)
            mode_btn.connect('clicked', lambda b, m=mode: self.set_power_mode(m))
            expanded_box.append(mode_btn)
        
        return expanded_box

    def handle_module_click(self, module_id, has_submenu):
        if has_submenu:
            if module_id in self.expanded_sections:
                self.expanded_sections.remove(module_id)
            else:
                self.expanded_sections.add(module_id)
            self.rebuild_ui()
        else:
            if module_id == "night_light":
                self.toggle_night_light()
            elif module_id == "dark_style":
                self.toggle_dark_style()
            elif module_id == "airplane":
                self.toggle_airplane_mode()

    def toggle_night_light(self):
        if self.night_light_active:
            subprocess.run(['pkill', 'hyprsunset'], capture_output=True)
        else:
            subprocess.Popen(['hyprsunset', '--temperature', '4000'])
        self.rebuild_ui()

    def toggle_dark_style(self):
        if self.dark_mode:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', 'Adwaita'])
        else:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', 'Adwaita-dark'])
        self.rebuild_ui()

    def toggle_airplane_mode(self):
        if self.airplane_mode:
            subprocess.run(['nmcli', 'radio', 'all', 'on'])
        else:
            subprocess.run(['nmcli', 'radio', 'all', 'off'])
        self.rebuild_ui()

    def connect_wifi(self, network_name):
        subprocess.Popen(['nmcli', 'connection', 'up', network_name])
        self.expanded_sections.discard("wifi")
        self.close_application()

    def set_power_mode(self, mode):
        subprocess.run(['powerprofilesctl', 'set', mode.lower()])
        self.expanded_sections.discard("power")
        self.rebuild_ui()

    def get_wifi_state(self):
        try:
            wifi_enabled = subprocess.run(['nmcli', 'radio', 'wifi'], 
                                        capture_output=True, text=True).stdout.strip() == 'enabled'
            
            if not wifi_enabled:
                return {'active': False, 'name': 'Off'}
            
            result = subprocess.run(['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
                                  capture_output=True, text=True)
            
            for line in result.stdout.strip().split('\n'):
                if line and '802-11-wireless' in line:
                    name = line.split(':')[0]
                    return {'active': True, 'name': name}
            
            return {'active': True, 'name': 'Not Connected'}
        except:
            return {'active': False, 'name': 'Unknown'}

    def get_bluetooth_state(self):
        try:
            result = subprocess.run(['bluetoothctl', 'show'], capture_output=True, text=True)
            return 'Powered: yes' in result.stdout
        except:
            return False

    def get_bluetooth_devices(self):
        try:
            result = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True)
            devices = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('Device'):
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        mac = parts[1]
                        name = parts[2]
                        conn_result = subprocess.run(['bluetoothctl', 'info', mac], capture_output=True, text=True)
                        connected = 'Connected: yes' in conn_result.stdout
                        devices.append({'name': name, 'mac': mac, 'connected': connected})
            return devices
        except:
            return []

    def get_power_mode(self):
        try:
            result = subprocess.run(['powerprofilesctl', 'get'], capture_output=True, text=True)
            mode = result.stdout.strip()
            return mode.capitalize() if mode else 'Balanced'
        except:
            return 'Balanced'

    def get_dark_mode_state(self):
        try:
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                                  capture_output=True, text=True)
            return 'dark' in result.stdout.lower()
        except:
            return False

    def get_night_light_state(self):
        try:
            result = subprocess.run(['pgrep', 'hyprsunset'], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def get_airplane_mode(self):
        try:
            result = subprocess.run(['nmcli', 'radio', 'all'], capture_output=True, text=True)
            return 'disabled' in result.stdout
        except:
            return False

    def get_battery_level(self):
        try:
            with open('/sys/class/power_supply/BAT0/capacity', 'r') as f:
                return int(f.read().strip())
        except:
            return 88

    def get_volume_value(self):
        try:
            result = subprocess.run(['pamixer', '--get-volume'], capture_output=True, text=True)
            return int(result.stdout.strip())
        except:
            return 50

    def set_volume_value(self, value):
        try:
            subprocess.run(['pamixer', '--set-volume', str(value)], check=True)
        except:
            pass

    def get_brightness_value(self):
        try:
            current = subprocess.run(['brightnessctl', 'get'], capture_output=True, text=True)
            max_val = subprocess.run(['brightnessctl', 'max'], capture_output=True, text=True)
            return int((int(current.stdout.strip()) / int(max_val.stdout.strip())) * 100)
        except:
            return 50

    def set_brightness_value(self, value):
        try:
            subprocess.run(['brightnessctl', 'set', f'{value}%'], check=True)
        except:
            pass

    def execute_command(self, command):
        try:
            subprocess.Popen(command, shell=True)
            self.close_application()
        except Exception as e:
            print(f"Error executing command: {e}")

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
        
        for edge in [Gtk4LayerShell.Edge.TOP, Gtk4LayerShell.Edge.BOTTOM, 
                     Gtk4LayerShell.Edge.LEFT, Gtk4LayerShell.Edge.RIGHT]:
            Gtk4LayerShell.set_anchor(self.overlay_window, edge, True)
            Gtk4LayerShell.set_margin(self.overlay_window, edge, 0)
        
        Gtk4LayerShell.set_exclusive_zone(self.overlay_window, 0)
        
        overlay_box = Gtk.Box()
        overlay_box.set_hexpand(True)
        overlay_box.set_vexpand(True)
        self.overlay_window.set_child(overlay_box)
        self.overlay_window.set_opacity(0.01)
        
        click_controller = Gtk.GestureClick()
        click_controller.connect('pressed', lambda *args: self.close_application())
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
        if hasattr(self, 'overlay_window') and self.overlay_window:
            self.overlay_window.close()
        if self.window:
            self.window.close()
        self.app.quit()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        window.main-window {
            background: transparent;
        }

        .main-container {
            background: linear-gradient(145deg, #2c2c34, #3a3a42);
            border-radius: 20px;
            padding: 20px;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .header-section {
            margin-bottom: 20px;
            padding: 0 4px;
        }

        .battery-icon, .battery-text {
            font-size: 16px;
            font-weight: 600;
            color: white;
        }

        .header-button {
            background: rgba(255, 255, 255, 0.15);
            border: none;
            border-radius: 18px;
            transition: all 0.2s ease;
        }

        .header-button:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        .power-button {
            background: rgba(255, 59, 48, 0.8);
        }

        .header-icon {
            font-size: 16px;
            color: white;
        }

        .sliders-section {
            margin-bottom: 24px;
        }

        .slider-container {
            padding: 8px 0;
        }

        .slider-icon {
            font-size: 18px;
            color: white;
            min-width: 24px;
        }

        .modern-slider trough {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            min-height: 6px;
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
            min-width: 20px;
            min-height: 20px;
            margin: -7px;
        }

        .modules-section {
            margin-bottom: 16px;
        }

        .capsule-module {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 20px;
            padding: 8px 12px;
            transition: all 0.2s ease;
            min-height: 40px;
        }

        .capsule-module:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        .active-module {
            background: #007AFF;
        }

        .module-icon {
            font-size: 16px;
            color: white;
        }

        .module-title {
            font-size: 13px;
            font-weight: 600;
            color: white;
        }

        .module-subtitle {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7);
        }

        .module-arrow {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.6);
        }

        .expanded-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 8px;
            margin: 4px 0;
        }

        .network-option {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 6px 8px;
        }

        .network-option:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .network-icon, .network-name {
            font-size: 12px;
            color: white;
        }

        .network-check {
            font-size: 12px;
            color: #007AFF;
        }
        """)
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def run(self):
        return self.app.run(sys.argv)

if __name__ == "__main__":
    menu = WaybarMenu()
    menu.run()
