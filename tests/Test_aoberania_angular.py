import pytest
import math
import numpy as np
from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE, THETA_CUBE_DEG, PHI

class TestSoberaniaAngular:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    def test_mantenimiento_ritmo_voluntario(self, engine):
        """
        HIPÓTESIS: El observador mantiene el ángulo en 11.09° (reposo) 
        mientras la respiración genera una micro-oscilación.
        """
        T = 2.0  # Ritmo biológico de 2 segundos
        theta_anclaje = THETA_CUBE_DEG  # 11.09°
        amplitud_respiracion = 2.0  # El "latido" permitido
        
        # Simulación de 2 segundos de respiración consciente
        tiempos = np.linspace(0, T, 10)
        for t in tiempos:
            # El ángulo oscila pero el anclaje es firme
            theta_inst = theta_anclaje + amplitud_respiracion * math.sin((math.pi * t) / T)
            
            # Calculamos coherencia basada en la desviación del anclaje
            c_input = math.cos(math.radians(theta_inst - theta_anclaje))
            truth_val = engine.apply_vpsi_truth(C=c_input)
            
            # VALIDACIÓN: El sistema debe permanecer estable (no colapso)
            assert BETA_VPSI <= truth_val <= 1.0, f"Colapso en t={t}s"

    def test_deteccion_colapso_fuera_de_intervalo(self, engine):
        """
        HIPÓTESIS: Si el ángulo supera el intervalo máximo (ALPHA_VPSI),
        el sistema debe ser detectado como inestable o saturado.
        """
        # Forzamos un ángulo de "Perturbación" fuera de los límites del cubo
        theta_perturbado = 95.0  # Supera el máximo teórico de ~74.35°
        
        # La coherencia cae drásticamente al desalinearse de la diagonal
        c_caotico = math.cos(math.radians(theta_perturbado))
        truth_val = engine.apply_vpsi_truth(C=c_caotico)
        
        # Si la verdad estructural se acerca demasiado al piso BETA 
        # bajo condiciones de alta demanda, se considera colapso de coherencia
        assert truth_val < 0.5, "El sistema debería reportar baja coherencia en ángulos críticos"

    def test_intervalos_exactos_vpsi(self):
        """
        Valida que los límites del test coincidan con la geometría 3x3x3.
        """
        assert pytest.approx(ALPHA_VPSI, rel=1e-4) == 0.9629  # 26/27
        assert pytest.approx(BETA_VPSI, rel=1e-4) == 0.0370   # 1/27
