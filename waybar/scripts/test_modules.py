#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

app = Gtk.Application()

def on_activate(app):
    window = Gtk.ApplicationWindow(application=app)
    window.set_title("Test")
    window.set_default_size(300, 200)
    
    # Test capsule button
    button = Gtk.Button()
    button.add_css_class('capsule-module')
    
    content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    
    icon_label = Gtk.Label(label="📶")
    content_box.append(icon_label)
    
    title_label = Gtk.Label(label="Wi-Fi")
    content_box.append(title_label)
    
    button.set_child(content_box)
    window.set_child(button)
    
    window.present()

app.connect('activate', on_activate)
app.run()
