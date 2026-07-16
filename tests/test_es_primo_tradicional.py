import math
import time

def es_primo_tradicional(n):
    """Verifica si un número es primo usando el método tradicional."""
    if n <= 1:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w
    return True

def es_primo_uis(n):
    """Verifica si un número es primo usando el Teorema de Arquitectura Modular de Primalidad."""
    if n <= 1:
        return False
    if n == 2 or n == 3:
        return True
        
    # Filtro de ubicación: 6k ± 1 (Elimina múltiplos de 2 y 3)
    if n % 6 != 1 and n % 6 != 5:
        return False
        
    # Filtro de eliminación base: módulos fundamentales del UIS
    # El módulo 9 se omite computacionalmente porque sus residuos prohibidos (0, 3, 6) 
    # ya fueron descartados por el filtro de ubicación al ser múltiplos de 3.
    if n % 5 == 0 or n % 7 == 0:
        return False
        
    # Filtro de eliminación extendido: primos ≤ √n
    # Como ya evaluamos el 5 y el 7, comenzamos el bucle desde el 11.
    max_divisor = math.isqrt(n) + 1
    for p in range(11, max_divisor, 6):
        # Evalúa p y p+2 (ej: 11 y 13, 17 y 19, etc.)
        if n % p == 0 or n % (p + 2) == 0:
            return False
            
    return True

def probar_teorema_uis(limite):
    """Prueba el Teorema de Arquitectura Modular de Primalidad en el rango [1, limite]."""
    print(f"Probando el Teorema de Arquitectura Modular de Primalidad en el rango [1, {limite}]...")

    primos_tradicional = 0
    primos_uis = 0
    errores = 0

    start_time = time.time()

    for n in range(1, limite + 1):
        tradicional = es_primo_tradicional(n)
        if tradicional:
            primos_tradicional += 1

        uis = es_primo_uis(n)
        if uis:
            primos_uis += 1

        if tradicional != uis:
            errores += 1
            print(f"Error en n = {n}: Tradicional = {tradicional}, UIS = {uis}")

    end_time = time.time()
    tiempo_ejecucion = end_time - start_time

    print("\n--- Resultados ---")
    print(f"Números primos (método tradicional): {primos_tradicional}")
    print(f"Números primos (método UIS): {primos_uis}")
    print(f"Errores: {errores}")
    print(f"Tiempo de ejecución: {tiempo_ejecucion:.2f} segundos")

    if errores == 0:
        print(f"\n✅ El Teorema de Arquitectura Modular de Primalidad es válido en el rango [1, {limite:,}].")
    else:
        print(f"\n❌ Se encontraron {errores} errores en el rango [1, {limite:,}].")

# Ejecutar la prueba
probar_teorema_uis(100000000)
