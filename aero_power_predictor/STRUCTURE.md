# Aero-Power Predictor 2026 - Directorio Raíz

├── .env # Variables de entorno (API Keys, URLs)
├── requirements.txt # Dependencias
├── README.md # Documentación técnica
│
├── core/ # IA & Modelado
│ ├── physics/ # PINN Aerodinámica
│ ├── graphs/ # GNN Circuitos
│ ├── energy/ # TFT Gestión Energética
│ └── ranking/ # PointNet++ Clasificación
│
├── data_pipeline/ # Orquestación con Dagster
│ ├── assets/ # Ingesta, Limpieza, Transformación
│ ├── partitions/ # Particiones de datos por GP/Año
│ └── setup.py # Configuración de Dagster
│
├── backend/ # FastAPI
│ ├── api/ # Router y Endpoints
│ ├── schemas/ # Pydantic models
│ └── triton/ # Configuración de clientes para Triton
│
├── frontend/ # Next.js 15
│ ├── components/ # Componentes UI
│ ├── three/ # Visualización 3D (Circuitos)
│ └── app/ # App Router Next.js
│
└── storage/ # DuckDB y archivos temporales
└── db/ # Base de datos analítica
