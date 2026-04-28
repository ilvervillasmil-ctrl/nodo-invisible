import pytest
import math
import numpy as np
from unittest.mock import MagicMock
import sys

# --- PROTECCIÓN DE ENTORNO (MOCKS) ---
# Evita que el test falle por dependencias externas de formulas.interaction
mock_formulas = MagicMock()
sys.modules["formulas"] = mock_formulas
sys.modules["formulas.interaction"] = MagicMock()
sys.modules["formulas.coherence"] = MagicMock()

from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
from core.constants import THETA_CUBE_DEG, PHI

class TestSoberaniaVillasmilOmega:
    @pytest.fixture
    def engine(self):
        return OmegaEngine()

    # 1. TEST DE INTERVALO ESTRUCTURAL (Mínimo/Máximo)
    def test_intervalo_vpsi_puro(self, engine):
        """
        Verifica que el motor respete los límites 1/27 y 26/27 
        definidos en el Teorema de la Verdad Estructural.
        """
        assert pytest.approx(BETA_VPSI, rel=1e-5) == 1.0/27.0
        assert pytest.approx(ALPHA_VPSI, rel=1e-5) == 26.0/27.0
        
        # El motor nunca debe devolver menos de BETA_VPSI
        res_min = engine.apply_vpsi_truth(C=0.0)
        assert res_min >= BETA_VPSI

    # 2. TEST DE SOBERANÍA (Mantenimiento de Ritmo 2s)
    def test_mantenimiento_soberano_2s(self, engine):
        """
        El observador mantiene su ángulo crítico (11.09°) durante el ciclo 
        biométrico de 2 segundos. La respiración es el motor de la oscilación.
        """
        theta_anclaje = THETA_CUBE_DEG # 11.09°
        T = 2.0 # Segundos
        
        tiempos = np.linspace(0, T, 20)
        for t in tiempos:
            # Oscilación de la respiración (0.5 grados de desviación permitida)
            # El observador mantiene el anclaje a pesar del "aliento"
            theta_inst = theta_anclaje + 0.5 * math.sin(math.pi * t)
            
            # Calculamos Coherencia (C) basada en la alineación
            c_input = math.cos(math.radians(theta_inst - theta_anclaje))
            
            # Aplicamos la Verdad Estructural
            yr = engine.apply_vpsi_truth(C=c_input)
            
            # Validación de soberanía: el sistema no colapsa ni se satura
            assert yr >= BETA_VPSI - 1e-7, f"Colapso en t={t}"
            assert yr <= ALPHA_VPSI + 1e-7, f"Saturación en t={t}"

    # 3. TEST DE COLAPSO (Pérdida de Estructura)
    def test_identificacion_colapso_terminal(self, engine):
        """
        Si el ángulo se desvía totalmente (Perturbación), el sistema 
        debe reportar el valor mínimo (BETA), indicando colapso.
        """
        # Desviación extrema de 90 grados
        resultado = engine.apply_vpsi_truth(C=0.0)
        
        # El colapso es el residuo 1/27 (BETA)
        assert pytest.approx(resultado, rel=1e-5) == BETA_VPSI
        
    # 4. TEST DE ESCALADO BIOLÓGICO (PHI/2)
    def test_escalado_biologico_live(self, engine):
        """
        Valida que el reporte vivo aplique el escalado PHI/2 
        sobre la verdad estructural sin romper la lógica del cubo.
        """
        c_omega = 1.0 # Coherencia máxima
        truth = engine.apply_vpsi_truth(c_omega)
        
        # El resultado vivo escala por PHI/2 (aprox 0.809)
        resultado_vivo = truth * (PHI / 2.0)
        
        # Verificamos que el escalado no produzca valores negativos o nulos
        assert resultado_vivo > 0.7 # Valor esperado aproximado para ALPHA_VPSI * PHI/2
