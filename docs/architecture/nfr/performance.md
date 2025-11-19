# Performance - Non-Functional Requirements

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Overview

The Premium Customer Notification System must deliver consistent, predictable performance across all operations. Performance targets are defined for critical paths and monitored continuously to ensure user expectations are met.

---

## 2. Performance Targets

### 2.1 API Response Times

| Operation | P50 | P95 | P99 | Target SLA |
|-----------|-----|-----|-----|-----------|
| Balance check retrieval | 50ms | 150ms | 300ms | 99% < 200ms |
| Qualification status query | 30ms | 100ms | 200ms | 99% < 150ms |
| Notification submission | 200ms | 500ms | 1000ms | 95% < 600ms |
| Report generation | 500ms | 2000ms | 5000ms | 90% < 3000ms |
| Webhook delivery callback | 100ms | 300ms | 600ms | 95% < 500ms |

### 2.2 Batch Processing Performance

| Operation | Input Size | Target Duration | Target Throughput |
|-----------|-----------|-----------------|------------------|
| Daily balance verification | 100,000 customers | 30 minutes | 3,333 checks/min |
| Monthly qualification | 100,000 customers | 5 minutes | 20,000 qualifications/min |
| SMS batch submission | 10,000 SMS | 2 minutes | 5,000 SMS/min |
| Delivery status polling | 1,000 SMS | 1 minute | 1,000 polls/min |
| Monthly report generation | 12 months of data | 2 minutes | N/A |

### 2.3 Database Performance

| Query Type | Data Volume | Target Latency | Index Strategy |
|-----------|------------|-----------------|-----------------|
| Customer lookup (by ID) | 100K rows | < 10ms | Primary key index |
| Balance check history | 30-day history | < 50ms | (customer_id, check_date) |
| Qualified customers list | Month qualification | < 100ms | (qualification_month, qualified) |
| Monthly report aggregation | 100K+ records | < 2s | CTEs + targeted indexes |
| Audit log retrieval | 10M+ rows | < 500ms | Partitioning by date |

---

## 3. Performance Optimization Strategies

### 3.1 Caching Strategy

**Multi-Level Cache Architecture:**

```
┌────────────────────────────────────────────┐
│ L1: Application Memory Cache (5-10 sec)    │
│ - Current customers list                   │
│ - Qualification threshold constants        │
└────────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ L2: Distributed Cache - Redis (24 hours)   │
│ - Customer master data                     │
│ - Qualified customers from previous month  │
│ - Report cache                             │
└────────────────────────────────────────────┘
           ↓
┌────────────────────────────────────────────┐
│ L3: Database (System of Record)            │
│ - All persistent data                      │
│ - Complete audit trail                     │
└────────────────────────────────────────────┘
```

**Redis Configuration:**

```csharp
public class CacheConfiguration
{
    // L1: In-memory cache
    public static readonly TimeSpan ShortLiveCache = TimeSpan.FromSeconds(10);
    
    // L2: Distributed Redis cache
    public static readonly TimeSpan CustomerDataCache = TimeSpan.FromHours(24);
    public static readonly TimeSpan QualificationCache = TimeSpan.FromDays(30);
    public static readonly TimeSpan ReportCache = TimeSpan.FromDays(30);
}

public class CustomerService
{
    public async Task<Customer> GetCustomerAsync(Guid customerId)
    {
        // Try L1 cache (IMemoryCache)
        if (_memoryCache.TryGetValue($"customer:{customerId}", out Customer cached))
        {
            return cached;
        }
        
        // Try L2 cache (Redis)
        var redisKey = $"customer:{customerId}";
        var redisValue = await _redisCache.GetStringAsync(redisKey);
        if (redisValue != null)
        {
            var customer = JsonSerializer.Deserialize<Customer>(redisValue);
            _memoryCache.Set($"customer:{customerId}", customer, 
                CacheConfiguration.ShortLiveCache);
            return customer;
        }
        
        // Query database (L3)
        var dbCustomer = await _database.Customers.FindAsync(customerId);
        
        // Populate caches
        if (dbCustomer != null)
        {
            await _redisCache.SetStringAsync(redisKey, 
                JsonSerializer.Serialize(dbCustomer),
                CacheConfiguration.CustomerDataCache);
            _memoryCache.Set($"customer:{customerId}", dbCustomer,
                CacheConfiguration.ShortLiveCache);
        }
        
        return dbCustomer;
    }
}
```

### 3.2 Database Query Optimization

**Index Design:**

