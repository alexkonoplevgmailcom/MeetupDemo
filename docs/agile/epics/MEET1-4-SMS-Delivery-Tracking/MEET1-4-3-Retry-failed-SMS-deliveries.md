# User Story: Retry failed SMS deliveries

**Story ID:** MEET1-4-3
**Epic:** [MEET1-4: SMS Delivery Tracking & Confirmation](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 3
**Related BRD:** BR-4 (Retry Logic)
**Related FSD:** Process 4 (Retry and resilience strategy)

---

## User Story

**As the** SMS Delivery System
**I want** to automatically retry failed message deliveries up to 2 times
**So that** temporary delivery failures don't result in permanently undelivered messages

---

## Acceptance Criteria

- [ ] **Retry Logic:** Failed messages automatically retried (max 2 retries)
- [ ] **Transient vs. Permanent:** Retry only for transient failures (not invalid numbers, auth errors)
- [ ] **Retry Timing:** Retries scheduled for next polling cycle (within 2-4 hours)
- [ ] **Attempt Tracking:** Retry count tracked for each message
- [ ] **Final Status:** Message marked final after 2 failed retries
- [ ] **Escalation:** Permanently failed messages escalated after retries exhausted
- [ ] **Logging:** All retry attempts logged with reasons
- [ ] **Success Recovery:** Successfully retried messages logged as delivered

### Definition of Done

This story is complete when:
- [ ] Retry logic implemented and tested
- [ ] Transient vs. permanent error classification working
- [ ] Retry scheduling working
- [ ] 1000+ message retry scenarios tested
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Transient Error Detection** (Estimated: 2 hours)
   - Classify error types
   - Create retry decision logic
   - Document retry criteria

2. **Build Retry Scheduler** (Estimated: 2 hours)
   - Schedule retries for next polling cycle
   - Track retry attempts
   - Update delivery status

3. **Create Retry Tracking** (Estimated: 1 hour)
   - Add retry_count to delivery log
   - Track retry history
   - Log retry decisions

4. **Implement Success Recovery** (Estimated: 1 hour)
   - Handle successful retry outcomes
   - Update delivery status to delivered
   - Log successful retry

5. **Write Tests** (Estimated: 2 hours)
   - Unit tests for retry logic
   - Integration tests with full workflow
   - Error classification tests

---

## Technical Considerations

**Error Classification for Retries**

| Failure Type | Retry? | Reason |
|-------------|--------|--------|
| Timeout | Yes | Transient network issue |
| Rate limit | Yes | Transient carrier issue |
| Service error | Yes | Transient carrier issue |
| Invalid number | No | Permanent - wrong number |
| Auth failed | No | Permanent - credentials issue |
| Blocked | No | Permanent - number blocked |

**Retry Logic (Pseudocode)**

```python
def should_retry_delivery(failure_code, current_retry_count):
    """Determine if message should be retried"""
    
    max_retries = 2
    if current_retry_count >= max_retries:
        return False  # Max retries exhausted
    
    transient_errors = ['TIMEOUT', 'RATE_LIMIT', 'SERVICE_ERROR', 'CONNECT_FAIL']
    return failure_code in transient_errors

def schedule_retry(tracking_id, delivery_status, failure_code):
    """Schedule retry for next polling cycle"""
    
    if not should_retry_delivery(failure_code, current_retry_count):
        return None
    
    # Get current retry count
    delivery_log = query_delivery_log(tracking_id)
    next_retry_count = delivery_log.retry_count + 1
    
    # Schedule for next polling cycle (in 2 hours)
    next_retry_time = datetime.now() + timedelta(hours=2)
    
    # Update delivery log
    update_delivery_log(
        tracking_id=tracking_id,
        retry_count=next_retry_count,
        next_retry_at=next_retry_time,
        delivery_status='RETRY_SCHEDULED'
    )
    
    return next_retry_time
```

**Database Updates**

```sql
-- Add retry tracking columns if not already present
ALTER TABLE sms_delivery_log ADD COLUMN (
  retry_count INT DEFAULT 0,
  next_retry_at DATETIME,
  original_failure_code VARCHAR(50)
);
```

---

## Testing Strategy

### Unit Tests
- Transient error detection
- Retry decision logic
- Max retry enforcement
- Retry scheduling

### Integration Tests
- End-to-end retry workflow
- Retry success scenarios
- Retry exhaustion scenarios
- Verify final status updates

### Manual Testing Scenarios
- Inject failure to trigger retry
- Monitor retry scheduling
- Verify successful retry
- Check retry logs

### Acceptance Test Checklist
- [ ] Transient failures retried
- [ ] Permanent failures not retried
- [ ] Max 2 retries enforced
- [ ] Retry scheduled correctly
- [ ] Retry attempts logged
- [ ] Successful retry marked as delivered

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-4-2 (delivery logging)
- Blocks: US-4-4 (escalation)

### External Dependencies
- None

---

## Documentation

### Technical Documentation
- Error classification reference
- Retry policy documentation

---

## Estimation & Effort

**Story Points:** 3
**Estimated Hours:** 8 hours
- Backend: 5 hours
- Testing: 2 hours
- Documentation: 1 hour

**Complexity:** Low-Medium
**Risk Level:** Low

---

## Related Stories

- [US-4-2](./US-4-2.md) - Delivery logging (predecessor)
- [US-4-4](./US-4-4.md) - Escalation (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
