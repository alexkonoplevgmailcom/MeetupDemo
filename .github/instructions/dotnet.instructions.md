---
description: .NET Backend Development Instructions
applyTo: 'src/backend/**'
---

# .NET Backend Development Instructions

**Framework:** .NET 10 + ASP.NET Core  
**Target Performance:** API <500ms, Database <100ms, Cache >80% hit rate

## Architecture Overview

### Technology Stack
- **.NET 10** with ASP.NET Core for the API
- **Entity Framework Core** for data access and ORM
- **MongoDB** for document storage
- **Redis** for distributed caching and session management
- **Azure OpenAI Vision API** (or other AI/ML services) for advanced features
- **Docker** for containerization and deployment
- **Kubernetes-ready** architecture for scalability

### System Design Principles
1. **Microservices-Ready**: Design services with clear boundaries and responsibilities
2. **API-First**: Define API contracts before implementation
3. **Scalability**: Support 100K+ concurrent users with stateless design
4. **Caching Strategy**: 80%+ cache hit rate using Redis
5. **Security-First**: Authentication, authorization, data protection
6. **Observability**: Logging, tracing, and monitoring from day one

## Clean Architecture Principles

Clean Architecture ensures maintainability, testability, and independence from frameworks. The backend strictly follows these principles:

### Core Tenets
1. **Independence from Frameworks**: The business logic doesn't depend on UI, database, or web frameworks
2. **Testability**: Business rules can be tested without external dependencies (UI, database, external APIs)
3. **Independence from UI**: UI can change without affecting business rules
4. **Independence from Database**: Database technology can be swapped without changing business rules
5. **Independence from External Agencies**: Business rules don't depend on external systems or libraries

### Dependency Rule
```
                    ┌─────────────────────┐
                    │    Presenters       │
                    │    Controllers      │
                    │    Gateways         │
                    └──────────┬──────────┘
                               ↑
                    ┌──────────┴──────────┐
                    │  Interface Adapters │
                    │  Repositories       │
                    │  Gateways           │
                    └──────────┬──────────┘
                               ↑
                    ┌──────────┴──────────┐
                    │  Application        │
                    │  (Use Cases)        │
                    │  Entities           │
                    └──────────┬──────────┘
                               ↑
                    ┌──────────┴──────────┐
                    │  Enterprise         │
                    │  (Business Rules)   │
                    └─────────────────────┘
```

**Key Rule**: Code can only depend INWARD. An entity in an inner circle cannot know about an entity in an outer circle.

### Layer Responsibilities

#### 1. **Enterprise Layer** (Innermost - No Dependencies)
Contains the highest-level business rules. Completely independent of any framework.

```csharp
namespace ProjectName.Domain.Entities;

// Pure domain entities with no framework dependencies
public class Meal
{
    public string Id { get; private set; }
    public UserId UserId { get; private set; }
    public FoodDescription Description { get; private set; }
    public MealImage Image { get; private set; }
    
    // Pure business logic methods
    public bool IsComplete() => Image != null && Description != null;
    
    public void AnalyzeNutrition(NutritionAnalysis analysis)
    {
        if (!IsComplete()) throw new InvalidOperationException("Meal not ready for analysis");
        Analysis = analysis;
    }
}

// Value Objects - Business rules encoded as types
public record FoodDescription(string Text)
{
    public FoodDescription(string text) : this(text)
    {
        if (string.IsNullOrWhiteSpace(text)) throw new ArgumentException("Description required");
        if (text.Length > 1000) throw new ArgumentException("Description too long");
    }
}
```

#### 2. **Application Layer** (Use Cases)
Contains application-specific business rules. Orchestrates between entities and interfaces.

