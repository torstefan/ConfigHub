#!/usr/bin/env python3
"""
Verification script for VLAN configuration on Catalyst Distribution switches.
Usage: verify_vlan.py <hostname> <mgmt_ip> <vlan_id>
"""

import sys
import subprocess
import yaml
import os
from typing import Dict, List

def load_vlan_config(node_path: str) -> List[Dict]:
    """Load VLAN configuration from vars/base_config.yml"""
    config_path = os.path.join(node_path, 'vars', 'base_config.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['vlans']

def verify_vlan_connectivity(hostname: str, mgmt_ip: str, vlan_id: str) -> None:
    """Verify VLAN configuration and connectivity"""
    # Find VLAN in configuration
    node_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vlans = load_vlan_config(node_path)
    
    target_vlan = None
    for vlan in vlans:
        if str(vlan['id']) == vlan_id:
            target_vlan = vlan
            break
    
    if not target_vlan:
        print(f"ERROR: VLAN {vlan_id} not found in configuration")
        sys.exit(1)
    
    # Check if VLAN interface exists (for routed VLANs)
    vlan_interface = f"Vlan{vlan_id}"
    interfaces_config = yaml.safe_load(open(os.path.join(node_path, 'vars', 'base_config.yml')))['interfaces']
    
    for interface in interfaces_config:
        if interface['name'] == vlan_interface:
            # Try to ping the VLAN interface IP
            try:
                result = subprocess.run(['ping', '-c', '4', interface['ip_address']], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"OK: VLAN {vlan_id} ({target_vlan['name']}) interface is reachable")
                    sys.exit(0)
                else:
                    print(f"ERROR: VLAN {vlan_id} ({target_vlan['name']}) interface is not reachable")
                    print(f"Ping output:\n{result.stdout}")
                    sys.exit(1)
            except Exception as e:
                print(f"ERROR: Failed to verify VLAN {vlan_id}: {str(e)}")
                sys.exit(1)
    
    # If VLAN has no interface, just report it exists in config
    print(f"OK: VLAN {vlan_id} ({target_vlan['name']}) exists in configuration")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: verify_vlan.py <hostname> <mgmt_ip> <vlan_id>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    mgmt_ip = sys.argv[2]
    vlan_id = sys.argv[3]
    
    verify_vlan_connectivity(hostname, mgmt_ip, vlan_id) 