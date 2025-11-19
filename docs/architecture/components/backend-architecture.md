# Backend Architecture - Premium Customer Notification System

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Overview

The backend architecture implements five core microservices responsible for daily balance monitoring, qualification calculation, SMS notification generation, delivery tracking, and reporting. Each service is deployed as an independent .NET 8 container with clear responsibilities and well-defined communication patterns.

---

## 2. Technology Stack

### Core Framework
- **.NET 8** - Latest LTS version with performance improvements
- **ASP.NET Core** - Web framework for API endpoints and background services
- **C# 12** - Modern language features for clean, maintainable code

### Key Libraries
- **Entity Framework Core 8** - ORM for database operations
- **Serilog** - Structured logging with multiple sinks
- **MassTransit** - Distributed message handling
- **Polly** - Resilience and retry policies
- **FluentValidation** - Input validation framework
- **AutoMapper** - Object mapping and transformation

---

## 3. Service Architecture

### 3.1 Balance Monitoring Service

**Responsibility:** Daily verification of customer account balances against the 15,000 NIS qualification threshold.

**Deployment:** One instance per environment with scheduled execution

**Key Components:**

```
BalanceMonitoringService/
├── Controllers/
│   └── BalanceCheckController.cs - Health and manual trigger endpoints
├── Services/
│   ├── BalanceVerificationService.cs - Core verification logic
│   ├── BankingSystemClient.cs - Banking system integration
│   └── BalanceCheckProcessor.cs - Batch processing
├── Models/
│   ├── BalanceCheckRequest
│   ├── BalanceCheckResult
│   └── DailyBalance
└── HostedServices/
    └── DailyBalanceCheckJob.cs - Scheduled task executor
```

**Key Responsibilities:**
- Connect to core banking system daily (end of business day)
- Retrieve account balance for all active customers
- Compare each balance to 15,000 NIS threshold
- Record result with timestamp and audit information
- Handle exceptions and data quality issues

**API Endpoints:**
```
POST /api/balance-checks/trigger - Manually trigger balance check
GET /api/balance-checks/status - Get current status
GET /api/balance-checks/{customerId} - Get customer's balance history
```

**Error Handling:**
- **ConnectionError:** Log and retry with exponential backoff
- **MissingBalance:** Log as data quality issue, mark customer
- **InvalidFormat:** Log parsing error, escalate to operations

**Technology Details:**
- Hosted Service for scheduled execution
- HttpClientFactory for banking system calls
- Polly circuit breaker for resilience
- Structured logging with correlation IDs

---

### 3.2 Qualification Engine

**Responsibility:** Calculate monthly qualification status based on 30-day balance compliance.

**Deployment:** Triggered at month-end with batch processing

**Key Components:**

```
QualificationEngine/
├── Controllers/
│   └── QualificationController.cs - Status and manual trigger
├── Services/
│   ├── QualificationCalculationService.cs - Core logic
│   ├── BalanceComplianceChecker.cs - Compliance verification
│   ├── QualifiedCustomerListBuilder.cs - Report generation
│   └── QualificationValidator.cs - Results validation
├── Models/
│   ├── QualificationCalculationRequest
│   ├── QualificationResult
│   └── QualifiedCustomer
└── HostedServices/
    └── MonthlyQualificationJob.cs - Month-end trigger
```

**Key Responsibilities:**
- Identify completed calendar month
- Retrieve all daily balance checks for that month
- Determine qualification (all days ≥ 15,000 NIS)
- Validate phone numbers for qualified customers
- Generate qualified customer list
- Publish qualification event

**Algorithm:**

```
For each active customer:
  1. Retrieve all balance checks for completed month
  2. Count days with balance ≥ 15,000 NIS
  3. If count == total calendar days:
     - Mark as Qualified
     - Validate phone number
     - Add to qualified list
  4. Else:
     - Mark as Not Qualified
     - Log disqualification reason
  5. Record qualification result with audit trail

Generate monthly qualification report:
- Total customers checked
- Qualified count and %
- Not qualified count and reasons
- Data quality issues
- System performance metrics
```

**Data Quality Checks:**
- All balance records present for month
- Phone number format validation
- Duplicate detection
- Historical anomalies flagged

**Technology Details:**
- Batch processing for performance
- LINQ for efficient data queries
- Transaction handling for data consistency
- Event publishing via message broker

---

### 3.3 Notification Service

**Responsibility:** Generate and dispatch SMS notifications to qualified customers.

**Deployment:** Multiple instances for parallel processing

**Key Components:**

