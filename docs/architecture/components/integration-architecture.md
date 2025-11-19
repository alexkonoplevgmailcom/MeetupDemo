# Integration Architecture - Premium Customer Notification System

**Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** Published

---

## 1. Overview

The integration architecture defines how the Premium Customer Notification System connects to external systems: the core banking platform for balance data and the SMS carrier for message delivery. Each integration point is designed for reliability, security, and auditability.

---

## 2. Core Banking System Integration

### 2.1 Overview

The system queries the core banking platform daily to retrieve customer account balances required for qualification determination. This is the critical source of truth for balance verification.

**Integration Type:** Synchronous REST API calls  
**Frequency:** Once daily (end of business day, 22:00 PM)  
**Timeout:** 30 seconds per request  
**Retry Policy:** 3 attempts with exponential backoff

### 2.2 API Specification

**Endpoint:** `GET /api/v1/accounts/{accountId}/balance`

**Request Parameters:**

```json
{
  "accountId": "ACC-12345-67890",
  "asOfDate": "2025-11-18",
  "asOfTime": "21:00:00"
}
```

**Response (Success - 200 OK):**

```json
{
  "accountId": "ACC-12345-67890",
  "customerId": "12345",
  "balance": {
    "amount": 25000.00,
    "currency": "NIS",
    "asOfDate": "2025-11-18",
    "asOfTime": "21:00:00"
  },
  "accountStatus": "ACTIVE",
  "timestamp": "2025-11-18T21:00:00Z",
  "referenceId": "REF-123456789"
}
```

**Error Responses:**

| Status | Code | Message | Action |
|--------|------|---------|--------|
| 400 | INVALID_REQUEST | Invalid account ID format | Log and retry |
| 401 | UNAUTHORIZED | Authentication failed | Check credentials, escalate |
| 404 | NOT_FOUND | Account not found | Log and skip account |
| 500 | INTERNAL_ERROR | Server error | Retry with backoff |
| 503 | SERVICE_UNAVAILABLE | Temporary unavailability | Retry with backoff, escalate if persistent |

### 2.3 Authentication

**Method:** Certificate-based mutual TLS (mTLS)

```
Client Certificate: /etc/secrets/banking-client.crt
Client Key: /etc/secrets/banking-client.key
CA Certificate: /etc/secrets/banking-ca.crt
Protocol: TLS 1.3
```

**Alternative:** API Key with encryption

```
Header: X-API-Key: [encrypted-api-key]
Bearer: Authorization: Bearer {JWT-token}
```

### 2.4 Integration Service Implementation

**Service:** BankingSystemClient

```csharp
public class BankingSystemClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<BankingSystemClient> _logger;
    private readonly IAsyncPolicy<HttpResponseMessage> _retryPolicy;
    
    public async Task<BalanceResponse> GetAccountBalanceAsync(
        string accountId, 
        DateTime asOfDate,
        CancellationToken cancellationToken)
    {
        var request = new HttpRequestMessage(HttpMethod.Get, 
            $"/api/v1/accounts/{accountId}/balance");
        request.Headers.Add("X-Correlation-Id", 
            CorrelationContext.Current.CorrelationId);
        
        var response = await _retryPolicy.ExecuteAsync(
            async () => await _httpClient.SendAsync(request, cancellationToken)
        );
        
        if (!response.IsSuccessStatusCode)
        {
            _logger.LogError(
                "Balance retrieval failed for {AccountId}: {StatusCode} {Reason}",
                accountId, 
                response.StatusCode, 
                response.ReasonPhrase
            );
            throw new BankingSystemException(response.StatusCode, 
                response.ReasonPhrase);
        }
        
        var content = await response.Content.ReadAsStringAsync(cancellationToken);
        return JsonSerializer.Deserialize<BalanceResponse>(content);
    }
}
```

### 2.5 Error Handling & Resilience

**Retry Policy (Polly):**

```csharp
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .Or<TimeoutException>()
    .OrResult<HttpResponseMessage>(r => 
        r.StatusCode == System.Net.HttpStatusCode.ServiceUnavailable ||
        r.StatusCode == System.Net.HttpStatusCode.RequestTimeout)
    .WaitAndRetryAsync(
        retryCount: 3,
        sleepDurationProvider: retryAttempt => 
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
        onRetry: (outcome, timespan, retryCount, context) =>
        {
            _logger.LogWarning(
                "Retry {RetryCount} after {DelaySeconds}s for account {AccountId}",
                retryCount, timespan.TotalSeconds, 
                context["accountId"]
            );
        }
    );
```

