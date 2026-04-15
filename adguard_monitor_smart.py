#!/usr/bin/env python3
"""
Smart AdGuard Home DNS Monitor
- Ignores telemetry/search/system sites
- Detects games/entertainment sites
- Queues suspicious sites for investigation
"""

import requests
import json
import time
import logging
import re
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartAdGuardMonitor:
    def __init__(self, config_file="adguard_config.json"):
        # Resolve config file path relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, config_file)
        
        # Load config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.base_url = config['base_url'].rstrip('/')
        self.username = config['username']
        self.password = config['password']
        self.watch_ips = set(config['watch_ips'])
        self.check_interval = 30
        
        # Session for API requests
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Track processed domains
        self.processed_domains = set()
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        """Test connection to AdGuard Home."""
        try:
            response = self.session.get(f"{self.base_url}/control/status", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Connected to AdGuard Home at {self.base_url}")
                return True
            else:
                logger.error(f"❌ Connection failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def get_query_log(self, limit=50):
        """Get recent query logs."""
        try:
            params = {'limit': limit, 'offset': 0, 'search': '', 'response_status': 'all'}
            response = self.session.get(f"{self.base_url}/control/querylog", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get query log: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting query log: {e}")
            return []
    
    def should_ignore(self, domain):
        """Check if domain should be ignored (telemetry, search, etc.)."""
        domain_lower = domain.lower()
        
        # Ignore patterns
        ignore_patterns = [
            # Microsoft
            r'.*\.microsoft\.com$',
            r'.*\.windows\.com$',
            r'.*\.office\.',
            r'^v\d+\.events\.data\.microsoft\.com$',
            r'^.*\.prod\.do\.dsp\.mp\.microsoft\.com$',
            
            # Google
            r'.*\.google\.com$',
            r'.*\.googleapis\.com$',
            r'.*\.gstatic\.com$',
            r'^.*\.clients\d*\.google\.com$',
            
            # Search engines
            r'^www\.bing\.com$',
            r'^bing\.com$',
            r'^www\.google\.com$',
            r'^google\.com$',
            r'^duckduckgo\.com$',
            
            # CDNs/cloud
            r'.*\.cloudfront\.net$',
            r'.*\.akamaiedge\.net$',
            r'.*\.amazonaws\.com$',
            
            # Apple
            r'.*\.apple\.com$',
            r'.*\.icloud\.com$',
            
            # Analytics/telemetry
            r'.*\.analytics\.',
            r'.*\.telemetry\.',
            r'.*\.metrics\.',
            
            # Ads
            r'.*\.doubleclick\.net$',
            r'.*\.googlesyndication\.com$',
        ]
        
        for pattern in ignore_patterns:
            if re.match(pattern, domain_lower):
                return True
        
        return False
    
    def is_games_entertainment(self, domain):
        """Check if domain appears to be games/entertainment."""
        domain_lower = domain.lower()
        
        # Game patterns
        game_patterns = [
            r'.*game.*',
            r'.*gaming.*',
            r'.*casino.*',
            r'.*poker.*',
            r'.*slot.*',
            r'.*bet.*',
            r'.*gamble.*',
            r'.*play.*game.*',
            r'.*free.*game.*',
        ]
        
        # Entertainment patterns
        entertainment_patterns = [
            r'.*movie.*',
            r'.*film.*',
            r'.*stream.*',
            r'.*video.*',
            r'.*youtube.*',
            r'.*netflix.*',
            r'.*hulu.*',
            r'.*disney.*',
            r'.*primevideo.*',
            r'.*spotify.*',
            r'.*music.*',
            r'.*tv.*',
        ]
        
        # Check games
        for pattern in game_patterns:
            if re.match(pattern, domain_lower):
                return 'games', 'high'
        
        # Check entertainment
        for pattern in entertainment_patterns:
            if re.match(pattern, domain_lower):
                return 'entertainment', 'high'
        
        # Check entertainment TLDs
        if domain_lower.endswith('.tv') or domain_lower.endswith('.fm'):
            return 'entertainment', 'medium'
        
        return None, None
    
    def process_queries(self, queries):
        """Process DNS queries with smart filtering."""
        for query in queries:
            client_ip = query.get('client', '')
            domain = query.get('question', {}).get('name', '')
            timestamp = query.get('time', '')
            
            if not domain or client_ip not in self.watch_ips:
                continue
            
            # Skip if already blocked by filter
            if query.get('filterId') is not None:
                logger.debug(f"Already blocked: {domain} (filterId: {query.get('filterId')})")
                continue
            
            # Skip if already processed
            domain_key = f"{client_ip}:{domain}"
            if domain_key in self.processed_domains:
                continue
            
            self.processed_domains.add(domain_key)
            
            # Check if should be ignored
            if self.should_ignore(domain):
                logger.debug(f"Ignored: {domain}")
                continue
            
            # Check if games/entertainment
            # print(f"Raw API data: {query}")  # Debugging line to see raw API response
            category, confidence = self.is_games_entertainment(domain)
            
            if category:
                # This is a violation - log it
                self.log_violation(client_ip, domain, timestamp, category, confidence)
            else:
                # Suspicious but not clearly games/entertainment - queue for investigation
                self.queue_for_investigation(client_ip, domain, timestamp)
    
    def log_violation(self, client_ip, domain, timestamp, category, confidence):
        """Log games/entertainment violation."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp[:19]
        
        message = (
            f"🚨 {category.upper()} site detected!\n"
            f"• IP: {client_ip}\n"
            f"• Domain: {domain}\n"
            f"• Time: {time_str}\n"
            f"• Confidence: {confidence}"
        )
        
        # Log to file
        with open("smart_violations.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n---\n")
        
        # Queue for Telegram
        with open("telegram_smart_queue.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n---\n")
        
        logger.warning(f"{category}: {client_ip} -> {domain}")
    
    def queue_for_investigation(self, client_ip, domain, timestamp):
        """Queue suspicious domain for investigation."""
        with open("suspicious_domains.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - {client_ip} - {domain}\n")
        
        logger.info(f"Suspicious (needs investigation): {client_ip} -> {domain}")
    
    def run(self):
        """Main monitoring loop."""
        logger.info(f"🎯 Smart AdGuard Monitor started")
        logger.info(f"📡 Monitoring IPs: {', '.join(self.watch_ips)}")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        logger.info("✅ Ignoring telemetry/search/system sites")
        logger.info("✅ Detecting games/entertainment automatically")
        logger.info("✅ Queuing suspicious sites for investigation")
        
        try:
            while True:
                queries = self.get_query_log(limit=500)
                if queries:
                    self.process_queries(queries)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

def main():
    monitor = SmartAdGuardMonitor()
    monitor.run()

if __name__ == "__main__":
    main()