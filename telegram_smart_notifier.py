#!/usr/bin/env python3
"""
Telegram Smart Notifier for AdGuard Monitor
Sends Telegram alerts when games/entertainment sites are detected.
"""

import json
import time
import logging
import os
import subprocess
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramSmartNotifier:
    def __init__(self, queue_file="telegram_smart_queue.log", sent_file="openclaw_sent_alerts.log", check_interval=10):
        self.queue_file = queue_file
        self.sent_file = sent_file
        self.check_interval = check_interval
        
        # Track sent messages
        self.sent_hashes = set()
        self._load_sent_messages()
    
    def _load_sent_messages(self):
        """Load already sent messages."""
        if os.path.exists(self.sent_file):
            with open(self.sent_file, 'r') as f:
                for line in f:
                    if line.strip():
                        self.sent_hashes.add(line.strip())
    
    def _mark_as_sent(self, message_hash: str):
        """Mark message as sent."""
        self.sent_hashes.add(message_hash)
        with open(self.sent_file, 'a') as f:
            f.write(f"{message_hash}\n")
    
    def _get_message_hash(self, message: str) -> str:
        """Create hash for message to detect duplicates."""
        return hashlib.md5(message.encode()).hexdigest()[:16]
    
    def read_queue(self):
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
                    if message:
                        messages.append(message)
        
        return messages
    
    def send_telegram_message(self, message: str) -> bool:
        """
        Send message to Telegram via OpenClaw.
        Send to Aaron's Telegram chat (ID: 8771371027).
        """
        try:
            # Use OpenClaw CLI to send to Aaron's Telegram chat
            cmd = [
                '/opt/homebrew/bin/openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--account', 'internetsecurity',
                '--target', '8771371027',
                '--message', message
            ]
            
            logger.info(f"Sending Telegram alert: {message[:50]}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Telegram message sent")
                return True
            else:
                logger.error(f"❌ Failed to send: {result.stderr}")
                # Fallback: log to file
                self._log_fallback(message)
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Send timeout")
            self._log_fallback(message)
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            self._log_fallback(message)
            return False
    
    def _log_fallback(self, message: str):
        """Log message to file if Telegram send fails."""
        with open("telegram_fallback.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n\n")
    
    def process_queue(self):
        """Process queued messages."""
        messages = self.read_queue()
        
        if not messages:
            logger.debug(f"No messages in queue ({datetime.now().strftime('%H:%M:%S')})")
            return 0
        
        sent_count = 0
        for message in messages:
            message_hash = self._get_message_hash(message)
            
            # Skip if already sent
            if message_hash in self.sent_hashes:
                continue
            
            # Send to Telegram
            if self.send_telegram_message(message):
                self._mark_as_sent(message_hash)
                sent_count += 1
                
                # Small delay to avoid rate limiting
                time.sleep(1)
        
        if sent_count > 0:
            logger.info(f"✅ Sent {sent_count} new alert(s)")
        
        return sent_count
    
    def run(self):
        """Main loop - check queue periodically."""
        logger.info("🤖 Telegram Smart Notifier Started")
        logger.info(f"📁 Queue file: {self.queue_file}")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        logger.info("=" * 50)
        
        try:
            while True:
                sent = self.process_queue()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Stopping Telegram Notifier")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram Smart Notifier for AdGuard Monitor')
    parser.add_argument('--queue', default='telegram_smart_queue.log', help='Queue file path')
    parser.add_argument('--interval', type=int, default=10, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Process once and exit')
    
    args = parser.parse_args()
    
    notifier = TelegramSmartNotifier(
        queue_file=args.queue,
        check_interval=args.interval
    )
    
    if args.once:
        # Process once and exit
        sent = notifier.process_queue()
        print(f"Processed {sent} messages")
    else:
        # Run continuously
        notifier.run()

if __name__ == "__main__":
    main()