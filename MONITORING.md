# Monitoring Guide for MoneySplit

Complete monitoring and observability documentation.

---

## Table of Contents

1. [Health Checks](#health-checks)
2. [Prometheus Metrics](#prometheus-metrics)
3. [Grafana Dashboards](#grafana-dashboards)
4. [Logging](#logging)
5. [Alerting](#alerting)
6. [Troubleshooting](#troubleshooting)

---

## Health Checks

### Three-Tier Health System

**1. Liveness Probe (`/health`)**
- Indicates if service is running
- Lightweight check (no dependencies)
- Returns immediately

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T10:30:00.000000",
  "uptime_seconds": 3600.5,
  "version": "1.0.0"
}
```

**2. Readiness Probe (`/health/ready`)**
- Indicates if service can accept traffic
- Checks database connectivity
- May return "not_ready" during startup

```bash
curl http://localhost:8000/health/ready
```

Response:
```json
{
  "status": "ready",
  "timestamp": "2025-11-30T10:30:00.000000",
  "uptime_seconds": 3600.5,
  "database": {
    "status": "healthy",
    "records_count": 150,
    "people_count": 300
  },
  "system": {
    "cpu_percent": 45.2,
    "memory_mb": 256.8,
    "memory_percent": 25.4,
    "open_files": 12,
    "threads": 8
  }
}
```

**3. Detailed Status (`/health/detailed`)**
- Comprehensive system information
- Full diagnostics
- For debugging and monitoring dashboards

```bash
curl http://localhost:8000/health/detailed
```

Response:
```json
{
  "timestamp": "2025-11-30T10:30:00.000000",
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "database": {...},
  "system": {
    "cpu_percent": 45.2,
    "cpu_status": "ok",
    "memory_mb": 256.8,
    "memory_percent": 25.4,
    "memory_status": "ok",
    "open_files": 12,
    "threads": 8
  },
  "version": "1.0.0",
  "environment": "production"
}
```

### Docker Health Checks

All containers configured with health checks:

```bash
# View health status
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Check specific container
docker inspect --format='{{json .State.Health}}' moneysplit-api | jq

# Manual health check in container
docker exec moneysplit-api curl http://localhost:8000/health
```

---

## Prometheus Metrics

### Metric Types

**Counters** (always increasing):
- `moneysplit_requests_total` - Total requests
- `moneysplit_errors_total` - Total errors
- `moneysplit_projects_created_total` - Projects created
- `moneysplit_tax_calculations_total` - Tax calculations

**Histograms** (latency distribution):
- `moneysplit_request_duration_seconds` - Request latency
- `moneysplit_request_size_bytes` - Request size
- `moneysplit_response_size_bytes` - Response size
- `moneysplit_db_query_duration_seconds` - Database latency

**Gauges** (point-in-time value):
- `moneysplit_active_requests` - Active requests now
- `moneysplit_db_records_total` - Total records
- `moneysplit_db_people_total` - Total people

### Accessing Metrics

```bash
# Raw metrics endpoint
curl http://localhost:8000/metrics

# Specific metric
curl http://localhost:8000/metrics | grep moneysplit_requests_total

# Text format
curl --header "Accept: text/plain" http://localhost:8000/metrics
```

### Useful Prometheus Queries

```promql
# Request rate (requests per second)
rate(moneysplit_requests_total[5m])

# Error rate
rate(moneysplit_errors_total[5m])

# 95th percentile latency
histogram_quantile(0.95, moneysplit_request_duration_seconds)

# Average latency
rate(moneysplit_request_duration_seconds_sum[5m]) / rate(moneysplit_request_duration_seconds_count[5m])

# Database query latency
histogram_quantile(0.95, moneysplit_db_query_duration_seconds)

# Active requests
moneysplit_active_requests

# Projects created rate
rate(moneysplit_projects_created_total[1h])

# Error count by type
moneysplit_errors_total{type=~".*"}
```

### Metric Labels

Labels allow filtering and aggregation:

```
moneysplit_requests_total{method="POST", endpoint="/api/projects", status="201"}
moneysplit_request_duration_seconds{method="GET", endpoint="/api/records"}
moneysplit_errors_total{type="ValidationError", endpoint="/api/projects"}
moneysplit_tax_calculations_total{country="US", tax_type="Individual"}
moneysplit_db_query_duration_seconds{operation="select"}
```

---

## Grafana Dashboards

### Access Grafana

```bash
# URL
http://localhost:3001

# Default credentials
Username: admin
Password: admin
```

### Adding Prometheus Datasource

1. Settings → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. URL: http://prometheus:9090
5. Click "Save & Test"

### Creating Dashboards

**Sample Dashboard Panels:**

1. **Request Rate**
   ```promql
   rate(moneysplit_requests_total[5m])
   ```
   - Type: Graph
   - Legend: {{method}} {{endpoint}}

2. **Error Rate**
   ```promql
   rate(moneysplit_errors_total[5m])
   ```
   - Type: Graph
   - Legend: {{type}}

3. **Latency (p95)**
   ```promql
   histogram_quantile(0.95, moneysplit_request_duration_seconds)
   ```
   - Type: Gauge
   - Units: seconds

4. **Database Performance**
   ```promql
   histogram_quantile(0.95, moneysplit_db_query_duration_seconds)
   ```
   - Type: Graph
   - Legend: {{operation}}

5. **System Resources**
   ```promql
   moneysplit_active_requests
   ```
   - Type: Gauge

### Dashboard Templates

Example dashboard JSON available in monitoring/grafana-dashboard.json

---

## Logging

### Log Format

Logs are JSON formatted for easy parsing:

```json
{
  "timestamp": "2025-11-30T10:30:00.123456",
  "level": "INFO",
  "logger": "api.main",
  "message": "Request completed",
  "module": "main",
  "function": "create_project",
  "line": 52,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General information about application state
- **WARNING** - Warning messages for potential issues
- **ERROR** - Error messages for failed operations
- **CRITICAL** - Critical errors affecting application

### Configuring Logging

**In config.py:**
```python
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"
```

**In .env:**
```bash
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

### Viewing Logs

```bash
# Real-time logs
docker logs -f moneysplit-api

# Last N lines
docker logs --tail 100 moneysplit-api

# Since timestamp
docker logs --since 2025-11-30T10:00:00 moneysplit-api

# Until timestamp
docker logs --until 2025-11-30T11:00:00 moneysplit-api

# With timestamps
docker logs -t moneysplit-api

# Combined
docker logs -f -t --tail 50 moneysplit-api
```

### Log Aggregation

For production, aggregate logs to centralized system:

**ELK Stack (Elasticsearch, Logstash, Kibana):**
```yaml
# logstash.conf
input {
  http {
    port => 8080
  }
}

filter {
  json { source => "message" }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
  }
}
```

**Splunk:**
- Stream logs to Splunk HTTP Event Collector
- Search and analyze in Splunk UI

---

## Alerting

### Prometheus Alert Rules

Create `monitoring/alert-rules.yml`:

```yaml
groups:
- name: moneysplit
  interval: 1m
  rules:
  - alert: HighErrorRate
    expr: rate(moneysplit_errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }}"

  - alert: HighLatency
    expr: histogram_quantile(0.95, moneysplit_request_duration_seconds) > 1
    for: 5m
    annotations:
      summary: "High latency detected"
      description: "p95 latency is {{ $value }}s"

  - alert: DatabaseDown
    expr: moneysplit_db_records_total == 0
    for: 1m
    annotations:
      summary: "Database is down"

  - alert: HighMemoryUsage
    expr: moneysplit_active_requests > 100
    for: 5m
    annotations:
      summary: "High number of active requests"
```

### Alertmanager Configuration

Create `monitoring/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'team-email'
  repeat_interval: 4h

receivers:
- name: 'team-email'
  email_configs:
  - to: 'team@example.com'
    from: 'alerts@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'user'
    auth_password: 'password'
```

---

## Monitoring Checklist

### Daily
- [ ] Check health endpoint responses
- [ ] Monitor error rates
- [ ] Review application logs

### Weekly
- [ ] Analyze Grafana dashboards
- [ ] Check storage usage
- [ ] Review database performance

### Monthly
- [ ] Analyze trends
- [ ] Optimize slow queries
- [ ] Update thresholds
- [ ] Review backups

---

## Troubleshooting

### Prometheus Issues

```bash
# Check Prometheus UI
curl http://localhost:9090

# Verify target status
curl http://localhost:9090/api/v1/targets

# Test query
curl http://localhost:9090/api/v1/query?query=up
```

### Metrics Not Appearing

1. Verify endpoint is accessible:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. Check Prometheus configuration:
   ```bash
   cat monitoring/prometheus.yml
   ```

3. Check scrape logs:
   ```bash
   docker logs prometheus
   ```

### High Memory Usage

```bash
# Monitor memory in real-time
docker stats moneysplit-api

# Check memory limit
docker inspect moneysplit-api | grep Memory

# Increase limit if needed
docker update --memory 2g moneysplit-api
```

### Database Connection Issues

```bash
# Test database connection
curl http://localhost:8000/health/ready

# Check database file
ls -la data/example.db

# Verify permissions
chmod 644 data/example.db
```

---

## Performance Baselines

Typical metrics for healthy system:

| Metric | Expected | Alert Threshold |
|--------|----------|---|
| Error Rate | < 1% | > 5% |
| Latency p95 | < 500ms | > 2s |
| Database Query | < 100ms | > 500ms |
| Active Requests | < 50 | > 200 |
| Memory Usage | 25-50% | > 80% |
| CPU Usage | 20-40% | > 80% |

---

**Last Updated:** 2025-11-30
**Status:** Monitoring Stack Ready
