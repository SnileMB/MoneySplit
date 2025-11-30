# MoneySplit - Heroku Deployment Guide

## Prerequisites

1. Heroku account (https://www.heroku.com)
2. Heroku CLI installed (https://devcenter.heroku.com/articles/heroku-cli)
3. Git repository initialized

## Quick Start

### 1. Login to Heroku
```bash
heroku login
```

### 2. Create Heroku App
```bash
heroku create moneysplit-app
```

Or if you want a specific app name:
```bash
heroku create my-moneysplit-app
```

### 3. Deploy to Heroku
```bash
git push heroku main
```

### 4. View Logs
```bash
heroku logs --tail
```

### 5. Access Application
```bash
heroku open
```

Your app will be available at: `https://my-moneysplit-app.herokuapp.com`

## Configuration

### Set Environment Variables
```bash
heroku config:set API_DEBUG=false
heroku config:set API_HOST=0.0.0.0
```

### View Configuration
```bash
heroku config
```

## Database Setup

### Initialize Database on First Deploy
```bash
heroku run python DB/setup.py
```

### Reset Database
```bash
heroku run python DB/reset.py
```

## Monitoring

### View Application Logs
```bash
# Last 100 lines
heroku logs

# Real-time logs
heroku logs --tail

# Filter by process type
heroku logs --dyno=web
```

### Check Application Status
```bash
heroku ps
```

### View Metrics
```bash
# Response time
heroku metrics

# Dyno type and status
heroku ps --verbose
```

## Scaling

### Scale Web Dyno
```bash
# Standard-1x dyno (recommended for production)
heroku dyno:type standard-1x -a my-moneysplit-app

# Standard-2x dyno (for higher traffic)
heroku dyno:type standard-2x -a my-moneysplit-app

# Check current dyno type
heroku ps --verbose
```

## Production Recommendations

### 1. Use PostgreSQL Database
```bash
# Add PostgreSQL add-on
heroku addons:create heroku-postgresql:standard-0

# Your app will be updated with DATABASE_URL env var
# Modify DB setup to use PostgreSQL if needed
```

### 2. Enable SSL/TLS
```bash
heroku certs:auto:enable
```

### 3. Set Up Custom Domain
```bash
heroku domains:add www.moneysplit.com
heroku domains:add moneysplit.com
```

### 4. Monitor with Alerts
```bash
heroku addons:create papertrail:choklad  # Logging
heroku addons:create heroku-datadog:free  # Monitoring
```

### 5. Schedule Maintenance
```bash
# Run database setup at midnight UTC daily
heroku addons:create scheduler:standard
```

## Troubleshooting

### App Won't Start
1. Check logs: `heroku logs --tail`
2. Ensure Procfile is correct
3. Verify requirements.txt has all dependencies

### Database Connection Issues
1. Run migrations: `heroku run python DB/setup.py`
2. Check DATABASE_URL: `heroku config | grep DATABASE_URL`

### 503 Service Unavailable
1. Check if dyno is running: `heroku ps`
2. Restart dyno: `heroku restart`
3. Check logs for errors: `heroku logs --tail`

### Slow Performance
1. Check dyno metrics: `heroku metrics`
2. Scale to larger dyno: `heroku dyno:type standard-1x`
3. Check database queries in logs

## Removing Application

To delete the Heroku app:
```bash
heroku apps:destroy --app my-moneysplit-app --confirm my-moneysplit-app
```

## Resources

- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Procfile Documentation](https://devcenter.heroku.com/articles/procfile)
- [Heroku Environment Variables](https://devcenter.heroku.com/articles/config-vars)
- [PostgreSQL on Heroku](https://devcenter.heroku.com/articles/heroku-postgresql)

---

**Last Updated:** 2025-11-30
