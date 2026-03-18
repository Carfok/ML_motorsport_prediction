.PHONY: help install dev-install run-backend run-dagster run-frontend run-all clean test setup run-pipeline run-services run-full-system

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
    @echo "🚀 Iniciando sistema completo..."
    # Ingesta primero (bloqueante para asegurar datos)
    python -m dagster asset materialize --select "*" -f data_pipeline/setup.py
    # Backend en segundo plano (Sintaxis Windows compatible si se usa Git Bash)
    (python backend/main.py &) 
    # Frontend
    cd frontend && npm run dev

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

setup:
    @echo "📦 Instalando dependencias de Python y Node..."
    pip install -r requirements.txt
    cd frontend && npm install
    @echo "✅ Setup completado."

# 2. Procesamiento de datos (Dagster)
# Ejecuta la ingesta y creación del grafo antes de que los modelos puedan predecir
run-pipeline:
    @echo "🔄 Ejecutando Pipeline de Datos (Dagster)..."
    dagster asset materialize --select "*" -f data_pipeline/setup.py

# 3. Servicios de Inferencia y Backend
# Nota: Triton debe estar corriendo (usualmente vía Docker)
run-services:
    @echo "🚀 Iniciando API Backend..."
    python backend/main.py &

# 4. Interfaz de Usuario
run-ui:
    @echo "🎨 Iniciando Frontend Next.js..."
    cd frontend && npm run dev

# 🔥 EL COMANDO MAESTRO
# Este comando ejecuta todo en el orden lógico de creación
dev:
    @echo "🏁 Arrancando The 2026 Aero-Power Predictor..."
    $(MAKE) run-pipeline
    @sleep 5
    $(MAKE) run-services &
    @sleep 3
    $(MAKE) run-ui
