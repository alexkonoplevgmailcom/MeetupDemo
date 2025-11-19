# Data Architecture - Premium Customer Notification System

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Overview

The data architecture defines the persistent storage strategy for the Premium Customer Notification System using PostgreSQL as the primary relational database. All customer data, balance verification records, qualification results, SMS notifications, and delivery tracking information are stored with complete audit trail and compliance support.

---

## 2. Database Selection Rationale

### Why PostgreSQL?

| Criterion | PostgreSQL | Alternative | Evaluation |
|-----------|-----------|-------------|-----------|
| **ACID Support** | Full ACID | Limited in NoSQL | ✅ Required for qualification accuracy |
| **Query Complexity** | SQL with CTEs, Window Functions | NoSQL limitations | ✅ Complex reporting queries needed |
| **Audit Trail** | Excellent with triggers | Limited | ✅ Financial audit requirements |
| **Consistency** | Strong consistency | Eventual consistency | ✅ Must prevent duplicate qualifications |
| **Scalability** | Vertical + Read replicas | Horizontal unlimited | ✅ Adequate for projected scale |
| **Cost** | Open source, low operational cost | Managed services higher | ✅ Cost-effective for startup phase |
| **Ecosystem** | Rich tools and frameworks | Growing | ✅ .NET integration excellent |

**Decision:** PostgreSQL 15+ for production

---

## 3. Database Schema

### 3.1 Customer Entity

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone_number VARCHAR(20),
    account_type VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_verified TIMESTAMP
);

CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_customers_phone ON customers(phone_number);
CREATE INDEX idx_customers_account ON customers(account_number);
```

**Attributes:**
- `id` - Unique customer identifier
- `account_number` - Bank account reference
- `first_name`, `last_name` - Customer identity
- `email` - Contact email (optional)
- `phone_number` - SMS recipient number (E.164 format)
- `account_type` - Customer segment classification
- `is_active` - Account status flag
- `created_at`, `updated_at` - Lifecycle tracking

---

### 3.2 Daily Balance Checks

```sql
CREATE TABLE daily_balance_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    check_date DATE NOT NULL,
    balance DECIMAL(18, 2) NOT NULL,
    threshold DECIMAL(18, 2) NOT NULL DEFAULT 15000,
    passes_threshold BOOLEAN NOT NULL,
    check_timestamp TIMESTAMP NOT NULL,
    data_quality_flag VARCHAR(100),
    correlation_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_daily_checks_customer_date 
    ON daily_balance_checks(customer_id, check_date);
CREATE INDEX idx_daily_checks_date_status 
    ON daily_balance_checks(check_date, passes_threshold);
CREATE INDEX idx_daily_checks_customer_month 
    ON daily_balance_checks(customer_id, EXTRACT(YEAR FROM check_date), 
                            EXTRACT(MONTH FROM check_date));
```

**Attributes:**
- `id` - Record unique identifier
- `customer_id` - Reference to customer
- `check_date` - Date of balance check (calendar date)
- `balance` - Account balance as of EOB
- `threshold` - Qualification threshold (15,000 NIS)
- `passes_threshold` - Boolean result (balance ≥ threshold)
- `check_timestamp` - Exact time of check
- `data_quality_flag` - Error/exception flag if any
- `correlation_id` - Trace across services

---

### 3.3 Monthly Qualifications

```sql
CREATE TABLE monthly_qualifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    qualification_month DATE NOT NULL,
    qualified BOOLEAN NOT NULL,
    qualifying_days INTEGER,
    total_days_in_month INTEGER,
    disqualification_reason VARCHAR(255),
    phone_number_validated BOOLEAN DEFAULT FALSE,
    calculated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, qualification_month)
);

CREATE INDEX idx_monthly_qual_customer_month 
    ON monthly_qualifications(customer_id, qualification_month);
CREATE INDEX idx_monthly_qual_month_status 
    ON monthly_qualifications(qualification_month, qualified);
CREATE INDEX idx_monthly_qual_qualified 
    ON monthly_qualifications(qualified, qualification_month);
```

**Attributes:**
- `id` - Record identifier
- `customer_id` - Reference to customer
- `qualification_month` - Year-month of qualification
- `qualified` - Final qualification decision
- `qualifying_days` - Days meeting threshold
- `total_days_in_month` - Calendar days in month
- `disqualification_reason` - If not qualified, reason
- `phone_number_validated` - Phone validation status
- `calculated_at` - When determination was made

---

### 3.4 Notifications (SMS Records)

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    qualification_id UUID NOT NULL REFERENCES monthly_qualifications(id),
    phone_number VARCHAR(20) NOT NULL,
    sms_content TEXT NOT NULL,
    character_count INTEGER,
    carrier_reference_id VARCHAR(255),
    submission_timestamp TIMESTAMP NOT NULL,
    submission_status VARCHAR(50), -- Submitted, Failed, Queued
    batch_id UUID,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_customer ON notifications(customer_id);
CREATE INDEX idx_notifications_carrier_ref 
    ON notifications(carrier_reference_id);
CREATE INDEX idx_notifications_submission 
    ON notifications(submission_timestamp);
CREATE INDEX idx_notifications_batch ON notifications(batch_id);
```

