# Reliability - Non-Functional Requirements

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Availability Targets

| Metric | Target | Budget |
|--------|--------|--------|
| **Annual Uptime** | 99.9% | 8.76 hours downtime/year |
| **Monthly Uptime** | 99.9% | 43 minutes downtime/month |
| **Weekly Uptime** | 99.9% | 10 minutes downtime/week |
| **Daily Uptime** | 99.9% | 1.44 minutes downtime/day |

---

## 2. Recovery Objectives

### 2.1 RTO & RPO Targets

| Scenario | RTO | RPO | Mechanism |
|----------|-----|-----|-----------|
| **App Instance Failure** | < 30 seconds | Real-time | Auto-restart via Kubernetes |
| **Single Pod Failure** | < 2 minutes | Real-time | Auto-replacement via HPA |
| **Database Primary Failure** | < 5 minutes | < 1 minute | Hot standby automatic failover |
| **Regional Outage** | < 15 minutes | < 5 minutes | Cross-region failover |
| **Complete Data Loss** | < 1 hour | < 1 hour | Backup restoration |

### 2.2 Database Replication Strategy

```
Primary Database (Write)
    │
    ├── Synchronous Replication → Hot Standby
    │   (Immediate failover on primary failure)
    │
    └── Asynchronous Replication → Read Replica 1
        Asynchronous Replication → Read Replica 2
        (For reporting and analytics)
```

---

## 3. Failure Modes & Mitigation

### 3.1 Failure Mode Analysis (FMEA)

| Failure Mode | Probability | Impact | Mitigation |
|--------------|-------------|--------|-----------|
| **App server crash** | Medium | High | Auto-restart, multiple replicas |
| **Database unavailable** | Low | Critical | Hot standby, automatic failover |
| **Network partition** | Low | High | Circuit breaker, graceful degradation |
| **Cache failure** | Low | Medium | Automatic bypass to DB |
| **Message queue failure** | Low | Medium | In-memory queue fallback |
| **SMS carrier outage** | Medium | Medium | Queue buffering, retry logic |
| **Banking API unavailable** | Low | Critical | Scheduled retry, daily reconciliation |

### 3.2 Circuit Breaker Pattern

```csharp
// Protects against cascading failures
var circuitBreakerPolicy = Policy
    .Handle<HttpRequestException>()
    .Or<TimeoutException>()
    .OrResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
    .CircuitBreakerAsync(
        handledEventsAllowedBeforeBreaking: 5,
        durationOfBreak: TimeSpan.FromSeconds(60),
        onBreak: (outcome, duration) =>
        {
            _logger.LogError(
                "Circuit breaker opened for {Duration}s",
                duration.TotalSeconds
            );
            _metrics.CircuitBreakerTriggered("BankingAPI");
        },
        onReset: () =>
        {
            _logger.LogInformation("Circuit breaker reset");
        }
    );
```

### 3.3 Bulkhead Isolation

```
Each service runs in isolated container with:
- Memory limits: Prevent memory exhaustion cascading
- CPU limits: Prevent resource starvation
- Connection pool limits: Prevent connection exhaustion
- Timeout enforcement: Prevent hanging requests

Example: If SMS service fails, balance verification continues
```

---

## 4. Redundancy Strategy

### 4.1 Multi-Instance Redundancy

```
┌──────────────────────────────────────────────┐
│ Kubernetes Cluster with Multiple Nodes       │
├──────────────────────────────────────────────┤
│ ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│ │ Node 1  │  │ Node 2  │  │ Node 3  │       │
│ │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │       │
│ │ │App-1│ │  │ │App-2│ │  │ │App-3│ │       │
│ │ └─────┘ │  │ └─────┘ │  │ └─────┘ │       │
│ └─────────┘  └─────────┘  └─────────┘       │
│      ↓              ↓             ↓          │
│  ┌─────────────────────────────────────┐    │
│  │ Database Cluster                    │    │
│  │ Primary + 2 Hot Standbys            │    │
│  └─────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 4.2 Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: notification-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: notification-service
```

**Impact:**
- Ensures at least 2 replicas running during node drains
- Prevents complete service outage during maintenance
- Allows graceful rolling updates

---

## 5. Health Check Strategy

### 5.1 Liveness Probes

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Endpoint Response:**

```json
{
  "status": "UP",
  "timestamp": "2025-11-18T15:30:00Z"
}
```

### 5.2 Readiness Probes

```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 80
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Checks:**
- Database connectivity
- Cache connectivity
- Message queue connectivity
- External API availability

### 5.3 Startup Probes

```yaml
startupProbe:
  httpGet:
    path: /health/startup
    port: 80
  failureThreshold: 30
  periodSeconds: 10
```

---

## 6. Disaster Recovery Procedures

### 6.1 Database Restoration

**Procedure:**

```
1. Detect: Primary database unrecoverable
2. Verify: Check hot standby health
3. Failover: Promote hot standby to primary
4. Update: Update connection strings via DNS/config
5. Notify: Alert all teams
6. Validate: Run smoke tests
7. Cleanup: Remove failed primary from cluster
8. Recovery: Restore failed primary from backup
9. Reinstate: Add recovered node as hot standby
```

**Estimated Time:** 5-10 minutes

### 6.2 Data Restoration from Backup

**Backup Strategy:**

```
Daily full backup at 02:00 AM (UTC+2)
Point-in-time recovery enabled (24-hour window)
Weekly archive backup (30-day retention)
Monthly long-term backup (1-year retention)
```

**Recovery Steps:**

```
1. Identify restoration point (specific timestamp)
2. Stop applications (prevent further writes)
3. Restore database from backup
4. Validate data integrity
5. Restart applications
6. Verify critical operations
```

**Estimated Time:** 1-2 hours

---

## 7. Monitoring & Alerting

### 7.1 Reliability Metrics

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| **Service Availability** | < 99.5% | Critical alert, page on-call |
| **Database Replication Lag** | > 5 minutes | Warning, investigate |
| **Failed Balance Checks** | > 1% | Warning, check banking API |
| **SMS Delivery Failure** | > 5% | Warning, check carrier |
| **Unhandled Exceptions** | > 10/min | Critical alert |
| **Circuit Breaker Trips** | Any | Warning, investigate cause |

### 7.2 SLO Tracking

```sql
-- Calculate daily availability
SELECT 
    DATE(event_timestamp) AS date,
    COUNT(*) FILTER (WHERE status = 'success') AS successful_requests,
    COUNT(*) AS total_requests,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'success') 
        / COUNT(*), 4) AS availability_percentage
FROM request_log
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY DATE(event_timestamp)
ORDER BY date DESC;

-- Alert if availability < 99.9%
```

---

## 8. Testing & Validation

### 8.1 Chaos Engineering

**Regular Tests:**

```
Weekly: Pod failure injection
Monthly: Network partition simulation
Quarterly: Database failover test
Bi-annually: Full disaster recovery drill
```

### 8.2 Load Testing

```
Target: 2x projected peak load
Duration: 1 hour sustained
Ramp-up: Gradual over 10 minutes
Scenarios:
- Normal operation
- 50% peak load
- Peak load (2x)
- Degraded (one instance down)
```

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
