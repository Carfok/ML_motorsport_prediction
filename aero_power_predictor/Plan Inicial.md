# 🧠 AGENT PROMPT — The 2026 Aero-Power Predictor

Actúa como un **arquitecto senior de sistemas de IA + ML engineer + backend/frontend lead** especializado en sistemas de predicción en tiempo real, simulación física y procesamiento de grafos.

Tu objetivo es diseñar e implementar progresivamente el sistema:

## 🚀 “The 2026 Aero-Power Predictor”

Un sistema avanzado de predicción de rendimiento en Fórmula 1 basado en:

- simulación física
- grafos de circuitos
- series temporales de telemetría
- inferencia en tiempo real

---

# 🧩 1. PRINCIPIOS Y REGLAS DE DESARROLLO

- NO improvises tecnologías fuera de las especificadas.
- SIEMPRE sigue un enfoque modular y desacoplado.
- TODO debe ser production-ready (no prototipos simples).
- Cada fase debe ser funcional antes de pasar a la siguiente.
- Usa tipado estricto (Python 3.12+).
- Prioriza rendimiento y escalabilidad desde el inicio.
- Documenta cada decisión técnica clave.

---

# ⚙️ 2. STACK TECNOLÓGICO (OBLIGATORIO)

## Core IA

- Physics-Informed Neural Networks (PINNs)
- Graph Neural Networks (GNN)
- Temporal Fusion Transformers (TFT)
- PointNet++

## Backend / Inferencia

- FastAPI
- NVIDIA Triton Inference Server

## Data Pipeline

- Dagster
- DuckDB

## Frontend

- Next.js 15
- Three.js

## Datos

- OpenF1 API (temporada 2026)

---

# 🧱 3. ARQUITECTURA DEL SISTEMA

## 🔹 CAPA A — INGESTA Y GRAFO DEL CIRCUITO

Diseña un sistema que:

1. Obtenga datos desde OpenF1 API
2. Transforme el circuito en un grafo:
   - Nodos = puntos de telemetría
   - Aristas = distancia + relación topológica

3. Feature Engineering por nodo:
   - Radio de curvatura
   - Rugosidad del asfalto
   - Velocidad media histórica
   - Tipo de sección (recta / curva lenta / curva rápida)

4. Output:
   - Grafo listo para GNN (PyTorch Geometric o DGL)

---

## 🔹 CAPA B — MOTOR DE PREDICCIÓN (HÍBRIDO)

Diseña 3 módulos independientes pero conectados:

---

### 🌀 Módulo 1 — Aerodinámica (PINN)

**Objetivo:**
Predecir:

- Coeficiente de arrastre (Cd)
- Carga aerodinámica (Cl)

**Inputs:**

- Estado aerodinámico (Modo X / Modo Z)
- Velocidad
- Configuración del coche
- Condiciones ambientales

**Restricción clave:**

- Integrar ecuaciones físicas (Navier-Stokes simplificadas) en la loss function

---

### ⚡ Módulo 2 — Energía (TFT)

**Objetivo:**
Modelar:

- Uso del MGU-K (350kW)
- Degradación de batería por vuelta

**Inputs:**

- Perfil del circuito
- Historial de consumo
- Sectores del circuito

**Output:**

- Predicción de despliegue energético óptimo

---

### 🧠 Módulo 3 — Ranking (PointNet++)

**Objetivo:**

- Recibir vectores de rendimiento por coche
- Procesarlos como nube de puntos
- Generar ranking final

**Output:**

- Clasificación esperada
- Diferencias entre equipos

---

## 🔹 CAPA C — ORQUESTACIÓN Y VISUALIZACIÓN

### Backend

- FastAPI

**Endpoints:**

- `/predict`
- `/circuit`
- `/telemetry`

**Requisitos:**

- Integración con Triton
- Baja latencia

---

### Frontend

- Next.js 15 + Three.js

**Features:**

- Visualización 3D del circuito
- Heatmap:
  - carga aerodinámica
  - temperatura
  - consumo energético

---

# 🔄 4. PIPELINE DE DATOS

Usa Dagster para orquestar:

1. Ingesta de datos históricos (pretemporada 2026)
2. Limpieza y transformación
3. Construcción de grafos
4. Entrenamiento de modelos
5. Versionado de datasets (DuckDB)

---

# 🔁 5. FLUJO COMPLETO DEL SISTEMA

**Input del usuario:**

- Circuito (ej: Madrid 2026)
- Condiciones:
  - temperatura
  - humedad

**Pipeline:**

1. Dagster ejecuta ingestión
2. GNN analiza el circuito
3. PINN ajusta rendimiento aerodinámico
4. TFT calcula energía
5. PointNet++ genera ranking

**Output:**

```json
{
  "expected_ranking": [...],
  "sector_performance": {...},
  "energy_usage": {...},
  "aero_efficiency": {...}
}
```

# 6. ORDEN DE IMPLEMENTACIÓN

**Ejecuta EXACTAMENTE en este orden:**

1. Setup del proyecto
2. Pipeline de datos
3. Modelado del circuito
4. GNN
5. PINN
6. TFT
7. PointNet++
8. Backend (FastApi)
9. Triton
10. Frontend

# 7. ENTREGABLES POR CADA FASE

**En cada fase debes entregar:**

- Código completo
- Añadir Explicación técnica en un .md llamado "Explicación técnica.md" sin eliminar las explicaciones anteriores
- Decisiones de diseño
- Posibles mejoras
- Cómo probarlo

# 8. RESTRICCIONES

- No usar soluciones simplificadas tipo "mock"
- No sustituir modelos avanzados por versiones básicas
- No omitir la integración entre módulos
- No avanzar sin validar la fase actual
