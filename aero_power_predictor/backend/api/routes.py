import duckdb
import os
from fastapi import APIRouter, HTTPException
from backend.schemas.prediction import PredictRequest, PredictionResponse
import random

router = APIRouter()
DB_PATH = "storage/db/f1_2026.duckdb"

@router.get("/status/connection")
async def check_connections():
    """
    Verifica la conexión con el storage (DuckDB) y la integridad de los datos.
    """
    try:
        if not os.path.exists(DB_PATH):
            return {"storage": "disconnected", "reason": "DuckDB file not found", "path": DB_PATH}
        
        conn = duckdb.connect(DB_PATH, read_only=True)
        tables = conn.execute("SELECT table_name FROM information_schema.tables").fetchall()
        row_count = 0
        if ("telemetry",) in tables:
            row_count = conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
        conn.close()
        
        return {
            "storage": "connected",
            "database": "DuckDB",
            "telemetry_rows": row_count,
            "api_status": "online"
        }
    except Exception as e:
        return {"storage": "error", "detail": str(e)}

@router.post("/predict", response_model=PredictionResponse)
async def perform_inference(request: PredictRequest):
    """
    Orquesta la inferencia completa para un piloto en un circuito.
    Procesa: GNN (Circuito) -> PINN (Aero) -> TFT (Energía) -> PointNet++ (Ranking)
    """
    try:
        # En una fase posterior, aquí se invoca a Triton Inference Server
        # Por ahora, simulamos la respuesta basada en el flujo lógico
        return PredictionResponse(
            prediction_id=f"PRED-{request.circuit_id}-{request.driver_id}-{random.randint(1000,9999)}",
            aero_efficiency={"cd": 0.84, "cl": 2.51},
            energy_usage={"soc_at_finish": 0.08, "mgu_k_deployment": 320.5},
            expected_ranking=[1, 4, 3, 2, 5],
            sector_performance={"S1": "Optimal", "S2": "High Drag", "S3": "Efficient"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/circuit/{circuit_id}")
async def get_circuit_graph(circuit_id: str):
    """
    Recupera la estructura del grafo del circuito para el frontend.
    """
    return {
        "circuit_id": circuit_id,
        "nodes": 1000,
        "edges": 1998,
        "type": "Graph-GNN-Ready"
    }

@router.get("/telemetry/{driver_id}")
async def get_driver_telemetry(driver_id: int):
    """
    Obtiene los últimos datos de telemetría de DuckDB.
    """
    return {
        "driver_id": driver_id,
        "status": "active",
        "current_lap": 42,
        "last_speed": 315.2
    }
