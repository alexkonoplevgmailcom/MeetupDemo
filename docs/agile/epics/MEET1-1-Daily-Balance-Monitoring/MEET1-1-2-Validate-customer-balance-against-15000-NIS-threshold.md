# User Story: Validate customer balance against 15,000 NIS threshold

**Story ID:** MEET1-1-2
**Epic:** [MEET1-1: Daily Balance Monitoring](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 1
**Related BRD:** BR-1 (Daily Balance Verification)
**Related FSD:** Process 1: Daily Balance Monitoring (Step 3), Feature 1: Daily Balance Verification

---

## User Story

**As a** Premium Customer Notification System
**I want** to compare each customer's daily balance against the 15,000 NIS threshold
**So that** I can accurately determine which customers maintain qualifying balances

---

## Acceptance Criteria

- [ ] **Threshold Logic:** Balance ≥ 15,000 NIS = Pass, Balance < 15,000 NIS = Fail
- [ ] **Precision:** Comparison accurate to last shekel (no rounding)
- [ ] **All Customers:** Every active customer account is checked
- [ ] **Exact Balance:** System uses end-of-business balance, not averaged or estimated
- [ ] **Results Logged:** Each check result stored with customer ID, balance, result, and timestamp
- [ ] **100% Coverage:** All active customers have balance check results in daily log (zero missing records)
- [ ] **Audit Trail:** Results cannot be modified after initial recording (immutable logging)
- [ ] **Data Quality Flags:** Missing or invalid data results flagged separately (not marked as Pass/Fail)

### Definition of Done

This story is complete when:
- [ ] Comparison logic implemented and tested
- [ ] Results stored in database with all required metadata
- [ ] 100% customer coverage verified in test
- [ ] Immutable logging implemented
- [ ] Data quality validation rules tested
- [ ] Unit tests ≥ 90% code coverage
- [ ] Integration tests with test banking data successful
- [ ] Performance validated (all customers checked within 2-hour window)
- [ ] Code peer-reviewed and merged to main

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Balance Comparison Logic** (Estimated: 4 hours)
   - Create comparison function (balance ≥ 15000)
   - Use Decimal type for precision (no floating-point rounding)
   - Handle null/invalid balance values
   - Unit test edge cases (exactly 15000, 14999.99, negative balances)

2. **Create Daily Balance Results Storage** (Estimated: 5 hours)
   - Design database schema for `daily_balance_checks` table
   - Add fields: customer_id, balance_amount, check_date, passes_threshold, data_quality_flag
   - Create indices on customer_id and check_date for query performance
   - Implement immutable record insertion (no updates allowed)

3. **Implement Batch Processing** (Estimated: 6 hours)
   - Retrieve all active customers from database
   - Process balance checks in configurable batch sizes (e.g., 1000 per batch)
   - Handle partial batch failures (continue processing remaining)
   - Log batch progress and statistics

4. **Add Data Quality Validation** (Estimated: 4 hours)
   - Check for null/missing balance values
   - Validate balance is numeric and non-negative
   - Flag records with data issues separately
   - Ensure flagged records don't count as Pass or Fail

5. **Create Logging & Audit Trail** (Estimated: 4 hours)
   - Log each balance check with full metadata
   - Include timestamp, customer ID, balance, result
   - Create immutable audit table
   - Implement log entry validation

6. **Write Comprehensive Tests** (Estimated: 5 hours)
   - Unit tests for comparison logic (boundary conditions)
   - Test data quality flag scenarios
   - Integration tests with test database
   - Performance test with large customer dataset (10K+ records)
   - Test batch processing with failures

---

## Technical Considerations

**Architecture Impacts:**
- Requires balance retrieval integration (from US-1-1 dependency)
- Need database for persistent storage of results

**Database Changes:**
```sql
CREATE TABLE daily_balance_checks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(50) NOT NULL,
  balance_amount DECIMAL(15, 2) NOT NULL,
  check_date DATE NOT NULL,
  check_timestamp DATETIME NOT NULL,
  passes_threshold BOOLEAN,
  data_quality_flag VARCHAR(50),  -- NULL, 'MISSING_BALANCE', 'INVALID_FORMAT', etc.
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_customer_date (customer_id, check_date),
  CONSTRAINT check_threshold CHECK (balance_amount >= 0)
);
```

**Code Example (Pseudocode)**
```python
def check_customer_balance(customer_id, balance_amount):
    if balance_amount is None:
        return {
            'passes_threshold': None,
            'data_quality_flag': 'MISSING_BALANCE'
        }
    
    if not isinstance(balance_amount, Decimal):
        return {
            'passes_threshold': None,
            'data_quality_flag': 'INVALID_FORMAT'
        }
    
    passes = balance_amount >= Decimal('15000.00')
    return {
        'passes_threshold': passes,
        'data_quality_flag': None
    }
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| customer_id | String(50) | Yes | Must exist in customers table |
| balance_amount | Decimal(15,2) | Yes | Must be ≥ 0; precisely stored |
| check_date | Date | Yes | Calendar date of check |
| check_timestamp | DateTime | Yes | End-of-business timestamp |
| passes_threshold | Boolean | No (if flagged) | true if balance ≥ 15000 NIS |
| data_quality_flag | String(50) | No | NULL if valid, error code if invalid |

**Performance:**
- Batch size: 1,000 customers per batch
- Target: Process all customers within 2 hours
- Database indexing on customer_id + check_date for fast daily lookups

**Security:**
- No sensitive banking data in logs (only amounts, not account numbers)
- Immutable records prevent accidental or malicious modifications
- Audit trail for all data quality flags

---

## Testing Strategy

### Unit Tests
- Balance check logic with boundary conditions:
  - balance = 15000.00 → Pass ✓
  - balance = 14999.99 → Fail ✗
  - balance = 15000.01 → Pass ✓
  - balance = 0 → Fail ✗
  - balance = NULL → Data Quality Flag ⚠
  - balance = "invalid" → Data Quality Flag ⚠
- Decimal precision (no rounding errors)
- Data quality flag validation

### Integration Tests
- Retrieve balances from test database (100+ test customers)
- Execute daily check process
- Verify results in daily_balance_checks table
- Check audit trail completeness
- Validate 100% customer coverage

### Manual Testing Scenarios
- Run daily check with 1000+ customer records
- Verify results accuracy manually (spot check 10 random customers)
- Check database logs for audit trail
- Validate performance metrics (completion time)

### Acceptance Test Checklist
- [ ] All 100+ test customers processed
- [ ] Balance = 15000 marked as Pass
- [ ] Balance = 14999.99 marked as Fail
- [ ] Missing balance flagged correctly
- [ ] Results immutable in database
- [ ] Audit trail complete
- [ ] Completion time < 2 hours

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-1-1 (scheduler must run first)
- Depends on: Balance data retrieval from core banking system
- Blocks: US-2-1 (qualification calculation needs daily check results)

### External Dependencies
- Core banking system must provide accurate balance data daily

### Known Blockers
- None initially; monitor data consistency from banking system

---

## Compliance & Regulatory

**Regulatory Requirement:** Audit trail for all financial data checks (compliance with banking regulations)
- [ ] All balance checks logged immutably
- [ ] Complete audit trail for compliance audits
- [ ] Data retention per regulatory requirements (suggest 7 years minimum)

---

## Documentation

### Technical Documentation
- [ ] API specification for balance retrieval
- [ ] Database schema documentation
- [ ] Data quality flag code reference
- [ ] Performance tuning guide

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 28 hours total
  - Backend development: 14 hours
  - Database design: 3 hours
  - Testing: 8 hours
  - Documentation: 3 hours

**Complexity:** Medium
**Risk Level:** Low

### Estimation Breakdown
- Balance comparison logic: 4 hours
- Database storage: 5 hours
- Batch processing: 6 hours
- Data quality validation: 4 hours
- Testing: 5 hours
- Documentation: 4 hours

---

## Notes & Comments

- Use Decimal/BigDecimal type to avoid floating-point precision issues (critical for financial calculations)
- All-or-nothing rule: single day below threshold disqualifies customer for entire month
- Weekends and holidays counted equally (no exemptions)
- Performance is critical: must complete within 2-hour window to maintain system reliability

---

## Related Stories

- [US-1-1](./US-1-1.md) - Scheduler (predecessor)
- [US-1-3](./US-1-3.md) - Error handling (parallel)
- [US-2-1](./epics/002-Monthly-Qualification/US-2-1.md) - Qualification calculation (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
