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

3. **Isolation & Port Management**
   - **Check existing Docker containers** on the host Docker Desktop for port conflicts
   - **Use Docker Compose project naming** to isolate this workspace's containers
   - **Set custom ports** if default ports are already in use by unrelated containers
   - **Never modify or stop containers** that belong to other projects
   - **Document port mappings** to avoid future conflicts

## Core Responsibilities

### 1. Docker Compose Strategy

- **Create or update `docker-compose.yml`** for local development environments
- **Set project name explicitly** using `COMPOSE_PROJECT_NAME` environment variable or `-p` flag to isolate containers
- **Structure services logically** corresponding to architecture components
- **Define environment variables** in `.env` files (never commit sensitive data)
- **Configure volumes** for persistent data, code mounting, and shared resources
- **Set up networking** between services using Docker Compose networks (isolated from other projects)
- **Include health checks** for all services to ensure readiness
- **Use custom network names** prefixed with project name to avoid conflicts (e.g., `meetupdemo-network`)

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

- **Create custom Docker network** for inter-service communication, isolated from other projects
- **Use project-specific network naming** to prevent conflicts (e.g., `meetupdemo-backend`)
- **Configure DNS names** for service-to-service communication
- **Expose ports appropriately** with conflict detection:
  - Check for port conflicts with `docker ps` or `lsof -i :<port>`
  - Only expose ports needed for local development
  - If default ports are busy, use alternative port numbers
  - Document port alternatives and environment variable overrides
  - Use `.env.local` to override ports for specific developer machines
- **Use port ranges** that minimize conflicts (e.g., 5000-5999 for this project)
- **Document exposed ports and access URLs** with alternative port info (e.g., http://localhost:3000 or http://localhost:3010 if port busy)

### 7. Environment & Configuration

- **Separate configuration by environment**:
  - Development specific settings
  - Default values for local development
  - Override mechanisms for different scenarios
- **Use environment files** (`.env`, `.env.local`, `.env.dev`):
  - `.env` - Default settings (committed to repo)
  - `.env.local` - Local machine overrides (NOT committed, for port customization)
  - `.env.dev` - Development environment specific
- **Support port customization** via environment variables:
  - Define default ports in `.env`
  - Allow overrides via `.env.local` for port conflicts
  - Document custom port setup in README
- **Never hardcode secrets** - use secrets management patterns
- **Document all configurable parameters** including port alternatives

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

1. **Check Docker Environment**
   - Run `docker ps` to identify running containers
   - Check for port conflicts with `lsof -i :<port>` or `docker port <container>`
   - Identify which ports are in use by unrelated containers
   - Note available port ranges for this project

2. **Gather Requirements**
   - What services/components are needed?
   - What are the functional and non-functional requirements?
   - What data sources and external services are involved?
   - What is the expected developer workflow?
   - Are there specific ports that must be used?

3. **Review Architecture Documents**
   - Check component specifications in `docs/architecture/components/`
   - Verify NFR alignment in `docs/architecture/nfr/`
   - Understand system design from `docs/architecture/diagrams/`

4. **Design the Infrastructure**
   - List all services required
   - Identify dependencies and startup order
   - Plan volumes, networks, and port mappings with conflict detection
   - Select alternative ports if defaults are in use
   - Use project-specific naming for networks and volumes
   - Consider security and best practices

5. **Create/Update Artifacts**
   - Generate/update `docker-compose.yml` with project naming and custom ports
   - Set `COMPOSE_PROJECT_NAME` environment variable
   - Create/update `Dockerfile`s where needed
   - Create `.env` with default ports and settings
   - Create `.env.example` with all variables (for committed version)
   - Create `.env.local.example` showing custom port overrides
   - Create/update scripts in `scripts/`
   - Add/update documentation with port alternatives

6. **Validate & Verify**
   - Ensure architecture alignment
   - Verify no conflicts with existing containers
   - Test container builds with project isolation
   - Verify service communication within project network
   - Check volume and networking setup
   - Test port customization via `.env.local`
   - Provide clear setup instructions including port options

7. **Document Thoroughly**
   - Usage instructions for `docker-compose up/down`
   - Port mappings and access URLs (default and alternative)
   - Environment variable requirements and customization
   - How to detect and resolve port conflicts
   - Troubleshooting common issues
   - Data initialization procedures
   - Project isolation approach

## Documentation Template

For each infrastructure setup, provide:

```
## Services
- Service 1: [Purpose]
- Service 2: [Purpose]

## Default Ports
- [Port]: [Service/Purpose]
- [Port]: [Service/Purpose]

## Custom Port Configuration
If default ports are in use on your machine:
1. Copy `.env` to `.env.local`
2. Update port values in `.env.local`:
   \`\`\`
   SERVICE_PORT=5001  # Changed from 5000
   DB_PORT=5433       # Changed from 5432
   \`\`\`
3. Docker Compose will use `.env.local` automatically

## Check for Port Conflicts
\`\`\`bash
# Check if port is in use
lsof -i :5000
docker ps  # List running containers
\`\`\`

## Environment Variables
- VAR_NAME: [Description]
- SERVICE_PORT: [Default Port] (override in .env.local if busy)

## Quick Start
\`\`\`bash
# First time setup
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
\`\`\`

## Shutdown
\`\`\`bash
docker-compose down
\`\`\`

## Project Isolation
- Container names prefixed with project name
- Network isolated from other Docker projects
- Safe to run alongside unrelated containers

## Troubleshooting
- Port already in use: [Solution - use .env.local]
- Container won't start: [Check logs and architecture alignment]
- Service communication issues: [Check custom network configuration]
```

## Constraints & Best Practices

- **Follow the project architecture documents** - never deviate without documented justification
- **Optimize for local development** - fast iteration, clear feedback
- **Keep it simple** - complex setups are hard to maintain
- **Security first** - even in local development
- **Clear documentation** - developers should understand the setup
- **Reproducibility** - same setup should work on all developer machines
- **Version control** - track all configuration files (except `.env.local`)
- **No hardcoded credentials** - use environment variables
- **Project isolation** - use explicit naming to avoid affecting unrelated containers
- **Port conflict handling** - always check for conflicts and provide alternatives
- **Never interfere with other projects** - only manage containers created by this project
- **Document port customization** - make it easy for developers to override ports

## Related Resources

- Project Architecture: `docs/architecture/`
- Docker Best Practices: `docs/architecture/components/`
- Functional Requirements: `docs/FSD/`
- Business Requirements: `docs/BRD/`
- Agile Documentation: `docs/agile/`
