# AdGuard Home DNS Monitor - Project Organization

## 📁 Folder Structure

```
/Users/ace/.openclaw/workspace/
├── adguard_monitor_project/          # Main project folder
│   ├── adguard_monitor_smart.py      # Main smart monitor script
│   ├── adguard_config.json           # Configuration file
│   ├── educational_domains.txt       # Educational domains list
│   ├── telegram_smart_notifier.py    # Telegram notifier
│   ├── web_investigator.py           # Web investigator
│   ├── openclaw_alert_sender.py      # OpenClaw alert sender
│   ├── send_alerts_now.py            # Send alerts script
│   ├── check_alerts.sh               # Check alerts script
│   ├── check_cron_status.sh          # Check cron status
│   ├── run_alert_check.sh            # Cron job script
│   ├── start_alert_bot.sh            # Start alert bot
│   ├── logs/                         # Log files
│   │   ├── adguard-monitor-enhanced.log
│   │   ├── adguard-monitor-enhanced.error.log
│   │   ├── telegram-notifier.log
│   │   └── web-investigator.log
│   ├── *.log                         # Data files
│   └── *.md                          # Documentation
│
├── check_adguard_alerts.sh           # Wrapper scripts in workspace root
├── check_adguard_cron_status.sh
├── send_adguard_alerts_now.sh
└── start_adguard_alert_bot.sh
```

## 🔧 Updated Paths

### Service Files (Launchd)
- **Smart Monitor**: `~/Library/LaunchAgents/com.aaron.adguard-monitor-enhanced.plist`
  - Updated to use: `/Users/ace/.openclaw/workspace/adguard_monitor_project/adguard_monitor_smart.py`
  - Working directory: `/Users/ace/.openclaw/workspace/adguard_monitor_project`
  - Logs: `/Users/ace/.openclaw/workspace/adguard_monitor_project/logs/`

- **Telegram Notifier**: `~/Library/LaunchAgents/com.aaron.telegram-notifier.plist`
  - Updated to use: `/Users/ace/.openclaw/workspace/adguard_monitor_project/telegram_smart_notifier.py`

- **Web Investigator**: `~/Library/LaunchAgents/com.aaron.web-investigator.plist`
  - Updated to use: `/Users/ace/.openclaw/workspace/adguard_monitor_project/web_investigator.py`

### Cron Job
- **Updated crontab**: Runs every minute
- **Command**: `/Users/ace/.openclaw/workspace/adguard_monitor_project/run_alert_check.sh`
- **Working directory**: `/Users/ace/.openclaw/workspace/adguard_monitor_project`

## 🚀 Management Commands

### New Wrapper Commands (in workspace root):
```bash
# Check alerts
./check_adguard_alerts.sh

# Check cron status
./check_adguard_cron_status.sh

# Send alerts now
./send_adguard_alerts_now.sh

# Start alert bot
./start_adguard_alert_bot.sh
```

### Direct Commands (in project folder):
```bash
cd ~/.openclaw/workspace/adguard_monitor_project

# Run any script directly
python3 send_alerts_now.py
./check_alerts.sh
./check_cron_status.sh
```

### Service Management:
```bash
# Check services
launchctl list | grep aaron

# Restart smart monitor
launchctl stop com.aaron.adguard-monitor-enhanced
launchctl start com.aaron.adguard-monitor-enhanced

# Restart all services
launchctl unload ~/Library/LaunchAgents/com.aaron.*.plist
launchctl load ~/Library/LaunchAgents/com.aaron.*.plist
```

## 📊 Current Status

✅ **Services Running:**
- Smart AdGuard Monitor (PID: from Launchd)
- Telegram Notifier (loaded)
- Web Investigator (loaded)

✅ **Cron Job:** Configured to run every minute

✅ **Detection Working:** System is detecting gaming/entertainment sites

✅ **Organization Complete:** All files moved to `adguard_monitor_project/`

## 🎯 Testing the System

1. **From monitored device** (`192.168.7.36`, `192.168.7.112`, `192.168.7.30`):
   ```bash
   # Visit gaming/entertainment site
   # Example: store.steampowered.com, netflix.com, youtube.com
   ```

2. **Check for detection**:
   ```bash
   cd ~/.openclaw/workspace
   ./check_adguard_alerts.sh
   ```

3. **Send alerts** (I'll send them in Telegram):
   ```bash
   ./send_adguard_alerts_now.sh
   ```

## 🔄 Files Moved to Project Folder

### Scripts:
- `adguard_monitor_smart.py` - Main smart monitor
- `telegram_smart_notifier.py` - Telegram notifier
- `web_investigator.py` - Web investigator
- `openclaw_alert_sender.py` - OpenClaw alert sender
- `send_alerts_now.py` - Send alerts script
- All other Python and shell scripts

### Configuration:
- `adguard_config.json` - AdGuard Home configuration
- `educational_domains.txt` - Educational domains list

### Data & Logs:
- All `*.log` files (violations, suspicious domains, cron logs)
- Logs moved to `logs/` subfolder

### Documentation:
- `README_adguard_monitor.md`
- `SERVICE_SETUP_COMPLETE.md`
- `TELEGRAM_NOTIFIER_SETUP.md`
- `SKILL_adguard_monitor.md`

## 📝 Notes

1. **All paths updated** in service files and cron job
2. **Wrapper scripts created** in workspace root for easy access
3. **Services restarted** with new paths
4. **System fully operational** with new organization
5. **Logs and data preserved** in project folder

The AdGuard Home DNS Monitor project is now neatly organized in its own folder while maintaining full functionality!