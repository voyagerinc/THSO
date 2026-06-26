# Systemd Service Installation Guide

> Setup Excel Master Exporter as a systemd service for production deployment

---

## 📋 Prerequisites

- Linux system with systemd
- Application files in `/opt/excel-exporter/` (or your chosen path)
- `excel-exporter.service` file
- User account `streamlit` (optional, will be created)

---

## 🚀 Installation Steps

### Step 1: Create Dedicated User (Recommended)
```bash
# Create streamlit user
sudo useradd -r -s /bin/bash streamlit

# Create home directory
sudo mkdir -p /home/streamlit
sudo chown streamlit:streamlit /home/streamlit
```

### Step 2: Prepare Application Directory
```bash
# Create app directory
sudo mkdir -p /opt/excel-exporter
cd /opt/excel-exporter

# Copy application files
sudo cp app.py .
sudo cp streamlit_service.sh .
sudo cp *.json .
# ... copy other files

# Set ownership
sudo chown -R streamlit:streamlit /opt/excel-exporter
sudo chmod 755 /opt/excel-exporter

# Make scripts executable
sudo chmod +x streamlit_service.sh
```

### Step 3: Update Service File Paths
Edit `excel-exporter.service` and update paths:

```bash
# Original placeholders:
WorkingDirectory=/path/to/app/directory

# Update to:
WorkingDirectory=/opt/excel-exporter

# Also update:
ReadWritePaths=/path/to/app/directory
# To:
ReadWritePaths=/opt/excel-exporter
```

### Step 4: Install Service File
```bash
# Copy service file to systemd directory
sudo cp excel-exporter.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/excel-exporter.service

# Reload systemd daemon
sudo systemctl daemon-reload
```

### Step 5: Enable and Start Service
```bash
# Enable service to start on boot
sudo systemctl enable excel-exporter

# Start the service
sudo systemctl start excel-exporter

# Check status
sudo systemctl status excel-exporter
```

---

## ✅ Verification

### Check Service Status
```bash
sudo systemctl status excel-exporter

# Expected output:
# ● excel-exporter.service - Excel Master Exporter - Streamlit Service
#    Loaded: loaded (/etc/systemd/system/excel-exporter.service; enabled)
#    Active: active (running)
#    Main PID: 12345
```

### Check Service is Listening
```bash
# Check if port 8501 is open
sudo netstat -tlnp | grep 8501

# Expected output:
# tcp        0      0 0.0.0.0:8501         0.0.0.0:*         LISTEN      12345/python
```

### Access Application
```
🌐 http://localhost:8501
or
🌐 http://<your-server-ip>:8501
```

### View Logs
```bash
# View recent logs
sudo journalctl -u excel-exporter -n 50

# Follow logs in real-time
sudo journalctl -u excel-exporter -f

# View logs for specific time period
sudo journalctl -u excel-exporter --since "2024-06-12 10:00:00"
```

---

## 🛠️ Service Management

### Start Service
```bash
sudo systemctl start excel-exporter
```

### Stop Service
```bash
sudo systemctl stop excel-exporter
```

### Restart Service
```bash
sudo systemctl restart excel-exporter
```

### Enable on Boot
```bash
sudo systemctl enable excel-exporter
```

### Disable on Boot
```bash
sudo systemctl disable excel-exporter
```

### Check Service Logs
```bash
# Last 100 lines
sudo journalctl -u excel-exporter -n 100

# Real-time logs
sudo journalctl -u excel-exporter -f

# Errors only
sudo journalctl -u excel-exporter -p err
```

---

## 🔧 Configuration Options

### Change Port
Edit `/etc/systemd/system/excel-exporter.service`:

```ini
ExecStart=/usr/bin/streamlit run app.py \
    --server.port=8502 \
    ...
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart excel-exporter
```

### Change Memory Limit
Edit service file:
```ini
MemoryLimit=1G    # Increase from 512M
```

### Change CPU Quota
Edit service file:
```ini
CPUQuota=100%     # Remove CPU limit (if needed)
```

### Change Log Level
Edit service file:
```ini
--logger.level=debug    # More verbose logging
```

---

## 🔐 Security Hardening

### Restrict Network Access
```bash
# Only allow localhost (production use)
sudo ufw allow from 127.0.0.1 to any port 8501

# Or allow specific subnet
sudo ufw allow from 192.168.1.0/24 to any port 8501
```

### Use HTTPS with Reverse Proxy

**Nginx Configuration Example:**
```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 443 ssl http2;
    server_name your.domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://streamlit;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Set File Permissions
```bash
# Restrict access to config files
sudo chmod 600 /opt/excel-exporter/version.json
sudo chmod 600 /opt/excel-exporter/changelog.json
sudo chmod 600 /opt/excel-exporter/custom_templates.json