```csharp
namespace ProjectName.Application.UseCases;

public interface ICreateMealUseCase
{
    Task<MealResponse> ExecuteAsync(CreateMealRequest request, CancellationToken cancellationToken);
}

// High-level use case - independent of Entity Framework, MongoDB, or any framework
public class CreateMealUseCase : ICreateMealUseCase
{
    private readonly IMealRepository _mealRepository;
    private readonly IFoodAnalysisService _analysisService;
    
    public CreateMealUseCase(
        IMealRepository mealRepository,
        IFoodAnalysisService analysisService)
    {
        _mealRepository = mealRepository ?? throw new ArgumentNullException(nameof(mealRepository));
        _analysisService = analysisService ?? throw new ArgumentNullException(nameof(analysisService));
    }
    
    public async Task<MealResponse> ExecuteAsync(CreateMealRequest request, CancellationToken cancellationToken)
    {
        // 1. Validate input (business rules)
        if (string.IsNullOrEmpty(request.FoodDescription))
            throw new DomainException("Food description required");
        
        // 2. Create domain entity
        var meal = new Meal(request.UserId, new FoodDescription(request.FoodDescription));
        
        // 3. Call external service (abstracted)
        var analysis = await _analysisService.AnalyzeFoodAsync(request.Base64Image, cancellationToken);
        meal.AnalyzeNutrition(analysis);
        
        // 4. Persist (abstracted via repository interface)
        await _mealRepository.AddAsync(meal, cancellationToken);
        
        // 5. Return response (converted from domain entity)
        return new MealResponse
        {
            Id = meal.Id,
            FoodDescription = meal.Description.Text,
            Calories = meal.Analysis?.Calories,
            CreatedAt = meal.CreatedAt
        };
    }
}
```

#### 3. **Interface Adapters Layer**
Converts data between external systems and internal format. Contains controllers, repositories, gateways.

```csharp
namespace ProjectName.Infrastructure.Repositories;

// Repository adapter - implements domain interface, uses MongoDB
public class MealRepository : IMealRepository
{
    private readonly IMongoCollection<MealDocument> _collection;
    
    public async Task<Meal> GetByIdAsync(string mealId, CancellationToken cancellationToken)
    {
        // 1. Query database (framework concern)
        var document = await _collection.Find(d => d.Id == new ObjectId(mealId))
            .FirstOrDefaultAsync(cancellationToken);
        
        if (document == null) return null;
        
        // 2. Convert to domain entity (adapter responsibility)
        return MapToDomain(document);
    }
    
    public async Task AddAsync(Meal meal, CancellationToken cancellationToken)
    {
        // 1. Convert domain entity to database document (adapter responsibility)
        var document = MapToDocument(meal);
        
        // 2. Persist (framework concern)
        await _collection.InsertOneAsync(document, cancellationToken: cancellationToken);
    }
    
    // Pure mapping logic - can be tested independently
    private Meal MapToDomain(MealDocument document)
    {
        return new Meal(
            document.UserId,
            new FoodDescription(document.FoodDescription));
    }
    
    private MealDocument MapToDocument(Meal meal)
    {
        return new MealDocument
        {
            UserId = meal.UserId,
            FoodDescription = meal.Description.Text
        };
    }
}
```

#### 4. **Frameworks & Drivers Layer** (Outermost)
Contains framework-specific code: ASP.NET Core controllers, database implementations, external API clients.

```csharp
namespace ProjectName.API.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class MealsController : ControllerBase
{
    private readonly ICreateMealUseCase _createMealUseCase;
    
    public MealsController(ICreateMealUseCase createMealUseCase)
    {
        _createMealUseCase = createMealUseCase ?? throw new ArgumentNullException(nameof(createMealUseCase));
    }
    
    [HttpPost]
    public async Task<ActionResult<MealResponse>> Create(
        [FromBody] CreateMealRequest request,
        CancellationToken cancellationToken)
    {
        try
        {
            // 1. Call use case (application layer - independent of ASP.NET)
            var result = await _createMealUseCase.ExecuteAsync(request, cancellationToken);
            
            // 2. Convert to HTTP response (framework concern)
            return Created(nameof(Create), result);
        }
        catch (DomainException ex)
        {
            // 3. Handle domain exceptions (business rule violations)
            return BadRequest(new { error = ex.Message });
        }
    }
}
```

### Concrete Layer Structure

