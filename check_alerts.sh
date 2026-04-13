#!/bin/bash
# Check for AdGuard Monitor alerts and display them

echo "🔍 Checking for AdGuard Monitor alerts..."
echo "========================================"

# Check if smart monitor is running
if ps aux | grep -q "adguard_monitor_smart" | grep -v grep; then
    echo "✅ Smart monitor: RUNNING"
else
    echo "❌ Smart monitor: NOT RUNNING"
fi

# Check if Telegram notifier is running
if ps aux | grep -q "telegram_smart_notifier" | grep -v grep; then
    echo "✅ Telegram notifier: RUNNING"
else
    echo "❌ Telegram notifier: NOT RUNNING"
fi

echo ""
echo "📊 Recent detections:"

# Check smart violations log
if [ -f "smart_violations.log" ]; then
    VIOLATION_COUNT=$(grep -c "🚨" smart_violations.log)
    echo "✅ Smart violations: $VIOLATION_COUNT total"
    
    # Show last 3 violations
    echo ""
    echo "Last 3 violations:"
    grep -A 3 "🚨" smart_violations.log | tail -12 || echo "  (none)"
else
    echo "❌ No violations log found"
fi

# Check suspicious domains
if [ -f "suspicious_domains.log" ]; then
    SUSPICIOUS_COUNT=$(wc -l < suspicious_domains.log)
    echo ""
    echo "🔎 Suspicious domains: $SUSPICIOUS_COUNT total"
    
    # Show last 5
    echo ""
    echo "Last 5 suspicious domains:"
    tail -5 suspicious_domains.log 2>/dev/null || echo "  (none)"
fi

# Check Telegram queue
if [ -f "telegram_smart_queue.log" ]; then
    QUEUE_COUNT=$(grep -c "🚨" telegram_smart_queue.log)
    echo ""
    echo "📨 Telegram queue: $QUEUE_COUNT messages waiting"
    
    # Show queued messages
    if [ $QUEUE_COUNT -gt 0 ]; then
        echo ""
        echo "Queued alerts:"
        grep -B 1 "🚨" telegram_smart_queue.log | tail -10
    fi
else
    echo ""
    echo "📨 Telegram queue: (empty)"
fi

echo ""
echo "🎯 To test the system:"
echo "   1. From monitored device (192.168.7.36/112/30), visit:"
echo "      • store.steampowered.com (gaming)"
echo "      • netflix.com (entertainment)"
echo "      • youtube.com (entertainment)"
echo "   2. Wait 30 seconds"
echo "   3. Run this script again to see detections"
echo ""
echo "🛠️  Management:"
echo "   # View all logs"
echo "   tail -f logs/adguard-monitor-enhanced.log"
echo ""
echo "   # Check services"
echo "   launchctl list | grep aaron"