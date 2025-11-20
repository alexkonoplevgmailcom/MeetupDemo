# User Story: Log and categorize SMS delivery outcomes

**Story ID:** MEET1-4-2
**Epic:** [MEET1-4: SMS Delivery Tracking & Confirmation](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 3
**Related BRD:** BR-4 (Delivery Logging)
**Related FSD:** Process 4 (Steps 3-5)

---

## User Story

**As a** System Administrator
**I want** to log and categorize all SMS delivery outcomes in a structured format
**So that** delivery success/failure can be analyzed and reported

---

## Acceptance Criteria

- [ ] **Complete Logging:** Every message delivery outcome logged (Delivered / Failed / Pending)
- [ ] **Failure Classification:** Failed messages categorized by failure type
- [ ] **Data Integrity:** All logs immutable and audit-traceable
- [ ] **Query Capability:** Delivery outcomes queryable by customer, date, status, failure reason
- [ ] **Reporting Ready:** Data formatted for analytics and reporting
- [ ] **Compliance:** Audit trail meets regulatory requirements
- [ ] **Performance:** Logging doesn't impact delivery polling performance
- [ ] **Data Quality:** No missing or incomplete records

### Definition of Done

This story is complete when:
- [ ] Delivery logging schema designed
- [ ] Logging queries written and tested
- [ ] 1000+ messages logged successfully
- [ ] Query performance validated
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Design Delivery Logging Schema** (Estimated: 2 hours)
   - Create detailed delivery log table
   - Include all tracking and outcome data
   - Design for query performance

2. **Implement Delivery Logging** (Estimated: 2 hours)
   - Log each delivery confirmation
   - Categorize outcomes (Delivered/Failed)
   - Capture failure reasons

3. **Build Query Layer** (Estimated: 2 hours)
   - Query by customer ID
   - Query by date range
   - Query by delivery status
   - Query by failure reason

4. **Create Failure Categorization** (Estimated: 2 hours)
   - Define failure categories
   - Map carrier failure codes to categories
   - Create categorization rules

5. **Implement Immutability** (Estimated: 1 hour)
   - Ensure delivery logs cannot be modified
   - Add audit constraints
   - Implement application-level validation

6. **Write Tests** (Estimated: 2 hours)
   - Unit tests for logging
   - Query accuracy tests
   - Integration tests

---

## Technical Considerations

**Failure Categories**

| Category | Examples | Action |
|----------|----------|--------|
| Invalid Number | Invalid format, non-existent | Manual number validation |
| Network Error | No carrier connection, timeout | Retry |
| Carrier Error | Rate limit, server error | Retry |
| Undeliverable | Blocked number, device off | Escalate |
| Unknown | No confirmation after 72h | Escalate |

**Database Schema**

```sql
CREATE TABLE sms_delivery_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tracking_id VARCHAR(100) NOT NULL,
  customer_id VARCHAR(50),
  phone_number VARCHAR(20),
  message_content TEXT,
  submission_timestamp DATETIME,
  delivery_status ENUM('DELIVERED', 'FAILED', 'PENDING') NOT NULL,
  failure_category VARCHAR(50),
  failure_reason TEXT,
  final_status_at DATETIME,
  retry_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_customer_id (customer_id),
  INDEX idx_status (delivery_status),
  INDEX idx_failure_category (failure_category),
  INDEX idx_final_status_at (final_status_at)
);
```

**Logging Logic (Pseudocode)**

```python
def log_delivery_outcome(tracking_id, delivery_status, failure_code=None):
    """Log SMS delivery outcome"""
    
    failure_category = categorize_failure(failure_code) if failure_code else None
    
    log_entry = {
        'tracking_id': tracking_id,
        'delivery_status': delivery_status,
        'failure_category': failure_category,
        'failure_reason': map_failure_code(failure_code),
        'final_status_at': datetime.now()
    }
    
    # Store in database
    store_delivery_log(log_entry)
    
    return log_entry

def categorize_failure(failure_code):
    """Categorize failure by type"""
    categories = {
        'INVALID_NUMBER': 'INVALID_NUMBER',
        'INVALID_FORMAT': 'INVALID_NUMBER',
        'TIMEOUT': 'NETWORK_ERROR',
        'CONNECT_FAIL': 'NETWORK_ERROR',
        'RATE_LIMIT': 'CARRIER_ERROR',
        'SERVICE_ERROR': 'CARRIER_ERROR',
        'BLOCKED': 'UNDELIVERABLE',
        'OFFLINE': 'UNDELIVERABLE',
        'UNKNOWN': 'UNKNOWN'
    }
    return categories.get(failure_code, 'UNKNOWN')

def query_delivery_by_status(status, start_date, end_date):
    """Query delivery outcomes by status"""
    return query_delivery_log(
        delivery_status=status,
        final_status_at_between=[start_date, end_date]
    )

def query_delivery_by_failure_category(category):
    """Query failed deliveries by failure category"""
    return query_delivery_log(
        failure_category=category,
        delivery_status='FAILED'
    )
```

**Query Examples**

```sql
-- Delivery success rate
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) as delivered,
  SUM(CASE WHEN delivery_status = 'FAILED' THEN 1 ELSE 0 END) as failed,
  ROUND(
    SUM(CASE WHEN delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    2
  ) as success_rate
FROM sms_delivery_log;

-- Failed messages by category
SELECT 
  failure_category,
  COUNT(*) as count,
  COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sms_delivery_log WHERE delivery_status = 'FAILED') as pct
FROM sms_delivery_log
WHERE delivery_status = 'FAILED'
GROUP BY failure_category
ORDER BY count DESC;
```

---

## Testing Strategy

### Unit Tests
- Logging function correctness
- Failure categorization
- Query accuracy
- Immutability constraints

### Integration Tests
- Log 1000+ delivery outcomes
- Query by status, customer, date
- Verify failure categorization
- Check performance

### Manual Testing Scenarios
- Review delivery logs for sample customers
- Query by failure category
- Check success rate calculation
- Verify immutability

### Acceptance Test Checklist
- [ ] 1000+ messages logged
- [ ] Success rate calculated correctly
- [ ] Failed messages categorized
- [ ] Queries performant
- [ ] Logs immutable
- [ ] No missing records

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-4-1 (polling for statuses)
- Blocks: US-5-1 (reporting aggregation)

### External Dependencies
- None

---

## Documentation

### Technical Documentation
- Delivery logging schema
- Failure categorization reference
- Query guide

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 11 hours
- Backend: 6 hours
- Testing: 3 hours
- Documentation: 2 hours

**Complexity:** Medium
**Risk Level:** Low

---

## Related Stories

- [US-4-1](./US-4-1.md) - Delivery polling (predecessor)
- [US-4-3](./US-4-3.md) - Retry logic (parallel)
- [US-5-1](./epics/005-Reporting-Analytics/US-5-1.md) - Reporting (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
