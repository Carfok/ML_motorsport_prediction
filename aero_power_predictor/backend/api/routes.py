import duckdb
import os
import uuid
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException

# Importamos tus esquemas 2026
from backend.schemas.prediction import PredictRequest, PredictionResponse

router = APIRouter()

# Configuración de entornos (En un .env real)
DB_PATH = "storage/db/f1_2026.duckdb"
EXTERNAL_F1_API = "https://api.openf1.org/v1" # URL Hipotética de la API oficial


def _resolve_db_path() -> str:
    return os.getenv("DUCKDB_PATH", DB_PATH)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_column(available_columns: set, candidates: List[str]) -> Optional[str]:
    for candidate in candidates:
        if candidate in available_columns:
            return candidate
    return None


def _load_pipeline_telemetry(driver_id: int, limit: int = 120) -> List[Dict[str, Any]]:
    db_path = _resolve_db_path()
    if not os.path.exists(db_path):
        raise HTTPException(status_code=503, detail="DuckDB no disponible; ejecuta la data_pipeline primero")

    conn = duckdb.connect(db_path, read_only=True)
    try:
        tables = {row[0] for row in conn.execute("SHOW TABLES").fetchall()}
        if "telemetry" not in tables:
            raise HTTPException(status_code=503, detail="Tabla telemetry no encontrada; materializa el pipeline")

        table_info = conn.execute("PRAGMA table_info('telemetry')").fetchall()
        available_columns = {row[1] for row in table_info}

        driver_col = _safe_column(available_columns, ["driver_id", "driver_number"])
        timestamp_col = _safe_column(available_columns, ["date", "timestamp", "time"])
        speed_col = _safe_column(available_columns, ["speed"])
        rpm_col = _safe_column(available_columns, ["rpm"])
        gear_col = _safe_column(available_columns, ["gear", "n_gear"])
        throttle_col = _safe_column(available_columns, ["throttle"])
        brake_col = _safe_column(available_columns, ["brake"])
        distance_col = _safe_column(available_columns, ["distance_track", "distance"])
        soc_col = _safe_column(available_columns, ["soc", "battery_soc"])
        overtake_col = _safe_column(available_columns, ["overtake_mode_active"])
        boost_col = _safe_column(available_columns, ["boost_active"])
        active_aero_col = _safe_column(available_columns, ["active_aero"])

        selected_columns = []
        selected_names = []
        for column_name, alias in [
            (timestamp_col, "timestamp"),
            (speed_col, "speed"),
            (rpm_col, "rpm"),
            (gear_col, "gear"),
            (throttle_col, "throttle"),
            (brake_col, "brake"),
            (distance_col, "distance_track"),
            (soc_col, "soc"),
            (overtake_col, "overtake_mode_active"),
            (boost_col, "boost_active"),
            (active_aero_col, "active_aero"),
        ]:
            if column_name:
                selected_columns.append(f"{column_name} AS {alias}")
                selected_names.append(alias)

        if not selected_columns:
            return []

        order_expression = timestamp_col if timestamp_col else "rowid"
        where_clause = f"WHERE {driver_col} = ?" if driver_col else ""
        query = (
            f"SELECT {', '.join(selected_columns)} "
            f"FROM telemetry {where_clause} "
            f"ORDER BY {order_expression} DESC LIMIT ?"
        )

        params: List[Any] = [driver_id, limit] if driver_col else [limit]
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    telemetry_points: List[Dict[str, Any]] = []
    for index, row in enumerate(reversed(rows)):
        row_data = dict(zip(selected_names, row))
        timestamp_raw = row_data.get("timestamp")
        if isinstance(timestamp_raw, datetime):
            timestamp_ms = timestamp_raw.timestamp() * 1000.0
        else:
            timestamp_ms = _coerce_float(timestamp_raw, float(index))

        speed = _coerce_float(row_data.get("speed"), 0.0)
        throttle = _coerce_float(row_data.get("throttle"), 0.0)
        soc = _coerce_float(row_data.get("soc"), max(0.0, min(100.0, 100.0 - throttle * 0.2)))
        active_aero = row_data.get("active_aero")
        if active_aero not in {"Z_MODE", "X_MODE"}:
            active_aero = "X_MODE" if speed >= 290 else "Z_MODE"

        telemetry_points.append(
            {
                "timestamp": timestamp_ms,
                "distance_track": _coerce_float(row_data.get("distance_track"), float(index)),
                "speed": speed,
                "rpm": _coerce_int(row_data.get("rpm"), 0),
                "gear": _coerce_int(row_data.get("gear"), 0),
                "throttle": throttle,
                "brake": _coerce_float(row_data.get("brake"), 0.0),
                "active_aero": active_aero,
                "boost_active": bool(row_data.get("boost_active", throttle > 95)),
                "overtake_mode_active": bool(row_data.get("overtake_mode_active", False)),
                "soc": max(0.0, min(100.0, soc)),
            }
        )

    return telemetry_points


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
    """Verifica DuckDB y la conectividad con la API externa de F1."""
    api_online = False
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{EXTERNAL_F1_API}/health")
            api_online = res.status_code == 200
        
        storage_exists = os.path.exists(DB_PATH)
        
        return {
            "storage_layer": "connected" if storage_exists else "offline",
            "external_f1_api": "connected" if api_online else "unreachable",
            "environment": "2026_REGULATION_READY"
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}