# Make sure streamlit user owns them
sudo chown streamlit:streamlit /opt/excel-exporter/*.json
```

---

## 📊 Monitoring

### Setup Log Monitoring
```bash
# Monitor service in real-time
sudo journalctl -u excel-exporter -f

# Check for errors
sudo journalctl -u excel-exporter -p err -f
```

### Monitor Resource Usage
```bash
# Check process resources
ps aux | grep streamlit

# Monitor with top
top -p $(pgrep -f "streamlit run")

# Or use systemctl status
sudo systemctl status excel-exporter
```

### Setup Alerts (Optional)
```bash
# Create monitoring script
cat > /opt/monitor.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet excel-exporter; then
    echo "Service down - attempting restart"
    sudo systemctl restart excel-exporter
    # Send alert email
    echo "Alert: Service restarted" | mail -s "Excel Exporter Alert" admin@example.com
fi
EOF

# Make executable
chmod +x /opt/monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/monitor.sh") | crontab -
```

---

## 🔄 Backup & Restore

### Backup Configuration
```bash
# Backup systemd service
sudo cp /etc/systemd/system/excel-exporter.service /opt/excel-exporter/backup/

# Backup application data
sudo tar -czf /opt/backups/excel-exporter-$(date +%Y%m%d_%H%M%S).tar.gz \
    /opt/excel-exporter

# Setup automated backups
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "$BACKUP_DIR/excel-exporter-$BACKUP_DATE.tar.gz" /opt/excel-exporter
# Keep only last 30 days
find "$BACKUP_DIR" -name "excel-exporter-*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup.sh") | crontab -
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status excel-exporter

# View full error logs
sudo journalctl -u excel-exporter -e

# Check if port is in use
sudo lsof -i :8501

# Check Python installation
python3 --version

# Check dependencies
pip list | grep streamlit
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8501

# Kill process
sudo kill -9 <PID>

# Or change port in service file
```

### Permission Denied
```bash
# Check directory ownership
ls -la /opt/excel-exporter

# Fix ownership
sudo chown -R streamlit:streamlit /opt/excel-exporter

# Check file permissions
ls -la /opt/excel-exporter/*.json

# Fix permissions
sudo chmod 644 /opt/excel-exporter/*.json
```

### High Memory Usage
```bash
# Check current memory limit
systemctl show -p MemoryLimit excel-exporter

# Increase memory limit in service file
MemoryLimit=1G

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart excel-exporter
```

---

## 📈 Performance Tuning

### Streamlit Settings
Edit `excel-exporter.service`:

```ini
ExecStart=/usr/bin/streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --client.maxMessageSize=200 \
    --logger.level=info \
    --server.enableXsrfProtection=true
```

### System Optimization
```bash
# Increase file descriptors
sudo sysctl -w fs.file-max=100000
echo "fs.file-max = 100000" | sudo tee -a /etc/sysctl.conf

# Increase connection backlog
sudo sysctl -w net.core.somaxconn=4096
echo "net.core.somaxconn = 4096" | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

---

## 📝 Example Complete Setup

### Full Installation Script
```bash
#!/bin/bash
set -e

echo "Installing Excel Master Exporter as systemd service..."

# 1. Create user
echo "Creating streamlit user..."
sudo useradd -r -s /bin/bash streamlit 2>/dev/null || true

# 2. Create directories
echo "Creating directories..."
sudo mkdir -p /opt/excel-exporter
sudo mkdir -p /opt/backups

# 3. Copy files
echo "Copying application files..."
sudo cp app.py /opt/excel-exporter/
sudo cp streamlit_service.sh /opt/excel-exporter/
sudo cp *.json /opt/excel-exporter/
sudo cp excel-exporter.service /etc/systemd/system/

# 4. Set permissions
echo "Setting permissions..."
sudo chown -R streamlit:streamlit /opt/excel-exporter
sudo chmod 755 /opt/excel-exporter
sudo chmod +x /opt/excel-exporter/streamlit_service.sh

# 5. Install service
echo "Installing systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable excel-exporter
sudo systemctl start excel-exporter

# 6. Verify
echo "Verifying installation..."
sleep 2
sudo systemctl status excel-exporter

echo "✅ Installation complete!"
echo "Access at: http://localhost:8501"
```

Save as `install.sh` and run:
```bash
chmod +x install.sh
./install.sh
```

---

## ✨ Post-Installation

### Change Default Credentials
Edit `/opt/excel-exporter/app.py`:
```python
ADMIN_USERNAME = "your_username"
ADMIN_PASSWORD = "your_secure_password"
```

Then restart:
```bash
sudo systemctl restart excel-exporter
```

### Configure GitHub Integration
Edit `/opt/excel-exporter/app.py`:
```python
GITHUB_CONFIG = {
    'repo_url': 'https://github.com/your-org/excel-exporter.git',
    'branch': 'main',
    'enabled': True
}
```

### Test Deployment Pipeline
1. Go to Admin & Deploy tab
2. Test "Git Pull + Streamlit Restart"
3. Verify version incremented in UI
4. Check logs: `sudo journalctl -u excel-exporter -f`

---

## 📞 Support

For issues:
1. Check service status: `sudo systemctl status excel-exporter`
2. View logs: `sudo journalctl -u excel-exporter -f`
3. Verify port is open: `sudo lsof -i :8501`
4. Check version: `cat /opt/excel-exporter/version.json`

---

**Installation Guide Complete! 🎉**

*For more information, see VERSION_MANAGEMENT_GUIDE.md*
