# User Story: Generate qualified customer list with metadata

**Story ID:** MEET1-2-2
**Epic:** [MEET1-2: Monthly Qualification Determination](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 2
**Related BRD:** BR-2 (Qualified Customer List Output)
**Related FSD:** Process 2: Monthly Qualification Calculation (Step 4-5), Data Output section

---

## User Story

**As the** SMS Notification Dispatch System
**I want** to retrieve a structured list of qualified customers with phone numbers and contact information
**So that** I can generate and send SMS notifications to premium customers

---

## Acceptance Criteria

- [ ] **Customer List:** List includes all qualified customers from current month-end calculation
- [ ] **Phone Numbers:** Each customer includes valid phone number for SMS delivery
- [ ] **Metadata:** List includes customer ID, name, phone number, qualification date
- [ ] **Structured Format:** Data provided in queryable format (database view or export file)
- [ ] **Currency Tracking:** Each record includes qualified customer ID and qualification month
- [ ] **No Duplicates:** Each qualified customer appears exactly once in list
- [ ] **Data Quality:** Phone numbers validated as deliverable (non-null, correct format)
- [ ] **Access Method:** SMS dispatch system can query list programmatically
- [ ] **Export Capability:** List can be exported to CSV or other format for reporting

### Definition of Done

This story is complete when:
- [ ] Database view or API endpoint created to retrieve qualified customer list
- [ ] Phone number validation implemented
- [ ] Duplicate checking verified
- [ ] Format meets SMS dispatch system requirements
- [ ] 100+ customer test dataset validated
- [ ] API documentation created
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration test successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Create Database View/Query** (Estimated: 3 hours)
   - Join monthly_qualifications with customers and contact_info tables
   - Filter: is_qualified = true for current month
   - Include: customer_id, name, phone_number, qualification_date
   - Sort by customer_id for consistency

2. **Implement Phone Number Validation** (Estimated: 3 hours)
   - Validate phone number format (Israeli format: +972-X-XXXX-XXXX or similar)
   - Check for null/empty phone numbers
   - Flag invalid numbers separately
   - Create validation rules (length, format, allowed characters)

3. **Build API Endpoint/Method** (Estimated: 3 hours)
   - Create REST endpoint: GET /api/v1/qualified-customers/current-month
   - Response includes array of customer objects
   - Support pagination for large result sets
   - Add filtering options (by date, customer ID)
   - Implement caching for performance

4. **Handle Edge Cases** (Estimated: 2 hours)
   - Customers with missing phone numbers (flag for manual review)
   - Customers with multiple phone numbers (select primary)
   - Invalid phone number format (exclude or flag)
   - Ensure exactly one entry per customer

5. **Create Export Functionality** (Estimated: 2 hours)
   - Generate CSV export of qualified customers
   - Include all metadata fields
   - Support scheduled export to file
   - Format compatible with SMS carrier batch upload

6. **Write Comprehensive Tests** (Estimated: 3 hours)
   - Unit tests for phone validation
   - Test query returns correct customers
   - Test no duplicates
   - Integration test with 100+ customers

---

## Technical Considerations

**Architecture Impacts:**
- API endpoint or database view for SMS system access
- Phone number validation module
- Export file generation

**Database Changes:**

```sql
-- Create view for qualified customers with contact info
CREATE VIEW v_qualified_customers_current_month AS
SELECT 
    mq.customer_id,
    c.name,
    c.phone_number,
    c.email,
    mq.qualification_month,
    mq.qualifying_days,
    mq.total_calendar_days,
    mq.calculation_timestamp
FROM monthly_qualifications mq
INNER JOIN customers c ON mq.customer_id = c.customer_id
WHERE mq.is_qualified = TRUE
  AND MONTH(mq.qualification_month) = MONTH(CURDATE())
  AND YEAR(mq.qualification_month) = YEAR(CURDATE())
ORDER BY mq.customer_id;

-- Alternatively, create API method/query if using ORM
```

**Phone Number Validation (Pseudocode)**

```python
import re

def validate_israeli_phone(phone_number):
    """
    Validate Israeli phone number format
    Acceptable formats:
    - 0X-XXXX-XXXX (local)
    - +972-X-XXXX-XXXX (international)
    """
    if not phone_number:
        return False, "MISSING_PHONE"
    
    # Remove spaces and dashes for validation
    clean_phone = re.sub(r'[\s-]', '', str(phone_number))
    
    # Check local format: 0 followed by 9 digits
    if re.match(r'^0\d{9}$', clean_phone):
        return True, None
    
    # Check international format: +972 followed by 9 digits
    if re.match(r'^\+972\d{9}$', clean_phone):
        return True, None
    
    return False, "INVALID_FORMAT"

def validate_phone_list(customers):
    """Validate all customer phone numbers"""
    valid = []
    invalid = []
    
    for customer in customers:
        is_valid, error = validate_israeli_phone(customer['phone_number'])
        if is_valid:
            valid.append(customer)
        else:
            invalid.append({
                'customer_id': customer['customer_id'],
                'phone_number': customer['phone_number'],
                'error': error
            })
    
    return valid, invalid
```

**API Response Example**

```json
{
  "month": "2025-11",
  "total_qualified": 1250,
  "generated_at": "2025-12-01T00:30:00Z",
  "customers": [
    {
      "customer_id": "CUST001",
      "name": "David Cohen",
      "phone_number": "+972-2-1234-5678",
      "email": "david@example.com",
      "qualification_month": "2025-11-01",
      "qualifying_days": 30,
      "total_calendar_days": 30
    },
    {
      "customer_id": "CUST002",
      "name": "Sarah Levi",
      "phone_number": "054-9876543",
      "email": "sarah@example.com",
      "qualification_month": "2025-11-01",
      "qualifying_days": 30,
      "total_calendar_days": 30
    }
  ]
}
```

**CSV Export Format**

```
customer_id,name,phone_number,email,qualification_month,qualifying_days
CUST001,David Cohen,+972-2-1234-5678,david@example.com,2025-11-01,30
CUST002,Sarah Levi,054-9876543,sarah@example.com,2025-11-01,30
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| customer_id | String(50) | Yes | Unique identifier |
| name | String(200) | Yes | Customer's full name |
| phone_number | String(20) | Yes | Israeli phone format |
| email | String(255) | No | Valid email format |
| qualification_month | Date | Yes | Month of qualification |
| qualifying_days | Integer | Yes | Days meeting threshold |

---

## Testing Strategy

### Unit Tests
- Phone number validation:
  - Valid: "+972-2-1234-5678" ✓
  - Valid: "054-9876543" ✓
  - Invalid: "123" ✗
  - Invalid: null ✗
  - Invalid: "abc-def-ghij" ✗
- Duplicate detection
- Query returns correct month

### Integration Tests
- Query 100+ qualified customers
- Verify phone numbers are valid
- Test export to CSV
- API response contains all fields
- Pagination works with large dataset

### Manual Testing Scenarios
- Query current month qualified customers
- Export to CSV and verify format
- Test with various phone number formats
- Verify no duplicates in result
- Check API performance with large result set

### Acceptance Test Checklist
- [ ] All qualified customers returned
- [ ] Phone numbers validated
- [ ] No duplicates in list
- [ ] Metadata complete
- [ ] CSV export format correct
- [ ] API performance acceptable
- [ ] Invalid phone numbers flagged

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-2-1 (qualification calculation)
- Blocks: US-3-2 (SMS generation uses qualified list)

### External Dependencies
- None (uses internal data)

### Known Blockers
- None initially; verify US-2-1 complete before starting

---

## Documentation

### User Documentation
- API endpoint documentation
- Export format specification

### Technical Documentation
- Phone validation algorithm
- Database view/query specification
- API response schema

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 16 hours total
  - Backend development: 9 hours
  - Database: 2 hours
  - Testing: 3 hours
  - Documentation: 2 hours

**Complexity:** Low-Medium
**Risk Level:** Low

### Estimation Breakdown
- Database view/query: 3 hours
- Phone validation: 3 hours
- API endpoint: 3 hours
- Edge cases: 2 hours
- Export functionality: 2 hours
- Testing: 3 hours

---

## Notes & Comments

- Phone number format is important: Israeli numbers have specific requirements
- Customers without phone numbers should be flagged but not block SMS processing (operations team handles)
- Export capability useful for manual reconciliation and reporting

---

## Related Stories

- [US-2-1](./US-2-1.md) - Qualification calculation (predecessor)
- [US-2-3](./US-2-3.md) - Audit validation (parallel)
- [US-3-1](./epics/003-SMS-Notification-Dispatch/US-3-1.md) - SMS dispatch (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
