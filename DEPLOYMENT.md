# Deployment Guide - Autonomous Replicator 7G

## 🎯 Overview

This guide covers deployment scenarios for the Autonomous Replicator 7G system. All deployments should be conducted in **authorized environments only**.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+) or macOS
- **Python**: 3.9 or higher
- **Memory**: Minimum 512MB, Recommended 2GB
- **Storage**: 500MB for application + space for logs/data
- **Network**: Ethernet or WiFi with appropriate permissions

### Software Requirements

```bash
# Python and pip
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3-venv

# Git
sudo apt-get install git

# Optional: Docker
sudo apt-get install docker.io docker-compose
```

## 🔧 Deployment Methods

### Method 1: Standard Python Deployment

#### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/autonomous_replicator_7g.git
cd autonomous_replicator_7g

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure

```bash
# Copy example config
cp config/config.yaml config/production_config.yaml

# Edit configuration
nano config/production_config.yaml
```

**Key Configuration Items:**

```yaml
# Network range for scanning
network:
  default_scan_range: "10.0.0.0/24"  # Your network

# Risk tolerance
ai_engine:
  risk_tolerance: 0.5  # Lower = more conservative

# Stealth settings
stealth:
  level: "maximum"
```

#### Step 3: Initialize Database

```bash
# Create data directory
mkdir -p data logs

# Test database connection
python3 -c "
import asyncio
from src.database_handler import DatabaseHandler

async def test():
    db = DatabaseHandler('data/replicator.db')
    await db.connect()
    print('Database initialized successfully')
    await db.disconnect()

asyncio.run(test())
"
```

#### Step 4: Run Tests

```bash
# Run test suite
python -m pytest tests/ -v

# Verify all modules
python tests/test_replicator.py
python tests/test_quantum.py
```

#### Step 5: Deploy

```bash
# Start replicator
python src/autonomous_replicator_7g.py

# Or with custom config
python src/autonomous_replicator_7g.py --config config/production_config.yaml

# Run in background
nohup python src/autonomous_replicator_7g.py > logs/output.log 2>&1 &
```

### Method 2: Docker Deployment

#### Step 1: Build Image

```bash
# Build Docker image
docker build -t autonomous-replicator:7.0 .

# Verify image
docker images | grep autonomous-replicator
```

#### Step 2: Configure Volumes

```bash
# Create persistent volumes
docker volume create replicator-data
docker volume create replicator-logs
```

#### Step 3: Run Container

```bash
# Run with volumes
docker run -d \
  --name replicator \
  --network host \
  -v replicator-data:/app/data \
  -v replicator-logs:/app/logs \
  -v $(pwd)/config:/app/config:ro \
  autonomous-replicator:7.0

# Check logs
docker logs -f replicator
```

#### Step 4: Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Method 3: Systemd Service (Linux)

#### Step 1: Create Service File

```bash
sudo nano /etc/systemd/system/autonomous-replicator.service
```

```ini
[Unit]
Description=Autonomous Replicator 7G
After=network.target

[Service]
Type=simple
User=replicator
WorkingDirectory=/opt/autonomous_replicator_7g
Environment="PATH=/opt/autonomous_replicator_7g/venv/bin"
ExecStart=/opt/autonomous_replicator_7g/venv/bin/python src/autonomous_replicator_7g.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 2: Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable autonomous-replicator

# Start service
sudo systemctl start autonomous-replicator

# Check status
sudo systemctl status autonomous-replicator

# View logs
sudo journalctl -u autonomous-replicator -f
```

## 🔒 Security Hardening

### Filesystem Permissions

```bash
# Create dedicated user
sudo useradd -r -s /bin/false replicator

# Set ownership
sudo chown -R replicator:replicator /opt/autonomous_replicator_7g

# Restrict permissions
chmod 700 /opt/autonomous_replicator_7g/data
chmod 700 /opt/autonomous_replicator_7g/logs
chmod 600 /opt/autonomous_replicator_7g/config/config.yaml
```

### Network Isolation

```bash
# Create isolated Docker network
docker network create --driver bridge replicator-net

# Run in isolated network
docker run -d \
  --name replicator \
  --network replicator-net \
  autonomous-replicator:7.0
```

