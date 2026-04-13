#!/bin/bash
# Simple script to find devices on local network

echo "🔍 Looking for devices on 192.168.7.0/24 network..."
echo "This may take a minute..."
echo ""

# Quick ping sweep
for i in {1..254}; do
    ip="192.168.7.$i"
    if ping -c 1 -W 1 "$ip" &> /dev/null; then
        # Try to get hostname
        hostname=$(nslookup "$ip" 2>/dev/null | grep "name =" | cut -d'=' -f2 | xargs)
        if [ -z "$hostname" ]; then
            hostname="(no hostname)"
        fi
        
        # Check if it's the current machine
        if [ "$ip" = "192.168.7.114" ]; then
            echo "📍 $ip - This machine $hostname"
        else
            echo "📱 $ip $hostname"
        fi
    fi
done | sort -t. -k4,4n

echo ""
echo "💡 Tip: Add IP addresses you want to monitor to 'watch_ips' in adguard_config.json"
echo "Example: \"watch_ips\": [\"192.168.7.50\", \"192.168.7.75\"]"