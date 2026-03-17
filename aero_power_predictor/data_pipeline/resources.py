from dagster import resource
import duckdb
import os

@resource
def duckdb_resource():
    """
    Recurso Dagster para manejo de DuckDB
    """
    db_path = os.getenv('DUCKDB_PATH', 'storage/db/f1_2026.duckdb')
    conn = duckdb.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Configuración de recursos por ambiente
resources_by_env = {
    'dev': {
        'duckdb': duckdb_resource.configured({'path': 'storage/db/f1_2026.duckdb'}),
    },
    'prod': {
        'duckdb': duckdb_resource.configured({'path': '/var/lib/f1_2026.duckdb'}),
    }
}
