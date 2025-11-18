---
description: Solution Architecture Development Instructions
applyTo: 'docs/architecture/**'
---

# Solution Architecture Development Instructions

## Overview

This document provides guidelines for creating and maintaining comprehensive solution architecture documentation for the Loan Application Processing System. Architecture documentation should be clear, modular, and easy to navigate.

## Document Structure

Architecture documentation is organized into **four main components**:

```
docs/architecture/
├── solution-architecture.md          (Main Index)
├── components/
│   ├── frontend-architecture.md
│   ├── backend-architecture.md
│   ├── data-architecture.md
│   ├── integration-architecture.md
│   └── security-architecture.md
├── nfr/
│   ├── performance.md
│   ├── scalability.md
│   ├── reliability.md
│   ├── security-compliance.md
│   └── operational-requirements.md
└── diagrams/
    ├── c4-context.md
    ├── c4-container.md
    ├── c4-component.md
    ├── data-flow.md
    ├── deployment.md
    └── system-interactions.md
```

---

## 1. Main Architecture Document (Index)

**File:** `docs/architecture/solution-architecture.md`

### Purpose
Serves as the primary entry point and navigation hub for all architecture documentation. Provides high-level overview and quick navigation to detailed documents.

### Content Structure

```markdown
# Loan Application Processing System - Solution Architecture

## 1. Executive Summary
- High-level system overview
- Key architectural decisions
- Technology stack summary

## 2. Quick Navigation
- Links to all component documents
- Links to all NFR documents
- Links to all diagrams

## 3. Architecture Overview
- System context and boundaries
- Key design principles
- Architectural patterns used

## 4. Component Architecture Overview
- Brief description of each major component
- Links to detailed component docs

## 5. Non-Functional Requirements (NFR) Overview
- Summary of NFR categories
- Performance targets
- Scalability approach
- Security posture

## 6. Deployment & Infrastructure
- High-level deployment overview
- Environment strategy
- Infrastructure decisions

## 7. Key Architectural Decisions (ADR Index)
- List of Architecture Decision Records
- Decision rationale
- Trade-offs evaluated

## 8. Technology Stack
- Frontend technologies
- Backend technologies
- Data storage solutions
- Integration platforms
- Monitoring & observability tools

## 9. Roadmap & Future Considerations
- Scalability roadmap
- Technology evolution path
- Planned enhancements

## 10. Glossary & References
- Key terms
- External document links
- Standards & compliance references
```

### Guidelines

- Keep executive summary concise (< 2 pages)
- Provide clear navigation structure with hyperlinks
- Update navigation whenever new docs are added
- Include version history and last updated date
- Add table of contents for quick reference
- Include contact information for architecture team

---

## 2. Component Architecture Documents

**Location:** `docs/architecture/components/`

### File Organization

Each component document should cover:

#### 2.1 Frontend Architecture (`frontend-architecture.md`)

**Content Sections:**
- Technology stack and frameworks
- Folder structure and organization
- Key components overview
- State management architecture
- Routing strategy
- API integration patterns
- Performance optimization
- Accessibility & i18n considerations
- Build & deployment process

**Key Topics:**
- React component hierarchy
- UI/UX framework decisions
- Form handling and validation
- Error handling and recovery
- Offline capabilities (if applicable)

#### 2.2 Backend Architecture (`backend-architecture.md`)

**Content Sections:**
- Technology stack and frameworks
- API design and REST conventions
- Service layer organization
- Business logic patterns
- Authentication & authorization
- Error handling and logging
- Database interaction patterns
- Caching strategy
- Rate limiting and throttling
- Queue and background job processing

**Key Topics:**
- Microservices vs monolith decision
- API versioning strategy
- Request/response patterns
- Async processing approach
- Integration with external services

#### 2.3 Data Architecture (`data-architecture.md`)