**Circuit Breaker Policy:**

```csharp
var circuitBreakerPolicy = Policy
    .Handle<HttpRequestException>()
    .CircuitBreakerAsync(
        handledEventsAllowedBeforeBreaking: 5,
        durationOfBreak: TimeSpan.FromSeconds(60),
        onBreak: (outcome, duration) =>
        {
            _logger.LogError(
                "Circuit breaker opened for {Duration}s due to {Exception}",
                duration.TotalSeconds, outcome.Exception?.Message
            );
        }
    );
```

### 2.6 Data Mapping

**Banking System Response → Internal Model:**

```csharp
public class BalanceVerificationMapper
{
    public DailyBalanceCheck MapToDailyCheck(
        BalanceResponse bankingResponse,
        Customer customer)
    {
        return new DailyBalanceCheck
        {
            CustomerId = customer.Id,
            CheckDate = bankingResponse.Balance.AsOfDate,
            Balance = bankingResponse.Balance.Amount,
            Threshold = 15000,
            PassesThreshold = bankingResponse.Balance.Amount >= 15000,
            CheckTimestamp = bankingResponse.Timestamp,
            CorrelationId = CorrelationContext.Current.CorrelationId,
            BankingReferenceId = bankingResponse.ReferenceId
        };
    }
}
```

---

## 3. SMS Carrier Integration

### 3.1 Overview

The system integrates with an SMS carrier (Twilio, local provider, or equivalent) to send notifications to qualified customers. Integration handles both batch submission and delivery status polling.

**Integration Type:** REST API  
**Submission:** Synchronous batch POST  
**Status Polling:** Asynchronous periodic GET  
**Batch Size:** 500-1000 SMS per request  
**Delivery Confirmation Window:** 72 hours

### 3.2 Submission API Specification

**Endpoint:** `POST /api/v1/messages/batch`

**Request:**

```json
{
  "batchId": "BATCH-20251118-001",
  "messages": [
    {
      "messageId": "MSG-001",
      "phoneNumber": "+972512345678",
      "content": "Hello John, We appreciate your continued loyalty...",
      "priority": "HIGH",
      "callbackUrl": "https://notification-service/callbacks/sms-delivery"
    },
    {
      "messageId": "MSG-002",
      "phoneNumber": "+972587654321",
      "content": "Hello Sarah, We appreciate your continued loyalty...",
      "priority": "HIGH",
      "callbackUrl": "https://notification-service/callbacks/sms-delivery"
    }
  ],
  "metadata": {
    "campaignId": "premium-monthly-nov-2025",
    "correlationId": "corr-20251118-001"
  }
}
```

**Response (Accepted - 202):**

```json
{
  "batchId": "BATCH-20251118-001",
  "submissionStatus": "ACCEPTED",
  "timestamp": "2025-11-18T09:00:00Z",
  "messages": [
    {
      "messageId": "MSG-001",
      "trackingId": "CARRIER-TRACK-00001",
      "status": "QUEUED"
    },
    {
      "messageId": "MSG-002",
      "trackingId": "CARRIER-TRACK-00002",
      "status": "QUEUED"
    }
  ]
}
```

### 3.3 Delivery Status API

**Endpoint:** `GET /api/v1/messages/{trackingId}/status`

**Response:**

```json
{
  "trackingId": "CARRIER-TRACK-00001",
  "messageId": "MSG-001",
  "status": "DELIVERED",
  "deliveryTimestamp": "2025-11-18T09:05:30Z",
  "statusCode": "0",
  "statusMessage": "Message successfully delivered"
}
```

**Status Values:**

| Status | Meaning | Action |
|--------|---------|--------|
| QUEUED | Awaiting send | Continue polling |
| SENT | Sent to carrier network | Continue polling |
| DELIVERED | Successfully delivered to phone | Mark success, stop polling |
| FAILED | Delivery failed | Categorize failure, attempt retry |
| UNDELIVERABLE | Permanent failure | Mark undeliverable, escalate |
| NO_STATUS | No update from carrier | Treat as pending after 72h |

### 3.4 SMS Carrier Client Implementation

**Service:** SmsCarrierClient

