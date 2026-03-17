import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, global_mean_pool

class CircuitGNN(torch.nn.Module):
    """
    Arquitectura GNN para analizar la topografía del circuito y predecir
    el impacto en el rendimiento por micro-sector.
    """
    
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super(CircuitGNN, self).__init__()
        # 1ª Capa Convolucional (procesa vecindarios inmediatos)
        self.conv1 = GCNConv(in_channels, hidden_channels)
        # 2ª Capa (extrae patrones espaciales complejos)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        # 3ª Capa
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        
        # Capa lineal para regresión final por nodo
        self.lin = torch.nn.Linear(hidden_channels, out_channels)

    def forward(self, x, edge_index, edge_attr=None):
        # 1. Aplicar mensaje pasando por el grafo
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.1, training=self.training)
        
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        
        x = self.conv3(x, edge_index)
        x = F.relu(x)
        
        # 2. Regresión final (Output: Performance Coefficient por nodo)
        out = self.lin(x)
        
        return out

if __name__ == "__main__":
    from builder import CircuitGraphBuilder
    
    # 1. Builder de prueba
    builder = CircuitGraphBuilder(n_points=100)
    data = builder.generate_dummy_circuit("Madrid-2026")
    
    # 2. Modelo
    # in_channels=4 (radio, elevación, rugosidad, avg_speed)
    # out_channels=1 (coeficiente de fricción/rendimiento base del sector)
    model = CircuitGNN(in_channels=4, hidden_channels=32, out_channels=1)
    
    # 3. Inferencia Dummy
    output = model(data.x, data.edge_index)
    print(f"Salida del modelo GNN (coeficientes por nodo): {output.shape}")
    print(f"Ejemplo de predicción nodo 0: {output[0].item()}")
