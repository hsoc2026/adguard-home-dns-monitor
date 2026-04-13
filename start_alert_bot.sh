#!/bin/bash
# Start the OpenClaw Alert Bot
# This will spawn an OpenClaw agent that sends AdGuard alerts to Telegram

echo "🚀 Starting OpenClaw Alert Bot..."
echo "================================="

# Check if Python script exists
if [ ! -f "openclaw_alert_sender.py" ]; then
    echo "❌ Error: openclaw_alert_sender.py not found"
    exit 1
fi

# Check if queue file exists
if [ ! -f "telegram_smart_queue.log" ]; then
    echo "⚠️  Warning: telegram_smart_queue.log not found"
    echo "   Creating empty queue file..."
    touch telegram_smart_queue.log
fi

echo "✅ Starting alert sender..."
echo "   • Check interval: 30 seconds"
echo "   • Queue file: telegram_smart_queue.log"
echo "   • Sent log: openclaw_sent_alerts.log"
echo ""
echo "📊 Current status:"

# Run status check
python3 openclaw_alert_sender.py --status

echo ""
echo "🤖 Starting alert sender in background..."
echo "   Press Ctrl+C to stop"

# Run the alert sender
python3 openclaw_alert_sender.py --interval 30

echo ""
echo "👋 Alert bot stopped"
echo ""
echo "📋 To check status anytime:"
echo "   cd ~/.openclaw/workspace && ./check_alerts.sh"
echo ""
echo "🔄 To restart:"
echo "   cd ~/.openclaw/workspace && ./start_alert_bot.sh"