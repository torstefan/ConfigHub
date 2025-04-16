#!/usr/bin/env python3
"""
Verification script for IP connectivity on ASR Core routers.
Usage: verify_ip.py <hostname> <mgmt_ip> <interface_name>
"""

import sys
import subprocess
import yaml
import os

def load_interface_config(node_path):
    """Load interface configuration from vars/base_config.yml"""
    config_path = os.path.join(node_path, 'vars', 'base_config.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['interfaces']

def verify_interface_connectivity(hostname, mgmt_ip, interface_name):
    """Verify interface connectivity using ping"""
    # Find interface IP from configuration
    node_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    interfaces = load_interface_config(node_path)
    
    target_interface = None
    for interface in interfaces:
        if interface['name'] == interface_name:
            target_interface = interface
            break
    
    if not target_interface:
        print(f"ERROR: Interface {interface_name} not found in configuration")
        sys.exit(1)
    
    # Try to ping the interface IP
    try:
        result = subprocess.run(['ping', '-c', '4', target_interface['ip_address']], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK: Interface {interface_name} ({target_interface['ip_address']}) is reachable")
            sys.exit(0)
        else:
            print(f"ERROR: Interface {interface_name} ({target_interface['ip_address']}) is not reachable")
            print(f"Ping output:\n{result.stdout}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to verify interface {interface_name}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: verify_ip.py <hostname> <mgmt_ip> <interface_name>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    mgmt_ip = sys.argv[2]
    interface_name = sys.argv[3]
    
    verify_interface_connectivity(hostname, mgmt_ip, interface_name) 