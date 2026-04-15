# OpenClaw Agent Integration Guide

This guide explains how to run the AdGuard Home DNS Monitor as an OpenClaw agent skill.

## 🎯 Overview

The AdGuard Home DNS Monitor can run as:
1. **Standalone application** - Independent Python scripts
2. **OpenClaw agent skill** - Integrated with OpenClaw for enhanced functionality

As an OpenClaw agent, the system gains:
- Seamless Telegram integration
- Persistent background execution
- Agent-to-agent communication
- Enhanced logging and monitoring
- Configuration management via OpenClaw

## 🔧 Prerequisites

### OpenClaw Requirements
1. OpenClaw installed and configured
2. Telegram plugin configured with at least one account
3. OpenClaw CLI accessible (`openclaw` command)
4. Permission to run background services

### System Requirements
1. Python 3.7+ with `requests` module
2. AdGuard Home running and accessible
3. (Optional) Cron or systemd for scheduling

## 🚀 Quick Setup as OpenClaw Agent

### 1. Clone and Configure
```bash
# Clone the repository
git clone https://github.com/hsoc2026/adguard-home-dns-monitor.git
cd adguard-home-dns-monitor

# Create configuration
cp adguard_config.example.json adguard_config.json
nano adguard_config.json  # Edit with your AdGuard Home details
```

### 2. Test OpenClaw Integration
```bash
# Test OpenClaw Telegram sending
openclaw message send --channel telegram --account YOUR_ACCOUNT --target YOUR_CHAT --message "AdGuard Monitor test"

# Test the monitor
python adguard_monitor_smart.py --test
```

### 3. Set Up as OpenClaw Skill
```bash
# Copy skill files to OpenClaw skills directory
cp -r . /path/to/openclaw/skills/adguard-monitor/

# Or run from current directory with OpenClaw integration
```

## 🤖 Agent Architecture

### Components
1. **Main Monitor** (`adguard_monitor_smart.py`)
   - Monitors AdGuard Home DNS logs
   - Detects gaming/entertainment sites
   - Queues alerts for notification

2. **Telegram Notifier** (`telegram_smart_notifier.py`)
   - Sends alerts via OpenClaw Telegram
   - Runs as background service
   - Prevents duplicate alerts

3. **Web Investigator** (`web_investigator.py`)
   - Investigates suspicious domains
   - Sends investigation results
   - Optional component

4. **Management Scripts**
   - `send_alerts_now.py` - Manual alert sender
   - `check_alerts.sh` - System status checker
   - Service files for background execution

### Communication Flow
```
AdGuard Home → Main Monitor → Alert Queue → Telegram Notifier → OpenClaw → Telegram
      ↓
Suspicious Domains → Web Investigator → Investigation Results → OpenClaw → Telegram
```

## ⚙️ Configuration as OpenClaw Agent

### OpenClaw-Specific Configuration
Add to your OpenClaw configuration or environment:

```yaml
# OpenClaw config.yaml
plugins:
  entries:
    adguard-monitor:
      enabled: true
      config:
        adguard_url: "http://YOUR_ADGUARD_HOME_IP:PORT"
        adguard_username: "YOUR_USERNAME"
        adguard_password: "YOUR_PASSWORD"
        watch_ips: ["192.168.1.100", "192.168.1.101"]
        telegram_account: "YOUR_TELEGRAM_ACCOUNT"
        telegram_target: "YOUR_CHAT_ID"
```

### Environment Variables
```bash
export ADGUARD_URL="http://YOUR_ADGUARD_HOME_IP:PORT"
export ADGUARD_USERNAME="YOUR_USERNAME"
export ADGUARD_PASSWORD="YOUR_PASSWORD"
export WATCH_IPS="192.168.1.100,192.168.1.101"
export TELEGRAM_ACCOUNT="YOUR_TELEGRAM_ACCOUNT"
export TELEGRAM_TARGET="YOUR_CHAT_ID"
```

## 🏃‍♂️ Running as OpenClaw Agent

### Method 1: Direct Execution
```bash
# Run main monitor
python adguard_monitor_smart.py

# Run Telegram notifier
python telegram_smart_notifier.py

# Run web investigator
python web_investigator.py
```

### Method 2: As Services
```bash
# macOS Launchd
launchctl load ~/Library/LaunchAgents/com.user.adguard-monitor-enhanced.plist
launchctl load ~/Library/LaunchAgents/com.user.telegram-notifier.plist

# Linux Systemd
sudo systemctl enable adguard-monitor-enhanced
sudo systemctl start adguard-monitor-enhanced
```

### Method 3: OpenClaw Skill Execution
```bash
# Via OpenClaw skill command
openclaw skill adguard-monitor start

# Or as part of OpenClaw agent startup
# Add to OpenClaw agent configuration
```

