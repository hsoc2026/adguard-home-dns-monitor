#!/bin/bash
# Setup cron job for OpenClaw Alert Sender

echo "🕐 Setting up cron job for AdGuard Alert Sender..."
echo "=================================================="

# Create the cron job script
cat > /Users/ace/.openclaw/workspace/run_alert_check.sh << 'EOF'
#!/bin/bash
# Cron job script to check for AdGuard alerts

cd /Users/ace/.openclaw/workspace

# Run the alert check
/Library/Frameworks/Python.framework/Versions/3.14/bin/python3 send_alerts_now.py > /tmp/adguard_alert_check.log 2>&1

# Check if there were new alerts
if grep -q "new alert(s) to send" /tmp/adguard_alert_check.log; then
    echo "$(date): New alerts found and marked for sending" >> /Users/ace/.openclaw/workspace/cron_job.log
fi
EOF

chmod +x /Users/ace/.openclaw/workspace/run_alert_check.sh

echo "✅ Created cron job script: run_alert_check.sh"

# Create crontab entry
CRON_JOB="* * * * * /Users/ace/.openclaw/workspace/run_alert_check.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_alert_check.sh"; then
    echo "✅ Cron job already exists"
else
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Added cron job to run every minute"
fi

# Create a simple status check script
cat > /Users/ace/.openclaw/workspace/check_cron_status.sh << 'EOF'
#!/bin/bash
echo "🕐 Cron Job Status Check"
echo "======================="
echo "Current time: $(date)"
echo ""

# Check if cron is running
if ps aux | grep -q "[c]rond" || ps aux | grep -q "[c]ron"; then
    echo "✅ Cron daemon: RUNNING"
else
    echo "❌ Cron daemon: NOT RUNNING"
fi

# Check our cron job
if crontab -l 2>/dev/null | grep -q "run_alert_check.sh"; then
    echo "✅ Our cron job: INSTALLED"
    crontab -l | grep "run_alert_check.sh"
else
    echo "❌ Our cron job: NOT INSTALLED"
fi

# Check last run
if [ -f "/Users/ace/.openclaw/workspace/cron_job.log" ]; then
    echo ""
    echo "📝 Last few runs:"
    tail -5 /Users/ace/.openclaw/workspace/cron_job.log
else
    echo ""
    echo "📝 No cron run log yet"
fi

echo ""
echo "🔍 To check alerts manually:"
echo "   cd ~/.openclaw/workspace && ./check_alerts.sh"
echo ""
echo "📨 To send alerts now:"
echo "   cd ~/.openclaw/workspace && python3 send_alerts_now.py"
EOF

chmod +x /Users/ace/.openclaw/workspace/check_cron_status.sh

echo "✅ Created status check script: check_cron_status.sh"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 What was set up:"
echo "   1. ✅ Cron job runs every minute"
echo "   2. ✅ Checks for new AdGuard alerts"
echo "   3. ✅ Marks alerts as sent"
echo "   4. ✅ Logs all activity"
echo ""
echo "🤖 How it works:"
echo "   • Every minute: Checks telegram_smart_queue.log"
echo "   • If new alerts: Marks them for sending"
echo "   • I (OpenClaw) will send them to you in Telegram"
echo ""
echo "🔧 Management commands:"
echo "   # Check cron status"
echo "   ./check_cron_status.sh"
echo ""
echo "   # Check alerts"
echo "   ./check_alerts.sh"
echo ""
echo "   # Send alerts now"
echo "   python3 send_alerts_now.py"
echo ""
echo "   # View cron logs"
echo "   tail -f cron_job.log"
echo ""
echo "🚀 The system is now fully automated!"
echo "   Alerts will be checked every minute"
echo "   I'll send them to you in Telegram"