```csharp
public class SmsCarrierClient
{
    private readonly HttpClient _httpClient;
    private readonly SmsCarrierConfig _config;
    private readonly ILogger<SmsCarrierClient> _logger;
    
    public async Task<BatchSubmissionResponse> SubmitBatchAsync(
        List<SmsMessage> messages,
        CancellationToken cancellationToken)
    {
        var batchId = Guid.NewGuid().ToString("N");
        
        var request = new BatchSubmissionRequest
        {
            BatchId = batchId,
            Messages = messages.Select(m => new CarrierSmsMessage
            {
                MessageId = m.Id,
                PhoneNumber = m.PhoneNumber,
                Content = m.Content,
                Priority = "HIGH",
                CallbackUrl = _config.CallbackUrl
            }).ToList(),
            Metadata = new BatchMetadata
            {
                CampaignId = "premium-monthly",
                CorrelationId = CorrelationContext.Current.CorrelationId
            }
        };
        
        var httpRequest = new HttpRequestMessage(HttpMethod.Post, 
            $"{_config.ApiUrl}/api/v1/messages/batch")
        {
            Content = new StringContent(
                JsonSerializer.Serialize(request),
                Encoding.UTF8,
                "application/json"
            )
        };
        
        httpRequest.Headers.Authorization = 
            new AuthenticationHeaderValue("Bearer", _config.ApiKey);
        
        var response = await _httpClient.SendAsync(httpRequest, cancellationToken);
        
        if (!response.IsSuccessStatusCode)
        {
            _logger.LogError(
                "Batch submission failed: {StatusCode} {Body}",
                response.StatusCode,
                await response.Content.ReadAsStringAsync(cancellationToken)
            );
            throw new SmsCarrierException("Batch submission failed");
        }
        
        return await response.Content
            .ReadAsAsync<BatchSubmissionResponse>(cancellationToken);
    }
    
    public async Task<DeliveryStatusResponse> GetDeliveryStatusAsync(
        string trackingId,
        CancellationToken cancellationToken)
    {
        var httpRequest = new HttpRequestMessage(
            HttpMethod.Get,
            $"{_config.ApiUrl}/api/v1/messages/{trackingId}/status"
        );
        
        httpRequest.Headers.Authorization = 
            new AuthenticationHeaderValue("Bearer", _config.ApiKey);
        
        var response = await _httpClient.SendAsync(httpRequest, cancellationToken);
        
        return await response.Content
            .ReadAsAsync<DeliveryStatusResponse>(cancellationToken);
    }
}
```

### 3.5 Webhook Integration (Delivery Callbacks)

**Endpoint:** `POST /api/webhooks/sms-delivery`

**Payload:**

```json
{
  "trackingId": "CARRIER-TRACK-00001",
  "messageId": "MSG-001",
  "status": "DELIVERED",
  "deliveryTimestamp": "2025-11-18T09:05:30Z",
  "phoneNumber": "+972512345678",
  "statusCode": "0"
}
```

**Webhook Handler:**

```csharp
[ApiController]
[Route("api/webhooks")]
public class WebhookController : ControllerBase
{
    private readonly DeliveryTrackingService _trackingService;
    
    [HttpPost("sms-delivery")]
    public async Task<IActionResult> HandleSmsDelivery(
        [FromBody] DeliveryCallbackRequest request,
        CancellationToken cancellationToken)
    {
        // Validate webhook authenticity (signature verification)
        if (!ValidateWebhookSignature(request))
        {
            return Unauthorized("Invalid webhook signature");
        }
        
        // Process delivery status
        await _trackingService.ProcessDeliveryStatusAsync(
            request.TrackingId,
            request.Status,
            request.DeliveryTimestamp,
            cancellationToken
        );
        
        return Ok(new { status = "processed" });
    }
    
    private bool ValidateWebhookSignature(DeliveryCallbackRequest request)
    {
        // Implementation: Compare webhook signature with expected signature
        // using carrier's public key
        return true; // Placeholder
    }
}
```

### 3.6 Error Handling for SMS Delivery

**Failure Categories:**

| Category | Code | Reason | Action |
|----------|------|--------|--------|
| Invalid Number | 21211 | Invalid phone number | Mark undeliverable, escalate |
| Carrier Reject | 21614 | SMS rejected by carrier | Log, retry up to 2x |
| Timeout | 20429 | Rate limit exceeded | Backoff and retry |
| Provider Error | 50001-50999 | Carrier system issue | Retry with backoff |
| Network Error | 503 | Network unavailable | Retry with backoff |

**Retry Logic:**