**Content Sections:**
- Database selection rationale
- Schema design and relationships
- Data modeling patterns
- Indexing strategy
- Query optimization
- Data consistency approach
- Backup and recovery strategy
- Data retention policies
- GDPR/compliance considerations
- Migration strategy

**Key Topics:**
- Entity-relationship diagrams
- Normalization approach
- Denormalization decisions
- Archive strategy
- Data warehouse/analytics approach

#### 2.4 Integration Architecture (`integration-architecture.md`)

**Content Sections:**
- External system integrations
- API gateway design
- Message queue architecture
- Event streaming approach
- Webhook handling
- Third-party service integration
- Data synchronization patterns
- Error handling in integrations
- Retry and resilience strategy

**Key Integrations:**
- Credit bureau integration
- ID verification services
- Watchlist screening systems
- Payment processing
- Email/SMS notification services
- Bank account verification

#### 2.5 Security Architecture (`security-architecture.md`)

**Content Sections:**
- Authentication mechanisms
- Authorization model (RBAC/ABAC)
- Data encryption (at-rest, in-transit)
- API security
- Network security
- Secrets management
- Audit logging
- Compliance frameworks (Bank of Israel regulations)
- Vulnerability management
- Incident response procedures

**Key Topics:**
- OAuth2/OpenID Connect implementation
- JWT token handling
- Role-based access control matrix
- Data classification levels
- Security scanning and testing

### Guidelines for Component Documents

- **Length:** 3-8 pages per component
- **Audience:** Development teams, architects, security reviewers
- **Format:** Clear sections with code examples where relevant
- **Diagrams:** Include inline ASCII diagrams or reference diagram files
- **Links:** Cross-reference between components where dependencies exist
- **Code Examples:** Provide actual or pseudo-code snippets
- **Trade-offs:** Document why specific technologies were chosen
- **Future Considerations:** Note limitations and potential improvements

---

## 3. Non-Functional Requirements (NFR) Documents

**Location:** `docs/architecture/nfr/`

### Purpose
Document quality attributes and system characteristics that are not directly related to functional behavior.

### File Organization

#### 3.1 Performance (`performance.md`)

**Content Sections:**
- Performance targets and SLOs
- Response time requirements
- Throughput targets
- Resource utilization targets
- Performance optimization strategies
- Bottleneck identification and mitigation
- Performance testing approach
- Monitoring and alerting

**Key Metrics:**
- API response time targets (e.g., p95 < 500ms)
- Database query performance targets
- Frontend load time targets
- Cache hit rate targets
- Concurrent user capacity

#### 3.2 Scalability (`scalability.md`)

**Content Sections:**
- Horizontal vs vertical scaling approach
- Load balancing strategy
- Database scaling approach (sharding, replication)
- Caching and CDN strategy
- Auto-scaling triggers and policies
- Rate limiting and quota management
- Capacity planning
- Growth roadmap (Year 1, 2, 3+)

**Key Targets:**
- Target user capacity (100K+)
- Transaction volume capacity
- Data storage growth projections
- Geographic expansion strategy

#### 3.3 Reliability (`reliability.md`)

**Content Sections:**
- Availability targets (e.g., 99.9% uptime)
- Failure modes and mitigation
- Redundancy approach
- Disaster recovery strategy
- Business continuity planning
- Circuit breaker patterns
- Timeout and retry strategies
- Health checks and monitoring
- Graceful degradation approach

**Key Focus:**
- SLA definitions
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Single points of failure elimination
- Dependency management

#### 3.4 Security & Compliance (`security-compliance.md`)

**Content Sections:**
- Compliance frameworks (Bank of Israel regulations, ISO 27001, etc.)
- Data protection requirements (encryption, access control)
- Audit requirements
- Incident response procedures
- Security assessment schedule
- Vulnerability disclosure process
- Third-party security reviews
- Regulatory reporting requirements

**Key Compliance Areas:**
- KYC/AML requirements
- Data residency requirements
- Privacy regulations
- Encryption standards
- Audit logging requirements

