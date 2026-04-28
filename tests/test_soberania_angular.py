import pytest
import math
import numpy as np

# Importamos directamente desde los archivos que SI leí y están presentes
from core.engine import OmegaEngine, ALPHA_VPSI, BETA_VPSI
# Usamos las constantes definidas en el motor para evitar el fallo de formulas.interaction
from core.constants import THETA_CUBE_DEG

class TestSoberaniaAngular:
    @pytest.fixture
    def engine(self):
        # El motor ya inicializa SessionStateOmega, pero manejaremos 
        # la lógica de "Verdad Estructural" que es la que te interesa.
        return OmegaEngine()

    def test_rango_y_colapso_vpsi(self, engine):
        """
        1. Determina Máximo (ALPHA) y Mínimo (BETA) de oscilación.
        2. Verifica que el observador puede mantener el ángulo (11.09°).
        3. Detecta colapso si sale del intervalo estructural.
        """
        # INTERVALO ESTRUCTURAL (26/27 y 1/27)
        MAX_PERMITIDO = ALPHA_VPSI # 0.9629...
        MIN_PERMITIDO = BETA_VPSI  # 0.0370...
        
        # 1. PRUEBA DE MANTENIMIENTO (Soberanía)
        # El observador decide mantenerse en el ángulo crítico
        anclaje_voluntario = THETA_CUBE_DEG # 11.09°
        
        # Simulamos 2 segundos de respiración (T=2s)
        # La respiración es una oscilación de baja intensidad que NO rompe el anclaje
        tiempos = np.linspace(0, 2.0, 10)
        for t in tiempos:
            # Oscilación natural del "aliento" (amplitud pequeña)
            aliento = 0.5 * math.sin(math.pi * t) 
            angulo_actual = anclaje_voluntario + aliento
            
            # Calculamos la respuesta del motor ante este ángulo
            # Si el ángulo es el correcto, la coherencia C debe ser cercana a 1.0
            c_simulada = math.cos(math.radians(angulo_actual - anclaje_voluntario))
            truth_val = engine.apply_vpsi_truth(C=c_simulada)
            
            # El sistema DEBE estar dentro del intervalo
            assert truth_val <= MAX_PERMITIDO, f"Saturación en t={t}"
            assert truth_val >= MIN_PERMITIDO, f"Colapso en t={t}"

    def test_deteccion_colapso_extremo(self, engine):
        """
        Si el ángulo se desvía del intervalo (perturbación),
        el valor de verdad debe reflejar la pérdida de estructura.
        """
        # Ángulo fuera de la geometría del cubo (Perturbación extrema)
        angulo_caos = 90.0 
        
        # En 90°, el coseno es 0, lo que nos lleva al suelo estructural BETA
        truth_val = engine.apply_vpsi_truth(C=0.0) 
        
        assert pytest.approx(truth_val, rel=1e-5) == BETA_VPSI
        # El sistema sobrevive pero en su expresión mínima (Residuo)
