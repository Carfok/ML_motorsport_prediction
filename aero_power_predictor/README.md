# 🏎️ The 2026 Aero-Power Predictor

Sistema de predicción de rendimiento para la temporada 2026 de Fórmula 1, utilizando arquitecturas avanzadas de IA para análisis aerodinámico y de potencia.

## 🚀 Arquitectura
- **Core IA**: PINNs (Física), GNNs (Grafos), TFT (Series Temporales) y PointNet++ (Nubes de puntos) para análisis físico y estratégico.
- **Pipeline**: Dagster + DuckDB para procesamiento de telemetría de alta frecuencia.
- **Inferencia**: NVIDIA Triton + FastAPI.
- **Visualización**: Next.js 15 y Three.js para renderizado de circuitos y telemetría 3D.

## 📋 Requisitos Previos

- **Python**: 3.12 o superior.
- **Node.js**: 18.x o superior (para el frontend).
- **Herramientas**: `make` (opcional, pero recomendado), `npm`.
- **Hardware**: Recomendado GPU NVIDIA con soporte CUDA para modelos de IA.

## 🛠️ Instalación y Configuración

Puedes realizar la instalación automática usando el script de configuración:

```bash
# Dar permisos de ejecución
chmod +x setup.sh

# Ejecutar el setup (instala dependencias de Python y Node, y crea directorios)
./setup.sh
```

O realizar la instalación manual paso a paso:

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/Carfok/ML_motorsport_prediction.git
    cd ML_motorsport_prediction/aero_power_predictor
    ```

2.  **Configurar entorno Python**:
    ```bash
    python -m venv venv
    # En Windows: venv\Scripts\activate
    # En Linux/Mac: source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configurar Frontend**:
    ```bash
    cd frontend
    npm install
    cd ..
    ```

4.  **Configurar variables de entorno**:
    Crea un archivo `.env` basado en la configuración necesaria para el backend y frontend (ver carpetas respectivas).

## 📈 Ejecución del Proyecto

El proyecto se compone de tres servicios principales que deben estar activos:

### Opción 1: Usando Makefile (Recomendado)

```bash
# Ejecutar todos los servicios en paralelo
make run-all

# O ejecutar individualmente
make run-backend    # Puerto 8000
make run-dagster    # Puerto 3000
make run-frontend   # Puerto 3001
```

### Opción 2: Ejecución Manual

-   **Backend (FastAPI)**:
    ```bash
    python backend/main.py
    ```
    Accede a la documentación en `http://localhost:8000/docs`.

-   **Pipeline de Datos (Dagster)**:
    ```bash
    dagster dev -f data_pipeline/setup.py
    ```
    Accede a Dagit en `http://localhost:3000`.

-   **Frontend (Next.js)**:
    ```bash
    cd frontend
    npm run dev
    ```
    Accede a la interfaz en `http://localhost:3001`. (Nota: ajustado a 3001 para evitar conflictos con Dagster).

## 📂 Estructura del Proyecto

- `backend/`: API principal con FastAPI y cliente Triton.
- `core/`: Implementación de modelos (PINN, GNN, TFT, PointNet++).
- `data_pipeline/`: Orquestación con Dagster y assets de ingesta.
- `frontend/`: Interfaz de usuario con Next.js y Three.js.
- `storage/`: Base de datos DuckDB y persistencia.

## 📄 Licencia
Este proyecto es propiedad de Carfok. Todos los derechos reservados.
