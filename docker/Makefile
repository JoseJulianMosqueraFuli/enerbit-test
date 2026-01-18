.PHONY: help build up down restart logs shell test clean migrate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📊 API: http://localhost:8000"
	@echo "📚 Docs: http://localhost:8000/docs"
	@echo "🔍 Health: http://localhost:8000/health"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs (use 'make logs service=app' for specific service)
	@if [ -z "$(service)" ]; then \
		docker-compose logs -f; \
	else \
		docker-compose logs -f $(service); \
	fi

shell: ## Open shell in app container
	docker-compose exec app /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U enerbit -d enerbit_db

redis-shell: ## Open Redis CLI
	docker-compose exec redis redis-cli

migrate: ## Run database migrations
	docker-compose exec app alembic upgrade head

migrate-create: ## Create new migration (use 'make migrate-create msg="description"')
	docker-compose exec app alembic revision --autogenerate -m "$(msg)"

test: ## Run tests
	docker-compose exec app pytest

clean: ## Remove containers, volumes, and images
	docker-compose down -v --rmi local
	@echo "✅ Cleaned up!"

prod-up: ## Start services in production mode
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

status: ## Show status of all services
	docker-compose ps

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "❌ App not responding"
	@curl -s http://localhost:8000/ready | python -m json.tool || echo "❌ Dependencies not ready"
