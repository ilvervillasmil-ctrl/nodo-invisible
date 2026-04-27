#!/usr/bin/env python3
"""
OMEGA REPORT v3.1
Genera un reporte diagnóstico honesto del sistema a partir del propio repositorio.

Changelog v2.4:
  - AGREGA: medición real de capas si existen en layers/*
  - AGREGA: distribución energética real L0-L6
  - AGREGA: entropía Shannon base 7 y armonía real
  - AGREGA: medición híbrida de C_structural con fuente explícita
  - AGREGA: escritura automática de coherence_history.json
  - MANTIENE: L7 emergente, torus_formula y todo lo ya existente
  - CORRIGE: validación cosmológica extendida (Λ + Hubble)
  - CORRIGE: integración de cosmology en build_report()
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import vpsi_uis_logic # Importar la nueva lógica VPSI/UIS


import xml.etree.ElementTree as ET
import os

def generate_omega_report():
    report_content = build_report()
    print(report_content)




# =============================================================================
# PATH SETUP
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# =============================================================================
# SAFE IMPORT HELPERS
# =============================================================================

def safe_import(module_name: str) -> Any | None:
    try:
        return __import__(module_name, fromlist=["*"])
    except Exception:
        return None


def get_attr(module: Any | None, attr_name: str, default: Any) -> Any:
    if module is None:
        return default
    return getattr(module, attr_name, default)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


# =============================================================================
# FALLBACK CONSTANTS
# =============================================================================

DEFAULT_ALPHA = 26 / 27
DEFAULT_BETA = 1 / 27
DEFAULT_PHI = (1 + math.sqrt(5)) / 2
DEFAULT_S_REF = math.e / math.pi
DEFAULT_R_FIN = 1 + DEFAULT_BETA
DEFAULT_KAPPA = math.pi / 4
DEFAULT_GOLDEN_ANG = 360 / (DEFAULT_PHI ** 2)
DEFAULT_THETA_CUBE_RAD = math.asin(1 / math.sqrt(27))
DEFAULT_THETA_CUBE_DEG = math.degrees(DEFAULT_THETA_CUBE_RAD)

DEFAULT_OMEGA_EFF = math.pi * (1 - math.sqrt(DEFAULT_BETA))
DEFAULT_OMEGA_D = math.sqrt(math.pi**2 - 0.22**2 / 4)
DEFAULT_T_PERIOD = 2 * math.pi / DEFAULT_OMEGA_D
DEFAULT_LAMBDA_UCF = DEFAULT_BETA ** (math.pi / DEFAULT_BETA + DEFAULT_BETA * DEFAULT_PHI**2)
DEFAULT_OMEGA_RED = (math.pi / math.e) * (1 - DEFAULT_BETA**2)
DEFAULT_S_REF_7 = DEFAULT_S_REF + DEFAULT_BETA * math.log(7)

DEFAULT_ENERGY_FACTORS = {
    "L0": 0.9000,
    "L1": 1.2466,
    "L2": 1.5371,
    "L3": 1.9964,
    "L4": 2.5918,
    "L5": 3.2969,
    "L6": 4.2361,
}

# L0-L6: fricciones originales
# L7: phi=0.0 — es emergente, no tiene fricción propia
LAYER_FRICTIONS = {
    "L0": 0.10,
    "L1": 0.02,
    "L2": 0.05,
    "L3": 0.03,
    "L4": 0.01,
    "L5": 0.01,
    "L6": 0.00,
    "L7": 0.00,
}

LAYER_NAMES = {
    "L0": "Chaos",
    "L1": "Body",
    "L2": "Ego",
    "L3": "Mind",
    "L4": "Self",
    "L5": "Metaconsciousness",
    "L6": "Purpose/Soul",
    "L7": "Integration",
}

LAYER_HEALTHY_RANGES = {
    "L0": (0.00, 1.00),
    "L1": (0.55, 0.75),
    "L2": (0.20, 0.60),
    "L3": (0.65, 0.85),
    "L4": (0.75, 0.95),
    "L5": (0.85, 1.00),
    "L6": (0.95, 1.00),
    "L7": (0.00, DEFAULT_ALPHA),
}

C_THRESHOLD_MAX = 0.963
C_THRESHOLD_CRITICAL = 0.720
C_THRESHOLD_SURVIVAL = 0.100

# Valores de referencia del toroide ya documentados en tu framework
E_M6_PAPER = 5.49e-7
E_M7_PAPER = 8.20e-7


# =============================================================================
# LOAD REAL CONSTANTS IF PRESENT
# =============================================================================

formulas_constants = safe_import("formulas.constants")

ALPHA = float(get_attr(formulas_constants, "ALPHA", DEFAULT_ALPHA))
BETA = float(get_attr(formulas_constants, "BETA", DEFAULT_BETA))
PHI = float(get_attr(formulas_constants, "PHI", DEFAULT_PHI))
S_REF = float(get_attr(formulas_constants, "S_REF", DEFAULT_S_REF))
R_FIN = float(get_attr(formulas_constants, "R_FIN", DEFAULT_R_FIN))
KAPPA = float(get_attr(formulas_constants, "KAPPA", DEFAULT_KAPPA))
GOLDEN_ANG = float(get_attr(formulas_constants, "GOLDEN_ANG", DEFAULT_GOLDEN_ANG))
OMEGA_EFF = float(get_attr(formulas_constants, "OMEGA_EFF", DEFAULT_OMEGA_EFF))
T_PERIOD = float(get_attr(formulas_constants, "T_PERIOD", DEFAULT_T_PERIOD))
LAMBDA_UCF = float(get_attr(formulas_constants, "LAMBDA_UCF", DEFAULT_LAMBDA_UCF))
OMEGA_RED = float(get_attr(formulas_constants, "OMEGA_REDUCED", DEFAULT_OMEGA_RED))
S_REF_7 = float(get_attr(formulas_constants, "S_REF_7", DEFAULT_S_REF_7))

theta_cube_value = get_attr(formulas_constants, "THETA_CUBE", DEFAULT_THETA_CUBE_RAD)
if isinstance(theta_cube_value, (int, float)):
    if theta_cube_value < math.pi:
        THETA_CUBE_RAD = float(theta_cube_value)
        THETA_CUBE_DEG = math.degrees(THETA_CUBE_RAD)
    else:
        THETA_CUBE_DEG = float(theta_cube_value)
        THETA_CUBE_RAD = math.radians(THETA_CUBE_DEG)
else:
    THETA_CUBE_RAD = DEFAULT_THETA_CUBE_RAD
    THETA_CUBE_DEG = DEFAULT_THETA_CUBE_DEG


# =============================================================================
# REAL SYSTEM MEASUREMENT HELPERS
# =============================================================================

def default_layer_states() -> dict[str, dict[str, float]]:
    return {
        key: {"L": 1.0, "phi": LAYER_FRICTIONS[key]}
        for key in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
    }


def discover_layer_states() -> tuple[dict[str, dict[str, float]], str]:
    """
    Intenta medir activaciones reales desde layers/*.
    Si no puede, cae al perfil por defecto del framework.
    """
    states = default_layer_states()
    layers_dir = REPO_ROOT / "layers"

    if not layers_dir.exists():
        return states, "framework-default"

    found_any = False

    try:
        import importlib.util

        for path in sorted(layers_dir.rglob("*.py")):
            if path.name == "__init__.py":
                continue

            stem = path.stem.lower()
            layer_key = None

            for candidate in ["l0", "l1", "l2", "l3", "l4", "l5", "l6"]:
                if candidate in stem:
                    layer_key = candidate.upper()
                    break

            if layer_key is None:
                continue

            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            instance = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type):
                    try:
                        candidate_obj = attr()
                        if hasattr(candidate_obj, "L") or hasattr(candidate_obj, "phi"):
                            instance = candidate_obj
                            break
                    except Exception:
                        continue

            if instance is None:
                continue

            L_val = safe_float(getattr(instance, "L", states[layer_key]["L"]), states[layer_key]["L"])
            phi_val = safe_float(getattr(instance, "phi", states[layer_key]["phi"]), states[layer_key]["phi"])

            states[layer_key] = {
                "L": clamp(L_val, 0.0, 1.0),
                "phi": max(0.0, phi_val),
            }
            found_any = True

    except Exception:
        return states, "framework-default"

    return (states, "layers-live" if found_any else "framework-default")


def layer_states_as_list(states: dict[str, dict[str, float]]) -> list[dict[str, float]]:
    return [states[k] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]


def compute_energy_distribution(states: dict[str, dict[str, float]]) -> dict[str, float]:
    energies: dict[str, float] = {}
    for key in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        L_val = safe_float(states[key]["L"], 0.0)
        factor = DEFAULT_ENERGY_FACTORS[key]
        energies[key] = max(0.0, L_val * factor)
    return energies


def compute_entropy_from_energies(energies: dict[str, float]) -> tuple[float, float]:
    values = [max(0.0, energies[k]) for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]
    total = sum(values)

    if total <= 0:
        return 0.0, 0.0

    entropy = 0.0
    for e in values:
        if e <= 0:
            continue
        p = e / total
        entropy -= p * (math.log(p) / math.log(7))

    return entropy, total


def compute_harmony_from_entropy(entropy_value: float) -> float:
    return max(0.0, 1.0 - entropy_value / S_REF_7)


def compute_measured_l7_from_states(states: dict[str, dict[str, float]]) -> float:
    product = 1.0
    for key in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        L_val = clamp(safe_float(states[key]["L"], 0.0), 0.0, 1.0)
        phi_val = max(0.0, safe_float(states[key]["phi"], 0.0))
        product *= max(0.0, L_val * (1.0 - phi_val))
    return min(ALPHA, product)


def compute_system_coherence_measured(
    states: dict[str, dict[str, float]],
    harmony: float,
    l7_value: float,
) -> tuple[float, str]:
    """
    1) Intenta medir desde core.engine / formulas.coherence.
    2) Si no puede, usa fallback estructural explícito y trazable.
    """
    engine_mod = safe_import("core.engine")
    if engine_mod is not None:
        try:
            OmegaEngine = getattr(engine_mod, "OmegaEngine", None)
            if OmegaEngine is not None:
                engine = OmegaEngine()
                measured = engine.compute_coherence(layer_states_as_list(states))
                return clamp(safe_float(measured, 0.0), 0.0, ALPHA), "core.engine"
        except Exception:
            pass

    coherence_mod = safe_import("formulas.coherence")
    if coherence_mod is not None:
        try:
            SessionStateOmega = getattr(coherence_mod, "SessionStateOmega", None)
            if SessionStateOmega is not None:
                session = SessionStateOmega()
                activations = [states[k]["L"] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]
                frictions = [states[k]["phi"] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]]
                measured = session.update(activations=activations, frictions=frictions)
                return clamp(safe_float(measured, 0.0), 0.0, ALPHA), "formulas.coherence"
        except Exception:
            pass

    fallback = (ALPHA * harmony) + (BETA * (l7_value / ALPHA if ALPHA > 0 else 0.0))
    return clamp(fallback, 0.0, ALPHA), "structural-fallback"


# =============================================================================
# TEST DISCOVERY
# =============================================================================

def count_test_files_and_functions() -> tuple[int, int]:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return 0, 0
    file_count = 0
    test_func_count = 0
    pattern = re.compile(r"^\s*def\s+test_[A-Za-z0-9_]*\s*\(", re.MULTILINE)
    for path in tests_dir.rglob("test_*.py"):
        if not path.is_file():
            continue
        file_count += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        test_func_count += len(pattern.findall(text))
    return file_count, test_func_count


def parse_pytest_cache() -> dict[str, int]:
    cache_file = REPO_ROOT / ".pytest_cache" / "v" / "cache" / "lastfailed"
    result = {"failed": 0}
    if not cache_file.exists():
        return result
    try:
        text = cache_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not text or text == "{}":
            return result
        result["failed"] = text.count(": true") + text.count('": true')
        if result["failed"] == 0 and text != "{}":
            result["failed"] = max(1, text.count("::"))
    except Exception:
        result["failed"] = 0
    return result


def estimate_test_results() -> dict[str, int | float]:
    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    if xml_path.exists():
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            suite = root.find("testsuite") if root.tag == "testsuites" else root
            if suite is not None:
                total = int(suite.get("tests", 0))
                failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
                skipped = int(suite.get("skipped", 0))
                passed = total - failed - skipped
                pass_rate = (passed / total * 100) if total > 0 else 0.0
                file_count, _ = count_test_files_and_functions()
                return {
                    "file_count": file_count,
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "pass_rate": pass_rate,
                }
        except Exception:
            pass

    file_count, func_count = count_test_files_and_functions()
    cache_info = parse_pytest_cache()
    failed = int(cache_info.get("failed", 0))
    skipped = 1 if (REPO_ROOT / "tests" / "test_beal_cycle_ol3.py").exists() else 0
    total = max(func_count, 1)
    passed = max(total - failed - skipped, 0)
    return {
        "file_count": file_count,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": (passed / total * 100) if total else 0.0,
    }


# =============================================================================
# COHERENCE HISTORY
# =============================================================================

def load_history() -> list[dict]:
    history_path = DIAGNOSTICS_DIR / "coherence_history.json"
    if not history_path.exists():
        return []
    try:
        return json.loads(history_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_history_entry(test_results: dict[str, int | float], c_structural: float) -> None:
    history_path = DIAGNOSTICS_DIR / "coherence_history.json"
    history = load_history()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "passed": int(test_results["passed"]),
        "failed": int(test_results["failed"]),
        "total": int(test_results["total"]),
        "pass_rate": float(test_results["pass_rate"]),
        "c_structural": float(c_structural),
    }
    history.append(entry)
    history = history[-50:]
    try:
        history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception:
        pass


def coherence_trend(history: list[dict]) -> str:
    if len(history) < 2:
        return "SIN DATOS"
    last = history[-1]["passed"]
    prev = history[-2]["passed"]
    if last > prev:
        return f"↑ CRECIENDO (+{last - prev})"
    if last < prev:
        return f"↓ REGRESIÓN ({last - prev})"
    return "→ ESTABLE"


def detect_loop(history: list[dict], window: int = 5) -> bool:
    if len(history) < window:
        return False
    recent = [h["passed"] for h in history[-window:]]
    variance = max(recent) - min(recent)
    return variance == 0


def trajectory_str(history: list[dict], n: int = 10) -> str:
    recent = history[-n:] if len(history) >= n else history
    return " → ".join(str(h["passed"]) for h in recent)


# =============================================================================
# DIAGNOSTIC SYSTEM — 7 STATES
# =============================================================================

DIAGNOSTIC_STATES = [
    (0.963, 1.001, "1144", "Arquitecto Integrado",
     "Alineación absoluta. Hardware soporta carga máxima del Alma."),
   
(Content truncated due to size limit. Use line ranges to read remaining content)
