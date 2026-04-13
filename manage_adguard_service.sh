#!/bin/bash
# Management script for AdGuard Home DNS Monitor service

SERVICE_NAME="com.aaron.adguard-monitor"
SERVICE_FILE="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"
LOG_DIR="$HOME/.openclaw/workspace/logs"

case "$1" in
    start)
        echo "🚀 Starting AdGuard Monitor service..."
        launchctl load "$SERVICE_FILE"
        launchctl start "$SERVICE_NAME"
        echo "✅ Service started"
        ;;
    
    stop)
        echo "🛑 Stopping AdGuard Monitor service..."
        launchctl stop "$SERVICE_NAME"
        launchctl unload "$SERVICE_FILE"
        echo "✅ Service stopped"
        ;;
    
    restart)
        echo "🔁 Restarting AdGuard Monitor service..."
        launchctl stop "$SERVICE_NAME" 2>/dev/null
        launchctl unload "$SERVICE_FILE" 2>/dev/null
        sleep 2
        launchctl load "$SERVICE_FILE"
        launchctl start "$SERVICE_NAME"
        echo "✅ Service restarted"
        ;;
    
    status)
        echo "📊 AdGuard Monitor Service Status"
        echo "================================="
        
        # Check if service is loaded
        if launchctl list | grep -q "$SERVICE_NAME"; then
            echo "✅ Service: LOADED"
            
            # Get PID
            PID=$(ps aux | grep adguard_monitor | grep -v grep | awk '{print $2}')
            if [ -n "$PID" ]; then
                echo "✅ Process: RUNNING (PID: $PID)"
                
                # Check how long it's been running
                UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | xargs)
                echo "⏱️  Uptime: $UPTIME"
            else
                echo "⚠️  Process: NOT RUNNING (but service is loaded)"
            fi
        else
            echo "❌ Service: NOT LOADED"
        fi
        
        # Check logs
        echo ""
        echo "📁 Log Files:"
        if [ -d "$LOG_DIR" ]; then
            ls -la "$LOG_DIR/"
            
            echo ""
            echo "📝 Recent log entries:"
            if [ -f "$LOG_DIR/adguard-monitor.log" ]; then
                echo "Main log (last 5 lines):"
                tail -5 "$LOG_DIR/adguard-monitor.log" 2>/dev/null || echo "  (empty)"
            else
                echo "Main log: (not created yet)"
            fi
            
            echo ""
            if [ -f "$LOG_DIR/adguard-monitor.error.log" ]; then
                ERROR_COUNT=$(wc -l < "$LOG_DIR/adguard-monitor.error.log")
                echo "Error log: $ERROR_COUNT lines"
                if [ "$ERROR_COUNT" -gt 0 ]; then
                    echo "Last error:"
                    tail -1 "$LOG_DIR/adguard-monitor.error.log"
                fi
            else
                echo "Error log: (not created yet)"
            fi
        else
            echo "Log directory not found: $LOG_DIR"
        fi
        
        # Check AdGuard connection
        echo ""
        echo "🌐 AdGuard Home Connection:"
        if command -v curl >/dev/null 2>&1; then
            # Try to load config and test
            CONFIG_FILE="$HOME/.openclaw/workspace/adguard_config.json"
            if [ -f "$CONFIG_FILE" ]; then
                # Extract credentials (simplified)
                BASE_URL=$(grep '"base_url"' "$CONFIG_FILE" | cut -d'"' -f4)
                if curl -s -I "$BASE_URL" >/dev/null 2>&1; then
                    echo "✅ AdGuard Home is accessible at: $BASE_URL"
                else
                    echo "❌ Cannot reach AdGuard Home at: $BASE_URL"
                fi
            else
                echo "⚠️  Config file not found: $CONFIG_FILE"
            fi
        else
            echo "⚠️  curl not available for connection test"
        fi
        ;;
    
    logs)
        echo "📋 Showing logs..."
        echo ""
        echo "=== MAIN LOG ==="
        tail -20 "$LOG_DIR/adguard-monitor.log" 2>/dev/null || echo "Main log is empty"
        
        echo ""
        echo "=== ERROR LOG ==="
        tail -20 "$LOG_DIR/adguard-monitor.error.log" 2>/dev/null || echo "Error log is empty"
        ;;
    
    follow)
        echo "👀 Following logs (Ctrl+C to stop)..."
        tail -f "$LOG_DIR/adguard-monitor.log" "$LOG_DIR/adguard-monitor.error.log" 2>/dev/null
        ;;
    
    test)
        echo "🧪 Testing monitor functionality..."
        cd "$HOME/.openclaw/workspace"
        
        # Check Python
        if ! command -v python3 >/dev/null 2>&1; then
            echo "❌ Python3 not found"
            exit 1
        fi
        
        # Check requests module
        if ! python3 -c "import requests" 2>/dev/null; then
            echo "❌ Python requests module not installed"
            echo "   Run: pip3 install requests"
            exit 1
        fi
        
        # Test AdGuard connection
        echo "Testing AdGuard Home connection..."
        python3 -c "
import requests, json, sys
try:
    with open('adguard_config.json', 'r') as f:
        config = json.load(f)
    
    session = requests.Session()
    session.auth = (config['username'], config['password'])
    
    response = session.get(f'{config[\"base_url\"]}/control/status', timeout=10)
    if response.status_code == 200:
        print('✅ AdGuard Home connection successful')
        sys.exit(0)
    else:
        print(f'❌ Connection failed: HTTP {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
        "
        ;;
    
    help|*)
        echo "AdGuard Home DNS Monitor Service Manager"
        echo "Usage: $0 {start|stop|restart|status|logs|follow|test|help}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status and logs"
        echo "  logs    - Show recent logs"
        echo "  follow  - Follow logs in real-time"
        echo "  test    - Test monitor functionality"
        echo "  help    - Show this help"
        ;;
esac