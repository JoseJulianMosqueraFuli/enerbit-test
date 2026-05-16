# 🚀 Service Order Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg?style=flat)](https://www.sqlalchemy.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/JoseJulianMosqueraFuli/enerbit-test/actions/workflows/ci.yml/badge.svg)](https://github.com/JoseJulianMosqueraFuli/enerbit-test/actions/workflows/ci.yml)
[![Security](https://github.com/JoseJulianMosqueraFuli/enerbit-test/actions/workflows/security.yml/badge.svg)](https://github.com/JoseJulianMosqueraFuli/enerbit-test/actions/workflows/security.yml)

A production-ready FastAPI application for efficiently managing customers, service orders, and analytics. Built with modern Python practices, comprehensive error handling, structured logging, and enterprise-grade security.

## ✨ Features

### 🎯 Core Functionality

- **Customer Management**: Complete CRUD operations for customer records
- **Work Order Tracking**: Create, update, and monitor service orders
- **Real-time Analytics**: Advanced data analysis and reporting capabilities
- **Event Streaming**: Redis-based event streaming with circuit breaker protection

### 🔒 Security & Reliability

- **Rate Limiting**: Configurable request throttling (default: 100 req/min)
- **Security Headers**: HSTS, CSP, X-Frame-Options, and more
- **CORS Protection**: Environment-specific origin validation
- **Circuit Breaker**: Automatic failover for external services
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes

### 📊 Observability

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Request Tracing**: End-to-end request tracking across services
- **Sensitive Data Redaction**: Automatic removal of passwords, tokens, and secrets from logs
- **Performance Monitoring**: Request duration tracking and database query logging

### 🏗️ Architecture

- **SQLAlchemy 2.0+**: Modern ORM with type safety and async support
- **Pydantic V2**: Advanced data validation and settings management
- **Repository Pattern**: Clean separation of concerns
- **Dependency Injection**: FastAPI's built-in DI system
- **Connection Pooling**: Optimized database connections

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

### Option 1: Docker (Recommended)

- **Docker** - [Download](https://www.docker.com/get-started)
- **Docker Compose** - Included with Docker Desktop

### Option 2: Local Development

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Poetry** - [Download](https://python-poetry.org/docs/#installation)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis 7.0+** - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)

## Installation

### Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone git@github.com:JoseJulianMosqueraFuli/enerbit-test.git
cd enerbit-test

# Start all services
cd docker
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

That's it! The API is now running at http://localhost:8000

See [DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for detailed Docker documentation.

### Manual Installation

#### 1. Clone the Repository

```bash
git clone git@github.com:JoseJulianMosqueraFuli/enerbit-test.git
cd enerbit-test
```

#### 2. Install Dependencies with Poetry

```bash
poetry install
```

This creates a virtual environment and installs all dependencies automatically.

To activate the virtual environment:

```bash
poetry shell
```

Or run commands directly with Poetry:

```bash
poetry run python main.py
poetry run pytest
```

#### 3. Set Up Database

Create a PostgreSQL database:

```bash
createdb service_orders
```

Or using psql:

```sql
CREATE DATABASE service_orders;
```

#### 4. Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (see [Configuration](#configuration) section).

## Configuration

The application uses environment variables for configuration. All settings are validated using Pydantic.

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/service_orders

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Optional Variables

```bash
# Application
APP_NAME=Service Order Management System
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production, test
DEBUG=False

# Database Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_PRE_PING=True

# Security
ALLOWED_ORIGINS=["*"]  # Use specific origins in production
RATE_LIMIT_PER_MINUTE=100
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# AWS (for deployment)
AWS_REGION=us-east-1
```

### Environment Validation

The application validates all settings on startup:

- ✅ Environment must be: `development`, `staging`, `production`, or `test`
- ✅ Log level must be valid
- ✅ Wildcard CORS (`*`) is blocked in production
- ✅ Database URL format is validated

## Running the Application

### Using Docker (Recommended)

```bash
# Navigate to docker directory
cd docker

# Start all services
make up

# View logs
make logs

# Stop services
make down

# See all commands
make help
```

### Manual Development Mode

```bash
# Using uvicorn with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the main script
python main.py
```

### Production Mode

```bash
# With Docker
cd docker && make prod-up

# Manual
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Readiness Check**: http://localhost:8000/ready

## API Documentation

### Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Customers

```http
GET    /customers          # List all customers
POST   /customers          # Create new customer
GET    /customers/{id}     # Get customer by ID
PUT    /customers/{id}     # Update customer
DELETE /customers/{id}     # Delete customer
```

#### Work Orders

```http
GET    /work-orders              # List all work orders
POST   /work-orders              # Create new work order
GET    /work-orders/{id}         # Get work order by ID
PUT    /work-orders/{id}         # Update work order
DELETE /work-orders/{id}         # Delete work order
GET    /work-orders/status/{status}  # Filter by status
```

#### Analytics

```http
GET    /analytics/summary        # Get analytics summary
GET    /analytics/customers      # Customer analytics
GET    /analytics/work-orders    # Work order analytics
```

### Request/Response Examples

#### Create Customer

```bash
curl -X POST "http://localhost:8000/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St",
    "is_active": true
  }'
```

#### Create Work Order

```bash
curl -X POST "http://localhost:8000/work-orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid-here",
    "title": "Installation Service",
    "status": "new"
  }'
```

## Project Structure

```
enerbit-test/
├── main.py                      # Application entry point
├── database.py                  # Database configuration
├── settings.py                  # Pydantic settings management
├── config.py                    # Legacy config (backward compatibility)
├── error_handlers.py            # Custom exception handlers
├── logger.py                    # Structured logging
├── middleware.py                # Custom middleware
├── security_headers.py          # Security headers middleware
├── health_check.py              # Health and readiness endpoints
│
├── models/                      # SQLAlchemy models
│   ├── __init__.py
│   ├── customer.py              # Customer model
│   └── work_order.py            # Work order model
│
├── repositories/                # Data access layer
│   ├── __init__.py
│   ├── customer_repository.py   # Customer CRUD operations
│   ├── work_order_repository.py # Work order CRUD operations
│   └── analytics_repository.py  # Analytics queries
│
├── routers/                     # API endpoints
│   ├── __init__.py
│   ├── customer_router.py       # Customer endpoints
│   ├── work_order_router.py     # Work order endpoints
│   └── analytics_router.py      # Analytics endpoints
│
├── schemas/                     # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py               # Request/response models
│
├── tasks/                       # Background tasks
│   ├── __init__.py
│   └── redis.py                 # Redis event streaming
│
├── alembic/                     # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── docker/                      # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── .dockerignore
│   ├── docker-entrypoint.sh
│   └── Makefile
│
├── docs/                        # Documentation
│   └── DOCKER_GUIDE.md
│
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_health.py
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
├── README.md                    # This file
└── PROJECT_STATUS.md            # Project status report
```

## Development

### Code Quality Tools

The project includes several code quality tools:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with pylint
pylint **/*.py

# Type checking with mypy
mypy .

# Remove unused imports with autoflake
autoflake --remove-all-unused-imports --recursive --in-place .
```

### Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Dependencies

```bash
# Install new package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_customers.py
```

### Test Structure

```
tests/
├── conftest.py              # Test fixtures
├── test_customers.py        # Customer tests
├── test_work_orders.py      # Work order tests
└── test_analytics.py        # Analytics tests
```

## Deployment

### Docker Deployment

#### Development

```bash
# Navigate to docker directory
cd docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Production

```bash
# Navigate to docker directory
cd docker

# Build and start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or using Makefile
make prod-up
```

See [DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for comprehensive Docker documentation.

### Docker Features

- Multi-stage builds for optimized image size
- Health checks for all services
- Automatic service dependencies
- Volume persistence for data
- Network isolation
- Non-root user for security
- Production-ready configuration

### AWS Deployment (Planned)

The project includes Terraform configurations for AWS deployment:

- ECS Fargate for container orchestration
- RDS PostgreSQL for database
- ElastiCache Redis for caching
- Application Load Balancer
- CloudWatch for monitoring

See `.kiro/specs/fastapi-refactor-deployment/` for detailed deployment plans.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all modules, classes, and functions
- Maintain test coverage above 80%
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Jose Julian Mosquera Fuli**

- GitHub: [@JoseJulianMosqueraFuli](https://github.com/JoseJulianMosqueraFuli)
- LinkedIn: [Jose Julian Mosquera Fuli](https://www.linkedin.com/in/jose-julian-mosquera-fuli/)

## Acknowledgments

- Built for enerBit technical assessment
- FastAPI framework by Sebastián Ramírez
- SQLAlchemy ORM
- Pydantic for data validation

## Support

For support, please open an issue in the GitHub repository or contact the author.

## CI/CD & Security

This project uses GitHub Actions for continuous integration and security scanning:

### Workflows

| Workflow | Description | Triggers |
|----------|-------------|----------|
| **CI - Tests & Linting** | Runs tests, linting, and type checking | Push, PR |
| **Security Scan** | SAST, dependency scanning, secret detection, CodeQL | Push, PR, Weekly |
| **Docker Security** | Container image scanning, Dockerfile linting | Push, PR, Weekly |

### Security Scans

- **SAST**: Bandit static analysis
- **Dependencies**: pip-audit + Safety
- **Secrets**: Gitleaks
- **Code Analysis**: CodeQL
- **Containers**: Trivy (filesystem + Docker image)
- **Dockerfile**: Hadolint
- **Auto-updates**: Dependabot (weekly)

### Running Security Checks Locally

```bash
# Install security tools
poetry run pip install bandit pip-audit safety

# Run SAST scan
poetry run bandit -r . --exclude venv,.venv,tests,alembic -ll

# Scan dependencies
poetry export -f requirements.txt --output req.txt --without-hashes --with dev
poetry run pip-audit -r req.txt
poetry run safety check -r req.txt

# Scan Dockerfile
docker run --rm -i hadolint/hadolint < docker/Dockerfile
```

---

Made with Python