**Attributes:**
- `id` - SMS record identifier
- `customer_id` - Reference to customer
- `qualification_id` - Reference to qualification
- `phone_number` - Recipient phone number
- `sms_content` - Exact message text sent
- `character_count` - SMS character count
- `carrier_reference_id` - Carrier's tracking ID
- `submission_timestamp` - When submitted to carrier
- `submission_status` - Submission result status
- `batch_id` - Batch submission grouping
- `retry_count` - Retry attempts made

---

### 3.5 Delivery Status Tracking

```sql
CREATE TABLE delivery_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES notifications(id),
    status VARCHAR(50) NOT NULL, -- Delivered, Failed, Undeliverable, Pending
    status_code VARCHAR(50),
    failure_reason VARCHAR(255),
    delivery_timestamp TIMESTAMP,
    last_check_timestamp TIMESTAMP,
    attempts INTEGER DEFAULT 1,
    final_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_delivery_status_notification 
    ON delivery_status(notification_id);
CREATE INDEX idx_delivery_status_status 
    ON delivery_status(status, final_status);
CREATE INDEX idx_delivery_status_timestamp 
    ON delivery_status(last_check_timestamp);
```

**Attributes:**
- `id` - Tracking record identifier
- `notification_id` - Reference to SMS record
- `status` - Current delivery status
- `status_code` - Carrier-specific error code
- `failure_reason` - Human-readable failure description
- `delivery_timestamp` - When delivered (if successful)
- `last_check_timestamp` - Last status query time
- `attempts` - Total polling attempts
- `final_status` - Whether status is final

---

### 3.6 Audit Log

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    operation VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, PROCESS
    old_values JSONB,
    new_values JSONB,
    correlation_id UUID,
    user_id VARCHAR(100),
    service_name VARCHAR(100),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_operation ON audit_log(operation, timestamp);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_correlation ON audit_log(correlation_id);
```

**Attributes:**
- `id` - Audit record identifier
- `entity_type` - Type of entity modified (Customer, Qualification, etc.)
- `entity_id` - ID of entity modified
- `operation` - Type of operation performed
- `old_values` - Previous state (JSON)
- `new_values` - New state (JSON)
- `correlation_id` - Request trace ID
- `user_id` - User who made change (if applicable)
- `service_name` - Service that performed operation
- `details` - Additional context (JSON)

---

### 3.7 System Metrics & Events

```sql
CREATE TABLE system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50), -- INFO, WARNING, ERROR, CRITICAL
    service_name VARCHAR(100),
    description TEXT,
    event_data JSONB,
    correlation_id UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_events_type ON system_events(event_type);
CREATE INDEX idx_system_events_severity ON system_events(severity);
CREATE INDEX idx_system_events_service ON system_events(service_name);
CREATE INDEX idx_system_events_timestamp ON system_events(created_at DESC);
```

**Attributes:**
- `id` - Event identifier
- `event_type` - Category of event
- `severity` - Severity level
- `service_name` - Service generating event
- `description` - Event description
- `event_data` - Event details (JSON)
- `correlation_id` - Request trace

---

## 4. Data Relationships

### Entity Relationship Diagram

```
Customers (1)
    ├─── (1:N) ─── DailyBalanceChecks
    ├─── (1:N) ─── MonthlyQualifications
    └─── (1:N) ─── Notifications
                       ├─── (1:1) ─── MonthlyQualifications
                       └─── (1:N) ─── DeliveryStatus
```

### Relationship Details

| Relationship | From | To | Type | Cascade |
|-------------|------|----|----|---------|
| Customer → Balance Checks | customers.id | daily_balance_checks.customer_id | 1:N | No |
| Customer → Qualifications | customers.id | monthly_qualifications.customer_id | 1:N | No |
| Customer → Notifications | customers.id | notifications.customer_id | 1:N | No |
| Qualification → Notifications | monthly_qualifications.id | notifications.qualification_id | 1:N | No |
| Notification → Delivery Status | notifications.id | delivery_status.notification_id | 1:N | Yes |

---

## 5. Indexing Strategy

### Primary Indexes (High Priority)

```sql
-- Query by customer for personal data access
CREATE INDEX idx_daily_checks_customer_date 
    ON daily_balance_checks(customer_id, check_date);

