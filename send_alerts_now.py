#!/usr/bin/env python3
"""
Send AdGuard alerts now via OpenClaw.
Run this to send any pending alerts immediately.
"""

import json
import os
import hashlib
from datetime import datetime

def get_message_hash(message: str) -> str:
    """Create hash for message."""
    return hashlib.md5(message.encode()).hexdigest()[:16]

def read_alerts(queue_file="telegram_smart_queue.log"):
    """Read alerts from queue file."""
    if not os.path.exists(queue_file):
        return []
    
    with open(queue_file, 'r') as f:
        content = f.read()
    
    alerts = []
    raw_messages = content.split('---\n')
    
    for raw_msg in raw_messages:
        if raw_msg.strip():
            lines = raw_msg.strip().split('\n')
            if len(lines) >= 2:
                message = '\n'.join(lines[1:]).strip()
                if message and "🚨" in message:
                    alerts.append(message)
    
    return alerts

def load_sent_hashes(sent_file="openclaw_sent_alerts.log"):
    """Load already sent message hashes."""
    sent_hashes = set()
    if os.path.exists(sent_file):
        with open(sent_file, 'r') as f:
            for line in f:
                if line.strip():
                    sent_hashes.add(line.strip())
    return sent_hashes

def mark_as_sent(message_hash: str, sent_file="openclaw_sent_alerts.log"):
    """Mark message as sent."""
    with open(sent_file, 'a') as f:
        f.write(f"{message_hash}\n")

def main():
    print("🔍 Checking for AdGuard alerts...")
    print("=" * 40)
    
    # Read alerts
    alerts = read_alerts()
    
    if not alerts:
        print("✅ No pending alerts found")
        return
    
    print(f"📨 Found {len(alerts)} alert(s) in queue")
    print()
    
    # Load sent hashes
    sent_hashes = load_sent_hashes()
    
    new_alerts = []
    for alert in alerts:
        alert_hash = get_message_hash(alert)
        if alert_hash not in sent_hashes:
            new_alerts.append(alert)
    
    if not new_alerts:
        print("✅ All alerts have already been sent")
        return
    
    print(f"📤 {len(new_alerts)} new alert(s) to send:")
    print("=" * 40)
    
    for i, alert in enumerate(new_alerts, 1):
        print(f"\nAlert {i}:")
        print("-" * 20)
        print(alert)
        
        # Mark as sent
        alert_hash = get_message_hash(alert)
        mark_as_sent(alert_hash)
        
        print(f"✅ Marked as sent (hash: {alert_hash})")
    
    print()
    print("=" * 40)
    print(f"✅ Processed {len(new_alerts)} new alert(s)")
    print()
    print("📋 Next steps:")
    print("   1. I'll send these alerts to you in Telegram")
    print("   2. Check your Telegram for the alerts")
    print("   3. Run this again to check for new alerts")
    print()
    print("🔄 To automate: Run this script every minute")

if __name__ == "__main__":
    main()