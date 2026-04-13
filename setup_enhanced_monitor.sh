#!/bin/bash
# Setup Enhanced AdGuard Home DNS Monitor with intelligent filtering

set -e

echo "🔧 Setting up Enhanced AdGuard Home DNS Monitor"
echo "================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install requests || {
    echo "⚠️  Failed to install requests via pip, trying pip3..."
    pip3 install requests || {
        echo "❌ Failed to install requests. Please install manually:"
        echo "   pip install requests"
        exit 1
    }
}

echo "✓ Dependencies installed"

# Make scripts executable
chmod +x adguard_monitor_enhanced.py web_investigator.py

echo "✓ Scripts made executable"

# Check if config file exists
if [ ! -f "adguard_config.json" ]; then
    echo "❌ Configuration file not found: adguard_config.json"
    echo "   Please run the configuration wizard first:"
    echo "   python configure_monitor.py"
    exit 1
else
    echo "✓ Configuration file exists"
fi

# Create Launchd service for enhanced monitor
echo "📝 Creating enhanced monitor service..."
cat > ~/Library/LaunchAgents/com.aaron.adguard-monitor-enhanced.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aaron.adguard-monitor-enhanced</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Library/Frameworks/Python.framework/Versions/3.14/bin/python3</string>
        <string>/Users/ace/.openclaw/workspace/adguard_monitor_enhanced.py</string>
        <string>--config</string>
        <string>/Users/ace/.openclaw/workspace/adguard_config.json</string>
        <string>--notify</string>
        <string>telegram</string>
        <string>--interval</string>
        <string>30</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/ace/.openclaw/workspace/logs/adguard-monitor-enhanced.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/ace/.openclaw/workspace/logs/adguard-monitor-enhanced.error.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/ace/.openclaw/workspace</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Library/Frameworks/Python.framework/Versions/3.14/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONPATH</key>
        <string>/Users/ace/.openclaw/workspace</string>
    </dict>
</dict>
</plist>
EOF

echo "✓ Enhanced monitor service file created"

# Create Launchd service for web investigator
echo "📝 Creating web investigator service..."
cat > ~/Library/LaunchAgents/com.aaron.web-investigator.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aaron.web-investigator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Library/Frameworks/Python.framework/Versions/3.14/bin/python3</string>
        <string>/Users/ace/.openclaw/workspace/web_investigator.py</string>
        <string>--interval</string>
        <string>600</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StartInterval</key>
    <integer>600</integer>
    <key>StandardOutPath</key>
    <string>/Users/ace/.openclaw/workspace/logs/web-investigator.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/ace/.openclaw/workspace/logs/web-investigator.error.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/ace/.openclaw/workspace</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Library/Frameworks/Python.framework/Versions/3.14/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONPATH</key>
        <string>/Users/ace/.openclaw/workspace</string>
    </dict>
</dict>
</plist>
EOF

echo "✓ Web investigator service file created"

# Stop old service if running
echo "🛑 Stopping old monitor service..."
launchctl unload ~/Library/LaunchAgents/com.aaron.adguard-monitor.plist 2>/dev/null || true

# Start new services
echo "🚀 Starting enhanced monitor service..."
launchctl load ~/Library/LaunchAgents/com.aaron.adguard-monitor-enhanced.plist
launchctl start com.aaron.adguard-monitor-enhanced

echo "🚀 Starting web investigator service..."
launchctl load ~/Library/LaunchAgents/com.aaron.web-investigator.plist
launchctl start com.aaron.web-investigator

echo ""
echo "✅ Enhanced setup complete!"
echo ""
echo "📋 Services running:"
echo "   1. Enhanced AdGuard Monitor - Intelligent filtering"
echo "   2. Web Investigator - Browses suspicious sites"
echo ""
echo "🎯 Features:"
echo "   • Ignores telemetry/search/system sites"
echo "   • Pattern-based game/entertainment detection"
echo "   • Web investigation for suspicious sites"
echo "   • Smart notifications only for confirmed violations"
echo ""
echo "📁 Log files:"
echo "   • logs/adguard-monitor-enhanced.log - Main monitor log"
echo "   • logs/web-investigator.log - Web investigation log"
echo "   • needs_investigation.log - Sites needing manual review"
echo "   • telegram_queue_enhanced.log - Notifications for Telegram"
echo ""
echo "🔧 Management:"
echo "   # Check status"
echo "   launchctl list | grep aaron"
echo ""
echo "   # View enhanced monitor logs"
echo "   tail -f logs/adguard-monitor-enhanced.log"
echo ""
echo "   # View investigation results"
echo "   tail -f logs/web-investigator.log"
echo ""
echo "   # Stop services"
echo "   launchctl unload ~/Library/LaunchAgents/com.aaron.adguard-monitor-enhanced.plist"
echo "   launchctl unload ~/Library/LaunchAgents/com.aaron.web-investigator.plist"
echo ""
echo "📝 Next steps:"
echo "   1. Test by visiting a game/entertainment site from monitored device"
echo "   2. Check logs for detection"
echo "   3. Review needs_investigation.log for false positives"
echo ""
echo "The enhanced system will now:"
echo "1. Ignore Microsoft/Google telemetry, search engines, CDNs"
echo "2. Use pattern matching to detect games/entertainment"
echo "3. Browse to suspicious sites for confirmation"
echo "4. Only notify for confirmed violations"