#!/usr/bin/env python3
"""
Configure AdGuard Monitor from YAML configuration file.
Updates all scripts with settings from config.yaml.
"""

import yaml
import json
import os
import re
from pathlib import Path

def load_config(config_file="config.yaml"):
    """Load configuration from YAML file."""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def update_adguard_config(config, output_file="adguard_config.json"):
    """Update AdGuard configuration JSON file."""
    adguard_config = {
        "base_url": config['adguard']['base_url'],
        "username": config['adguard']['username'],
        "password": config['adguard']['password'],
        "watch_ips": config['monitoring']['watch_ips'],
        "educational_domains_file": config['monitoring']['educational_domains_file'],
        "notification_channel": config['monitoring']['notification_channel']
    }
    
    with open(output_file, 'w') as f:
        json.dump(adguard_config, f, indent=2)
    
    print(f"✅ Updated {output_file}")

def update_telegram_notifier(config, script_file="telegram_smart_notifier.py"):
    """Update Telegram notifier script with configuration."""
    with open(script_file, 'r') as f:
        content = f.read()
    
    # Update account and target
    telegram_config = config.get('telegram', {})
    if telegram_config:
        account = telegram_config.get('account', '')
        target = telegram_config.get('target', '')
        
        # Find and replace the command list
        pattern = r"cmd = \[.*?\]"
        new_cmd = f"""cmd = [
                '{config.get('openclaw', {}).get('cli_path', '/opt/homebrew/bin/openclaw')}', 'message', 'send',
                '--channel', 'telegram',
                '--account', '{account}',
                '--target', '{target}',
                '--message', message
            ]"""
        
        content = re.sub(pattern, new_cmd, content, flags=re.DOTALL)
        
        # Update check interval if specified
        check_interval = telegram_config.get('check_interval', 15)
        content = re.sub(r'check_interval=(\d+)', f'check_interval={check_interval}', content)
    
    with open(script_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {script_file}")

def update_send_alerts_now(config, script_file="send_alerts_now.py"):
    """Update send_alerts_now script with configuration."""
    with open(script_file, 'r') as f:
        content = f.read()
    
    # Update Telegram sending command
    telegram_config = config.get('telegram', {})
    if telegram_config:
        account = telegram_config.get('account', '')
        target = telegram_config.get('target', '')
        
        # Find and replace the command list
        pattern = r"cmd = \[.*?\]"
        new_cmd = f"""cmd = [
            '{config.get('openclaw', {}).get('cli_path', '/opt/homebrew/bin/openclaw')}', 'message', 'send',
            '--channel', 'telegram',
            '--account', '{account}',
            '--target', '{target}',
            '--message', message
        ]"""
        
        content = re.sub(pattern, new_cmd, content, flags=re.DOTALL)
    
    with open(script_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {script_file}")

def update_web_investigator(config, script_file="web_investigator.py"):
    """Update web investigator script with configuration."""
    with open(script_file, 'r') as f:
        content = f.read()
    
    # Update Telegram sending command
    telegram_config = config.get('telegram', {})
    if telegram_config:
        account = telegram_config.get('account', '')
        target = telegram_config.get('target', '')
        
        # Find and replace the command list
        pattern = r"cmd = \[.*?\]"
        new_cmd = f"""cmd = [
                '{config.get('openclaw', {}).get('cli_path', '/opt/homebrew/bin/openclaw')}', 'message', 'send',
                '--channel', 'telegram',
                '--account', '{account}',
                '--target', '{target}',
                '--message', message
            ]"""
        
        content = re.sub(pattern, new_cmd, content, flags=re.DOTALL)
    
    with open(script_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {script_file}")

def update_service_files(config):
    """Update service files with configuration."""
    service_config = config.get('service', {})
    
    if not service_config:
        return
    
    python_path = service_config.get('python_path', '/usr/bin/python3')
    working_dir = service_config.get('working_dir', str(Path.cwd()))
    
    # Update macOS Launchd plist files
    for plist_file in Path('.').glob('*.plist'):
        with open(plist_file, 'r') as f:
            content = f.read()
        
        # Update Python path
        content = re.sub(r'<string>/[^<]+/python3</string>', 
                        f'<string>{python_path}</string>', content)
        
        # Update working directory
        content = re.sub(r'<string>/[^<]+</string>\s*<key>WorkingDirectory</key>',
                        f'<string>{working_dir}</string>\n    <key>WorkingDirectory</key>', content)
        
        with open(plist_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {plist_file}")
    
    # Update Linux systemd service files
    for service_file in Path('.').glob('*.service'):
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Update working directory
        content = re.sub(r'WorkingDirectory=[^\n]+', 
                        f'WorkingDirectory={working_dir}', content)
        
        # Update exec command
        content = re.sub(r'ExecStart=/[^\s]+', 
                        f'ExecStart={python_path}', content)
        
        with open(service_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {service_file}")

def create_logs_directory(config):
    """Create logs directory if it doesn't exist."""
    log_dir = config.get('logging', {}).get('log_dir', 'logs')
    Path(log_dir).mkdir(exist_ok=True)
    print(f"✅ Created/verified logs directory: {log_dir}")

def main():
    """Main configuration function."""
    config_file = "config.yaml"
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file {config_file} not found.")
        print(f"   Copy config_template.yaml to {config_file} and edit it.")
        return
    
    print("🔧 Configuring AdGuard Home DNS Monitor from YAML...")
    
    try:
        config = load_config(config_file)
        
        # Update configurations
        update_adguard_config(config)
        update_telegram_notifier(config)
        update_send_alerts_now(config)
        update_web_investigator(config)
        update_service_files(config)
        create_logs_directory(config)
        
        print("\n✅ Configuration complete!")
        print("\n📋 Next steps:")
        print("   1. Review the updated configuration files")
        print("   2. Test the system: python adguard_monitor_smart.py --test")
        print("   3. Set up services (see SETUP.md for instructions)")
        
    except Exception as e:
        print(f"❌ Error during configuration: {e}")
        raise

if __name__ == "__main__":
    main()