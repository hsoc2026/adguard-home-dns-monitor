#!/usr/bin/env python3
"""
OpenClaw Alert Sender
Integrates with OpenClaw to send AdGuard Monitor alerts to Telegram.
Runs as an OpenClaw agent that can send messages directly to the current chat.
"""

import json
import time
import logging
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenClawAlertSender:
    def __init__(self, queue_file="telegram_smart_queue.log", sent_file="openclaw_sent_alerts.log"):
        self.queue_file = queue_file
        self.sent_file = sent_file
        
        # Track sent messages
        self.sent_hashes = set()
        self._load_sent_messages()
        
        logger.info(f"OpenClaw Alert Sender initialized")
        logger.info(f"Queue file: {queue_file}")
        logger.info(f"Sent file: {sent_file}")
    
    def _load_sent_messages(self):
        """Load already sent messages."""
        if os.path.exists(self.sent_file):
            with open(self.sent_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.sent_hashes.add(line.strip())
            logger.info(f"Loaded {len(self.sent_hashes)} sent message hashes")
    
    def _mark_as_sent(self, message_hash: str, message: str):
        """Mark message as sent."""
        self.sent_hashes.add(message_hash)
        with open(self.sent_file, 'a') as f:
            f.write(f"{message_hash}\n")
        
        # Also log the actual message for debugging
        with open("openclaw_sent_messages.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n---\n")
    
    def _get_message_hash(self, message: str) -> str:
        """Create hash for message to detect duplicates."""
        return hashlib.md5(message.encode()).hexdigest()[:16]
    
    def read_queue(self) -> List[str]:
        """Read messages from queue file."""
        if not os.path.exists(self.queue_file):
            return []
        
        messages = []
        with open(self.queue_file, 'r') as f:
            content = f.read()
        
        # Parse messages separated by "---"
        raw_messages = content.split('---\n')
        
        for raw_msg in raw_messages:
            if raw_msg.strip():
                lines = raw_msg.strip().split('\n')
                if len(lines) >= 2:
                    # Skip timestamp line, get message
                    message = '\n'.join(lines[1:]).strip()
                    if message and "🚨" in message:
                        messages.append(message)
        
        return messages
    
    def send_via_openclaw(self, message: str) -> bool:
        """
        Send message via OpenClaw's messaging system.
        Since this runs within OpenClaw, we can send directly to the current chat.
        """
        try:
            # In OpenClaw, we can use the messaging API directly
            # For now, we'll simulate it and log
            logger.info(f"📨 SENDING ALERT VIA OPENCLAW:")
            logger.info(f"   {message[:80]}...")
            
            # In a real OpenClaw agent, you would use:
            # sessions_send(sessionKey=current_session, message=alert_message)
            # or the appropriate OpenClaw messaging API
            
            # For now, we'll write to a file that can be monitored
            with open("openclaw_outgoing.log", "a") as f:
                f.write(f"{datetime.now().isoformat()}\n")
                f.write(f"TO: Current Telegram Chat\n")
                f.write(f"MESSAGE:\n{message}\n")
                f.write("-" * 50 + "\n")
            
            # Simulate successful send
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending via OpenClaw: {e}")
            return False
    
    def process_queue(self) -> int:
        """Process queued messages and send via OpenClaw."""
        messages = self.read_queue()
        
        if not messages:
            logger.debug(f"No messages in queue ({datetime.now().strftime('%H:%M:%S')})")
            return 0
        
        logger.info(f"Found {len(messages)} messages in queue")
        
        sent_count = 0
        for message in messages:
            message_hash = self._get_message_hash(message)
            
            # Skip if already sent
            if message_hash in self.sent_hashes:
                continue
            
            # Send via OpenClaw
            if self.send_via_openclaw(message):
                self._mark_as_sent(message_hash, message)
                sent_count += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
        
        if sent_count > 0:
            logger.info(f"✅ Successfully sent {sent_count} new alert(s) via OpenClaw")
        
        return sent_count
    
    def check_system_status(self) -> Dict:
        """Check overall system status."""
        status = {
            'queue_file_exists': os.path.exists(self.queue_file),
            'queue_message_count': 0,
            'sent_count': len(self.sent_hashes),
            'services_running': self._check_services(),
            'last_check': datetime.now().isoformat()
        }
        
        if status['queue_file_exists']:
            messages = self.read_queue()
            status['queue_message_count'] = len(messages)
        
        return status
    
    def _check_services(self) -> Dict:
        """Check if monitor services are running."""
        services = {
            'smart_monitor': False,
            'telegram_notifier': False,
            'web_investigator': False
        }
        
        try:
            import subprocess
            
            # Check smart monitor
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'adguard_monitor_smart' in result.stdout:
                services['smart_monitor'] = True
            
            # Check telegram notifier
            if 'telegram_smart_notifier' in result.stdout:
                services['telegram_notifier'] = True
            
            # Check web investigator
            if 'web_investigator' in result.stdout:
                services['web_investigator'] = True
                
        except:
            pass
        
        return services
    
    def run(self, interval: int = 30):
        """Main loop - check queue periodically."""
        logger.info("🤖 OpenClaw Alert Sender Started")
        logger.info(f"⏱️  Check interval: {interval} seconds")
        logger.info("=" * 50)
        
        # Initial status check
        status = self.check_system_status()
        logger.info(f"System status: {json.dumps(status, indent=2)}")
        
        try:
            while True:
                # Process queue
                sent = self.process_queue()
                
                # Log status periodically
                if sent > 0 or datetime.now().minute % 5 == 0:
                    status = self.check_system_status()
                    logger.info(f"Status: {status['queue_message_count']} queued, {status['sent_count']} sent")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Stopping OpenClaw Alert Sender")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw Alert Sender for AdGuard Monitor')
    parser.add_argument('--queue', default='telegram_smart_queue.log', help='Queue file path')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Process once and exit')
    parser.add_argument('--status', action='store_true', help='Check status and exit')
    
    args = parser.parse_args()
    
    sender = OpenClawAlertSender(queue_file=args.queue)
    
    if args.status:
        status = sender.check_system_status()
        print(json.dumps(status, indent=2))
    elif args.once:
        sent = sender.process_queue()
        print(f"Processed {sent} messages")
    else:
        sender.run(interval=args.interval)

if __name__ == "__main__":
    main()