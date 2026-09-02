import numpy as np
import time

def is_prime_uis_xtreme(n: int) -> bool:
    """
    Motor CRF-UIS con Pinza de Tenazas y Filtro Geométrico Estricto.
    Optimiza la CPU purgando el 66.6% del universo en la primera línea.
    """
    if n < 2:
        return False
        
    # FILTRO 1: Canal 6k ± 1 (Descarta pares y múltiplos de 3 en un microsegundo)
    if n % 6 != 1 and n % 6 != 5:
        return False

    # FILTRO 2: La Pinza de Tenazas (Purga compuestos pequeños de forma ultra rápida)
    for p in:
        if n % p == 0:
            return n == p

    # TEST FINAL: Miller-Rabin (Solo se ejecuta si el número pasó los dos filtros anteriores)
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for a in witnesses:
        if a >= n:
            break
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def analizar_frecuencias_uis(inicio: int, ventana: int):
    """
    Ejecuta el laboratorio forense de Gaps y FFT sobre el retículo hexagonal.
    """
    print("=" * 70)
    print(f" LAB LAB FORENSE UIS: ANÁLISIS DE FRECUENCIAS EN ESCALA {inicio:.1e}")
    print("=" * 70)
    
    inicio_tiempo = time.time()
    
    # 1. Proyectar candidatos únicamente en las columnas válidas (6k ± 1)
    k0 = inicio // 6
    k1 = (inicio + ventana) // 6
    
    nodos_vivos = []
    for k in range(k0, k1):
        # Rama positiva
        n_pos = 6 * k + 1
        if is_prime_uis_xtreme(n_pos):
            nodos_vivos.append(n_pos)
            
        # Rama negativa / espejo
        n_neg = 6 * k - 1
        if is_prime_uis_xtreme(n_neg):
            nodos_vivos.append(n_neg)
            
    nodos_vivos.sort()
    duracion_busqueda = time.time() - inicio_tiempo
    
    print(f" -> Primos encontrados : {len(nodos_vivos)}")
    print(f" -> Tiempo de cómputo  : {duracion_busqueda:.4f} segundos")
    
    if len(nodos_vivos) < 2:
        print(" >> No hay suficientes nodos para calcular brechas.")
        return

    # 2. Calcular las brechas (Gaps) entre primos consecutivos
    gaps = np.diff(nodos_vivos)
    media_gaps = np.mean(gaps)
    
    # 3. Aplicar la Transformada Rápida de Fourier (FFT) sobre las brechas
    # Esto busca el ritmo o la "música periódica" oculta en las distancias
    fft_valores = np.abs(np.fft.fft(gaps))
    
    # Ignoramos el componente de frecuencia 0 (DC offset) para buscar la oscilación real
    frecuencia_dominante = np.argmax(fft_valores[1:]) + 1
    
    print("-" * 70)
    print(" RESULTADOS CUANTIFICADOS DEL RETÍCULO")
    print("-" * 70)
    print(f" Brecha promedio (Media de Gaps) : {media_gaps:.4f}")
    print(f" Índice de Frecuencia Dominante  : {frecuencia_dominante}")
    print(f" Máxima amplitud espectral       : {np.max(fft_valores[1:]):.2f}")
    print("=" * 70)


if __name__ == "__main__":
    # Corremos la simulación en una escala de un millón para que sea instantáneo en tu CPU
    analizar_frecuencias_uis(inicio=1_000_000, ventana=100_000)
