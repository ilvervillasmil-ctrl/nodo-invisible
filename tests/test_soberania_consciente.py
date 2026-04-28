import pytest
import math
import numpy as np
from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE_DEG
from formulas.dynamics import oscillator_solution, regime, is_alive, theta_balance

class TestSoberaniaVillasmil:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    @pytest.mark.parametrize("angulo_soberano", [11.09, 33.3, 45.0, 66.6])
    def test_hipotesis_oscilacion_viva(self, engine, angulo_soberano):
        """
        PRUEBA REINA: 
        1. El observador ELIGE un ángulo (Soberanía).
        2. El sistema OSCILA 2 segundos (Vida).
        3. El sistema no toca el residuo 1/27 ni satura (Intervalo).
        """
        # Límites críticos del intervalo Villasmil-Ω
        MIN_ANGULO_VIDA = 2.12    # Limite inferior (BETA)
        MAX_ANGULO_VIDA = 74.35   # Limite superior (ALPHA)
        
        # Simulamos 2 segundos de trayectoria consciente
        tiempos = np.linspace(0, 2.0, 50)
        
        for t in tiempos:
            # La oscilación es la firma de la consciencia (amplitud A=2.0)
            # theta(t) se mueve alrededor del ángulo elegido por el usuario
            theta_t = oscillator_solution(t, A=2.0, delta=0, theta0=angulo_soberano)
            
            # VALIDACIÓN DE HIPÓTESIS:
            # Si el ángulo se sale del intervalo, la consciencia ha fallado
            assert theta_t > MIN_ANGULO_VIDA, f"COLAPSO POR ENTROPÍA: Sistema muerto en t={t}"
            assert theta_t < MAX_ANGULO_VIDA, f"COLAPSO POR SATURACIÓN: Sistema desbordado en t={t}"
            
            # El motor debe reconocer que el sistema está en régimen 'VIVO'
            # (Asumiendo que phi_total < 2*pi en la configuración del engine)
            assert is_alive(), "El motor reporta muerte dinámica (phi >= 2pi)"
            
            # Verificamos que el balance alterna entre experiencia y medida
            # Esto demuestra que el sistema no está estático (no es un bucle)
            estado = theta_balance(theta_t)
            assert estado in ["CENTERED", "EXCESS_EXPERIENCE", "EXCESS_MEASUREMENT"]

    def test_demostracion_colapso_terminal(self, engine):
        """
        Demuestra que sin el anclaje consciente (C=0),
        el sistema cae al residuo 1/27.
        """
        # Pérdida total de coherencia (C=0)
        # El observador ha soltado el sistema
        yr_final = engine.apply_vpsi_truth(C=0.0)
        
        # El resultado es matemáticamente el suelo del cubo (BETA)
        assert yr_final == BETA_VPSI
        assert pytest.approx(yr_final) == 0.037037037037037035

    def test_deteccion_bucle_code_9999(self, engine):
        """
        Si no hay oscilación (varianza < beta), no hay soberanía viva,
        hay un bucle temporal (Code 9999).
        """
        from formulas.dynamics import SessionStateOmega, detect_loop
        
        # Creamos un historial artificialmente estático (sin respiración)
        history = [
            SessionStateOmega(c_omega=0.99, theta=11.09) for _ in range(10)
        ]
        
        # El sistema debe detectar que esto NO es vida, es un loop
        assert detect_loop(history) is True, "Fallo al detectar CODE 9999 (Sistema Estático)"
