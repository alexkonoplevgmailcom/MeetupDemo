# Functional Specification Document (FSD)
## Premium Customer Monthly Notification System

---

## Document Metadata

| Item | Value |
|------|-------|
| **Document Title** | Premium Customer Monthly Notification System - FSD |
| **Document Version** | 1.0 |
| **Created Date** | November 18, 2025 |
| **Last Updated** | November 18, 2025 |
| **Status** | Draft |
| **Author** | Business Analyst |
| **Related BRD** | Premium_Customer_Notification_BRD.md v1.0 |
| **Currency** | Israeli New Shekel (NIS) |

---

## Executive Summary

The Premium Customer Monthly Notification System automates the identification and recognition of high-value customers maintaining daily account balances of 15,000 NIS or above throughout entire calendar months. The system sends personalized SMS notifications at month-end to acknowledge customer loyalty and strengthen engagement. This specification covers daily balance monitoring, qualification logic, SMS delivery, tracking, and reporting functions required for system implementation.

---

## User Roles & Personas

### 1. Automated System (Core Actor)
**Role:** Daily Balance Monitor & Notification Engine
**Responsibilities:**
- Continuously monitor customer account balances
- Calculate monthly qualification status
- Generate and deliver SMS notifications
- Track delivery confirmations
- Maintain audit logs

**Capabilities:**
- Access real-time and historical balance data
- Execute scheduled daily and month-end processes
- Integrate with SMS carrier APIs
- Generate reports and analytics

---

### 2. Operations Manager
**Role:** System Monitor & Exception Handler
**Responsibilities:**
- Monitor system health and notification delivery
- Handle failed delivery cases and exceptions
- Review monthly qualification reports
- Escalate issues requiring manual intervention

**Capabilities:**
- View system dashboards and reports
- Access delivery logs and audit trails
- Retry failed SMS sends
- Export data for analysis

---

### 3. Business Stakeholder / Product Owner
**Role:** Program Oversight & Performance Tracking
**Responsibilities:**
- Review program performance metrics
- Track customer engagement and retention impact
- Approve program adjustments or threshold changes
- Strategic decision-making on program expansion

**Capabilities:**
- Access monthly performance dashboards
- View aggregated customer metrics
- Export reports for executive review

---

### 4. Customer (Premium Segment)
**Role:** Notification Recipient
**Responsibilities:**
- Maintain qualifying account balance throughout month
- Respond to SMS notification (optional)
- Manage SMS opt-in/opt-out preferences

**Capabilities:**
- Receive SMS notifications
- Opt-in or opt-out of SMS communication
- Contact customer service regarding notification

---

## Core Business Processes

### Process 1: Daily Balance Monitoring (Ongoing)

**Purpose:** Track each customer's daily account balance against qualification threshold throughout the calendar month.

**Process Steps:**

1. System retrieves current date (daily, at end of business day)
2. System fetches account balance for all customers from core banking system
3. For each customer account:
   - Retrieve balance as of end of business day
   - Compare balance against 15,000 NIS threshold
   - Record balance check result (meets threshold: Y/N)
   - Flag any data quality issues or missing balance records
4. Store daily balance check results in audit log
5. Update running monthly qualification status for each customer

**Business Rules:**
- Balance must be ≥ 15,000 NIS (exactly 15,000 qualifies)
- Weekends and holidays are included (no exemptions)
- Missing balance data disqualifies customer for that month
- Any day the balance falls below threshold disqualifies customer for entire month

**Data Captured:**
- Customer ID
- Account balance as of end of business day
- Comparison result (passes/fails threshold)
- Date and timestamp of check
- Data quality flags

**Exception Handling:**
- If balance data unavailable: Log error, escalate to operations team, customer marked as "Data Unavailable" (disqualifies)
- If system unable to execute daily check: Log failure, retry on next business day, trigger alert

---

### Process 2: Monthly Qualification Calculation (Month-End)

**Purpose:** Determine which customers qualify for month-end notification based on threshold compliance throughout entire month.

**Trigger:** First day of following calendar month at 00:01 AM

**Process Steps:**

1. System identifies the just-completed calendar month
2. For each customer with active account:
   - Retrieve all daily balance check records for the completed month
   - Verify balance checks for every calendar day in month (28-31 days)
   - Determine if ALL days show balance ≥ 15,000 NIS
   - Identify any missing balance records or exceptions
3. Generate qualified customer list containing:
   - Customer ID
   - Customer phone number
   - Customer name/identifier
   - Confirmation of threshold met every day
   - Qualification status (Qualified / Not Qualified)
4. Store qualification results in audit database
5. Mark qualified customers for SMS generation

**Business Rules:**
- Customer must have balance ≥ 15,000 NIS on EVERY day of the calendar month
- A single day below threshold disqualifies entire month
- No exceptions for weekends, holidays, or system issues
- If balance data is missing for any day, customer is not qualified
- Qualification resets monthly; prior month status does not carry forward