```
src/backend/
├── ProjectName.Domain/                          # ENTERPRISE LAYER
│   ├── Entities/
│   │   ├── User.cs
│   │   ├── Meal.cs
│   │   ├── MealAnalysis.cs
│   │   └── ...
│   ├── ValueObjects/
│   │   ├── Email.cs
│   │   ├── FoodDescription.cs
│   │   ├── NutritionFacts.cs
│   │   └── ...
│   ├── Interfaces/                           # OUTPUT PORTS (abstractions)
│   │   ├── IMealRepository.cs               # Repository interface
│   │   ├── IFoodAnalysisService.cs          # Service interface
│   │   └── ...
│   └── Exceptions/
│       ├── DomainException.cs
│       ├── ValidationException.cs
│       └── ...
│
├── ProjectName.Application/                     # APPLICATION LAYER (Use Cases)
│   ├── UseCases/
│   │   ├── ICreateMealUseCase.cs            # INPUT PORT (interface)
│   │   ├── CreateMealUseCase.cs
│   │   ├── IGetMealsUseCase.cs
│   │   ├── GetMealsUseCase.cs
│   │   └── ...
│   ├── DTOs/                                 # Data Transfer Objects
│   │   ├── CreateMealRequest.cs
│   │   ├── MealResponse.cs
│   │   └── ...
│   └── Validators/
│       ├── CreateMealValidator.cs
│       └── ...
│
├── ProjectName.Infrastructure/                  # INTERFACE ADAPTERS
│   ├── Repositories/                         # PRIMARY ADAPTERS (implement domain interfaces)
│   │   ├── MealRepository.cs
│   │   ├── UserRepository.cs
│   │   └── ...
│   ├── ExternalServices/                     # SECONDARY ADAPTERS (implement domain interfaces)
│   │   ├── AzureOpenAIAdapter.cs             # Implements IFoodAnalysisService
│   │   ├── TelegramGateway.cs                # Implements ITelegramService
│   │   └── ...
│   ├── Data/
│   │   ├── MongoDbContext.cs
│   │   ├── MealDocument.cs
│   │   └── ...
│   └── Configurations/
│       └── DependencyInjection.cs
│
└── ProjectName.API/                             # FRAMEWORKS & DRIVERS
    ├── Controllers/                          # HTTP Adapters
    │   ├── MealsController.cs
    │   ├── UsersController.cs
    │   └── ...
    ├── Middleware/
    │   ├── ExceptionHandlingMiddleware.cs
    │   ├── AuthenticationMiddleware.cs
    │   └── ...
    ├── Filters/
    │   ├── ValidationFilter.cs
    │   └── ...
    └── Program.cs                            # Dependency Injection setup
```

### Dependency Injection - Enforcing Clean Architecture

```csharp
// Program.cs - Wire up layers following clean architecture
var builder = WebApplication.CreateBuilder(args);

// DOMAIN LAYER - No registration needed (no dependencies)

// APPLICATION LAYER - Register use cases
builder.Services.AddScoped<ICreateMealUseCase, CreateMealUseCase>();
builder.Services.AddScoped<IGetMealsUseCase, GetMealsUseCase>();
builder.Services.AddScoped<IDeleteMealUseCase, DeleteMealUseCase>();

// INTERFACE ADAPTERS - Register repositories (implement domain interfaces)
builder.Services.AddScoped<IMealRepository, MealRepository>();
builder.Services.AddScoped<IUserRepository, UserRepository>();

// Register external service adapters (implement domain interfaces)
builder.Services.AddScoped<IFoodAnalysisService, AzureOpenAIAdapter>();
builder.Services.AddScoped<ITelegramService, TelegramGateway>();

// FRAMEWORKS - Register framework-specific services
builder.Services.AddControllers();
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
});
```

### Testing with Clean Architecture

```csharp
// Test file can test use case independently - NO MOCKING NEEDED for domain logic
[TestClass]
public class CreateMealUseCaseTests
{
    [TestMethod]
    public async Task Execute_WithValidInput_CreatesMealWithAnalysis()
    {
        // Arrange - Mock ONLY external dependencies (repositories, services)
        var mockRepository = new Mock<IMealRepository>();
        var mockAnalysisService = new Mock<IFoodAnalysisService>();
        
        var request = new CreateMealRequest
        {
            UserId = "user-123",
            FoodDescription = "Grilled salmon with vegetables",
            Base64Image = "data:image/..."
        };
        
        mockAnalysisService
            .Setup(s => s.AnalyzeFoodAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new NutritionAnalysis { Calories = 450, Protein = 35 });
        
        var useCase = new CreateMealUseCase(mockRepository.Object, mockAnalysisService.Object);
        
        // Act - Call use case (pure business logic)
        var result = await useCase.ExecuteAsync(request, CancellationToken.None);
        
        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual(450, result.Calories);
        mockRepository.Verify(r => r.AddAsync(It.IsAny<Meal>(), It.IsAny<CancellationToken>()), Times.Once);
    }
    
    [TestMethod]
    [ExpectedException(typeof(DomainException))]
    public async Task Execute_WithoutFoodDescription_ThrowsDomainException()
    {
        // Business rule violation - tested WITHOUT mocks
        var useCase = new CreateMealUseCase(
            new Mock<IMealRepository>().Object,
            new Mock<IFoodAnalysisService>().Object);
        
        var invalidRequest = new CreateMealRequest { UserId = "user-123", FoodDescription = "" };
        
        await useCase.ExecuteAsync(invalidRequest, CancellationToken.None);
    }
}
```

