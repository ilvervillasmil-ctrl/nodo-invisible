import numpy as np

def extraer_constantes_fisicas_UIS(inicio, ventana):
    """
    Extrae constantes físicas reales observando el comportamiento
    dinámico de los primos en el retículo hexagonal (6k ± 1).
    """
    k0 = (inicio + 5) // 6
    k1 = (inicio + ventana) // 6
    
    # 1. GENERACIÓN DE DATOS CRUDOS
    # Filtro de fase inicial para obtener el comportamiento del sistema
    nodos = []
    for k in range(k0, k1 + 1):
        n = 6*k + 1
        # Filtro de fase ultra-fino para obtener densidad pura
        if all(n % m != 0 for m in [5, 7, 11, 13, 17, 19, 23, 29, 31]):
            nodos.append(n)
            
    nodos = np.array(nodos)
    gaps = np.diff(nodos)
    
    # 2. EXTRACCIÓN DE CONSTANTES (La física del retículo)
    
    # Constante de Densidad de Fase (Mu_phi)
    # Proporción de nodos que sobreviven a la interferencia
    mu_phi = len(nodos) / (ventana / 6)
    
    # Constante de Resonancia de Brecha (Omega_gap)
    # Frecuencia fundamental medida vía FFT de los gaps
    fft = np.abs(np.fft.fft(gaps))
    freqs = np.fft.fftfreq(len(gaps))
    # Nos quedamos con la componente armónica dominante
    idx = np.argmax(fft[1:]) + 1
    omega_gap = np.abs(freqs[idx])
    
    # Constante de Fricción de Fase (Zeta_friction)
    # Desviación estándar de los gaps normalizada por la media
    zeta_friction = np.std(gaps) / np.mean(gaps)
    
    print(f"\n--- CONSTANTES FÍSICAS EXTRAÍDAS EN {inicio} ---")
    print(f"Densidad de Fase (mu_phi):   {mu_phi:.6f}")
    print(f"Resonancia Gap (omega_gap):  {omega_gap:.6f}")
    print(f"Fricción de Fase (zeta_fric): {zeta_friction:.6f}")
    
    return {"mu": mu_phi, "omega": omega_gap, "zeta": zeta_friction}

if __name__ == "__main__":
    # Escaneamos una ventana profunda para extraer valores reales
    extraer_constantes_fisicas_UIS(inicio=10**20, ventana=10**7)
