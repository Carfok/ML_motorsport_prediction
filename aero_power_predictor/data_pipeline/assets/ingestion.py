from dagster import asset, Definitions, AssetIn
import duckdb
import pandas as pd
import requests

OPENF1_BASE_URL = "https://api.openf1.org/v1"

@asset
def raw_telemetry_historical() -> pd.DataFrame:
    """
    Ingesta datos históricos de telemetría de la temporada 2023/24/25
    como base para el entrenamiento inicial.
    """
    # Ejemplo simplificado: Obtener telemetría de una sesión específica
    # Nota: En producción, esto se particionaría por GP y Fecha.
    params = {"session_key": 9158, "speed[gt]": 200} # Filtro ejemplo
    response = requests.get(f"{OPENF1_BASE_URL}/car_data", params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

@asset
def raw_circuits() -> pd.DataFrame:
    """
    Obtener metadatos de circuitos desde OpenF1.
    """
    response = requests.get(f"{OPENF1_BASE_URL}/sessions")
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        return df[['circuit_key', 'circuit_short_name', 'location']].drop_duplicates()
    return pd.DataFrame()

@asset(ins={"telemetry": AssetIn("raw_telemetry_historical")})
def clean_telemetry(telemetry: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza y normalización de telemetría.
    """
    if telemetry.empty:
        return telemetry
    
    # Normalización básica y tipado
    telemetry['date'] = pd.to_datetime(telemetry['date'])
    telemetry['n_gear'] = telemetry['n_gear'].astype(int)
    telemetry = telemetry.dropna(subset=['speed', 'rpm'])
    
    return telemetry

@asset(ins={"telemetry": AssetIn("clean_telemetry")})
def telemetry_to_duckdb(telemetry: pd.DataFrame):
    """
    Persistencia de datos limpios en DuckDB para análisis rápido y versionado.
    """
    conn = duckdb.connect(database="storage/db/f1_historical.duckdb", read_only=False)
    conn.execute("CREATE TABLE IF NOT EXISTS telemetry AS SELECT * FROM telemetry")
    conn.execute("INSERT INTO telemetry SELECT * FROM telemetry")
    conn.close()

defs = Definitions(
    assets=[raw_telemetry_historical, raw_circuits, clean_telemetry, telemetry_to_duckdb]
)
