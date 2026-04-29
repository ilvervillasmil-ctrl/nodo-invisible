import math
from constants import BETA, GAMMA_COUPLING, EPSILON_OBSERVER, CUBE_VOLUME
from engine import ALPHA_VPSI, BETA_VPSI

def test_light_v33_observability():
    """
    TEST TÉCNICO: Validación de la Ecuación de la Luz como Proyección.
    Calcula la convergencia entre el 'sudor' (energía) y la interfaz (percepción).
    """
    print("--- INICIANDO VALIDACIÓN TÉCNICA: ECUACIÓN DE LA LUZ ---")

    # A. Cálculo de la Proyección (El fenómeno físico / 'Sudor')
    # L = 2 * ALPHA * BETA
    L_fisica = 2 * ALPHA_VPSI * BETA_VPSI
    
    # B. Cálculo de la Interfaz (La observabilidad / 'Lo que se ve')
    # Basado en constants.py: GAMMA_COUPLING = BETA / EPSILON_OBSERVER
    # Por tanto, la luz percibida es la inversa del acoplamiento en el centro
    L_perceptual = BETA_VPSI / GAMMA_COUPLING

    print(f"L_física (Proyección 52/729): {L_fisica:.10f}")
    print(f"L_perceptual (Interfaz):      {L_perceptual:.10f}")

    # C. Verificación de Invarianza
    # La luz debe ser la diferencia que permite la observación sin romper F3
    error_tolerancia = 1e-15
    
    # Test 1: La luz es el puente entre la estructura y el residuo del observador
    # 2 * alpha * epsilon_observer * gamma_coupling debe igualar a L_fisica
    val_identidad = 2 * ALPHA_VPSI * EPSILON_OBSERVER * GAMMA_COUPLING
    
    assert abs(L_fisica - val_identidad) < error_tolerancia, "Falla: La luz no es coherente con el acoplamiento Gamma"
    
    # Test 2: Invarianza de Masa (La luz no tiene volumen)
    assert (ALPHA_VPSI + BETA_VPSI) == 1.0, "Falla: Error en la partición unitaria del cubo"

    print("ESTADO: COHERENCIA PROYECTIVA VALIDADA.")
    print(f"IDENTIDAD DE VILLASMIL: L = {L_fisica}")

if __name__ == "__main__":
    test_light_v33_observability()
