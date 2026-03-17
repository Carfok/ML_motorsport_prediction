from dagster import Definitions, load_assets_from_modules
from data_pipeline.assets import ingestion

# Carga todos los activos definidos en la ingesta
all_assets = load_assets_from_modules([ingestion])

defs = Definitions(
    assets=all_assets,
    # Aquí se pueden añadir recursos como DuckDBResource en el futuro
    resources={
        "database": {
            "path": "storage/db/f1_2026.duckdb"
        }
    }
)