```
NotificationService/
├── Controllers/
│   └── NotificationController.cs - Status and manual retry
├── Services/
│   ├── NotificationGenerationService.cs - SMS creation
│   ├── SmsCarrierClient.cs - Carrier API integration
│   ├── NotificationBatchProcessor.cs - Batch handling
│   └── PhoneNumberValidator.cs - Validation logic
├── Models/
│   ├── NotificationRequest
│   ├── SmsMessage
│   └── CarrierSubmissionRequest
└── Consumers/
    └── QualificationCalculatedConsumer.cs - Event handler
```

**Key Responsibilities:**
- Consume qualification events
- Validate phone numbers
- Render SMS message template with customer data
- Batch SMS for efficient carrier submission
- Submit to SMS carrier API
- Track carrier reference IDs
- Publish notification sent event

**SMS Message Template:**

```
Hello {CustomerFirstName},

We appreciate your continued loyalty! As a valued customer, 
you've maintained a premium balance throughout {MonthName}. 
Thank you for your trust.

[Learn about premium benefits: https://bank.example/premium]

Reply STOP to opt out.
```

**Message Generation Logic:**
- Personalize with customer first name
- Format month name correctly
- Include organization branding
- Ensure message fits SMS size (160 chars standard, 306 chars for Unicode)

**Carrier Integration:**
- REST API with API key authentication
- Batch submission for performance
- Automatic retry on carrier errors
- Idempotent submission (prevent duplicates)

**Technology Details:**
- Message queue consumer with MassTransit
- Template rendering with Scriban or Liquid
- Batch processing with configurable sizes
- Error tracking and alerting

---

### 3.4 Delivery Tracking Service

**Responsibility:** Monitor SMS delivery confirmations and track final delivery status.

**Deployment:** Multiple polling instances for concurrent status checks

**Key Components:**

```
DeliveryTrackingService/
├── Controllers/
│   └── DeliveryController.cs - Status queries
├── Services/
│   ├── DeliveryStatusPoller.cs - Polling orchestration
│   ├── CarrierStatusClient.cs - Carrier API queries
│   ├── DeliveryStatusProcessor.cs - Status reconciliation
│   └── FailureAnalyzer.cs - Failure categorization
├── Models/
│   ├── DeliveryStatusQuery
│   ├── CarrierStatusResponse
│   └── DeliveryFailure
└── HostedServices/
    └── DeliveryStatusPollingJob.cs - Continuous polling
```

**Key Responsibilities:**
- Poll SMS carrier for delivery confirmations every 2 hours
- Categorize delivery status (Success/Failed/Pending)
- Identify failure reasons
- Manage retry logic for failed SMS
- Publish delivery confirmation events
- Calculate delivery metrics

**Delivery Status Flow:**

```
Sent → Polling (0-72 hours)
       ├─ Delivered → Success (stop polling)
       ├─ Failed → Categorize failure, attempt retry
       └─ No Confirmation (72h) → Mark undeliverable

Retry Logic:
- Initial attempt + 2 retries = 3 total attempts
- Wait 6 hours between retries
- After 3 failures, mark permanent failure
- Escalate to operations team
```

**Failure Categorization:**
- **Invalid Number** - Phone number format or carrier rejection
- **Timeout** - Carrier network or timeout error
- **Quota Exceeded** - Carrier rate limiting
- **Undeliverable** - General carrier rejection
- **Provider Error** - Carrier system issue

**Technology Details:**
- Hosted service for continuous polling
- Async/await for concurrent API calls
- Event-based failure notifications
- Comprehensive logging with context

---

### 3.5 Reporting & Analytics Service

**Responsibility:** Aggregate program data and generate performance reports.

**Deployment:** Single instance with scheduled report generation

**Key Components:**

```
ReportingService/
├── Controllers/
│   └── ReportController.cs - Report access and generation
├── Services/
│   ├── MonthlyReportGenerator.cs - Report creation
│   ├── MetricsCalculator.cs - Metric aggregation
│   ├── ReportExporter.cs - Excel/PDF export
│   └── ReportDistributionService.cs - Email distribution
├── Models/
│   ├── MonthlyReport
│   ├── PerformanceMetrics
│   └── ExceptionSummary
└── HostedServices/
    └── MonthlyReportGenerationJob.cs - Scheduled execution
```

**Key Responsibilities:**
- Aggregate monthly program metrics
- Calculate qualification and delivery rates
- Analyze failures and exceptions
- Generate executive reports
- Export reports (Excel, PDF)
- Distribute to stakeholders
- Archive reports for compliance

**Report Contents:**

