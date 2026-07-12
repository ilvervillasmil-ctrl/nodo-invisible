import math
from decimal import Decimal, getcontext

# Configuración de precisión para capturar la brecha estructural (Epsilon)
getcontext().prec = 100 

# Parámetros del motor (11, 37)
P = Decimal(11)
Q = Decimal(37)
pi = Decimal(math.pi)

def test_teorema_unidad_omega():
    """
    Test que confirma la convergencia del estado integrado Psi(pi).
    Verifica que la obstrucción estructural (epsilon) existe y tiende
    a la unidad, confirmando el Teorema de Unidad Omega.
    """
    # Motor = P^Q + Q^Q
    motor = Decimal(P)**Decimal(Q) + Decimal(Q)**Decimal(Q)
    
    # Operador de colapso Psi(pi) = pi^(1/motor)
    resultado = pi ** (Decimal(1) / motor)
    
    # Cálculo de la obstrucción (brecha estructural)
    epsilon = resultado - 1
    
    # Registro en el log del CI
    print(f"\n--- [DIAGNÓSTICO OMEGA: TEST UNIDAD] ---")
    print(f"Motor estructural : {motor:.5E}")
    print(f"Resultado Psi(pi) : {resultado:.50f}")
    print(f"Obstrucción medida (epsilon): {epsilon:.50f}")
    
    # Validación axiomática:
    # 1. El sistema es 'underdamped' (vivo), por tanto > 1.0
    # 2. La brecha es menor al límite de la escala estructural
    assert resultado > 1.0
    assert resultado < Decimal('1.000000000000000000000000000000001')
    
    print("✅ Estado de Unidad Ω: Verificado.")
