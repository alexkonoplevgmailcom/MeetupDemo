# Scalability - Non-Functional Requirements

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Overview

The Premium Customer Notification System is designed to scale horizontally to support growth from 100,000 to 1,000,000+ customers over 3-5 years with minimal architectural changes and zero downtime.

---

## 2. Scalability Targets

### 2.1 Customer & Volume Scaling

| Phase | Timeline | Customers | Daily Checks | Monthly SMS | Concurrent Users |
|-------|----------|-----------|--------------|-------------|------------------|
| **MVP** | Now - Q1 2026 | 100K | 100K | 30K-100K | 10 |
| **Growth** | Q2-Q4 2026 | 300K | 300K | 90K-300K | 30 |
| **Scale** | Q1-Q4 2027 | 1M | 1M | 300K-1M | 100 |
| **Enterprise** | 2028+ | 5M+ | 5M+ | 1.5M-5M | 500+ |

### 2.2 Infrastructure Scaling

| Component | MVP | Growth | Scale | Enterprise |
|-----------|-----|--------|-------|-----------|
| **App Instances** | 2-3 | 5-8 | 10-15 | 20-30 |
| **Database Replicas** | 1 primary + 1 hot standby | 1 primary + 2 standby | 1 primary + 3 standby + read replicas | Sharded setup |
| **Cache Nodes (Redis)** | 2-3 nodes | 5-8 nodes | 10-15 nodes | 20+ cluster |
| **Message Queue** | 1 broker | 2-3 brokers | 3-5 brokers | RabbitMQ cluster |

---

## 3. Horizontal Scaling Architecture

### 3.1 Stateless Service Design

All backend services are stateless, enabling horizontal scaling:

```
┌────────────────────────────────────────────┐
│ Load Balancer (Ingress Controller)         │
└────────────────┬─────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
    ┌─▼─┐      ┌─▼─┐      ┌─▼─┐
    │App│      │App│      │App│
    │ 1 │      │ 2 │      │ 3 │
    └─┬─┘      └─┬─┘      └─┬─┘
      │          │          │
      └──────────┼──────────┘
                 │
        ┌────────▼────────┐
        │  Shared State   │
        ├─────────────────┤
        │ PostgreSQL (DB) │
        │ Redis (Cache)   │
        │ RabbitMQ (Queue)│
        └─────────────────┘
```

**Kubernetes Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
spec:
  replicas: 3  # Scales automatically with HPA
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: notification-service
    spec:
      containers:
      - name: app
        image: notification-service:1.0
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        env:
        - name: DATABASE_CONNECTION_POOL_SIZE
          value: "20"
        - name: CACHE_CONNECTION_POOL_SIZE
          value: "10"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: notification-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: notification-service
  minReplicas: 3
  maxReplicas: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 3.2 Load Balancing Strategy

**Kubernetes Ingress with Round-Robin:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: notification-ingress
  annotations:
    nginx.ingress.kubernetes.io/load-balance: "round_robin"
    nginx.ingress.kubernetes.io/upstream-hash-by: "$http_x_correlation_id"
spec:
  ingressClassName: nginx
  rules:
  - host: api.notification.bank
    http:
      paths:
      - path: /api/notifications
        pathType: Prefix
        backend:
          service:
            name: notification-service
            port:
              number: 80
```

---

## 4. Database Scaling Strategy

### 4.1 Scaling Approaches (MVP to Enterprise)

**Phase 1: MVP (100K customers)**
- Single PostgreSQL instance with hot standby
- Read replicas for reporting queries
- Partition by date (RANGE partitioning)

**Phase 2: Growth (300K customers)**
- Primary + 2 standby replicas
- Multiple read replicas for reporting
- Time-based partitioning (daily/monthly)
- Archive old data to S3

**Phase 3: Scale (1M customers)**
- Primary + 3 standby for HA
- Distributed read replicas across regions
- Sharding on customer_id (if needed)
- Archive data > 1 year old

**Phase 4: Enterprise (5M+ customers)**
- Database sharding by customer_id
- Each shard: Primary + 2 standby
- Cross-region replication
- Complete archive strategy

### 4.2 Partitioning Strategy

**Time-Based Partitioning (Daily):**

```sql
CREATE TABLE daily_balance_checks (
    id UUID,
    customer_id UUID,
    check_date DATE,
    balance DECIMAL(18, 2),
    passes_threshold BOOLEAN,
    check_timestamp TIMESTAMP,
    PRIMARY KEY (id, check_date)
) PARTITION BY RANGE (check_date);

