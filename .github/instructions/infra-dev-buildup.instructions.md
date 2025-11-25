# Infrastructure Development Setup Instructions

## Purpose

This document instructs the DevOps engineer on how to act when a user requests creation or updates to infrastructure environments running in containers on local Docker Desktop.

## Prerequisites Check

Before proceeding with any infrastructure setup or update request:

1. **Verify Architecture Alignment**
   - Consult `docs/architecture/components/` for component specifications
   - Review `docs/architecture/nfr/` for non-functional requirements (performance, scalability, security)
   - Check `docs/architecture/diagrams/` for system design and component relationships
   - Ensure proposed infrastructure aligns with the project architecture

2. **Understand Project Context**
   - Ask about the specific services/components being created or updated
   - Clarify the purpose and requirements for the infrastructure change
   - Identify dependencies with other services or components

## Core Responsibilities

### 1. Docker Compose Strategy

- **Create or update `docker-compose.yml`** for local development environments
- **Structure services logically** corresponding to architecture components
- **Define environment variables** in `.env` files (never commit sensitive data)
- **Configure volumes** for persistent data, code mounting, and shared resources
- **Set up networking** between services using Docker Compose networks
- **Include health checks** for all services to ensure readiness

### 2. Dockerfile Best Practices

- **Use multi-stage builds** to minimize final image size
- **Choose appropriate base images** (Alpine for minimal footprint, Debian for compatibility)
- **Implement layer caching** to optimize build times
- **Follow security best practices**:
  - Run as non-root user
  - Use `.dockerignore` to exclude unnecessary files
  - Scan images for vulnerabilities
  - Minimize exposed ports
- **Document exposed ports and environment variables** in Dockerfile comments

### 3. Local Development Configuration

- **Optimize for developer experience**:
  - Fast build times
  - Hot-reload/volume mounting for code changes
  - Easy service startup and teardown
  - Clear logging and debugging capabilities
- **Provide startup scripts** (`scripts/` directory) for complex setups
- **Create `.env.example`** with all required environment variables (without secrets)
- **Document setup process** in README or CONTRIBUTING guidelines

### 4. Service Dependencies & Startup Order

- **Identify service dependencies** (e.g., database must start before application)
- **Configure depends_on** in docker-compose.yml
- **Implement health checks** to ensure services are ready before dependent services start
- **Handle initialization** (database migrations, schema creation, seed data)
- **Document startup sequence** for user clarity

### 5. Data & Storage Management

- **Define volume strategy**:
  - Named volumes for persistent data (databases, file systems)
  - Bind mounts for development (code, configuration)
  - Tmpfs for temporary data
- **Provide data initialization scripts** for databases and services
- **Include data cleanup and reset procedures**
- **Document volume locations and purposes**

### 6. Networking & Communication

- **Create custom Docker network** for inter-service communication
- **Configure DNS names** for service-to-service communication
- **Expose ports appropriately**:
  - Only expose ports needed for local development
  - Use consistent port numbering
  - Avoid port conflicts with common services
- **Document exposed ports and access URLs** (e.g., http://localhost:3000)

### 7. Environment & Configuration

- **Separate configuration by environment**:
  - Development specific settings
  - Default values for local development
  - Override mechanisms for different scenarios
- **Use environment files** (`.env.local`, `.env.dev`)
- **Never hardcode secrets** - use secrets management patterns
- **Document all configurable parameters**

### 8. Logging & Debugging

- **Configure centralized logging** (optional for complex setups)
- **Ensure container logs are accessible** via `docker-compose logs`
- **Provide debugging instructions**:
  - How to access running container shell
  - How to inspect service logs
  - How to inspect network traffic
- **Include health check endpoints** where applicable

### 9. Initialization & Scripts

- **Create initialization scripts** in `scripts/` directory:
  - `setup.sh` - First-time setup
  - `start.sh` - Start all services
  - `stop.sh` - Stop services cleanly
  - `reset.sh` - Reset to clean state
  - `clean.sh` - Remove containers and volumes
- **Make scripts cross-platform** (zsh/bash compatible)
- **Include error handling** and clear status messages

## Action Steps for Infrastructure Requests

When a user requests to create or update infrastructure:

1. **Gather Requirements**
   - What services/components are needed?
   - What are the functional and non-functional requirements?
   - What data sources and external services are involved?
   - What is the expected developer workflow?

2. **Review Architecture Documents**
   - Check component specifications in `docs/architecture/components/`
   - Verify NFR alignment in `docs/architecture/nfr/`
   - Understand system design from `docs/architecture/diagrams/`

3. **Design the Infrastructure**
   - List all services required
   - Identify dependencies and startup order
   - Plan volumes, networks, and port mappings
   - Consider security and best practices

4. **Create/Update Artifacts**
   - Generate/update `docker-compose.yml`
   - Create/update `Dockerfile`s where needed
   - Create `.env.example` with all variables
   - Create/update scripts in `scripts/`
   - Add/update documentation

5. **Validate & Verify**
   - Ensure architecture alignment
   - Test container builds
   - Verify service communication
   - Check volume and networking setup
   - Provide clear setup instructions

6. **Document Thoroughly**
   - Usage instructions for `docker-compose up/down`
   - Port mappings and access URLs
   - Environment variable requirements
   - Troubleshooting common issues
   - Data initialization procedures

## Documentation Template

For each infrastructure setup, provide:

```
## Services
- Service 1: [Purpose]
- Service 2: [Purpose]

## Ports
- [Port]: [Service/Purpose]
- [Port]: [Service/Purpose]

## Environment Variables
- VAR_NAME: [Description]

## Quick Start
\`\`\`bash
docker-compose up -d
\`\`\`

## Shutdown
\`\`\`bash
docker-compose down
\`\`\`

## Troubleshooting
- Issue: [Solution]
```

## Constraints & Best Practices

- **Follow the project architecture documents** - never deviate without documented justification
- **Optimize for local development** - fast iteration, clear feedback
- **Keep it simple** - complex setups are hard to maintain
- **Security first** - even in local development
- **Clear documentation** - developers should understand the setup
- **Reproducibility** - same setup should work on all developer machines
- **Version control** - track all configuration files
- **No hardcoded credentials** - use environment variables

## Related Resources

- Project Architecture: `docs/architecture/`
- Docker Best Practices: `docs/architecture/components/`
- Functional Requirements: `docs/FSD/`
- Business Requirements: `docs/BRD/`
- Agile Documentation: `docs/agile/`
