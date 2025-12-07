#!/usr/bin/env python3
import subprocess
import re

def get_bluetooth_status():
    """Get bluetooth power status"""
    try:
        result = subprocess.run(['bluetoothctl', 'show'], capture_output=True, text=True)
        return 'Powered: yes' in result.stdout
    except:
        return False

def get_bluetooth_devices():
    """Get only currently connected Bluetooth devices (optimized for performance)"""
    # Skip expensive operations only on very first call
    if not hasattr(get_bluetooth_devices, '_first_call_done'):
        get_bluetooth_devices._first_call_done = True
        return []  # Return empty list for fast initial load
        
    try:
        devices = []
        
        # Only get connected devices to avoid slow scanning
        paired_result = subprocess.run(['bluetoothctl', 'devices', 'Connected'], 
                                     capture_output=True, text=True, timeout=2)
        
        for line in paired_result.stdout.strip().split('\n'):
            if line.startswith('Device'):
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    devices.append({
                        'mac': parts[1],
                        'name': parts[2],
                        'connected': True,
                        'paired': True
                    })
        
        return devices
    except:
        return []

def get_network_connections():
    """Get both WiFi and wired network connections - optimized for fast loading"""
    # Skip expensive operations only on very first call
    if not hasattr(get_network_connections, '_first_call_done'):
        get_network_connections._first_call_done = True
        return []  # Return empty list for fast initial load
    
    try:
        connections = []
        
        # Get active connections
        active_result = subprocess.run(['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
                                     capture_output=True, text=True, timeout=2)
        
        active_connections = {}
        for line in active_result.stdout.strip().split('\n'):
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    name = parts[0]
                    conn_type = parts[1]
                    device = parts[2]
                    active_connections[name] = {'type': conn_type, 'device': device}
        
        # Add active wired connections first
        for name, info in active_connections.items():
            if '802-3-ethernet' in info['type'] or 'ethernet' in info['type'].lower():
                connections.append({
                    'name': 'Wired',  # Generic label instead of connection name
                    'real_name': name,  # Keep real name for connection operations
                    'type': 'wired',
                    'signal': '100',  # Wired always full signal
                    'secure': 'wired',
                    'connected': True,
                    'device': info['device']
                })
        
        # Get WiFi networks (both connected and available)
        try:
            wifi_result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'dev', 'wifi'], 
                                       capture_output=True, text=True, timeout=3)
            seen_networks = set()
            
            for line in wifi_result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 2 and parts[0] and parts[0] not in seen_networks:
                        network_name = parts[0]
                        is_connected = network_name in active_connections and '802-11-wireless' in active_connections[network_name]['type']
                        
                        connections.append({
                            'name': network_name,
                            'type': 'wifi',
                            'signal': parts[1] if len(parts) > 1 else '0',
                            'secure': 'secured' if len(parts) > 2 and parts[2] else 'open',
                            'connected': is_connected,
                            'device': active_connections.get(network_name, {}).get('device', '')
                        })
                        seen_networks.add(network_name)
        except:
            pass
        
        return connections[:10]  # Limit to 10 connections
    except:
        return []

def get_network_status():
    """Get current network status - prioritize wired over WiFi"""
    try:
        connections = get_network_connections()
        
        # Check for active wired connection first (priority)
        for conn in connections:
            if conn['connected'] and conn['type'] == 'wired':
                return {
                    'connected': True,
                    'name': conn['name'],
                    'type': 'wired',
                    'icon': '󰈀'  # Wired icon
                }
        
        # Check for active WiFi connection
        for conn in connections:
            if conn['connected'] and conn['type'] == 'wifi':
                return {
                    'connected': True,
                    'name': conn['name'],
                    'type': 'wifi',
                    'icon': '󰤨'  # WiFi icon
                }
        
        # No active connections
        return {
            'connected': False,
            'name': 'Not Connected',
            'type': 'none',
            'icon': '󰤭'  # Disconnected icon
        }
    except:
        return {'connected': False, 'name': 'Unknown', 'type': 'none', 'icon': '󰤭'}

def get_power_profiles():
    """Get available power profiles"""
    try:
        result = subprocess.run(['powerprofilesctl', 'list'], capture_output=True, text=True)
        profiles = []
        current = None
        
        # Get current profile
        current_result = subprocess.run(['powerprofilesctl', 'get'], capture_output=True, text=True)
        current = current_result.stdout.strip()
        
        # Parse available profiles
        for line in result.stdout.split('\n'):
            if 'Profile' in line and ':' in line:
                profile_name = line.split(':')[1].strip()
                profiles.append({
                    'name': profile_name,
                    'active': profile_name == current
                })
        return profiles
    except:
        return [
            {'name': 'performance', 'active': False},
            {'name': 'balanced', 'active': True},
            {'name': 'power-saver', 'active': False}
        ]