```sql
-- Frequently used indexes (Priority 1)
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_daily_checks_customer_date 
    ON daily_balance_checks(customer_id, check_date);
CREATE INDEX idx_monthly_qual_month_status 
    ON monthly_qualifications(qualification_month, qualified);

-- Secondary indexes (Priority 2)
CREATE INDEX idx_notifications_status 
    ON notifications(submission_status);
CREATE INDEX idx_delivery_status_final 
    ON delivery_status(final_status, status);

-- Partial indexes for common queries
CREATE INDEX idx_pending_qualifications 
    ON monthly_qualifications(customer_id) 
    WHERE qualified = TRUE;
CREATE INDEX idx_undelivered_sms 
    ON delivery_status(notification_id, status) 
    WHERE status != 'Delivered' AND final_status = FALSE;
```

**Query Plan Analysis:**

```sql
-- Analyze slow queries (> 100ms)
EXPLAIN ANALYZE
SELECT c.id, c.phone_number, COUNT(*) as check_count
FROM customers c
LEFT JOIN daily_balance_checks dbc ON c.id = dbc.customer_id
WHERE dbc.check_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.id, c.phone_number;

-- Expected: Index Scan (customer_id, check_date)
-- Execution Time: ~50-100ms for 100K customers
```

### 3.3 Batch Processing Optimization

**Parallel Processing Configuration:**

```csharp
public class BalanceVerificationProcessor
{
    private readonly int _parallelism = 
        Math.Min(Environment.ProcessorCount, 8);
    private readonly int _batchSize = 1000;
    
    public async Task ProcessAllCustomersAsync(
        List<Customer> customers,
        CancellationToken cancellationToken)
    {
        var batches = customers
            .Chunk(_batchSize)
            .ToList();
        
        // Process batches in parallel
        var options = new ParallelOptions 
        { 
            MaxDegreeOfParallelism = _parallelism,
            CancellationToken = cancellationToken 
        };
        
        await Parallel.ForEachAsync(batches, options, 
            async (batch, ct) =>
        {
            await ProcessBatchAsync(batch, ct);
        });
    }
    
    private async Task ProcessBatchAsync(
        Customer[] batch,
        CancellationToken cancellationToken)
    {
        var results = await Task.WhenAll(
            batch.Select(c => 
                _bankingClient.GetBalanceAsync(c.AccountNumber, cancellationToken)
            )
        );
        
        // Bulk insert results
        await _database.DailyBalanceChecks.AddRangeAsync(
            results.Select(r => new DailyBalanceCheck { /* ... */ }),
            cancellationToken
        );
        
        await _database.SaveChangesAsync(cancellationToken);
    }
}
```

### 3.4 Connection Pooling

**Database Connection Configuration:**

```
Max Pool Size: 100 connections
Min Pool Size: 20 connections
Connection Lifetime: 300 seconds
Command Timeout: 30 seconds
```

**Implementation:**

```json
{
  "ConnectionStrings": {
    "Default": "Host=postgres;Database=notifications;MaxPoolSize=100;MinPoolSize=20;Pooling=true;Connection Lifetime=300;Command Timeout=30"
  }
}
```

### 3.5 Message Queue Optimization

**RabbitMQ Configuration:**

```
Prefetch Count: 10 (per consumer)
Batch Publishing: 100 messages per batch
Acknowledgment Mode: Auto-ack for fire-and-forget
Durable Queues: Yes
Message TTL: 24 hours
```

---

## 4. Monitoring & Metrics

### 4.1 Key Performance Indicators (KPIs)

| KPI | Target | Measurement | Frequency |
|-----|--------|-------------|-----------|
| Balance check completion | 100% daily | Count/total | Daily |
| Qualification accuracy | 100% | Sample audit | Monthly |
| SMS delivery rate | 98%+ | Delivered/sent | Daily |
| System uptime | 99.9% | Availability | Continuous |
| P95 API latency | < 200ms | Response time | Real-time |
| Database query time | < 100ms (avg) | Query duration | Real-time |

### 4.2 Performance Monitoring

**Prometheus Metrics:**