**Data Output:**
- Month qualification report (Excel/CSV format)
- List of qualified customer IDs with phone numbers
- Count of qualified customers
- Count of disqualified customers (with reason)
- Data quality audit trail

---

### Process 3: SMS Notification Generation & Delivery (Month-End +1 Day)

**Purpose:** Create and send congratulatory SMS messages to all qualified customers.

**Trigger:** First business day after month-end at 09:00 AM

**Process Steps:**

1. Retrieve qualified customer list from Process 2
2. For each qualified customer:
   - Validate phone number format and deliverability
   - Create personalized SMS message acknowledging qualification
   - Flag invalid phone numbers for manual follow-up
3. Format batch SMS file for carrier submission
4. Submit batch to SMS carrier via API or file transfer
5. Receive initial delivery confirmation from carrier
6. Log all SMS records with timestamps and tracking IDs
7. Generate delivery initiation report

**SMS Message Content:** (Business perspective - exact wording subject to approval)
- Acknowledge customer loyalty and commitment
- Reference month completed (e.g., "November 2025")
- Brief mention of premium status recognition
- Optional call-to-action (e.g., "Inquire about our premium services")
- Organization identifier and opt-out instructions

**Business Rules:**
- One SMS per qualified customer per month
- Messages sent only to customers with valid phone numbers
- SMS delivery attempted within 24 hours of month-end
- Invalid phone numbers logged for customer service follow-up
- Message content consistent across all recipients (no personalization beyond name/greeting)

**Data Tracked:**
- Qualified customer ID and phone number
- SMS message content
- Timestamp of SMS submission to carrier
- Carrier tracking ID
- Initial delivery status

**Exception Handling:**
- Invalid phone number: Mark for manual review, alert operations team
- Carrier API failure: Retry up to 3 times, escalate after final failure
- Batch submission failure: Log error, retry next business day

---

### Process 4: SMS Delivery Tracking & Confirmation (Ongoing, Post-Delivery)

**Purpose:** Monitor SMS delivery confirmations and track final delivery status for all notifications.

**Process Steps:**

1. System polls SMS carrier for delivery confirmations (every 2 hours for 72 hours post-send)
2. For each SMS sent:
   - Retrieve delivery status from carrier (Delivered / Failed / No Confirmation)
   - Timestamp final delivery confirmation
   - Log delivery outcome
3. For failed deliveries:
   - Categorize failure reason (invalid number, carrier reject, timeout, etc.)
   - Queue for retry if applicable (up to 2 retries over 48 hours)
   - Escalate to operations team after final failure
4. Generate delivery status report:
   - Total SMS sent
   - Successfully delivered count
   - Failed delivery count
   - Pending/no confirmation count
5. Store all delivery records in audit trail

**Business Rules:**
- Delivery confirmation window: 72 hours post-send
- Retry failed SMS up to 2 times (retries within 24 hours)
- After 3 total attempts, mark as undeliverable
- Failed numbers flagged for customer service investigation
- Success metric: ≥ 98% delivery rate

**Data Tracked:**
- SMS ID and tracking number
- Delivery timestamp
- Delivery status (success/failure)
- Failure reason/code (if applicable)
- Final delivery outcome

---

### Process 5: Monthly Reporting & Analytics (End of Month +2 Days)

**Purpose:** Provide stakeholders with comprehensive program performance metrics and insights.

**Trigger:** Second business day after month-end

**Process Steps:**

1. Aggregate all monthly data:
   - Total customers monitored
   - Qualified customers (count and percentage)
   - SMS sent and delivery metrics
   - Delivery success rate
   - Failed delivery reasons
2. Generate performance report containing:
   - Executive summary (key metrics)
   - Detailed delivery status breakdown
   - Geographic or demographic distribution of qualified customers (if available)
   - Carrier performance data
   - Data quality and audit findings
3. Calculate against success metrics:
   - Qualification accuracy (sample audit)
   - Delivery performance vs. 98% target
   - System uptime status
   - Processing completion timeliness
4. Identify exceptions and issues requiring follow-up
5. Distribute report to stakeholders (Product Owner, Operations, Finance)

**Report Contents:**
- Month and year covered
- Qualified customers: count and %
- SMS sent: count and delivery rate
- Failed deliveries: count and primary reasons
- System uptime: % availability
- Processing completion time vs. target
- Exception summary
- Recommendations for next month

---

## Feature Specifications

### Feature 1: Daily Balance Verification

**Related BRD Requirements:** BR-1

**Purpose:** Automatically verify each customer's daily account balance to track month-to-date compliance with 15,000 NIS threshold.

**User Benefit:** Accurate, automated tracking enables reliable identification of premium customers without manual review.

**Actors:** Automated System

