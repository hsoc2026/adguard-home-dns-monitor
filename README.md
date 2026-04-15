# AdGuard Home DNS Monitor

A smart DNS monitoring system for AdGuard Home that detects non-educational, gaming, and entertainment sites accessed by specific IP addresses.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
  - [Simple JSON Configuration](#option-1-simple-json-configuration)
  - [YAML Configuration](#option-2-yaml-configuration-recommended)
  - [OpenClaw Agent Integration](#option-3-openclaw-agent-integration)
- [Configuration](#-configuration)
- [Notification Setup](#-notification-setup)
- [Service Setup](#-service-setup)
- [OpenClaw Agent Integration](#-openclaw-agent-integration)
- [Detection Logic](#-detection-logic)
- [Testing](#-testing)
- [Management](#-management)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Contributing](#-contributing)
- [Support](#-support)

## 🚀 Features

- **Smart Filtering**: Ignores telemetry, search engines, CDNs, and system services
- **Game/Entertainment Detection**: Uses pattern matching to identify gaming and entertainment sites
- **Real-time Monitoring**: Checks DNS logs every 30 seconds
- **Multiple Notification Channels**: Telegram (via OpenClaw), console, or file output
- **Web Investigation**: Optional agent to browse suspicious sites for confirmation
- **Service Integration**: Runs as background services on macOS/Linux
- **OpenClaw Integration**: Seamless Telegram notifications via OpenClaw
- **YAML Configuration**: Easy configuration management
- **Duplicate Prevention**: Prevents sending the same alert multiple times
- **Alert Throttling**: Configurable rate limiting for notifications

## Use Cases

- Parental controls - Monitor children's devices for non-educational content
- Workplace monitoring - Ensure work devices are used appropriately
- Educational institutions - Track student device usage
- Personal productivity - Monitor your own device usage patterns

## 📦 Installation

### Prerequisites
- AdGuard Home running and accessible via HTTP/HTTPS
- Python 3.7+ with `requests` module
- (Optional) OpenClaw for Telegram notifications
- (Optional) PyYAML for YAML configuration support

### Quick Start

#### Option 1: Simple JSON Configuration

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hsoc2026/adguard-home-dns-monitor.git
   cd adguard-home-dns-monitor
   ```

2. **Install dependencies**:
   ```bash
   pip install requests
   ```

3. **Configure AdGuard Home**:
   ```bash
   cp adguard_config.example.json adguard_config.json
   nano adguard_config.json
   ```

   Update the configuration with your AdGuard Home details:
   ```json
   {
     "base_url": "http://YOUR_ADGUARD_HOME_IP:PORT",
     "username": "YOUR_USERNAME",
     "password": "YOUR_PASSWORD",
     "watch_ips": ["192.168.1.100", "192.168.1.101"],
     "educational_domains_file": "educational_domains.txt",
     "notification_channel": "telegram"
   }
   ```

4. **Run the monitor**:
   ```bash
   python adguard_monitor_smart.py
   ```

#### Option 2: YAML Configuration (Recommended)

1. **Clone and install**:
   ```bash
   git clone https://github.com/hsoc2026/adguard-home-dns-monitor.git
   cd adguard-home-dns-monitor
   pip install requests pyyaml
   ```

2. **Create configuration**:
   ```bash
   cp config_template.yaml config.yaml
   nano config.yaml  # Edit with your settings
   ```

3. **Apply configuration**:
   ```bash
   python configure_from_yaml.py
   ```

4. **Run the monitor**:
   ```bash
   python adguard_monitor_smart.py
   ```

#### Option 3: OpenClaw Agent Integration

See [OPENCLAW_AGENT_SETUP.md](OPENCLAW_AGENT_SETUP.md) for detailed instructions on running as an OpenClaw agent skill.

## Configuration

### Monitored IPs
Add the IP addresses you want to monitor to the `watch_ips` array in `adguard_config.json`.

### Educational Domains
Edit `educational_domains.txt` to add or remove domains that should be considered educational. The file includes 200+ default educational domains.

### Notification Channels
- `telegram`: Send alerts to Telegram (requires OpenClaw integration)
- `stdout`: Print alerts to console
- `file`: Save alerts to log file

## Service Setup

### macOS (Launchd)
```bash
# Copy service files
cp *.plist ~/Library/LaunchAgents/

# Load and start services
launchctl load ~/Library/LaunchAgents/com.user.adguard-monitor-enhanced.plist
launchctl load ~/Library/LaunchAgents/com.user.telegram-notifier.plist
launchctl load ~/Library/LaunchAgents/com.user.web-investigator.plist

# Start services
launchctl start com.user.adguard-monitor-enhanced
```

### Linux (Systemd)
```bash
# Copy service files
sudo cp *.service /etc/systemd/system/

# Enable and start services
sudo systemctl enable adguard-monitor-enhanced
sudo systemctl start adguard-monitor-enhanced
```

## Files

### Core Scripts
- `adguard_monitor_smart.py` - Main monitoring script
- `telegram_smart_notifier.py` - Telegram notification agent
- `web_investigator.py` - Web investigation agent
- `openclaw_alert_sender.py` - OpenClaw integration

### Configuration
- `adguard_config.example.json` - Example configuration
- `educational_domains.txt` - Educational domains list
- `*.plist` - macOS Launchd service files
- `*.service` - Linux Systemd service files

### Management Scripts
- `check_alerts.sh` - Check for detected violations
- `check_cron_status.sh` - Check cron job status
- `send_alerts_now.py` - Send alerts immediately
- `start_alert_bot.sh` - Start the alert bot

## How It Works

1. **DNS Query Monitoring**: Connects to AdGuard Home API to fetch DNS query logs
2. **Smart Filtering**: Ignores telemetry, search engines, CDNs, and system services
3. **Pattern Detection**: Uses regex patterns to identify games and entertainment sites
4. **Alert Queueing**: Queues alerts for notification delivery
5. **Notification**: Sends alerts via configured channels (Telegram, console, file)

### Detection Patterns

**Games**: `*game*`, `*gaming*`, `*casino*`, `*poker*`, `*bet*`, `*play*game*`
**Entertainment**: `*movie*`, `*film*`, `*stream*`, `*video*`, `*youtube*`, `*netflix*`, `*music*`, `*.tv`

### Ignored Patterns
- `*.microsoft.com`, `*.google.com`, `*.apple.com`
- `bing.com`, `google.com` (search engines)
- `*.cloudfront.net`, `*.amazonaws.com` (CDNs)
- `*.analytics.*`, `*.telemetry.*` (telemetry)
- `*.doubleclick.net` (ads)

## Testing

1. **From a monitored device**, visit:
   - `store.steampowered.com` (Steam - gaming)
   - `netflix.com` (Netflix - entertainment)
   - `youtube.com` (YouTube - entertainment)

2. **Wait 30 seconds** for detection

3. **Check for alerts**:
   ```bash
   ./check_alerts.sh
   ```

## Management

### Check Status
```bash
# Check if services are running
launchctl list | grep adguard

# View logs
tail -f logs/adguard-monitor-enhanced.log

# Check detected violations
cat smart_violations.log
```

### Restart Services
```bash
# macOS
launchctl stop com.user.adguard-monitor-enhanced
launchctl start com.user.adguard-monitor-enhanced

# Linux
sudo systemctl restart adguard-monitor-enhanced
```

## Security Notes

1. **Credentials**: Store AdGuard Home credentials securely in `adguard_config.json`
2. **Network**: Use HTTPS if AdGuard Home supports it
3. **Permissions**: Run with minimal necessary privileges
4. **Logs**: Review notification logs regularly

## Troubleshooting

### No Alerts Received
1. Verify AdGuard Home is running and accessible
2. Check if monitored IPs are making DNS queries
3. Review logs: `tail -f logs/adguard-monitor-enhanced.error.log`

### False Positives
1. Review `smart_violations.log`
2. Add domains to `educational_domains.txt`
3. Adjust detection patterns in `adguard_monitor_smart.py`

### Service Not Running
```bash
# Check service status
launchctl list | grep adguard

# View error logs
tail -f logs/adguard-monitor-enhanced.error.log

# Restart service
launchctl stop com.user.adguard-monitor-enhanced
launchctl start com.user.adguard-monitor-enhanced
```

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub
1. Monitor DNS queries in real-time
2. Send alerts to configured Telegram channels
3. Provide status updates via OpenClaw messaging
4. Run as a persistent background service

### OpenClaw Configuration
Ensure OpenClaw has:
1. Telegram plugin configured with appropriate account
2. Access to AdGuard Home API
3. Permission to run background services

### Agent Commands
```bash
# Check system status
openclaw message send --channel telegram --account YOUR_ACCOUNT --target YOUR_CHAT --message "Check AdGuard monitor status"

# Send test alert
openclaw message send --channel telegram --account YOUR_ACCOUNT --target YOUR_CHAT --message "Test alert from AdGuard monitor"
```

## 📊 Detection Logic

### Games Detection
- Patterns: `*game*`, `*gaming*`, `*casino*`, `*poker*`, `*bet*`, `*gamble*`
- Examples: `catalog.gamepass.com`, `store.steampowered.com`, `sdk.crazygames.com`

### Entertainment Detection
- Patterns: `*movie*`, `*film*`, `*stream*`, `*video*`, `*youtube*`, `*netflix*`
- TLDs: `.tv`, `.fm`
- Examples: `netflix.com`, `youtube.com`, `twitch.tv`

### Ignored Domains
- Telemetry: `*.microsoft.com`, `*.google.com`, `*.apple.com`
- Search engines: `bing.com`, `google.com`, `duckduckgo.com`
- CDNs: `*.cloudfront.net`, `*.amazonaws.com`
- Analytics: `*.analytics.*`, `*.telemetry.*`, `*.metrics.*`

## 🧪 Testing

### 1. Test AdGuard Connection
```bash
python test_adguard_connection.py
```

### 2. Test Monitoring
```bash
python test_monitor_once.py
```

### 3. Test Telegram Notifications
```bash
python send_alerts_now.py
```

### 4. Full System Test
1. From a monitored device, visit:
   - `store.steampowered.com` (gaming)
   - `netflix.com` (entertainment)
   - `youtube.com` (entertainment)
2. Wait 30 seconds
3. Check for alerts in Telegram/console/logs

## 🛠️ Management

### Check System Status
```bash
./check_alerts.sh
```

### Send Alerts Immediately
```bash
python send_alerts_now.py
```

### Check Cron Status
```bash
./check_cron_status.sh
```

### View Logs
```bash
# Main monitor logs
tail -f logs/adguard-monitor-enhanced.log

# Telegram notifier logs
tail -f logs/telegram-notifier.log

# Web investigator logs
tail -f logs/web-investigator.log
```

### Service Management (macOS)
```bash
# Check services
launchctl list | grep adguard

# Restart smart monitor
launchctl stop com.user.adguard-monitor-enhanced
launchctl start com.user.adguard-monitor-enhanced

# Restart all services
launchctl unload ~/Library/LaunchAgents/com.user.*.plist
launchctl load ~/Library/LaunchAgents/com.user.*.plist
```

## 📁 Project Structure

```
adguard-home-dns-monitor/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── config_template.yaml         # Configuration template
├── config.yaml                  # Main configuration (create from template)
├── adguard_config.example.json  # AdGuard config example
├── adguard_config.json          # AdGuard configuration (create from example)
├── educational_domains.txt      # Educational domains list
├── adguard_monitor_smart.py     # Main smart monitor
├── telegram_smart_notifier.py   # Telegram notification agent
├── web_investigator.py          # Web investigation agent
├── send_alerts_now.py           # Manual alert sender
├── openclaw_alert_sender.py     # OpenClaw integration
├── check_alerts.sh              # Check system status
├── check_cron_status.sh         # Check cron job status
├── run_alert_check.sh           # Cron job script
├── start_alert_bot.sh           # Start alert bot
├── *.plist                      # macOS Launchd service files
├── *.service                    # Linux Systemd service files
└── logs/                        # Log directory
```

## 🔧 Troubleshooting

### No Alerts Received
1. Verify AdGuard Home is running and accessible
2. Check if monitored IPs are making DNS queries
3. Review logs: `tail -f logs/adguard-monitor-enhanced.error.log`
4. Test detection: `python test_monitor_once.py`

### Telegram Notifications Not Working
1. Verify OpenClaw Telegram configuration
2. Check Telegram notifier logs: `tail -f logs/telegram-notifier.error.log`
3. Test Telegram sending: `python send_alerts_now.py`
4. Ensure bot has permission to send to target chat

### Service Not Running
```bash
# Check service status
launchctl list | grep adguard

# View error logs
tail -f logs/adguard-monitor-enhanced.error.log

# Restart service
launchctl stop com.user.adguard-monitor-enhanced
launchctl start com.user.adguard-monitor-enhanced
```

### False Positives
1. Review `smart_violations.log` for detected sites
2. Add domains to `educational_domains.txt`
3. Adjust detection patterns in `adguard_monitor_smart.py`

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub

---

**Happy Monitoring!** 🎯