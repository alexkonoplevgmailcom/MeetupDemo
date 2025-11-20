# User Story: Distribute reports to stakeholders

**Story ID:** MEET1-5-4
**Epic:** [MEET1-5: Monthly Reporting & Analytics](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 5
**Related BRD:** BR-5 (Report Distribution)
**Related FSD:** Process 5 (Stakeholder distribution and communication)

---

## User Story

**As the** Notification System Administrator
**I want** to automatically distribute monthly reports to stakeholders
**So that** key business leaders receive timely performance insights

---

## Acceptance Criteria

- [ ] **Automated Distribution:** Reports sent automatically on schedule
- [ ] **Correct Recipients:** Reports sent to all configured stakeholders
- [ ] **Multiple Channels:** Support email and dashboard distribution
- [ ] **Professional Format:** Reports professionally formatted and branded
- [ ] **Delivery Confirmation:** Delivery status tracked
- [ ] **Retry Logic:** Failed sends retried
- [ ] **Archive:** Reports archived for historical reference
- [ ] **Audit Trail:** Distribution logged for compliance

### Definition of Done

This story is complete when:
- [ ] Distribution logic implemented
- [ ] Email delivery configured and tested
- [ ] Dashboard distribution working
- [ ] Stakeholder list management implemented
- [ ] Delivery tracking working
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Configure Stakeholder List** (Estimated: 1 hour)
   - Store stakeholder email addresses
   - Support role-based distribution
   - Enable/disable recipients
   - Track subscription preferences

2. **Implement Email Distribution** (Estimated: 2 hours)
   - Configure email service
   - Create email template
   - Attach report PDF/Excel
   - Send with retry logic

3. **Build Dashboard Distribution** (Estimated: 1 hour)
   - Upload report to dashboard
   - Make accessible to stakeholders
   - Version control for historical access

4. **Implement Delivery Tracking** (Estimated: 1 hour)
   - Track email open rates
   - Log delivery status
   - Record delivery failures

5. **Create Archive** (Estimated: 1 hour)
   - Store reports in accessible location
   - Enable historical access
   - Implement retention policy

6. **Write Tests** (Estimated: 1 hour)
   - Unit tests for distribution logic
   - Integration tests with email service
   - Delivery tracking tests

---

## Technical Considerations

**Distribution Channels**

| Channel | Details | Audience |
|---------|---------|----------|
| Email | PDF/Excel attachment | All stakeholders |
| Dashboard | Web-based access | Internal team |
| Archive | Historical storage | All stakeholders |

**Stakeholder Configuration**

```sql
CREATE TABLE stakeholder_subscriptions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stakeholder_id VARCHAR(100) NOT NULL,
  name VARCHAR(255),
  email VARCHAR(255),
  role VARCHAR(100),
  active BOOLEAN DEFAULT TRUE,
  receive_email BOOLEAN DEFAULT TRUE,
  receive_dashboard BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_active (active),
  INDEX idx_role (role)
);
```

**Distribution Logic (Pseudocode)**

```python
def distribute_monthly_report(month_year, report_file):
    """Distribute report to all stakeholders"""
    
    # Get list of active stakeholders
    stakeholders = query_active_stakeholders()
    
    distribution_results = []
    
    for stakeholder in stakeholders:
        result = {
            'stakeholder_id': stakeholder.id,
            'month': month_year,
            'channels': []
        }
        
        # Email distribution
        if stakeholder.receive_email:
            try:
                send_report_email(
                    to=stakeholder.email,
                    report_file=report_file,
                    stakeholder_name=stakeholder.name
                )
                result['channels'].append({
                    'channel': 'email',
                    'status': 'sent',
                    'sent_at': datetime.now()
                })
            except EmailError as e:
                result['channels'].append({
                    'channel': 'email',
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Dashboard distribution
        if stakeholder.receive_dashboard:
            try:
                upload_to_dashboard(
                    report_file=report_file,
                    stakeholder_id=stakeholder.id
                )
                result['channels'].append({
                    'channel': 'dashboard',
                    'status': 'available',
                    'uploaded_at': datetime.now()
                })
            except DashboardError as e:
                result['channels'].append({
                    'channel': 'dashboard',
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Store result
        store_distribution_result(result)
        distribution_results.append(result)
    
    # Archive report
    archive_report(report_file, month_year)
    
    return distribution_results

def send_report_email(to, report_file, stakeholder_name):
    """Send report via email"""
    
    email_subject = f'Premium Customer Notification Program - Monthly Report {month_year}'
    
    email_body = f"""
    Dear {stakeholder_name},
    
    Please find attached the monthly performance report for the Premium Customer Notification Program.
    
    Key Highlights:
    - Qualification Success Rate: {metrics['qualification_rate']}%
    - SMS Delivery Rate: {metrics['delivery_rate']}%
    - Total Customers: {metrics['total_customers']}
    
    For questions or access to the full dashboard, please contact the program team.
    
    Best regards,
    Premium Customer Notification System
    """
    
    email_service.send(
        to=to,
        subject=email_subject,
        body=email_body,
        attachments=[report_file],
        retry_count=3,
        retry_delay=300  # 5 minutes
    )
```

**Distribution Tracking**

```sql
CREATE TABLE report_distributions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  month_year VARCHAR(7),
  stakeholder_id VARCHAR(100),
  channel VARCHAR(50),  -- email, dashboard
  status VARCHAR(50),   -- sent, failed, pending
  sent_at DATETIME,
  opened_at DATETIME,
  error_message TEXT,
  retry_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_month_stakeholder (month_year, stakeholder_id),
  INDEX idx_status (status),
  INDEX idx_sent_at (sent_at)
);

CREATE TABLE report_archive (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  month_year VARCHAR(7),
  report_file_path VARCHAR(500),
  file_size BIGINT,
  format VARCHAR(50),  -- pdf, excel
  archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  retention_until DATETIME,
  UNIQUE KEY uk_month (month_year),
  INDEX idx_archived_at (archived_at)
);
```

---

## Testing Strategy

### Unit Tests
- Stakeholder query logic
- Email composition
- Distribution logic
- Retry mechanism

### Integration Tests
- Send emails to test addresses
- Upload to dashboard
- Track delivery status
- Archive functionality

### Manual Testing Scenarios
- Send test report to sample stakeholders
- Verify email delivery
- Check dashboard access
- Verify archive functionality

### Acceptance Test Checklist
- [ ] Stakeholders receive emails
- [ ] Reports accessible on dashboard
- [ ] Historical archive available
- [ ] Delivery status tracked
- [ ] Retries work correctly
- [ ] All stakeholders receive reports

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-5-2 (report generation)
- Blocks: None

### External Dependencies
- Requires email service (SMTP)
- Requires dashboard infrastructure

---

## Documentation

### User Documentation
- Stakeholder subscription guide
- Dashboard access instructions
- Report interpretation guide

### Technical Documentation
- Email configuration
- Distribution API
- Archive management

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

- [US-5-2](./US-5-2.md) - Report generation (predecessor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