### Key Benefits of Clean Architecture

✅ **Testability**: Test business logic without database, web server, or external services  
✅ **Flexibility**: Swap MongoDB for SQL, HTTP for gRPC, Azure OpenAI for another service  
✅ **Maintainability**: Clear separation of concerns makes code easier to understand and modify  
✅ **Framework Independence**: Business rules survive framework upgrades  
✅ **Clear Dependencies**: Dependency arrows point inward - no outward dependencies  
✅ **Team Scaling**: New developers understand structure immediately

## API Design Standards

### REST Conventions
```
GET    /api/{version}/resource              # List resources
GET    /api/{version}/resource/{id}         # Get specific resource
POST   /api/{version}/resource              # Create resource
PUT    /api/{version}/resource/{id}         # Update resource
DELETE /api/{version}/resource/{id}         # Delete resource
```

### Versioning
- Use URL versioning: `/api/v1/`, `/api/v2/`
- Maintain backward compatibility within major versions
- Plan migration path for deprecations (minimum 2 versions support)

### Response Format (Standard)
```json
{
  "success": true,
  "data": { /* resource */ },
  "message": "Operation successful",
  "timestamp": "2025-11-16T10:30:00Z",
  "requestId": "req-123-abc"
}
```

### Error Responses
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  },
  "timestamp": "2025-11-16T10:30:00Z",
  "requestId": "req-123-abc"
}
```

## Code Structure

### Project Organization
```
src/backend/
├── ProjectName.API/                 # Main ASP.NET Core project
│   ├── Controllers/              # API endpoints
│   ├── Services/                 # Business logic
│   ├── Models/                   # DTOs and view models
│   ├── Middleware/               # Custom middleware
│   ├── Extensions/               # Extension methods
│   └── Program.cs               # Dependency injection & configuration
├── ProjectName.Domain/             # Domain models and entities
│   ├── Entities/                # Core business entities
│   ├── ValueObjects/            # Value objects (Email, Money, etc.)
│   ├── Interfaces/              # Domain interfaces
│   └── Exceptions/              # Custom exceptions
├── ProjectName.Application/        # Application services
│   ├── Services/                # Application service logic
│   ├── Validators/              # FluentValidation validators
│   ├── Mappers/                 # AutoMapper profiles
│   └── DTOs/                    # Data transfer objects
├── ProjectName.Infrastructure/     # Infrastructure concerns
│   ├── Data/                    # MongoDB context and migrations
│   ├── Cache/                   # Redis caching layer
│   ├── ExternalServices/        # Azure OpenAI, Telegram APIs
│   ├── Repositories/            # Data access layer
│   └── Configurations/          # Configuration classes
└── ProjectName.Tests/              # Unit and integration tests
    ├── Unit/
    ├── Integration/
    └── Fixtures/
```

### Layered Architecture
```
Controllers (API Layer)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Database (MongoDB) + Cache (Redis)
```

## Entity & Model Guidelines

### Domain Entity (Core)
```csharp
namespace ProjectName.Domain.Entities;

public class Meal
{
    public string Id { get; set; } = ObjectId.GenerateNewId().ToString();
    public string UserId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    // Business properties
    public required string FoodDescription { get; set; }
    public required MealImage Image { get; set; }
    public MealAnalysis? Analysis { get; set; }
    
    // Navigation
    public User? User { get; set; }
}
```

### Value Objects (Immutable)
```csharp
namespace ProjectName.Domain.ValueObjects;

public record MealImage(
    string Url,
    string Base64Data,
    int Size,
    string ContentType)
{
    public void Validate()
    {
        if (string.IsNullOrEmpty(Url)) throw new ArgumentException("URL required");
        if (Size > 5 * 1024 * 1024) throw new ArgumentException("File too large");
    }
}
```

### DTOs (for API)
```csharp
namespace ProjectName.Application.DTOs;