| Section | Metrics |
|---------|---------|
| **Program Summary** | Month, customers monitored, qualified count, delivery rate |
| **Qualification Metrics** | Total qualified, qualification %, reasons for non-qualification |
| **SMS Delivery** | Total sent, delivered, failed, pending counts |
| **Delivery Failures** | Failure categories and counts, top issues |
| **System Performance** | Processing times, uptime, error rates |
| **Recommendations** | Issues to address, improvements needed |

**Technology Details:**
- Scheduled report generation
- LINQ for complex data aggregation
- EPPlus or OpenXML for Excel export
- Email integration for distribution
- Report caching for performance

---

## 4. API Design

### 4.1 REST Conventions

All services follow RESTful conventions:

```
POST /api/{resource} - Create new resource
GET /api/{resource} - List resources
GET /api/{resource}/{id} - Get specific resource
PUT /api/{resource}/{id} - Update resource
DELETE /api/{resource}/{id} - Delete resource

POST /api/{resource}/actions/{action} - Custom actions
GET /api/{resource}/status - Status endpoint
POST /api/{resource}/retry - Retry failed operations
```

### 4.2 Common Response Format

```json
{
  "success": true,
  "data": { /* Response payload */ },
  "errors": ["List of error messages"],
  "metadata": {
    "timestamp": "2025-11-18T15:30:00Z",
    "correlationId": "uuid",
    "path": "/api/balance-checks/trigger"
  }
}
```

### 4.3 Error Handling

Standard HTTP status codes:
- **200 OK** - Success
- **202 Accepted** - Async operation accepted
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Authentication failed
- **403 Forbidden** - Authorization failed
- **404 Not Found** - Resource not found
- **409 Conflict** - Business rule violation
- **500 Internal Error** - Server error
- **503 Service Unavailable** - Dependent service down

---

## 5. Service Communication

### 5.1 Event-Driven Communication

Services communicate through domain events:

```
BalanceVerified
├── CustomerId
├── Balance
├── Threshold
├── Passed: boolean
├── Timestamp
└── CorrelationId

QualificationCalculated
├── Month
├── TotalQualified
├── QualifiedCustomers[]
├── Timestamp
└── CorrelationId

NotificationSent
├── CustomerId
├── SmsId
├── CarrierReference
├── Timestamp
└── CorrelationId

DeliveryConfirmed
├── SmsId
├── Status
├── Timestamp
└── CorrelationId
```

### 5.2 Message Broker Integration

Using MassTransit with RabbitMQ/Azure Service Bus:

```csharp
// Publish event
await _publishEndpoint.Publish(new BalanceVerifiedEvent 
{
    CustomerId = customerId,
    Balance = balance,
    // ...
});

// Subscribe to event
public class QualificationCalculatedConsumer : 
    IConsumer<QualificationCalculatedEvent>
{
    public async Task Consume(ConsumeContext<QualificationCalculatedEvent> context)
    {
        // Process event
    }
}
```

---

## 6. Business Logic Patterns

### 6.1 Qualification Calculation

```csharp
public class QualificationCalculationService
{
    public async Task<MonthlyQualificationResult> CalculateQualifications(
        DateTime month, 
        CancellationToken cancellationToken)
    {
        var result = new MonthlyQualificationResult();
        var daysInMonth = DateTime.DaysInMonth(month.Year, month.Month);
        
        var customers = await _customerRepository.GetAllActiveAsync(cancellationToken);
        
        foreach (var customer in customers)
        {
            var balanceChecks = await _balanceCheckRepository
                .GetByMonthAsync(customer.Id, month, cancellationToken);
                
            var qualifiedDays = balanceChecks
                .Count(b => b.PassesThreshold);
                
            if (qualifiedDays == daysInMonth)
            {
                result.QualifiedCustomers.Add(new QualifiedCustomer
                {
                    CustomerId = customer.Id,
                    PhoneNumber = customer.PhoneNumber,
                    Month = month
                });
            }
            else
            {
                result.DisqualifiedCustomers.Add(
                    customer.Id, 
                    $"Qualified {qualifiedDays}/{daysInMonth} days"
                );
            }
        }
        
        return result;
    }
}
```

### 6.2 SMS Batch Processing

```csharp
public class NotificationBatchProcessor
{
    private const int BatchSize = 1000;
    
    public async Task ProcessQualifiedCustomersAsync(
        IEnumerable<QualifiedCustomer> customers,
        CancellationToken cancellationToken)
    {
        var batches = customers
            .Chunk(BatchSize)
            .Select(chunk => chunk.ToList())
            .ToList();
            
        foreach (var batch in batches)
        {
            var messages = batch
                .Select(c => new SmsMessage
                {
                    PhoneNumber = c.PhoneNumber,
                    Content = RenderMessageTemplate(c),
                    CustomerId = c.Id
                })
                .ToList();
                
            var result = await _carrierClient.SubmitBatchAsync(
                messages, 
                cancellationToken
            );
            
            await LogSubmissionAsync(result, cancellationToken);
        }
    }
}
```

