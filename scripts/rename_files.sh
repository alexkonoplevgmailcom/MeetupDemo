#!/bin/bash

EPICS_DIR="/Users/alexk/Projects/ MeetupDemo/docs/agile/epics"

# Epic 1: AID-11
cd "$EPICS_DIR/AID-11-Daily-Balance-Monitoring"
mv "US-1-1.md" "AID-12-Set-up-automated-daily-balance-check-execution.md"
mv "US-1-2.md" "AID-13-Validate-customer-balance-against-15000-NIS-threshold.md"
mv "US-1-3.md" "AID-14-Handle-balance-verification-failures-and-data-quality-issues.md"
echo "✓ Epic AID-11 files renamed"

# Epic 2: AID-15
cd "$EPICS_DIR/AID-15-Monthly-Qualification"
mv "US-2-1.md" "AID-16-Calculate-month-end-qualification-status.md"
mv "US-2-2.md" "AID-17-Generate-qualified-customer-list-with-metadata.md"
mv "US-2-3.md" "AID-18-Audit-and-validate-qualification-results.md"
echo "✓ Epic AID-15 files renamed"

# Epic 3: AID-19
cd "$EPICS_DIR/AID-19-SMS-Notification-Dispatch"
mv "US-3-1.md" "AID-20-Validate-customer-phone-numbers.md"
mv "US-3-2.md" "AID-21-Generate-SMS-notification-batch-file.md"
mv "US-3-3.md" "AID-22-Submit-SMS-batch-to-carrier.md"
mv "US-3-4.md" "AID-23-Handle-SMS-submission-failures-and-retries.md"
echo "✓ Epic AID-19 files renamed"

# Epic 4: AID-24
cd "$EPICS_DIR/AID-24-SMS-Delivery-Tracking"
mv "US-4-1.md" "AID-25-Poll-SMS-carrier-for-delivery-confirmations.md"
mv "US-4-2.md" "AID-26-Log-and-categorize-SMS-delivery-outcomes.md"
mv "US-4-3.md" "AID-27-Retry-failed-SMS-deliveries.md"
mv "US-4-4.md" "AID-28-Escalate-undeliverable-messages-to-operations.md"
echo "✓ Epic AID-24 files renamed"

# Epic 5: AID-29
cd "$EPICS_DIR/AID-29-Reporting-Analytics"
mv "US-5-1.md" "AID-30-Aggregate-qualification-and-delivery-metrics.md"
mv "US-5-2.md" "AID-31-Generate-monthly-performance-report.md"
mv "US-5-3.md" "AID-32-Calculate-key-performance-indicators-KPIs.md"
mv "US-5-4.md" "AID-33-Distribute-reports-to-stakeholders.md"
echo "✓ Epic AID-29 files renamed"

echo ""
echo "All files renamed successfully!"
