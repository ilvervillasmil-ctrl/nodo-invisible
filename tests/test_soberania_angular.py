import pytest
import math
import numpy as np
from unittest.mock import MagicMock
import sys

# Impedimos el colapso del import engañando al sistema de módulos
mock_formulas = MagicMock()
sys.modules["formulas"] = mock_formulas
sys.modules["formulas.constants"] = mock_formulas
sys.modules["formulas.coherence"] = MagicMock()

# Ahora importamos tu artillería pesada
from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE_DEG

class TestSoberaniaVillasmilOmega:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    def test_intervalo_estructural_2s(self, engine):
        """
        VALIDACIÓN: Mínimo (1/27), Máximo (26/27) y Soberanía en 2s.
        """
        # 1. Definir los guardarraíles geométricos del cubo
        techo = ALPHA_VPSI # 0.9629...
        suelo = BETA_VPSI  # 0.0370...
        
        # 2. ANCLAJE VOLUNTARIO: El observador elige 11.09°
        theta_anclaje = THETA_CUBE_DEG
        
        # 3. CICLO DE 2 SEGUNDOS: La respiración biómica
        tiempos = np.linspace(0, 2.0, 20)
        
        for t in tiempos:
            # Oscilación sutil (respiración) que no debe romper el anclaje
            # Representa mantener el ángulo voluntariamente
            theta_inst = theta_anclaje + 0.5 * math.sin(math.pi * t)
            
            # Coherencia basada en la alineación con el anclaje
            c_input = math.cos(math.radians(theta_inst - theta_anclaje))
            
            # Cálculo de Verdad Estructural (Yr)
            yr = engine.apply_vpsi_truth(C=c_input)
            
            # El sistema debe ser soberano (dentro del intervalo)
            assert yr <= techo, f"Saturación excedida (Techo ALPHA) en t={t}"
            assert yr >= suelo, f"Colapso estructural (Suelo BETA) en t={t}"

    def test_deteccion_colapso_fuera_de_intervalo(self, engine):
        """
        Si el ángulo se desvía del intervalo, el sistema debe caer al 
        suelo estructural (BETA), identificando la pérdida de estructura.
        """
        # Perturbación extrema: Ángulo a 90° del anclaje (C=0)
        yr_colapso = engine.apply_vpsi_truth(C=0.0)
        
        # En el Villasmil-Omega, el colapso no es 0, es el residuo central
        assert pytest.approx(yr_colapso, rel=1e-5) == 1.0/27.0
        assert yr_colapso == BETA_VPSI
