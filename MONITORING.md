# MoneySplit Monitoring & Observability Guide

## Overview

MoneySplit includes comprehensive monitoring and observability infrastructure to track application health, performance, and business metrics. The monitoring stack consists of:

- **Prometheus**: Metrics collection and time-series database
- **Grafana**: Visualization and dashboarding
- **Health Checks**: Built-in endpoint health verification
- **Structured Logging**: JSON-formatted application logs

## Health Check Endpoints

### Basic Health Check
```
GET /health
```
Returns the basic health status of the application.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-30T12:00:00Z",
  "version": "1.0.0"
}
```

### Readiness Probe
```
GET /health/ready
```
Checks if the application is ready to accept requests (database connectivity, dependencies).

**Response:**
```json
{
  "ready": true,
  "database": "connected",
  "timestamp": "2024-11-30T12:00:00Z"
}
```

### Liveness Probe
```
GET /health/live
```
Checks if the application process is alive and running.

**Response:**
```json
{
  "live": true,
  "uptime_seconds": 3600,
  "timestamp": "2024-11-30T12:00:00Z"
}
```

## Metrics Endpoint

### Prometheus Metrics
```
GET /metrics
```

Exposes all application metrics in Prometheus text format. This endpoint is scraped by Prometheus server.

**Key Metrics Tracked:**
- `http_requests_total`: Total HTTP requests by endpoint, method, and status
- `http_request_duration_seconds`: Request latency distribution
- `http_requests_error_total`: Error count by endpoint and error type
- `database_operations_total`: Database operation count
- `tax_calculations_total`: Tax calculation operations
- `projects_created_total`: Business metrics

## Setting Up Monitoring

### Local Development (Docker Compose)

Start the complete monitoring stack:

```bash
docker-compose up -d
```

This starts:
- MoneySplit API on `http://localhost:8000`
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3001`
- Frontend on `http://localhost:3000`

### Accessing Prometheus

1. Navigate to http://localhost:9090
2. Use the query interface to explore metrics
3. Example queries:
   ```
   rate(http_requests_total[5m])  # Request rate
   histogram_quantile(0.95, http_request_duration_seconds)  # 95th percentile latency
   http_requests_error_total  # Error count
   ```

### Accessing Grafana

1. Navigate to http://localhost:3001
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin` (or `${GRAFANA_PASSWORD}` if set)
3. Configure Prometheus data source:
   - Go to Configuration → Data Sources
   - Click "Add data source"
   - Select Prometheus
   - Set URL to `http://prometheus:9090`
   - Click "Save & Test"

## Prometheus Configuration

The Prometheus configuration is stored in `monitoring/prometheus.yml` and includes:

- **Scrape interval**: 15 seconds (global default)
- **Job: moneysplit-api**: Scrapes `/metrics` endpoint every 10 seconds
- **Job: prometheus**: Self-monitoring
- **Job: grafana**: Grafana health metrics (30-second interval)

### Environment Variables

Configure monitoring via environment variables:

```bash
# .env file
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_PASSWORD=your_secure_password
```

## Alerting (Future Enhancement)

To set up alerting:

1. Create `monitoring/alert_rules.yml` with alert rules
2. Configure Alertmanager in `prometheus.yml`
3. Example alert rule:
   ```yaml
   groups:
     - name: moneysplit
       rules:
         - alert: HighErrorRate
           expr: rate(http_requests_error_total[5m]) > 0.05
           for: 5m
           annotations:
             summary: "High error rate detected"
   ```

## Logging

### Structured Logging

All application logs are structured in JSON format for easy parsing and analysis.

**Log Levels:**
- INFO: General application events
- WARNING: Potential issues
- ERROR: Error conditions
- DEBUG: Detailed debugging information

### Log Files

Logs are stored in `./logs/app.log` and rotated daily.

### Accessing Logs

Via Docker:
```bash
docker logs moneysplit-api
```

Via file system:
```bash
tail -f logs/app.log | jq .
```

## Performance Metrics

### Request Performance
- Mean latency: Track `http_request_duration_seconds_sum / http_request_duration_seconds_count`
- P95 latency: `histogram_quantile(0.95, http_request_duration_seconds)`
- P99 latency: `histogram_quantile(0.99, http_request_duration_seconds)`

### Error Tracking
- Error rate: `rate(http_requests_error_total[5m]) / rate(http_requests_total[5m])`
- Error types: `http_requests_error_total` by error_type

### Business Metrics
- Tax calculations: `rate(tax_calculations_total[1m])`
- Projects created: `increase(projects_created_total[1d])`
- Database operations: `rate(database_operations_total[5m])`

## Troubleshooting

### Prometheus Not Scraping Metrics

Check:
1. API is running: `curl http://localhost:8000/health`
2. Metrics endpoint is accessible: `curl http://localhost:8000/metrics`
3. Prometheus configuration: Check `monitoring/prometheus.yml`
4. Prometheus logs: `docker logs moneysplit-prometheus`

### Grafana Can't Connect to Prometheus

Ensure:
1. Prometheus is running: `docker ps | grep prometheus`
2. Data source URL is correct: `http://prometheus:9090` (internal Docker network)
3. Grafana logs: `docker logs moneysplit-grafana`

### High Memory Usage

Reduce Prometheus retention:
```yaml
# prometheus.yml
prometheus:
  environment:
    - "--storage.tsdb.retention.time=7d"  # Default is 15 days
```

## Production Deployment

For production:

1. **Secure Grafana**: Change default password
2. **Configure HTTPS**: Use reverse proxy (nginx, Traefik)
3. **Set up backups**: Regular backup of Prometheus TSDB and Grafana dashboards
4. **Configure retention**: Adjust `--storage.tsdb.retention.time` based on disk space
5. **Enable authentication**: Use OAuth2/LDAP for Grafana
6. **Set up alerting**: Configure Alertmanager with notification channels
7. **Monitor monitoring**: Ensure Prometheus itself is healthy

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Client Libraries](https://prometheus.io/docs/instrumenting/clientlibs/)
- [Best Practices](https://prometheus.io/docs/practices/naming/)

---

Last updated: 2024-11-30
