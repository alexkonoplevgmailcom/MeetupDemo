# User Story: Poll SMS carrier for delivery confirmations

**Story ID:** MEET1-4-1
**Epic:** [MEET1-4: SMS Delivery Tracking & Confirmation](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 3
**Related BRD:** BR-4 (Delivery Tracking)
**Related FSD:** Process 4 (Steps 1-2), Delivery confirmation section

---

## User Story

**As the** Premium Customer Notification System
**I want** to periodically query the SMS carrier for delivery confirmations of sent messages
**So that** I can track which messages were successfully delivered and which failed

---

## Acceptance Criteria

- [ ] **Polling Schedule:** Carrier queried every 2 hours for 72 hours after SMS submission
- [ ] **Complete Data:** Queries retrieve status for all sent messages
- [ ] **Status Capture:** Delivery status stored (Delivered / Failed / Pending)
- [ ] **Failure Codes:** Failure reasons captured for analysis
- [ ] **Tracking Continuity:** Each message tracked from submission through final confirmation
- [ ] **Database Logging:** All polling results logged for audit
- [ ] **Performance:** Each polling cycle completes within 15 minutes
- [ ] **Reliability:** Polling continues on schedule even if individual messages fail

### Definition of Done

This story is complete when:
- [ ] Polling logic implemented and scheduled
- [ ] SMS carrier API query working
- [ ] Results parsed and stored in database
- [ ] 1000+ message delivery tracking tested
- [ ] Polling scheduler running reliably
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Polling Scheduler** (Estimated: 2 hours)
   - Create scheduled job for every 2 hours
   - Query messages submitted within last 72 hours
   - Handle job failures gracefully
   - Logging for each poll cycle

2. **Build Carrier API Query** (Estimated: 3 hours)
   - Connect to SMS carrier status API
   - Query by batch ID or tracking ID
   - Parse carrier response
   - Handle API errors and retries

3. **Create Status Processing** (Estimated: 2 hours)
   - Process carrier status codes
   - Map to standard statuses (Delivered/Failed/Pending)
   - Extract failure codes/reasons
   - Update database with results

4. **Implement Results Logging** (Estimated: 2 hours)
   - Create delivery_confirmations table
   - Log each poll result
   - Store timestamp and status
   - Enable historical queries

5. **Build Monitoring** (Estimated: 1 hour)
   - Monitor polling success rate
   - Alert if polling fails
   - Log polling metrics

6. **Write Tests** (Estimated: 2 hours)
   - Unit tests for polling logic
   - Integration tests with carrier sandbox
   - Test error scenarios

---

## Technical Considerations

**Polling Schedule**

```
Submission: 2025-12-01 09:00:00
Poll 1: 2025-12-01 11:00:00  (+2h)
Poll 2: 2025-12-01 13:00:00  (+4h)
Poll 3: 2025-12-01 15:00:00  (+6h)
...
Poll 36: 2025-12-04 09:00:00 (+72h)
Stop: Polling ends after 72 hours
```

**Database Schema**

```sql
CREATE TABLE sms_delivery_confirmations (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tracking_id VARCHAR(100) NOT NULL,
  customer_id VARCHAR(50),
  phone_number VARCHAR(20),
  carrier_batch_id VARCHAR(100),
  delivery_status ENUM('DELIVERED', 'FAILED', 'PENDING') NOT NULL,
  failure_code VARCHAR(50),
  failure_reason VARCHAR(255),
  polled_at DATETIME NOT NULL,
  delivery_confirmed_at DATETIME,
  poll_attempt INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_tracking_id (tracking_id),
  INDEX idx_polled_at (polled_at),
  INDEX idx_status (delivery_status)
);
```

**Polling Logic (Pseudocode)**

```python
def poll_delivery_status():
    """Poll carrier for delivery status on all recent messages"""
    
    # Find all messages submitted in last 72 hours
    cutoff_time = datetime.now() - timedelta(hours=72)
    recent_submissions = query_submissions(submitted_after=cutoff_time)
    
    poll_results = []
    
    for submission_batch in recent_submissions:
        try:
            # Query carrier for this batch
            carrier_results = carrier_api.get_batch_status(
                batch_id=submission_batch.carrier_batch_id
            )
            
            # Process each message status
            for message_status in carrier_results:
                delivery_record = {
                    'tracking_id': message_status['tracking_id'],
                    'delivery_status': map_carrier_status(message_status['status']),
                    'failure_code': message_status.get('error_code'),
                    'failure_reason': message_status.get('error_message'),
                    'polled_at': datetime.now()
                }
                
                # Store in database
                store_delivery_confirmation(delivery_record)
                poll_results.append(delivery_record)
        
        except CarrierAPIError as e:
            log_polling_error(submission_batch.id, str(e))
            continue
    
    return poll_results

def map_carrier_status(carrier_status):
    """Map carrier status codes to standard statuses"""
    mapping = {
        'DELIVERED': 'DELIVERED',
        'FAILED': 'FAILED',
        'PENDING': 'PENDING',
        'QUEUED': 'PENDING',
        'REJECTED': 'FAILED',
        'TIMEOUT': 'FAILED'
    }
    return mapping.get(carrier_status, 'PENDING')
```

**Carrier Status Codes (Example)**

| Carrier Code | Meaning | Standard Status |
|-------------|---------|-----------------|
| DELIVERED | Message delivered | DELIVERED |
| FAILED | Delivery failed | FAILED |
| REJECTED | Invalid number | FAILED |
| TIMEOUT | No delivery confirmation | PENDING |
| QUEUED | In carrier queue | PENDING |
| BOUNCED | Invalid number | FAILED |

---

## Testing Strategy

### Unit Tests
- Polling scheduler timing
- Status code mapping
- Error handling
- Result processing

### Integration Tests
- Poll carrier sandbox for 100+ messages
- Verify all statuses captured
- Check database logging
- Test polling schedule reliability

### Manual Testing Scenarios
- Monitor polling cycle
- Check carrier response times
- Verify database updates
- Review polling logs

### Acceptance Test Checklist
- [ ] Polling executes every 2 hours
- [ ] All 1000+ messages queried
- [ ] Statuses captured correctly
- [ ] Database logging complete
- [ ] Polling completes within 15 minutes
- [ ] Errors handled gracefully

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-3-3 (carrier batch IDs)
- Blocks: US-4-2 (delivery logging)

### External Dependencies
- **CRITICAL:** SMS carrier delivery status API available

---

## Documentation

### Technical Documentation
- Polling schedule specification
- Carrier API documentation
- Status code reference

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 12 hours
- Backend: 7 hours
- Testing: 4 hours
- Documentation: 1 hour

**Complexity:** Medium
**Risk Level:** Medium (carrier API dependency)

---

## Related Stories

- [US-3-3](./epics/003-SMS-Notification-Dispatch/US-3-3.md) - SMS submission (predecessor)
- [US-4-2](./US-4-2.md) - Delivery logging (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
