# tests/test_uis_prime_architecture.py

"""
TEST UIS-PRIME-ARCHITECTURE-001

Análisis estructural del retículo hexagonal y supervivencia modular.
Suite maestra para el Mapeo de Densidad y Resonancia.
"""

import numpy as np
import pytest
import sympy as sp

# ==========================================================
# PARÁMETROS UIS
# ==========================================================
MODULOS_UIS = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
VENTANA = 100000

# ==========================================================
# GENERADORES
# ==========================================================
def nodo_hexagonal(k):
    return 6 * k + 1

def nodo_espejo(k):
    return 6 * k - 1

def sobrevive_filtro(n, modulos):
    return all(n % m != 0 for m in modulos)

def generar_supervivientes(inicio, ventana, modulos):
    k0 = inicio // 6
    k1 = (inicio + ventana) // 6
    nodos = []
    for k in range(k0, k1):
        n = nodo_hexagonal(k)
        if sobrevive_filtro(n, modulos):
            nodos.append(n)
    return nodos

# ==========================================================
# SUITE MAESTRA DE TESTS
# ==========================================================

def test_densidad_supervivencia_uis():
    inicio = 10**12
    nodos = generar_supervivientes(inicio, VENTANA, MODULOS_UIS)
    densidad = len(nodos) / (VENTANA / 6)
    print(f"\n[UIS-DENSIDAD] Nodos vivos: {len(nodos)} | Densidad: {densidad}")
    assert len(nodos) > 0
    assert densidad > 0

def test_jerarquia_modular():
    inicio = 10**12
    densidades = []
    for i in range(1, len(MODULOS_UIS) + 1):
        nodos = generar_supervivientes(inicio, VENTANA, MODULOS_UIS[:i])
        d = len(nodos) / (VENTANA / 6)
        densidades.append(d)
    print(f"\n[UIS-JERARQUIA] Capas: {densidades}")
    for a, b in zip(densidades, densidades[1:]):
        assert b <= a

def test_estructura_gaps():
    nodos = generar_supervivientes(10**12, VENTANA, MODULOS_UIS)
    gaps = np.diff(nodos)
    media = np.mean(gaps)
    fft = np.abs(np.fft.fft(gaps))
    dominante = np.argmax(fft[1:]) + 1
    print(f"\n[UIS-GAPS] Media: {media} | Frecuencia dominante: {dominante}")
    assert media > 0
    assert len(gaps) > 0

def test_simetria_6k():
    limite = 100000
    positivos = sum(1 for k in range(2, limite) if sp.isprime(nodo_hexagonal(k)))
    negativos = sum(1 for k in range(2, limite) if sp.isprime(nodo_espejo(k)))
    diferencia = abs(positivos - negativos)
    print(f"\n[UIS-SIMETRIA] 6k+1: {positivos} | 6k-1: {negativos} | Dif: {diferencia}")
    assert positivos > 0
    assert negativos > 0

def test_supervivencia_vs_primos():
    inicio = 10**10
    candidatos = generar_supervivientes(inicio, 100000, MODULOS_UIS)
    primos = [n for n in candidatos if sp.isprime(n)]
    eficiencia = len(primos) / len(candidatos)
    print(f"\n[UIS-FILTRO] Eficiencia: {eficiencia}")
    assert len(candidatos) > 0

def test_invarianza_escala():
    escalas = [10**6, 10**8, 10**10, 10**12]
    resultados = []
    for x in escalas:
        nodos = generar_supervivientes(x, 100000, MODULOS_UIS)
        d = len(nodos) / (100000 / 6)
        resultados.append(d)
    print(f"\n[UIS-ESCALA] Resultados: {resultados}")
    assert all(r > 0 for r in resultados)
