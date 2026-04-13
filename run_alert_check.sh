#!/bin/bash
# Cron job script to check for AdGuard alerts

cd /Users/ace/.openclaw/workspace/adguard_monitor_project

# Run the alert check
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 send_alerts_now.py > /tmp/adguard_alert_check.log 2>&1

# Check if there were new alerts
if grep -q "new alert(s) to send" /tmp/adguard_alert_check.log; then
    echo "$(date): New alerts found and marked for sending" >> /Users/ace/.openclaw/workspace/adguard_monitor_project/cron_job.log
fi
