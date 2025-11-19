# Operational Requirements - Non-Functional Requirements

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Monitoring & Observability

### 1.1 Three Pillars of Observability

**1. Metrics (Prometheus)**

```
System Metrics:
- CPU usage, Memory usage, Disk I/O
- Request count, Response time (latency distribution)
- Error rates, Exception counts
- Business metrics (balance checks, qualifications, SMS sent)
```

**2. Logging (ELK Stack)**

```
Log Types:
- Application logs (INFO, WARNING, ERROR, CRITICAL)
- Request/Response logs (HTTP interactions)
- Audit logs (all data modifications)
- Integration logs (banking API, SMS carrier)
```

**3. Tracing (Jaeger / Application Insights)**

```
Distributed Tracing:
- Request flow across services
- Latency breakdown per service
- Error propagation tracking
- Dependency visualization
```

### 1.2 Monitoring Dashboard

**Real-Time Dashboards (Grafana):**

```
System Health:
├── Service Availability: 99.91%
├── Active Instances: 3/3
├── Error Rate: 0.05%
├── P95 Latency: 245ms
├── Memory Usage: 62%
└── Disk Usage: 45%

Application Metrics:
├── Daily Balance Checks: 100,245/100,000 ✓
├── Qualified Customers: 15,342
├── SMS Sent: 4,821
├── SMS Delivered: 4,754 (98.6%)
└── Avg Delivery Time: 8.3s

External Integration:
├── Banking API: 99.97% availability
├── SMS Carrier: 98.8% delivery rate
└── Message Queue: 2 messages backlog
```

---

## 2. Logging Strategy

### 2.1 Log Levels

| Level | Usage | Examples |
|-------|-------|----------|
| **DEBUG** | Development only | Variable states, method entry/exit |
| **INFO** | Normal operation | Service started, process completed |
| **WARNING** | Potentially harmful | Retry attempt, degraded mode, high latency |
| **ERROR** | Error condition | Failed API call, database error |
| **CRITICAL** | System failure | Service down, complete data loss |

### 2.2 Structured Logging Format

```json
{
  "timestamp": "2025-11-18T15:30:45.123Z",
  "level": "INFO",
  "service": "BalanceMonitoringService",
  "correlationId": "corr-20251118-001",
  "traceId": "trace-20251118-001",
  "userId": "system",
  "operation": "DailyBalanceVerification",
  "message": "Balance verification completed successfully",
  "context": {
    "customersProcessed": 100245,
    "successCount": 100240,
    "failureCount": 5,
    "durationMs": 1842
  },
  "tags": ["daily-job", "balance-monitoring"],
  "environment": "production"
}
```

### 2.3 Log Retention Policy

| Log Type | Retention | Storage | Query |
|----------|-----------|---------|-------|
| **Application Logs** | 30 days (hot), 1 year (cold) | Hot: Elasticsearch, Cold: S3 | Last 30 days |
| **Audit Logs** | 7 years | Database + Archive | Full retention queryable |
| **Integration Logs** | 90 days (hot), 2 years (cold) | Hot: Elasticsearch, Cold: S3 | Last 90 days |
| **System Events** | 1 year | Database | Last 1 year |

---

## 3. Alerting & On-Call

### 3.1 Alert Severity Levels

| Severity | Response Time | Escalation | Example |
|----------|---------------|-----------|---------|
| **P1 - Critical** | Immediate (5 min) | Page on-call engineer | Service completely down |
| **P2 - High** | 15 minutes | Slack notification + email | 50% error rate, >1s latency |
| **P3 - Medium** | 1 hour | Slack notification | 10% error rate, degraded performance |
| **P4 - Low** | Next business day | Ticket created | Minor issues, informational |

### 3.2 Alert Rules