**Preconditions:**
- Core banking system available with real-time balance data
- Customer accounts exist and are active
- System connectivity to banking data source established

**User Interactions/Process:**
1. System executes nightly at end-of-business (22:00 PM)
2. System connects to core banking system
3. Retrieves current balance for all active customer accounts
4. Compares each balance to 15,000 NIS threshold
5. Records result (Pass/Fail) with timestamp and balance amount
6. If balance data unavailable: logs error and marks as exception

**Business Rules:**
- Threshold is exactly 15,000 NIS (≥ 15,000 qualifies)
- Daily checks include all calendar days (weekends, holidays)
- Balance must be captured at consistent time daily (end of business day)
- No grace period or averaging allowed

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| Customer ID | String (UUID) | Yes | Must exist in customer database |
| Account Balance | Decimal (NIS) | Yes | Must be ≥ 0; non-null value |
| Check Date | Date | Yes | Standard calendar date |
| Check Timestamp | DateTime | Yes | End of business day timestamp |
| Passes Threshold | Boolean | Yes | Calculated: Balance ≥ 15000 |
| Data Quality Flag | String | No | Error code if balance unavailable |

**Success Criteria:**
- Daily check completes without missing any customer account
- Balance comparison is accurate to last shekel
- All results logged with timestamp for audit
- System alerts triggered for any data quality issues
- Processing completes within 2-hour window after end of business day

---

### Feature 2: Monthly Qualification Determination

**Related BRD Requirements:** BR-2

**Purpose:** Calculate final qualification list for month-end notification based on consistent threshold compliance.

**User Benefit:** Ensures only customers meeting strict criteria receive recognition, maintaining program integrity.

**Actors:** Automated System, Operations Manager (review)

**Preconditions:**
- Calendar month completed
- All daily balance verification completed for month
- Qualified customer list not yet generated

**User Interactions/Process:**
1. At start of following calendar month (Day 1, 00:01 AM)
2. System retrieves all daily balance check records for previous month
3. For each customer:
   - Counts days where balance ≥ 15,000 NIS
   - Compares count to total calendar days in month
   - If count equals total days: Qualify = Yes
   - If any day missing or below threshold: Qualify = No
4. Generates structured list of qualified customers
5. Operations Manager receives automated report for review
6. Results stored in qualification audit database

**Business Rules:**
- All calendar days must have balance ≥ 15,000 NIS (no exceptions)
- Calculation is all-or-nothing (one day below disqualifies entire month)
- Missing balance data for any day = disqualified
- Qualification is month-specific (prior month irrelevant)
- Result is final once calculated (no retroactive adjustments)

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| Customer ID | String (UUID) | Yes | Must match customer database |
| Month | Date (Month/Year) | Yes | Previous calendar month |
| Qualifying Days | Integer | Yes | 0 to 28-31 depending on month |
| Required Days | Integer | Yes | Actual calendar days in month |
| Qualified | Boolean | Yes | True only if Qualifying Days = Required Days |
| Phone Number | String | Yes (if Qualified) | Valid format, non-null for qualified |
| Disqualification Reason | String | No (if Qualified) | Reason for non-qualification if applicable |

**Success Criteria:**
- 100% accuracy in qualification determination (verified by audit)
- All qualified customers have valid phone numbers
- Report generated by 06:00 AM on Day 1 of following month
- Zero false positives and false negatives
- Complete audit trail of qualification logic

---

### Feature 3: SMS Notification Dispatch

**Related BRD Requirements:** BR-3

**Purpose:** Generate and send personalized SMS notifications to qualified customers acknowledging their loyalty.

**User Benefit:** Customers feel recognized and valued; organization strengthens customer relationships.

**Actors:** Automated System, SMS Carrier

**Preconditions:**
- Qualified customer list finalized
- All phone numbers validated
- SMS message template approved
- SMS carrier API accessible

**User Interactions/Process:**
1. At 09:00 AM on first business day after month-end
2. System retrieves qualified customer list
3. For each qualified customer:
   - Validates phone number format
   - Personalizes message with customer name
   - Creates SMS record with unique tracking ID
4. Generates batch file for SMS carrier
5. Submits batch via API to SMS carrier
6. Receives batch confirmation and tracking numbers
7. Logs all SMS records with carrier tracking IDs

**SMS Message Template (Business Content):**
```
Hello [Customer Name],

We appreciate your continued loyalty! As a valued customer, 
you've maintained a premium balance throughout [Month Name]. 
Thank you for your trust.

[Optional: Learn about premium benefits: www.link]

Reply STOP to opt out.
```

**Business Rules:**
- Message personalized with customer first name minimum
- One SMS per qualified customer per month (no duplicates)
- SMS sent within 24 hours of month-end
- Invalid phone numbers excluded and logged
- Message content identical for all recipients (no custom variations)

