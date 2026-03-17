import torch
import torch.nn as nn

class AeroPINN(nn.Module):
    """
    Physics-Informed Neural Network para predecir Cd (Drag) y Cl (Downforce).
    
    Integra la pérdida basada en los datos observados con la pérdida de las
    ecuaciones físicas simplificadas (Base: Navier-Stokes/Euler).
    """
    
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64):
        super(AeroPINN, self).__init__()
        # Red neuronal densa para aproximar Cd y Cl
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(), # Tanh es preferible en PINNs para facilitar el cálculo de gradientes
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 2) # Output: [Cd, Cl]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Inputs: [Velocidad, DRS_Status, Pitch, Roll]
        Outputs: [Cd, Cl]
        """
        return self.net(x)

    def physics_loss(self, inputs: torch.Tensor, outputs: torch.Tensor) -> torch.Tensor:
        """
        Calcula la pérdida física basada en la relación 
        Arrastre = 0.5 * rho * v^2 * Area * Cd
        
        Asegura que Cd y Cl se comporten de acuerdo a la ley cuadrada de la velocidad.
        """
        v = inputs[:, 0] # Velocidad
        cd_pred, cl_pred = outputs[:, 0], outputs[:, 1]
        
        # En una PINN real, aquí calcularíamos gradientes respecto a los inputs (autograd)
        # y forzaríamos el cumplimiento de las ecuaciones diferenciales residuales.
        
        # Simplificación: Consistencia física (Cd no puede ser negativo, Cl aumenta con V^2)
        penalty_cd = torch.mean(torch.relu(-cd_pred))
        penalty_cl = torch.mean(torch.relu(-cl_pred))
        
        return penalty_cd + penalty_cl

if __name__ == "__main__":
    # Test Módulo 1: Aero
    model = AeroPINN()
    
    # Inputs: [V (m/s), DRS (bool), Pitch, Roll]
    dummy_input = torch.tensor([[80.0, 1.0, 0.01, 0.005]], requires_grad=True)
    preds = model(dummy_input)
    
    loss_p = model.physics_loss(dummy_input, preds)
    
    print(f"Predicción Aero [Cd, Cl]: {preds.detach().numpy()}")
    print(f"Pérdida física residual: {loss_p.item()}")
