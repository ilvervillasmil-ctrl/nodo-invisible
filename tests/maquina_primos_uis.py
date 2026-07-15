import math

def is_prime_mr(n, k=8):
    """Miller-Rabin (rápido y confiable para números grandes)"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    witnesses = [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37][:k]
    for a in witnesses:
        if a >= n: break
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def is_prime_uis(n):
    """Filtro completo UIS"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    if n % 6 != 1: return False  # Solo anclas 6k+1
    
    # Filtros modulares rápidos
    for f in [5,7,9,11,13,17,19,23]:
        if n % f == 0: return False
    return is_prime_mr(n)

def find_next_prime_uis(start):
    """Busca el siguiente primo a partir de start"""
    k = (start + 5) // 6
    while True:
        candidate = 6 * k + 1
        if is_prime_uis(candidate):
            return candidate
        k += 1

# Ejemplo de uso
if __name__ == "__main__":
    print("=== Máquina de Primos UIS ===")
    start = int(input("Ingresa número inicial (ej: 638359262626): ") or 638359262626)
    cantidad = int(input("Cuántos primos quieres generar? (ej: 10): ") or 10)
    
    current = start
    for i in range(cantidad):
        current = find_next_prime_uis(current)
        print(f"Primo {i+1}: {current}")