### Firewall Rules

```bash
# Allow only necessary outbound
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check if running
ps aux | grep autonomous_replicator

# Or with systemd
sudo systemctl status autonomous-replicator

# Or with Docker
docker ps | grep replicator
```

### Log Monitoring

```bash
# Tail logs
tail -f logs/replicator.log

# Search for errors
grep ERROR logs/replicator.log

# Monitor in real-time
watch -n 5 'tail -20 logs/replicator.log'
```

### Database Maintenance

```bash
# Backup database
cp data/replicator.db data/replicator.db.backup.$(date +%Y%m%d)

# Export data
python3 -c "
import asyncio
from src.database_handler import DatabaseHandler

async def export():
    db = DatabaseHandler()
    await db.connect()
    await db.export_data('backup/export.json')
    await db.disconnect()

asyncio.run(export())
"
```

### Performance Monitoring

```bash
# Monitor resources
top -p $(pgrep -f autonomous_replicator)

# Or with Docker
docker stats replicator

# Database size
du -h data/replicator.db

# Log size
du -h logs/
```

## 🔄 Updates and Upgrades

### Updating Code

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart autonomous-replicator
```

### Database Migration

```bash
# Backup first
cp data/replicator.db data/replicator.db.pre-migration

# Run migrations (if any)
python scripts/migrate_database.py

# Verify
python tests/test_database.py
```

## 🚨 Troubleshooting

### Common Issues

#### Issue: Permission Denied

```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/autonomous_replicator_7g
chmod +x src/autonomous_replicator_7g.py
```

#### Issue: Port Already in Use

```bash
# Find process using port
sudo lsof -i :PORT_NUMBER

# Kill process
kill -9 PID
```

#### Issue: Database Locked

```bash
# Check for multiple instances
ps aux | grep autonomous_replicator

# Kill duplicates
killall autonomous_replicator_7g.py
```

#### Issue: Out of Memory

```bash
# Check memory
free -h

# Increase swap (temporary)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🧪 Testing Deployment

### Functional Tests

```bash
# Run full test suite
python -m pytest tests/ -v --tb=short

# Test network connectivity
python3 -c "
import asyncio
from src.stealth_operations import StealthModule

async def test():
    stealth = StealthModule()
    await stealth.activate()
    targets = await stealth.scan_targets('127.0.0.1/32')
    print(f'Test complete: {len(targets)} targets found')

asyncio.run(test())
"
```

### Load Testing

```bash
# Simulate multiple targets
for i in {1..10}; do
    python scripts/simulate_target.py &
done

# Monitor performance
python scripts/monitor_performance.py
```

## 📋 Deployment Checklist

- [ ] Environment meets minimum requirements
- [ ] All dependencies installed
- [ ] Configuration files customized
- [ ] Database initialized
- [ ] Tests passed
- [ ] Permissions configured correctly
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Documentation reviewed
- [ ] Authorization obtained
- [ ] Security measures implemented

## 🔐 Production Best Practices

### 1. Configuration Management

```bash
# Use environment-specific configs
config/
  ├── config.yaml           # Default
  ├── development.yaml      # Dev
  ├── staging.yaml         # Staging
  └── production.yaml      # Production
```

### 2. Secrets Management

```bash
# Never commit secrets
echo "*.yaml" >> .gitignore
echo "*.key" >> .gitignore

# Use environment variables
export REPLICATOR_DB_PASSWORD="secure_password"
```

### 3. Monitoring

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/autonomous-replicator

/opt/autonomous_replicator_7g/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 replicator replicator
}
```

### 4. Backup Strategy

```bash
# Automated backups
echo "0 2 * * * /opt/autonomous_replicator_7g/scripts/backup.sh" | crontab -
```

## 📞 Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Run diagnostic script: `python scripts/diagnose.py`
4. Open GitHub issue with logs

## ⚠️ Important Reminders

- **Always** obtain proper authorization before deployment
- **Never** deploy on networks you don't own/manage
- **Always** run in isolated/controlled environments
- **Keep** detailed deployment logs
- **Monitor** continuously for issues
- **Backup** regularly

---

**Next Steps**: See [README.md](README.md) for usage instructions.