```csharp
public async Task<SmsDeliveryResult> SendWithRetryAsync(
    SmsMessage message,
    CancellationToken cancellationToken)
{
    const int maxAttempts = 3;
    int attempt = 1;
    
    while (attempt <= maxAttempts)
    {
        try
        {
            var result = await _carrierClient.SendAsync(message, cancellationToken);
            
            if (result.Success)
            {
                return new SmsDeliveryResult 
                { 
                    Success = true, 
                    TrackingId = result.TrackingId,
                    Attempts = attempt
                };
            }
            
            // Check if error is retryable
            if (!IsRetryableError(result.ErrorCode))
            {
                return new SmsDeliveryResult 
                { 
                    Success = false, 
                    ErrorCode = result.ErrorCode,
                    ErrorMessage = result.ErrorMessage,
                    Retryable = false,
                    Attempts = attempt
                };
            }
            
            // Exponential backoff before retry
            await Task.Delay(
                TimeSpan.FromSeconds(Math.Pow(2, attempt)),
                cancellationToken
            );
            
            attempt++;
        }
        catch (Exception ex)
        {
            _logger.LogError(
                "SMS send attempt {Attempt} failed: {Exception}",
                attempt, ex.Message
            );
            
            if (attempt == maxAttempts)
            {
                return new SmsDeliveryResult 
                { 
                    Success = false, 
                    ErrorMessage = ex.Message,
                    Attempts = attempt
                };
            }
            
            attempt++;
        }
    }
    
    return new SmsDeliveryResult 
    { 
        Success = false, 
        ErrorMessage = "Max retry attempts exceeded",
        Attempts = maxAttempts
    };
}

private bool IsRetryableError(string errorCode) =>
    errorCode switch
    {
        "20429" => true,  // Rate limit
        "503" => true,    // Service unavailable
        "50001" => true,  // Provider error
        _ => false
    };
```

---

## 4. Data Flow Diagrams

### 4.1 Daily Balance Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Daily Balance Verification Process (22:00 PM)            │
└─────────────────────────────────────────────────────────────┘

BalanceMonitoringService
    │
    ├─ Get all active customers from DB
    │
    ├─ For each customer batch (1000 accounts):
    │
    ├─ Call Banking System API
    │       │
    │       ├─ GET /api/v1/accounts/{accountId}/balance
    │       │       ↓
    │       ├─ Retry 3x with exponential backoff
    │       │       ↓
    │       ├─ Return: { balance, timestamp, referenceId }
    │
    ├─ Map response to DailyBalanceCheck
    │       │
    │       ├─ balance: 25000.00
    │       ├─ threshold: 15000
    │       ├─ passesThreshold: true
    │       ├─ checkDate: 2025-11-18
    │       └─ checkTimestamp: 2025-11-18T22:00:00Z
    │
    ├─ Store in Database
    │       │
    │       └─ INSERT INTO daily_balance_checks (...)
    │
    ├─ Publish Event: BalanceVerified
    │       │
    │       └─ Message Queue (RabbitMQ)
    │
    └─ Log audit trail with correlation ID
```

### 4.2 SMS Submission & Tracking Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 2. SMS Notification Submission (09:00 AM Day+1)             │
└─────────────────────────────────────────────────────────────┘

QualificationEngine
    │
    ├─ Calculate qualified customers
    │       │
    │       └─ Publish: QualificationCalculated
    │
    └─ Message Queue (RabbitMQ)
            │
            ├─ [Event consumed by NotificationService]
            │
            ├─ Validate phone numbers
            │
            ├─ Render SMS template
            │
            ├─ Batch SMS (500 per batch)
            │
            └─ Submit to Carrier
                    │
                    ├─ POST /api/v1/messages/batch
                    │       ↓
                    ├─ Response: 202 Accepted
                    │       │
                    │       └─ trackingIds: [CARRIER-TRACK-00001, ...]
                    │
                    ├─ Store notification records with trackingId
                    │
                    ├─ Publish Event: NotificationSent
                    │
                    └─ Log submission audit trail

┌─────────────────────────────────────────────────────────────┐
│ 3. Delivery Status Polling (Every 2 hours for 72 hours)     │
└─────────────────────────────────────────────────────────────┘

DeliveryTrackingService
    │
    ├─ Get all notifications with pending status
    │
    ├─ For each trackingId:
    │
    ├─ Query Carrier API
    │       │
    │       ├─ GET /api/v1/messages/{trackingId}/status
    │       │       ↓
    │       ├─ Response: { status, deliveryTimestamp }
    │
    ├─ Categorize result
    │       │
    │       ├─ Delivered: Stop polling, mark success
    │       ├─ Failed: Log failure, prepare retry
    │       └─ Pending: Continue polling
    │
    ├─ Update delivery_status table
    │
    ├─ Publish Event: DeliveryConfirmed (if final)
    │
    └─ Generate metrics & alerts
```

