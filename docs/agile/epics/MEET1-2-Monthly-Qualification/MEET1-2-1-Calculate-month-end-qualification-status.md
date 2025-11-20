# User Story: Calculate month-end qualification status

**Story ID:** MEET1-2-1
**Epic:** [MEET1-2: Monthly Qualification Determination](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 8
**Sprint:** Sprint 2
**Related BRD:** BR-2 (Monthly Qualification Logic)
**Related FSD:** Process 2: Monthly Qualification Calculation (Steps 1-4), Business Rules section

---

## User Story

**As a** Premium Customer Notification System
**I want** to calculate which customers maintained the 15,000 NIS balance threshold throughout an entire calendar month
**So that** I can accurately determine which customers qualify for premium recognition notifications

---

## Acceptance Criteria

- [ ] **Qualification Trigger:** Automatic execution on Day 1 of following month at 00:01 AM UTC
- [ ] **Complete Month Review:** All daily balance checks for entire previous calendar month analyzed
- [ ] **All-or-Nothing Logic:** Customer qualifies ONLY if balance ≥ 15,000 NIS on EVERY day
- [ ] **Missing Data Handling:** Any missing balance record for a day disqualifies customer
- [ ] **Binary Result:** Qualification is deterministic (Qualified or Not Qualified, no partial)
- [ ] **100% Customer Coverage:** Every active customer evaluated; no missing records
- [ ] **Results Logged:** Qualification decision with calculation details stored for audit
- [ ] **Performance:** Calculation completes within 1 hour for all customers
- [ ] **No Manual Override:** System calculates automatically; no manual adjustments

### Definition of Done

This story is complete when:
- [ ] Qualification logic implemented and tested
- [ ] Month-end trigger implemented and scheduled
- [ ] Results stored in database with all metadata
- [ ] All-or-nothing rule verified with test cases
- [ ] Missing data scenarios handled correctly
- [ ] Performance tested with 1000+ customers
- [ ] Unit tests ≥ 90% code coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Month-End Trigger** (Estimated: 3 hours)
   - Create scheduled job for Day 1 at 00:01 AM
   - Calculate previous month automatically
   - Add logging for trigger execution
   - Create configuration for timing override

2. **Build All-or-Nothing Qualification Logic** (Estimated: 6 hours)
   - Query daily_balance_checks for previous month
   - Group by customer_id
   - Count days where passes_threshold = true
   - Count total calendar days in month
   - Apply rule: qualifies if passes_threshold_count == total_days
   - Handle missing records (count as fail)

3. **Create Results Storage** (Estimated: 4 hours)
   - Design monthly_qualifications table schema
   - Add fields: customer_id, month, passes_threshold, qualifying_days, total_days, calculation_timestamp
   - Create indices for efficient queries
   - Implement immutable record insertion

4. **Implement Missing Data Handling** (Estimated: 3 hours)
   - Detect customers with missing balance records
   - Flag as disqualified in results
   - Log reason for disqualification (missing data)
   - Generate report of customers with missing data

5. **Add Audit & Logging** (Estimated: 3 hours)
   - Log all qualification decisions with reasoning
   - Create audit trail table
   - Include calculation parameters in log
   - Enable audit trail queries for compliance

6. **Optimize Performance** (Estimated: 3 hours)
   - Index daily_balance_checks by month/customer
   - Use batch processing if 1000+ customers
   - Monitor query performance
   - Optimize for sub-1-hour execution

---

## Technical Considerations

**Architecture Impacts:**
- Requires month-end batch processor
- Integration with daily balance check data
- Results storage for SMS dispatch system

**Database Changes:**

```sql
CREATE TABLE monthly_qualifications (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(50) NOT NULL,
  qualification_month DATE NOT NULL,  -- First day of month
  total_calendar_days INT NOT NULL,
  qualifying_days INT NOT NULL,
  is_qualified BOOLEAN NOT NULL,
  calculation_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_customer_month (customer_id, qualification_month),
  INDEX idx_month (qualification_month),
  INDEX idx_qualified (is_qualified)
);

CREATE TABLE qualification_audit (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(50),
  qualification_month DATE,
  detail VARCHAR(255),
  logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_customer_month (customer_id, qualification_month)
);
```

**Qualification Logic (Pseudocode)**

```python
def calculate_monthly_qualifications(year, month):
    """
    Calculate qualifications for all customers for given month
    Rule: Customer qualifies IFF balance ≥ 15000 on EVERY day
    """
    first_day = date(year, month, 1)
    last_day = get_last_day_of_month(year, month)
    total_days = (last_day - first_day).days + 1
    
    qualified_customers = []
    
    # Get all customers
    for customer in get_all_active_customers():
        # Get daily checks for this customer for this month
        daily_checks = query_daily_checks(
            customer_id=customer.id,
            start_date=first_day,
            end_date=last_day
        )
        
        # Check for missing data
        if len(daily_checks) < total_days:
            # Missing data - disqualify
            log_qualification(
                customer_id=customer.id,
                month=first_day,
                is_qualified=False,
                reason="MISSING_DATA"
            )
            continue
        
        # Count days that pass threshold
        qualifying_days = sum(1 for check in daily_checks 
                             if check.passes_threshold == True)
        
        # Apply all-or-nothing rule
        is_qualified = (qualifying_days == total_days)
        
        log_qualification(
            customer_id=customer.id,
            month=first_day,
            is_qualified=is_qualified,
            qualifying_days=qualifying_days,
            total_days=total_days
        )
        
        if is_qualified:
            qualified_customers.append(customer)
    
    return qualified_customers
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| customer_id | String(50) | Yes | Must exist in customers table |
| qualification_month | Date | Yes | First day of calendar month |
| total_calendar_days | Integer | Yes | 28-31 depending on month/year |
| qualifying_days | Integer | Yes | 0 to total_calendar_days |
| is_qualified | Boolean | Yes | true only if qualifying_days == total_calendar_days |

**Performance:**
- Target: < 1 hour for 10,000+ customers
- Use database sorting/aggregation where possible
- Consider parallel processing if volume warrants
- Index on month for historical month queries

**Security:**
- Results are financial records; access controlled
- Audit trail immutable
- Calculation parameters logged for compliance
- No sensitive customer data in results (ID only)

---

## Testing Strategy

### Unit Tests
- All-or-nothing logic with various day counts:
  - 30 qualifying days out of 30 → Qualified ✓
  - 29 qualifying days out of 30 → Not Qualified ✗
  - 0 qualifying days out of 30 → Not Qualified ✗
- Missing data detection
- Month boundary calculations (February leap year, etc.)
- Edge cases (single day qualifying)

### Integration Tests
- Calculate qualifications for test month with 100+ customers
- Verify results in database
- Check audit trail completeness
- Test with missing data scenarios
- Verify performance with large dataset

### Manual Testing Scenarios
- Run qualification for historical month (verify known results)
- Check database for all customers present
- Verify edge cases (Feb 28/29, month starts/ends)
- Review audit trail for sample customers

### Acceptance Test Checklist
- [ ] Trigger executes on Day 1 at 00:01 AM
- [ ] All customers evaluated (no missing)
- [ ] Qualified customer has 30/30 days (test month)
- [ ] Disqualified customer has 29/30 days
- [ ] Missing data correctly disqualifies
- [ ] Results stored in database
- [ ] Audit trail present and queryable
- [ ] Execution completes in < 1 hour

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-1-1, US-1-2, US-1-3 (E-001 must be complete)
- Blocks: US-3-1, US-3-2, US-3-3 (SMS dispatch)
- Blocks: US-5-1 (reporting aggregation)

### External Dependencies
- None (uses internal data from daily balance checks)

### Known Blockers
- None initially; verify E-001 completion before starting

---

## Compliance & Regulatory

**Regulatory Requirement:** Qualification determination audit trail
- [ ] All calculations logged with timestamp
- [ ] Customer qualification history maintained
- [ ] Calculation logic documented and auditable
- [ ] No manual adjustments or overrides (automated only)

---

## Documentation

### Technical Documentation
- [ ] Qualification logic specification
- [ ] Database schema documentation
- [ ] Month calculation approach
- [ ] Audit trail reference guide

---

## Estimation & Effort

**Story Points:** 8
**Estimated Hours:** 22 hours total
  - Backend development: 12 hours
  - Database: 3 hours
  - Testing: 5 hours
  - Documentation: 2 hours

**Complexity:** Medium
**Risk Level:** Low

### Estimation Breakdown
- Month-end trigger: 3 hours
- Qualification logic: 6 hours
- Results storage: 4 hours
- Missing data handling: 3 hours
- Audit logging: 3 hours
- Performance optimization: 3 hours

---

## Notes & Comments

- The all-or-nothing rule is absolutely strict: literally one missing day or one day below threshold disqualifies
- Month boundaries must follow calendar (Jan 1 - Jan 31, not rolling 30 days)
- No grace period, no averaging, no partial qualification
- Performance is important: must complete within business day for SMS dispatch

---

## Related Stories

- [US-2-2](./US-2-2.md) - Generate qualified customer list (successor)
- [US-2-3](./US-2-3.md) - Audit validation (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
