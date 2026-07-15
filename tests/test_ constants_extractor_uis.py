import numpy as np

def extraer_constantes_uis():
    """
    Extrae los invariantes fundamentales del retículo hexagonal.
    Estas constantes definen la resonancia y la densidad estructural.
    """
    
    # Constantes base del cubo 3x3x3
    BETA = 1/27
    ALPHA = 26/27
    PHI = (1 + np.sqrt(5)) / 2
    
    # Cálculo de la Frecuencia fundamental (Omega efectiva)
    # Basada en la resonancia de fase del retículo
    OMEGA_EFF = np.pi * (1 - np.sqrt(BETA))
    
    # Cálculo de la Constante de fricción de fases (Phi efectiva)
    # Refleja la resistencia estructural medida en el sistema
    PHI_EFF = 1 / (1 - np.sqrt(BETA) * (np.pi/6))
    
    # Cálculo del Período de oscilación del sistema
    T_PERIOD = 2 * np.pi / OMEGA_EFF
    
    constantes = {
        "BETA_residuo": BETA,
        "ALPHA_estructura": ALPHA,
        "PHI_friccion": PHI,
        "OMEGA_frecuencia": OMEGA_EFF,
        "PHI_efectiva": PHI_EFF,
        "T_periodo_oscilacion": T_PERIOD
    }
    
    print("--- INVARIANTES ESTRUCTURALES DEL RETÍCULO (UIS) ---")
    for k, v in constantes.items():
        print(f"{k}: {v:.6f}")
    
    return constantes

if __name__ == "__main__":
    extraer_constantes_uis()
