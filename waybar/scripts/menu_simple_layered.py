#!/usr/bin/env python3
import gi
import sys
import subprocess
import signal
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib, Gdk, Gtk4LayerShell

# Ctrl+C quits
signal.signal(signal.SIGINT, lambda *a: Gtk.main_quit() if hasattr(Gtk, "main_quit") else sys.exit(0))

class WaybarMenu:
    def __init__(self):
        self.app = Gtk.Application(application_id='com.waybar.menu')
        self.app.connect('activate', self.on_activate)

        # Top section icon buttons (circular)
        self.top_icons_left = [

            {'icon': '', 'command': 'hyprpicker -a'},
            {'icon': '', 'command': 'grimblast copy area'},

        ]

        self.top_icons_right = [
            {'icon': '󰌾', 'command': 'systemctl reboot'},
            {'icon': '󰐥', 'command': 'systemctl poweroff'},
        ]

        # Bottom section pill modules
        self.bottom_modules = [
            {'icon': '󰖩', 'label': 'Wired', 'command': 'nmcli radio wifi toggle', 'size': 'large'},
            {'icon': '󰌾', 'label': 'Power Mode', 'subtitle': 'Balanced', 'command': 'powerprofilesctl set balanced', 'size': 'large'},
            {'icon': '󰃛', 'label': 'Dark Style', 'command': 'gsettings set org.gnome.desktop.interface gtk-theme Adwaita-dark', 'size': 'large'},
            {'icon': '󰘳', 'label': 'Caffeine', 'command': 'caffeine toggle', 'size': 'small'},
            {'icon': '󰍉', 'label': 'Location', 'command': 'hyprsunset --temperature 5000', 'size': 'medium'},
            {'icon': '󰄀', 'label': 'Camera', 'command': 'cheese', 'size': 'large'},
            {'icon': '󰍬', 'label': 'Microphone', 'command': 'pavucontrol', 'size': 'medium'},
        ]

        self.window = None
        self.slider_window = None

    def on_activate(self, app):
        self.create_main_window()

    def create_main_window(self):
        # Create main window
        self.window = Gtk.ApplicationWindow(application=self.app)
        self.window.set_title("waybar-menu")
        self.window.set_default_size(200, 300)  # Taller for sliders
        self.window.set_resizable(False)
        self.window.set_decorated(False)

        # Make the window itself transparent and have round corners
        self.window.add_css_class('main-window')

        # Initialize Layer Shell for top-right positioning
        Gtk4LayerShell.init_for_window(self.window)
        Gtk4LayerShell.set_layer(self.window, Gtk4LayerShell.Layer.OVERLAY)  # Use OVERLAY layer to be above TOP layer
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.RIGHT, True)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.TOP, 10)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.RIGHT, 10)

        # Enable keyboard interactivity for layer shell
        Gtk4LayerShell.set_keyboard_mode(self.window, Gtk4LayerShell.KeyboardMode.ON_DEMAND)

        # Load CSS
        self.load_css()

        # Create main container that fills the entire window
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.add_css_class('main-container')
        main_box.set_margin_top(0)
        main_box.set_margin_bottom(0)
        main_box.set_margin_start(0)
        main_box.set_margin_end(0)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)

        # Section 1: Top circular icon buttons
        top_section = self.create_top_icons_section()
        main_box.append(top_section)

        # Section 2: Inline sliders
        sliders_section = self.create_sliders_section()
        main_box.append(sliders_section)

        # Section 3: Bottom pill modules
        bottom_section = self.create_bottom_modules_section()
        main_box.append(bottom_section)

        self.window.set_child(main_box)

        # Connect escape key to close
        key_controller = Gtk.EventControllerKey()
        key_controller.connect('key-pressed', self.on_key_pressed)
        self.window.add_controller(key_controller)

        # Add click controller for the window itself
        click_controller = Gtk.GestureClick()
        click_controller.connect('pressed', self.on_window_clicked)
        self.window.add_controller(click_controller)

        # Create invisible overlay for outside click detection
        self.create_click_overlay()

        # Show window and request focus
        GLib.idle_add(self.present_and_focus)

    def create_top_icons_section(self):
        """Create the top section with three columns: left icons, empty middle, right icons"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        section_box.add_css_class('top-icons-section')
        section_box.set_homogeneous(True)  # Equal width columns

        # Left column - icons
        left_column = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        left_column.set_halign(Gtk.Align.START)
        left_column.set_hexpand(True)

        for item in self.top_icons_left:
            button = self.create_circular_icon_button(item)
            left_column.append(button)

        # Middle column - empty space
        middle_column = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        middle_column.set_hexpand(True)

        # Right column - icons
        right_column = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        right_column.set_halign(Gtk.Align.END)
        right_column.set_hexpand(True)

        for item in self.top_icons_right:
            button = self.create_circular_icon_button(item)
            right_column.append(button)

        section_box.append(left_column)
        section_box.append(middle_column)
        section_box.append(right_column)

        return section_box

    def create_sliders_section(self):
        """Create the middle section with inline sliders"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section_box.add_css_class('sliders-section')

        # Volume slider
        volume_box = self.create_inline_slider("󰕾", self.get_volume_value, self.set_volume_value)
        section_box.append(volume_box)

        # Brightness slider
        brightness_box = self.create_inline_slider("", self.get_brightness_value, self.set_brightness_value)
        section_box.append(brightness_box)

        return section_box

    def create_bottom_modules_section(self):
        """Create the bottom section with pill-shaped modules in a stable two-column grid"""
        section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        section_box.add_css_class('bottom-modules-section')

        # Use a proper grid for stable two-column layout
        grid = Gtk.Grid()
        grid.set_column_spacing(8)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(True)  # Equal column widths

        # Row 0: Wired (left) + Power Mode (right)
        wired_btn = self.create_pill_module(self.bottom_modules[0])
        power_btn = self.create_pill_module(self.bottom_modules[1])
        grid.attach(wired_btn, 0, 0, 1, 1)  # column 0, row 0
        grid.attach(power_btn, 1, 0, 1, 1)  # column 1, row 0

        # Row 1: Dark Style (left) + Caffeine (right)
        dark_btn = self.create_pill_module(self.bottom_modules[2])
        caffeine_btn = self.create_pill_module(self.bottom_modules[3])
        grid.attach(dark_btn, 0, 1, 1, 1)   # column 0, row 1
        grid.attach(caffeine_btn, 1, 1, 1, 1) # column 1, row 1

        # Row 2: Location (left) + Camera (right)
        location_btn = self.create_pill_module(self.bottom_modules[4])
        camera_btn = self.create_pill_module(self.bottom_modules[5])
        grid.attach(location_btn, 0, 2, 1, 1) # column 0, row 2
        grid.attach(camera_btn, 1, 2, 1, 1)   # column 1, row 2

        section_box.append(grid)
        return section_box

    def create_circular_icon_button(self, item):
        """Create a circular icon button for the top section"""
        button = Gtk.Button()
        button.add_css_class('circular-icon-button')
        button.set_size_request(35, 35)

        icon_label = Gtk.Label(label=item['icon'])
        icon_label.add_css_class('circular-icon')
        button.set_child(icon_label)

        button.connect('clicked', self.on_icon_button_clicked, item)
        return button

    def create_inline_slider(self, icon, get_func, set_func):
        """Create an inline slider with icon on the left"""
        slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        slider_box.add_css_class('inline-slider')

        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('slider-icon')
        icon_label.set_size_request(20, 20)
        slider_box.append(icon_label)

        # Slider
        current_value = get_func()
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        slider.set_value(current_value)
        slider.add_css_class('inline-slider-bar')
        slider.set_hexpand(True)
        slider.set_draw_value(False)
        slider.connect('value-changed', lambda s: set_func(int(s.get_value())))
        slider_box.append(slider)

        return slider_box

    def create_pill_module(self, item):
        """Create a pill-shaped module button"""
        button = Gtk.Button()
        button.add_css_class('pill-module')
        button.add_css_class(f'pill-{item["size"]}')

        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        content_box.set_halign(Gtk.Align.START)
        content_box.set_valign(Gtk.Align.CENTER)

        # Icon
        icon_label = Gtk.Label(label=item['icon'])
        icon_label.add_css_class('pill-icon')
        content_box.append(icon_label)

        # Text content
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Main label
        main_label = Gtk.Label(label=item['label'])
        main_label.add_css_class('pill-label')
        main_label.set_halign(Gtk.Align.START)
        text_box.append(main_label)

        # Subtitle if available
        if 'subtitle' in item:
            sub_label = Gtk.Label(label=item['subtitle'])
            sub_label.add_css_class('pill-subtitle')
            sub_label.set_halign(Gtk.Align.START)
            text_box.append(sub_label)

        content_box.append(text_box)
        button.set_child(content_box)

        button.connect('clicked', self.on_pill_button_clicked, item)
        return button

    def create_slider_control(self, label, icon, get_func, set_func):
        # Create container for this slider
        slider_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        slider_box.add_css_class('slider-control')

        # Header with icon and label
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.set_halign(Gtk.Align.START)

        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class('slider-icon')
        header_box.append(icon_label)

        title_label = Gtk.Label(label=label)
        title_label.add_css_class('slider-label')
        header_box.append(title_label)

        # Current value
        current_value = get_func()
        value_label = Gtk.Label(label=f"{current_value}%")
        value_label.add_css_class('slider-value')
        value_label.set_halign(Gtk.Align.END)
        header_box.append(value_label)

        slider_box.append(header_box)

        # Slider
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        slider.set_value(current_value)
        slider.add_css_class('slider')
        slider.set_hexpand(True)
        slider.connect(
            'value-changed',
            lambda s: self.on_slider_changed(s, value_label, set_func)
        )
        slider_box.append(slider)

        return slider_box

    def on_slider_changed(self, slider, value_label, set_func):
        value = int(slider.get_value())
        value_label.set_text(f"{value}%")
        set_func(value)

    def create_menu_button(self, item):
        button = Gtk.Button()
        button.add_css_class('menu-button')

        # Add special styling for certain button types (GNOME style)
        if item['label'] in ['Logout', 'Poweroff']:
            button.add_css_class('destructive')
        elif item['label'] in ['Updates']:
            button.add_css_class('suggested')

        # Create button content with icon and label
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        # Icon
        icon_label = Gtk.Label(label=item['icon'])
        icon_label.add_css_class('menu-icon')
        box.append(icon_label)

        # Text
        text_label = Gtk.Label(label=item['label'])
        text_label.add_css_class('menu-text')
        box.append(text_label)

        button.set_child(box)

        # Connect click handler
        button.connect('clicked', self.on_button_clicked, item)
        return button

    def on_icon_button_clicked(self, button, item):
        """Handle clicks on circular icon buttons"""
        command = item['command']
        try:
            subprocess.Popen(command, shell=True)
            self.close_application()
        except Exception as e:
            print(f"Error executing command: {e}")

    def on_pill_button_clicked(self, button, item):
        """Handle clicks on pill module buttons"""
        command = item['command']
        try:
            subprocess.Popen(command, shell=True)
            self.close_application()
        except Exception as e:
            print(f"Error executing command: {e}")

    def on_button_clicked(self, button, item):
        command = item['command']
        # Execute command
        try:
            subprocess.Popen(command, shell=True)
            self.close_application()
        except Exception as e:
            print(f"Error executing command: {e}")

    def get_brightness_value(self):
        try:
            current = subprocess.check_output(['brightnessctl', 'get']).decode().strip()
            max_val = subprocess.check_output(['brightnessctl', 'max']).decode().strip()
            return int((int(current) / int(max_val)) * 100)
        except:
            return 50

    def set_brightness_value(self, value):
        try:
            subprocess.run(['brightnessctl', 'set', f'{value}%'], check=True)
        except:
            pass

    def get_volume_value(self):
        try:
            output = subprocess.check_output(['pamixer', '--get-volume']).decode().strip()
            return int(output)
        except:
            return 50

    def set_volume_value(self, value):
        try:
            subprocess.run(['pamixer', '--set-volume', str(value)], check=True)
        except:
            pass

    def present_and_focus(self):
        """Present the window and grab focus/keyboard input"""
        self.window.present()
        # Force focus grab for layer shell window
        self.window.set_can_focus(True)
        self.window.grab_focus()
        return False

    def create_click_overlay(self):
        """Create an invisible overlay window to catch outside clicks"""
        self.overlay_window = Gtk.ApplicationWindow(application=self.app)
        self.overlay_window.set_title("click-overlay")
        self.overlay_window.set_decorated(False)
        self.overlay_window.set_resizable(True)  # Allow resizing

        # Get screen dimensions
        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0)  # Primary monitor
        geometry = monitor.get_geometry()
        screen_width = geometry.width
        screen_height = geometry.height

        # Set window to full screen size
        self.overlay_window.set_default_size(screen_width, screen_height)

        # Initialize as layer shell overlay
        Gtk4LayerShell.init_for_window(self.overlay_window)
        Gtk4LayerShell.set_layer(self.overlay_window, Gtk4LayerShell.Layer.TOP)  # Use TOP layer to be above other apps

        # Anchor to all edges to fill screen
        Gtk4LayerShell.set_anchor(self.overlay_window, Gtk4LayerShell.Edge.TOP, True)
        Gtk4LayerShell.set_anchor(self.overlay_window, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_anchor(self.overlay_window, Gtk4LayerShell.Edge.LEFT, True)
        Gtk4LayerShell.set_anchor(self.overlay_window, Gtk4LayerShell.Edge.RIGHT, True)

        # Set margins to 0 to ensure full coverage
        Gtk4LayerShell.set_margin(self.overlay_window, Gtk4LayerShell.Edge.TOP, 0)
        Gtk4LayerShell.set_margin(self.overlay_window, Gtk4LayerShell.Edge.BOTTOM, 0)
        Gtk4LayerShell.set_margin(self.overlay_window, Gtk4LayerShell.Edge.LEFT, 0)
        Gtk4LayerShell.set_margin(self.overlay_window, Gtk4LayerShell.Edge.RIGHT, 0)

        # Set exclusive zone to 0 so it doesn't interfere
        Gtk4LayerShell.set_exclusive_zone(self.overlay_window, 0)

        # Create an invisible box to fill the overlay
        overlay_box = Gtk.Box()
        overlay_box.set_hexpand(True)
        overlay_box.set_vexpand(True)
        overlay_box.set_size_request(screen_width, screen_height)
        self.overlay_window.set_child(overlay_box)

        # Make it nearly invisible but clickable
        self.overlay_window.set_opacity(0.01)  # Nearly invisible but still functional

        # Add click detection to the overlay window itself
        overlay_click = Gtk.GestureClick()
        overlay_click.connect('pressed', self.on_overlay_clicked)
        self.overlay_window.add_controller(overlay_click)

        # Also add click detection to the box
        box_click = Gtk.GestureClick()
        box_click.connect('pressed', self.on_overlay_clicked)
        overlay_box.add_controller(box_click)

        # Show overlay behind main window
        GLib.idle_add(self.show_overlay)

    def show_overlay(self):
        """Show the overlay window"""
        self.overlay_window.present()
        # Immediately present main window on top - no delay needed with proper layering
        if self.window:
            self.window.present()
        return False

    def ensure_main_window_on_top(self):
        """Ensure main window stays on top of overlay"""
        if self.window:
            self.window.present()
        return False

    def on_window_clicked(self, gesture, n_press, x, y):
        """Handle clicks on the main window - don't close"""
        return True  # Event handled, don't propagate

    def on_overlay_clicked(self, gesture, n_press, x, y):
        """Handle clicks on the overlay (outside main window) - close menu"""
        self.close_application()
        return True

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:  # Use Gdk.KEY_Escape instead of raw value
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
        self.load_default_css(css_provider)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def load_default_css(self, css_provider):
        css_provider.load_from_data(b"""
        /* Window styling - remove default background and borders */
        window.main-window {
          background: #363644;
          border-radius: 12px;

        }

        /* Remove any default styling from overlay and containers */
        overlay {
          background: transparent;
          border: none;
          outline: none;
        }

        /* Main container with round borders - fills entire window */
        .main-container {
        box-shadow:
          background: #363644;
          padding: 10px;
          color: white;
          font-family: "JetBrainsMono Nerd Font", monospace;
          margin: 0;
        }

        /* Top Icons Section */
        .top-icons-section {

        }

        .circular-icon-button {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          border: none;
          transition: all 0.2s ease;

        }

        .circular-icon-button:hover {
          background: rgba(255, 255, 255, 0.3);

        }

        .circular-icon {
          font-size: 15px;
          color: white;
          font-weight: bold;

        }

        /* Sliders Section */
        .sliders-section {
          # margin: 8px 0;
        }

        .inline-slider {
           # background: rgba(255, 255, 255, 0.15);
          # border-radius: 18px;
          # padding: 8px 10px;
          # margin: 4px 0;
        }

        .slider-icon {
          font-size: 16px;
          color: white;
          font-weight: bold;
        }

        .inline-slider-bar trough {
          background: rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          border:none;
          min-height: 2px;
        }

        .inline-slider-bar highlight {
          background: linear-gradient(90deg, #ff6b9d, #ff8a80);
          border-radius: 8px;
        }

        .inline-slider-bar slider {
          background: white;
          border: none;
          border-radius: 50%;
          min-width: 14px;
          min-height: 14px;
          margin: -5px;
        }

        /* Bottom Modules Section */
        .bottom-modules-section {
          # margin-top: 6px;
        }

        .pill-module {
          border-radius: 25px;
          border: none;
          padding: 0 15px;
          transition: all 0.2s ease;
          font-weight: 1000;
          margin: 2px;
        }

        .pill-large {
          background: linear-gradient(135deg, #ff6b9d, #ff8a80);
          color: white;
          min-height: 32px;
        }

        .pill-medium {
          background: rgba(255, 255, 255, 0.25);
          color: white;
          min-height: 30px;
        }

        .pill-small {
          background: rgba(255, 255, 255, 0.2);
          color: white;
          min-height: 28px;
        }

        .pill-module:hover {

          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }

        .pill-icon {
          font-size: 14px;
          font-weight: bold;
        }

        .pill-label {
          font-size: 12px;
          font-weight: bold;
        }

        .pill-subtitle {
          font-size: 9px;
          opacity: 0.8;
        }



        """)

    def run(self):
        return self.app.run(sys.argv)


if __name__ == "__main__":
    menu = WaybarMenu()
    menu.run()