#### 3.5 Operational Requirements (`operational-requirements.md`)

**Content Sections:**
- Monitoring and alerting strategy
- Logging and tracing approach
- Troubleshooting procedures
- Maintenance windows and scheduling
- Rollback procedures
- Environment management (dev, staging, prod)
- Incident severity levels and escalation
- On-call procedures
- Documentation requirements
- Knowledge transfer process

**Key Topics:**
- Observability framework
- Metrics collection
- Log aggregation
- Distributed tracing
- Alert routing and escalation

### Guidelines for NFR Documents

- **Quantifiable:** All NFR should have measurable targets
- **Realistic:** Targets should be achievable given resource constraints
- **Tracked:** Each NFR should have monitoring/measurement approach
- **Reviewed:** Regular review of NFR achievement and adjustment
- **Aligned:** NFR should align with business goals
- **Documented Trade-offs:** Note where NFR influenced architecture decisions

---

## 4. Diagram Files

**Location:** `docs/architecture/diagrams/`

### Diagram Guidelines

#### 4.1 Format Requirements

- **Format:** Mermaid diagrams only
- **File Type:** `.md` files containing Mermaid diagram code blocks
- **Each File:** One or more related diagrams, logically grouped

#### 4.2 Naming Convention

- Use descriptive names: `c4-context.md`, `data-flow.md`, `deployment.md`
- Avoid generic names like `diagram1.md`, `architecture.md`
- Use kebab-case for file names

#### 4.3 Mermaid Diagram Best Practices

**Component Naming:**
- Use **simple, descriptive names** (not full URLs or complex identifiers)
- Examples: ✅ "Loan Service" vs ❌ "com.example.services.LoanApplicationService"
- Keep names to 2-3 words where possible
- Use consistent terminology across diagrams

**Descriptions:**
- Include brief descriptions for each component/node
- Describe the component's role, not its implementation
- Examples: "Processes credit assessment and calculates risk score"
- Keep descriptions concise (< 15 words)

**Diagram Structure:**
- Clear hierarchies and relationships
- Color coding to indicate categories or criticality
- Direction: Top-to-bottom for flows, left-to-right for sequences
- Avoid diagram clutter: Use multiple diagrams for complex systems

#### 4.4 C4 Model Diagrams

**File:** `c4-context.md`
- System context diagram
- Shows system boundary, external systems, users
- Simplest level of detail

**File:** `c4-container.md`
- Container diagram (applications, databases, services)
- Shows major building blocks and technologies
- Internal structure of the system

**File:** `c4-component.md`
- Component diagram (libraries, components, packages)
- Detailed view of internal structure
- Can have multiple files for different subsystems

#### 4.5 Flow Diagrams

**File:** `data-flow.md`
- Data movement through system
- Shows processes and data stores
- Tracks information flow from source to destination

**Example Structure:**
```markdown
# Data Flow Diagrams

## Application Submission Data Flow
[Mermaid flowchart showing data movement during application submission]

## Credit Assessment Data Flow
[Mermaid flowchart showing data movement during credit assessment]

## Disbursement Data Flow
[Mermaid flowchart showing data movement during fund transfer]
```

#### 4.6 Deployment Diagrams

**File:** `deployment.md`
- Infrastructure topology
- Servers, containers, networks
- Production/staging/dev environments
- Disaster recovery setup

#### 4.7 System Interaction Diagrams

**File:** `system-interactions.md`
- Sequence diagrams for key workflows
- Integration points between systems
- External system interactions

### Mermaid Diagram Template

