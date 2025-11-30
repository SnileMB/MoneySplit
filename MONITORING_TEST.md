# Testing Prometheus & Grafana Monitoring

## Quick Start

### 1. Start the Full Stack

```bash
docker-compose up -d
```

This starts:
- **API** on http://localhost:8000
- **Frontend** on http://localhost:3000
- **Prometheus** on http://localhost:9090
- **Grafana** on http://localhost:3001

### 2. Verify Services are Running

```bash
docker-compose ps
```

All services should show status: `Up (healthy)`

### 3. Access Monitoring Tools

#### Prometheus
- **URL:** http://localhost:9090
- **Targets:** http://localhost:9090/targets (shows scraping status)
- **Metrics:** http://localhost:9090/graph (query metrics)

**Example Queries:**
```
# Request count
http_requests_total

# Request duration
http_request_duration_seconds

# Active requests
http_requests_in_progress
```

#### Grafana
- **URL:** http://localhost:3001
- **Login:** admin / admin (change on first login)
- **Datasource:** Prometheus (pre-configured)
- **Dashboard:** "MoneySplit Dashboard" (pre-loaded)

### 4. Generate Traffic for Metrics

```bash
# Create some projects to generate metrics
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "num_people": 2,
    "revenue": 100000,
    "costs": [20000],
    "country": "US",
    "tax_type": "Individual",
    "people": [
      {"name": "Alice", "work_share": 0.5},
      {"name": "Bob", "work_share": 0.5}
    ]
  }'

# Fetch records (generates more metrics)
curl http://localhost:8000/api/records

# Check health endpoint
curl http://localhost:8000/health
```

### 5. View Metrics in Prometheus

1. Go to http://localhost:9090/graph
2. Enter query: `http_requests_total`
3. Click "Execute"
4. Switch to "Graph" tab to see visualization

### 6. View Dashboard in Grafana

1. Go to http://localhost:3001
2. Login with admin/admin
3. Navigate to Dashboards → MoneySplit Dashboard
4. You'll see:
   - Request rate
   - Response times
   - Error rates
   - Active requests

## Verification Checklist

- [ ] All containers running and healthy
- [ ] Prometheus targets showing "UP" status
- [ ] Metrics visible at http://localhost:8000/metrics
- [ ] Grafana dashboard loading data
- [ ] Metrics updating after API requests

## Troubleshooting

### API Target Down in Prometheus

If Prometheus shows "api:8000" as down:
```bash
# Restart the API service
docker-compose restart api

# Check API logs
docker-compose logs api
```

### Grafana Can't Connect to Prometheus

```bash
# Restart Grafana
docker-compose restart grafana

# Check if datasource is configured
# Grafana UI → Configuration → Data Sources → Prometheus
```

### No Metrics Showing

1. Verify API is exposing metrics:
   ```bash
   curl http://localhost:8000/metrics
   ```
2. Check Prometheus is scraping:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

## Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v
```

## What's Being Monitored

### Application Metrics (from `/metrics`)
- **http_requests_total** - Total number of HTTP requests
- **http_request_duration_seconds** - Request latency histogram
- **http_requests_in_progress** - Number of requests being processed
- **process_cpu_seconds_total** - CPU usage
- **process_resident_memory_bytes** - Memory usage
- **http_exceptions_total** - Total number of exceptions

### System Metrics (from Prometheus)
- Scrape duration
- Target health
- Time series count

## Dashboard Features

The pre-configured Grafana dashboard shows:
- **Request Rate** - Requests per second over time
- **Error Rate** - HTTP errors (4xx, 5xx) over time
- **Response Time** - P50, P95, P99 latencies
- **Active Requests** - Current requests being processed
- **Top Endpoints** - Most frequently called endpoints
- **Status Code Distribution** - Breakdown of 2xx, 4xx, 5xx responses

## Production Deployment

For production (Heroku), metrics are exposed at:
- **Metrics:** https://your-app.herokuapp.com/metrics
- **Health:** https://your-app.herokuapp.com/health

Note: Prometheus and Grafana are typically not deployed on Heroku free tier.
For production monitoring, consider:
- Grafana Cloud (free tier available)
- Datadog
- New Relic
- Prometheus + Grafana on separate infrastructure
