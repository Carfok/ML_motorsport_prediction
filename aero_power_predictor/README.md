# 🏎️ The 2026 Aero-Power Predictor

Sistema de predicción de rendimiento para la temporada 2026 de Fórmula 1.

## 🚀 Arquitectura
- **Core IA**: PINNs, GNNs, TFT y PointNet++ para análisis físico y estratégico.
- **Pipeline**: Dagster + DuckDB para procesamiento de telemetría de alta frecuencia.
- **Inferencia**: NVIDIA Triton + FastAPI.
- **Visualización**: Next.js 15 y Three.js.

## 🛠️ Instalación
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📈 Ejecución
- **Dagster**: `dagster dev -f data_pipeline/assets/ingestion.py`
- **Backend**: `python backend/main.py`
- **Docs**: Accede a `http://localhost:8000/docs`
