# AdGuard Home DNS Monitor Agent

A Python-based agent that monitors AdGuard Home DNS logs for non-educational sites accessed by specific IP addresses and sends notifications.

## Quick Start

### 1. Install dependencies
```bash
pip install requests
```

### 2. Configure AdGuard Home connection
Edit `adguard_config.json`:
```json
{
  "base_url": "http://YOUR_ADGUARD_IP:PORT",
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD",
  "watch_ips": ["192.168.1.100", "192.168.1.101"],
  "educational_domains_file": "educational_domains.txt",
  "notification_channel": "telegram"
}
```

### 3. Test connection
```bash
python test_adguard_connection.py
```

### 4. Run the monitor
```bash
python adguard_monitor.py --config adguard_config.json
```

## Files

- `adguard_monitor.py` - Main monitoring agent
- `adguard_config.json` - Configuration file
- `educational_domains.txt` - List of educational domains
- `test_adguard_connection.py` - Connection test script
- `SKILL_adguard_monitor.md` - OpenClaw skill documentation

## Features

- **Real-time monitoring** of DNS queries
- **IP-based filtering** for specific devices
- **Educational domain detection** with customizable lists
- **Multiple notification channels** (Telegram, stdout, file)
- **Duplicate prevention** to avoid spam
- **Configurable check intervals**

## Use Cases

1. **Parental controls** - Monitor children's devices for non-educational content
2. **Workplace monitoring** - Ensure work devices are used appropriately
3. **Educational institutions** - Track student device usage
4. **Personal productivity** - Monitor your own device usage patterns

## Configuration Options

### Watch IPs
Add IP addresses to monitor in the `watch_ips` array in `adguard_config.json`.

### Educational Domains
Edit `educational_domains.txt` to add or remove domains. The file supports:
- One domain per line
- Comments starting with `#`
- Subdomain matching (e.g., `google.com` matches `docs.google.com`)

### Notification Channels
- `telegram` - Send to Telegram via OpenClaw
- `stdout` - Print to console
- `file` - Append to `adguard_violations.log`

## Running as a Service

### macOS (Launchd)
```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.user.adguard-monitor.plist

# Check status
launchctl list | grep adguard-monitor
```

### Linux (Systemd)
```bash
# Enable and start
sudo systemctl enable adguard-monitor
sudo systemctl start adguard-monitor

# Check status
sudo systemctl status adguard-monitor
```

## Integration with OpenClaw

### As a cron job
Add to OpenClaw's cron configuration to run periodically.

### As a subagent
```bash
openclaw agents spawn --label "AdGuard Monitor" --command "python adguard_monitor.py --config adguard_config.json"
```

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Verify AdGuard Home is running
   - Check IP address and port
   - Test with: `curl http://YOUR_IP:PORT/control/status`

2. **Authentication failed**
   - Verify username/password
   - Check if authentication is enabled in AdGuard Home

3. **No notifications**
   - Check if watched IPs are making DNS queries
   - Verify educational domains list
   - Check notification channel configuration

### Debug Mode
Run with verbose logging:
```bash
python adguard_monitor.py --config adguard_config.json 2>&1 | tee monitor.log
```

## Security Considerations

1. Store credentials securely
2. Use HTTPS if available
3. Run with minimal privileges
4. Regularly review logs and notifications

## API Reference

The agent uses AdGuard Home's official API:
- `GET /control/status` - System status
- `GET /control/querylog` - DNS query logs

See [AdGuard Home API Documentation](https://github.com/AdguardTeam/AdGuardHome/wiki/API) for details.

## Customization

### Adding Custom Logic
Modify the `is_educational_domain()` method in `adguard_monitor.py` for custom filtering.

### Multiple Domain Lists
Create separate domain files for different categories:
```bash
python adguard_monitor.py --educational-domains stem_domains.txt
```

### Advanced Filtering
Extend the `analyze_queries()` method to add time-based rules, category filtering, or other logic.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AdGuard Home logs
3. Test with the connection test script
4. Examine the agent's output logs