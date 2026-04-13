#!/usr/bin/env python3
"""
Test the monitor once to verify it works with current configuration
"""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import
try:
    from adguard_monitor import AdGuardMonitor
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import...")
    # Import the module directly
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "adguard_monitor", 
        os.path.join(os.path.dirname(__file__), "adguard_monitor.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    AdGuardMonitor = module.AdGuardMonitor

def test_monitor():
    print("🧪 Testing AdGuard Monitor with current configuration...")
    print("=" * 50)
    
    # Load config
    with open('adguard_config.json', 'r') as f:
        config = json.load(f)
    
    print(f"AdGuard Home: {config['base_url']}")
    print(f"Monitoring IPs: {', '.join(config['watch_ips'])}")
    print(f"Notification channel: {config['notification_channel']}")
    print()
    
    try:
        # Create monitor with stdout notifications for test
        monitor = AdGuardMonitor(
            base_url=config['base_url'],
            username=config['username'],
            password=config['password'],
            watch_ips=config['watch_ips'],
            educational_domains_file=config['educational_domains_file'],
            check_interval=5,
            notification_channel='stdout'  # Use stdout for test
        )
        
        print("✅ Monitor initialized successfully")
        print()
        
        # Get one batch of queries
        print("Fetching recent DNS queries...")
        queries = monitor.get_query_log(limit=20)
        
        if queries:
            print(f"📊 Found {len(queries)} recent queries")
            print()
            
            # Analyze them
            violations = monitor.analyze_queries(queries)
            
            if violations:
                print(f"🚨 Found {len(violations)} potential violations:")
                for i, violation in enumerate(violations, 1):
                    print(f"  {i}. {violation['client_ip']} -> {violation['domain']}")
            else:
                print("✅ No violations found in recent queries")
                print("   (All domains from watched IPs appear educational)")
            
            # Show sample of watched IP queries
            print()
            print("📋 Sample queries from watched IPs:")
            watched_queries = [q for q in queries if q.get('client') in config['watch_ips']]
            
            if watched_queries:
                for i, query in enumerate(watched_queries[:5], 1):
                    client = query.get('client', 'Unknown')
                    domain = query.get('domain', 'Unknown')
                    status = query.get('status', 'Unknown')
                    is_edu = monitor.is_educational_domain(domain)
                    edu_status = "✅ Educational" if is_edu else "🚨 Non-educational"
                    print(f"  {i}. {client} -> {domain} ({status}) - {edu_status}")
            else:
                print("  No recent queries from watched IPs")
                
        else:
            print("⚠️  No queries found in log")
        
        print()
        print("✅ Test completed successfully!")
        print("   The monitor is ready to run as a service")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_monitor()
    sys.exit(0 if success else 1)