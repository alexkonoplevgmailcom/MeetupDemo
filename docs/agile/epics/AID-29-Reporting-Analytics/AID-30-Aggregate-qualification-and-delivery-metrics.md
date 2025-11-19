# User Story: Aggregate qualification and delivery metrics

**Story ID:** US-5-1
**Epic:** [E-005: Monthly Reporting & Analytics](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 5
**Sprint:** Sprint 4
**Related BRD:** BR-5 (Metrics Aggregation)
**Related FSD:** Process 5 (Data aggregation and analysis)

---

## User Story

**As a** Business Analyst
**I want** to aggregate qualification and SMS delivery metrics from all program data
**So that** comprehensive reporting can analyze overall program performance

---

## Acceptance Criteria

- [ ] **Data Aggregation:** All monthly data collected and aggregated
- [ ] **Accuracy:** Aggregation results verified against source data
- [ ] **Completeness:** 100% of qualifying customers included
- [ ] **Consolidation:** Delivery metrics consolidated by status
- [ ] **Trending:** Month-over-month data available for comparison
- [ ] **Performance:** Aggregation completes in < 1 hour
- [ ] **Audit Trail:** All aggregation queries logged
- [ ] **Data Validation:** Quality checks performed on aggregated data

### Definition of Done

This story is complete when:
- [ ] Aggregation logic implemented and tested
- [ ] Query performance optimized
- [ ] 1000+ records aggregated successfully
- [ ] Accuracy verified with spot checks
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Design Aggregation Queries** (Estimated: 2 hours)
   - Qualification metrics (qualified customers, success rate)
   - SMS delivery metrics (sent, delivered, failed)
   - Customer engagement metrics
   - Month-over-month deltas

2. **Implement Data Collection** (Estimated: 2 hours)
   - Query daily balance logs
   - Query qualification results
   - Query SMS delivery log
   - Join related data

3. **Build Consolidation Logic** (Estimated: 2 hours)
   - Consolidate by metric type
   - Remove duplicates
   - Calculate aggregates

4. **Implement Validation** (Estimated: 1 hour)
   - Quality checks on aggregated data
   - Consistency validation
   - Missing data detection

5. **Create Aggregation Report** (Estimated: 1 hour)
   - Format aggregated data
   - Include source record counts
   - Enable export for downstream reporting

6. **Write Tests** (Estimated: 1 hour)
   - Unit tests for aggregation logic
   - Integration tests with real data
   - Accuracy validation tests

---

## Technical Considerations

**Metrics to Aggregate**

```
Qualification Metrics:
- Total customers processed
- Customers qualified
- Customers disqualified
- Qualification success rate %
- Month-over-month change

SMS Delivery Metrics:
- Total SMS sent
- SMS delivered
- SMS failed
- Delivery success rate %
- Failure categories breakdown

Customer Engagement:
- Active customers
- Repeat qualifications
- Engagement rate
```

**Aggregation Queries (SQL Examples)**

```sql
-- Qualification Aggregation
SELECT
  DATE_FORMAT(qualification_date, '%Y-%m') as month,
  COUNT(DISTINCT customer_id) as total_customers,
  SUM(CASE WHEN status = 'QUALIFIED' THEN 1 ELSE 0 END) as qualified,
  SUM(CASE WHEN status = 'DISQUALIFIED' THEN 1 ELSE 0 END) as disqualified,
  ROUND(SUM(CASE WHEN status = 'QUALIFIED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as qualification_rate
FROM qualifications
GROUP BY DATE_FORMAT(qualification_date, '%Y-%m')
ORDER BY month DESC;

-- SMS Delivery Aggregation
SELECT
  DATE_FORMAT(polled_at, '%Y-%m') as month,
  COUNT(*) as total_sms,
  SUM(CASE WHEN delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) as delivered,
  SUM(CASE WHEN delivery_status = 'FAILED' THEN 1 ELSE 0 END) as failed,
  ROUND(SUM(CASE WHEN delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as delivery_rate
FROM sms_delivery_log
GROUP BY DATE_FORMAT(polled_at, '%Y-%m')
ORDER BY month DESC;

-- Failure Category Breakdown
SELECT
  failure_category,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sms_delivery_log WHERE delivery_status = 'FAILED'), 2) as pct
FROM sms_delivery_log
WHERE delivery_status = 'FAILED'
GROUP BY failure_category
ORDER BY count DESC;
```

**Aggregation Logic (Pseudocode)**

```python
def aggregate_monthly_metrics(month_year):
    """Aggregate all metrics for a specific month"""
    
    # Qualification Metrics
    qualification_metrics = {
        'total_customers': count_customers(month_year),
        'qualified': count_qualified(month_year),
        'disqualified': count_disqualified(month_year),
        'qualification_rate': calculate_qualification_rate(month_year)
    }
    
    # SMS Delivery Metrics
    sms_metrics = {
        'total_sent': count_sms_sent(month_year),
        'delivered': count_sms_delivered(month_year),
        'failed': count_sms_failed(month_year),
        'delivery_rate': calculate_delivery_rate(month_year),
        'failure_breakdown': get_failure_breakdown(month_year)
    }
    
    # Engagement Metrics
    engagement_metrics = {
        'active_customers': count_active_customers(month_year),
        'repeat_qualifications': count_repeat_qualifications(month_year),
        'engagement_rate': calculate_engagement_rate(month_year)
    }
    
    # Combine
    aggregated = {
        'month': month_year,
        'qualification': qualification_metrics,
        'sms_delivery': sms_metrics,
        'engagement': engagement_metrics,
        'aggregated_at': datetime.now()
    }
    
    # Validate
    validate_aggregation(aggregated)
    
    # Store
    store_aggregation(aggregated)
    
    return aggregated
```

**Data Validation Rules**

| Validation | Rule | Action |
|-----------|------|--------|
| Completeness | 100% of records present | Alert if < 100% |
| Consistency | Delivered + Failed ≤ Total Sent | Flag inconsistencies |
| Reasonableness | Delivery rate 80-99% | Alert if outside range |
| Duplication | No duplicate records | Remove duplicates |

---

## Testing Strategy

### Unit Tests
- Aggregation query correctness
- Metric calculation accuracy
- Validation logic
- Month filtering

### Integration Tests
- Aggregate 1000+ records
- Verify accuracy against source data
- Test month-over-month comparison
- Spot-check multiple months

### Manual Testing Scenarios
- Review aggregated metrics
- Verify calculations
- Compare with source data
- Check performance

### Acceptance Test Checklist
- [ ] All metrics aggregated correctly
- [ ] Accuracy verified with spot checks
- [ ] Performance <1 hour
- [ ] 1000+ records processed
- [ ] Month-over-month data available
- [ ] Validation rules applied

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-4-2 (delivery logging)
- Blocks: US-5-2 (report generation)

### External Dependencies
- None

---

## Documentation

### Technical Documentation
- Aggregation query reference
- Metric definitions
- Validation rules

---

## Estimation & Effort

**Story Points:** 5
**Estimated Hours:** 10 hours
- Backend: 6 hours
- Testing: 3 hours
- Documentation: 1 hour

**Complexity:** Medium
**Risk Level:** Low

---

## Related Stories

- [US-4-2](./epics/004-SMS-Delivery-Tracking/US-4-2.md) - Delivery logging (predecessor)
- [US-5-2](./US-5-2.md) - Report generation (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
