import math

# ==================== CONFIGURACIÓN (cambia estos valores) ====================

N1 = 11                    # Número de términos de la PRIMERA suma (orden de la raíz)
N2 = 37                   # Número de términos de la SEGUNDA suma (diferente)
p = 37                     # Exponente (el mismo para ambas sumas)

# =====================================================================

# Primera suma → será el orden de la raíz
suma_orden = sum(k ** p for k in range(1, N1 + 1))

# Segunda suma (diferente, como dijiste)
suma_diferente = sum(k ** p for k in range(1, N2 + 1))

# Raíz de orden "suma_orden" de π
resultado = math.pi ** (1 / suma_orden)

# Mostrar resultados
print(f"Exponente p = {p}")
print(f"N1 (para orden de raíz) = {N1}")
print(f"N2 (suma diferente) = {N2}")
print(f"Suma orden de raíz = {suma_orden}")
print(f"Suma diferente = {suma_diferente}")
print(f"\nRaíz de orden {suma_orden} de π ≈ {resultado:.15f}")
