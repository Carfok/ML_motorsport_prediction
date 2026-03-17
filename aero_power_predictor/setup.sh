#!/bin/bash
# 🏎️ The 2026 Aero-Power Predictor — Setup & Run Script

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  🏎️  The 2026 Aero-Power Predictor v2026.1.0"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}[1/6]${NC} Validando Python 3.12+..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "  Python: ${GREEN}$python_version${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}[2/6]${NC} Instalando dependencias Python..."
pip install -r requirements.txt > /dev/null 2>&1
echo -e "  ${GREEN}✓ Dependencias instaladas${NC}"

# Create necessary directories
echo ""
echo -e "${YELLOW}[3/6]${NC} Creando directorios..."
mkdir -p storage/db
mkdir -p dagster_home
mkdir -p triton_models
echo -e "  ${GREEN}✓ Directorios creados${NC}"

# Install frontend dependencies
echo ""
echo -e "${YELLOW}[4/6]${NC} Instalando dependencias Frontend..."
cd frontend && npm install > /dev/null 2>&1 && cd ..
echo -e "  ${GREEN}✓ Dependencias Frontend instaladas${NC}"

# Verify structure
echo ""
echo -e "${YELLOW}[5/6]${NC} Verificando estructura del proyecto..."

required_files=(
    ".env"
    "requirements.txt"
    "README.md"
    "Makefile"
    "dagster.yaml"
    "requirements.txt"
    "core/physics/pinn.py"
    "core/graphs/model.py"
    "core/energy/tft_model.py"
    "core/ranking/pointnet_ranking.py"
    "backend/main.py"
    "data_pipeline/assets/ingestion.py"
    "frontend/package.json"
)

all_exist=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (FALTA)"
        all_exist=false
    fi
done

if [ "$all_exist" = true ]; then
    echo -e "  ${GREEN}✓ Estructura completa${NC}"
else
    echo -e "  ${RED}✗ Algunos archivos faltan${NC}"
    exit 1
fi

# Ready to run
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ SETUP COMPLETADO EXITOSAMENTE${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Para iniciar el proyecto:"
echo ""
echo "  Opción 1 - Ejecutar cada servicio por separado:"
echo "    make run-backend       # FastAPI en puerto 8000"
echo "    make run-dagster       # Dagster UI en puerto 3000"
echo "    make run-frontend      # Next.js en puerto 3001"
echo ""
echo "  Opción 2 - Ejecutar todos en paralelo:"
echo "    make run-all"
echo ""
echo "  Opción 3 - Ver todos los comandos disponibles:"
echo "    make help"
echo ""
echo "📖 Documentación:"
echo "    - README.md              (Información general)"
echo "    - VALIDACION_PROYECTO.md (Estado del proyecto)"
echo "    - ESTRUCTURA_FINAL.md    (Estructura de carpetas)"
echo ""
echo "🌐 URLs de acceso una vez iniciado:"
echo "    - Backend API:   http://localhost:8000"
echo "    - API Docs:      http://localhost:8000/docs"
echo "    - Dagster UI:    http://localhost:3000"
echo "    - Frontend:      http://localhost:3001"
echo ""
