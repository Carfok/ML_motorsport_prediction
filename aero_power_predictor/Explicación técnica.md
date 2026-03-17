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

---

## Fase 3: Modelado del Circuito y GNN (Graph Neural Networks)

Se ha implementado el motor de procesamiento espacial que transforma el asfalto en una estructura de datos conectada (grafo). Esta fase permite que el predictor entienda no solo dónde está el coche, sino cómo la geometría de la sección anterior y posterior afecta al rendimiento.

### 2. Decisiones de Diseño y Arquitectura

- **Topología en Loop:** Cada circuito se modela como un grafo de $N$ nodos conectados de forma secuencial y circular, asegurando que la información de flujo aerodinámico y el "gap" entre el final e inicio de meta sea continuo.
- **Node Features (4-Channels):** El modelo procesa por cada micro-sector:
  - Radio de curvatura (Calculado por derivada segunda).
  - Elevación (Pendientes).
  - Rugosidad del asfalto (Afecta delta-T y degradación).
  - Velocidad media histórica (Referencia de carga aerodinámica).
- **GCNConv (Graph Convolutional Networks):** Elegida por su eficiencia en procesar vecindarios espaciales. La información de "aire sucio" o "carga aerodinámica en frenada" se propaga a través de las aristas del grafo.

### 3. Código Completo

- **Builder (`core/graphs/builder.py`):** Clase encargada de la discretización del circuito y asignación de pesos topológicos.
- **Model (`core/graphs/model.py`):** Arquitectura GNN profunda con 3 capas de convolución, ReLU y Dropout para evitar el overfitting en circuitos con pocas curvas (como Monza).

### 4. Posibles Mejoras

- **Multi-edge Attention:** Utilizar `GAT` (Graph Attention Networks) para que el modelo aprenda por sí solo qué curvas son más críticas para el tiempo de vuelta total.
- **Nodos Virtuales:** Añadir nodos "Box" o "DRS Zone" para mejorar la precisión estratégica.

### 5. Cómo Probarlo

Ejecutar el script de validación del modelo:
```bash
python core/graphs/model.py
```
El output debe mostrar un tensor de predicción por cada nodo del circuito, validando el flujo de datos completo a través de la red neuronal.

---

## Fase 4: Modelado Aerodinámico PINN (Physics-Informed Neural Networks)

Se ha implementado el **Módulo 1 — Aerodinámica**, encargado de predecir los coeficientes de carga (`Cl`) y arrastre (`Cd`) integrando restricciones físicas de fluidos directamente en la función de pérdida.

### 2. Decisiones de Diseño y Arquitectura

- **Loss Function Híbrida:** A diferencia de una red neuronal convencional, la PINN utiliza una pérdida de datos (comparación con telemetría real de túnel de viento o CFD) y una pérdida de física (cumplimiento de las ecuaciones de Navier-Stokes simplificadas).
- **Activación Tanh:** Elegida específicamente para PINNs para permitir el cálculo de segundas derivadas estables respecto a los inputs, algo fundamental para el cumplimiento de las EDO/EDP aerodinámicas.
- **Modos DRS (X/Z):** El modelo distingue entre configuraciones de ala abierta (DRS on) y cerrada, ajustando dinámicamente el balance aerodinámico esperado por cada coche.

### 3. Código Completo

- **Módulo PINN (`core/physics/pinn.py`):** Define la arquitectura multicapa que vincula velocidad, posición de chasis (Pitch/Roll) y estado aerodinámico. Incluye el método `physics_loss` para asegurar la consistencia dimensional de la predicción.

### 4. Posibles Mejoras

- **Integración CFD en Tiempo Real:** Enriquecer el entrenamiento con simulaciones de Star-CCM+ o OpenFOAM para obtener superficies de respuesta más ricas en turbulencias.
- **Sensibilidad Térmica:** Añadir la temperatura del aire (`rho`) como input dinámico para predecir la pérdida de carga en circuitos de gran altitud (México).

### 5. Cómo Probarlo

Ejecutar la validación aerodinámica:
```bash
python core/physics/pinn.py
```
El script generará una predicción de `Cd/Cl` y calculará el residuo físico, el cual debería aproximarse a cero durante el entrenamiento.

---

## Fase 5: Gestión Energética TFT (Temporal Fusion Transformers)

Se ha implementado el **Módulo 2 — Energía**, diseñado para modelar el complejo sistema de propulsión de 2026, donde el MGU-K (350kW) y el SOC (State of Charge) de la batería son factores determinantes en el tiempo de vuelta y la estrategia de carrera.

### 2. Decisiones de Diseño y Arquitectura