-- Query by month for qualification calculation
CREATE INDEX idx_daily_checks_customer_month 
    ON daily_balance_checks(customer_id, 
                            EXTRACT(YEAR FROM check_date),
                            EXTRACT(MONTH FROM check_date));

-- Query qualification status by month
CREATE INDEX idx_monthly_qual_month_status 
    ON monthly_qualifications(qualification_month, qualified);

-- Query undelivered SMS
CREATE INDEX idx_delivery_undelivered 
    ON delivery_status(status) WHERE status != 'Delivered';
```

### Performance Analysis

| Index | Query Pattern | Selectivity | Estimated Rows |
|-------|---------------|-------------|-----------------|
| idx_daily_checks_customer_date | Balance check history | Low (~1000 rows/month) | 100-1000 |
| idx_monthly_qual_month_status | Qualified customers | Medium (~10-20%) | 10K-20K |
| idx_notifications_carrier_ref | Delivery tracking | High (unique) | 1 |
| idx_delivery_undelivered | Failed SMS analysis | Low (~2%) | 100-1000 |

---

## 6. Query Optimization

### 6.1 Qualification Calculation Query

```sql
-- Optimized: Single query with window functions
SELECT 
    c.id,
    c.phone_number,
    COUNT(dbc.id) FILTER (WHERE dbc.passes_threshold = TRUE) 
        AS qualifying_days,
    COUNT(dbc.id) AS total_days,
    COUNT(dbc.id) FILTER (WHERE dbc.passes_threshold = TRUE) = COUNT(dbc.id) 
        AS qualified
FROM customers c
LEFT JOIN daily_balance_checks dbc 
    ON c.id = dbc.customer_id
    AND EXTRACT(YEAR FROM dbc.check_date) = 2025
    AND EXTRACT(MONTH FROM dbc.check_date) = 11
WHERE c.is_active = TRUE
GROUP BY c.id, c.phone_number
HAVING COUNT(dbc.id) > 0;
```

**Query Performance:**
- Uses indexes on `(customer_id, check_date)`
- Aggregate functions prevent full table scans
- Execution time: < 1 second for 100K customers

### 6.2 Monthly Performance Report Query

```sql
-- Aggregated metrics with CTEs
WITH qualified_cte AS (
    SELECT 
        COUNT(*) AS qualified_count,
        COUNT(*) * 100.0 / 
            (SELECT COUNT(DISTINCT customer_id) 
             FROM daily_balance_checks 
             WHERE check_date BETWEEN '2025-11-01' AND '2025-11-30')
        AS qualification_rate
    FROM monthly_qualifications
    WHERE qualification_month = '2025-11-01'
      AND qualified = TRUE
),
delivery_cte AS (
    SELECT 
        COUNT(*) AS total_sent,
        COUNT(*) FILTER (WHERE status = 'Delivered') AS delivered,
        COUNT(*) FILTER (WHERE status = 'Delivered') * 100.0 / COUNT(*)
            AS delivery_rate
    FROM delivery_status ds
    JOIN notifications n ON ds.notification_id = n.id
    WHERE n.submission_timestamp >= '2025-11-01'
)
SELECT * FROM qualified_cte, delivery_cte;
```

**Query Performance:**
- CTEs enable modular analysis
- Uses targeted indexes
- Execution time: < 2 seconds

---

## 7. Data Consistency & Integrity

### 7.1 Constraints

```sql
-- Business rule: Qualification requires validated phone number
ALTER TABLE monthly_qualifications
ADD CONSTRAINT chk_qualified_has_phone 
    CHECK (qualified = FALSE OR phone_number_validated = TRUE);

-- Business rule: Balance must be non-negative
ALTER TABLE daily_balance_checks
ADD CONSTRAINT chk_balance_positive CHECK (balance >= 0);

-- Business rule: SMS must have carrier reference if submitted
ALTER TABLE notifications
ADD CONSTRAINT chk_submitted_has_reference 
    CHECK (submission_status != 'Submitted' 
           OR carrier_reference_id IS NOT NULL);
```

### 7.2 Triggers for Audit Trail

```sql
CREATE OR REPLACE FUNCTION audit_balance_check_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log 
        (entity_type, entity_id, operation, new_values, 
         timestamp, service_name)
    VALUES 
        ('BalanceCheck', NEW.id, TG_OP, row_to_json(NEW), 
         CURRENT_TIMESTAMP, 'BalanceMonitor');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER balance_check_audit_trigger
