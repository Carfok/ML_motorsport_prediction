import torch
import torch.nn as nn

class EnergyTFT(nn.Module):
    """
    Temporal Fusion Transformer (TFT) para predecir el consumo energético
    y el despliegue del MGU-K (350kW) en el coche de 2026.
    
    TFT permite combinar:
    - Inputs Estáticos: Características del coche, clima del GP.
    - Inputs Temporales Conocidos: Próximas curvas, DRS zones.
    - Inputs Temporales Observados: Telemetría de batería, SOC (State of Charge).
    """
    
    def __init__(self, observation_window: int = 20, prediction_horizon: int = 5):
        super(EnergyTFT, self).__init__()
        self.obs_window = observation_window
        self.pred_horizon = prediction_horizon
        
        # En una arquitectura real usaríamos Multi-head attention y Gate Linear Units
        # Para esta fase, definimos el skeleton de la arquitectura TFT
        self.temporal_encoder = nn.LSTM(input_size=5, hidden_size=64, batch_first=True)
        self.attention = nn.MultiheadAttention(embed_dim=64, num_heads=4, batch_first=True)
        self.output_layer = nn.Linear(64, prediction_horizon) # Predice los próximos 5 pasos de SOC

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input: [Batch, Time, Features]
        Features: [SOC, Speed, Throttle, MGU-K Duty, Energy Recov]
        """
        # 1. Encoding temporal
        lstm_out, _ = self.temporal_encoder(x)
        
        # 2. Self-attention para detectar patrones históricos de recuperación
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # 3. Predicción del estado futuro de la batería
        last_hidden = attn_out[:, -1, :]
        return self.output_layer(last_hidden)

if __name__ == "__main__":
    # Test Módulo 2: Energía
    model = EnergyTFT(observation_window=20, prediction_horizon=5)
    
    # 1 Batch de 20 pasos temporales con 5 features cada uno
    dummy_input = torch.rand((1, 20, 5)) 
    prediction = model(dummy_input)
    
    print(f"Predicción SOC futuro (5 pasos): {prediction.detach().numpy()}")
    print(f"Estado de carga final esperado: {prediction[0, -1].item():.4f}")
