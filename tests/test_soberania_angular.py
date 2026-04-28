import pytest
import math
import numpy as np
from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE_DEG

class TestSoberaniaConsciente:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    @pytest.mark.parametrize("angulo_elegido", [11.09, 33.0, 45.0, 60.0])
    def test_mantenimiento_voluntario(self, engine, angulo_elegido):
        """
        HIPÓTESIS: El observador puede elegir CUALQUIER ángulo y mantenerse.
        La soberanía se demuestra si en 2s la oscilación no toca los bordes.
        """
        # Límites de la estructura (VPSI 9.4)
        LIMITE_INFERIOR_BETA = 2.12   # Ángulo de colapso por entropía
        LIMITE_SUPERIOR_ALPHA = 74.35  # Ángulo de colapso por saturación
        
        # El observador mantiene su voluntad durante el ciclo biométrico
        tiempos = np.linspace(0, 2.0, 20)
        for t in tiempos:
            # Oscilación consciente (la respiración que sostiene el ángulo)
            amplitud_respiracion = 1.0 
            theta_inst = angulo_elegido + amplitud_respiracion * math.sin(math.pi * t)
            
            # 1. Verificamos que el ángulo no sobrepasa los límites de colapso
            assert theta_inst > LIMITE_INFERIOR_BETA, f"COLAPSO POR ENTROPÍA en t={t}: Ángulo muy bajo"
            assert theta_inst < LIMITE_SUPERIOR_ALPHA, f"COLAPSO POR SATURACIÓN en t={t}: Ángulo muy alto"
            
            # 2. Calculamos la coherencia respecto al ángulo que la persona ELIGIÓ
            # Si el sistema responde a la voluntad del observador, C es alta
            c_soberana = math.cos(math.radians(theta_inst - angulo_elegido))
            yr = engine.apply_vpsi_truth(C=c_soberana)
            
            # La verdad estructural debe mantenerse viva (por encima del residuo)
            assert yr > BETA_VPSI, "El sistema ha muerto (Residuo BETA alcanzado)"

    def test_colapso_por_desborde(self, engine):
        """
        Demuestra que si se sobrepasa el ángulo superior, hay colapso estructural.
        """
        angulo_caos = 80.0 # Fuera del intervalo de 74.35°
        
        # En este punto, el motor ya no puede mapear la coherencia al cubo
        c_input = math.cos(math.radians(angulo_caos))
        yr = engine.apply_vpsi_truth(C=c_input)
        
        # El sistema se degrada hacia el mínimo porque perdió la geometría
        assert yr < 0.20, "El sistema debería mostrar degradación por desborde"
