import math
from decimal import Decimal, getcontext

# ======================================================================
# CONFIGURACIÓN DE PRECISIÓN (Aumentada para evitar errores de redondeo)
# ======================================================================
getcontext().prec = 100 

# ======================================================================
# PARÁMETROS ESTRUCTURALES DEL SISTEMA
# ======================================================================
CUBO_TOTAL = Decimal(27)
DECIMAL_BASE = Decimal(10)
Q = CUBO_TOTAL + DECIMAL_BASE      # 37
P = DECIMAL_BASE + 1               # 11
EPSILON = Decimal('1e-90')         # Tolerancia estricta para el test

# ======================================================================
# FUNCIONES DEL TEOREMA 8
# ======================================================================
def raiz_q():
    """Calcula R = (P^Q + Q^Q)^(1/Q) con precisión arbitraria."""
    return (Decimal(P)**Decimal(Q) + Decimal(Q)**Decimal(Q)) ** (Decimal(1) / Decimal(Q))

def identidad_exacta():
    """Calcula la forma exacta: R = Q * (1 + (P/Q)^Q)^(1/Q)."""
    return Decimal(Q) * (1 + (Decimal(P) / Decimal(Q)) ** Decimal(Q)) ** (Decimal(1) / Decimal(Q))

# ======================================================================
# TESTS DE VERIFICACIÓN (Pytest style)
# ======================================================================
def test_teorema_identidad_exacta():
    """Verifica que la identidad algebraica es exacta."""
    r = raiz_q()
    exacta = identidad_exacta()
    
    diff = abs(r - exacta)
    print(f"\n--- Verificación del Teorema 8 ---")
    print(f"Lado izquierdo (R) : {r}")
    print(f"Lado derecho (Forma): {exacta}")
    print(f"Diferencia          : {diff}")
    
    assert diff < EPSILON

def test_corolario_normalizacion():
    """Verifica la normalización U = R/Q."""
    u = raiz_q() / Decimal(Q)
    esperado = (1 + (Decimal(P) / Decimal(Q)) ** Decimal(Q)) ** (Decimal(1) / Decimal(Q))
    
    print(f"\n--- Verificación del Corolario 8.1 ---")
    print(f"Normalización (U)   : {u}")
    print(f"Valor esperado      : {esperado}")
    
    assert abs(u - esperado) < EPSILON

if __name__ == "__main__":
    try:
        test_teorema_identidad_exacta()
        test_corolario_normalizacion()
        print("\n✅ Todos los tests superados: La identidad algebraica es consistente.")
    except AssertionError as e:
        print(f"\n❌ Fallo en el test: {e}")
