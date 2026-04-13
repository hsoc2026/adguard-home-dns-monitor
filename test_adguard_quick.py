#!/usr/bin/env python3
"""
Quick test for AdGuard Home connection
"""

import requests
import getpass

def quick_test():
    base_url = "http://192.168.7.251"
    
    print(f"Testing AdGuard Home at: {base_url}")
    print("-" * 40)
    
    # Get credentials
    username = input("AdGuard Home username [admin]: ").strip() or "admin"
    password = getpass.getpass("AdGuard Home password: ")
    
    # Test connection
    session = requests.Session()
    session.auth = (username, password)
    
    try:
        # Test status endpoint
        print("\nTesting API connection...")
        response = session.get(f"{base_url}/control/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully connected!")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Protection enabled: {data.get('protection_enabled', 'Unknown')}")
            print(f"   DNS queries today: {data.get('dns_queries', {}).get('today', 'Unknown')}")
            
            # Test query log
            print("\nTesting query log access...")
            params = {'limit': 3}
            response = session.get(f"{base_url}/control/querylog", params=params, timeout=10)
            
            if response.status_code == 200:
                query_data = response.json()
                queries = query_data.get('data', [])
                print(f"✅ Query log accessible ({len(queries)} recent queries)")
                
                if queries:
                    print("\nRecent queries:")
                    for i, q in enumerate(queries, 1):
                        client = q.get('client', 'Unknown')
                        domain = q.get('domain', 'Unknown')
                        status = q.get('status', 'Unknown')
                        print(f"  {i}. {client} -> {domain} ({status})")
            else:
                print(f"⚠️  Query log failed: HTTP {response.status_code}")
                
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            if response.status_code == 401:
                print("   Authentication failed - check username/password")
            print(f"   Response: {response.text[:100]}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {base_url}")
        print("   Check if AdGuard Home is running and accessible")
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()