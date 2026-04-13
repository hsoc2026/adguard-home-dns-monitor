#!/usr/bin/env python3
"""
AdGuard Home DNS Monitor Agent
Monitors DNS logs for non-educational sites accessed by specific IP addresses
and sends notifications when detected.

Based on AdGuard Home API: https://github.com/AdguardTeam/AdGuardHome/wiki/API
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Set, Optional
import argparse
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdGuardMonitor:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        watch_ips: List[str],
        educational_domains_file: str = None,
        check_interval: int = 10,
        notification_channel: str = "telegram"
    ):
        """
        Initialize AdGuard Home monitor.
        
        Args:
            base_url: AdGuard Home base URL (e.g., http://192.168.1.1:3000)
            username: AdGuard Home admin username
            password: AdGuard Home admin password
            watch_ips: List of IP addresses to monitor
            educational_domains_file: Path to file with educational domains (one per line)
            check_interval: How often to check logs (seconds)
            notification_channel: Where to send notifications (telegram, stdout, file)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.watch_ips = set(watch_ips)
        self.check_interval = check_interval
        self.notification_channel = notification_channel
        
        # Load educational domains
        self.educational_domains = set()
        if educational_domains_file and os.path.exists(educational_domains_file):
            with open(educational_domains_file, 'r') as f:
                for line in f:
                    domain = line.strip().lower()
                    if domain and not domain.startswith('#'):
                        self.educational_domains.add(domain)
            logger.info(f"Loaded {len(self.educational_domains)} educational domains")
        else:
            # Default educational domains (can be expanded)
            default_educational = {
                'khanacademy.org', 'khanacademy.com',
                'edx.org', 'coursera.org', 'udemy.com',
                'codecademy.com', 'freecodecamp.org',
                'mit.edu', 'harvard.edu', 'stanford.edu',
                'yale.edu', 'princeton.edu',
                'wikipedia.org', 'wikimedia.org',
                'arxiv.org', 'researchgate.net',
                'scholar.google.com', 'academia.edu',
                'jstor.org', 'projectgutenberg.org',
                'libgen.rs', 'libgen.is',
                'duolingo.com', 'memrise.com',
                'brilliant.org', 'skillshare.com',
                'ted.com', 'crashcourse.com',
                'nationalgeographic.com', 'smithsonianmag.com',
                'nasa.gov', 'noaa.gov',
                'github.com', 'gitlab.com',  # For coding education
                'stackoverflow.com', 'stackexchange.com',
                'python.org', 'rust-lang.org', 'golang.org',
                'developer.mozilla.org', 'w3schools.com',
                'leetcode.com', 'hackerrank.com',
                'mathway.com', 'wolframalpha.com',
                'desmos.com', 'geogebra.org',
                'chemguide.co.uk', 'physicsclassroom.com',
                'biologycorner.com', 'khanacademy.org'
            }
            self.educational_domains = default_educational
            logger.info(f"Using {len(self.educational_domains)} default educational domains")
        
        # Track already notified domains to avoid duplicate notifications
        self.notified_domains = set()
        
        # Session for API requests
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Test connection
        if not self.test_connection():
            raise ConnectionError(f"Failed to connect to AdGuard Home at {base_url}")
    
    def test_connection(self) -> bool:
        """Test connection to AdGuard Home API."""
        try:
            response = self.session.get(f"{self.base_url}/control/status", timeout=5)
            if response.status_code == 200:
                logger.info(f"Connected to AdGuard Home at {self.base_url}")
                return True
            else:
                logger.error(f"Connection failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def get_query_log(self, limit: int = 100) -> List[Dict]:
        """Get recent query logs from AdGuard Home."""
        try:
            params = {
                'limit': limit,
                'offset': 0,
                'search': '',
                'response_status': 'all'
            }
            response = self.session.get(
                f"{self.base_url}/control/querylog",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get query log: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting query log: {e}")
            return []
    
    def is_educational_domain(self, domain: str) -> bool:
        """Check if a domain is educational."""
        domain_lower = domain.lower()
        
        # Check exact match
        if domain_lower in self.educational_domains:
            return True
        
        # Check subdomains (e.g., docs.google.com contains google.com)
        for edu_domain in self.educational_domains:
            if domain_lower.endswith(f".{edu_domain}"):
                return True
        
        # Check for common educational TLDs
        educational_tlds = {'.edu', '.ac.', '.sch.'}
        for tld in educational_tlds:
            if tld in domain_lower:
                return True
        
        return False
    
    def analyze_queries(self, queries: List[Dict]) -> List[Dict]:
        """Analyze queries for non-educational sites from watched IPs."""
        violations = []
        
        for query in queries:
            client_ip = query.get('client', '')
            # Get domain from question.name field (AdGuard Home API structure)
            question = query.get('question', {})
            domain = question.get('name', '')
            timestamp = query.get('time', '')
            status = query.get('status', '')
            
            # Check if from watched IP
            if client_ip in self.watch_ips:
                # Check if domain is non-educational
                if domain and not self.is_educational_domain(domain):
                    # Avoid duplicate notifications for same domain
                    domain_key = f"{client_ip}:{domain}"
                    if domain_key not in self.notified_domains:
                        violation = {
                            'client_ip': client_ip,
                            'domain': domain,
                            'timestamp': timestamp,
                            'status': status,
                            'query': query
                        }
                        violations.append(violation)
                        self.notified_domains.add(domain_key)
        
        return violations
    
    def send_notification(self, violation: Dict):
        """Send notification about violation."""
        client_ip = violation['client_ip']
        domain = violation['domain']
        timestamp = violation['timestamp']
        
        # Format timestamp for readability
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = timestamp[:19]
        
        message = (
            f"🚨 Non-educational site detected!\n"
            f"• IP: {client_ip}\n"
            f"• Domain: {domain}\n"
            f"• Time: {time_str}\n"
            f"• Status: {violation['status']}"
        )
        
        # Always log to violations file
        self._log_violation(message, violation)
        
        if self.notification_channel == "telegram":
            # For Telegram, we log to a special file that another agent can read
            logger.info(f"Telegram notification queued: {message}")
            self._log_telegram_queue(message)
        elif self.notification_channel == "stdout":
            print(f"\n[ALERT] {message}\n")
        elif self.notification_channel == "file":
            # Already logged above
            pass
        
        logger.warning(f"Non-educational site: {client_ip} -> {domain}")
    
    def _log_violation(self, message: str, violation: Dict):
        """Log violation to violations file."""
        from datetime import datetime
        with open("adguard_violations.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n\n")
    
    def _log_telegram_queue(self, message: str):
        """Log to Telegram queue file for separate notifier agent."""
        from datetime import datetime
        with open("telegram_queue.log", "a") as f:
            f.write(f"{datetime.now().isoformat()}\n{message}\n---\n")
    
    def run(self):
        """Main monitoring loop."""
        logger.info(f"Starting AdGuard Home monitor for IPs: {', '.join(self.watch_ips)}")
        logger.info(f"Checking every {self.check_interval} seconds")
        
        try:
            while True:
                # Get recent queries
                queries = self.get_query_log(limit=50)
                
                if queries:
                    # Analyze for violations
                    violations = self.analyze_queries(queries)
                    
                    # Send notifications for new violations
                    for violation in violations:
                        self.send_notification(violation)
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise

def load_config(config_file: str) -> Dict:
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='AdGuard Home DNS Monitor')
    parser.add_argument('--config', '-c', default='adguard_config.json',
                       help='Configuration file (JSON)')
    parser.add_argument('--educational-domains', '-e',
                       help='File with educational domains (one per line)')
    parser.add_argument('--interval', '-i', type=int, default=10,
                       help='Check interval in seconds')
    parser.add_argument('--notify', '-n', default='stdout',
                       choices=['telegram', 'stdout', 'file'],
                       help='Notification channel')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Required configuration
    required = ['base_url', 'username', 'password', 'watch_ips']
    missing = [key for key in required if key not in config]
    
    if missing:
        logger.error(f"Missing required config keys: {', '.join(missing)}")
        logger.info("Please create a config file with the following structure:")
        logger.info(json.dumps({
            "base_url": "http://192.168.1.1:3000",
            "username": "admin",
            "password": "your_password",
            "watch_ips": ["192.168.1.100", "192.168.1.101"],
            "educational_domains_file": "educational_domains.txt"
        }, indent=2))
        sys.exit(1)
    
    # Create monitor
    try:
        monitor = AdGuardMonitor(
            base_url=config['base_url'],
            username=config['username'],
            password=config['password'],
            watch_ips=config['watch_ips'],
            educational_domains_file=args.educational_domains or config.get('educational_domains_file'),
            check_interval=args.interval,
            notification_channel=args.notify
        )
        
        # Start monitoring
        monitor.run()
        
    except Exception as e:
        logger.error(f"Failed to start monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()