```markdown
# [Diagram Category] - [Specific Diagram Name]

## Overview
Brief explanation of what this diagram shows and its purpose.

## Diagram
\`\`\`mermaid
graph TB
    User["👤 User<br/>Loan Applicant"]
    Portal["🖥️ Web Portal<br/>Application submission interface"]
    API["🔌 API Gateway<br/>Request routing and rate limiting"]
    Service["⚙️ Loan Service<br/>Business logic processor"]
    DB[(📊 Database<br/>Application storage)]
    
    User -->|Submit Application| Portal
    Portal -->|API Request| API
    API -->|Process Request| Service
    Service -->|Query/Store Data| DB
    
    style User fill:#e1f5ff
    style Portal fill:#fff3e0
    style API fill:#f3e5f5
    style Service fill:#e8f5e9
    style DB fill:#fce4ec
\`\`\`

## Description
- **User:** Loan applicants accessing the system
- **Web Portal:** Frontend interface for application submission
- **API Gateway:** Centralized entry point for all requests
- **Loan Service:** Core business logic for loan processing
- **Database:** Persistent storage for application data

## Data Flow
1. User submits application through web portal
2. Portal sends API request through gateway
3. API gateway routes to appropriate service
4. Service processes business logic and queries database
5. Results returned to portal and displayed to user

## Key Components
- Response time: < 500ms
- Concurrent capacity: 1,000 users
- Database: PostgreSQL with replication
```

### Diagram Documentation

Each diagram file should include:

- **Filename:** Descriptive name (c4-context.md)
- **Title:** Clear diagram name
- **Purpose:** What the diagram shows and why
- **Legend:** Color coding or symbol meanings
- **Component Descriptions:** Each node/box explained
- **Relationships:** How components interact
- **Notes:** Key architectural decisions reflected in the diagram
- **Version:** Last updated date

---

## 5. Creating Architecture Documentation

### Step 1: Start with the Index
1. Create `solution-architecture.md`
2. Outline main sections
3. Leave placeholders for component and NFR links

### Step 2: Define Components
1. Identify major system components
2. Create component architecture documents
3. Document each component's responsibilities
4. Link interdependencies

### Step 3: Define Non-Functional Requirements
1. Define performance targets with business stakeholders
2. Define scalability roadmap
3. Define compliance and security requirements
4. Define operational requirements

### Step 4: Create Diagrams
1. Create C4 context diagram (highest level)
2. Create container diagram (major systems)
3. Create component diagrams (as needed)
4. Create data flow and deployment diagrams
5. Add sequence diagrams for key workflows

### Step 5: Link and Validate
1. Update main index with all links
2. Cross-reference between documents
3. Verify all links work
4. Review for consistency and completeness

---

## 6. Maintenance & Updates

### Review Schedule
- **Quarterly:** Full architecture review
- **Monthly:** NFR metrics review
- **Upon Major Changes:** Update relevant documents within 5 business days
- **Prior to Releases:** Validate architecture documentation matches implementation

### Update Workflow
1. Identify what needs to be updated
2. Create feature branch: `docs/architecture-update-{date}`
3. Update affected documents
4. Update diagram(s) if architectural changes
5. Update main index if adding new sections
6. Create pull request with architecture review checklist

### Version Control
- Track changes in git history
- Maintain change log in main architecture document
- Document "Last Updated" date on each component doc
- Use meaningful commit messages for architecture changes

### Documentation Accuracy
- Code reviews should verify architecture compliance
- Architecture decisions should be documented in ADRs
- Discrepancies between docs and code should be flagged
- Quarterly audits to ensure documentation reflects reality

---

## 7. Guidelines & Best Practices

### Writing Style
- **Clear:** Use simple, direct language
- **Concise:** Avoid unnecessary detail; link to detailed docs when needed
- **Consistent:** Use same terminology throughout
- **Audience-Aware:** Write for target audience (developers, architects, operators)

### Structure
- **Modular:** Each document should be independently understandable
- **Hierarchical:** Main index → Component docs → Implementation details
- **Cross-Referenced:** Link between related documents
- **Navigable:** Clear table of contents and section headings

