from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes

app = FastAPI(
    title="The 2026 Aero-Power Predictor API",
    description="Sistema de predicción de F1 en tiempo real basado en PINN, GNN, TFT y PointNet++",
    version="2.1.0"
)

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye los routers definidos
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "version": "2026.1.1",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