## 📡 Agent Commands

### Status Commands
```bash
# Check monitor status
python send_alerts_now.py --status

# Check queue
python send_alerts_now.py --queue

# Check services
./check_alerts.sh
```

### Control Commands
```bash
# Start monitoring
python adguard_monitor_smart.py --daemon

# Stop monitoring
pkill -f adguard_monitor_smart.py

# Send test alert
python send_alerts_now.py --test

# Clear queue
echo "" > telegram_smart_queue.log
```

### OpenClaw Integration Commands
```bash
# Send status via OpenClaw
openclaw message send --channel telegram --account YOUR_ACCOUNT --target YOUR_CHAT --message "$(./check_alerts.sh)"

# Schedule checks via OpenClaw cron
openclaw cron add --name "adguard-check" --schedule "* * * * *" --command "python /path/to/send_alerts_now.py"
```

## 🔄 Integration Patterns

### Pattern 1: Full OpenClaw Integration
- Run all components as OpenClaw-managed services
- Use OpenClaw configuration system
- Integrate with OpenClaw messaging
- Benefit from OpenClaw logging and monitoring

### Pattern 2: Hybrid Approach
- Run monitor as standalone service
- Use OpenClaw only for Telegram notifications
- Simple setup, focused integration

### Pattern 3: Minimal Integration
- Run everything standalone
- Use OpenClaw CLI only for sending messages
- Maximum flexibility, minimal dependency

## 📊 Monitoring and Logging

### OpenClaw Logs
```bash
# View OpenClaw logs
openclaw logs --follow

# Filter for AdGuard monitor logs
openclaw logs --grep "adguard"
```

### Agent Logs
```bash
# Monitor logs
tail -f logs/adguard-monitor-enhanced.log

# Telegram logs
tail -f logs/telegram-notifier.log

# Web investigator logs
tail -f logs/web-investigator.log
```

### Alert Logs
```bash
# View sent alerts
cat openclaw_sent_alerts.log

# View alert queue
cat telegram_smart_queue.log

# View violations
cat smart_violations.log
```

## 🛡️ Security Considerations

### Credential Management
- Store AdGuard credentials in `adguard_config.json` (not in Git)
- Use OpenClaw secure configuration for Telegram tokens
- Consider environment variables for sensitive data

### Access Control
- Limit AdGuard Home API access to monitoring only
- Use separate Telegram bot/account for notifications
- Implement rate limiting for alerts

### Network Security
- Use HTTPS for AdGuard Home if available
- Restrict monitor to local network when possible
- Implement firewall rules as needed

## 🔍 Troubleshooting

### OpenClaw Integration Issues
```bash
# Test OpenClaw Telegram
openclaw message send --channel telegram --account YOUR_ACCOUNT --target YOUR_CHAT --message "Test"

# Check OpenClaw configuration
openclaw config get --key "plugins.entries.telegram"

# Verify OpenClaw CLI access
which openclaw
openclaw --version
```

### Agent Communication Issues
```bash
# Test AdGuard connection
python test_adguard_connection.py

# Test alert queue
python send_alerts_now.py --test

# Check service status
./check_alerts.sh
```

### Performance Issues
```bash
# Monitor resource usage
top -p $(pgrep -f adguard_monitor)

# Check log sizes
du -sh logs/*.log

# Review queue size
wc -l telegram_smart_queue.log
```

## 📈 Scaling and Optimization

### For Large Deployments
1. Increase check interval for high traffic
2. Implement alert throttling
3. Use database instead of flat files
4. Add monitoring dashboard

### Performance Tips
1. Adjust `check_interval` based on needs
2. Limit `max_domains_per_run` for web investigator
3. Implement log rotation
4. Use connection pooling for AdGuard API

### High Availability
1. Run multiple monitor instances
2. Implement health checks
3. Add automatic restart on failure
4. Monitor with external service

## 🎯 Best Practices

### Configuration
- Use version control for configuration templates
- Document all configuration changes
- Test configuration changes in staging
- Backup configuration regularly

### Monitoring
- Set up alerting for monitor failures
- Monitor queue sizes and processing times
- Track detection accuracy and false positives
- Regular log review and cleanup

### Maintenance
- Regular updates to educational domains list
- Periodic review of detection patterns
- Performance optimization as needed
- Security updates and patches

## 🔗 Related Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [AdGuard Home API Reference](https://github.com/AdguardTeam/AdGuardHome/wiki/HTTP-API)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python Requests Library](https://docs.python-requests.org)

## 📞 Support

For OpenClaw agent integration issues:
1. Check OpenClaw logs: `openclaw logs --grep adguard`
2. Verify OpenClaw configuration
3. Test OpenClaw Telegram sending
4. Open issue on GitHub repository

---

**Happy Monitoring with OpenClaw!** 🦞