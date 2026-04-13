#!/usr/bin/env python3
"""
Interactive configuration wizard for AdGuard Home DNS Monitor
"""

import json
import getpass
import os
import sys

def configure_monitor():
    print("🎯 AdGuard Home DNS Monitor - Configuration Wizard")
    print("=" * 50)
    
    config = {}
    
    # Base URL
    print("\n1. AdGuard Home Connection")
    print(f"   Detected at: http://192.168.7.251")
    use_default = input(f"   Use this address? (Y/n): ").strip().lower()
    
    if use_default in ['', 'y', 'yes']:
        config['base_url'] = "http://192.168.7.251"
    else:
        config['base_url'] = input("   Enter AdGuard Home URL (e.g., http://192.168.1.1:3000): ").strip()
    
    # Credentials
    print("\n2. Authentication")
    config['username'] = input("   Username [admin]: ").strip() or "admin"
    config['password'] = getpass.getpass("   Password: ")
    
    # IP addresses to monitor
    print("\n3. Devices to Monitor")
    print("   Your current IP: 192.168.7.114")
    print("   Run './find_devices.sh' to see other devices on your network")
    
    ips = []
    while True:
        ip = input(f"   Enter IP address to monitor (or press Enter when done): ").strip()
        if not ip:
            break
        if ip not in ips:
            ips.append(ip)
            print(f"     Added: {ip}")
    
    if not ips:
        print("   ⚠️  No IPs added. Using example IPs.")
        ips = ["192.168.7.100", "192.168.7.101"]
    
    config['watch_ips'] = ips
    
    # Educational domains
    print("\n4. Educational Domains")
    print("   Default file includes 200+ educational domains")
    use_default_domains = input("   Use default educational domains? (Y/n): ").strip().lower()
    
    if use_default_domains in ['', 'y', 'yes']:
        config['educational_domains_file'] = "educational_domains.txt"
    else:
        custom_file = input("   Enter path to custom domains file: ").strip()
        config['educational_domains_file'] = custom_file
    
    # Notification channel
    print("\n5. Notifications")
    print("   Choose how to receive alerts:")
    print("   1. Telegram (via OpenClaw)")
    print("   2. Console output")
    print("   3. Log file")
    
    choice = input("   Select option (1-3) [1]: ").strip() or "1"
    
    if choice == "1":
        config['notification_channel'] = "telegram"
    elif choice == "2":
        config['notification_channel'] = "stdout"
    elif choice == "3":
        config['notification_channel'] = "file"
    else:
        config['notification_channel'] = "telegram"
    
    # Save configuration
    config_file = "adguard_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_file}")
    
    # Show summary
    print("\n📋 Configuration Summary:")
    print(f"   AdGuard Home: {config['base_url']}")
    print(f"   Username: {config['username']}")
    print(f"   Monitoring IPs: {', '.join(config['watch_ips'])}")
    print(f"   Domains file: {config['educational_domains_file']}")
    print(f"   Notifications: {config['notification_channel']}")
    
    # Offer to test
    print("\n🧪 Test Configuration")
    test_now = input("   Test connection now? (Y/n): ").strip().lower()
    
    if test_now in ['', 'y', 'yes']:
        print("\nTesting connection...")
        
        import requests
        session = requests.Session()
        session.auth = (config['username'], config['password'])
        
        try:
            response = session.get(f"{config['base_url']}/control/status", timeout=10)
            if response.status_code == 200:
                print("✅ Connection successful!")
                
                # Test query log
                params = {'limit': 2}
                response = session.get(f"{config['base_url']}/control/querylog", params=params, timeout=10)
                if response.status_code == 200:
                    print("✅ Query log accessible")
                else:
                    print("⚠️  Query log access issue")
            else:
                print(f"❌ Connection failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Next steps
    print("\n🚀 Next Steps:")
    print("   1. Review configuration: cat adguard_config.json")
    print("   2. Test connection: python test_adguard_quick.py")
    print("   3. Run monitor: python adguard_monitor.py --config adguard_config.json")
    print("   4. Find devices: ./find_devices.sh")
    print("\n📚 See SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    configure_monitor()