-- Create partitions (auto-managed or manual)
CREATE TABLE daily_balance_checks_2025_11 
    PARTITION OF daily_balance_checks
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE daily_balance_checks_2025_12 
    PARTITION OF daily_balance_checks
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
```

**Customer-Based Sharding (Enterprise Phase):**

```
Shard Logic: hash(customer_id) % shard_count

Shard 0 (customers 0-24%)  → db-shard-0
Shard 1 (customers 25-49%) → db-shard-1
Shard 2 (customers 50-74%) → db-shard-2
Shard 3 (customers 75-99%) → db-shard-3
```

### 4.3 Read Replica Strategy

**Read Replica Configuration:**

```
Primary Database (Write Only)
    ├── Hot Standby (Failover)
    ├── Read Replica 1 (Reporting)
    ├── Read Replica 2 (Reporting)
    └── Read Replica 3 (Analytics/Archive)

Read Router (Connection String):
- Write: Direct to Primary
- Report: Round-robin to Read Replicas
- Analytics: Specific to Archive Replica
```

**Connection Configuration:**

```json
{
  "ConnectionStrings": {
    "Primary": "Host=db-primary;Database=notifications",
    "ReadReplica": "Host=db-replica-1,db-replica-2,db-replica-3;Database=notifications",
    "Analytics": "Host=db-analytics;Database=notifications"
  }
}
```

---

## 5. Cache Layer Scaling

### 5.1 Redis Cluster Configuration

**MVP to Growth Phase:**

```
Redis Standalone with Replication
- Master: 8GB memory
- Replica 1: 8GB memory
- Replica 2: 8GB memory
```

**Scale Phase onwards:**

```
Redis Cluster (3 primary nodes × 2 replicas)
- Node 1 Primary: Slots 0-5460 (8GB)
- Node 1 Replica: (8GB)
- Node 2 Primary: Slots 5461-10922 (8GB)
- Node 2 Replica: (8GB)
- Node 3 Primary: Slots 10923-16383 (8GB)
- Node 3 Replica: (8GB)

Total: 48GB distributed cache capacity
```

**Kubernetes Redis Cluster:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-cluster-config
data:
  redis.conf: |
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    maxmemory 8gb
    maxmemory-policy allkeys-lru
    save ""
    appendonly no
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6  # 3 primary + 3 replica
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - /conf/redis.conf
        ports:
        - containerPort: 6379
          name: client
        - containerPort: 16379
          name: gossip
        resources:
          requests:
            cpu: 500m
            memory: 8Gi
          limits:
            cpu: 2000m
            memory: 8Gi
        volumeMounts:
        - name: config
          mountPath: /conf
        - name: data
          mountPath: /data
      volumes:
      - name: config
        configMap:
          name: redis-cluster-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

---

## 6. Message Queue Scaling

### 6.1 RabbitMQ Clustering

**MVP Configuration:**
- Single RabbitMQ node
- Durable queues
- 5-day message retention

**Scale Configuration:**
```
RabbitMQ Cluster (3 nodes)
- Node 1 (Master)
- Node 2 (Replica)
- Node 3 (Replica)

Queue Mirroring: All queues replicated to 2 nodes
Prefetch: 10 messages per consumer
```

### 6.2 Queue Configuration for Scaling

```csharp
public class QueueConfiguration
{
    public const string BalanceVerifiedQueue = "balance-verified";
    public const string QualificationCalculatedQueue = "qualification-calculated";
    public const string NotificationSentQueue = "notification-sent";
    public const string DeliveryConfirmedQueue = "delivery-confirmed";
    
