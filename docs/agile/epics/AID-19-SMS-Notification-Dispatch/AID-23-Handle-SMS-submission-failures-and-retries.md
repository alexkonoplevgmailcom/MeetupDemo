# User Story: Handle SMS submission failures and retries

**Story ID:** US-3-4
**Epic:** [E-003: SMS Notification Generation & Delivery](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 3
**Related BRD:** BR-3 (Error handling)
**Related FSD:** Process 3 (Exception Handling)

---

## User Story

**As a** System Operator
**I want** the SMS submission process to automatically retry failed submissions and alert me of persistent failures
**So that** temporary carrier issues don't prevent message delivery and I can intervene for critical failures

---

## Acceptance Criteria

- [ ] **Automatic Retry:** Failed submissions retry up to 3 times with exponential backoff
- [ ] **Retry Delays:** 5 minutes, 10 minutes, 20 minutes between attempts
- [ ] **Error Logging:** Each retry logged with timestamp, error details, attempt number
- [ ] **Carrier Error Categorization:** Different handling for transient vs. permanent errors
- [ ] **Alert on Failure:** Operations team alerted after 3 failed attempts
- [ ] **Manual Intervention:** Failed batch available for manual resubmission
- [ ] **Batch Status Tracking:** Each batch tracked through submission attempts
- [ ] **Success Confirmation:** Successful submission confirmed (carrier accepted batch)

### Definition of Done

This story is complete when:
- [ ] Retry logic implemented with exponential backoff
- [ ] Error categorization implemented
- [ ] Alert mechanism tested and operational
- [ ] Batch status tracking implemented
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration test with simulated carrier errors
- [ ] Manual resubmission process tested
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Retry Logic** (Estimated: 3 hours)
   - Create retry scheduler (cron or job queue)
   - Implement exponential backoff (5s, 10s, 20s)
   - Track retry attempts
   - Stop after 3 failed attempts

2. **Categorize Errors** (Estimated: 2 hours)
   - Transient errors: retry (timeout, rate limit, temporary outage)
   - Permanent errors: don't retry (auth failed, invalid format, etc.)
   - Create error code mapping
   - Document error handling strategy

3. **Create Alert System** (Estimated: 2 hours)
   - Alert after final failure
   - Include error details in alert
   - Send to operations team
   - Log alert event

4. **Implement Batch Status Tracking** (Estimated: 2 hours)
   - Track batch through submission attempts
   - Update status: pending → confirmed or pending → failed
   - Enable query by status
   - Store attempt history

5. **Build Manual Resubmission** (Estimated: 1 hour)
   - Create API endpoint to resubmit failed batch
   - Reset retry counter
   - Log manual resubmission
   - Allow operations team to retry

6. **Write Tests** (Estimated: 2 hours)
   - Unit tests for retry logic
   - Test error categorization
   - Integration test with simulated failures
   - Test alert triggering

---

## Technical Considerations

**Error Categorization**

| Error Code | Type | Action |
|-----------|------|--------|
| TIMEOUT | Transient | Retry |
| RATE_LIMIT | Transient | Retry with backoff |
| SERVICE_UNAVAILABLE | Transient | Retry |
| AUTH_FAILED | Permanent | Alert, don't retry |
| INVALID_FORMAT | Permanent | Alert, don't retry |
| BATCH_REJECTED | Permanent | Alert, don't retry |

**Retry Logic (Pseudocode)**

```python
def submit_with_retry(batch_id, max_retries=3):
    """Submit batch with automatic retry on failure"""
    retry_delays = [300, 600, 1200]  # 5, 10, 20 minutes in seconds
    
    for attempt in range(max_retries):
        try:
            result = carrier.submit_batch(batch_id)
            if result['success']:
                log_submission_success(batch_id, result)
                update_batch_status(batch_id, 'CONFIRMED')
                return True
            else:
                error_code = result['error_code']
                if is_transient_error(error_code):
                    if attempt < max_retries - 1:
                        log_retry_attempt(batch_id, attempt + 1, error_code)
                        sleep(retry_delays[attempt])
                        continue
                    else:
                        log_final_failure(batch_id, error_code)
                        alert_operations(batch_id, error_code)
                        update_batch_status(batch_id, 'FAILED')
                        return False
                else:
                    # Permanent error - don't retry
                    log_permanent_failure(batch_id, error_code)
                    alert_operations(batch_id, error_code)
                    update_batch_status(batch_id, 'FAILED')
                    return False
        
        except Exception as e:
            error_code = categorize_exception(e)
            if attempt < max_retries - 1:
                log_retry_attempt(batch_id, attempt + 1, error_code)
                sleep(retry_delays[attempt])
            else:
                alert_operations(batch_id, error_code)
                update_batch_status(batch_id, 'FAILED')
                return False
```

**Database Schema**

```sql
ALTER TABLE sms_submission_logs ADD COLUMN (
  submission_status ENUM('PENDING', 'CONFIRMED', 'FAILED') DEFAULT 'PENDING',
  current_retry_attempt INT DEFAULT 0,
  last_error_code VARCHAR(50),
  last_error_message TEXT,
  next_retry_at DATETIME
);

CREATE TABLE sms_submission_attempts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_id BIGINT NOT NULL,
  attempt_number INT NOT NULL,
  attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  error_code VARCHAR(50),
  error_message TEXT,
  carrier_response VARCHAR(500),
  next_retry_at DATETIME,
  INDEX idx_batch_id (batch_id),
  FOREIGN KEY (batch_id) REFERENCES sms_submission_logs(id)
);
```

---

## Testing Strategy

### Unit Tests
- Retry logic with various error types
- Exponential backoff timing
- Error categorization
- Alert triggering conditions
- Manual resubmission

### Integration Tests
- Simulate carrier timeout
- Simulate rate limit error
- Simulate auth failure
- Verify retry attempts
- Verify alert sent after failures
- Verify successful retry

### Manual Testing Scenarios
- Configure carrier to fail first submission
- Observe automatic retry
- Check retry logs
- Verify alert received
- Test manual resubmission
- Verify eventual success

### Acceptance Test Checklist
- [ ] Retry attempted 3 times
- [ ] Delays: 5min, 10min, 20min
- [ ] Transient errors retried
- [ ] Permanent errors stop retry
- [ ] Alert sent after 3 failures
- [ ] Manual resubmission works
- [ ] Batch status tracked correctly

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-3-3 (carrier submission)
- Blocks: None (runs in parallel)

### External Dependencies
- Requires SMS carrier error responses to be well-documented

---

## Documentation

### Technical Documentation
- Error code reference
- Retry policy documentation
- Alert configuration guide

---

## Estimation & Effort

**Story Points:** 3
**Estimated Hours:** 12 hours
- Backend: 7 hours
- Testing: 3 hours
- Documentation: 2 hours

**Complexity:** Medium
**Risk Level:** Low

---

## Related Stories

- [US-3-3](./US-3-3.md) - Carrier submission (predecessor)
- [US-4-1](./epics/004-SMS-Delivery-Tracking/US-4-1.md) - Delivery tracking (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
