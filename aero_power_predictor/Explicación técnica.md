# Explicación Técnica y Registro de Avance

---

## Fase 1: Setup del Proyecto y Estructura de Datos (Core Infra)

### 1. Resumen de la Fase

Se ha establecido la infraestructura base del sistema **The 2026 Aero-Power Predictor**. Esta fase es crítica ya que define la jerarquía de directorios, el entorno de ejecución (Python 3.12+) y el stack de librerías de IA que sostendrán los modelos físicos y de grafos.

### 2. Decisiones de Diseño y Arquitectura

- **Arquitectura Modular Desacoplada:** Se ha estructurado el proyecto en 4 grandes capas (`core`, `data_pipeline`, `backend`, `frontend`). Cada submódulo del `core` (PINN, GNN, TFT, PointNet++) tiene su propio espacio para evitar dependencias circulares.
- **Validación de IA Core:** Se ha asegurado la interoperabilidad entre `torch` y `torch-geometric` instalando versiones compatibles que permiten el procesamiento de grafos en hardware acelerado (GPU) o CPU.
- **Tipado Estricto:** Uso de `pydantic` y `typing` como estándar para garantizar que el flujo de datos entre modelos sea robusto y libre de errores de tipo en tiempo de ejecución.

### 3. Código y Estructura de Directorios

Se ha implementado la siguiente estructura:

- `core/physics/`: Framework para la PINN aerodinámica.
- `core/graphs/`: Utilidades para la construcción del grafo del circuito.
- `core/energy/`: Arquitectura para el Temporal Fusion Transformer.
- `core/ranking/`: Espacio para procesamiento de nubes de puntos con PointNet++.
- `storage/db/`: Directorio persistente para la base de datos DuckDB.

---

## Fase 2: Pipeline de Datos (Dagster + DuckDB)

Se ha implementado el motor de ingesta y orquestación del sistema. La Fase 2 garantiza que los datos de telemetría de ultra-alta frecuencia (hasta 20Hz) sean capturados, limpiados y almacenados de forma eficiente para su posterior consumo por los modelos de IA (GNN, PINN, TFT).

## 2. Decisiones de Diseño y Arquitectura

- **Orquestación con Dagster:** Se han definido `Soft Assets` que permiten un rastreo completo del linaje de los datos. Desde el metadato de la sesión hasta el almacenaje final (`warehouse`).
- **Storage con DuckDB:** Elegido por ser _in-process_, columnar y altamente optimizado para análisis tipo `OLAP`. Esto elimina la necesidad de un servidor de BD externo y ofrece latencias de microsegundos en lecturas para el entrenamiento de modelos.
- **Limpieza Estratégica:** Realizamos limpieza de nulos en columnas críticas (`speed`, `throttle`) y aseguramos el ordenamiento temporal por piloto, fundamental para que el módulo **TFT (Energía)** reciba secuencias coherentes.

## 3. Código Completo

El módulo principal se encuentra en `data_pipeline/assets/ingestion.py`.
Define 4 activos clave:

1. `openf1_session_metadata`: Descubrimiento de GPs y Sesiones.
2. `raw_telemetry_stream`: Ingesta cruda.
3. `clean_telemetry_v1`: Transformación y tipado.
4. `telemetry_warehouse`: Persistencia en `storage/db/f1_2026.duckdb`.

## 4. Posibles Mejoras

- **Implementar Sensores:** Sensores de Dagster que detecten automáticamente el inicio de una sesión en vivo en la temporada 2026.
- **Particionamiento:** Dividir el almacenamiento por `GP_ID` y `DRIVER_ID` para mejorar el rendimiento en circuitos largos como Spa.

## 5. Cómo Probarlo

1. Ejecutar el terminal de Dagster:
   ```bash
   dagster dev -f data_pipeline/assets/ingestion.py
   ```
2. Abrir la interfaz web (`http://localhost:3000`).
3. Seleccionar todos los assets y pulsar **"Materialize All"**.
4. Confirmar que el archivo `storage/db/f1_2026.duckdb` ha sido creado.
