# 🐳 Docker Deployment Guide

## Quick Start

### Development Mode

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Makefile (Recommended)

```bash
# See all available commands
make help

# Start services
make up

# View logs
make logs

# Stop services
make down
```

## Architecture

The application consists of three services:

1. **app** - FastAPI application (port 8000)
2. **postgres** - PostgreSQL database (port 5432)
3. **redis** - Redis cache (port 6379)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
APP_NAME=Service Order Management System
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=false

# Database
POSTGRES_USER=enerbit
POSTGRES_PASSWORD=enerbit123
POSTGRES_DB=enerbit_db
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
REDIS_DB=0

# Security
ALLOWED_ORIGINS=*
RATE_LIMIT_PER_MINUTE=100
SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO
```

## Common Commands

### Service Management

```bash
# Build images
make build

# Start services
make up

# Restart services
make restart

# Stop services
make down

# View service status
make status
```

### Logs and Debugging

```bash
# View all logs
make logs

# View specific service logs
make logs service=app
make logs service=postgres
make logs service=redis

# Open shell in app container
make shell

# Open PostgreSQL shell
make db-shell

# Open Redis CLI
make redis-shell
```

### Database Migrations

```bash
# Run migrations
make migrate

# Create new migration
make migrate-create msg="add new table"
```

### Health Checks

```bash
# Check service health
make health

# Or manually
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Production Deployment

### Using Production Configuration

```bash
# Start in production mode
make prod-up

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production Checklist

- [ ] Update `.env` with production values
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `ALLOWED_ORIGINS` with specific domains
- [ ] Set `DEBUG=false`
- [ ] Use strong database passwords
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## Dockerfile Details

### Multi-Stage Build

The Dockerfile uses a multi-stage build:

1. **Builder stage**: Installs dependencies
2. **Runtime stage**: Minimal production image

Benefits:

- Smaller final image size
- Faster builds with layer caching
- Improved security (no build tools in production)

### Security Features

- Non-root user (appuser)
- Minimal base image (python:3.11-slim)
- No unnecessary packages
- Health checks enabled

## Troubleshooting

### Services won't start

```bash
# Check logs
make logs

# Check service status
make status

# Restart services
make restart
```

### Database connection issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
make logs service=postgres

# Test connection
make db-shell
```

### Redis connection issues

```bash
# Check Redis is running
docker-compose ps redis

# Check Redis logs
make logs service=redis

# Test connection
make redis-shell
```

### Port conflicts

If ports are already in use, update `.env`:

```env
APP_PORT=8001
POSTGRES_PORT=5433
REDIS_PORT=6380
```

## Cleanup

```bash
# Remove containers and volumes
make clean

# Or manually
docker-compose down -v --rmi local
```

## Monitoring

### Container Stats

```bash
# View resource usage
docker stats

# View specific container
docker stats enerbit-app
```

### Health Endpoints

- `/health` - Liveness check (app is running)
- `/ready` - Readiness check (dependencies are healthy)

## Networking

All services communicate through the `enerbit-network` bridge network.

Internal hostnames:

- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `app` - FastAPI application

## Volumes

Persistent data is stored in Docker volumes:

- `postgres_data` - PostgreSQL data
- `redis_data` - Redis data

### Backup Volumes

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U enerbit enerbit_db > backup.sql

# Restore PostgreSQL
docker-compose exec -T postgres psql -U enerbit enerbit_db < backup.sql
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker-compose build
      - name: Run tests
        run: docker-compose run app pytest
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
