import pandas as pd
import requests
import duckdb
import os
from dagster import asset, AssetIn, Definitions, Output, MetadataValue
from typing import Dict, Any

OPENF1_BASE_URL = "https://api.openf1.org/v1"
DB_PATH = "storage/db/f1_2026.duckdb"

@asset(group_name="ingestion")
def openf1_session_metadata() -> pd.DataFrame:
    """
    Obtiene metadatos de las sesiones de la temporada 2026 (o las más recientes disponibles).
    """
    response = requests.get(f"{OPENF1_BASE_URL}/sessions")
    if response.status_code != 200:
        raise Exception(f"Error al conectar con OpenF1 API: {response.status_code}")
    
    df = pd.DataFrame(response.json())
    return df

@asset(group_name="ingestion")
def raw_telemetry_stream() -> pd.DataFrame:
    """
    Simula o captura el stream de telemetría de alta frecuencia.
    """
    # session_key=9158 es una referencia real de 2023 usada para el desarrollo del pipeline
    params = {"session_key": 9158}
    
    response = requests.get(f"{OPENF1_BASE_URL}/car_data", params=params)
    if response.status_code != 200:
        return pd.DataFrame()
    
    return pd.DataFrame(response.json())

@asset(
    ins={"raw_data": AssetIn("raw_telemetry_stream")},
    group_name="transformation"
)
def clean_telemetry_v1(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza, deduplicación y tipado estricto de la telemetría.
    """
    if raw_data.empty:
        return raw_data

    # 1. Conversión de tipos
    raw_data["date"] = pd.to_datetime(raw_data["date"])
    numeric_cols = ["speed", "rpm", "n_gear", "throttle", "brake"]
    for col in numeric_cols:
        if col in raw_data.columns:
            raw_data[col] = pd.to_numeric(raw_data[col], errors="coerce")

    # 2. Manejo de nulos y duplicados
    df = raw_data.dropna(subset=["speed", "date"]).drop_duplicates(subset=["date", "driver_number"])
    
    # 3. Sort temporal por piloto
    df = df.sort_values(["driver_number", "date"])
    
    return df

@asset(
    ins={"clean_data": AssetIn("clean_telemetry_v1")},
    group_name="storage"
)
def telemetry_warehouse(clean_data: pd.DataFrame) -> Output[None]:
    """
    Persistencia columnar en DuckDB para acceso ultra-rápido por los modelos de IA.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Usamos DataFrame literal para la inserción
    conn = duckdb.connect(DB_PATH)
    
    conn.execute("CREATE TABLE IF NOT EXISTS telemetry AS SELECT * FROM clean_data WHERE 1=0")
    conn.execute("INSERT INTO telemetry SELECT * FROM clean_data")
    
    row_count = conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
    conn.close()
    
    return Output(
        None,
        metadata={
            "total_rows": MetadataValue.int(row_count),
            "db_path": MetadataValue.path(os.path.abspath(DB_PATH))
        }
    )

defs = Definitions(
    assets=[
        openf1_session_metadata,
        raw_telemetry_stream,
        clean_telemetry_v1,
        telemetry_warehouse
    ]
)
