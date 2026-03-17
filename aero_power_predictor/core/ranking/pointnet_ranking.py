import torch
import torch.nn as nn
import torch.nn.functional as F

class PointNetRanking(nn.Module):
    """
    PointNet++ Modificado para Ranking de Pilotos.
    
    Cada coche se trata como un "punto" en una nube de rendimiento.
    La arquitectura procesa el conjunto completo (los 20 coches) de golpe 
    para extraer relaciones de superioridad técnica y generar el ranking.
    """
    
    def __init__(self, num_features: int = 10, num_drivers: int = 20):
        super(PointNetRanking, self).__init__()
        # MLP para procesar características locales de cada coche (Point embedding)
        self.mlp1 = nn.Linear(num_features, 64)
        self.mlp2 = nn.Linear(64, 128)
        self.mlp3 = nn.Linear(128, 512)
        
        # Simetría: El Global Feature permite al modelo entender el "nivel" general del GP
        self.fc1 = nn.Linear(512, 256)
        self.fc2 = nn.Linear(256, 128)
        
        # Clasificación/Regresión por coche: Predictor de posición final
        self.ranking_head = nn.Linear(128, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input: [Batch, Num_Drivers, Features] (Nube de puntos de rendimiento)
        Features: [Pace_Aero, Energy_Efficiency, Tyres_Health, Driver_Skill, Gap_To_Leader]
        """
        b, n, f = x.size()
        
        # 1. Transformación individual (MLP Compartido)
        x = F.relu(self.mlp1(x))
        x = F.relu(self.mlp2(x))
        x = F.relu(self.mlp3(x))
        
        # 2. Max Pooling simétrico (Extrae la característica global de la carrera)
        global_feat, _ = torch.max(x, 1) # [B, 512]
        
        # 3. Consolidación de ranking
        x_global = global_feat.unsqueeze(1).repeat(1, n, 1) # Expandir global a cada coche
        
        # Fusionar local (coche i) con global (estado carrera)
        # En esta arquitectura simplificada, solo procesamos el global feature
        # para predecir el score de cada piloto
        out = F.relu(self.fc1(x))
        out = F.relu(self.fc2(out))
        
        # Output: Puntuación de Ranking (Menor score = mejor posición esperada)
        ranking_scores = self.ranking_head(out).squeeze(-1)
        
        return ranking_scores

if __name__ == "__main__":
    # Test Módulo 3: Ranking PointNet++
    # 20 coches con 10 métricas de rendimiento cada uno
    model = PointNetRanking(num_features=10, num_drivers=20)
    
    # 1 Batch de 20 pilotos [B, N, F]
    dummy_performance = torch.rand((1, 20, 10))
    ranking_scores = model(dummy_performance)
    
    # Generar ranking ordenado
    scores = ranking_scores[0].detach().numpy()
    sorted_indices = scores.argsort()
    
    print(f"Predicción de Ranking (Top 3):")
    for i, idx in enumerate(sorted_indices[:3]):
        print(f"P{i+1}: Piloto ID {idx} (Score: {scores[idx]:.4f})")
