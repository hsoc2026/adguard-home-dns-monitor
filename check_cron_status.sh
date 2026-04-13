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
