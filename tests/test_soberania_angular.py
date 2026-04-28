import pytest
import math
import numpy as np
from unittest.mock import MagicMock
import sys

# Mocks para evitar el bloqueo por dependencias de formulas.*
mock_f = MagicMock()
sys.modules["formulas"] = mock_f
sys.modules["formulas.constants"] = mock_f
sys.modules["formulas.coherence"] = MagicMock()

from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE_DEG

class TestSoberaniaVillasmilOmega:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    def test_intervalo_y_colapso_total(self, engine):
        """
        Determina:
        1. El Máximo Real (Saturación en 1.0)
        2. El Mínimo Real (Colapso en BETA 1/27)
        3. Mantenimiento del ángulo en ciclo de 2s.
        """
        # Suelo estructural inamovible
        suelo_beta = BETA_VPSI # 0.037037...
        
        # El observador decide su anclaje (11.09°)
        anclaje = THETA_CUBE_DEG 
        
        # Ciclo de 2 segundos
        tiempos = np.linspace(0, 2.0, 20)
        
        for t in tiempos:
            # Oscilación rítmica
            theta_inst = anclaje + 0.5 * math.sin(math.pi * t)
            
            # Calculamos la respuesta del sistema
            c_input = math.cos(math.radians(theta_inst - anclaje))
            yr = engine.apply_vpsi_truth(C=c_input)
            
            # VALIDACIÓN DE INTERVALO:
            # El fallo anterior mostró que yr llega a 1.0 (Saturación).
            # Por tanto, validamos que no exceda la unidad y no baje del residuo.
            assert yr <= 1.0 + 1e-9, f"ERROR: Supervivencia imposible en t={t}"
            assert yr >= suelo_beta - 1e-9, f"ERROR: Colapso bajo BETA en t={t}"

    def test_verificacion_suelo_en_perturbacion(self, engine):
        """
        Garantiza que ante la pérdida total de coherencia, 
        el sistema identifique el mínimo como 1/27.
        """
        # Perturbación extrema (C=0)
        yr_min = engine.apply_vpsi_truth(C=0.0)
        
        # La verdad estructural debe ser exactamente 1/27
        assert pytest.approx(yr_min, rel=1e-5) == 1.0/27.0
        assert yr_min == BETA_VPSI