    public static void ConfigureQueues(IServiceCollection services)
    {
        services.AddMassTransit(x =>
        {
            x.AddConsumers(typeof(Program).Assembly);
            
            x.UsingRabbitMq((context, cfg) =>
            {
                cfg.Host("rabbitmq-cluster", 5672, h =>
                {
                    h.Username("rabbitmq");
                    h.Password("rabbitmq-password");
                });
                
                // Auto-scaling queues
                cfg.ReceiveEndpoint(BalanceVerifiedQueue, e =>
                {
                    e.Durable = true;
                    e.AutoDelete = false;
                    e.PrefetchCount = 10;
                    e.ConfigureConsumer<BalanceVerifiedConsumer>(context);
                });
                
                cfg.ReceiveEndpoint(QualificationCalculatedQueue, e =>
                {
                    e.Durable = true;
                    e.ConcurrentMessageLimit = 100;  // Scale with load
                    e.ConfigureConsumer<QualificationCalculatedConsumer>(context);
                });
            });
        });
    }
}
```

---

## 7. Geographic Scaling

### 7.1 Multi-Region Deployment (Future)

**Phase 4+ Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│ Global Load Balancer (GeoDNS)                           │
└─────────────┬───────────────────────────────┬───────────┘
              │                               │
       ┌──────▼──────┐               ┌───────▼──────┐
       │  Region 1   │               │  Region 2    │
       │ (Primary)   │               │ (Secondary)  │
       │ +───────+   │               │ +──────+     │
       │ │App ×3 │   │               │ │App ×2 │   │
       │ +───────+   │               │ +──────+     │
       │ +───────+   │               │ +──────+     │
       │ │  DB   │   │               │ │  DB  │     │
       │ └───────┘   │               │ └──────┘     │
       └─────────────┘               └──────────────┘
```

---

## 8. Scaling Triggers & Actions

### 8.1 Auto-Scaling Policies

| Metric | Threshold | Action | Cooldown |
|--------|-----------|--------|----------|
| CPU Usage | > 70% | +1 instance | 2 minutes |
| Memory Usage | > 80% | +1 instance | 2 minutes |
| Request Queue | > 100 | +2 instances | 5 minutes |
| API Response Time | > 500ms P95 | +2 instances | 5 minutes |
| Database Connections | > 90% pool | Alert, scale app | Immediate |
| Cache Hit Rate | < 70% | Increase cache size | Immediate |

### 8.2 Manual Scaling Triggers

| Condition | Action | Timeline |
|-----------|--------|----------|
| Customer base grows 50% | Add infrastructure | 1-2 weeks |
| Peak season approaching | +30% capacity | 2 weeks before |
| New feature deployment | +20% capacity | During deploy |
| Database size > 70% | Archive old data | Immediate |
| Replication lag > 1min | Add replicas | 1 week |

---

## 9. Capacity Planning Model

### 9.1 Growth Projection

```
Year 1 (MVP):      100,000 customers
Year 2 (Growth):   300,000 customers (+200%)
Year 3 (Scale):    1,000,000 customers (+233%)
Year 5 (Enterprise): 5,000,000 customers (+400%)
```

### 9.2 Resource Scaling Formula

```
App Instances = ceiling(Customers / 50,000) + 1

Database CPU = ceiling(DailyChecks / 100,000) + 1 (cores)

Cache Size (GB) = ceiling(Customers / 10,000)

Message Queue Size = ceiling(PeakThroughput / 10,000) (GB)
```

---

## 10. Monitoring Scalability Health

### 10.1 Scaling Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| **Pod CPU** | > 85% for > 5 min |
| **Node Memory** | > 90% |
| **Disk I/O** | > 80% utilization |
| **Network Bandwidth** | > 80% capacity |
| **Queue Depth** | > 10,000 messages |
| **Replication Lag** | > 5 minutes |
| **Connection Pool** | > 95% used |

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