AFTER INSERT OR UPDATE ON daily_balance_checks
FOR EACH ROW EXECUTE FUNCTION audit_balance_check_change();
```

### 7.3 Data Validation

| Field | Validation Rule |
|-------|-----------------|
| `phone_number` | E.164 format: `^\+\d{1,15}$` |
| `balance` | Decimal with 2 places, ≥ 0 |
| `check_date` | Valid calendar date, not future |
| `email` | RFC 5322 email format |
| `account_number` | Non-empty, 50 char max |

---

## 8. Backup & Recovery Strategy

### 8.1 Backup Policy

```sql
-- Daily full backups
-- Retention: 30 days for daily, 90 days for weekly, 1 year for monthly

-- Example: PostgreSQL pg_dump configuration
-- pg_dump --format=custom --verbose \
--   -d notifications_db > backup_$(date +%Y%m%d).dump

-- Automated backup with PITR
-- WAL archiving to S3: wal_level = replica
-- wal_archive_command = 'aws s3 cp %p s3://backups/wal/%f'
```

### 8.2 Recovery Objectives

| Metric | Target | Implementation |
|--------|--------|-----------------|
| **RPO** (Recovery Point Objective) | < 1 hour | Continuous WAL streaming |
| **RTO** (Recovery Time Objective) | < 5 minutes | Hot standby replica failover |
| **Backup Retention** | 90 days | Automated lifecycle |

### 8.3 Disaster Recovery Procedure

```
1. Primary database fails
2. Automated detection (health check)
3. Failover to hot standby within 30 seconds
4. Connection string updated via DNS
5. Applications reconnect automatically
6. Validation of data integrity
7. Investigation of primary failure
8. Recovery and resynchronization
```

---

## 9. Data Retention & Archival

### 9.1 Retention Policies

| Entity | Retention Period | Rationale | Archive Strategy |
|--------|-----------------|-----------|-----------------|
| **Daily Balance Checks** | 7 years | Regulatory compliance | Archive to cold storage after 1 year |
| **Monthly Qualifications** | 7 years | Audit trail | Archive to cold storage after 1 year |
| **Notifications** | 7 years | Compliance | Archive to cold storage after 1 year |
| **Delivery Status** | 7 years | SMS audit | Archive to cold storage after 1 year |
| **Audit Log** | 10 years | Financial regulations | Archive to cold storage after 2 years |
| **System Events** | 1 year | Operational | Automated deletion after 1 year |

### 9.2 Archival Process

```sql
-- Archive old records to cold storage
CREATE TABLE daily_balance_checks_archive LIKE daily_balance_checks;

-- Automated daily archival job (runs 02:00 AM)
INSERT INTO daily_balance_checks_archive
SELECT * FROM daily_balance_checks
WHERE check_date < DATE_TRUNC('year', CURRENT_DATE - interval '1 year');

DELETE FROM daily_balance_checks
WHERE check_date < DATE_TRUNC('year', CURRENT_DATE - interval '1 year');

-- Compress and move to S3
-- AWS Glue job or similar to export archive tables to parquet/CSV
```

---

## 10. Compliance & GDPR

### 10.1 Data Classification

| Classification | Examples | Protection Level |
|----------------|----------|-----------------|
| **Public** | System events, general metrics | None required |
| **Internal** | Balance amounts, qualification status | Encryption at rest |
| **Sensitive** | Phone numbers, customer names | Encryption at rest + TLS + Audit log |
| **Highly Sensitive** | Email addresses, PII | Encryption at rest + TLS + Access control + Audit log |

### 10.2 Data Subject Rights

```sql
-- Right to Access: Retrieve all customer data
SELECT * FROM customers WHERE id = $1;
SELECT * FROM daily_balance_checks WHERE customer_id = $1;
SELECT * FROM monthly_qualifications WHERE customer_id = $1;
SELECT * FROM notifications WHERE customer_id = $1;
SELECT * FROM delivery_status WHERE notification_id IN (
    SELECT id FROM notifications WHERE customer_id = $1
);

-- Right to Erasure: Delete customer data (soft delete recommended)
UPDATE customers SET is_active = FALSE WHERE id = $1;
-- Hard delete only if no audit/compliance requirements
DELETE FROM daily_balance_checks WHERE customer_id = $1;
```

---

## 11. Monitoring & Alerts

### Database Health Monitoring

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| **Disk Usage** | > 80% | Scale storage, alert team |
| **Replication Lag** | > 1 minute | Investigate replica health |
| **Slow Queries** | > 5 seconds | Analyze query plans |
| **Connection Pool** | > 90% used | Scale connections |
| **Transaction Deadlock** | Any deadlock | Analyze transaction isolation |
| **Backup Failure** | 24 hours since backup | Investigate, restore manually |

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
