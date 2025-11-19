# User Story: Submit SMS batch to carrier

**Story ID:** US-3-3
**Epic:** [E-003: SMS Notification Generation & Delivery](./epic.md)
**Priority:** P0 (Critical)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 2-3
**Related BRD:** BR-3 (Carrier Integration)
**Related FSD:** Process 3 (Steps 4-7)

---

## User Story

**As the** SMS Notification System
**I want** to submit the SMS batch to the carrier for delivery
**So that** qualified customers receive their notification messages

---

## Acceptance Criteria

- [ ] **Carrier Connection:** Establishes secure connection to SMS carrier API/SFTP
- [ ] **Batch Submission:** Sends entire batch file to carrier
- [ ] **Confirmation Receipt:** Receives initial acceptance confirmation from carrier
- [ ] **Tracking IDs:** Captures carrier-provided batch ID and tracking information
- [ ] **Error Logging:** Any submission errors logged with details
- [ ] **Metadata Stored:** Submission details stored for audit (timestamp, batch ID, message count)
- [ ] **Completion Within Window:** Entire process completes within 2-hour window
- [ ] **Carrier Integration:** Successfully integrated with chosen SMS provider

### Definition of Done

This story is complete when:
- [ ] SMS carrier integration implemented (API or SFTP)
- [ ] Connection credentials configured securely
- [ ] Batch submission tested with carrier sandbox
- [ ] 1000+ message batch successfully submitted
- [ ] Carrier confirmation received and logged
- [ ] Submission metadata stored in database
- [ ] Error handling tested (carrier errors, network failures)
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests with actual carrier successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Implement Carrier API Integration** (Estimated: 4 hours)
   - Research SMS carrier API (Twilio, Vonage, local Israeli provider)
   - Implement authentication (API key, OAuth, etc.)
   - Create batch submission method
   - Parse carrier response
   - Handle carrier errors/exceptions

2. **Create Carrier Connection Management** (Estimated: 2 hours)
   - Implement connection pooling if needed
   - Handle connection timeouts
   - Implement retry logic for transient failures
   - Log all connection attempts

3. **Build Submission Logging** (Estimated: 2 hours)
   - Create submission_logs table
   - Log: batch_id, submission_time, message_count, carrier_batch_id
   - Track submission status (pending, confirmed, failed)
   - Enable audit trail queries

4. **Implement Response Handling** (Estimated: 2 hours)
   - Parse carrier response
   - Extract carrier batch ID and confirmation
   - Handle partial failures (some messages accepted, some rejected)
   - Log carrier-provided tracking information

5. **Create Error Handling** (Estimated: 1 hour)
   - Handle carrier API errors (rate limit, auth, validation)
   - Implement exponential backoff retry
   - Log detailed error information
   - Create alert for critical failures

6. **Write Tests** (Estimated: 3 hours)
   - Unit tests with mocked carrier API
   - Integration test with carrier sandbox
   - Test error scenarios
   - Test retry logic
   - Performance test

---

## Technical Considerations

**Carrier Integration Options**

| Provider | Method | Auth | Format |
|----------|--------|------|--------|
| Twilio | REST API | Bearer token | JSON |
| Vonage (Nexmo) | REST API | API key | JSON |
| Local Israeli | REST/SFTP | API key/credentials | CSV/JSON |

**API Integration Example (Pseudocode - Twilio)**

```python
import requests
import json

class SMSCarrierIntegration:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def submit_batch(self, messages):
        """Submit SMS batch to carrier"""
        try:
            payload = {
                'messages': messages,
                'source': 'PremiumNotification'
            }
            
            response = requests.post(
                f'{self.api_url}/messages/send-batch',
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'carrier_batch_id': result['batch_id'],
                    'message_count': result['accepted_count'],
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'success': False,
                    'error_code': response.status_code,
                    'error_message': response.text
                }
        
        except requests.Timeout:
            return {'success': False, 'error': 'TIMEOUT'}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}
```

**Database Schema**

```sql
CREATE TABLE sms_submission_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_date DATE NOT NULL,
  message_count INT NOT NULL,
  carrier_batch_id VARCHAR(100),
  submitted_at DATETIME NOT NULL,
  carrier_response VARCHAR(500),
  submission_status ENUM('PENDING', 'CONFIRMED', 'FAILED') DEFAULT 'PENDING',
  retry_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_batch_date (batch_date),
  INDEX idx_carrier_batch_id (carrier_batch_id)
);
```

**Submission Workflow**

1. Read SMS batch file (generated by US-3-2)
2. Connect to SMS carrier
3. Authenticate with API key
4. Submit batch with all messages
5. Receive confirmation with carrier batch ID
6. Log submission with tracking IDs
7. Store for SMS delivery tracking (E-004)

---

## Testing Strategy

### Unit Tests
- API connection initialization
- Payload formatting
- Response parsing
- Error code handling
- Retry logic

### Integration Tests
- Submit batch to carrier sandbox
- Verify carrier accepts batch
- Verify carrier batch ID received
- Verify logging stores details correctly
- Test with 1000+ messages

### Manual Testing Scenarios
- Submit test batch to sandbox
- Review carrier response
- Check submission logs
- Verify carrier batch ID
- Trace tracking information

### Acceptance Test Checklist
- [ ] Carrier API credentials configured
- [ ] Test batch successfully submitted
- [ ] Carrier confirmation received
- [ ] Submission logged with all details
- [ ] Carrier batch ID captured
- [ ] 1000+ message batch accepted
- [ ] Performance acceptable (< 2 hours)

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-3-2 (SMS batch generation)
- Blocks: US-4-1 (delivery tracking)

### External Dependencies
- **CRITICAL:** SMS carrier account and API credentials
- **CRITICAL:** Carrier API documentation
- **CRITICAL:** Carrier sandbox environment for testing

### Known Blockers
- SMS carrier account must be activated before development
- API credentials must be securely managed

**Blocker Resolution:** 
- Coordinate with operations/procurement for carrier account setup
- Request API documentation and sandbox access from carrier

---

## Security Considerations

- [ ] API credentials stored in vault/secrets manager (not in code)
- [ ] HTTPS/TLS required for all carrier communication
- [ ] No sensitive data (customer names) logged in submission details
- [ ] Batch ID tracking only (allows tracing without exposing messages)
- [ ] Rate limiting: respect carrier's submission limits
- [ ] Timeout: 30 seconds max for API calls

---

## Documentation

### Technical Documentation
- Carrier API integration guide
- Submission process flow diagram
- Error code reference
- API credentials management

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 14 hours
- Carrier API integration: 6 hours
- Connection management: 2 hours
- Error handling: 2 hours
- Testing: 3 hours
- Documentation: 1 hour

**Complexity:** Medium
**Risk Level:** Medium (carrier API dependency)

---

## Notes & Comments

- Carrier integration is critical path: must be completed before E-004
- SMS delivery depends on carrier reliability
- Rate limiting from carrier may affect submission timing
- Sandbox testing essential before production deployment

---

## Related Stories

- [US-3-2](./US-3-2.md) - Batch generation (predecessor)
- [US-3-4](./US-3-4.md) - Error handling (parallel)
- [US-4-1](./epics/004-SMS-Delivery-Tracking/US-4-1.md) - Delivery tracking (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
