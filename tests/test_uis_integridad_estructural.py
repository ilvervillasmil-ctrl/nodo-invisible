import math

class UISPrimeEngine:
    """
    Motor de Identificación Estructural (CRF-UIS).
    Valida la arquitectura 6k+1 y filtra mediante Pinza de Tenazas.
    """
    
    @staticmethod
    def is_prime_mr(n, k=40):
        """Test Miller-Rabin determinista para n < 3.3e16 (con los witnesses correctos)"""
        if n < 2: return False
        if n == 2 or n == 3: return True
        if n % 2 == 0: return False
        
        # Test de divisibilidad simple pre-MR
        for p in [3, 5, 7, 11, 13, 17, 19, 23]:
            if n == p: return True
            if n % p == 0: return False
            
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
            
        # Witnesses para Miller-Rabin (seguros hasta n < 3.3e16)
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
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

    @classmethod
    def is_prime_uis(cls, n):
        """Filtro UIS: ADN 6k+1 + Pinza de Tenazas"""
        if n < 7: return n in [2, 3, 5]
        # ADN estructural: 6k+1
        if n % 6 != 1: return False
        
        # Pinza de Tenazas (filtros modulares contra fases muertas)
        if n % 5 == 0: return False
        if n % 7 == 0: return False
        
        return cls.is_prime_mr(n)

    @classmethod
    def find_next_prime_uis(cls, start):
        """Busca el siguiente nodo de anclaje (primo)"""
        k = (start + 5) // 6
        while True:
            candidate = 6 * k + 1
            if candidate > start and cls.is_prime_uis(candidate):
                return candidate
            k += 1

# --- EJECUCIÓN ---
if __name__ == "__main__":
    try:
        start_val = int(input("Número de inicio (ej: 638359262626): ") or 638359262626)
        engine = UISPrimeEngine()
        print(f"Buscando desde {start_val}...")
        
        # Ejemplo: buscar el siguiente
        primo = engine.find_next_prime_uis(start_val)
        print(f"Primo encontrado: {primo}")
        
    except ValueError:
        print("Error: Entrada no válida.")
