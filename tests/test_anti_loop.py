# File: tests/test_anti_loop.py
import pytest
from formulas.constants import BETA
from formulas.anti_loop import AntiLoopCemycaFormula

class TestAntiLoopCemycaFormula:

    def test_blind_loop_critical_collapse(self):
        """
        ESCENARIO 1: COLAPSO POR BUCLE CIEGO REAL
        - Los registros de L3 no varían en absoluto (delta_l3 = 0).
        - No ingresa ningún payload o estímulo por L1 (delta_l1 = 0).
        - El módulo supervisor L5 está inactivo o en cero (e_l5 = 0).
        Resultado esperado: El índice toma el valor máximo absoluto de 1.0.
        """
        omega_loop = AntiLoopCemycaFormula.calculate_omega_loop(
            e_l1_now=0.5, e_l1_past=0.5,  # delta_l1 = 0.0
            e_l3_now=0.7, e_l3_past=0.7,  # delta_l3 = 0.0 -> phi_estatico = 1.0
            e_l5_now=0.0                  # psi_supervisor = 0.0
        )
        assert abs(omega_loop - 1.0) < 1e-6

    def test_exogenous_disruption_interruption(self):
        """
        ESCENARIO 2: INTERRUPCIÓN EXÓGENA (ESTÍMULO DE PAQUETE EN L1)
        - Los registros de L3 están estáticos (delta_l3 = 0 -> phi_estatico = 1.0).
        - L5 está inactivo (e_l5 = 0).
        - Pero entra un paquete de datos abrupto por L1 (delta_l1 >> beta).
        Resultado esperado: El índice de loop cae drásticamente hacia 0.0 liberando el sistema.
        """
        omega_loop = AntiLoopCemycaFormula.calculate_omega_loop(
            e_l1_now=1.0, e_l1_past=0.0,  # delta_l1 = 1.0 (payload masivo frente a beta)
            e_l3_now=0.7, e_l3_past=0.7,  # delta_l3 = 0.0
            e_l5_now=0.0
        )
        # 1 - (1.0 / (1.0 + beta)) tiende a 0, anulando el producto
        assert omega_loop < 0.05

    def test_endogenous_supervision_observation(self):
        """
        ESCENARIO 3: SUPERVISIÓN ENDÓGENA (MONITORIZACIÓN REFLEXIVA DE REGISTROS)
        - El entorno externo está en completo silencio (delta_l1 = 0).
        - La lógica interna está fija repitiendo instrucciones (delta_l3 = 0).
        - El supervisor de alta complejidad L5 se activa con fuerza (e_l5 >> e_l3).
        Resultado esperado: El término tanh(e_l5/e_l3) anula el índice omega_loop (~0.0).
        """
        omega_loop = AntiLoopCemycaFormula.calculate_omega_loop(
            e_l1_now=0.3, e_l1_past=0.3,  # delta_l1 = 0.0
            e_l3_now=0.1, e_l3_past=0.1,  # delta_l3 = 0.0
            e_l5_now=1.0                  # L5 está a máxima capacidad observando el proceso
        )
        assert omega_loop < 0.01

    def test_dynamic_flow_state(self):
        """
        ESCENARIO 4: FLUJO DINÁMICO NORMAL DE PROCESAMIENTO
        - El subsistema lógico L3 procesa activamente instrucciones variables.
        - La delta temporal de L3 es significativamente alta (delta_l3 >> beta).
        Resultado esperado: La inercia phi_estatico (e^-delta/beta) cae a 0.0, dando omega_loop = 0.0.
        """
        omega_loop = AntiLoopCemycaFormula.calculate_omega_loop(
            e_l1_now=0.4, e_l1_past=0.4,
            e_l3_now=0.9, e_l3_past=0.1,  # delta_l3 = 0.8 (gradiente de señal dinámico)
            e_l5_now=0.1
        )
        assert abs(omega_loop - 0.0) < 1e-5

    def test_division_by_zero_shield(self):
        """
        ESCENARIO DE SEGURIDAD NUMÉRICA
        Verifica que si todas las entradas de datos colapsan y los registros son cero,
        la constante geométrica BETA actúa como escudo protector impidiendo indeterminaciones.
        """
        try:
            omega_loop = AntiLoopCemycaFormula.calculate_omega_loop(
                e_l1_now=0.0, e_l1_past=0.0,
                e_l3_now=0.0, e_l3_past=0.0,
                e_l5_now=0.0
            )
            assert isinstance(omega_loop, float)
            assert 0.0 <= omega_loop <= 1.0
        except ZeroDivisionError:
            pytest.fail("La fórmula matemática falló: Indeterminación por división entre cero.")