**Data Requirements:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| SMS ID | String (UUID) | Yes | Unique identifier |
| Customer ID | String (UUID) | Yes | Must match qualified list |
| Phone Number | String | Yes | Valid E.164 format (+972...) |
| Customer Name | String | Yes | For personalization |
| Message Content | Text | Yes | ≤ 160 characters (SMS standard) |
| Carrier Reference ID | String | Yes | Assigned by SMS carrier |
| Sent Timestamp | DateTime | Yes | Exact time SMS submitted to carrier |
| Sent Status | Enum | Yes | Submitted / Failed / Queued |

**Success Criteria:**
- 100% of qualified customers receive SMS
- All SMS submitted to carrier within 24-hour window
- All SMS records logged with carrier tracking IDs
- Processing completes by 18:00 on dispatch day
- Zero SMS with invalid phone numbers sent

---

### Feature 4: SMS Delivery Confirmation & Tracking

**Related BRD Requirements:** BR-4

**Purpose:** Confirm successful SMS delivery and maintain detailed audit trail of all notifications.

**User Benefit:** Ensures delivery accuracy and provides compliance documentation.

**Actors:** Automated System, SMS Carrier, Operations Manager

**Preconditions:**
- SMS notification batch submitted to carrier
- Carrier API accepting delivery status inquiries
- Audit database operational

**User Interactions/Process:**
1. System polls SMS carrier API every 2 hours for 72 hours post-send
2. For each SMS sent:
   - Queries carrier for delivery status
   - Receives status: Delivered / Failed / Pending
   - Timestamps status confirmation
   - Logs delivery outcome
3. For failed SMS (after 72-hour window):
   - Categorizes failure reason
   - Logs final status as "Undeliverable"
   - Flags for operations team follow-up
4. Operations Manager reviews failed delivery report
5. Generates delivery confirmation report

**Delivery Status Logic:**
- **Delivered:** Carrier confirms message reached recipient phone
- **Failed:** Carrier unable to deliver (invalid number, network issue, rejected)
- **Pending/No Confirmation:** After 72 hours, mark as undeliverable if still pending

**Business Rules:**
- Polling window: 72 hours post-send
- If status confirmed "Delivered" before 72 hours: stop polling
- Failed SMS eligible for retry (up to 2 retries within 24 hours)
- After 3 total attempts: mark permanent failure
- Delivery success target: ≥ 98%

**Data Tracked:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| SMS ID | String (UUID) | Yes | Reference to original SMS |
| Delivery Status | Enum | Yes | Delivered / Failed / Undeliverable |
| Delivery Timestamp | DateTime | Yes | When status confirmed |
| Status Code | String | No | Carrier-specific error code if failed |
| Failure Reason | String | No | Human-readable reason (invalid number, timeout, etc.) |
| Retry Count | Integer | Yes | 0, 1, or 2 |
| Final Status | Enum | Yes | Success / Permanent Failure |

**Success Criteria:**
- Delivery status confirmed for ≥ 98% of SMS sent
- All failed SMS categorized with reason
- Operations team alerted to undeliverable numbers within 24 hours
- Complete audit trail of all status changes
- Report generated within 48 hours of polling window completion

---

### Feature 5: Monthly Performance Reporting

**Related BRD Requirements:** BR-5

**Purpose:** Provide stakeholders with comprehensive program performance data for oversight and decision-making.

**User Benefit:** Visibility into program effectiveness, metrics tracking, and identification of issues.

**Actors:** Automated System, Operations Manager, Business Stakeholder

**Preconditions:**
- Monthly cycle complete (balance monitoring, qualification, SMS delivery, tracking)
- All data aggregated and processed
- Report template available

**User Interactions/Process:**
1. At 14:00 on second business day after month-end
2. System aggregates all monthly data:
   - Total customers monitored
   - Qualified customer count and list
   - SMS sent count
   - Delivery success/failure counts
   - System uptime and processing times
3. Calculates key metrics:
   - Delivery success rate %
   - Qualified customer %
   - Failed delivery reason breakdown
   - Geographic distribution (if available)
4. Generates formatted report (Excel/PDF)
5. Distributes to Product Owner, Operations Manager, Finance
6. Archives report in audit system

