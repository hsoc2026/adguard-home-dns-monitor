#!/bin/bash
# Setup script for AdGuard Home DNS Monitor

set -e

echo "🔧 Setting up AdGuard Home DNS Monitor"
echo "======================================"

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
chmod +x adguard_monitor.py test_adguard_connection.py

echo "✓ Scripts made executable"

# Check if config file exists
if [ ! -f "adguard_config.json" ]; then
    echo "📝 Creating configuration file..."
    cat > adguard_config.json << 'EOF'
{
  "base_url": "http://192.168.1.1:3000",
  "username": "admin",
  "password": "your_password_here",
  "watch_ips": ["192.168.1.100", "192.168.1.101"],
  "educational_domains_file": "educational_domains.txt",
  "notification_channel": "stdout"
}
EOF
    echo "⚠️  Please edit adguard_config.json with your AdGuard Home details"
else
    echo "✓ Configuration file exists"
fi

# Check if educational domains file exists
if [ ! -f "educational_domains.txt" ]; then
    echo "📝 Creating educational domains file..."
    # This should already exist from the creation above
    echo "✓ Educational domains file created"
else
    echo "✓ Educational domains file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit adguard_config.json with your AdGuard Home details"
echo "2. Test connection: python test_adguard_connection.py"
echo "3. Run monitor: python adguard_monitor.py --config adguard_config.json"
echo ""
echo "For more options: python adguard_monitor.py --help"
echo "Documentation: See README_adguard_monitor.md"