@router.post("/predict", response_model=PredictionResponse)
async def perform_inference(request: PredictRequest):
    """
    Inferencia que consume telemetría proveniente de data_pipeline (DuckDB).
    """
    try:
        telemetry_window = request.telemetry_window
        if not telemetry_window:
            telemetry_window = _load_pipeline_telemetry(request.driver_id)

        if not telemetry_window:
            raise HTTPException(status_code=404, detail="No hay telemetría disponible en data_pipeline para el piloto")

        speeds = [point["speed"] if isinstance(point, dict) else point.speed for point in telemetry_window]
        throttles = [point["throttle"] if isinstance(point, dict) else point.throttle for point in telemetry_window]
        brakes = [point["brake"] if isinstance(point, dict) else point.brake for point in telemetry_window]
        soc_values = [point["soc"] if isinstance(point, dict) else point.soc for point in telemetry_window]

        avg_speed = sum(speeds) / len(speeds)
        avg_throttle = sum(throttles) / len(throttles)
        avg_brake = sum(brakes) / len(brakes)
        soc_start = soc_values[0]
        soc_finish = soc_values[-1]

        lap_time_base = max(68.0, 150.0 - (avg_speed * 0.22))
        tyre_degradation = min(1.0, max(0.0, (request.lap_number * 0.01) + (avg_brake / 300.0)))
        sector_1 = round(lap_time_base * 0.29, 3)
        sector_2 = round(lap_time_base * 0.43, 3)
        sector_3 = round(lap_time_base - sector_1 - sector_2, 3)
        cd = round(max(0.6, min(1.2, 1.02 - avg_speed / 1000.0)), 3)
        cl = round(max(1.4, min(3.0, 1.9 + avg_brake / 100.0)), 3)
        ranking_seed = [request.driver_id, 1, 16, 55, 63]

        return PredictionResponse(
            prediction_id=str(uuid.uuid4()),
            predicted_lap_time=round(lap_time_base, 3),
            tyre_degradation_score=round(tyre_degradation, 3),
            aero_efficiency={"cd": cd, "cl": cl},
            energy_usage={
                "soc_at_finish": round(max(0.0, min(1.0, soc_finish / 100.0)), 4),
                "soc_delta": round(soc_finish - soc_start, 3),
                "avg_throttle": round(avg_throttle, 3),
            },
            sector_times={
                "sector_1": sector_1,
                "sector_2": sector_2,
                "sector_3": sector_3,
            },
            expected_ranking=ranking_seed,
        )
    except HTTPException:
        raise
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
