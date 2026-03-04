# Ubuntu Deployment Guide for KenGen Tender Tracking System

This guide covers deploying the Django application on Ubuntu using Nginx and Gunicorn with systemd.

## Prerequisites

- Ubuntu 20.04 or later
- PostgreSQL installed and configured
- Python 3.8 or later
- Root or sudo access

## Step 1: System Update and Dependencies

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib -y
```

## Step 2: Create Application Directory

```bash
sudo mkdir -p /home/bernard/projects/KenGen-Tender-Tracking-System
sudo chown -R bernard:bernard /home/bernard/projects/KenGen-Tender-Tracking-System
```

## Step 3: Upload Your Application

Transfer your application files to the server:

```bash
# From your local machine (in the project directory)
scp -r * bernard@your-server-ip:/home/bernard/projects/KenGen-Tender-Tracking-System/

# OR use rsync
rsync -avz --exclude='env' --exclude='__pycache__' --exclude='*.pyc' \
    ./ bernard@your-server-ip:/home/bernard/projects/KenGen-Tender-Tracking-System/
```

## Step 4: Set Up Python Virtual Environment

```bash
cd /home/bernard/projects/KenGen-Tender-Tracking-System
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Add gunicorn for production
```

## Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
nano /home/bernard/projects/KenGen-Tender-Tracking-System/.env
```

Add the following (adjust values as needed):

```env
SECRET_KEY=your-very-secure-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip

# Database settings
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432
```

## Step 6: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, create database and user
CREATE DATABASE tenders;
CREATE USER tendersuser WITH PASSWORD 'your-secure-password';
ALTER ROLE tendersuser SET client_encoding TO 'utf8';
ALTER ROLE tendersuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE tendersuser SET timezone TO 'Africa/Nairobi';
GRANT ALL PRIVILEGES ON DATABASE tenders TO tendersuser;
\q
```

Update `.env` file with database credentials:

```env
DB_USER=tendersuser
DB_PASSWORD=your-secure-password
```

## Step 7: Run Django Migrations and Collect Static Files

```bash
cd /home/bernard/projects/KenGen-Tender-Tracking-System
source env/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Step 8: Create Log Directory

```bash
sudo mkdir -p /var/log/tendertracking
sudo chown -R bernard:bernard /var/log/tendertracking
```

## Step 9: Set Up Systemd Service

Copy the service file:

```bash
sudo cp /home/bernard/projects/KenGen-Tender-Tracking-System/tendertracking.service /etc/systemd/system/
```

Update permissions:

```bash
sudo chown -R bernard:bernard /home/bernard/projects/KenGen-Tender-Tracking-System
sudo chmod -R 755 /home/bernard/projects/KenGen-Tender-Tracking-System
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tendertracking

# Start the service
sudo systemctl start tendertracking

# Check status
sudo systemctl status tendertracking
```

## Step 10: Configure Nginx

Copy the Nginx configuration:

```bash
sudo cp /home/bernard/projects/KenGen-Tender-Tracking-System/nginx.conf /etc/nginx/sites-available/tendertracking
```

Edit the configuration file to update your domain:

```bash
sudo nano /etc/nginx/sites-available/tendertracking
# Replace 'your-domain.com' with your actual domain or server IP
```

Enable the site:

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/tendertracking /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 11: Configure Firewall

```bash
# Allow Nginx
sudo ufw allow 'Nginx Full'

# Allow SSH (if not already allowed)
sudo ufw allow OpenSSH

# Enable firewall
sudo ufw enable
```

## Step 12: Optional - Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## Useful Commands

### Check Service Status
```bash
sudo systemctl status tendertracking
```

### View Service Logs
```bash
# View systemd logs
sudo journalctl -u tendertracking -f

# View Gunicorn logs
sudo tail -f /var/log/tendertracking/error.log
sudo tail -f /var/log/tendertracking/access.log

# View Nginx logs
sudo tail -f /var/log/nginx/tendertracking_error.log
sudo tail -f /var/log/nginx/tendertracking_access.log
```

### Restart Services
```bash
# Restart application
sudo systemctl restart tendertracking

# Restart Nginx
sudo systemctl restart nginx
```

### Update Application
```bash
cd /home/bernard/projects/KenGen-Tender-Tracking-System
source env/bin/activate

# Pull latest changes (if using git)
git pull

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart tendertracking
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u tendertracking -n 50 --no-pager

# Check if socket file exists
ls -l /home/bernard/projects/KenGen-Tender-Tracking-System/tendertracking.sock

# Check permissions
ls -la /home/bernard/projects/KenGen-Tender-Tracking-System
```

### Static files not loading
```bash
# Ensure collectstatic was run
python manage.py collectstatic --noinput

# Check Nginx static file path in config
sudo nano /etc/nginx/sites-available/tendertracking

# Restart Nginx
sudo systemctl restart nginx
```

### Database connection errors
```bash
# Test database connection
sudo -u postgres psql -d tenders

# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify .env file settings
cat /home/bernard/projects/KenGen-Tender-Tracking-System/.env
```

## Security Recommendations

1. **Keep DEBUG=False in production**
2. **Use strong SECRET_KEY** (generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
3. **Regularly update packages**: `sudo apt update && sudo apt upgrade`
4. **Set up automatic backups** for database and media files
5. **Enable SSL/HTTPS** with Let's Encrypt
6. **Restrict database access** to localhost only
7. **Set up monitoring** (e.g., UptimeRobot, Prometheus)
8. **Regular security audits** and log monitoring

## Backup Strategy

### Database Backup
```bash
# Create backup directory
sudo mkdir -p /var/backups/tendertracking

# Backup database
sudo -u postgres pg_dump tenders > /var/backups/tendertracking/tenders_$(date +%Y%m%d_%H%M%S).sql

# Restore database
sudo -u postgres psql tenders < /var/backups/tendertracking/backup_file.sql
```

### Application Backup
```bash
# Backup entire application directory
sudo tar -czf /var/backups/tendertracking/app_$(date +%Y%m%d_%H%M%S).tar.gz /home/bernard/projects/KenGen-Tender-Tracking-System
```

### Automated Daily Backups (Cron)
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * sudo -u postgres pg_dump tenders > /var/backups/tendertracking/tenders_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

## Performance Optimization

1. **Increase Gunicorn workers** based on CPU cores: `workers = 2 * CPU_cores + 1`
2. **Enable Nginx caching** for static assets
3. **Set up database connection pooling**
4. **Use Redis for caching** (optional)
5. **Enable gzip compression** in Nginx

Your application should now be accessible at `http://your-domain.com` or `http://your-server-ip`
