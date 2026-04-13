#!/usr/bin/env python3
"""
Telegram Notifier Agent for AdGuard Home DNS Monitor
Reads from telegram_queue.log and sends notifications to Telegram via OpenClaw.
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
import subprocess

class TelegramNotifier:
    def __init__(self, queue_file="telegram_queue.log", sent_file="telegram_sent.log", check_interval=10):
        self.queue_file = queue_file
        self.sent_file = sent_file
        self.check_interval = check_interval
        
        # Track which messages we've already sent
        self.sent_messages = set()
        self._load_sent_messages()
    
    def _load_sent_messages(self):
        """Load already sent messages from file."""
        if os.path.exists(self.sent_file):
            with open(self.sent_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.sent_messages.add(line.strip())
    
    def _mark_as_sent(self, message_hash: str):
        """Mark a message as sent."""
        self.sent_messages.add(message_hash)
        with open(self.sent_file, 'a') as f:
            f.write(f"{message_hash}\n")
    
    def _get_message_hash(self, message: str) -> str:
        """Create a simple hash for a message to detect duplicates."""
        import hashlib
        return hashlib.md5(message.encode()).hexdigest()[:16]
    
    def read_queue(self):
        """Read new messages from queue file."""
        if not os.path.exists(self.queue_file):
            return []
        
        messages = []
        with open(self.queue_file, 'r') as f:
            content = f.read()
        
        # Parse messages separated by "---"
        raw_messages = content.split('---\n')
        
        for raw_msg in raw_messages:
            if raw_msg.strip():
                # Extract just the message part (skip timestamp line)
                lines = raw_msg.strip().split('\n')
                if len(lines) >= 2:
                    # Join all lines except the first (timestamp)
                    message = '\n'.join(lines[1:]).strip()
                    if message:
                        messages.append(message)
        
        return messages
    
    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram using OpenClaw CLI."""
        try:
            # Use OpenClaw CLI to send Telegram message
            # Note: This assumes OpenClaw is configured for Telegram
            cmd = [
                '/opt/homebrew/bin/openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--message', message
            ]
            
            print(f"Sending Telegram message: {message[:50]}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Message sent successfully")
                return True
            else:
                print(f"❌ Failed to send message: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Send command timeout")
            return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def process_queue(self):
        """Process all queued messages."""
        messages = self.read_queue()
        
        if not messages:
            print(f"No messages in queue ({datetime.now().strftime('%H:%M:%S')})")
            return 0
        
        sent_count = 0
        for message in messages:
            message_hash = self._get_message_hash(message)
            
            # Skip if already sent
            if message_hash in self.sent_messages:
                continue
            
            # Send to Telegram
            if self.send_telegram_message(message):
                self._mark_as_sent(message_hash)
                sent_count += 1
                
                # Small delay between messages to avoid rate limiting
                time.sleep(1)
        
        if sent_count > 0:
            print(f"✅ Sent {sent_count} new notification(s)")
        
        return sent_count
    
    def run(self):
        """Main loop - check queue periodically."""
        print("🤖 Telegram Notifier Agent Started")
        print(f"📁 Queue file: {self.queue_file}")
        print(f"⏱️  Check interval: {self.check_interval} seconds")
        print("=" * 50)
        
        try:
            while True:
                sent = self.process_queue()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping Telegram Notifier")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Notifier for AdGuard Monitor')
    parser.add_argument('--queue', default='telegram_queue.log', help='Queue file path')
    parser.add_argument('--interval', type=int, default=10, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Process queue once and exit')
    
    args = parser.parse_args()
    
    notifier = TelegramNotifier(
        queue_file=args.queue,
        check_interval=args.interval
    )
    
    if args.once:
        # Process queue once and exit
        sent = notifier.process_queue()
        print(f"Processed {sent} messages")
    else:
        # Run continuously
        notifier.run()

if __name__ == "__main__":
    main()