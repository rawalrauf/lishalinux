#!/usr/bin/env python3
import time
start_time = time.time()

import gi
import sys
import subprocess
import signal
import os

gi.require_version('Gtk', '4.0')
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gtk4LayerShell

signal.signal(signal.SIGINT, lambda *a: sys.exit(0))

# Fast system call functions - no caching
def get_bluetooth_status():
    try:
        result = subprocess.run(['bluetoothctl', 'show'], capture_output=True, text=True, timeout=1)
        return 'Powered: yes' in result.stdout
    except:
        return False

def get_bluetooth_devices():
    try:
        devices = []
        result = subprocess.run(['bluetoothctl', 'devices', 'Connected'], 
                               capture_output=True, text=True, timeout=1)
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith('Device'):
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    devices.append({'mac': parts[1], 'name': parts[2]})
        return devices
    except:
        return []

def get_network_status():
    try:
        result = subprocess.run(['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
                               capture_output=True, text=True, timeout=1)
        
        for line in result.stdout.strip().split('\n'):
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    conn_type = parts[1]
                    if '802-3-ethernet' in conn_type:
                        return {'connected': True, 'icon': '󰈀', 'name': 'Wired'}
                    elif '802-11-wireless' in conn_type:
                        return {'connected': True, 'icon': '󰤨', 'name': parts[0]}
        
        return {'connected': False, 'icon': '󰤭', 'name': 'Disconnected'}
    except:
        return {'connected': False, 'icon': '󰤭', 'name': 'Unknown'}

def get_network_connections():
    try:
        connections = []
        result = subprocess.run(['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
                               capture_output=True, text=True, timeout=1)
        
        for line in result.stdout.strip().split('\n'):
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    connections.append({'name': parts[0], 'type': parts[1]})
        return connections
    except:
        return []

class OptimizedMenu:
    def __init__(self):
        self.app = Gtk.Application(application_id='com.waybar.optimized')
        self.app.connect('activate', self.on_activate)
        self.expanded_sections = set()
        self.expand_widgets = {}  # Lazy loading cache
        self.module_widgets = {}  # Widget references for updates
        self.window = None

    def on_activate(self, app):
        self.create_window()

    def create_window(self):
        self.window = Gtk.ApplicationWindow(application=self.app)
        self.window.set_title("Quick Settings")
        
        # Layer shell setup
        Gtk4LayerShell.init_for_window(self.window)
        Gtk4LayerShell.set_layer(self.window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.TOP, 40)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.RIGHT, 10)
        
        self.load_css()
        self.build_ui()
        
        # Auto-close on focus loss
        self.window.connect('notify::is-active', self.on_focus_change)
        
        GLib.idle_add(self.present_window)

    def present_window(self):
        self.window.present()
        load_time = time.time() - start_time
        print(f"Window loaded in {load_time:.3f} seconds")
        return False

    def on_focus_change(self, window, param):
        if not window.is_active():
            GLib.timeout_add(100, self.close_if_not_active)

    def close_if_not_active(self):
        if not self.window.is_active():
            self.window.close()
        return False

    def build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.add_css_class('main-container')
        
        # Header with buttons
        header = self.create_header()
        main_box.append(header)
        
        # Module sections
        modules = self.create_modules()
        main_box.append(modules)
        
        self.window.set_child(main_box)

    def create_header(self):
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.add_css_class('header-container')
        
        # Settings button
        settings_btn = Gtk.Button(label='󰒓')
        settings_btn.add_css_class('header-button')
        settings_btn.connect('clicked', lambda b: subprocess.Popen(['gnome-control-center']))
        header_box.append(settings_btn)
        
        # Lock button
        lock_btn = Gtk.Button(label='󰌾')
        lock_btn.add_css_class('header-button')
        lock_btn.connect('clicked', lambda b: subprocess.Popen(['hyprlock']))
        header_box.append(lock_btn)
        
        # Power button
        power_btn = Gtk.Button(label='󰐥')
        power_btn.add_css_class('header-button')
        power_btn.add_css_class('power-button')
        power_btn.connect('clicked', lambda b: subprocess.run(['systemctl', 'poweroff']))
        header_box.append(power_btn)
        
        return header_box

    def create_modules(self):
        modules_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Row 1: Network + Bluetooth
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Network module (expandable)
        net_status = get_network_status()
        network_module = self.create_module('wifi', net_status['icon'], 'Network', 
                                          net_status['connected'], True)
        row1.append(network_module)
        
        # Bluetooth module (expandable)
        bt_active = get_bluetooth_status()
        bluetooth_module = self.create_module('bluetooth', '󰂯', 'Bluetooth', 
                                            bt_active, True)
        row1.append(bluetooth_module)
        
        modules_box.append(row1)
        
        # Row 2: Power Saver + Night Light
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Power Saver module (non-expandable)
        try:
            power_active = 'power-saver' in subprocess.run(['powerprofilesctl', 'get'], 
                                                          capture_output=True, text=True, timeout=1).stdout
        except:
            power_active = False
        
        power_module = self.create_module('power_mode', '󰁹', 'Power Saver', 
                                        power_active, False)
        row2.append(power_module)
        
        # Night Light module (non-expandable)
        try:
            night_active = subprocess.run(['pgrep', 'hyprsunset'], 
                                        capture_output=True, timeout=1).returncode == 0
        except:
            night_active = False
            
        night_module = self.create_module('night_light', '󰖔', 'Night Light', 
                                        night_active, False)
        row2.append(night_module)
        
        modules_box.append(row2)
        
        return modules_box

    def create_module(self, module_id, icon, title, active, expandable):
        """Create new expandable module design (button >)"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Single button with arrow
        button = Gtk.Button()
        button.add_css_class('module-button')
        if active:
            button.add_css_class('active')
        
        # Store reference for updates
        self.module_widgets[module_id] = button
        
        # Button content
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('module-icon')
        button_box.append(icon_label)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.add_css_class('module-title')
        title_label.set_hexpand(True)
        title_label.set_halign(Gtk.Align.START)
        button_box.append(title_label)
        
        # Arrow for expandable modules
        if expandable:
            arrow_label = Gtk.Label(label='>')
            arrow_label.add_css_class('expand-arrow')
            button_box.append(arrow_label)
        
        button.set_child(button_box)
        
        # Click handlers
        if expandable:
            button.connect('clicked', lambda b: self.toggle_expand(module_id))
        else:
            button.connect('clicked', lambda b: self.toggle_module(module_id))
        
        container.append(button)
        
        # Lazy-loaded expand section
        if expandable and module_id in self.expanded_sections:
            expand_section = self.create_expand_section(module_id)
            container.append(expand_section)
        
        return container

    def toggle_expand(self, module_id):
        """Toggle expand section with lazy loading"""
        if module_id in self.expanded_sections:
            self.expanded_sections.remove(module_id)
        else:
            self.expanded_sections.add(module_id)
        
        # Rebuild only this module's container
        self.rebuild_module(module_id)

    def toggle_module(self, module_id):
        """Toggle module state (for non-expandable modules)"""
        if module_id == 'power_mode':
            self.toggle_power_saver()
        elif module_id == 'night_light':
            self.toggle_night_light()
        
        # Update widget state immediately
        self.update_module_widget(module_id)

    def toggle_power_saver(self):
        try:
            current = subprocess.run(['powerprofilesctl', 'get'], 
                                   capture_output=True, text=True, timeout=1).stdout.strip()
            if current == 'power-saver':
                subprocess.run(['powerprofilesctl', 'set', 'balanced'])
            else:
                subprocess.run(['powerprofilesctl', 'set', 'power-saver'])
        except:
            pass

    def toggle_night_light(self):
        try:
            if subprocess.run(['pgrep', 'hyprsunset'], capture_output=True).returncode == 0:
                subprocess.run(['pkill', 'hyprsunset'])
            else:
                subprocess.Popen(['hyprsunset', '--temperature', '4000'])
        except:
            pass

    def update_module_widget(self, module_id):
        """Update only the specific module widget"""
        widget = self.module_widgets.get(module_id)
        if not widget:
            return
        
        # Get current state
        active = False
        if module_id == 'power_mode':
            try:
                active = 'power-saver' in subprocess.run(['powerprofilesctl', 'get'], 
                                                       capture_output=True, text=True, timeout=1).stdout
            except:
                pass
        elif module_id == 'night_light':
            try:
                active = subprocess.run(['pgrep', 'hyprsunset'], 
                                      capture_output=True, timeout=1).returncode == 0
            except:
                pass
        
        # Update CSS class
        if active:
            widget.add_css_class('active')
        else:
            widget.remove_css_class('active')

    def rebuild_module(self, module_id):
        """Rebuild only specific module (for expand/collapse)"""
        # This is a simplified version - in full implementation, 
        # you'd find the module container and rebuild just that part
        self.build_ui()

    def create_expand_section(self, module_id):
        """Create expand section with toggle slider and refresh button"""
        expand_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        expand_box.add_css_class('expand-section')
        
        # Header with toggle slider and refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.add_css_class('expand-header')
        
        # Toggle slider for module on/off
        toggle_slider = self.create_toggle_slider(module_id)
        header_box.append(toggle_slider)
        
        # Refresh button
        refresh_btn = Gtk.Button(label='🔄')
        refresh_btn.add_css_class('refresh-button')
        refresh_btn.connect('clicked', lambda b: self.refresh_expand_content(module_id))
        header_box.append(refresh_btn)
        
        expand_box.append(header_box)
        
        # Content
        content = self.create_expand_content(module_id)
        expand_box.append(content)
        
        return expand_box

    def create_toggle_slider(self, module_id):
        """Create toggle slider for module on/off"""
        slider = Gtk.Switch()
        slider.add_css_class('toggle-slider')
        
        # Set initial state
        if module_id == 'wifi':
            slider.set_active(get_network_status()['connected'])
        elif module_id == 'bluetooth':
            slider.set_active(get_bluetooth_status())
        
        # Connect toggle handler
        slider.connect('notify::active', lambda s, p: self.handle_slider_toggle(module_id, s.get_active()))
        
        return slider

    def handle_slider_toggle(self, module_id, active):
        """Handle toggle slider changes"""
        if module_id == 'wifi':
            if active:
                subprocess.run(['nmcli', 'radio', 'wifi', 'on'])
            else:
                subprocess.run(['nmcli', 'radio', 'wifi', 'off'])
        elif module_id == 'bluetooth':
            if active:
                subprocess.run(['bluetoothctl', 'power', 'on'])
            else:
                subprocess.run(['bluetoothctl', 'power', 'off'])

    def create_expand_content(self, module_id):
        """Create expand section content"""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        if module_id == 'wifi':
            connections = get_network_connections()
            for conn in connections:
                item = Gtk.Label(label=f"📶 {conn['name']}")
                item.add_css_class('device-item')
                content_box.append(item)
        
        elif module_id == 'bluetooth':
            devices = get_bluetooth_devices()
            for device in devices:
                item = Gtk.Label(label=f"🔵 {device['name']}")
                item.add_css_class('device-item')
                content_box.append(item)
        
        return content_box

    def refresh_expand_content(self, module_id):
        """Refresh only expand section content"""
        # Find and rebuild just the expand section
        self.rebuild_module(module_id)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .main-container {
            padding: 16px;
            border-radius: 12px;
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header-container {
            padding: 8px 0;
            margin-bottom: 12px;
        }

        .header-button {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            margin: 0 4px;
            color: white;
            font-size: 16px;
            min-width: 40px;
            min-height: 40px;
        }

        .header-button:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        .power-button {
            background: rgba(255, 59, 48, 0.8);
        }

        .power-button:hover {
            background: rgba(255, 79, 68, 0.9);
        }

        .module-button {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 2px 4px;
            color: white;
            min-width: 140px;
            min-height: 50px;
        }

        .module-button:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .module-button.active {
            background: rgba(0, 122, 255, 0.8);
        }

        .module-icon {
            font-size: 18px;
            margin-right: 8px;
        }

        .module-title {
            font-size: 14px;
            font-weight: 500;
        }

        .expand-arrow {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }

        .expand-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 12px;
            margin: 4px 0;
        }

        .expand-header {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 8px;
        }

        .toggle-slider {
            margin-right: 8px;
        }

        .refresh-button {
            background: rgba(0, 122, 255, 0.8);
            border: none;
            border-radius: 6px;
            padding: 4px 8px;
            color: white;
            font-size: 12px;
        }

        .refresh-button:hover {
            background: rgba(0, 122, 255, 1.0);
        }

        .device-item {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            padding: 8px 12px;
            margin: 2px 0;
            color: white;
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
    menu = OptimizedMenu()
    menu.run()