**Report Sections:**
1. **Executive Summary**
   - Month covered
   - Qualified customers: [#] ([%] of total)
   - SMS sent: [#]
   - Delivery success rate: [%]
   - Status: On Target / At Risk / Below Target

2. **Detailed Metrics**
   - Total customers monitored: [#]
   - Customers qualified: [#] ([%])
   - Customers not qualified: [#] ([%])
   - SMS successfully delivered: [#] ([%])
   - SMS failed to deliver: [#] ([%])
   - SMS pending/no confirmation: [#] ([%])

3. **Delivery Failure Analysis**
   - Failure reason breakdown (invalid numbers, network issues, etc.)
   - Count per failure type
   - Unresolved/pending count

4. **Process Compliance**
   - Balance verification: Completed by [date] ✓
   - Qualification calculation: Completed by [date] ✓
   - SMS dispatch: Completed by [date] ✓
   - Delivery tracking: Completed by [date] ✓

5. **System Health**
   - System uptime: [%]
   - Processing completion time vs. target: [On Time / Delayed]
   - Data quality issues: [#] flagged
   - Exceptions requiring manual follow-up: [#]

6. **Recommendations**
   - Issues requiring attention
   - Process improvements
   - Threshold or policy changes to consider

**Data Output:**
- Excel file with detailed data
- PDF report for executive distribution
- CSV export for further analysis
- Automated email distribution to stakeholders

**Success Criteria:**
- Report generated on schedule (Day 2 +2, 14:00)
- All metrics accurate and verified
- Exception items clearly highlighted
- Report accessible to all authorized stakeholders
- Historical archive maintained for trend analysis

---

## Data Requirements

### Data Entities (Business View)

**Entity 1: Customer Account**

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|-----------|-------------|
| Customer ID | UUID | Yes | Unique, non-null | System-generated unique identifier |
| Customer Name | String | Yes | Non-null, 1-100 chars | Full name for personalization |
| Phone Number | String (E.164) | Yes | Format +972XXXXXXXXX | Mobile number for SMS |
| Active Status | Boolean | Yes | Default: True | Whether account is currently active |
| SMS Opt-In | Boolean | Yes | Must be True | Customer consent for SMS communications |
| Account Opening Date | Date | Yes | Valid date | When customer account opened |

**Entity 2: Daily Balance Record**

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|-----------|-------------|
| Record ID | UUID | Yes | Unique, non-null | Unique daily record identifier |
| Customer ID | UUID | Yes | Foreign key to Customer | Links to customer account |
| Check Date | Date | Yes | Valid calendar date | Date of balance check |
| Account Balance | Decimal | Yes | ≥ 0 | Balance amount in NIS |
| Threshold Check Result | Boolean | Yes | Calculated (≥ 15000) | Whether balance meets threshold |
| Check Timestamp | DateTime | Yes | Non-null | Time balance was recorded |
| Data Quality Flag | String | No | Error code if applicable | Flag for any data issues |

**Entity 3: Monthly Qualification**

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|-----------|-------------|
| Qualification ID | UUID | Yes | Unique, non-null | Unique qualification record |
| Customer ID | UUID | Yes | Foreign key to Customer | Links to customer account |
| Month | Date (Month/Year) | Yes | Valid month/year | Calendar month evaluated |
| Qualifying Days Count | Integer | Yes | 0 to 31 | Number of days meeting threshold |
| Required Days Count | Integer | Yes | 28-31 | Total calendar days in month |
| Qualified Status | Boolean | Yes | True if counts equal | Final qualification decision |
| Disqualification Reason | String | No | Enum if not qualified | Why customer did not qualify |
| Calculated Date | DateTime | Yes | Non-null | When qualification calculated |

**Entity 4: SMS Notification**

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|-----------|-------------|
| SMS ID | UUID | Yes | Unique, non-null | Unique SMS record identifier |
| Customer ID | UUID | Yes | Foreign key to Customer | Links to customer account |
| Month | Date (Month/Year) | Yes | Valid month/year | Month notification relates to |
| Phone Number | String (E.164) | Yes | Format +972XXXXXXXXX | Target phone number |
| Message Content | Text | Yes | ≤ 160 chars (SMS limit) | Full SMS message text |
| Carrier Reference ID | String | Yes | Non-null | SMS carrier tracking reference |
| Sent Timestamp | DateTime | Yes | Non-null | When SMS submitted to carrier |
| Sent Status | Enum | Yes | Submitted / Failed / Queued | Initial submission status |

**Entity 5: SMS Delivery Status**

| Attribute | Type | Required | Validation | Description |
|-----------|------|----------|-----------|-------------|
| Delivery ID | UUID | Yes | Unique, non-null | Unique delivery record |
| SMS ID | UUID | Yes | Foreign key to SMS | Links to SMS notification |
| Delivery Status | Enum | Yes | Delivered / Failed / Undeliverable | Final delivery outcome |
| Delivery Timestamp | DateTime | Yes | Non-null | When delivery confirmed/failed |
| Failure Code | String | No | Carrier error code | Error code if delivery failed |
| Failure Reason | String | No | Human-readable reason | Explanation of failure (if any) |
| Retry Count | Integer | Yes | 0, 1, or 2 | Number of delivery attempts |
| Final Status | Enum | Yes | Success / Permanent Failure | Whether delivery ultimately succeeded |

### Data Validation Rules

| Data Field | Rule | Error Handling |
|-----------|------|-----------------|
| Customer ID | Must exist in customer database | Reject record, log error |
| Phone Number | Must be valid E.164 format (+972XXXXXXXXX) | Flag for manual review, exclude from SMS |
| Account Balance | Must be numeric, ≥ 0 | Log error, mark day as data unavailable |
| Threshold Check Date | Must be valid calendar date | Reject record, escalate to operations |
| SMS Message | Must be ≤ 160 characters (SMS limit) | Truncate or reject, alert operations |
| Carrier Reference ID | Must be non-null string | Retry SMS submission, escalate if repeated |
| Month | Must be valid month in YYYY-MM format | Reject record, log error |

### Data Relationships

- **Customer** (1) ↔ (Many) **Daily Balance Record** - One customer has many daily balance checks
- **Customer** (1) ↔ (Many) **Monthly Qualification** - One customer has monthly qualification record per month
- **Monthly Qualification** (1) ↔ (1) **SMS Notification** - Each qualified customer gets one SMS per month
- **SMS Notification** (1) ↔ (1) **SMS Delivery Status** - Each SMS has one final delivery status

---

## Business Rules & Logic

### Rule 1: Qualification Logic
**Condition:** Customer maintains balance ≥ 15,000 NIS every calendar day of the month
**Consequence:** Customer qualifies for month-end SMS notification
**Details:** 
- No exemptions or exceptions
- One day below 15,000 NIS = entire month disqualified
- Missing balance data for any day = disqualified
- Month resets on 1st of calendar month

---

### Rule 2: Threshold Comparison
**Condition:** Account balance at end of business day is compared to 15,000 NIS
**Consequence:** Result (Pass/Fail) recorded for daily tracking
**Details:**
- Threshold is ≥ 15,000 (exactly 15,000 passes)
- Comparison uses end-of-business-day balance
- Comparison happens daily without exception
- No averaging or grace periods

---

### Rule 3: SMS Delivery Retry Logic
**Condition:** Initial SMS delivery fails from carrier
**Consequence:** SMS automatically retried up to 2 additional times (3 total attempts)
**Details:**
- First failure: Retry within 2 hours
- Second failure: Retry within 24 hours
- Third failure: Mark as permanent failure, escalate to operations
- After 3 attempts: Stop retrying and log final status

---

### Rule 4: SMS Message Frequency
**Condition:** Customer qualifies for month
**Consequence:** Exactly one SMS sent per qualified customer per calendar month
**Details:**
- No duplicate SMS for same customer in same month
- SMS sent once in first business day after month-end
- Prior month qualification does not carry forward

---

### Rule 5: Data Quality Requirement
**Condition:** Balance record missing or invalid for any calendar day in month
**Consequence:** Customer disqualified regardless of other days' data
**Details:**
- No missing data tolerance
- Invalid data treated same as missing
- Disqualification reason logged as "Data Quality Issue"

---

### Rule 6: Phone Number Validation
**Condition:** Phone number format invalid or non-deliverable
**Consequence:** SMS not sent; flagged for manual customer service follow-up
**Details:**
- Must be valid E.164 format: +972XXXXXXXXX
- Checked before SMS submission
- Invalid numbers excluded from batch
- Operations team receives alert for each invalid number

---

### Rule 7: Processing Timeline
**Condition:** Each process step (balance check, qualification, SMS send, tracking)
**Consequence:** Completes within defined time window
**Details:**
- Daily balance check: Nightly 22:00-24:00
- Qualification calculation: Month-end +1 day, 00:01 AM
- SMS dispatch: Month-end +1 day, 09:00 AM (first business day)
- Delivery tracking: Ongoing, every 2 hours for 72 hours post-send

---

### Rule 8: Audit Trail Requirements
**Condition:** Any data processing or SMS delivery action
**Consequence:** Complete record logged with timestamp for compliance
**Details:**
- All balance checks logged
- All qualification decisions logged with reason
- All SMS submissions logged with carrier reference
- All delivery confirmations/failures logged
- Audit trail retained for minimum 24 months

---

## Integration Requirements

### Integration 1: Core Banking System (Balance Data)

**Function:** Retrieve daily account balances for all customers

**Data Exchange:**
- **Input:** Daily trigger at end-of-business-day
- **Output:** Customer ID, Account Balance, Check Timestamp
- **Format:** API (REST/JSON) or scheduled data export (CSV/XML)
- **Frequency:** Once daily
- **Reliability:** Must be 99.5% available; failures trigger alert

**Business Impact:** Without balance data, customers cannot be qualified

**Dependency:** Real-time access to current account balances

---

### Integration 2: SMS Carrier API

**Function:** Submit SMS notifications and receive delivery confirmations

**Data Exchange:**
- **Input to Carrier:** Customer phone number, SMS message content, batch reference
- **Output from Carrier:** Submission confirmation, Carrier tracking ID
- **Format:** REST API with JSON payload
- **Authentication:** API key or OAuth token
- **Rate Limits:** Batch submission up to 1,000 SMS per request

**Delivery Confirmation:**
- **Method:** Carrier webhook callbacks or polling API
- **Data:** SMS ID (carrier ref), Delivery Status, Timestamp
- **Format:** JSON webhook or REST GET endpoint
- **Polling Frequency:** Every 2 hours for 72 hours

**Business Impact:** Without SMS carrier, notifications cannot be delivered

**Dependency:** Reliable SMS carrier partnership and API availability

---

### Integration 3: Audit & Compliance Database

**Function:** Store all processing records, decisions, and delivery confirmations

**Data Exchange:**
- **Input:** Daily balance records, Qualification decisions, SMS logs, Delivery confirmations
- **Output:** Historical records for reporting and audit
- **Format:** Direct database writes via application
- **Retention:** Minimum 24 months

**Business Impact:** Without audit logging, compliance and verification impossible

**Dependency:** Audit database must be reliable and highly available

---

## Reporting & Analytics

### Report 1: Monthly Performance Report

**Purpose:** Executive and operational visibility into program metrics

**Frequency:** Monthly, generated Day 2 after month-end

**Recipients:** Product Owner, Operations Manager, Finance Lead

**Metrics:**
- Qualified customers: count and %
- SMS sent: count
- Delivery success rate: %
- Failed deliveries: count and reasons
- System uptime: %
- Processing completion time

**Outputs:** Excel, PDF, Email distribution

---

### Report 2: Daily Operations Dashboard (Internal)

**Purpose:** Real-time monitoring for operations team

**Frequency:** Continuous update

**Metrics:**
- Today's balance check status (pending/complete)
- Current month qualification status (in-progress/at-risk/on-track)
- SMS delivery status for current month (pending/sent/failed)
- System health (uptime, error count)
- Alerts and exceptions requiring action

**Outputs:** Web dashboard, email alerts

---

### Report 3: Delivery Audit Report

**Purpose:** Compliance verification of SMS delivery

**Frequency:** Monthly

**Contents:**
- All SMS sent with timestamps and tracking IDs
- Delivery confirmation status for each SMS
- Failed SMS with reason codes
- Retry attempts and outcomes
- Undeliverable phone numbers with reason

**Outputs:** CSV export for archival and compliance review

---

## Acceptance Criteria

### Functional Acceptance

| Criterion | Definition | Verification |
|-----------|-----------|--------------|
| Balance Monitoring Accuracy | All customer balances correctly compared to 15,000 NIS threshold daily | Sample audit of 100+ records vs. source system |
| Qualification Accuracy | All qualifying customers correctly identified based on 100% daily threshold compliance | Manual verification of 10+ qualified customers' daily records |
| SMS Delivery Completeness | 100% of qualified customers receive SMS (or marked as invalid/undeliverable) | Count of SMS sent vs. qualified customer count |
| Timely Execution | All processes complete within defined time windows (daily, month-end, dispatch, tracking) | Log timestamps vs. target times for each process |
| Data Integrity | All records logged accurately with complete audit trail | Spot check of 20+ records across all entities |
| Error Handling | System appropriately handles exceptions (missing data, invalid phone, carrier failures) | Test cases for each exception scenario |
| Reporting Accuracy | Monthly report metrics match underlying data records | Reconcile report numbers to audit database |

### Non-Functional Acceptance

| Criterion | Definition | Target |
|-----------|-----------|--------|
| System Uptime | Platform availability for monitoring and processing | 99.5% monthly uptime |
| SMS Delivery Success Rate | % of SMS successfully delivered by carrier | ≥ 98% delivery rate |
| Processing Performance | Daily balance check completes within 2-hour window | ≤ 2 hours nightly |
| Data Accuracy | Zero false positives/negatives in qualification | 100% accuracy verified by audit |

### Test Scenarios

**Scenario 1: Happy Path - Qualified Customer**
- Precondition: Customer with balance ≥ 15,000 NIS all 30 days of November
- Action: System processes November month-end
- Expected: Customer appears on qualification list, receives SMS, delivery confirmed
- Acceptance: SMS received with correct content and timestamp logged

**Scenario 2: Failed Threshold - One Day Below**
- Precondition: Customer with balance ≥ 15,000 NIS all days except November 15 (12,000 NIS)
- Action: System processes November month-end
- Expected: Customer excluded from qualification list, no SMS sent
- Acceptance: Customer not on list, zero SMS sent for this customer

**Scenario 3: Missing Balance Data**
- Precondition: Customer account but balance data missing for November 8
- Action: System processes November month-end
- Expected: Customer disqualified due to data quality issue
- Acceptance: Disqualification reason logged, no SMS sent

**Scenario 4: Invalid Phone Number**
- Precondition: Qualified customer but phone number format invalid (555-1234)
- Action: System attempts SMS dispatch
- Expected: SMS rejected, customer flagged for manual follow-up
- Acceptance: Alert sent to operations team, customer not counted in sent SMS

**Scenario 5: SMS Delivery Failure**
- Precondition: SMS submitted to carrier, carrier returns delivery failure
- Action: System retries delivery up to 2 additional times
- Expected: After 3 total attempts, SMS marked as undeliverable, escalated
- Acceptance: Log shows 3 retry attempts, final status "Permanent Failure", operations alerted

**Scenario 6: System Outage During Monitoring**
- Precondition: Daily balance check scheduled, system becomes unavailable at 23:00
- Action: System comes back online at 23:45
- Expected: System automatically retries balance check on next availability
- Acceptance: All balance data captured despite outage, no data loss

---

## Glossary of Terms

| Term | Definition |
|------|-----------|
| **Qualified Customer** | Customer whose account balance was ≥ 15,000 NIS on every single calendar day of the month |
| **Daily Balance** | Account balance recorded at end of business day (22:00 PM) |
| **Calendar Month** | First through last day of a month (28-31 days depending on month) |
| **Threshold** | Minimum required balance: 15,000 NIS |
| **SMS** | Short Message Service; text message sent to mobile phone |
| **Carrier Tracking ID** | Unique reference number assigned by SMS carrier for tracking delivery |
| **Delivery Confirmation** | Carrier confirmation that SMS reached recipient's phone |
| **Audit Trail** | Complete log of all system actions and data processing for compliance |
| **Data Quality Flag** | Marker indicating missing, invalid, or problematic data |
| **Month-End** | Last calendar day of the month (28th-31st depending on month) |
| **E.164 Format** | International phone number standard: +[country code][phone number] |
| **Batch Submission** | Submitting multiple SMS to carrier in single request |
| **Polling** | Regularly checking SMS carrier for delivery status updates |

---

## Process Flow Diagrams

### Daily Balance Monitoring Flow

```
[22:00 PM - End of Business Day]
        ↓
[Trigger Daily Balance Check]
        ↓
[Connect to Banking System]
        ↓
[Retrieve All Customer Balances]
        ↓
[For Each Customer: Compare Balance to 15,000 NIS]
        ↓
        ├─→ Balance ≥ 15,000 → Record "Pass"
        └─→ Balance < 15,000 → Record "Fail"
        ↓
[Store Daily Record in Audit DB]
        ↓
[Update Month-to-Date Tracking]
        ↓
[Log Completion - Next Day 06:00]
```

### Monthly Qualification Flow

```
[Month Completed - Day 1 of Next Month, 00:01 AM]
        ↓
[Retrieve All Daily Records for Previous Month]
        ↓
[For Each Customer:
  Count Days where Balance ≥ 15,000 NIS
  Compare to Total Calendar Days in Month]
        ↓
        ├─→ Count = Total Days → Qualify = YES
        └─→ Count < Total Days → Qualify = NO
        ↓
[Generate Qualified Customer List with Phone #]
        ↓
[Store Qualification Results in DB]
        ↓
[Alert Operations Manager - List Ready for Review]
        ↓
[Prepare for SMS Dispatch (06:00 AM)]
```

### SMS Dispatch & Delivery Flow

```
[Day 1 of Following Month, 09:00 AM]
        ↓
[Retrieve Qualified Customer List]
        ↓
[For Each Qualified Customer:
  Validate Phone Number Format
  Create Personalized SMS Message
  Generate Tracking ID]
        ↓
[Format Batch SMS File]
        ↓
[Submit Batch to SMS Carrier API]
        ↓
[Carrier Returns: Batch ID + Individual Tracking IDs]
        ↓
[Log SMS Records with Carrier Tracking IDs]
        ↓
[Monitor for Delivery Status (Every 2 Hours × 72 Hours)]
        ↓
        ├─→ Delivered → Log Success
        ├─→ Failed → Retry (up to 2 additional attempts)
        └─→ No Confirmation After 72 Hours → Mark Undeliverable
        ↓
[Generate Delivery Report - Day 2 +2]
```

---

## Review & Approval

### Stakeholder Sign-off

This FSD should be reviewed and approved by:

- **Business Analyst** - Functional specification accuracy and completeness
- **Product Owner** - Business requirements alignment and scope
- **Operations Manager** - Process feasibility and operational fit
- **Compliance Officer** - Regulatory and data privacy requirements
- **IT/Systems Architect** - Technical feasibility confirmation
- **SMS Carrier Partner** - Delivery capability confirmation

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-18 | Business Analyst | Initial FSD creation from BRD v1.0 |

---

**Document Prepared:** November 18, 2025  
**Last Updated:** November 18, 2025  
**Status:** Draft - Awaiting Stakeholder Review

---

**END OF FUNCTIONAL SPECIFICATION DOCUMENT**
