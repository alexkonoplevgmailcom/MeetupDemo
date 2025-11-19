# User Story: Validate customer phone numbers

**Story ID:** US-3-1
**Epic:** [E-003: SMS Notification Generation & Delivery](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 2
**Related BRD:** BR-3 (Phone validation requirement)
**Related FSD:** Process 3 (Step 2-3), Feature 1 (Phone validation section)

---

## User Story

**As the** SMS Notification Dispatch System
**I want** to validate that customer phone numbers are properly formatted and deliverable
**So that** I don't waste SMS credits on invalid numbers and ensure messages reach customers

---

## Acceptance Criteria

- [ ] **Format Validation:** Israeli phone numbers validated for correct format
- [ ] **Null Check:** Missing phone numbers identified and flagged
- [ ] **Deliverability:** Numbers checked against carrier's accepted formats
- [ ] **Invalid Flagging:** Invalid numbers marked as "undeliverable" for manual review
- [ ] **100% Coverage:** All qualified customers' phone numbers validated
- [ ] **Error Reporting:** Invalid numbers logged with reason (too short, invalid characters, etc.)
- [ ] **Manual Escalation:** Operations team notified of invalid numbers for follow-up
- [ ] **Batch Purity:** Valid numbers passed to next step; invalid segregated for review

### Definition of Done

This story is complete when:
- [ ] Phone validation logic implemented
- [ ] Israeli phone format rules documented
- [ ] Invalid phone list exported for manual review
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests with 100+ customer sample
- [ ] Edge cases tested (null, empty, special chars)
- [ ] Manual escalation process tested
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Define Israeli Phone Format Rules** (Estimated: 2 hours)
   - Document acceptable formats:
     - Local: 05X-XXXX-XXXX (10 digits starting with 05)
     - International: +972-5X-XXXX-XXXX
   - Research carrier requirements
   - Create validation rule set
   - Document edge cases

2. **Implement Phone Validation** (Estimated: 3 hours)
   - Create validation function for each format
   - Normalize format (remove dashes, spaces)
   - Check length requirements (exactly 10 digits for local)
   - Validate allowed characters (0-9, +, -)
   - Return validation result with error code

3. **Create Invalid Number Handling** (Estimated: 2 hours)
   - Flag invalid numbers separately
   - Create detailed error codes (TOO_SHORT, INVALID_CHARS, NULL_VALUE, etc.)
   - Generate invalid phone number report
   - Log for operations team review

4. **Build Manual Escalation** (Estimated: 2 hours)
   - Create alert for invalid numbers
   - Generate report with customer details
   - Implement workflow for operations to update phone numbers
   - Track resolution of invalid numbers

5. **Write Tests** (Estimated: 2 hours)
   - Unit tests for all format variations
   - Test edge cases
   - Integration test with customer sample
   - Performance test with 1000+ records

---

## Technical Considerations

**Phone Formats (Israeli)**

| Format | Example | Notes |
|--------|---------|-------|
| Local | 054-1234-5678 | Mobile (05X series) |
| Local | 054 1234 5678 | Mobile with spaces |
| International | +972-54-1234-5678 | +972 replaces 0 |
| International | +972541234567 | No separators |

**Validation Logic (Pseudocode)**

```python
def validate_israeli_phone(phone_number):
    """Validate Israeli phone number"""
    
    if not phone_number or phone_number.strip() == "":
        return False, "NULL_VALUE"
    
    # Normalize: remove spaces and dashes
    clean = phone_number.replace(" ", "").replace("-", "")
    
    # Check local format (0 + 9 digits)
    if re.match(r'^0\d{9}$', clean):
        return True, None
    
    # Check international format (+972 + 9 digits)
    if re.match(r'^\+972\d{9}$', clean):
        return True, None
    
    # Check local format without leading 0 (for some carrier APIs)
    if re.match(r'^5[0-9]\d{7}$', clean):
        return True, None
    
    # Invalid
    if len(clean) < 9:
        return False, "TOO_SHORT"
    if len(clean) > 15:
        return False, "TOO_LONG"
    if not clean.replace("+", "").isdigit():
        return False, "INVALID_CHARACTERS"
    
    return False, "INVALID_FORMAT"

def validate_customer_phones(qualified_customers):
    """Validate all customer phone numbers"""
    valid = []
    invalid = []
    
    for customer in qualified_customers:
        is_valid, error_code = validate_israeli_phone(customer['phone_number'])
        
        if is_valid:
            valid.append(customer)
        else:
            invalid.append({
                'customer_id': customer['customer_id'],
                'phone_number': customer['phone_number'],
                'error_code': error_code,
                'customer_name': customer['name']
            })
    
    return valid, invalid
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| customer_id | String(50) | Yes | Unique ID |
| phone_number | String(20) | Yes | Israeli format |
| is_valid | Boolean | Yes | Validation result |
| error_code | String(50) | No | If invalid |
| error_message | String(255) | No | If invalid |

**Error Codes:**

| Code | Meaning | Action |
|------|---------|--------|
| NULL_VALUE | Phone number missing | Escalate to operations |
| TOO_SHORT | Less than 9 digits | Escalate to operations |
| TOO_LONG | More than 15 digits | Escalate to operations |
| INVALID_CHARACTERS | Non-numeric characters | Escalate to operations |
| INVALID_FORMAT | Doesn't match expected pattern | Escalate to operations |

---

## Testing Strategy

### Unit Tests
- Valid local format: "054-1234-5678" → Valid ✓
- Valid international: "+972-54-1234-5678" → Valid ✓
- Valid no separator: "0541234567" → Valid ✓
- Invalid too short: "054-123" → Error: TOO_SHORT ✗
- Invalid null: None/empty → Error: NULL_VALUE ✗
- Invalid chars: "054-ABCD-5678" → Error: INVALID_CHARACTERS ✗

### Integration Tests
- Validate 100+ customer phone numbers
- Check 20 valid numbers pass
- Check 5 invalid numbers flagged correctly
- Verify report generation
- Test alert to operations team

### Manual Testing Scenarios
- Run validation on test customer set
- Review invalid numbers report
- Verify each invalid number has error code
- Check alert notification
- Verify operations team receives report

### Acceptance Test Checklist
- [ ] All phone numbers validated
- [ ] Valid numbers = 95/100
- [ ] Invalid numbers = 5/100 with error codes
- [ ] Report generated and readable
- [ ] Operations team alert triggered
- [ ] Performance acceptable (< 5 seconds for 1000 numbers)

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-2-2 (qualified customer list)
- Blocks: US-3-2 (SMS generation uses validated list)

### External Dependencies
- Requires SMS carrier format specifications

---

## Documentation

### Technical Documentation
- Phone format specifications
- Validation rule reference
- Error code catalog

---

## Estimation & Effort

**Story Points:** 3
**Estimated Hours:** 11 hours total
- Backend development: 6 hours
- Testing: 3 hours
- Documentation: 2 hours

**Complexity:** Low
**Risk Level:** Low

---

## Related Stories

- [US-2-2](./epics/002-Monthly-Qualification/US-2-2.md) - Qualified customer list (predecessor)
- [US-3-2](./US-3-2.md) - SMS generation (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
