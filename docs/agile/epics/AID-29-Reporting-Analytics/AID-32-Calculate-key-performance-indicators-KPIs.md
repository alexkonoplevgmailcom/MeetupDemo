# User Story: Calculate key performance indicators (KPIs)

**Story ID:** US-5-3
**Epic:** [E-005: Monthly Reporting & Analytics](./epic.md)
**Priority:** P1 (High)
**Status:** Not Started
**Story Points:** 3
**Sprint:** Sprint 4
**Related BRD:** BR-5 (KPI Tracking)
**Related FSD:** Process 5 (Key performance indicators)

---

## User Story

**As a** Program Manager
**I want** to track key performance indicators (KPIs) for the notification program
**So that** I can measure program health and report on strategic objectives

---

## Acceptance Criteria

- [ ] **KPI Definition:** All KPIs clearly defined and measured
- [ ] **Accuracy:** KPIs calculated correctly from source data
- [ ] **Trending:** KPIs tracked and trended month-over-month
- [ ] **Targets:** KPIs compared against strategic targets
- [ ] **Alerts:** Alert when KPIs fall below thresholds
- [ ] **Visibility:** KPIs easily accessible to leadership
- [ ] **Documentation:** KPI definitions and targets documented
- [ ] **Calculation Verified:** KPI calculations validated

### Definition of Done

This story is complete when:
- [ ] KPI calculation logic implemented
- [ ] KPIs calculated for past 12 months
- [ ] Month-over-month trending working
- [ ] Alert thresholds configured
- [ ] Unit tests ≥ 90% coverage
- [ ] Integration tests successful
- [ ] Code peer-reviewed and merged

---

## Tasks & Technical Details

### Development Tasks

1. **Define KPI Set** (Estimated: 1 hour)
   - Qualification success rate
   - SMS delivery success rate
   - Customer engagement rate
   - Month-over-month growth

2. **Implement KPI Calculations** (Estimated: 2 hours)
   - Build calculation logic for each KPI
   - Implement month-over-month comparison
   - Calculate variance from target

3. **Build Target Tracking** (Estimated: 1 hour)
   - Store KPI targets
   - Compare actual vs. target
   - Calculate variance percentage

4. **Implement Alert Logic** (Estimated: 1 hour)
   - Define alert thresholds
   - Trigger alerts when KPIs fall below threshold
   - Log alerts for review

5. **Write Tests** (Estimated: 1 hour)
   - Unit tests for KPI calculations
   - Integration tests with data
   - Alert logic tests

---

## Technical Considerations

**Key Performance Indicators**

| KPI | Formula | Target | Alert Threshold |
|-----|---------|--------|-----------------|
| Qualification Success Rate | Qualified / Processed | 75% | < 70% |
| SMS Delivery Success Rate | Delivered / Sent | 98% | < 96% |
| Customer Engagement Rate | Active / Qualified | 80% | < 75% |
| Month-over-Month Growth | (Current - Prior) / Prior | 5% | < 0% |

**KPI Calculation Logic (Pseudocode)**

```python
def calculate_kpis(month_year):
    """Calculate all KPIs for a month"""
    
    kpis = {}
    
    # 1. Qualification Success Rate
    kpis['qualification_rate'] = {
        'value': metrics['qualified'] / metrics['total_customers'],
        'target': 0.75,
        'unit': 'percent'
    }
    
    # 2. SMS Delivery Success Rate
    kpis['delivery_rate'] = {
        'value': metrics['delivered'] / metrics['total_sent'],
        'target': 0.98,
        'unit': 'percent'
    }
    
    # 3. Customer Engagement Rate
    kpis['engagement_rate'] = {
        'value': metrics['active_customers'] / metrics['qualified'],
        'target': 0.80,
        'unit': 'percent'
    }
    
    # 4. Month-over-Month Growth
    prior_metrics = query_metrics(get_prior_month(month_year))
    kpis['mom_growth'] = {
        'value': (metrics['qualified'] - prior_metrics['qualified']) / prior_metrics['qualified'],
        'target': 0.05,
        'unit': 'percent'
    }
    
    # Calculate variance from target
    for kpi_name, kpi_data in kpis.items():
        kpi_data['variance'] = kpi_data['value'] - kpi_data['target']
        kpi_data['status'] = 'GREEN' if kpi_data['variance'] >= 0 else 'RED'
        
        # Check alert threshold
        alert_threshold = kpi_data['target'] * 0.95  # 5% below target
        if kpi_data['value'] < alert_threshold:
            kpi_data['alert'] = True
            trigger_kpi_alert(kpi_name, kpi_data)
    
    return kpis

def trigger_kpi_alert(kpi_name, kpi_data):
    """Alert when KPI below threshold"""
    alert = {
        'kpi': kpi_name,
        'current_value': kpi_data['value'],
        'target': kpi_data['target'],
        'variance': kpi_data['variance'],
        'alertedAt': datetime.now()
    }
    store_kpi_alert(alert)
    notify_management(alert)
```

**KPI Dashboard Data Structure**

```sql
CREATE TABLE kpi_tracking (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  month_year VARCHAR(7),  -- YYYY-MM
  kpi_name VARCHAR(100),
  kpi_value DECIMAL(10,4),
  target_value DECIMAL(10,4),
  variance DECIMAL(10,4),
  status ENUM('GREEN', 'YELLOW', 'RED'),
  alert BOOLEAN DEFAULT FALSE,
  calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_month_kpi (month_year, kpi_name),
  INDEX idx_month (month_year),
  INDEX idx_status (status)
);

CREATE TABLE kpi_alerts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  kpi_name VARCHAR(100),
  alert_month VARCHAR(7),
  current_value DECIMAL(10,4),
  target_value DECIMAL(10,4),
  alert_message TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  acknowledged_at DATETIME,
  acknowledged_by VARCHAR(100),
  INDEX idx_created_at (created_at),
  INDEX idx_acknowledged (acknowledged_at)
);
```

---

## Testing Strategy

### Unit Tests
- KPI calculation accuracy
- Variance calculation
- Alert threshold logic
- Status determination

### Integration Tests
- Calculate KPIs for 12 months
- Verify accuracy against source data
- Test alert triggering
- Month-over-month comparison

### Manual Testing Scenarios
- Review calculated KPIs
- Verify accuracy
- Check alert thresholds
- Review month-over-month trends

### Acceptance Test Checklist
- [ ] All KPIs calculated correctly
- [ ] Targets configured accurately
- [ ] Variance calculations correct
- [ ] Alerts trigger appropriately
- [ ] 12-month history available
- [ ] Performance acceptable

---

## Dependencies & Blockers

### Internal Dependencies
- Depends on: US-5-1 (metric aggregation)
- Parallel with: US-5-2 (report generation)

### External Dependencies
- None

---

## Documentation

### Technical Documentation
- KPI definitions and formulas
- Target justification
- Alert threshold definitions

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

- [US-5-1](./US-5-1.md) - Metric aggregation (predecessor)
- [US-5-2](./US-5-2.md) - Report generation (parallel)
- [US-5-4](./US-5-4.md) - Distribution (successor)

---

**Created:** November 18, 2025
**Last Updated:** November 18, 2025
**Assignee:** [To be assigned]
**Reviewer:** [To be assigned]
