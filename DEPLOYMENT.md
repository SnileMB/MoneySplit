# Deployment Guide for MoneySplit

Complete deployment documentation for production and cloud environments.

---

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment (Azure)](#cloud-deployment-azure)
4. [Health Checks](#health-checks)
5. [Scaling](#scaling)
6. [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Development Environment

```bash
# Clone and setup
git clone <repository>
cd MoneySplit

# Backend setup
pip install -r requirements.txt
python3 -m uvicorn api.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### Access URLs

- API: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Docker Deployment

### Building Images

**Backend:**
```bash
docker build -t moneysplit:latest .
docker run -p 8000:8000 moneysplit:latest
```

**Frontend:**
```bash
docker build -f Dockerfile.frontend -t moneysplit-frontend:latest .
docker run -p 80:80 moneysplit-frontend:latest
```

### Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

Create `.env` file:
```bash
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
DB_PATH=/app/data/example.db
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Volumes & Data Persistence

```yaml
# docker-compose.yml volumes
volumes:
  - ./data:/app/data           # Database persistence
  - ./logs:/app/logs           # Log persistence
  - prometheus-data:/prometheus
  - grafana-data:/var/lib/grafana
```

---

## Cloud Deployment (Azure)

### Prerequisites

- Azure subscription
- Azure CLI installed
- GitHub secrets configured:
  - `AZURE_CREDENTIALS_FOR_GITHUB_ACTIONS`
  - `SERVICE_PRINCIPALS_CREDENTIALS`

### Azure Container Registry

```bash
# Create container registry
az acr create --resource-group mygroup --name moneysplit --sku Basic

# Login
az acr login --name moneysplit

# Build and push
docker build -t moneysplit:latest .
docker tag moneysplit:latest moneysplit.azurecr.io/moneysplit:latest
docker push moneysplit.azurecr.io/moneysplit:latest
```

### Azure Container Instances

```bash
# Deploy container
az container create \
  --resource-group mygroup \
  --name moneysplit \
  --image moneysplit.azurecr.io/moneysplit:latest \
  --registry-login-server moneysplit.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --ports 8000 \
  --memory 1 \
  --cpu 1
```

### Azure App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name moneysplit-plan \
  --resource-group mygroup \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group mygroup \
  --plan moneysplit-plan \
  --name moneysplit-app \
  --deployment-container-image-name moneysplit.azurecr.io/moneysplit:latest

# Configure for Docker
az webapp config container set \
  --name moneysplit-app \
  --resource-group mygroup \
  --docker-custom-image-name moneysplit.azurecr.io/moneysplit:latest \
  --docker-registry-server-url https://moneysplit.azurecr.io
```

### GitHub Actions Deployment

The CI/CD pipeline can automatically deploy to Azure:

```yaml
# .github/workflows/deploy.yml (to be created)
- name: Deploy to Azure
  uses: azure/webapps-deploy@v2
  with:
    app-name: moneysplit-app
    images: ${{ secrets.REGISTRY }}/moneysplit:${{ github.sha }}
    registries: |
      username=${{ secrets.REGISTRY_USERNAME }}
      password=${{ secrets.REGISTRY_PASSWORD }}
```

---

## Health Checks

### Basic Health Check

```bash
curl http://localhost:8000/health
# Response:
# {
#   "status": "healthy",
#   "uptime_seconds": 3600,
#   "version": "1.0.0"
# }
```

### Readiness Check

```bash
curl http://localhost:8000/health/ready
# Checks: Database connectivity, system resources
```

### Detailed Status

```bash
curl http://localhost:8000/health/detailed
# Includes: Full system info, metrics, environment
```

### Docker Health Checks

All containers have health checks:

```bash
# Check specific container
docker inspect --format='{{.State.Health}}' moneysplit-api

# View health status
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

**Docker Swarm:**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml moneysplit

# Scale service
docker service scale moneysplit_api=3
```

**Kubernetes:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: moneysplit
spec:
  replicas: 3
  selector:
    matchLabels:
      app: moneysplit
  template:
    metadata:
      labels:
        app: moneysplit
    spec:
      containers:
      - name: api
        image: moneysplit:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
```

### Vertical Scaling (More Resources)

```bash
# Increase container memory
docker update --memory 2g moneysplit-api

# Increase CPU limit
docker update --cpus 2 moneysplit-api
```

---

## Monitoring & Logging

### Prometheus Metrics

```bash
# Access metrics
curl http://localhost:8000/metrics

# Useful queries:
# Request rate: rate(moneysplit_requests_total[5m])
# Error rate: rate(moneysplit_errors_total[5m])
# Latency: histogram_quantile(0.95, moneysplit_request_duration_seconds)
```

### Grafana Dashboard

1. Open http://localhost:3001
2. Login with admin/admin
3. Add Prometheus datasource: http://prometheus:9090
4. Create dashboards from metrics

### Log Analysis

```bash
# View container logs
docker logs moneysplit-api

# Follow logs
docker logs -f moneysplit-api

# Last 100 lines
docker logs --tail 100 moneysplit-api

# Timestamp format
docker logs -t moneysplit-api

# Since/until timestamps
docker logs --since 2025-11-30T10:00:00 moneysplit-api
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
cp data/example.db data/example.db.backup

# Restore from backup
cp data/example.db.backup data/example.db
```

### Volume Backup

```bash
# Backup volumes
docker run --rm \
  -v moneysplit_db:/source \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/db-backup.tar.gz -C /source .

# Restore volumes
docker run --rm \
  -v moneysplit_db:/target \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/db-backup.tar.gz -C /target
```

---

## Performance Tuning

### API Optimization

```python
# In config.py
# Increase connection pool size
DB_TIMEOUT = 10  # Increase timeout

# Enable caching
CACHE_TTL = 300  # 5 minutes

# Optimize logging
LOG_LEVEL = "WARNING"  # Less verbose in production
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_record_created ON tax_records(created_at);
CREATE INDEX idx_person_record ON people(record_id);
```

### Frontend Optimization

```bash
# Build production bundle
cd frontend
npm run build

# Optimize bundle
npm install --save-dev webpack-bundle-analyzer
```

---

## Security Checklist

- [ ] Environment variables set (no hardcoded secrets)
- [ ] API running with HTTPS in production
- [ ] Database backups enabled
- [ ] Health checks configured
- [ ] Monitoring alerts enabled
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Secrets rotated regularly
- [ ] Docker images scanned for vulnerabilities
- [ ] Logs aggregated and retained

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs moneysplit-api

# Inspect container
docker inspect moneysplit-api

# Remove and rebuild
docker rm moneysplit-api
docker build -t moneysplit:latest .
docker run -p 8000:8000 moneysplit:latest
```

### Database Connection Issues

```bash
# Check database file
ls -la data/example.db

# Verify permissions
chmod 644 data/example.db

# Reset database
rm data/example.db
python3 -m MoneySplit  # Recreates database
```

### Health Check Failing

```bash
# Test endpoint manually
curl -v http://localhost:8000/health

# Check logs for errors
docker logs moneysplit-api | grep -i health

# Verify database is accessible
sqlite3 data/example.db ".tables"
```

---

## Deployment Checklist

- [ ] Code reviewed and merged
- [ ] Tests passing (70%+ coverage)
- [ ] CI/CD pipeline successful
- [ ] Docker images built
- [ ] Environment variables configured
- [ ] Backups created
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Documentation updated
- [ ] Team notified

---

**Last Updated:** 2025-11-30
**Status:** Ready for Production