### Technical Accuracy
- **Verified:** Information should be accurate and current
- **Rationale:** Explain *why* decisions were made, not just *what*
- **Trade-offs:** Document alternatives considered and rejected
- **Evidence:** Support claims with data or references

### Diagrams
- **Simple:** Avoid overcomplicated diagrams; split into multiple if needed
- **Labeled:** Every component should have a clear, descriptive label
- **Consistent:** Use same shapes and colors for same concepts across diagrams
- **Described:** Include text explanation alongside diagram

### Examples
```markdown
✅ GOOD:
"The API Gateway handles request routing, rate limiting, and authentication 
before forwarding to backend services. This reduces duplication of security 
logic across services."

❌ POOR:
"The API Gateway does routing."
```

```markdown
✅ GOOD:
Component Name: "Credit Assessment Engine"
Description: "Evaluates applicant creditworthiness using credit bureau data, 
income verification, and debt-to-income ratio calculation"

❌ POOR:
Component Name: "CreditAssessmentEngine"
Description: "Credit assessment"
```

---

## 8. Document Checklist

### Main Architecture Document Checklist
- [ ] Executive summary (< 2 pages)
- [ ] Complete navigation to all component docs
- [ ] Complete navigation to all NFR docs
- [ ] Complete navigation to all diagrams
- [ ] Technology stack listed with justification
- [ ] Key architectural decisions summarized
- [ ] Contact information for architecture team
- [ ] Version history
- [ ] Last updated date

### Component Document Checklist
- [ ] Clear purpose statement
- [ ] Technology stack documented
- [ ] Design patterns explained
- [ ] Major decisions and trade-offs documented
- [ ] Examples or code snippets where helpful
- [ ] Links to related components
- [ ] Performance characteristics noted
- [ ] Security considerations included
- [ ] Future enhancement notes

### NFR Document Checklist
- [ ] Targets are quantifiable and measurable
- [ ] Targets are realistic and achievable
- [ ] Measurement/monitoring approach defined
- [ ] Rationale for each target explained
- [ ] Impact on architecture documented
- [ ] Review schedule established
- [ ] Accountability assigned

### Diagram File Checklist
- [ ] Filename is descriptive and follows naming convention
- [ ] Mermaid format used (not images)
- [ ] Simple, clear component names
- [ ] Brief descriptions for each component
- [ ] Color coding consistent with other diagrams
- [ ] Legend provided if using special symbols
- [ ] Data flows and relationships clear
- [ ] Title and purpose stated
- [ ] Last updated date included

---

## 9. Tools & Resources

### Mermaid Diagram Resources
- [Mermaid Official Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [C4 Model with Mermaid](https://mermaid.js.org/ecosystem/integrations.html)

### Architecture Documentation Tools
- Markdown editors: VS Code, Obsidian
- Diagram tools: Mermaid Live, Lucidchart (for exporting as Mermaid)
- Version control: Git with GitHub/GitLab

### Reference Architecture Patterns
- [C4 Model](https://c4model.com/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Cloud Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)

---

## 10. Common Mistakes to Avoid

❌ **Don't:**
- Create long, overwhelming single documents (break into components)
- Use overly complex component names in diagrams
- Have diagrams without explanatory text
- Make architectural decisions without documenting them
- Forget to update diagrams when architecture changes
- Mix high-level and low-level details in same document
- Create documentation no one can find (ensure proper indexing)
- Document without linking to related documents

✅ **Do:**
- Break documentation into logical, modular pieces
- Use simple, descriptive component names
- Explain every diagram with text descriptions
- Document all architectural decisions with rationale
- Update diagrams as soon as architecture changes
- Separate concerns by layer (frontend, backend, data, etc.)
- Create clear navigation and index
- Cross-reference related documents frequently

---

## 11. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-17 | Initial solution architecture instructions |

---

**Document Classification:** Internal - Development Guidelines  
**Last Updated:** 2025-11-17  
**Maintained By:** Architecture Team  
**Review Frequency:** Quarterly

