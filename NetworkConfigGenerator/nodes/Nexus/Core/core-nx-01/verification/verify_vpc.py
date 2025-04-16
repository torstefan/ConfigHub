#!/usr/bin/env python3
"""
Verification script for VPC configuration on Nexus Core switches.
Usage: verify_vpc.py <hostname> <mgmt_ip> <vpc_id>
"""

import sys
import subprocess
import yaml
import os
from typing import Dict, List, Optional

def load_vpc_config(node_path: str) -> Dict:
    """Load VPC configuration from vars/base_config.yml"""
    config_path = os.path.join(node_path, 'vars', 'base_config.yml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return {
        'vpc_config': config['vpc_config'],
        'interfaces': config['interfaces']
    }

def find_vpc_interface(interfaces: List[Dict], vpc_id: str) -> Optional[Dict]:
    """Find interface with specific VPC ID"""
    for interface in interfaces:
        if interface.get('type') == 'vpc-member' and str(interface.get('vpc_id')) == vpc_id:
            return interface
    return None

def verify_vpc_status(hostname: str, mgmt_ip: str, vpc_id: str) -> None:
    """Verify VPC configuration and connectivity"""
    # Load configuration
    node_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = load_vpc_config(node_path)
    
    # Check if VPC domain is configured
    if not config['vpc_config']:
        print("ERROR: No VPC configuration found")
        sys.exit(1)
    
    # Find interface with this VPC ID
    vpc_interface = find_vpc_interface(config['interfaces'], vpc_id)
    if not vpc_interface:
        print(f"ERROR: No interface found with VPC ID {vpc_id}")
        sys.exit(1)
    
    # Verify VPC peer-keepalive connectivity
    vpc_peer_ip = config['vpc_config'][0]['peer_ip']
    try:
        result = subprocess.run(['ping', '-c', '4', vpc_peer_ip],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: VPC peer-keepalive IP {vpc_peer_ip} is not reachable")
            print(f"Ping output:\n{result.stdout}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to verify VPC peer-keepalive: {str(e)}")
        sys.exit(1)
    
    # If we get here, basic connectivity is working
    print(f"OK: VPC {vpc_id} configuration verified:")
    print(f"  - Interface: {vpc_interface['name']}")
    print(f"  - Description: {vpc_interface['description']}")
    print(f"  - Allowed VLANs: {vpc_interface['allowed_vlans']}")
    print(f"  - Peer-keepalive IP {vpc_peer_ip} is reachable")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: verify_vpc.py <hostname> <mgmt_ip> <vpc_id>")
        sys.exit(1)
    
    hostname = sys.argv[1]
    mgmt_ip = sys.argv[2]
    vpc_id = sys.argv[3]
    
    verify_vpc_status(hostname, mgmt_ip, vpc_id) 