```csharp
public class PerformanceMetrics
{
    private readonly IMeter _meter;
    
    public PerformanceMetrics(IMeterFactory factory)
    {
        _meter = factory.Create("NotificationService");
        
        // API response time histogram
        _apiLatencyHistogram = _meter.CreateHistogram<double>(
            "api_request_duration_ms",
            unit: "ms",
            description: "HTTP request latency"
        );
        
        // Query execution time
        _dbQueryHistogram = _meter.CreateHistogram<double>(
            "db_query_duration_ms",
            unit: "ms",
            description: "Database query duration"
        );
        
        // Balance check throughput
        _balanceCheckCounter = _meter.CreateCounter<long>(
            "balance_checks_total",
            description: "Total balance checks executed"
        );
    }
}

// Usage in API controller
[HttpGet("balance/{customerId}")]
public async Task<IActionResult> GetBalance(Guid customerId)
{
    using var activity = _meter.StartActivity("GetBalance");
    var stopwatch = Stopwatch.StartNew();
    
    try
    {
        var balance = await _balanceService.GetAsync(customerId);
        stopwatch.Stop();
        _metrics.RecordApiLatency(stopwatch.ElapsedMilliseconds, "GetBalance", "200");
        return Ok(balance);
    }
    catch (Exception ex)
    {
        stopwatch.Stop();
        _metrics.RecordApiLatency(stopwatch.ElapsedMilliseconds, "GetBalance", "500");
        throw;
    }
}
```

### 4.3 Alerting Thresholds

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| P95 Latency High | > 500ms | Warning | Investigate, scale if needed |
| P99 Latency High | > 1000ms | Critical | Page on-call, scale immediately |
| Database Connection Pool Exhausted | > 95% used | Critical | Investigate connection leaks |
| Query Execution Time | > 5 seconds | Warning | Analyze query plan, add indexes |
| CPU Utilization | > 80% | Warning | Prepare for scaling |
| Memory Utilization | > 85% | Critical | Investigate memory leaks |

---

## 5. Load Testing & Capacity Planning

### 5.1 Load Test Scenarios

**Scenario 1: Daily Balance Verification**

```
- 100,000 customers
- 1 check per customer per day
- Expected duration: 30 minutes
- Parallel concurrency: 8 threads
- Throughput target: 3,333 checks/min
```

**Scenario 2: Month-End Qualification**

```
- 100,000 customers with 30-day history
- Single batch processing
- Expected duration: 5 minutes
- Parallel concurrency: 8 threads
- Throughput target: 20,000 qualifications/min
```

**Scenario 3: SMS Batch Submission**

```
- 10,000 SMS sent to carrier
- Batch size: 500 SMS per request
- Expected duration: 2 minutes
- Parallel concurrency: 4 requests
- Throughput target: 5,000 SMS/min
```

### 5.2 Capacity Planning

**Current Capacity (Year 1):**

```
- Concurrent users: 10
- Customer base: 100,000
- Balance checks: 100K/day
- SMS per month: 30K-100K
- Database size: ~50GB (with 7-year history)
```

**Projected Capacity (Year 3):**

```
- Concurrent users: 50
- Customer base: 500,000
- Balance checks: 500K/day
- SMS per month: 150K-500K
- Database size: ~500GB (with 7-year history)
```

**Scaling Plan:**

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|---------|
| App Instances | 2-3 | 5-8 | 10-15 |
| Database Size | 50GB | 150GB | 500GB |
| Cache Size | 10GB | 30GB | 100GB |
| API RPS | 100 | 500 | 2000 |

---

## 6. Performance Best Practices

### 6.1 Code-Level Optimization

**Async/Await:**

```csharp
// ✅ GOOD: Async all the way
public async Task<List<BalanceCheck>> GetBalancesAsync(Guid[] customerIds)
{
    return await _database.BalanceChecks
        .Where(b => customerIds.Contains(b.CustomerId))
        .ToListAsync();
}

// ❌ BAD: Blocking call
public List<BalanceCheck> GetBalances(Guid[] customerIds)
{
    return _database.BalanceChecks
        .Where(b => customerIds.Contains(b.CustomerId))
        .ToList();  // Blocks thread
}
```

**String Allocation:**

```csharp
// ✅ GOOD: Reuse StringBuilder for large strings
var sb = new StringBuilder();
foreach (var item in items)
{
    sb.Append(item.ToString());
}
var result = sb.ToString();

// ❌ BAD: String concatenation creates allocations
string result = "";
foreach (var item in items)
{
    result += item.ToString();
}
```

**LINQ Optimization:**

```csharp
// ✅ GOOD: Push filtering to database
var qualifiedCustomers = await _db.Customers
    .Where(c => c.IsActive)
    .Where(c => c.Qualifications.Any(q => q.Qualified))
    .ToListAsync();

// ❌ BAD: Load all, filter in memory
var allCustomers = await _db.Customers.ToListAsync();
var qualifiedCustomers = allCustomers
    .Where(c => c.IsActive)
    .Where(c => c.Qualifications.Any(q => q.Qualified))
    .ToList();
```

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
