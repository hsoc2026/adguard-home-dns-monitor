#!/usr/bin/env python3
"""
Test script to verify AdGuard Home connection and API access.
"""

import requests
import json
import sys

def test_adguard_connection(base_url, username, password):
    """Test connection to AdGuard Home API."""
    print(f"Testing connection to: {base_url}")
    
    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({'Content-Type': 'application/json'})
    
    # Test 1: Status endpoint
    try:
        response = session.get(f"{base_url}/control/status", timeout=10)
        print(f"Status endpoint: HTTP {response.status_code}")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✓ Connected successfully!")
            print(f"  Version: {status_data.get('version')}")
            print(f"  DNS servers: {len(status_data.get('dns_servers', []))}")
            print(f"  Protection enabled: {status_data.get('protection_enabled')}")
        else:
            print(f"✗ Failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed: Cannot connect to {base_url}")
        print("  Check if AdGuard Home is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Connection timeout: Server not responding")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Test 2: Query log endpoint
    try:
        params = {'limit': 5, 'offset': 0}
        response = session.get(f"{base_url}/control/querylog", params=params, timeout=10)
        print(f"\nQuery log endpoint: HTTP {response.status_code}")
        
        if response.status_code == 200:
            query_data = response.json()
            queries = query_data.get('data', [])
            print(f"✓ Query log accessible")
            print(f"  Recent queries: {len(queries)}")
            
            if queries:
                print(f"\nSample queries:")
                for i, query in enumerate(queries[:3], 1):
                    print(f"  {i}. {query.get('client')} -> {query.get('domain')} ({query.get('status')})")
        else:
            print(f"✗ Query log failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Query log error: {e}")
    
    # Test 3: Check authentication
    try:
        # Try without auth
        response = requests.get(f"{base_url}/control/status", timeout=5)
        if response.status_code == 200:
            print(f"\n⚠️  Warning: No authentication required")
            print("  Consider enabling authentication in AdGuard Home settings")
        else:
            print(f"\n✓ Authentication required: Good")
    except:
        pass
    
    return True

def main():
    # Try to load from config file
    config_file = "adguard_config.json"
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        base_url = config.get('base_url', '')
        username = config.get('username', '')
        password = config.get('password', '')
        
        if not all([base_url, username, password]):
            print(f"Missing configuration in {config_file}")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        print("\nPlease provide AdGuard Home details:")
        base_url = input("Base URL (e.g., http://192.168.1.1:3000): ").strip()
        username = input("Username: ").strip()
        password = input("Password: ").strip()
    
    print("=" * 60)
    success = test_adguard_connection(base_url, username, password)
    print("=" * 60)
    
    if success:
        print("\n✅ Connection test successful!")
        print("\nNext steps:")
        print("1. Update watch_ips in adguard_config.json")
        print("2. Customize educational_domains.txt if needed")
        print("3. Run: python adguard_monitor.py --config adguard_config.json")
    else:
        print("\n❌ Connection test failed")
        print("\nTroubleshooting:")
        print("1. Verify AdGuard Home is running")
        print("2. Check IP address and port")
        print("3. Verify username/password")
        print("4. Check firewall/network settings")

if __name__ == "__main__":
    main()