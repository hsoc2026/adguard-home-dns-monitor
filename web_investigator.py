#!/usr/bin/env python3
"""
Web Investigator Agent for AdGuard Monitor
Browses to suspicious sites and analyzes if they're games/entertainment.
"""

import json
import time
import logging
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import sys
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebInvestigator:
    def __init__(self, investigation_file: str = "needs_investigation.log"):
        self.investigation_file = investigation_file
        self.processed_domains = set()
        self._load_processed_domains()
    
    def _load_processed_domains(self):
        """Load already processed domains."""
        if os.path.exists("investigated_domains.log"):
            with open("investigated_domains.log", 'r') as f:
                for line in f:
                    if line.strip():
                        self.processed_domains.add(line.strip())
    
    def _mark_as_processed(self, domain: str):
        """Mark domain as processed."""
        self.processed_domains.add(domain)
        with open("investigated_domains.log", 'a') as f:
            f.write(f"{domain}\n")
    
    def read_investigation_queue(self) -> List[Dict]:
        """Read domains that need investigation."""
        # Try multiple possible investigation files
        investigation_files = [
            self.investigation_file,
            "suspicious_domains.log",
            "needs_investigation.log"
        ]
        
        for file_path in investigation_files:
            if os.path.exists(file_path):
                return self._read_investigation_file(file_path)
        
        return []
    
    def _read_investigation_file(self, file_path: str) -> List[Dict]:
        """Read domains from a specific investigation file."""
        domains_to_investigate = []
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Parse line based on format
                    # Format 1: timestamp - IP - domain (from suspicious_domains.log)
                    # Format 2: timestamp - domain - reason (from needs_investigation.log)
                    
                    # Try format 1 first (timestamp - IP - domain)
                    if ' - ' in line:
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            ip = parts[1]
                            domain = parts[2]
                            reason = f"Suspicious domain from {ip}"
                        elif len(parts) >= 2:
                            timestamp = parts[0]
                            domain = parts[1]
                            reason = "Unknown"
                        else:
                            continue
                    else:
                        # Just a domain name
                        timestamp = datetime.now().isoformat()
                        domain = line
                        reason = "Unknown"
                    
                    # Skip if already processed
                    if domain in self.processed_domains:
                        continue
                    
                    domains_to_investigate.append({
                        'domain': domain,
                        'timestamp': timestamp,
                        'reason': reason
                    })
        
        return domains_to_investigate
    
    def investigate_with_browser(self, domain: str) -> Dict:
        """
        Investigate a domain by browsing to it.
        This is a simplified version - in production, you'd use:
        - Selenium/Playwright for browser automation
        - OpenClaw's web browsing capabilities
        - Or an external service
        """
        
        # For now, we'll simulate investigation with pattern matching
        # and attempt to fetch the page title
        
        logger.info(f"Investigating domain: {domain}")
        
        try:
            # Try to get page title using curl (simplified)
            url = f"http://{domain}"
            cmd = ['curl', '-s', '-L', '--max-time', '10', url]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                html = result.stdout.lower()
                
                # Look for title tag
                title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No title found"
                
                # Analyze content for games/entertainment indicators
                analysis = self._analyze_content(html, title)
                
                return {
                    'domain': domain,
                    'title': title,
                    'analysis': analysis,
                    'method': 'curl_fetch',
                    'success': True
                }
            else:
                # Try HTTPS
                url = f"https://{domain}"
                cmd = ['curl', '-s', '-L', '--max-time', '10', url]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    html = result.stdout.lower()
                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    title = title_match.group(1) if title_match else "No title found"
                    
                    analysis = self._analyze_content(html, title)
                    
                    return {
                        'domain': domain,
                        'title': title,
                        'analysis': analysis,
                        'method': 'curl_fetch_https',
                        'success': True
                    }
                else:
                    return {
                        'domain': domain,
                        'title': 'Could not fetch',
                        'analysis': {'category': 'unknown', 'confidence': 'low', 'reason': 'Could not fetch page'},
                        'method': 'failed',
                        'success': False
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'domain': domain,
                'title': 'Timeout',
                'analysis': {'category': 'unknown', 'confidence': 'low', 'reason': 'Request timeout'},
                'method': 'timeout',
                'success': False
            }
        except Exception as e:
            return {
                'domain': domain,
                'title': f'Error: {str(e)[:50]}',
                'analysis': {'category': 'unknown', 'confidence': 'low', 'reason': f'Error: {e}'},
                'method': 'error',
                'success': False
            }
    
    def _analyze_content(self, html: str, title: str) -> Dict:
        """Analyze HTML content for games/entertainment indicators."""
        
        # Combine title and HTML for analysis
        content = f"{title} {html[:5000]}"  # First 5000 chars of HTML
        
        # Game indicators
        game_keywords = [
            'game', 'games', 'gaming', 'play', 'player', 'score', 'level',
            'casino', 'poker', 'slot', 'bet', 'gamble', 'roulette',
            'arcade', 'puzzle', 'adventure', 'role-playing', 'rpg',
            'strategy', 'action', 'shooter', 'sports', 'racing'
        ]
        
        # Entertainment indicators
        entertainment_keywords = [
            'movie', 'movies', 'film', 'films', 'tv', 'television',
            'stream', 'streaming', 'video', 'videos', 'watch',
            'youtube', 'netflix', 'hulu', 'disney', 'prime video',
            'hbo', 'spotify', 'music', 'podcast', 'audio',
            'entertainment', 'show', 'series', 'episode'
        ]
        
        # Count matches
        game_matches = sum(1 for keyword in game_keywords if keyword in content)
        entertainment_matches = sum(1 for keyword in entertainment_keywords if keyword in content)
        
        # Determine category
        if game_matches > 3:
            return {
                'category': 'games',
                'confidence': 'high',
                'reason': f'Found {game_matches} game-related keywords',
                'game_matches': game_matches,
                'entertainment_matches': entertainment_matches
            }
        elif entertainment_matches > 3:
            return {
                'category': 'entertainment',
                'confidence': 'high',
                'reason': f'Found {entertainment_matches} entertainment-related keywords',
                'game_matches': game_matches,
                'entertainment_matches': entertainment_matches
            }
        elif game_matches > 0:
            return {
                'category': 'possible_games',
                'confidence': 'medium',
                'reason': f'Found {game_matches} game-related keywords',
                'game_matches': game_matches,
                'entertainment_matches': entertainment_matches
            }
        elif entertainment_matches > 0:
            return {
                'category': 'possible_entertainment',
                'confidence': 'medium',
                'reason': f'Found {entertainment_matches} entertainment-related keywords',
                'game_matches': game_matches,
                'entertainment_matches': entertainment_matches
            }
        else:
            return {
                'category': 'unknown',
                'confidence': 'low',
                'reason': 'No clear game/entertainment keywords found',
                'game_matches': game_matches,
                'entertainment_matches': entertainment_matches
            }
    
    def generate_notification(self, domain_info: Dict, investigation_result: Dict) -> str:
        """Generate notification message."""
        domain = domain_info['domain']
        reason = domain_info.get('reason', 'Unknown')
        title = investigation_result.get('title', 'Unknown')
        analysis = investigation_result.get('analysis', {})
        
        category = analysis.get('category', 'unknown')
        confidence = analysis.get('confidence', 'low')
        analysis_reason = analysis.get('reason', 'No analysis available')
        
        message = (
            f"🔍 Web Investigation Result\n"
            f"• Domain: {domain}\n"
            f"• Title: {title[:100]}\n"
            f"• Category: {category}\n"
            f"• Confidence: {confidence}\n"
            f"• Analysis: {analysis_reason}\n"
            f"• Original reason: {reason}"
        )
        
        return message
    
    def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram via OpenClaw."""
        try:
            cmd = [
                '/opt/homebrew/bin/openclaw', 'message', 'send',
                '--channel', 'telegram',
                '--account', 'internetsecurity',
                '--target', '8771371027',
                '--message', message
            ]
            
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
                logger.error(f"❌ Failed to send: {result.stderr[:100]}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Send timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def _get_message_hash(self, message: str) -> str:
        """Create hash for message."""
        return hashlib.md5(message.encode()).hexdigest()[:16]
    
    def _load_sent_investigation_hashes(self) -> set:
        """Load already sent investigation message hashes."""
        sent_hashes = set()
        if os.path.exists("investigation_sent.log"):
            with open("investigation_sent.log", 'r') as f:
                for line in f:
                    if line.strip():
                        sent_hashes.add(line.strip())
        return sent_hashes
    
    def _mark_investigation_as_sent(self, message_hash: str):
        """Mark investigation message as sent."""
        with open("investigation_sent.log", "a") as f:
            f.write(f"{message_hash}\n")
    
    def process_queue(self):
        """Process investigation queue."""
        domains = self.read_investigation_queue()
        
        if not domains:
            logger.info("No domains need investigation")
            return 0
        
        logger.info(f"Found {len(domains)} domains to investigate")
        
        # Load sent hashes
        sent_hashes = self._load_sent_investigation_hashes()
        
        processed_count = 0
        sent_notifications = 0
        for domain_info in domains[:5]:  # Limit to 5 per run
            domain = domain_info['domain']
            
            logger.info(f"Investigating: {domain}")
            
            # Investigate domain
            result = self.investigate_with_browser(domain)
            
            # Generate notification if it's games/entertainment
            analysis = result.get('analysis', {})
            category = analysis.get('category', 'unknown')
            confidence = analysis.get('confidence', 'low')
            
            # Only notify for high/medium confidence games/entertainment
            if confidence in ['high', 'medium'] and category in ['games', 'entertainment', 'possible_games', 'possible_entertainment']:
                notification = self.generate_notification(domain_info, result)
                
                # Check if already sent
                message_hash = self._get_message_hash(notification)
                if message_hash in sent_hashes:
                    logger.info(f"Already sent notification for {domain}")
                else:
                    # Send to Telegram
                    if self.send_telegram_message(notification):
                        self._mark_investigation_as_sent(message_hash)
                        sent_notifications += 1
                        logger.info(f"✅ Sent notification for {domain} ({category}, {confidence})")
                    else:
                        # Fallback: log to file
                        with open("telegram_investigation_results.log", "a") as f:
                            f.write(f"{datetime.now().isoformat()}\n{notification}\n---\n")
                        logger.info(f"Queued notification for {domain} ({category}, {confidence})")
            
            # Mark as processed
            self._mark_as_processed(domain)
            processed_count += 1
            
            # Log full result
            with open("investigation_results.log", "a") as f:
                f.write(f"{datetime.now().isoformat()}\n")
                f.write(f"Domain: {domain}\n")
                f.write(f"Result: {json.dumps(result, indent=2)}\n")
                f.write("\n")
            
            # Small delay between investigations
            time.sleep(2)
        
        if sent_notifications > 0:
            logger.info(f"✅ Sent {sent_notifications} investigation notification(s)")
        
        return processed_count
    
    def run(self, interval: int = 300):
        """Run investigator periodically."""
        logger.info(f"Starting Web Investigator")
        logger.info(f"Check interval: {interval} seconds")
        
        try:
            while True:
                processed = self.process_queue()
                if processed > 0:
                    logger.info(f"Processed {processed} domains")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Investigator stopped")
        except Exception as e:
            logger.error(f"Investigator error: {e}")
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Investigator for AdGuard Monitor')
    parser.add_argument('--file', default='needs_investigation.log', help='Investigation queue file')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Process once and exit')
    
    args = parser.parse_args()
    
    investigator = WebInvestigator(investigation_file=args.file)
    
    if args.once:
        processed = investigator.process_queue()
        print(f"Processed {processed} domains")
    else:
        investigator.run(interval=args.interval)

if __name__ == "__main__":
    main()