public record CreateMealRequest(
    [Required] string FoodDescription,
    [Required] string Base64Image,
    string? Notes = null);

public record MealResponse(
    string Id,
    string FoodDescription,
    string ImageUrl,
    MealAnalysisResponse? Analysis,
    DateTime CreatedAt);
```

## Service Layer Standards

### Service Interface (Contract-First)
```csharp
namespace ProjectName.Application.Services;

public interface IMealService
{
    Task<MealResponse> CreateMealAsync(CreateMealRequest request, CancellationToken cancellationToken);
    Task<MealResponse> GetMealAsync(string mealId, CancellationToken cancellationToken);
    Task<IEnumerable<MealResponse>> GetUserMealsAsync(string userId, PaginationRequest pagination, CancellationToken cancellationToken);
    Task<bool> DeleteMealAsync(string mealId, CancellationToken cancellationToken);
}
```

### Service Implementation
```csharp
public class MealService : IMealService
{
    private readonly IMealRepository _repository;
    private readonly IAzureOpenAIService _aiService;
    private readonly ICacheService _cache;
    private readonly ILogger<MealService> _logger;
    
    public MealService(
        IMealRepository repository,
        IAzureOpenAIService aiService,
        ICacheService cache,
        ILogger<MealService> logger)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _aiService = aiService ?? throw new ArgumentNullException(nameof(aiService));
        _cache = cache ?? throw new ArgumentNullException(nameof(cache));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }
    
    public async Task<MealResponse> CreateMealAsync(CreateMealRequest request, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Creating meal for user {UserId}", GetCurrentUserId());
        
        // Validate input
        var validator = new CreateMealRequestValidator();
        var validationResult = await validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
            throw new ValidationException(validationResult.Errors);
        
        // Create domain entity
        var meal = new Meal
        {
            FoodDescription = request.FoodDescription,
            Image = new MealImage(
                Url: await _storage.UploadAsync(request.Base64Image),
                Base64Data: request.Base64Image,
                Size: System.Convert.FromBase64String(request.Base64Image).Length,
                ContentType: "image/jpeg")
        };
        
        // Analyze with AI
        meal.Analysis = await _aiService.AnalyzeFoodImageAsync(meal.Image);
        
        // Persist
        await _repository.AddAsync(meal, cancellationToken);
        await _repository.SaveChangesAsync(cancellationToken);
        
        // Cache
        await _cache.SetAsync($"meal:{meal.Id}", meal, TimeSpan.FromHours(1));
        
        _logger.LogInformation("Meal created: {MealId}", meal.Id);
        return MapToResponse(meal);
    }
}
```

## Caching Strategy

### Cache Configuration
```csharp
services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = configuration.GetConnectionString("Redis");
    options.InstanceName = "projectname:";
});
```

### Cache Key Naming Convention
```
user:{userId}:profile               # User profile
meal:{mealId}                       # Meal detail
user:{userId}:meals:page:{page}     # Paginated meals
nutritiondata:{code}                # Nutrition database
analysis:{mealId}                   # Cached analysis
session:{sessionId}                 # Session data
```

### Cache Implementation Pattern
```csharp
public async Task<UserProfile> GetUserProfileAsync(string userId)
{
    const string cacheKey = $"user:{userId}:profile";
    
    // Try cache first
    var cached = await _cache.GetAsync<UserProfile>(cacheKey);
    if (cached != null)
        return cached;
    
    // Fetch from database
    var profile = await _repository.GetUserProfileAsync(userId);
    if (profile == null)
        throw new NotFoundException($"User {userId} not found");
    
    // Cache for 24 hours
    await _cache.SetAsync(cacheKey, profile, TimeSpan.FromHours(24));
    
    return profile;
}
```

## Database (MongoDB) Guidelines

### Document Design
```csharp
// Keep documents denormalized for read performance
public class MealDocument
{
    [BsonId]
    public ObjectId Id { get; set; }
    public string UserId { get; set; }
    public string FoodDescription { get; set; }
    public AnalysisResult Analysis { get; set; }
    public DateTime CreatedAt { get; set; }
    
