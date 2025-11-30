.PHONY: help setup dev backend frontend test lint format clean docker-build docker-up docker-down docker-logs docker-ps health-check run-all install-dev

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)MoneySplit - Development & Deployment Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(NC)"
	@echo "  make setup              - Install all dependencies (backend + frontend)"
	@echo "  make install-dev        - Install development dependencies only"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@echo "  make backend            - Run backend API server (http://localhost:8000)"
	@echo "  make frontend           - Run frontend React app (http://localhost:3000)"
	@echo "  make dev                - Run backend and frontend (requires 2 terminals)"
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@echo "  make test               - Run all tests with coverage"
	@echo "  make test-fast          - Run tests without coverage report"
	@echo "  make test-backend       - Run backend tests only"
	@echo "  make test-frontend      - Run frontend tests only"
	@echo "  make lint               - Run linting (pylint, flake8, ESLint)"
	@echo "  make format             - Format code with black and prettier"
	@echo "  make coverage           - Generate HTML coverage report"
	@echo ""
	@echo "$(GREEN)Docker Commands:$(NC)"
	@echo "  make docker-build       - Build Docker images"
	@echo "  make docker-up          - Start containers with docker-compose"
	@echo "  make docker-down        - Stop and remove containers"
	@echo "  make docker-logs        - View container logs"
	@echo "  make docker-ps          - Show running containers"
	@echo "  make docker-clean       - Remove all Docker images and volumes"
	@echo "  make docker-rebuild     - Rebuild and restart containers"
	@echo ""
	@echo "$(GREEN)Health & Diagnostics:$(NC)"
	@echo "  make health-check       - Check API health endpoints"
	@echo "  make metrics            - View Prometheus metrics"
	@echo "  make db-status          - Check database connection"
	@echo ""
	@echo "$(GREEN)Deployment:$(NC)"
	@echo "  make deploy-heroku      - Deploy to Heroku (requires Heroku CLI)"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean              - Remove Python cache, logs, coverage reports"
	@echo "  make clean-all          - Clean everything including Docker images"
	@echo ""

# ============================================================================
# SETUP COMMANDS
# ============================================================================

setup: install-backend install-frontend
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "Run '$(BLUE)make dev$(NC)' to start development"

install-backend:
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-frontend:
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install

install-dev: install-backend install-frontend
	@echo "$(GREEN)✓ All development dependencies installed$(NC)"

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

backend:
	@echo "$(BLUE)Starting backend API server...$(NC)"
	@echo "API will be available at: $(GREEN)http://localhost:8000$(NC)"
	@echo "API docs: $(GREEN)http://localhost:8000/docs$(NC)"
	@echo "Press Ctrl+C to stop"
	python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "$(BLUE)Starting frontend React app...$(NC)"
	@echo "Frontend will be available at: $(GREEN)http://localhost:3000$(NC)"
	@echo "Press Ctrl+C to stop"
	cd frontend && npm start

dev:
	@echo "$(BLUE)To run both backend and frontend:$(NC)"
	@echo "1. Open a new terminal and run: $(GREEN)make backend$(NC)"
	@echo "2. In another terminal run: $(GREEN)make frontend$(NC)"
	@echo "Or run them together with: $(GREEN)make docker-up$(NC)"

# ============================================================================
# TESTING & QUALITY COMMANDS
# ============================================================================

test:
	@echo "$(BLUE)Running all tests with coverage...$(NC)"
	python3 -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

test-fast:
	@echo "$(BLUE)Running tests (no coverage)...$(NC)"
	python3 -m pytest tests/ -v

test-backend:
	@echo "$(BLUE)Running backend tests...$(NC)"
	python3 -m pytest tests/ -v -k "not test_" --co -q || python3 -m pytest tests/ -v

test-frontend:
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test -- --watchAll=false --passWithNoTests

lint:
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "  • pylint..."
	-pylint Logic/ api/ tests/ --disable=all --enable=E,F
	@echo "  • flake8..."
	-flake8 Logic/ api/ tests/ --max-line-length=120
	@echo "$(GREEN)✓ Linting complete$(NC)"

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	@echo "  • black..."
	black Logic/ api/ tests/ --line-length=120
	@echo "  • prettier..."
	cd frontend && npm run prettier --write src/
	@echo "$(GREEN)✓ Formatting complete$(NC)"

coverage:
	@echo "$(BLUE)Generating HTML coverage report...$(NC)"
	python3 -m pytest tests/ --cov=. --cov-report=html
	@echo "$(GREEN)✓ Open htmlcov/index.html to view coverage$(NC)"

# ============================================================================
# DOCKER COMMANDS
# ============================================================================

docker-build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built successfully$(NC)"

docker-up:
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@sleep 3
	@echo "$(GREEN)✓ Containers started:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(GREEN)Services available at:$(NC)"
	@echo "  • Backend API: http://localhost:8000"
	@echo "  • Frontend: http://localhost:3000"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • Grafana: http://localhost:3001 (admin/admin)"

docker-down:
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers stopped$(NC)"

docker-logs:
	@echo "$(BLUE)Displaying container logs...$(NC)"
	docker-compose logs -f

docker-ps:
	@echo "$(BLUE)Running Docker containers:$(NC)"
	docker-compose ps

docker-clean:
	@echo "$(RED)Removing all Docker images and volumes...$(NC)"
	docker-compose down -v --rmi all
	@echo "$(GREEN)✓ Docker cleanup complete$(NC)"

docker-rebuild: docker-down docker-build docker-up
	@echo "$(GREEN)✓ Docker rebuild complete$(NC)"

# ============================================================================
# HEALTH & DIAGNOSTICS
# ============================================================================

health-check:
	@echo "$(BLUE)Checking API health endpoints...$(NC)"
	@echo ""
	@echo "1. Basic health check:"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "$(RED)✗ Failed$(NC)"
	@echo ""
	@echo "2. Readiness probe (database check):"
	@curl -s http://localhost:8000/health/ready | python3 -m json.tool || echo "$(RED)✗ Failed$(NC)"
	@echo ""
	@echo "3. Liveness probe:"
	@curl -s http://localhost:8000/health/live | python3 -m json.tool || echo "$(RED)✗ Failed$(NC)"
	@echo ""

metrics:
	@echo "$(BLUE)Prometheus metrics:$(NC)"
	@curl -s http://localhost:8000/metrics | head -20
	@echo ""
	@echo "View all metrics at: http://localhost:9090"

db-status:
	@echo "$(BLUE)Checking database status...$(NC)"
	python3 -c "from DB.setup import get_conn; conn = get_conn(); print('$(GREEN)✓ Database connected$(NC)'); conn.close()" || echo "$(RED)✗ Database connection failed$(NC)"

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy-heroku:
	@echo "$(BLUE)Deploying to Heroku...$(NC)"
	@echo "1. Logging in to Heroku..."
	heroku login
	@echo "2. Creating app (if needed)..."
	heroku create moneysplit-app || true
	@echo "3. Deploying code..."
	git push heroku main
	@echo "4. Running database setup..."
	heroku run python DB/setup.py
	@echo "$(GREEN)✓ Deployment complete!$(NC)"
	@echo "App URL: $$(heroku apps:info -a moneysplit-app -s | grep web-url)"

# ============================================================================
# CLEANUP
# ============================================================================

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf dist/ build/ *.egg-info/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean docker-clean
	@echo "$(GREEN)✓ Complete cleanup done$(NC)"

# ============================================================================
# DEFAULT TARGET
# ============================================================================

.DEFAULT_GOAL := help