def get_airplane_mode_status():
    """Get airplane mode status - only true when ALL radios are disabled"""
    try:
        result = subprocess.run(['nmcli', 'radio', 'all'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            # Parse the actual radio states (second line, columns 2 and 4)
            parts = lines[1].split()
            if len(parts) >= 4:
                wifi_state = parts[1]  # WIFI column
                wwan_state = parts[3]  # WWAN column
                # Airplane mode is active when both WiFi and WWAN are disabled
                return wifi_state == 'disabled' and wwan_state == 'disabled'
        return False
    except:
        return False

def get_last_color():
    """Get last picked color from clipboard or file"""
    try:
        result = subprocess.run(['wl-paste'], capture_output=True, text=True)
        color = result.stdout.strip()
        if re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return color
        return '#000000'
    except:
        return '#000000'
    """Get last picked color from clipboard or file"""
    try:
        result = subprocess.run(['wl-paste'], capture_output=True, text=True)
        color = result.stdout.strip()
        if re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return color
        return '#000000'
    except:
        return '#000000'

# Module configuration
MODULES_CONFIG = {
    'header_modules': [
        {
            'id': 'color_picker',
            'icon': '󰏘',
            'command': 'hyprpicker -a',
            'position': 'left',
            'expandable': True,
            'expand_data': {
                'type': 'custom',
                'get_data': get_last_color,
                'template': 'last_color',
                'actions': [
                    {'label': 'Pick New Color', 'command': 'hyprpicker -a', 'icon': '󰏘'},
                    {'label': 'Copy to Clipboard', 'command': 'echo "{data}" | wl-copy', 'icon': '󰆏'}
                ]
            }
        },
        {
            'id': 'settings',
            'icon': '󰒓',
            'command': 'gnome-control-center',
            'position': 'right'
        },
        {
            'id': 'lock',
            'icon': '󰌾',
            'command': 'hyprlock',
            'position': 'right'
        },
        {
            'id': 'power',
            'icon': '󰐥',
            'command': 'systemctl poweroff',
            'position': 'right',
            'css_class': 'power-button',
            'expandable': True,
            'expand_data': {
                'type': 'static_options',
                'options': [
                    {'icon': '󰜉', 'label': 'Restart', 'command': 'systemctl reboot'},
                    {'icon': '󰒲', 'label': 'Sleep', 'command': 'systemctl suspend'},
                    {'icon': '󰍃', 'label': 'Logout', 'command': 'hyprctl dispatch exit'}
                ]
            }
        }
    ],
    'capsule_modules': [
        {
            'row': 1,
            'modules': [
                {
                    'id': 'wifi',
                    'get_icon': lambda: get_network_status()['icon'],
                    'title': 'Network',
                    'get_subtitle': lambda: get_network_status()['name'],
                    'get_active': lambda: get_network_status()['connected'],
                    'expandable': True,
                    'expand_data': {
                        'type': 'dynamic_list',
                        'get_data': get_network_connections,
                        'template': 'network_list'
                    }
                },
                {
                    'id': 'bluetooth',
                    'icon': '󰂯',
                    'title': 'Bluetooth',
                    'get_subtitle': lambda: 'On' if get_bluetooth_status() else 'Off',
                    'get_active': lambda: get_bluetooth_status(),
                    'expandable': True,
                    'expand_data': {
                        'type': 'dynamic_list',
                        'get_data': get_bluetooth_devices,
                        'template': 'device_list'
                    }
                }
            ]
        },
        {
            'row': 2,
            'modules': [
                {
                    'id': 'power_mode',
                    'icon': '󰁹',
                    'title': 'Power Mode',
                    'get_subtitle': lambda: subprocess.run(['powerprofilesctl', 'get'], capture_output=True, text=True).stdout.strip().capitalize(),
                    'get_active': lambda: 'power-saver' in subprocess.run(['powerprofilesctl', 'get'], capture_output=True, text=True).stdout.strip()
                },
                {
                    'id': 'night_light',
                    'icon': '󰖔',
                    'title': 'Night Light',
                    'subtitle': '',
                    'get_active': lambda: subprocess.run(['pgrep', 'hyprsunset'], capture_output=True).returncode == 0,
                    'toggle_command': lambda active: 'pkill hyprsunset' if active else 'hyprsunset --temperature 4000'
                }
            ]
        }
    ]
}
