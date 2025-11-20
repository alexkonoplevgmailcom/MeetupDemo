# User Story: Audit and validate qualification results

**Story ID:** MEET1-2-3
**Epic:** [MEET1-2: Monthly Qualification Determination](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 2
**Related BRD:** BR-2 (Audit Requirements)
**Related FSD:** Process 2: Daily Balance Monitoring (Data Output section), Audit trail requirements

---

## User Story

**As a** Compliance Officer
**I want** to audit and validate that qualification calculations are accurate and properly logged
**So that** I can ensure the system meets regulatory requirements and calculations are correct

---

## Acceptance Criteria

- [ ] **Audit Trail Complete:** All qualification decisions logged with calculation details
- [ ] **Calculation Verification:** Sample verification of qualification results shows 100% accuracy
- [ ] **Immutable Records:** Qualification records cannot be modified after initial creation
- [ ] **Data Traceability:** Each qualified customer can be traced back to source daily balance checks
- [ ] **Exception Logging:** All exceptions (missing data, errors) logged separately
- [ ] **Calculation Transparency:** Calculation logic and parameters documented and auditable
- [ ] **Compliance Report:** Audit report shows all calculations for regulatory review
- [ ] **Data Integrity:** Cross-checks verify no missing customers or duplicates

### Definition of Done

This story is complete when:
- [ ] Audit trail table created and populated
- [ ] Immutability constraints implemented in database
- [ ] Audit queries written and tested
- [ ] Sample verification (20+ customers) performed
- [ ] Compliance report template created
- [ ] Unit tests for audit queries
- [ ] Integration tests with full month of data
- [ ] Documentation complete
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Create Audit Trail Tables** (Estimated: 3 hours)
   - Design qualification_audit table
   - Store calculation decisions with reasoning
   - Include: timestamp, customer_id, qualification_month, decision, reason
   - Make records immutable (no updates allowed)

2. **Implement Immutability Constraints** (Estimated: 2 hours)
   - Add database constraints (no UPDATE/DELETE on audit records)
   - Implement application-level validation
   - Log any attempts to modify records
   - Use database triggers for enforcement

3. **Build Audit Queries** (Estimated: 3 hours)
   - Query to verify customer qualification by tracing to daily checks
   - Query to list all exceptions and failures
   - Query to count qualified vs. not qualified
   - Query to verify no missing customers

4. **Create Sample Verification Script** (Estimated: 3 hours)
   - Spot-check 20+ qualified customers
   - Verify calculation by manually reviewing daily checks
   - Verify disqualified customers have at least one day below threshold
   - Report any discrepancies

5. **Generate Compliance Report** (Estimated: 2 hours)
   - Create report template showing:
     - Total customers evaluated
     - Total qualified
     - Total disqualified (with reasons)
     - Exceptions and errors
     - Sample verification results
   - Make report exportable (PDF/Excel)

6. **Write Audit Tests** (Estimated: 2 hours)
   - Unit tests for audit queries
   - Integration tests with full month data
   - Test verification script accuracy
   - Test report generation

---

## Technical Considerations

**Database Changes:**

```sql
-- Audit trail table (immutable)
CREATE TABLE qualification_audit (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(50) NOT NULL,
  qualification_month DATE NOT NULL,
  is_qualified BOOLEAN NOT NULL,
  qualifying_days INT,
  total_calendar_days INT,
  decision_reason VARCHAR(255),  -- "ALL_DAYS_QUALIFY", "MISSING_DATA", "BELOW_THRESHOLD_ON_DAY_X"
  audit_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_customer_month (customer_id, qualification_month),
  CONSTRAINT check_audit_record CHECK (id IS NOT NULL)
  -- No updates allowed - application enforces this
);

-- Make monthly_qualifications immutable
ALTER TABLE monthly_qualifications
ADD CONSTRAINT prevent_updates CHECK (1=1);
-- Application layer prevents actual updates

-- Log any modification attempts
CREATE TABLE modification_attempts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  table_name VARCHAR(50),
  record_id BIGINT,
  attempted_by VARCHAR(50),
  attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  reason VARCHAR(255),
  INDEX idx_attempted_at (attempted_at)
);
```

**Audit Query Examples (Pseudocode)**

```python
def verify_customer_qualification(customer_id, qualification_month):
    """
    Trace customer qualification back to source data
    Returns: qualification result and verification status
    """
    # Get qualification decision
    decision = query_qualification(customer_id, qualification_month)
    
    # Get all daily checks for this customer in this month
    daily_checks = query_daily_checks(
        customer_id=customer_id,
        month=qualification_month
    )
    
    # Manually calculate what should be qualified
    passing_days = sum(1 for check in daily_checks 
                      if check.passes_threshold)
    total_days = len(daily_checks)
    should_qualify = (passing_days == total_days)
    
    # Compare
    verification_passed = (decision.is_qualified == should_qualify)
    
    return {
        'customer_id': customer_id,
        'month': qualification_month,
        'decision': decision.is_qualified,
        'manual_calculation': should_qualify,
        'verification_passed': verification_passed,
        'passing_days': passing_days,
        'total_days': total_days,
        'daily_checks_count': len(daily_checks)
    }

def generate_compliance_report(qualification_month):
    """Generate audit report for regulatory review"""
    all_customers = get_all_customers()
    qualifications = query_qualifications_for_month(qualification_month)
    
    total_evaluated = len(all_customers)
    total_qualified = sum(1 for q in qualifications if q.is_qualified)
    total_not_qualified = total_evaluated - total_qualified
    
    exceptions = query_exceptions_for_month(qualification_month)
    missing_data_exceptions = filter(lambda e: e.reason == "MISSING_DATA", exceptions)
    
    # Spot-check sample
    sample_size = min(20, len(qualifications))
    sample_customers = random_sample(qualifications, sample_size)
    verification_results = [
        verify_customer_qualification(c.customer_id, qualification_month)
        for c in sample_customers
    ]
    verification_passed_count = sum(1 for r in verification_results if r.verification_passed)
    
    return {
        'month': qualification_month,
        'total_customers_evaluated': total_evaluated,
        'total_qualified': total_qualified,
        'total_not_qualified': total_not_qualified,
        'exception_count': len(exceptions),
        'missing_data_count': len(missing_data_exceptions),
        'sample_verification': {
            'sample_size': sample_size,
            'passed': verification_passed_count,
            'failed': sample_size - verification_passed_count,
            'details': verification_results
        }
    }
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| customer_id | String(50) | Yes | Matches qualification record |
| qualification_month | Date | Yes | Month evaluated |
| is_qualified | Boolean | Yes | true/false based on logic |
| qualifying_days | Integer | No | Days meeting threshold |
| total_calendar_days | Integer | No | Days in month |
| decision_reason | String(255) | Yes | Explanation of decision |
| audit_timestamp | DateTime | Yes | When recorded (immutable) |

---

## Testing Strategy

### Unit Tests
- Audit query accuracy
- Verification script correctness
- Sample calculation matches system calculation
- Report generation format

### Integration Tests
- Verify full month of 100+ customers
- Spot-check 20+ random customers
- Verify audit trail completeness
- Test immutability constraints

### Manual Testing Scenarios
- Manually review 10 qualified customers
- Trace each to source daily checks
- Review 10 disqualified customers
- Verify reason for disqualification
- Generate compliance report
- Export report to PDF

### Acceptance Test Checklist
- [ ] Audit trail table populated
- [ ] Immutability constraints prevent updates
- [ ] Verification script runs successfully
- [ ] Sample verification shows 100% accuracy
- [ ] All customers traced to daily checks
- [ ] No missing customers in audit
- [ ] Compliance report generates correctly
- [ ] All exceptions logged separately

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-2-1 (qualification calculation must be complete)
- Depends on: US-2-2 (qualified list generation)

### External Dependencies
- None (uses internal data)

### Known Blockers
- None initially

---

## Compliance & Regulatory

**Regulatory Requirement:** Complete audit trail for all financial calculations
- [ ] All qualification decisions logged immutably
- [ ] Calculation logic documented and verifiable
- [ ] Sample verification shows accuracy
- [ ] Exception handling documented
- [ ] Compliance report available for auditors

---

## Documentation

### Technical Documentation
- Audit query reference guide
- Immutability enforcement documentation
- Verification script guide
- Compliance report format specification

---

## Estimation & Effort

**Story Points:** 3
**Estimated Hours:** 15 hours total
  - Backend development: 8 hours
  - Database: 2 hours
  - Testing: 3 hours
  - Documentation: 2 hours

**Complexity:** Low
**Risk Level:** Low

### Estimation Breakdown
- Audit tables: 3 hours
- Immutability: 2 hours
- Audit queries: 3 hours
- Verification script: 3 hours
- Compliance report: 2 hours
- Testing: 2 hours

---

## Notes & Comments

- Immutability is key: once a qualification is recorded, it cannot be changed
- Audit trail is for regulatory compliance: must be complete and accurate
- Sample verification provides confidence in system accuracy
- Compliance report is executive-facing: must be clear and comprehensive

---

## Related Stories

- [US-2-1](./US-2-1.md) - Qualification calculation (predecessor)
- [US-2-2](./US-2-2.md) - Customer list generation (predecessor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
