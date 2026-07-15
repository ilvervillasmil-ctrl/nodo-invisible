import numpy as np

def evaluar_estructura_densidad(inicio, ventana):
    """
    Evaluación bruta de la estructura de supervivencia.
    Sin aserciones, solo extracción de datos crudos.
    """
    k_start = inicio // 6
    k_end = (inicio + ventana) // 6
    
    nodos_vivos = []
    
    # Filtro de fase (Pinza de Tenazas extendida)
    # Evaluamos la densidad real de los nodos que sobreviven
    for k in range(k_start, k_end):
        n = 6 * k + 1
        if all(n % p != 0 for p in [5, 7, 11, 13, 17, 19, 23, 29, 31]):
            nodos_vivos.append(n)
            
    # Cálculo de métricas estructurales
    gaps = np.diff(nodos_vivos)
    densidad = len(nodos_vivos) / (k_end - k_start)
    
    # Análisis de frecuencia (transformada de Fourier simple de los gaps)
    # Esto revelará si hay una periodicidad subyacente
    frecuencias = np.fft.fft(gaps)
    
    return {
        "nodos": len(nodos_vivos),
        "densidad": densidad,
        "media_gap": np.mean(gaps),
        "std_gap": np.std(gaps),
        "frecuencia_dominante": np.argmax(np.abs(frecuencias))
    }

# Ejecución de evaluación bruta
if __name__ == "__main__":
    inicio = 10**14
    ventana = 10**7
    resultados = evaluar_estructura_densidad(inicio, ventana)
    
    print(f"--- EVALUACIÓN ESTRUCTURAL BRUTA {inicio} ---")
    for k, v in resultados.items():
        print(f"{k}: {v}")