```yaml
# Critical Alerts
- alert: ServiceUnavailable
  expr: up{job="notification-service"} == 0
  for: 2m
  annotations:
    severity: critical
    description: "Notification Service is down"
    runbook: "https://wiki/runbooks/service-down"

- alert: DatabaseDown
  expr: pg_up{job="postgres"} == 0
  for: 1m
  annotations:
    severity: critical
    description: "PostgreSQL database is unavailable"

- alert: HighErrorRate
  expr: rate(errors_total[5m]) > 0.05
  for: 5m
  annotations:
    severity: high
    description: "Error rate is above 5%"

- alert: HighLatency
  expr: histogram_quantile(0.95, rate(request_duration_seconds_bucket[5m])) > 1
  for: 10m
  annotations:
    severity: high
    description: "P95 latency is above 1 second"

# Medium Alerts
- alert: CacheHitRateLow
  expr: cache_hit_ratio < 0.70
  for: 15m
  annotations:
    severity: medium
    description: "Cache hit rate is below 70%"

- alert: QueueDepthHigh
  expr: rabbitmq_queue_messages_ready > 5000
  for: 10m
  annotations:
    severity: medium
    description: "Message queue has > 5000 pending messages"
```

### 3.3 On-Call Escalation

```
Primary Engineer (on-call)
    ↓ (no response in 5 min)
Backup Engineer
    ↓ (no response in 10 min)
Team Lead
    ↓ (no response in 15 min)
Director / Management
```

---

## 4. Incident Response

### 4.1 Incident Response Procedure

**Phase 1: Detection (0-5 min)**
- Alert fires
- Page on-call engineer
- Create incident in tracking system
- Start war room (Slack + call bridge)

**Phase 2: Triage (5-15 min)**
- On-call assesses severity
- Determines if escalation needed
- Gathers initial context
- Posts status update to stakeholders

**Phase 3: Mitigation (15-60 min)**
- Execute emergency procedures
- Attempt quick fixes
- Scale resources if needed
- Keep stakeholders updated every 15 min

**Phase 4: Resolution (60+ min)**
- Resolve root cause
- Validate system stability
- Perform full health check
- Document what happened

**Phase 5: Post-Incident (24-48 hours)**
- Post-mortem meeting
- Document RCA (Root Cause Analysis)
- Create action items
- Update runbooks/documentation
- Communicate learnings

### 4.2 Runbooks

**Example: Service Down Runbook**

```
ALERT: Notification Service Down (P1 - Critical)

1. VERIFY
   - Check pod status: kubectl get pods -n production
   - Check logs: kubectl logs -f pod-name -n production
   - Check node status: kubectl get nodes
   
2. INITIAL DIAGNOSIS
   - If pod restarting: "CrashLoopBackOff"
     → Check application logs for startup errors
   - If pod pending: "Pending"
     → Check resource requests vs available
   - If node issue: Check node logs

3. QUICK FIXES
   - Restart pod: kubectl delete pod <pod-name> -n production
   - Scale up instances: kubectl scale deployment --replicas=5
   - Check database connectivity
   - Check external API availability

4. ROLLBACK (if recent deployment)
   - kubectl rollout undo deployment/notification-service -n production
   - Verify traffic restored
   - Investigate failed deployment

5. ESCALATE IF UNRESOLVED (15 min)
   - Page team lead
   - Engage database team if DB issue
   - Engage infrastructure team if cluster issue

6. COMMUNICATION
   - Update status page every 15 minutes
   - Notify customer success team
   - Post #incidents channel updates
```

---

## 5. Maintenance & Updates

### 5.1 Maintenance Windows

**Planned Maintenance:**

```
Schedule: Tuesday 02:00-04:00 AM (UTC+2)
Duration: 2 hours
Frequency: Monthly
Notification: 7 days advance notice

Activities:
- Database maintenance (VACUUM, ANALYZE)
- OS security patches
- Framework/library updates
- Infrastructure upgrades
- Backup verification
```

**Emergency Maintenance:**

```
Critical security patches: Immediate (with short notice)
Database corruption: Immediate
Data loss recovery: As needed
```

### 5.2 Update Strategy

**Application Updates:**