---

## 5. Security & Compliance

### 5.1 Transport Security

**TLS Configuration:**

```
Protocol Version: TLS 1.3 minimum
Cipher Suites: Only strong ciphers
- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

Certificate Pinning: Yes (for banking system)
HSTS: Yes (Strict-Transport-Security header)
OCSP Stapling: Yes
```

### 5.2 Authentication & Authorization

**Banking System:**
- Mutual TLS (mTLS) with client certificate
- Certificate rotation: Annual
- Private key storage: Azure Key Vault / HashiCorp Vault

**SMS Carrier:**
- API Key stored encrypted in Key Vault
- Bearer token rotation: Quarterly
- OAuth2 or JWT option for future

### 5.3 Data Protection

**In Transit:**
- All external API calls use HTTPS/TLS 1.3
- Request/response encryption (if required)
- No sensitive data in logs or error messages

**At Rest:**
- Phone numbers encrypted with AES-256
- API keys encrypted with AWS KMS / Azure Key Vault
- Balance amounts stored encrypted (configurable)

### 5.4 Audit & Compliance

**Logging:**
- All external API calls logged with:
  - Timestamp, endpoint, method
  - Request/response status
  - Error codes and messages
  - Correlation ID for tracing
  - No sensitive data (phone numbers masked)

**Retention:**
- API call logs: 90 days (hot storage)
- Audit trail: 7 years (archive storage)
- Compliance: PCI DSS, SOX, Bank of Israel regulations

---

## 6. Monitoring & Alerting

### 6.1 Integration Health Monitoring

| Metric | Alert Threshold | Owner |
|--------|-----------------|-------|
| **Banking API Availability** | < 99.5% | Banking Team |
| **Banking API Response Time** | > 5 seconds | Banking Team |
| **SMS Carrier Availability** | < 98% | SMS Team |
| **SMS Delivery Rate** | < 98% | Notification Team |
| **Failed SMS Retry Exhaustion** | Any | Operations |
| **Webhook Delivery Failures** | > 5 consecutive | Operations |

### 6.2 Monitoring Queries

```sql
-- Banking API health last 24 hours
SELECT 
    DATE(event_data->>'timestamp') AS date,
    COUNT(*) AS total_calls,
    COUNT(*) FILTER (WHERE event_data->>'status' ~ '^(2|3)') 
        AS successful_calls,
    ROUND(100.0 * COUNT(*) FILTER (WHERE event_data->>'status' ~ '^(2|3)') 
        / COUNT(*), 2) AS success_rate
FROM system_events
WHERE event_type = 'banking_api_call'
  AND created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE(event_data->>'timestamp');

-- SMS delivery rate by hour
SELECT 
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS notifications_sent,
    COUNT(*) FILTER (WHERE status = 'Delivered') AS delivered,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'Delivered') 
        / COUNT(*), 2) AS delivery_rate
FROM delivery_status
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
```

---

## 7. Disaster Recovery

### 7.1 Banking System Outage

**Scenario:** Core banking system unavailable

**Response:**
1. Detect: Health check fails (timeout or 5xx error)
2. Alert: Escalate to banking team and operations
3. Retry: Exponential backoff up to 3x
4. Escalate: If outage > 2 hours, skip balance check for day
5. Notify: Send alert to stakeholders
6. Recovery: When service restored, catch-up with missed data

**Configuration:**

```csharp
"Banking": {
  "OutageThreshold": "02:00:00",  // Hours
  "EnableSkipOnOutage": true,
  "EscalationContacts": ["banking-team@bank.com"]
}
```

### 7.2 SMS Carrier Outage

**Scenario:** SMS carrier unavailable or high failure rate

**Response:**
1. Detect: Delivery rate < 95% or carrier returns errors
2. Alert: Operations team and SMS carrier support
3. Queue: Buffer SMS in message queue (configurable retention)
4. Retry: Exponential backoff + circuit breaker
5. Failover: Switch to secondary carrier (if configured)
6. Recovery: Resume sending when carrier recovers

---

**Last Updated:** November 18, 2025  
**Architecture Review Status:** ✅ Ready for Implementation