- **Arquitectura Temporal Desacoplada:** El uso de un **Temporal Fusion Transformer (TFT)** permite capturar dependencias a largo plazo (degradación acumulada por vuelta) y a corto plazo (despliegue en la recta actual).
- **Multi-head Attention:** Incorporada para identificar qué sectores del circuito son óptimos para la regeneración de energía (frenadas fuertes) versus sectores de alto consumo (rectas largas).
- **Inferencia de Horizonte Variable:** El modelo predice no solo el estado inmediato de la carga, sino un horizonte temporal completo (ej. próximos 5 segundos de carrera), permitiendo estrategias proactivas.

### 3. Código Completo

- **Módulo Energy (`core/energy/tft_model.py`):** Define la red neuronal temporal basada en codificación LSTM de alta frecuencia y mecanismos de atención para el balance energético del motor.

### 4. Posibles Mejoras

- **Variables Estáticas del Piloto:** Integrar el "estilo de conducción" como variable estática que condicione el perfil de consumo energético del Transformer.
- **Predicción de Degradación Térmica:** Vincular el uso intensivo del MGU-K con el aumento de temperatura en las celdas de la batería para simular el "thermal clipping".

### 5. Cómo Probarlo

Ejecutar la validación del modelo energético:
```bash
python core/energy/tft_model.py
```
El modelo devolverá un vector de 5 pasos temporales prediciendo la evolución del `SOC` (State of Charge) para el siguiente tramo del circuito.

---

## Fase 6: Módulo de Ranking PointNet++ (AI Nubes de Puntos)

Se ha implementado el **Módulo 3 — Ranking**, encargado de consolidar todas las predicciones parciales (Aero, Energía, Circuito) y procesarlas como un "set" de datos para generar la parrilla final esperada.

### 2. Decisiones de Diseño y Arquitectura

- **Arquitectura Basada en Sets:** A diferencia de una red neuronal que procesa coche por coche, **PointNet++** trata a los 20 pilotos como una "nube de puntos". Esto permite que el modelo aprenda la competencia relativa entre ellos (si un coche gana 2 décimas en recta, cómo afecta eso a los 19 puntos restantes de la nube).
- **Simetría y MLP Compartidos:** Uso de transformaciones invariantes al orden (los pilotos pueden entrar en cualquier orden al vector) y capas densas compartidas para extraer la "firma de rendimiento" única de cada monoplaza.
- **Global Feature Fusion:** El modelo extrae una característica global del Gran Premio (por ejemplo, si es una carrera de alto consumo de gasolina o de degradación extrema) y la fusiona con el estado local de cada piloto para refinar la posición final.

### 3. Código Completo

- **Módulo Ranking (`core/ranking/pointnet_ranking.py`):** Define la red neuronal basada en nubes de puntos con 20 entradas (pilotos) y 10 features de rendimiento (PACE, ERS, TYRES), devolviendo una puntuación de ranking para la clasificación.

### 4. Posibles Mejoras

- **Set-to-Set Transformer:** Evolucionar hacia un arquitectura "Cross-Attention" donde cada piloto compare su vector de rendimiento directamente con sus rivales directos en el campeonato.
- **Incertidumbre Aleatoria:** Añadir capas Bayesianas para predecir no solo la posición, sino la probabilidad de abandono o error humano bajo presión.

### 5. Cómo Probarlo

Ejecutar la validación del motor de ranking:
```bash
python core/ranking/pointnet_ranking.py
```
El sistema generará una predicción de `Top 3` basada en vectores de rendimiento sintéticos, validando la lógica de agregación global.

---

## Fase 7: Backend FastAPI (Orquestación e Inferencia)

Se ha implementado la capa de servicios **Backend**, que actúa como el cerebro operativo de la plataforma, orquestando las llamadas a los modelos de IA y conectando con el almacenamiento DuckDB.

### 2. Decisiones de Diseño y Arquitectura

- **Estructura Asíncrona:** Uso de `FastAPI` con `async/await` para gestionar múltiples peticiones de telemetría en tiempo real sin bloquear el hilo de ejecución para otros usuarios.
- **Validación con Pydantic:** Se han definido esquemas estrictos de entrada (`PredictRequest`), asegurando que los datos que llegan de la pista (vía API o simulador) tengan el formato correcto antes de entrar a la GPU.
- **Preparación para NVIDIA Triton:** Los endpoints están diseñados para derivar la computación pesada (GNN, PINN, TFT) a servidores de inferencia especializados, manteniendo la API ligera y escalable.

### 3. Código Completo

- **Backend Principal (`backend/main.py`):** Define el router de la aplicación, los endpoints de `/predict`, `/telemetry` y el estado de salud del sistema, permitiendo la comunicación fluida con el frontend.

### 4. Posibles Mejoras

