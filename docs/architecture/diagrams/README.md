# Architecture Diagrams

**Last Updated:** November 18, 2025

This directory contains PlantUML architecture diagrams for the Premium Customer Notification System. All diagrams are in PlantUML format and can be rendered by various tools.

---

## Diagrams

### 1. C4 Context Diagram (`c4-context.plantuml`)

**Purpose:** Show system boundaries and external actors

**Shows:**
- Premium Customer Notification System as a black box
- External actors: Premium Customers, Operations Manager
- External systems: Core Banking System, SMS Carrier
- High-level interactions

**Usage:** Use this to explain the system to non-technical stakeholders

---

### 2. C4 Container Diagram (`c4-container.plantuml`)

**Purpose:** Decompose the system into major containers/components

**Shows:**
- Five core microservices:
  - Balance Monitoring Service
  - Qualification Engine
  - Notification Service
  - Delivery Tracking Service
  - Reporting Service
- Shared infrastructure:
  - PostgreSQL Database
  - Redis Cache
  - RabbitMQ Message Queue
- External system integrations
- Event-based communication between services

**Usage:** Use this to explain the system architecture to developers

---

### 3. Data Flow Diagram (`data-flow.plantuml`)

**Purpose:** Illustrate how data moves through the system over time

**Shows:**
- Daily balance check process (22:00)
- Month-end qualification calculation (00:01)
- SMS notification generation and dispatch (09:00)
- Delivery status polling (every 2 hours)
- Monthly report generation
- Event-driven communication
- Database operations
- External API interactions

**Usage:** Use this for process training and understanding system flow

---

### 4. Deployment Diagram (`deployment.plantuml`)

**Purpose:** Show the physical/logical infrastructure deployment

**Shows:**
- Kubernetes cluster components
- Load balancer and ingress
- Application pods (5 services)
- Database cluster architecture:
  - Primary (read/write)
  - Hot standby (failover)
  - Read replicas (analytics/reporting)
- Redis cluster for caching
- RabbitMQ cluster for messaging
- Monitoring infrastructure (Prometheus, Grafana, ELK)
- External systems

**Usage:** Use this for infrastructure planning and deployment documentation

---

## Rendering Options

### Option 1: PlantUML Online Editor
1. Visit: https://www.plantuml.com/plantuml/uml/
2. Copy and paste diagram content
3. View rendered diagram

### Option 2: VS Code Extensions
- Install: PlantUML extension
- Right-click on `.plantuml` file → "Show PlantUML Preview"

### Option 3: Command Line
```bash
# Install plantuml
brew install plantuml

# Render to PNG
plantuml c4-context.plantuml -o output/

# Render to SVG
plantuml -tsvg c4-context.plantuml -o output/
```

### Option 4: IntelliJ IDEA
- Built-in PlantUML support
- Right-click file → "Open Diagram" or "View Diagram"

---

## Color Scheme

| Color | Meaning |
|-------|---------|
| Green | Application Services |
| Orange | Databases / Storage |
| Purple | Monitoring / Observability |
| Blue | Load Balancing / Network |
| Yellow | Caching |
| Pink | Message Queue |

---

## Updates & Maintenance

### When to Update Diagrams

- When adding/removing services
- When changing integration points
- When modifying deployment architecture
- When updating data flows
- When adding new infrastructure components

### How to Update

1. Edit the appropriate `.plantuml` file
2. Render to verify changes
3. Commit to version control with descriptive message
4. Update this README if adding new diagrams
5. Notify architecture team of changes

---

## Diagram Details

### C4 Context
- **Actors:** 2 (Customer, Operations Manager)
- **Systems:** 1 core + 2 external
- **Interactions:** 4 major flows

### C4 Container
- **Services:** 5 microservices
- **Databases:** 1 PostgreSQL
- **Caches:** 1 Redis
- **Queues:** 1 RabbitMQ
- **Integrations:** 2 external APIs

### Data Flow
- **Processes:** 5 major workflows
- **Events:** 4 event types
- **Database Tables:** 5 primary tables
- **External Systems:** 2 integrations

### Deployment
- **Kubernetes Nodes:** 3+ (scalable)
- **Application Pods:** 5 services × 1-N replicas
- **Databases:** 1 Primary + 1 Standby + 2 Replicas
- **Cache Nodes:** 3+ for clustering
- **Queue Nodes:** 3 for clustering

---

## Legend

```
Flow Types:
→ Synchronous request/response
⇢ Asynchronous event
↔ Bidirectional communication
⇠ Data replication

Architecture Elements:
[Box] External System
{Box} Internal Component
(Cylinder) Database
[Cluster] Distributed Component
```

---

**For questions or updates, contact the Architecture team.**