---

## 7. Data Access Patterns

### 7.1 Entity Framework Configuration

```csharp
modelBuilder.Entity<BalanceCheck>(entity =>
{
    entity.HasKey(e => e.Id);
    entity.HasIndex(e => new { e.CustomerId, e.CheckDate });
    entity.HasIndex(e => new { e.CheckDate, e.PassesThreshold });
    
    entity.Property(e => e.Balance)
        .HasPrecision(18, 2);
});

modelBuilder.Entity<MonthlyQualification>(entity =>
{
    entity.HasKey(e => new { e.CustomerId, e.Month });
    entity.HasIndex(e => e.Month);
    entity.HasIndex(e => new { e.Month, e.Qualified });
});
```

### 7.2 Query Optimization

```csharp
// Optimized query for balance check retrieval
var monthlyChecks = await _dbContext.BalanceChecks
    .AsNoTracking()
    .Where(b => b.CustomerId == customerId 
        && b.CheckDate.Month == month.Month 
        && b.CheckDate.Year == month.Year)
    .OrderBy(b => b.CheckDate)
    .ToListAsync(cancellationToken);
```

---

## 8. Resilience & Error Handling

### 8.1 Polly Resilience Policies

```csharp
// Retry policy with exponential backoff
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .Or<TimeoutException>()
    .WaitAndRetryAsync(
        retryCount: 3,
        sleepDurationProvider: attempt => 
            TimeSpan.FromSeconds(Math.Pow(2, attempt)),
        onRetry: (outcome, timespan, retryCount, context) =>
        {
            _logger.LogWarning(
                $"Retry {retryCount} after {timespan.TotalSeconds}s"
            );
        }
    );

// Circuit breaker policy
var circuitBreakerPolicy = Policy
    .Handle<HttpRequestException>()
    .CircuitBreakerAsync(
        handledEventsAllowedBeforeBreaking: 5,
        durationOfBreak: TimeSpan.FromSeconds(30)
    );

// Combined policy
var policyWrap = Policy.WrapAsync(retryPolicy, circuitBreakerPolicy);
```

### 8.2 Health Checks

```csharp
services.AddHealthChecks()
    .AddDbContextCheck<NotificationContext>()
    .AddRedis(_configuration["Redis:ConnectionString"])
    .AddRabbitMQ(_configuration["RabbitMQ:ConnectionString"])
    .AddCheck("BankingSystemCheck", 
        new BankingSystemHealthCheck(_bankingClient),
        tags: new[] { "banking" }
    );
```

---

## 9. Deployment & Configuration

### 9.1 Docker Configuration

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app/out .
EXPOSE 80
ENTRYPOINT ["dotnet", "NotificationService.dll"]
```

### 9.2 Environment Configuration

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  },
  "Database": {
    "ConnectionString": "Host=postgres;Database=notifications;..."
  },
  "Cache": {
    "ConnectionString": "redis:6379"
  },
  "MessageBroker": {
    "ConnectionString": "rabbitmq://rabbitmq:5672",
    "Queue": "notifications"
  },
  "Banking": {
    "ApiUrl": "https://banking-api.internal/",
    "Timeout": 30000
  },
  "SmsCarrier": {
    "ApiUrl": "https://sms-carrier.example/api",
    "ApiKey": "[SECRET]"
  }
}
```

---

## 10. Performance Considerations

### 10.1 Caching Strategy

- **Customer Cache:** Redis cache for customer master data (TTL: 24h)
- **Balance Threshold Cache:** Configuration cache (TTL: 7d)
- **Report Cache:** Calculated reports (TTL: 30d)

### 10.2 Query Optimization

- Proper indexing on frequently queried columns
- Pagination for large result sets
- Connection pooling for database connections
- Read replicas for reporting queries

### 10.3 Batch Processing

- Process balance checks in batches of 1,000
- Process SMS submissions in batches of 100-500
- Parallel processing with configurable concurrency

---

## 11. Security Considerations

### 11.1 Authentication & Authorization

- API key for service-to-service communication
- Role-based access control for API endpoints
- JWT tokens with expiration
- Audit logging for sensitive operations

### 11.2 Data Protection

- Encryption in transit (TLS 1.3)
- Encryption at rest for sensitive data
- Phone numbers masked in logs
- API keys stored in secure vault (Azure Key Vault)

### 11.3 Input Validation

- FluentValidation for all input models
- Sanitization of user inputs
- Rate limiting on public APIs
- CORS configuration for frontend access

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
