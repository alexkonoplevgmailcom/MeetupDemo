# Epic: Monthly Qualification Determination

**Epic ID:** E-002
**Priority:** P0 (Critical - MVP)
**Status:** Not Started
**Target Sprint(s):** Sprint 1-2
**Related BRD:** Premium_Customer_Notification_BRD.md - BR-2 (Monthly Qualification)
**Related FSD:** Premium_Customer_Notification_FSD.md - Process 2 (Monthly Qualification Calculation), Feature 2 (Monthly Qualification Determination)

---

## Epic Overview

**Business Goal:**
Calculate which customers qualify for premium recognition notifications based on maintaining the 15,000 NIS balance threshold for every day of the calendar month.

**User Story:**
As the Premium Customer Notification System, I want to determine month-end qualification based on all-or-nothing daily threshold compliance, so that only truly premium customers receive recognition notifications.

**Success Criteria:**
- Qualification calculation executes automatically on Day 1 of following month (00:01 AM)
- All daily balance check records for previous month are reviewed
- Customers with balance < 15,000 NIS on ANY day are disqualified
- Missing balance data for ANY day disqualifies customer
- Qualified customer list includes phone numbers for SMS dispatch
- Qualification results are immutable and audited
- Results available for SMS dispatch within 1 hour of calculation
- Audit trail shows calculation logic and all decisions

---

## Scope

### What's Included
- Retrieve all daily balance checks from previous calendar month
- Apply all-or-nothing qualification logic
- Generate qualified customer list with contact information
- Create audit trail of qualification decisions
- Store results for SMS dispatch system

### What's Excluded
- SMS notification sending (handled by E-003)
- Customer-facing qualification status
- Manual qualification overrides or exceptions
- Qualification history beyond current month
- Customer communication about qualification

---

## User Stories

| Story ID | Title | Points | Status |
|----------|-------|--------|--------|
| [US-2-1](./US-2-1.md) | Calculate month-end qualification status | 8 | Not Started |
| [US-2-2](./US-2-2.md) | Generate qualified customer list with metadata | 5 | Not Started |
| [US-2-3](./US-2-3.md) | Audit and validate qualification results | 3 | Not Started |

**Total Story Points:** 16

---

## Dependencies

### Internal Dependencies
- Depends on: Epic E-001 (Daily Balance Monitoring) - must be complete before month-end calculation
- Precedes: Epic E-003 (SMS Notification Dispatch)
- Precedes: Epic E-005 (Reporting & Analytics)

### External Dependencies
- None (uses data from E-001)

---

## Acceptance Criteria (Epic Level)

For the epic to be considered complete:
- [ ] All user stories meet acceptance criteria
- [ ] Qualification logic tested with 100+ customers across multiple months
- [ ] All-or-nothing rule verified (one day below disqualifies)
- [ ] Missing data handled correctly
- [ ] Qualified customer list accurate and accessible
- [ ] Audit trail complete and queryable
- [ ] Performance: qualification calculation completes within 1 hour
- [ ] Architecture review completed and approved
- [ ] Stakeholder sign-off obtained

---

## Technical Notes

**Architecture Impacts:**
- Requires month-end batch processor
- Need qualification results storage
- Integration with SMS dispatch system

**Database Changes:**
- Create `monthly_qualifications` table to store results
- Fields: qualification_id, customer_id, month, qualification_status, qualified_days, total_days, created_at

**Performance:**
- Query daily_balance_checks efficiently by month and customer
- Batch process results in memory or chunks
- Index optimization for month/customer lookups

**Security:**
- Qualification results treated as financial records
- Audit trail immutable and secured
- Access controlled to authorized systems only

---

## Timeline

**Estimated Duration:** 2 weeks (spans Sprint 1-2 depending on E-001 completion)
**Start Date:** After E-001 complete (end of Sprint 1)
**Target Completion:** End of Sprint 2
**Review Frequency:** Daily standup, Sprint review

---

## Metrics & Reporting

**Velocity Prediction:** 16 story points (1-2 sprints)
**Risk Level:** Low
- Depends on accurate daily data from E-001
- Logic is deterministic (all-or-nothing)

**Key Blockers:** None anticipated

---

## Notes

- The all-or-nothing rule is strict: literally one day below 15,000 NIS disqualifies entire month
- No partial credit or averaging
- Month boundary: strictly calendar month (Jan 1 - Jan 31, etc.)
- Qualification is month-specific; prior month results don't carry forward
- This is a critical process: must be 100% accurate

**Last Updated:** November 18, 2025
**Epic Owner:** [To be assigned]
**Product Owner Review:** Pending Approval
