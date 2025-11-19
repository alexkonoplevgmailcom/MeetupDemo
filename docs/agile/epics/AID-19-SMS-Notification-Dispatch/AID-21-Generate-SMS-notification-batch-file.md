# User Story: Generate SMS notification batch file

**Story ID:** US-3-2
**Epic:** [E-003: SMS Notification Generation & Delivery](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 2
**Related BRD:** BR-3 (SMS Message Content)
**Related FSD:** Process 3 (SMS generation)

---

## User Story

**As the** SMS Notification System
**I want** to generate SMS notification messages for all qualified customers and format them for carrier submission
**So that** customers receive personalized congratulations messages on their premium status

---

## Acceptance Criteria

- [ ] **Message Generation:** SMS created for each qualified customer with personalization
- [ ] **Personalization:** Customer name included in message
- [ ] **Content Consistency:** All messages follow approved template
- [ ] **Batch Formatting:** Messages formatted according to carrier requirements
- [ ] **Metadata:** Each SMS includes tracking ID, customer ID, timestamp
- [ ] **File Format:** Batch exported in carrier-compatible format (CSV/JSON/XML as required)
- [ ] **Message Length:** SMS fits within SMS character limits (160 chars typical)
- [ ] **Compliance:** Message includes required opt-out/compliance language

### Definition of Done

This story is complete when:
- [ ] SMS message template created and approved
- [ ] Personalization logic implemented
- [ ] Batch file generation implemented
- [ ] Format validated against carrier spec
- [ ] 1000+ message batch generated successfully
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Create SMS Message Template** (Estimated: 2 hours)
   - Design message content (business-approved text)
   - Include: greeting, month reference, call-to-action
   - Ensure fits in 160 character SMS limit
   - Include opt-out language
   - Test with various name lengths

2. **Implement Personalization** (Estimated: 2 hours)
   - Replace placeholder with customer name
   - Handle name length variations
   - Handle special characters in names
   - Create fallback if name too long (use ID)

3. **Build Batch File Generator** (Estimated: 3 hours)
   - Format messages per carrier spec
   - Add tracking ID and metadata
   - Support multiple file formats (CSV, JSON)
   - Handle large batches (1000+)
   - Create file with timestamp

4. **Implement Message Validation** (Estimated: 2 hours)
   - Verify each message ≤ 160 characters
   - Validate special characters allowed
   - Check for required compliance language
   - Log any messages that don't meet requirements

5. **Write Tests** (Estimated: 2 hours)
   - Unit tests for message generation
   - Test personalization logic
   - Test batch file format
   - Integration test with 1000+ messages
   - Performance test

---

## Technical Considerations

**Message Template**

Proposed template (to be approved by business):
```
Hi {CUSTOMER_NAME}, thanks for your loyalty! You've maintained premium status 
throughout {MONTH}. Learn about exclusive benefits at [link]. Reply STOP to opt-out.
```

Character count: ~140 (fits in single SMS)

Alternative template options should be documented.

**Batch File Format Examples**

CSV Format:
```
customer_id,phone_number,message,tracking_id,scheduled_send_time
CUST001,0541234567,Hi David! Thanks for...,TRK001,2025-12-01T09:00:00Z
CUST002,0549876543,Hi Sarah! Thanks for...,TRK002,2025-12-01T09:00:00Z
```

JSON Format:
```json
{
  "batch_id": "BATCH_202512_001",
  "submission_timestamp": "2025-12-01T08:00:00Z",
  "messages": [
    {
      "tracking_id": "TRK001",
      "customer_id": "CUST001",
      "phone_number": "0541234567",
      "message": "Hi David! Thanks for..."
    }
  ]
}
```

**Message Generation Logic (Pseudocode)**

```python
def generate_sms_batch(qualified_customers, batch_date):
    """Generate SMS batch for all qualified customers"""
    
    SMS_TEMPLATE = "Hi {NAME}, thanks for your loyalty! Maintained premium status throughout {MONTH}. Stop reply."
    MAX_SMS_LENGTH = 160
    
    messages = []
    tracking_id_counter = 1
    
    for customer in qualified_customers:
        # Personalize message
        customer_name = truncate_name(customer['name'], max_length=20)
        month_name = format_month(batch_date)  # "November"
        
        message = SMS_TEMPLATE.format(
            NAME=customer_name,
            MONTH=month_name
        )
        
        # Validate length
        if len(message) > MAX_SMS_LENGTH:
            log_warning(f"Message too long for {customer['customer_id']}, truncating")
            message = message[:MAX_SMS_LENGTH]
        
        # Create tracking ID
        tracking_id = f"TRK{batch_date.strftime('%Y%m%d')}{tracking_id_counter:06d}"
        tracking_id_counter += 1
        
        messages.append({
            'tracking_id': tracking_id,
            'customer_id': customer['customer_id'],
            'phone_number': customer['phone_number'],
            'message': message,
            'scheduled_send_time': batch_date.isoformat() + "Z"
        })
    
    return messages

def export_batch_to_csv(messages, output_file):
    """Export batch to CSV format"""
    import csv
    
    fieldnames = ['customer_id', 'phone_number', 'message', 'tracking_id', 'scheduled_send_time']
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for msg in messages:
            writer.writerow({
                'customer_id': msg['customer_id'],
                'phone_number': msg['phone_number'],
                'message': msg['message'],
                'tracking_id': msg['tracking_id'],
                'scheduled_send_time': msg['scheduled_send_time']
            })
```

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| tracking_id | String | Yes | Unique per message |
| customer_id | String(50) | Yes | From qualified list |
| phone_number | String(20) | Yes | Pre-validated |
| message | String(160) | Yes | ≤ 160 characters |
| scheduled_send_time | DateTime | Yes | ISO format |

---

## Testing Strategy

### Unit Tests
- Message personalization with various names
- Message length validation
- Tracking ID generation
- CSV file format
- JSON file format

### Integration Tests
- Generate batch for 100+ customers
- Verify all messages in batch
- Check CSV/JSON format validity
- Verify tracking ID uniqueness
- Performance test (1000+ messages)

### Manual Testing Scenarios
- Generate test batch
- Review sample messages
- Check file format
- Validate message content
- Spot-check personalization

### Acceptance Test Checklist
- [ ] 1000 messages generated
- [ ] All messages ≤ 160 chars
- [ ] Names personalized correctly
- [ ] Tracking IDs unique
- [ ] CSV/JSON format valid
- [ ] File generated successfully

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-3-1 (phone validation)
- Blocks: US-3-3 (carrier submission)

### External Dependencies
- Requires SMS carrier format specification

---

## Documentation

### Technical Documentation
- Message template specification
- Batch file format reference
- Tracking ID generation rules

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 11 hours
- Backend: 7 hours
- Testing: 3 hours
- Documentation: 1 hour

**Complexity:** Low-Medium
**Risk Level:** Low

---

## Related Stories

- [US-3-1](./US-3-1.md) - Phone validation (predecessor)
- [US-3-3](./US-3-3.md) - Carrier submission (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
