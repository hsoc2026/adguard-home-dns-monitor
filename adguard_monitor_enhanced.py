    parser = argparse.ArgumentParser(description='Enhanced AdGuard Home DNS Monitor')
    parser.add_argument('--config', '-c', default='adguard_config.json',
                       help='Configuration file (JSON)')
    parser.add_argument('--educational-domains', '-e',
                       help='File with educational domains (one per line)')
    parser.add_argument('--interval', '-i', type=int, default=10,
                       help='Check interval in seconds')
    parser.add_argument('--notify', '-n', default='stdout',
                       choices=['telegram', 'stdout', 'file'],
                       help='Notification channel')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Required configuration
    required = ['base_url', 'username', 'password', 'watch_ips']
    missing = [key for key in required if key not in config]
    
    if missing:
        logger.error(f"Missing required config keys: {', '.join(missing)}")
        sys.exit(1)
    
    # Create monitor
    try:
        monitor = EnhancedAdGuardMonitor(
            base_url=config['base_url'],
            username=config['username'],
            password=config['password'],
            watch_ips=config['watch_ips'],
            educational_domains_file=args.educational_domains or config.get('educational_domains_file'),
            check_interval=args.interval,
            notification_channel=args.notify
        )
        
        # Start monitoring
        monitor.run()
        
    except Exception as e:
        logger.error(f"Failed to start monitor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()