- **WebSocket Integration:** Implementar WebSockets para streaming de datos de telemetría a 20Hz directamente al frontend sin necesidad de polling.
- **Rate-limiting Inteligente:** Control de flujo para evitar sobrecargar los modelos de IA durante picos de tráfico en sesiones de clasificación.

### 5. Cómo Probarlo

Levantar el servidor web de desarrollo:
```bash
python backend/main.py
```
Acceder a la documentación interactiva en `http://localhost:8000/docs` para realizar peticiones de prueba a los modelos de predicción.

---

## Fase Final de Estructuracion y Scaffolding (Cierre Punto 9)

Se ha completado la arquitectura de directorios y archivos de soporte descrita en el punto 9 del Plan Inicial. Esto asegura que el proyecto cumpla con los estándares de robustez y organización necesarios para un entorno de producción de Fórmula 1 en 2026.

### 1. Archivos Críticos de Configuración y Documentación
- **`.env`:** Gestión de variables de entorno para API Keys (OpenF1), rutas de DuckDB y configuración de red del Backend.
- **`README.md`:** Guía completa de arquitectura, instalación y flujo de ejecución para desarrolladores y analistas de datos.
- **`data_pipeline/setup.py`:** Punto de entrada centralizado para Dagster, permitiendo la carga automática de activos y recursos de base de datos.

### 2. Estructura de Persistencia y Particionado
- **`storage/db/`:** Directorio dedicado para el motor analítico DuckDB.
- **`data_pipeline/partitions/`:** Preparado para soportar el particionado de datos por Gran Premio (GP) y Piloto, optimizando la velocidad de lectura durante las fases de entrenamiento de las GNN y PINN.

### 3. Esqueleto del Frontend (Next.js 15)
- **`frontend/app/page.js`:** Punto de entrada del App Router de Next.js, integrando el Dashboard reactivo y la vista 3D de Three.js.

### 4. Cómo Probarlo
Para verificar la integridad de la estructura recién creada:
- Inspecciona el archivo `.env` para asegurar que las rutas coincidan con tu entorno.
- Ejecuta `dagster dev` apuntando a `data_pipeline/setup.py` para validar la orquestación global.
- Comprueba que la carpeta `storage/db/` esté lista para recibir los datos de `ingestion.py`.


---

## Fase 8: Backend & Triton Client (Producción)

Se ha evolucionado el backend hacia una arquitectura de producción desacoplada siguiendo el plan inicial. 

### 2. Decisiones de Diseño y Arquitectura

- **Schemas de Inferencia (`backend/schemas/`):** Uso de `Pydantic` para definir micro-objetos de telemetría, asegurando que el flujo de datos entre el Frontend, el Backend y Triton sea consistente y tipado.
- **Triton Inference Client (`backend/triton/`):** Creación de un cliente especializado para interactuar con NVIDIA Triton Server, abstrayendo las llamadas `HTTP/gRPC` de la lógica de negocio.
- **Modularización de Rutas:** Separación de la lógica de la API en el archivo `routes.py`, permitiendo una escalabilidad horizontal de endpoints (Circuitos, Telemetría, Predicciones).

### 3. Código Completo

- **Backend API (`backend/api/routes.py`):** Define las operaciones de negocio.
- **Client Triton (`backend/triton/client.py`):** Lógica de comunicación con el servidor de inferencia de NVIDIA.
- **Models (`backend/main.py`):** Orquestador principal de la API.

---

## Fase 9: Frontend (Next.js 15 + Three.js + Heatmaps)

Se ha implementado la capa de visualización avanzada para que los ingenieros de pista puedan interpretar los resultados de los modelos de IA de forma intuitiva.

### 2. Decisiones de Diseño y Arquitectura

- **Visualización 3D del Grafo (`frontend/three/`):** Uso de `Three.js` para renderizar el trazado del circuito a partir de las coordenadas del grafo GNN. La geometría se genera dinámicamente mediante `TubeGeometry`.
- **Dashboard Reactivo (`frontend/components/`):** Interfaz diseñada con `Tailwind CSS` y `Next.js 15` para mostrar métricas de PINN (Aero), TFT (Energía) y Ranking PointNet++ en tiempo real.
- **Unión Hardware/Software:** El Dashboard está preparado para recibir `streams` de datos del backend y actualizar las mallas 3D para reflejar "heatmaps" de carga aerodinámica o degradación.

### 3. Código Completo

- **Visualizador 3D (`frontend/three/Circuit3D.js`):** Motor de renderizado del circuito.
- **Dashboard (`frontend/components/Dashboard.js`):** Interfaz de usuario para monitorización de rendimiento.

### 5. Cómo Probarlo

Para el Backend:
```bash
python backend/main.py
```
Para el Frontend (Simulado):
```bash
cd frontend
npm run dev
```
Visualizar en `http://localhost:3000` el Dashboard de IA del GP de Madrid 2026.






