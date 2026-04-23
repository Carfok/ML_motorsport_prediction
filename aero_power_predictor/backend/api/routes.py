import duckdb
import os
import uuid
import httpx
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

# Importamos tus esquemas 2026
from backend.schemas.prediction import PredictRequest, PredictionResponse

router = APIRouter()

# Configuración de entornos (En un .env real)
DB_PATH = "storage/db/f1_2026.duckdb"
EXTERNAL_F1_API = "https://api.openf1.org/v1" # URL Hipotética de la API oficial

# --- SERVICIO DE DATOS EXTERNOS ---
class F1DataService:
    """Clase para desacoplar la obtención de datos de la lógica del router."""
    
    @staticmethod
    async def get_calendar() -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            # En producción, esto podría tener headers de autenticación
            response = await client.get(f"{EXTERNAL_F1_API}/calendar")
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Error al conectar con la API de F1")
            return response.json()

    @staticmethod
    async def get_team_info(team_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_F1_API}/teams/{team_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Equipo {team_id} no existe en 2026")
            return response.json()

    @staticmethod
    async def validate_circuit(circuit_id: str) -> bool:
        calendar = await F1DataService.get_calendar()
        return any(c['circuit_id'] == circuit_id for c in calendar)

# --- RUTAS ---

@router.get("/status/connection")
async def check_connections():
    """Verifica DuckDB, la conectividad externa y devuelve metadatos de circuitos."""
    api_online = False
    available_circuits = []
    current_conditions = {"air_temp": 25, "track_temp": 35, "humidity": 45}
    
    try:
        # Intenta obtener circuitos reales de la API OpenF1 (Datos procesados)
        try:
            calendar = await F1DataService.get_calendar()
            available_circuits = [{"id": c['circuit_id'], "name": c['circuit_name']} for c in calendar]
            api_online = True
        except Exception:
            # Si no hay circuitos disponibles tras el error, lanzamos el mensaje solicitado
            return {
                "status": "error",
                "message": "No hay circuitos, hubo un error en la carga de los datos",
                "storage_layer": "connected" if os.path.exists(DB_PATH) else "offline",
                "external_f1_api": "unreachable"
            }

        storage_exists = os.path.exists(DB_PATH)
        
        return {
            "storage_layer": "connected" if storage_exists else "offline",
            "external_f1_api": "connected" if api_online else "unreachable",
            "available_circuits": available_circuits,
            "current_conditions": current_conditions,
            "environment": "2026_REGULATION_READY"
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

@router.post("/predict", response_model=PredictionResponse)
async def perform_inference(request: PredictRequest):
    """
    Inferencia que valida datos dinámicamente contra la API externa.
    """
    # Para desarrollo: Si el ID es uno de los conocidos o 'madrid-2026', saltamos validación externa si falla
    try:
        is_valid_circuit = await F1DataService.validate_circuit(request.circuit_id)
        if not is_valid_circuit and request.circuit_id not in ["madrid-2026", "monaco-2026", "silverstone-2026", "interlagos-2026"]:
            raise HTTPException(status_code=400, detail="Circuito no válido para la temporada 2026")
    except Exception:
        # Fallback para desarrollo sin conexión real a API OpenF1
        pass

    try:
        # En una implementación real, aquí se enviarían los datos de la API externa
        # junto con la telemetría del request a tu modelo de ML (Triton/TorchServe)
        
        # Simulamos lógica basada en el SOC del último punto de la ventana
        last_point = request.telemetry_window[-1]
        
        # Lógica 2026: Si el SOC es bajo y no está en Overtake Mode, el rendimiento cae
        performance_multiplier = 1.0
        if last_point.soc < 10.0 and not last_point.overtake_mode_active:
            performance_multiplier = 0.85

        return PredictionResponse(
            prediction_id=str(uuid.uuid4()),
            predicted_lap_time=75.230 * performance_multiplier,
            tyre_degradation_score=0.15, # Dato que vendría del modelo PINN
            battery_depletion_risk=1.0 if last_point.soc < 5.0 else 0.2,
            sector_times={
                "S1": 21.5,
                "S2": 32.8,
                "S3": 20.9
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")

@router.get("/circuit/{circuit_id}/graph")
async def get_circuit_graph(circuit_id: str):
    """
    Recupera la geometría del circuito desde la API externa para alimentar el GNN.
    """
    async with httpx.AsyncClient() as client:
        # Consultamos a la API externa por la geometría del circuito
        response = await client.get(f"{EXTERNAL_F1_API}/circuits/{circuit_id}/geometry")
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Geometría del circuito no disponible")
        
        data = response.json()
        return {
            "circuit_id": circuit_id,
            "gnn_nodes": data.get("nodes", 0),
            "active_aero_mapping": data.get("x_mode_segments", []),
            "source": "Official 2026 F1 Mapping Service"
        }

@router.get("/team-analysis/{team_id}")
async def get_team_live_data(team_id: str):
    """
    Obtiene datos técnicos del equipo desde la API externa (ej. eficiencia del MGU-K).
    """
    team_data = await F1DataService.get_team_info(team_id)
    
    # Combinamos con datos locales de DuckDB si fuera necesario
    conn = duckdb.connect(DB_PATH, read_only=True)
    historical_avg = conn.execute(
        "SELECT AVG(speed) FROM telemetry WHERE driver_id IN (SELECT id FROM drivers WHERE team=?)", 
        [team_id]
    ).fetchone()
    conn.close()

    return {
        "team_metadata": team_data,
        "historical_avg_speed": historical_avg[0] if historical_avg else 0,
        "regulation_year": 2026
    }
