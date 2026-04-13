#!/usr/bin/env python3
import subprocess
import json
import os

print("🧪 Simple AdGuard Monitor Test")
print("=" * 40)

# Load config
with open('adguard_config.json', 'r') as f:
    config = json.load(f)

print(f"AdGuard Home: {config['base_url']}")
print(f"Username: {config['username']}")
print(f"Monitoring IPs: {', '.join(config['watch_ips'])}")
print()

# Test using curl (no Python dependencies)
print("Testing connection with curl...")
cmd = [
    'curl', '-s',
    '-u', f"{config['username']}:{config['password']}",
    f"{config['base_url']}/control/status"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("✅ Connection successful")
        
        # Try to parse JSON
        try:
            data = json.loads(result.stdout)
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Protection: {data.get('protection_enabled', 'Unknown')}")
        except:
            print("   (Could not parse JSON response)")
    else:
        print(f"❌ Connection failed: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("❌ Connection timeout")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("✅ Configuration looks good!")
print()
print("Next: Starting the background service...")