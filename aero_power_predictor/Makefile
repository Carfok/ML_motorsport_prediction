.PHONY: help install dev-install run-backend run-dagster run-frontend run-all clean test

help:
	@echo "🏎️ The 2026 Aero-Power Predictor — Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install Python & Node dependencies"
	@echo "  make dev-install      - Install dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend      - Start FastAPI server (port 8000)"
	@echo "  make run-dagster      - Start Dagster UI (port 3000)"
	@echo "  make run-frontend     - Start Next.js frontend (port 3000)"
	@echo "  make run-all          - Start all services (background)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Remove cache & build files"
	@echo "  make test             - Run tests"

install:
	pip install -r requirements.txt
	cd frontend && npm install

dev-install: install
	pip install pytest pytest-cov black flake8
	cd frontend && npm install --save-dev

run-backend:
	python backend/main.py

run-dagster:
	dagster dev -f data_pipeline/setup.py

run-frontend:
	cd frontend && npm run dev

run-all:
	@echo "Starting backend, dagster, and frontend..."
	python backend/main.py &
	dagster dev -f data_pipeline/setup.py &
	cd frontend && npm run dev &

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	cd frontend && rm -rf .next node_modules
	rm -rf dagster_home

test:
	pytest tests/ -v --cov

lint:
	black . --check
	flake8 core/ backend/ data_pipeline/