    // Embed related data for single query
    public UserSummary User { get; set; } // Embedded
}
```

### Indexing Strategy
```csharp
public class MealDbContext : MongoDbContext
{
    protected override void OnModelCreating(IMongoModelBuilder modelBuilder)
    {
        // Single-field indexes
        modelBuilder.Entity<Meal>()
            .HasIndex(m => m.UserId);
        
        // Composite indexes
        modelBuilder.Entity<Meal>()
            .HasIndex(m => new { m.UserId, m.CreatedAt });
        
        // Text search indexes for food descriptions
        modelBuilder.Entity<Meal>()
            .HasIndex(m => m.FoodDescription, IndexType.Text);
    }
}
```

## Performance Optimization

### Target Metrics
- **API Response:** <500ms (90th percentile)
- **Database Query:** <100ms (90th percentile)
- **Cache Hit Rate:** >80%

### Async/Await Best Practices
```csharp
// ✅ DO: Use async all the way
public async Task<IActionResult> GetMeal(string id)
{
    var meal = await _service.GetMealAsync(id, CancellationToken.None);
    return Ok(meal);
}

// ❌ DON'T: Block async calls
public IActionResult GetMeal(string id)
{
    var meal = _service.GetMealAsync(id).Result; // Deadlock risk
    return Ok(meal);
}
```

### Pagination Pattern
```csharp
public record PaginationRequest(int Page = 1, int PageSize = 20)
{
    public const int MaxPageSize = 100;
    public int ValidPageSize => Math.Min(PageSize, MaxPageSize);
    public int Skip => (Page - 1) * ValidPageSize;
}

// Usage
var meals = await _repository.GetPagedAsync(
    predicate: m => m.UserId == userId,
    skip: request.Skip,
    take: request.ValidPageSize);
```

## Security Requirements

### Authentication & Authorization
```csharp
// Add authentication
services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = configuration["Auth:Authority"];
        options.Audience = configuration["Auth:Audience"];
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true
        };
    });

// Apply authorization
[Authorize]
[HttpGet("{id}")]
public async Task<IActionResult> GetMeal(string id)
{
    // Only allow users to access their own meals
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    var meal = await _service.GetMealAsync(id);
    
    if (meal.UserId != userId)
        return Forbid();
    
    return Ok(meal);
}
```

### Input Validation
```csharp
public class CreateMealRequestValidator : AbstractValidator<CreateMealRequest>
{
    public CreateMealRequestValidator()
    {
        RuleFor(x => x.FoodDescription)
            .NotEmpty()
            .MaximumLength(1000);
        
        RuleFor(x => x.Base64Image)
            .NotEmpty()
            .Matches(@"^data:image\/")
            .Custom((image, context) =>
            {
                var bytes = Convert.FromBase64String(image);
                if (bytes.Length > 5 * 1024 * 1024)
                    context.AddFailure("Image exceeds 5MB limit");
            });
    }
}
```

### Data Protection
- Encrypt sensitive data (passwords, tokens) in transit and at rest
- Use HTTPS only
- Implement rate limiting to prevent abuse
- Sanitize all user inputs
- Follow OWASP guidelines

## Logging & Monitoring

### Structured Logging
```csharp
// Use structured logging for all operations
_logger.LogInformation(
    "Processing meal for user {UserId} with food type {FoodType}",
    userId,
    foodType);

// Log errors with context
_logger.LogError(
    exception,
    "Failed to analyze meal {MealId} for user {UserId}",
    mealId,
    userId);
```

### Distributed Tracing
- Implement request ID tracking across services
- Use Activity and ActivityListener for distributed tracing
- Include trace IDs in all logs and error responses

## Testing Standards

### Unit Test Requirements
```csharp
[TestClass]
public class MealServiceTests
{
    [TestMethod]
    public async Task CreateMeal_WithValidInput_ReturnsMealResponse()
    {
        // Arrange
        var service = new MealService(
            repository: Mock.Of<IMealRepository>(),
            aiService: Mock.Of<IAzureOpenAIService>(),
            cache: Mock.Of<ICacheService>());
        var request = new CreateMealRequest("Pizza", "data:image/...");
        
        // Act
        var result = await service.CreateMealAsync(request, CancellationToken.None);
        
        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual("Pizza", result.FoodDescription);
    }
}
```

### Test Coverage
- Target: >80% code coverage
- Unit tests for all public methods
- Integration tests for repository and external service calls
- Performance tests for critical paths

## Dependency Injection

### Registration Pattern
```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddScoped<IMealService, MealService>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IAuthService, AuthService>();