```
1. Develop and test in development environment
2. Deploy to staging environment
3. Run full test suite + smoke tests
4. Get approval from architect/tech lead
5. Deploy to production (canary: 10% → 50% → 100%)
6. Monitor error rate and latency
7. Rollback if issues detected
```

**Database Migrations:**

```
1. Create migration script
2. Test on copy of production data
3. Verify backward compatibility
4. Schedule off-peak time
5. Create full backup before migration
6. Execute migration
7. Verify data integrity
8. Update documentation
```

---

## 6. Performance Tuning

### 6.1 Regular Optimization Tasks

| Task | Frequency | Owner | Impact |
|------|-----------|-------|--------|
| Database statistics update | Daily | DBA | Query performance |
| Index fragmentation analysis | Weekly | DBA | Query performance |
| Connection pool optimization | Monthly | DevOps | Resource efficiency |
| Cache hit rate analysis | Weekly | Performance | Memory efficiency |
| Query plan review | Quarterly | Database Team | Optimization |
| Capacity planning review | Quarterly | DevOps | Scalability |

### 6.2 Performance Tuning Checklist

```
Database:
- ☐ VACUUM and ANALYZE completed
- ☐ Index fragmentation < 20%
- ☐ Query cache hit rate > 80%
- ☐ Replication lag < 1 minute
- ☐ Transaction log size < threshold

Application:
- ☐ Memory utilization < 80%
- ☐ CPU utilization < 75% average
- ☐ Connection pool efficiency > 80%
- ☐ API response time P95 < 200ms
- ☐ Exception rate < 0.1%

Infrastructure:
- ☐ Disk utilization < 80%
- ☐ Network bandwidth < 50% capacity
- ☐ Pod density optimal
- ☐ Node resource balanced
```

---

## 7. Deployment Process

### 7.1 Deployment Steps

```
1. Build Stage (2 min)
   - Code compilation
   - Unit tests
   - Build Docker image
   - Push to registry

2. Test Stage (10 min)
   - Integration tests
   - API contract tests
   - Database migration tests
   - Performance baseline

3. Security Stage (5 min)
   - SAST scanning
   - Dependency check
   - Container scan
   - Infrastructure scan

4. Approval (variable)
   - Manual review
   - Architecture approval
   - Tech lead sign-off

5. Staging Deploy (5 min)
   - Deploy to staging
   - Run smoke tests
   - Verify metrics

6. Production Deploy (5-10 min)
   - Canary deployment (10%)
   - Monitor error rate (2 min)
   - If OK, expand to 50%
   - Monitor error rate (2 min)
   - If OK, expand to 100%

7. Verification (5 min)
   - Health checks pass
   - Smoke tests pass
   - Metrics normal
   - No alerts

8. Rollback Ready
   - Automatic rollback if errors
   - Manual rollback available
   - Previous version retained
```

---

## 8. Documentation Requirements

### 8.1 Required Documentation

- [x] Architecture documentation (this package)
- [x] API documentation (OpenAPI/Swagger)
- [x] Database schema documentation
- [x] Deployment procedures
- [x] Runbooks for common incidents
- [x] Troubleshooting guides
- [x] Configuration management
- [x] Disaster recovery procedures

### 8.2 Documentation Maintenance

| Document | Update Frequency | Owner |
|----------|-----------------|-------|
| Architecture | Quarterly | Solution Architect |
| API Docs | With each release | Backend Team |
| Runbooks | As incidents occur | On-Call Team |
| Deployment Procedures | With infrastructure changes | DevOps |
| Troubleshooting Guides | Continuously | Support Team |

---

## 9. Knowledge Transfer & Training

### 9.1 Onboarding Program

```
Week 1: Fundamentals
- Architecture overview
- Component responsibilities
- Technology stack
- Development environment setup

Week 2: Deep Dive
- Source code walkthrough
- Database schema review
- API integration points
- Testing strategies

Week 3: Operations
- Monitoring dashboards
- Alert handling
- Incident response
- Deployment procedures

Week 4: Shadow & Support
- Shadow on-call engineer
- Handle low-priority issues
- Review architecture decisions
- Independent on-call ready
```

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
