from pydantic import BaseModel, Field
from typing import List, Optional

class TelemetryPoint(BaseModel):
    speed: float = Field(..., example=312.4)
    drs: bool = Field(..., example=True)
    pitch: float = Field(..., example=0.01)
    roll: float = Field(..., example=0.005)
    soc: float = Field(..., example=0.85)

class PredictRequest(BaseModel):
    circuit_id: str = Field(..., example="madrid-2026")
    driver_id: int = Field(..., example=14)
    telemetry_window: List[TelemetryPoint]

class PredictionResponse(BaseModel):
    prediction_id: str
    aero_efficiency: dict = Field(..., example={"cd": 0.85, "cl": 2.45})
    energy_usage: dict = Field(..., example={"soc_at_finish": 0.12})
    expected_ranking: List[int]
    sector_performance: dict
