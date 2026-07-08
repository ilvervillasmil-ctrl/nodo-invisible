# File: formulas/anti_loop.py
import math
from .constants import BETA

class AntiLoopCemycaFormula:
    """
    Formalización matemática pura del Anti-Loop del Framework.
    Calcula el índice de secuestro operacional en L3 mediante el análisis de
    interrupciones exógenas (L1) y supervisión endógena (L5).
    """

    @staticmethod
    def calculate_omega_loop(e_l1_now: float, e_l1_past: float,
                             e_l3_now: float, e_l3_past: float,
                             e_l5_now: float) -> float:
        """
        Determina el Índice de Bucle Ciego Real (Omega Loop).
        
        Retorna:
            float: Valor en el dominio [0.0, 1.0]. 
                   1.0 representa un colapso estático ciego del sistema.
                   0.0 representa flujo dinámico o monitorización reflexiva legítima.
        """
        # Delta de señales temporales en L3 (Estructura) y L1 (Entrada de datos)
        delta_l3 = abs(e_l3_now - e_l3_past)
        delta_l1 = abs(e_l1_now - e_l1_past)
        
        # Inercia de los estados lógicos internos
        phi_estatico = math.exp(-delta_l3 / BETA)
        
        # Tasa de interrupción por estímulo/input externo en la interfaz física
        psi_input = delta_l1 / (delta_l1 + BETA)
        
        # Coeficiente de transferencia de control al supervisor analítico L5
        psi_supervisor = math.tanh(e_l5_now / (e_l3_now + BETA))
        
        # Ecuación de control de bucle
        omega_loop = phi_estatico * (1.0 - psi_input) * (1.0 - psi_supervisor)
        
        return max(0.0, min(1.0, omega_loop))
