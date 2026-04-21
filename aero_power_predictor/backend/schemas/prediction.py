from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# 1. Telemetría Enriquecida (Nivel Micro)
class TelemetryPoint(BaseModel):
    # Contexto espacial y temporal
    timestamp: float = Field(..., description="Tiempo relativo desde el inicio de la vuelta o sesión (ms)")
    distance_track: float = Field(..., description="Distancia recorrida en la pista (metros)")
    
    # Dinámica del coche
    speed: float = Field(..., example=312.4, description="Velocidad en km/h")
    rpm: int = Field(..., example=11500, description="Revoluciones del motor")
    gear: int = Field(..., example=8, description="Marcha actual (1-8)")
    
    # Inputs del piloto
    throttle: float = Field(..., ge=0, le=100, example=100.0, description="Presión del acelerador (%)")
    brake: float = Field(..., ge=0, le=100, example=0.0, description="Presión del freno (%)")
    
    # Aerodinámica y Energía
    active_aero: Literal["Z_MODE", "X_MODE"] = Field(
        "Z_MODE", 
        description="Z_MODE: Alta carga (curvas). X_MODE: Baja resistencia (rectas)"
    )
    
    # Energía Híbrida MGU-K (Sustituye la táctica del DRS)
    boost_active: bool = Field(
        ..., 
        description="Indica si el piloto está pulsando el botón de Boost estándar"
    )
    overtake_mode_active: bool = Field(
        ..., 
        description="Manual Override: Despliegue de los 0.5 MJ extra por estar a menos de 1s del rival"
    )
    soc: float = Field(..., ge=0, le=100, example=85.0, description="Estado de carga de la batería (%)")

# 2. Configuración y Estado del Coche (Nivel Macro)
class CarStatus(BaseModel):
    tyre_compound: str = Field(..., example="SOFT", description="SOFT, MEDIUM, HARD, INTER, WET")
    tyre_age_laps: int = Field(..., example=12, description="Vueltas de vida del neumático")
    fuel_load_kg: Optional[float] = Field(None, example=45.5, description="Carga de combustible estimada")
    front_wing_angle: Optional[float] = Field(None, description="Ángulo del alerón delantero")

# 3. Condiciones Meteorológicas Dinámicas
class WeatherConditions(BaseModel):
    air_temperature: float = Field(25.0, description="Temperatura del aire en °C")
    track_temperature: float = Field(35.0, description="Temperatura de la pista en °C")
    humidity: float = Field(45.0, description="Porcentaje de humedad")
    wind_speed: float = Field(..., example=15.2, description="Velocidad del viento en km/h")
    wind_direction: int = Field(..., ge=0, le=360, example=180, description="Dirección del viento en grados")
    rainfall: bool = Field(False, description="Presencia de lluvia")

# 4. Request Principal Refactorizado
class PredictRequest(BaseModel):
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    circuit_id: str = Field(..., example="madrid-2026")
    driver_id: int = Field(..., example=14)
    session_type: str = Field(..., example="RACE", description="FP1, FP2, FP3, QUALY, RACE")
    lap_number: int = Field(..., example=45)
    
    # Modelos anidados para mantener el JSON limpio
    weather: WeatherConditions
    car_status: CarStatus
    
    # Telemetría en formato de serie temporal
    telemetry_window: List[TelemetryPoint]

# 5. Response Ampliado
class PredictionResponse(BaseModel):
    prediction_id: str
    predicted_lap_time: float = Field(..., example=82.345, description="Tiempo de vuelta predicho en segundos")
    tyre_degradation_score: float = Field(..., ge=0, le=1, description="Estimación de desgaste para la vuelta")
    aero_efficiency: Dict[str, float] = Field(..., example={"cd": 0.85, "cl": 2.45})
    energy_usage: Dict[str, float] = Field(..., example={"soc_delta": -5.2})
    sector_times: Dict[str, float] = Field(..., example={"sector_1": 28.5, "sector_2": 31.2, "sector_3": 22.6})