// Repositories
builder.Services.AddScoped<IMealRepository, MealRepository>();
builder.Services.AddScoped<IUserRepository, UserRepository>();

// Infrastructure
builder.Services.AddScoped<IAzureOpenAIService, AzureOpenAIService>();
builder.Services.AddScoped<IStorageService, AzureStorageService>();
builder.Services.AddStackExchangeRedisCache(options => { /* ... */ });

var app = builder.Build();

// Middleware
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

## Error Handling

### Custom Exceptions
```csharp
public class NotFoundException : Exception
{
    public NotFoundException(string message) : base(message) { }
}

public class ValidationException : Exception
{
    public ValidationException(IEnumerable<ValidationFailure> errors)
        : base("Validation failed")
    {
        Errors = errors.ToList();
    }
    public List<ValidationFailure> Errors { get; }
}
```

### Exception Middleware
```csharp
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;
        context.Response.ContentType = "application/json";
        
        var response = exception switch
        {
            NotFoundException => (StatusCode: StatusCodes.Status404NotFound, Error: exception.Message),
            ValidationException ve => (StatusCode: StatusCodes.Status400BadRequest, Error: string.Join(", ", ve.Errors.Select(e => e.ErrorMessage))),
            _ => (StatusCode: StatusCodes.Status500InternalServerError, Error: "Internal server error")
        };
        
        context.Response.StatusCode = response.StatusCode;
        await context.Response.WriteAsJsonAsync(new { error = response.Error });
    });
});
```

## Deployment & DevOps

### Docker Configuration
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10 AS build
WORKDIR /src
COPY ["src/backend/ProjectName.API/ProjectName.API.csproj", "ProjectName.API/"]
RUN dotnet restore "ProjectName.API/ProjectName.API.csproj"
COPY src/backend/ .
RUN dotnet build "ProjectName.API/ProjectName.API.csproj" -c Release

FROM mcr.microsoft.com/dotnet/aspnet:10 AS runtime
WORKDIR /app
COPY --from=build /src/bin/Release/net10.0/publish/ .
EXPOSE 5000 5001
ENTRYPOINT ["dotnet", "ProjectName.API.dll"]
```

### Environment Configuration
```csharp
// Use environment-based configuration
var mongoUri = configuration.GetConnectionString("MongoDB");
var redisUri = configuration.GetConnectionString("Redis");
var apiKey = configuration["AzureOpenAI:ApiKey"];

// Never hardcode secrets - use Azure Key Vault
if (app.Environment.IsProduction())
{
    builder.Configuration.AddAzureKeyVault(
        new Uri(configuration["KeyVault:Url"]),
        new DefaultAzureCredential());
}
```

## Code Standards & Quality

### Naming Conventions
- Classes/Methods: PascalCase (`MealService`, `CreateMealAsync`)
- Properties: PascalCase (`FoodDescription`)
- Private fields: camelCase with underscore prefix (`_repository`)
- Constants: UPPER_CASE (`MAX_IMAGE_SIZE`)
- Namespaces: Company.Project.Layer (`CompanyName.ProjectName.Application.Services`)

### Code Style
- Max line length: 120 characters
- Use var only when type is obvious
- Always use using statements for IDisposable
- Use nullable reference types (`#nullable enable`)
- Apply null-coalescing and null-conditional operators

### Documentation Requirements
- XML comments on all public APIs
- Architecture decision records for major choices
- README files in each project with setup instructions
- Inline comments for complex logic only

## Performance Checklist

Before considering code complete:
- [ ] API response time <500ms (tested)
- [ ] Database queries optimized with indexes
- [ ] Cache strategy implemented (target >80% hit rate)
- [ ] Async/await used throughout
- [ ] Pagination implemented for list endpoints
- [ ] Error handling with proper status codes
- [ ] Unit tests pass (>80% coverage)
- [ ] No N+1 query problems
- [ ] Input validation on all endpoints
- [ ] Authentication/authorization in place

## Related Documentation
- `SYSTEM_ARCHITECTURE.md` - Overall system design
- `TECHNOLOGY_STACK.md` - Technology justifications
- `DOCKER_DEPLOYMENT_GUIDE.md` - Deployment procedures
- `full-stack-developer.prompt.md` - Story-by-story workflow
