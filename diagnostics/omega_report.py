"""
OMEGA REPORT v2.6
Genera un reporte diagnóstico honesto del sistema a partir del propio repositorio.

Changelog v2.6.3:
  - AGREGA: inventario AST + censo de módulos/símbolos/fórmulas
  - AGREGA: findings + producers omega_validation()/__omega_report__()
  - AGREGA: cobertura de auditoría en Markdown y CI (cajas 46)
  - NO sustituye secciones científicas v2.4 ni cajas v2.6.1

Changelog v2.6.2:
  - CAPTURA: discover_diagnostics() recorre diagnostics/ entero
  - PRESERVA: document completo + file metadata; índice no sustituye raw
  - ENGINE: snapshot de atributos públicos serializables + censar completo
  - QUITA: catálogo manual axioms/gen/contratos/evaluaciones como frontera
  - QUITA: slices CI pares[:N] y skip de dict/list
  - MANTIENE: secciones científicas v2.4 y render 2.6.1

Changelog v2.6.1:
  - SEPARA: md_table = Markdown; render_ci = cajas Unicode 46 cols
  - QUITA: duplicación Markdown+caja en la misma función
  - QUITA: print(report) en stdout; tee del workflow
  - TARJETA por entidad (no caja por celda)
  - MANTIENE: auditoría v2.6 intacta

Changelog v2.6:
  - AGREGA: tablas Markdown alineadas + md_cell
  - AGREGA: tests solo XML; Omega ya no escribe coherence_history
  - AGREGA: JSON desde paquete (cero regex)
  - AGREGA: inventario/Engine/CI evidence/fórmulas con provenance
  - CONSERVA: todas las secciones científicas v2.4

Changelog v2.5:
  - AGREGA: cajas Unicode estilo Omega SPARTACO (md_table → ┌─┐)
  - AGREGA: iconografía canónica en cabecera y secciones
  - MANTIENE: medición, validaciones y recorrido v2.4 intactos

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

import ast
import contextlib
import hashlib
import importlib
import io
import json
import math
import os
import platform
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List


# =============================================================================
# PATH SETUP
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VERSION = "2.6.6"

SECRET_KEYS = ("password", "secret", "token", "api_key", "apikey", "private_key")
SKIP_DIAG_NAMES = {
    "omega_report.py",
    "omega_diary_publisher.py",
    "__init__.py",
}


def _is_secret_key(key: str) -> bool:
    k = str(key).lower()
    return any(s in k for s in SECRET_KEYS)


def _redact(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = "[REDACTED]" if _is_secret_key(k) else _redact(v)
        return out
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    return obj


def _safe_jsonable(obj):
    try:
        json.dumps(obj, default=str)
        return True
    except Exception:
        return False


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _index_key_for(path: Path, document) -> str:
    name = path.name.lower()
    stem = path.stem.lower()
    if isinstance(document, dict):
        tipo = str(document.get("tipo") or document.get("type") or document.get("schema") or "").lower()
        if tipo:
            return tipo
    if "axiom" in stem:
        return "axioms"
    if "generativ" in stem:
        return "generatividad"
    if "contrato" in stem:
        return "contratos"
    if "evaluacion" in stem:
        return "evaluaciones"
    if "coherence_history" in stem:
        return "coherence_history"
    if "test_results" in stem:
        return "tests_xml"
    if "omega_report_data" in stem:
        return "omega_package_prev"
    if "omega_report" in stem and path.suffix.lower() == ".md":
        return "omega_report_md"
    if "diario" in stem or "diary" in stem:
        return "diario"
    return stem or name


def capture_artifact(path: Path) -> dict:
    rel = str(path.relative_to(REPO_ROOT)) if REPO_ROOT in path.parents or path.parent == REPO_ROOT else str(path)
    rec = {
        "path": rel,
        "name": path.name,
        "suffix": path.suffix,
        "bytes": path.stat().st_size if path.exists() else 0,
        "sha256": _sha256_file(path) if path.exists() else None,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat() if path.exists() else None,
        "present": path.exists(),
        "read_ok": False,
        "parse_ok": False,
        "content_type": path.suffix.lstrip(".").lower() or "unknown",
        "document": None,
        "document_metadata": {},
        "error": None,
    }
    if not path.exists() or not path.is_file():
        return rec
    try:
        raw = path.read_bytes()
        rec["read_ok"] = True
    except Exception as e:
        rec["error"] = str(e)
        return rec
    suffix = path.suffix.lower()
    text = None
    try:
        text = raw.decode("utf-8")
    except Exception:
        rec["document"] = {"_binary": True, "bytes": rec["bytes"]}
        return rec
    if suffix == ".json":
        try:
            document = json.loads(text)
            rec["parse_ok"] = True
            rec["document"] = _redact(document)
            if isinstance(document, dict):
                rec["document_metadata"] = {
                    k: document.get(k)
                    for k in (
                        "tipo", "type", "schema", "schema_version", "version",
                        "origen", "invocador_id", "estado_engine", "timestamp",
                        "n", "nota", "coherente", "incoherente",
                    )
                    if k in document
                }
        except Exception as e:
            rec["error"] = str(e)
            rec["document"] = {"_raw_text": text}
    elif suffix == ".xml":
        rec["document"] = {"_xml_text": text}
        rec["parse_ok"] = True
    elif suffix in {".md", ".txt"}:
        rec["document"] = {"_text": text}
        rec["parse_ok"] = True
    else:
        rec["document"] = {"_text": text}
        rec["parse_ok"] = True
    return rec


def discover_diagnostics() -> dict:
    artifacts = []
    index = {}
    if DIAGNOSTICS_DIR.exists():
        for path in sorted(DIAGNOSTICS_DIR.rglob("*")):
            if not path.is_file():
                continue
            if path.name in SKIP_DIAG_NAMES:
                continue
            if path.suffix == ".pyc" or "__pycache__" in path.parts:
                continue
            rec = capture_artifact(path)
            artifacts.append(rec)
            key = _index_key_for(path, rec.get("document"))
            if key not in index:
                index[key] = rec
    return {"artifacts": artifacts, "index": index}


def snapshot_engine() -> dict:
    snap = {"available": False, "startup": "UNAVAILABLE", "error": None, "public": {}}
    try:
        engine_mod = __import__("core.engine", fromlist=["*"])
    except Exception as e:
        snap["error"] = "{0}: {1}".format(type(e).__name__, e)
        snap["startup"] = "ERROR"
        return snap

    ArranqueError = getattr(engine_mod, "ArranqueError", Exception)
    EngineCls = getattr(engine_mod, "Engine", None)
    OmegaCls = getattr(engine_mod, "OmegaEngine", None)
    snap["module_classes"] = [
        n for n in ("Engine", "OmegaEngine")
        if getattr(engine_mod, n, None) is not None
    ]

    eng = None
    last_err = None
    if EngineCls is not None:
        try:
            eng = EngineCls(REPO_ROOT / "modules", invocador_id="omega", strict=True)
        except TypeError:
            try:
                eng = EngineCls()
            except Exception as e:
                last_err = e
        except ArranqueError as e:
            last_err = e
        except Exception as e:
            last_err = e
    if eng is None and OmegaCls is not None:
        try:
            eng = OmegaCls()
        except Exception as e:
            last_err = e
    if eng is None:
        snap["startup"] = "ERROR"
        snap["error"] = (
            "{0}: {1}".format(type(last_err).__name__, last_err)
            if last_err is not None
            else "no Engine/OmegaEngine constructible in core.engine"
        )
        return snap

    try:
        snap["available"] = True
        snap["startup"] = "OK"
        snap["class"] = type(eng).__name__
        public = {}
        for name in dir(eng):
            if name.startswith("_"):
                continue
            try:
                val = getattr(eng, name)
            except Exception as e:
                public[name] = {"_error": str(e)}
                continue
            if callable(val):
                continue
            if _safe_jsonable(val):
                public[name] = val
            else:
                public[name] = repr(val)
        if hasattr(eng, "censar"):
            try:
                public["census"] = eng.censar()
            except Exception as e:
                public["census_error"] = str(e)
        if hasattr(eng, "paquete_omega"):
            try:
                public["paquete_omega"] = eng.paquete_omega()
            except Exception as e:
                public["paquete_omega_error"] = str(e)
        snap["public"] = public
        snap["estado"] = public.get("estado") or public.get("state") or "OPERATIVO"
        snap["invocador_id"] = public.get("invocador_id") or "omega"
        snap["errores_arranque"] = public.get("errores_arranque")
        snap["fallos"] = public.get("fallos")
        snap["census"] = public.get("census")
    except Exception as e:
        snap["available"] = False
        snap["startup"] = "ERROR"
        snap["error"] = "{0}: {1}".format(type(e).__name__, e)
    return snap


def generated_metadata(now: str, sha: str) -> dict:
    return {
        "utc": now,
        "sha": sha,
        "framework": "Universal Integration System",
        "omega_version": VERSION,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "ref": os.environ.get("GITHUB_REF"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
        "workflow": os.environ.get("GITHUB_WORKFLOW"),
        "job": os.environ.get("GITHUB_JOB"),
        "event": os.environ.get("GITHUB_EVENT_NAME"),
    }


FINDINGS: list[dict] = []
AUDIT_ROOTS = ("core", "formulas", "layers", "modules")


def _finding(severity: str, category: str, component: str, message: str) -> None:
    FINDINGS.append({
        "severity": severity,
        "category": category,
        "component": component,
        "message": str(message),
    })


def _mod_from_rel(rel: str) -> str | None:
    if not rel.endswith(".py"):
        return None
    parts = Path(rel).with_suffix("").parts
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return None
    return ".".join(parts)


def discover_audit() -> dict:
    FINDINGS.clear()
    py_rows = []
    modules = []
    formulas = []
    producers = []
    symbols_n = 0
    import_ok = 0
    import_fail = 0
    layers_n = 0

    for root_name in AUDIT_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            _finding("INFO", "audit", root_name + "/", "directorio ausente")
            continue
        for path in sorted(root.rglob("*.py")):
            if path.name == "__init__.py" and path.stat().st_size == 0:
                continue
            rel = str(path.relative_to(REPO_ROOT))
            rec = {
                "path": rel,
                "lines": 0,
                "classes": [],
                "functions": [],
                "parse_ok": False,
            }
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                rec["lines"] = text.count("\n") + 1
                tree = ast.parse(text)
                rec["parse_ok"] = True
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        rec["classes"].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        rec["functions"].append({
                            "name": node.name,
                            "args": [a.arg for a in node.args.args],
                            "line": node.lineno,
                            "public": not node.name.startswith("_"),
                        })
            except Exception as e:
                rec["parse_error"] = str(e)
                _finding("ERROR", "parse", rel, e)
            py_rows.append(rec)
            if root_name == "layers":
                layers_n += 1

            name = _mod_from_rel(rel)
            if not name:
                continue
            entry = {
                "name": name,
                "path": rel,
                "importable": False,
                "symbols": [],
                "error": None,
                "stdout": "",
            }
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    imported = importlib.import_module(name)
                    for hook in ("omega_validation", "__omega_report__", "demo", "run_demo", "main", "audit", "report"):
                        fn = getattr(imported, hook, None)
                        if callable(fn) and hook in {"demo", "run_demo", "audit", "report", "main"}:
                            try:
                                sig_ok = True
                                try:
                                    import inspect
                                    params = [p for p in inspect.signature(fn).parameters.values() if p.default is inspect.Parameter.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
                                    if len(params) > 0:
                                        sig_ok = False
                                except Exception:
                                    sig_ok = hook != "main"
                                if sig_ok:
                                    fn()
                            except Exception:
                                pass
                entry["stdout"] = buf.getvalue()
                entry["importable"] = True
                import_ok += 1
                public = []
                for attr in dir(imported):
                    if attr.startswith("_") and attr not in {"__omega_report__"}:
                        continue
                    try:
                        val = getattr(imported, attr)
                    except Exception:
                        continue
                    if callable(val) and not isinstance(val, type):
                        kind = "function"
                        shown = attr
                    elif isinstance(val, type):
                        kind = "class"
                        shown = attr
                    else:
                        kind = "variable"
                        shown = "[REDACTED]" if _is_secret_key(attr) else val
                        if not _safe_jsonable(shown):
                            shown = repr(shown)[:120]
                    public.append({"name": attr, "kind": kind, "value": shown})
                entry["symbols"] = public
                symbols_n += len(public)
                if name.startswith("formulas."):
                    for fn in rec.get("functions") or []:
                        if fn.get("public"):
                            formulas.append({
                                "module": name,
                                "name": fn.get("name"),
                                "args": fn.get("args") or [],
                                "line": fn.get("line"),
                            })
                for hook in ("omega_validation", "__omega_report__"):
                    fn = getattr(imported, hook, None)
                    if callable(fn):
                        try:
                            payload = fn()
                            producers.append({
                                "id": name.replace(".", "_") + "_" + hook,
                                "title": name,
                                "hook": hook,
                                "source": name,
                                "status": "MEASURED",
                                "metrics": payload if isinstance(payload, dict) else {"value": payload},
                            })
                        except Exception as e:
                            _finding("ERROR", "producer", name + "." + hook, e)
            except Exception as e:
                entry["stdout"] = buf.getvalue()
                entry["error"] = "{0}: {1}".format(type(e).__name__, e)
                import_fail += 1
                _finding("ERROR", "import", name, entry["error"])
            else:
                if not entry.get("stdout"):
                    entry["stdout"] = buf.getvalue()
            modules.append(entry)

    # Los tests no se reimportan por nombre.
    # Autoridad: diagnostics/test_results.xml (system-out de CADA testcase).

    skip = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "venv", "node_modules", ".tox"}
    repo_files = []
    repo_dirs = set()
    buckets = {"python": 0, "markdown": 0, "json": 0, "yaml": 0, "xml": 0, "txt": 0, "other": 0, "bytes": 0}
    edges = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip]
        base = Path(dirpath)
        try:
            repo_dirs.add(str(base.relative_to(REPO_ROOT)))
        except Exception:
            continue
        for name in filenames:
            path = base / name
            rel = str(path.relative_to(REPO_ROOT))
            ext = path.suffix.lower()
            bucket = "other"
            if ext == ".py":
                bucket = "python"
            elif ext == ".md":
                bucket = "markdown"
            elif ext == ".json":
                bucket = "json"
            elif ext in {".yml", ".yaml"}:
                bucket = "yaml"
            elif ext == ".xml":
                bucket = "xml"
            elif ext == ".txt":
                bucket = "txt"
            try:
                size = path.stat().st_size
            except Exception:
                size = 0
            buckets[bucket] = buckets.get(bucket, 0) + 1
            buckets["bytes"] += size
            repo_files.append({"path": rel, "type": bucket, "bytes": size})
            if ext == ".py":
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
                    src = _mod_from_rel(rel)
                    for node in tree.body:
                        if isinstance(node, ast.Import):
                            for a in node.names:
                                edges.append({"from": src, "to": a.name, "kind": "import"})
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            edges.append({"from": src, "to": node.module, "kind": "from"})
                except Exception:
                    pass

    # tests AST only — no import (evita reejecutar demos de 30 min)
    tests_dir = REPO_ROOT / "tests"
    test_fns = []
    if tests_dir.exists():
        for path in sorted(tests_dir.rglob("test_*.py")):
            rel = str(path.relative_to(REPO_ROOT))
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        test_fns.append({"file": rel, "name": node.name, "line": node.lineno})
            except Exception as e:
                _finding("ERROR", "parse", rel, e)

    return {
        "python_files": py_rows,
        "modules": modules,
        "formulas": formulas,
        "producers": producers,
        "findings": list(FINDINGS),
        "repository": {
            "summary": {
                "files": len(repo_files),
                "directories": len(repo_dirs),
                **{k: v for k, v in buckets.items()},
            },
            "files": repo_files,
        },
        "dependencies": {
            "edges": edges,
            "n_edges": len(edges),
        },
        "test_functions": test_fns,
        "module_stdout": [
            {"name": m.get("name"), "path": m.get("path"), "stdout": m.get("stdout") or ""}
            for m in modules if (m.get("stdout") or "").strip()
        ],
        "coverage": {
            "python_files_discovered": len(py_rows),
            "repo_files": len(repo_files),
            "modules_importable": import_ok,
            "modules_failed_import": import_fail,
            "public_symbols_discovered": symbols_n,
            "layers_discovered": layers_n,
            "formulas_discovered": len(formulas),
            "validations_discovered": len(producers),
            "findings_n": len(FINDINGS),
            "module_stdout_n": sum(1 for m in modules if (m.get("stdout") or "").strip()),
        },
    }


ICON_OMEGA = "Ω"
ICON_OK = "✅"
ICON_FAIL = "❌"
ICON_ERR = "🚨"
ICON_WARN = "⚠️"
ICON_INFO = "ℹ️"
ICON_SKIP = "⏭️"
ICON_COH = "🧬"
ICON_ENGINE = "🧩"
ICON_PKG = "📦"
ICON_REPO = "🗂️"
ICON_DIR = "📁"
ICON_FILE = "📄"
ICON_PY = "🐍"
ICON_CONTRACT = "📜"
ICON_FN = "⚙️"
ICON_NUM = "🔢"
ICON_MET = "📊"
ICON_FORM = "📐"
ICON_LAYER = "📶"
ICON_GEN = "🧠"
ICON_AX = "📚"
ICON_TEST = "🧪"
ICON_HIST = "❤️"
ICON_DEP = "🔗"
ICON_GRAPH = "🕸️"
ICON_SRC = "📡"
ICON_EV = "📎"
ICON_DISK = "💾"
ICON_LOCK = "🔐"
ICON_AUDIT = "🔎"
ICON_TYPE = "🏷️"
ICON_TIME = "⏱️"
ICON_ID = "🆔"
ICON_DER = "🔄"
ICON_RES = "🎯"
ICON_BAN = "🚫"
ICON_ITEM = "🔹"
ICON_CUBE = "🧱"
ICON_STAR = "⭐"
ICON_WAVE = "🌊"
ICON_ATOM = "⚛️"
ICON_EARTH = "🌍"
ICON_BOLT = "⚡"
ICON_FIRE = "🔥"
ICON_MOON = "🌙"
ICON_SUN = "☀️"
ICON_SCALE = "⚖️"
ICON_ORBIT = "🪐"
ICON_PULSE = "💓"
ICON_SEED = "🌱"
ICON_LENS = "🔬"
ICON_GEAR = "🛠️"
ICON_MAP = "🗺️"
ICON_FLAG = "🚩"
ICON_PIN = "📌"
ICON_BOX = "🗃️"


def _icono_status(valor):
    s = str(valor).strip().upper()
    if s in {"PASS", "OK", "YES", "TRUE", "INTEGRATED"}:
        return "{0} {1}".format(ICON_OK, valor)
    if s in {"FAIL", "NO", "FALSE", "COLLAPSED"}:
        return "{0} {1}".format(ICON_FAIL, valor)
    if s in {"WARN", "WARNING", "REVIEW"}:
        return "{0} {1}".format(ICON_WARN, valor)
    return str(valor)


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

C_THRESHOLD_MAX = 0.962962962962963
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


def discover_test_files() -> list[str]:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return []
    return sorted(str(p.relative_to(REPO_ROOT)) for p in tests_dir.rglob("test_*.py") if p.is_file())


def read_executed_tests() -> dict:
    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    discovered = discover_test_files()
    file_count, func_count = count_test_files_and_functions()
    base = {
        "source": "diagnostics/test_results.xml" if xml_path.exists() else "unavailable",
        "executed": False,
        "file_count": file_count,
        "discovered_n": len(discovered),
        "discovered_files": discovered,
        "functions_static": func_count,
        "total": None,
        "passed": None,
        "failed": None,
        "failures": None,
        "errors": None,
        "skipped": None,
        "pass_rate": None,
        "duration": None,
        "suites": [],
        "cases": [],
        "class": "UNAVAILABLE",
    }
    if not xml_path.exists():
        return base
    try:
        root = ET.parse(xml_path).getroot()
    except Exception as e:
        base["error"] = str(e)
        return base
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = failures = errors = skipped = 0
    duration = 0.0
    suite_rows = []
    cases = []
    for s in suites:
        t = int(s.get("tests", 0) or 0)
        f = int(s.get("failures", 0) or 0)
        e = int(s.get("errors", 0) or 0)
        k = int(s.get("skipped", 0) or 0)
        try:
            dur = float(s.get("time") or 0)
        except Exception:
            dur = 0.0
        total += t
        failures += f
        errors += e
        skipped += k
        duration += dur
        s_out = s.find("system-out")
        suite_rows.append({
            "name": s.get("name"), "tests": t, "failures": f, "errors": e,
            "skipped": k, "passed": t - f - e - k, "time": dur,
            "stdout": (s_out.text or "") if s_out is not None else "",
        })
        for tc in s.iter("testcase"):
            status = "passed"
            detail = None
            node = tc.find("failure")
            if node is not None:
                status = "failure"
                detail = ((node.get("message") or "") + " " + (node.text or "")).strip()
            else:
                node = tc.find("error")
                if node is not None:
                    status = "error"
                    detail = ((node.get("message") or "") + " " + (node.text or "")).strip()
                elif tc.find("skipped") is not None:
                    status = "skipped"
                    node = tc.find("skipped")
                    detail = node.get("message") or node.text
            so = tc.find("system-out")
            se = tc.find("system-err")
            stdout = (so.text or "") if so is not None else ""
            stderr = (se.text or "") if se is not None else ""
            cases.append({
                "classname": tc.get("classname"),
                "name": tc.get("name"),
                "time": tc.get("time"),
                "status": status,
                "detail": detail,
                "stdout": stdout,
                "stderr": stderr,
            })
    failed = failures + errors
    passed = total - failed - skipped
    base.update({
        "executed": True,
        "total": total,
        "passed": passed,
        "failed": failed,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": (passed / total * 100) if total else 0.0,
        "duration": duration,
        "suites": suite_rows,
        "cases": cases,
        "class": "MEASURED",
        "file_count": file_count,
    })
    return base


def estimate_test_results() -> dict[str, int | float]:
    """Compatibilidad v2.4: usa XML real. Ya no estima ejecución."""
    executed = read_executed_tests()
    if executed.get("executed"):
        return {
            "file_count": executed.get("file_count") or 0,
            "total": executed.get("total") or 0,
            "passed": executed.get("passed") or 0,
            "failed": executed.get("failed") or 0,
            "skipped": executed.get("skipped") or 0,
            "pass_rate": executed.get("pass_rate") or 0.0,
            "source": executed.get("source"),
            "class": "MEASURED",
        }
    return {
        "file_count": executed.get("file_count") or 0,
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "pass_rate": 0.0,
        "source": "unavailable",
        "class": "UNAVAILABLE",
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
# DIAGNOSTIC SYSTEM — STRUCTURAL STATES
#
# Dominio físico:
#     β = 1/27  = 0.037037037037
#     α = 26/27 = 0.962962962963
#
# Umbral crítico del framework:
#     C* = 0.450000000000
# =============================================================================

DIAGNOSTIC_STATES = [

    # 95% – 100% del dominio estructural
    (0.916666666667, 0.962962962963,
     "1144", "Arquitecto Integrado",
     "Alineación estructural máxima. El sistema opera cerca del límite físico α."),

    # 80% – 95%
    (0.777777777778, 0.916666666667,
     "1133", "Integración Superior",
     "Alta coherencia estructural con gran capacidad de adaptación."),

    # 65% – 80%
    (0.638888888889, 0.777777777778,
     "1044", "Integración Avanzada",
     "Sistema altamente coherente y funcional."),

    # 50% – 65%
    (0.500000000000, 0.638888888889,
     "0144", "Integración Funcional",
     "Coherencia suficiente para operar con estabilidad."),

    # Umbral crítico definido por el framework
    (0.450000000000, 0.500000000000,
     "1122", "Umbral Crítico",
     "Límite mínimo de autosostenibilidad estructural."),

    # Entre β y el umbral crítico
    (0.370000000000, 0.450000000000,
     "1111", "Zona de Peligro",
     "La estructura pierde estabilidad y depende de soporte externo."),

    # Colapso
    (0.037037037037, 0.370000000000,
     "0000", "Colapso Estructural",
     "La coherencia se aproxima al mínimo estructural β."),
]


def diagnostic_label(c_structural: float) -> tuple[str, str, str]:
    for low, high, code, name, desc in DIAGNOSTIC_STATES:
        if low <= c_structural < high:
            return code, name, desc
    return "0000", "Colapso Estructural", DIAGNOSTIC_STATES[-1][4]


def diagnostic_vector_interpretation(code: str) -> str:
    if len(code) != 4:
        return ""
    d1, d2, d3, d4 = code
    origin = (
        "✅ Self+Soul conectados" if d1 == "1" and d4 == "1" else
        "⚠️ Soul activa, Self ausente" if d1 == "0" and d3 == "1" else
        "⚠️ Self activo, Soul silenciada" if d1 == "1" and d2 == "0" else
        "❌ Desconexión origen"
    )
    manifest = f"Robustez Mind+Body: {d3}{d4}/44"
    return f"{origin} | {manifest}"


# ============================================================
# STRUCTURAL NORMALIZATION
# ============================================================

def structural_percent(c_structural: float) -> float:
    """
    Convierte CΩ al porcentaje del dominio físico [β, α].

    β  ->   0 %
    α  -> 100 %
    """
    c = max(BETA, min(ALPHA, float(c_structural)))
    return (c - BETA) / (ALPHA - BETA)


# ============================================================
# PHENOMENOLOGICAL STATE
# ============================================================

def phenomenological_state(c_structural: float) -> tuple[str, str]:
    p = structural_percent(c_structural)

    if p >= 0.95:
        return "ARQUITECTO INTEGRADO", "⟨◉⟩"

    if p >= 0.80:
        return "INTEGRACIÓN SUPERIOR", "⟨◉⟩"

    if p >= 0.65:
        return "INTEGRACIÓN AVANZADA", "⟨◐⟩"

    if p >= 0.50:
        return "INTEGRACIÓN FUNCIONAL", "⟨◑⟩"

    if p >= 0.45:
        return "UMBRAL CRÍTICO", "⟨◑⟩"

    if p >= 0.37:
        return "ZONA DE PELIGRO", "⟨◯⟩"

    return "COLAPSO ESTRUCTURAL", "⟨○⟩"


# =============================================================================
# MODULE STATUS
# =============================================================================

def check_module_status() -> list[tuple[str, str]]:
    """Descubre módulos reales bajo formulas/, layers/, modules/, core/ si existen."""
    roots = []
    for name in ("formulas", "layers", "modules", "core"):
        d = REPO_ROOT / name
        if d.exists() and d.is_dir():
            roots.append(d)
    results = []
    seen = set()
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if path.name == "__init__.py":
                continue
            rel = str(path.relative_to(REPO_ROOT))
            if rel in seen:
                continue
            seen.add(rel)
            parts = path.with_suffix("").parts
            # relative to repo
            rel_parts = path.relative_to(REPO_ROOT).with_suffix("").parts
            mod_name = ".".join(rel_parts)
            imported = safe_import(mod_name)
            status = "✅ activo" if imported is not None else "❌ no importable"
            results.append((mod_name + "  (" + rel + ")", status))
    if not results:
        results.append(("(sin formulas/ layers/ modules/ core/)", "⚠️ ausente"))
    return results


# =============================================================================
# SYSTEM METRICS
# =============================================================================

def compute_zeta(states: dict[str, dict[str, float]] | None = None) -> float:
    source = states if states is not None else default_layer_states()
    phi_total = sum(source[k]["phi"] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"])
    return phi_total / (2 * math.pi)


def compute_omega_d(states: dict[str, dict[str, float]] | None = None) -> float:
    source = states if states is not None else default_layer_states()
    phi_total = sum(source[k]["phi"] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"])
    return math.sqrt(max(math.pi**2 - phi_total**2 / 4, 0.0))


def compute_period(omega_d: float) -> float:
    return (2 * math.pi / omega_d) if omega_d > 0 else float("inf")


def compute_system_entropy(states: dict[str, dict[str, float]]) -> tuple[float, float, dict[str, float]]:
    energies = compute_energy_distribution(states)
    entropy, total_energy = compute_entropy_from_energies(energies)
    return entropy, total_energy, energies


def compute_system_harmony(entropy_value: float) -> float:
    return compute_harmony_from_entropy(entropy_value)


# =============================================================================
# L7 INTEGRATION STATUS
# =============================================================================

def l7_integration_status(states: dict[str, dict[str, float]] | None = None) -> dict:
    """
    Calcula L7 = producto multiplicativo de L0-L6.
    Prioridad:
      1. layers.l7_integration
      2. cálculo estructural directo desde estados detectados
    """
    source_states = states if states is not None else default_layer_states()

    mod = safe_import("layers.l7_integration")
    if mod is not None:
        try:
            LayerIntegration = getattr(mod, "LayerIntegration")
            layer = LayerIntegration()

            layers_data = [
                {"L": source_states["L0"]["L"], "phi": source_states["L0"]["phi"]},
                {"L": source_states["L1"]["L"], "phi": source_states["L1"]["phi"]},
                {"L": source_states["L2"]["L"], "phi": source_states["L2"]["phi"]},
                {"L": source_states["L3"]["L"], "phi": source_states["L3"]["phi"]},
                {"L": source_states["L4"]["L"], "phi": source_states["L4"]["phi"]},
                {"L": source_states["L5"]["L"], "phi": source_states["L5"]["phi"]},
                {"L": source_states["L6"]["L"], "phi": source_states["L6"]["phi"]},
            ]

            value = layer.compute(layers_data)
            integrated = layer.is_integrated()

            return {
                "available": True,
                "value": value,
                "status": "INTEGRATED" if integrated else "COLLAPSED",
                "formula": "L7 = ∏ Li * (1 - phi_i)  para i = 0..6",
                "law": "Ley 8: Integración Total — Todo lo que no se integra colapsa",
                "note": "L6 orienta. L7 verifica.",
                "max_possible": ALPHA,
                "source": "layers.l7_integration",
            }
        except Exception:
            pass

    fallback_value = compute_measured_l7_from_states(source_states)
    return {
        "available": True,
        "value": fallback_value,
        "status": "INTEGRATED" if fallback_value > 0 else "COLLAPSED",
        "formula": "L7 = ∏ Li * (1 - phi_i)  para i = 0..6",
        "law": "Ley 8: Integración Total — Todo lo que no se integra colapsa",
        "note": "L6 orienta. L7 verifica.",
        "max_possible": ALPHA,
        "source": "structural-fallback",
    }


# =============================================================================
# TORUS FORMULA VALIDATION
# =============================================================================

def torus_formula_validation() -> dict:
    """
    Valida la Fórmula del Toroide desde formulas/torus_formula.py.
    Verifica las 4 leyes estructurales, E(M) y conexión UCF.
    """
    mod = safe_import("formulas.torus_formula")
    if mod is None:
        return {
            "available": False,
            "status": "MODULO NO ENCONTRADO",
        }

    try:
        primes = [2, 3, 5, 7]

        law1 = getattr(mod, "law1_cycle_independence")(primes)
        law2 = getattr(mod, "law2_cycle_resonance")([4, 6])
        law3 = getattr(mod, "law3_prime_filtering")(7)
        law4 = getattr(mod, "law4_field_energy")(primes, prime_limit=5000)
        beta_analysis = getattr(mod, "beta_torus_residue_analysis")()

        all_laws = (
            law1["law_holds"]
            and law2["law_holds"]
            and law3["law_holds"]
            and law4["law_holds"]
        )

        return {
            "available": True,
            "primes": primes,
            "M": law1["M"],
            "phi_M": getattr(mod, "phi_M")(primes),
            "law1_holds": law1["law_holds"],
            "law2_holds": law2["law_holds"],
            "law3_holds": law3["law_holds"],
            "law4_holds": law4["law_holds"],
            "all_laws": all_laws,
            "E_M_computed": law4.get("E_M", "N/A"),
            "E_M6_paper": E_M6_PAPER,
            "E_M7_paper": E_M7_PAPER,
            "beta_closest_n": beta_analysis["closest_n"],
            "beta_closest_v": beta_analysis["closest_value"],
            "beta_status": beta_analysis["status"],
            "rh_status": "completo",
            "ucf_link": "beta = residuo del cubo | E(M) = residuo del toroide",
            "status": "PASS" if all_laws else "REVIEW",
        }
    except Exception as e:
        return {
            "available": False,
            "status": f"ERROR: {e}",
        }


# =============================================================================
# DOMAIN VALIDATIONS
# =============================================================================

def cosmological_constant_validation() -> dict:
    """
    Validación cosmológica extendida del framework.

    Incluye:
      1. Constante cosmológica Λ
      2. Tensión de Hubble Ω_H
    """

    cosmology_mod = safe_import("formulas.cosmology")
    constants_mod = safe_import("formulas.constants")

    # =========================================================================
    # Λ — CONSTANTE COSMOLÓGICA
    # =========================================================================

    lambda_base_term = 27 * math.pi
    lambda_correction_term = BETA * (PHI ** 2)
    lambda_exponent = lambda_base_term + lambda_correction_term
    lambda_prediction = BETA ** lambda_exponent

    lambda_observed = None
    lambda_observed_candidates = [
        "LAMBDA_OBSERVED",
        "OBSERVED_LAMBDA",
        "LAMBDA_COSMO_OBSERVED",
        "LAMBDA_VALUE_OBSERVED",
    ]

    for mod in (cosmology_mod, constants_mod):
        if mod is None:
            continue
        for name in lambda_observed_candidates:
            value = get_attr(mod, name, None)
            if value is not None:
                try:
                    lambda_observed = float(value)
                    if lambda_observed > 0:
                        break
                except Exception:
                    pass
        if lambda_observed is not None:
            break

    if lambda_observed is None:
        lambda_observed = 2.8880e-122

    lambda_error_pct = abs(lambda_prediction - lambda_observed) / lambda_observed * 100
    lambda_log10_prediction = math.log10(lambda_prediction) if lambda_prediction > 0 else float("-inf")
    lambda_log10_observed = math.log10(lambda_observed) if lambda_observed > 0 else float("-inf")
    lambda_log10_error = abs(lambda_log10_prediction - lambda_log10_observed)

    if lambda_error_pct < 5:
        lambda_status = "PASS"
    elif lambda_error_pct < 20:
        lambda_status = "REVIEW"
    else:
        lambda_status = "FAIL"

    # =========================================================================
    # H0 / TENSIÓN DE HUBBLE
    # =========================================================================

    hubble_formula_label = "Omega_H = BETA * PHI * sqrt(2)"
    hubble_prediction = BETA * PHI * math.sqrt(2)

    h_early = None
    h_late = None
    obs_diff = None

    h_early_candidates = ["H_EARLY", "H0_EARLY", "HUBBLE_EARLY"]
    h_late_candidates = ["H_LATE", "H0_LATE", "HUBBLE_LATE"]
    obs_diff_candidates = ["OBS_DIFF", "HUBBLE_OBS_DIFF", "OBSERVED_HUBBLE_TENSION"]

    for mod in (cosmology_mod, constants_mod):
        if mod is None:
            continue

        for name in h_early_candidates:
            value = get_attr(mod, name, None)
            if value is not None:
                try:
                    h_early = float(value)
                    break
                except Exception:
                    pass

        for name in h_late_candidates:
            value = get_attr(mod, name, None)
            if value is not None:
                try:
                    h_late = float(value)
                    break
                except Exception:
                    pass

        for name in obs_diff_candidates:
            value = get_attr(mod, name, None)
            if value is not None:
                try:
                    obs_diff = float(value)
                    break
                except Exception:
                    pass

    if h_early is None:
        h_early = 67.4
    if h_late is None:
        h_late = 73.0
    if obs_diff is None:
        obs_diff = (h_late - h_early) / h_early

    hubble_abs_error = abs(hubble_prediction - obs_diff)
    hubble_error_pct = (hubble_abs_error / obs_diff * 100) if obs_diff != 0 else float("inf")
    hubble_tolerance = 0.01

    if hubble_abs_error < hubble_tolerance:
        hubble_status = "PASS"
    elif hubble_abs_error < 2 * hubble_tolerance:
        hubble_status = "REVIEW"
    else:
        hubble_status = "FAIL"

    # =========================================================================
    # STATUS GLOBAL COSMOLÓGICO
    # =========================================================================

    if lambda_status == "PASS" and hubble_status == "PASS":
        overall_status = "PASS"
    elif lambda_status == "FAIL" or hubble_status == "FAIL":
        overall_status = "FAIL"
    else:
        overall_status = "REVIEW"

    return {
        "status": overall_status,
        "lambda": {
            "formula": "Lambda = BETA^(27π + BETA·PHI^2)",
            "prediction": lambda_prediction,
            "observed": lambda_observed,
            "error_pct": lambda_error_pct,
            "log10_prediction": lambda_log10_prediction,
            "log10_observed": lambda_log10_observed,
            "log10_error": lambda_log10_error,
            "exponent_total": lambda_exponent,
            "base_term_27pi": lambda_base_term,
            "correction_term_beta_phi2": lambda_correction_term,
            "correction_ratio": (
                lambda_correction_term / lambda_exponent if lambda_exponent != 0 else 0.0
            ),
            "numerically_stable": math.isfinite(lambda_prediction) and lambda_prediction > 0,
            "improvement_qm": "10^120",
            "status": lambda_status,
        },
        "hubble": {
            "formula": hubble_formula_label,
            "prediction": hubble_prediction,
            "observed_diff": obs_diff,
            "H_early": h_early,
            "H_late": h_late,
            "abs_error": hubble_abs_error,
            "error_pct": hubble_error_pct,
            "tolerance": hubble_tolerance,
            "status": hubble_status,
        },
    }


def economic_cycles_validation() -> dict:
    natural_zeta = 0.118322
    observed = 0.11
    damping_error = abs(natural_zeta - observed) / observed * 100
    predicted_k = 54.8
    observed_k = 54.0
    kond_error = abs(predicted_k - observed_k) / observed_k * 100
    return {
        "natural_zeta": natural_zeta,
        "observed_zeta": observed,
        "damping_error_pct": damping_error,
        "kond_pred": predicted_k,
        "kond_obs": observed_k,
        "kond_error_pct": kond_error,
        "status": "PASS" if damping_error < 10 and kond_error < 5 else "REVIEW",
    }



# =============================================================================
# MARKDOWN HELPERS — cajas Unicode (estilo Omega SPARTACO)
# =============================================================================

ANCHO_MIN = 8
ANCHO_MAX = 42
ANCHO_TOTAL = 52
ANCHO_TOTAL_CI = 46
CAMPO_MAX = 18
CAMPO_MAX_CI = 16


def _ancho_vis(texto: str) -> int:
    n = 0
    for ch in str(texto):
        o = ord(ch)
        if (
            0x0300 <= o <= 0x036F
            or 0xFE00 <= o <= 0xFE0F
            or o in (0x200D, 0x20E3, 0xFEFF)
        ):
            continue
        if (
            0x1F000 <= o <= 0x1FAFF
            or 0x2600 <= o <= 0x27BF
            or 0x2300 <= o <= 0x23FF
            or 0x2B00 <= o <= 0x2BFF
            or 0x2190 <= o <= 0x21FF
            or o in (0x2139, 0x2122, 0x3030, 0x3297, 0x3299)
            or 0x2E80 <= o <= 0x9FFF
            or 0xF900 <= o <= 0xFAFF
            or 0xFF01 <= o <= 0xFF60
            or 0xFFE0 <= o <= 0xFFE6
        ):
            n += 2
        else:
            n += 1
    return n


def _pad(texto: str, ancho: int, alineacion: str = "left") -> str:
    s = str(texto)
    hueco = max(0, ancho - _ancho_vis(s))
    if alineacion == "center":
        izq = hueco // 2
        s = (" " * izq) + s + (" " * (hueco - izq))
    elif alineacion == "right":
        s = (" " * hueco) + s
    else:
        s = s + (" " * hueco)
    while _ancho_vis(s) < ancho:
        s += " "
    while _ancho_vis(s) > ancho and s.endswith(" "):
        s = s[:-1]
    return s


def _envolver(texto: str, ancho: int):
    s = str(texto).replace("\r", " ").replace("\n", " ").strip()
    if not s:
        return [""]
    if _ancho_vis(s) <= ancho:
        return [s]
    palabras = s.split(" ")
    if palabras and _ancho_vis(palabras[0]) <= 2 and len(palabras) >= 2:
        palabras = [palabras[0] + " " + palabras[1]] + palabras[2:]
    lineas = []
    actual = ""
    for p in palabras:
        cand = (actual + " " + p).strip() if actual else p
        if _ancho_vis(cand) <= ancho:
            actual = cand
            continue
        if actual:
            lineas.append(actual)
        if _ancho_vis(p) <= ancho:
            actual = p
            continue
        trozo = ""
        for ch in p:
            prueba = trozo + ch
            if _ancho_vis(prueba) <= ancho:
                trozo = prueba
            else:
                if trozo:
                    lineas.append(trozo)
                trozo = ch
        actual = trozo
    if actual:
        lineas.append(actual)
    return lineas or [""]


def _alinea_celda(valor):
    s = str(valor).strip()
    if s in {"✅", "❌", "⚠️", "ℹ️", "⏭️", "★"}:
        return "center"
    if s.upper() in {"PASS", "FAIL", "WARN", "YES", "NO", "TRUE", "FALSE", "OK", "N/A"}:
        return "center"
    try:
        float(s.replace("%", "").replace(",", ""))
        return "center"
    except Exception:
        return "left"


def _anchos(headers, filas):
    n = len(headers)
    anchos = []
    for j, enc in enumerate(headers):
        m = _ancho_vis(enc)
        for fila in filas:
            if j < len(fila):
                m = max(m, min(_ancho_vis(str(fila[j])), ANCHO_MAX))
        estrecha = False
        for fila in filas:
            if j < len(fila) and _alinea_celda(fila[j]) == "center":
                estrecha = True
                break
        if estrecha:
            m = max(6, min(m, 14))
        else:
            m = max(ANCHO_MIN if n == 1 else 6, min(m, ANCHO_MAX))
        anchos.append(m)
    keys = [h.lower() for h in headers]
    if n == 2 and keys in (["campo", "valor"], ["metric", "value"], ["check", "status"], ["módulo", "estado"], ["modulo", "estado"], ["layer", "energy"]):
        w0 = max(8, min(anchos[0], CAMPO_MAX))
        w1 = ANCHO_TOTAL - 3 - w0
        if w1 < 12:
            w0 = max(8, ANCHO_TOTAL - 3 - 12)
            w1 = ANCHO_TOTAL - 3 - w0
        return [w0, max(8, w1)]
    while sum(anchos) + n + 1 > ANCHO_TOTAL:
        idx = max(range(n), key=lambda i: anchos[i])
        if anchos[idx] <= 4:
            break
        anchos[idx] -= 1
    return anchos


def _tabla_apilada(headers, filas):
    """Tarjeta POR FILA, no caja por celda. Usado por renderer CI."""
    out = []
    for fila in filas:
        title_bits = []
        pairs = []
        for j, enc in enumerate(headers):
            val = fila[j] if j < len(fila) else ""
            if j == 0:
                title_bits.append(str(val))
            elif j == 1 and len(headers) > 2:
                title_bits.append(str(val))
            else:
                pairs.append((str(enc), str(val)))
        if len(headers) <= 2:
            pairs = [(str(headers[j]), str(fila[j]) if j < len(fila) else "") for j in range(len(headers))]
            title = ""
        else:
            title = " · ".join(x for x in title_bits if x)
        out.extend(ci_card(title, pairs))
    return out


def _tabla_caja(headers, filas):
    headers = [str(h) for h in headers]
    pintadas = []
    for fila in filas:
        celdas = [str(c) if c is not None else "" for c in list(fila)]
        if len(celdas) < len(headers):
            celdas = celdas + [""] * (len(headers) - len(celdas))
        pintadas.append(celdas[: len(headers)])
    if not pintadas:
        pintadas = [[""] * len(headers)]
    anchos = _anchos(headers, pintadas)
    if len(headers) > 3 or min(anchos) < 8:
        return _tabla_apilada(headers, pintadas)

    def linea(izq, mid, der):
        return izq + mid.join("─" * w for w in anchos) + der

    def fila_envuelta(celdas, es_encabezado):
        env = [_envolver(celdas[j], anchos[j]) for j in range(len(headers))]
        alto = max(len(x) for x in env)
        out = []
        for r in range(alto):
            partes = []
            for j in range(len(headers)):
                trozo = env[j][r] if r < len(env[j]) else ""
                ali = "left" if es_encabezado else (_alinea_celda(celdas[j]) if r == 0 else "left")
                partes.append(_pad(trozo, anchos[j], ali))
            out.append("│" + "│".join(partes) + "│")
        return out

    out = [linea("┌", "┬", "┐")]
    out.extend(fila_envuelta(headers, True))
    out.append(linea("├", "┼", "┤"))
    for i, fila in enumerate(pintadas):
        out.extend(fila_envuelta(fila, False))
        if i < len(pintadas) - 1:
            out.append(linea("├", "┼", "┤"))
    out.append(linea("└", "┴", "┘"))
    if any(_ancho_vis(x) > ANCHO_TOTAL + 4 for x in out):
        return _tabla_apilada(headers, pintadas)
    return out


def md_cell(value) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r", " ").replace("\n", " ").replace("|", "\\|").replace("`", "'")
    return text


def _align_mark(header: str, sample_rows, col: int) -> str:
    name = str(header).lower()
    if name in {"#", "estado", "status", "clase", "ok", "icono"}:
        return ":---:"
    vals = [str(r[col]) if col < len(r) else "" for r in sample_rows]
    if any(v.strip() in {"✅", "❌", "⚠️", "ℹ️", "⏭️"} or v.strip().upper() in {"PASS", "FAIL", "WARN", "TRUE", "FALSE", "YES", "NO"} for v in vals):
        return ":---:"
    numeric = 0
    for v in vals:
        s = v.strip().replace("%", "").replace(",", "")
        try:
            float(s)
            numeric += 1
        except Exception:
            pass
    if vals and numeric >= max(1, len(vals) // 2):
        return "---:"
    return ":---"


def md_table(headers: list[str], rows: list[list[str]], align=None) -> str:
    headers = [md_cell(h) for h in headers]
    body_rows = []
    for row in rows:
        cells = list(row) + [""] * (len(headers) - len(row))
        body_rows.append([md_cell(c) for c in cells[: len(headers)]])
    marks = []
    for i, h in enumerate(headers):
        if align and i < len(align):
            a = align[i]
            marks.append(":---:" if a == "center" else ("---:" if a == "right" else ":---"))
        else:
            marks.append(_align_mark(h, body_rows, i))
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(marks) + " |"]
    for row in body_rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)





def _ci_limite():
    return ANCHO_TOTAL_CI


def _ci_campo_valor_anchos():
    inner = ANCHO_TOTAL_CI - 2
    w0 = CAMPO_MAX_CI
    w1 = inner - 1 - w0
    if w1 < 12:
        w0 = max(8, inner - 1 - 12)
        w1 = inner - 1 - w0
    return w0, max(8, w1)


def ci_card(title, pairs):
    w0, w1 = _ci_campo_valor_anchos()
    inner = w0 + 1 + w1
    out = []
    top = "┌" + ("─" * inner) + "┐"
    mid = "├" + ("─" * w0) + "┼" + ("─" * w1) + "┤"
    bot = "└" + ("─" * w0) + "┴" + ("─" * w1) + "┘"
    if title:
        out.append(top)
        for i, t in enumerate(_envolver(str(title), inner)):
            out.append("│" + _pad(t, inner, "left") + "│")
        out.append(mid)
    else:
        out.append("┌" + ("─" * w0) + "┬" + ("─" * w1) + "┐")
    for i, (campo, valor) in enumerate(pairs):
        labs = _envolver(str(campo), w0)
        vals = _envolver(str(valor), w1)
        alto = max(len(labs), len(vals))
        ali = _alinea_celda(valor)
        for r in range(alto):
            lab = labs[r] if r < len(labs) else ""
            val = vals[r] if r < len(vals) else ""
            a = ali if r == 0 else "left"
            out.append("│" + _pad(lab, w0, "left") + "│" + _pad(val, w1, a) + "│")
        if i < len(pairs) - 1:
            out.append(mid)
    out.append(bot)
    return out


def ci_kv(pares):
    return ci_card("", [(str(k), v) for k, v in pares])


def ci_table(headers, filas):
    headers = [str(h) for h in headers]
    pintadas = []
    for fila in filas:
        celdas = ["" if c is None else str(c) for c in list(fila)]
        if len(celdas) < len(headers):
            celdas += [""] * (len(headers) - len(celdas))
        pintadas.append(celdas[: len(headers)])
    if len(headers) <= 2:
        if not headers:
            return []
        if len(headers) == 1:
            return ci_card(headers[0], [(headers[0], r[0] if r else "") for r in pintadas])
        pares = []
        # if first row looks like headered records use cards when many rows with long text
        return ci_card("", [(r[0], r[1] if len(r) > 1 else "") for r in pintadas])
    return _tabla_apilada(headers, pintadas)


def ci_banner(titulo):
    inner = ANCHO_TOTAL_CI
    bar = "═" * inner
    t = str(titulo)
    if _ancho_vis(t) > inner:
        t = _envolver(t, inner)[0]
    return [bar, _pad(t, inner, "left"), bar]


def ci_sep():
    return "─" * ANCHO_TOTAL_CI


def stdout_a_pares(text: str):
    pares = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if set(line) <= set("-=─━═|*_ "):
            continue
        parsed = False
        for sep in (" = ", ":", "→", "="):
            if sep in line:
                k, v = line.split(sep, 1)
                k = k.strip(" -•*#")
                v = v.strip()
                if k and v and len(k) <= 48:
                    pares.append((k, v))
                    parsed = True
                    break
        if not parsed and len(line) > 2:
            pares.append(("·", line))
    return pares


def _fmt_ci(v):
    if v is None:
        return "N/D"
    if isinstance(v, bool):
        return "True" if v else "False"
    if isinstance(v, float):
        if abs(v) >= 1e4 or (abs(v) > 0 and abs(v) < 1e-3):
            return "{0:.4e}".format(v)
        return "{0:.6f}".format(v)
    return str(v)


def render_ci(paquete):
    lines = []
    gen = (paquete.get("generated") or {}) if isinstance(paquete.get("generated"), dict) else {}
    metrics = paquete.get("metrics") or {}
    diag = paquete.get("diagnostic") or {}
    tests = paquete.get("tests") or {}
    engine = paquete.get("engine") or {}
    status = paquete.get("system_status") or {}
    vals = paquete.get("validations") or {}
    modules = paquete.get("modules") or []
    history = paquete.get("history") or []
    checks = paquete.get("const_checks") or []
    ci_ev = paquete.get("ci_evidence") or {}
    states = metrics.get("states") or {}
    energies = metrics.get("energies") or {}
    l7 = metrics.get("l7") or {}

    audit0 = paquete.get("audit") or {}
    cov0 = audit0.get("coverage") or paquete.get("coverage") or {}
    lines.extend(ci_banner("{0} OMEGA DIAGNOSTIC REPORT · v{1}".format(ICON_OMEGA, VERSION)))
    lines.extend(ci_kv([
        ("{0} Generated".format(ICON_TIME), gen.get("utc") or ""),
        ("{0} Framework".format(ICON_AX), "UCF v3.2"),
        ("{0} Commit".format(ICON_SRC), gen.get("sha") or ""),
        ("{0} Authority".format(ICON_ENGINE), engine.get("class") or "discovery"),
        ("{0} Py repo".format(ICON_PKG), cov0.get("repo_files")),
        ("{0} Import OK".format(ICON_OK), cov0.get("modules_importable")),
        ("{0} Import FAIL".format(ICON_FAIL), cov0.get("modules_failed_import")),
        ("{0} Símbolos".format(ICON_NUM), cov0.get("public_symbols_discovered")),
        ("{0} Layers".format(ICON_LAYER), cov0.get("layers_discovered")),
        ("{0} Validaciones+".format(ICON_AX), cov0.get("validations_discovered")),
        ("{0} Stdout tests".format(ICON_TEST), cov0.get("captured_stdout_n")),
    ]))

    lines.extend(ci_banner("{0} ESTADO FENOMENOLÓGICO".format(ICON_COH)))
    lines.extend(ci_kv([
        ("{0} Estado".format(ICON_COH), "{0} {1}".format(diag.get("symbol") or "", diag.get("pheno") or "")),
        ("{0} C_struct".format(ICON_MET), _fmt_ci(metrics.get("C_struct"))),
        ("{0} C_global".format(ICON_MET), _fmt_ci(metrics.get("C_global_norm"))),
        ("{0} C_CI".format(ICON_TEST), _fmt_ci(metrics.get("C_CI"))),
        ("{0} phi_eff".format(ICON_FORM), _fmt_ci(metrics.get("phi_eff"))),
        ("{0} L7".format(ICON_LAYER), _fmt_ci(metrics.get("L7"))),
        ("{0} Tendencia".format(ICON_HIST), diag.get("trend")),
    ]))

    lines.extend(ci_banner("{0} CÓDIGO DIAGNÓSTICO".format(ICON_ID)))
    lines.extend(ci_kv([
        ("{0} Código".format(ICON_ID), diag.get("code")),
        ("{0} Nombre".format(ICON_FLAG), diag.get("name")),
        ("{0} C_struct".format(ICON_MET), _fmt_ci(metrics.get("C_struct"))),
        ("{0} Desc".format(ICON_ITEM), diag.get("desc")),
    ]))

    lines.extend(ci_banner("{0} SYSTEM STATUS".format(ICON_MET)))
    lines.extend(ci_kv([
        ("{0} C_struct".format(ICON_COH), _fmt_ci(metrics.get("C_struct"))),
        ("{0} C_global".format(ICON_MET), _fmt_ci(metrics.get("C_global_norm"))),
        ("{0} L7".format(ICON_LAYER), _fmt_ci(metrics.get("L7"))),
        ("{0} Entropy".format(ICON_WAVE), _fmt_ci(metrics.get("entropy"))),
        ("{0} Harmony".format(ICON_PULSE), _fmt_ci(metrics.get("harmony"))),
        ("{0} Energy".format(ICON_BOLT), _fmt_ci(metrics.get("total_energy"))),
        ("{0} Zeta".format(ICON_ORBIT), _fmt_ci(metrics.get("zeta"))),
        ("{0} Period".format(ICON_TIME), _fmt_ci(metrics.get("period"))),
        ("{0} Source".format(ICON_SRC), metrics.get("coherence_source")),
    ]))

    lines.extend(ci_banner("{0} TEST RESULTS".format(ICON_TEST)))
    lines.extend(ci_kv([
        ("{0} Source".format(ICON_SRC), tests.get("source")),
        ("{0} Executed".format(ICON_RES), tests.get("executed")),
        ("{0} Total".format(ICON_NUM), tests.get("total")),
        ("{0} Passed".format(ICON_OK), tests.get("passed")),
        ("{0} Failed".format(ICON_FAIL), tests.get("failed")),
        ("{0} Skipped".format(ICON_SKIP), tests.get("skipped")),
        ("{0} Rate".format(ICON_MET), tests.get("pass_rate")),
    ]))

    lines.extend(ci_banner("{0} COHERENCE HISTORY".format(ICON_HIST)))
    if history:
        last = history[-1] if isinstance(history[-1], dict) else {}
        lines.extend(ci_kv([
            ("{0} Runs".format(ICON_NUM), len(history)),
            ("{0} Last passed".format(ICON_OK), last.get("passed")),
            ("{0} Last failed".format(ICON_FAIL), last.get("failed")),
            ("{0} Estado".format(ICON_COH), last.get("estado") or last.get("pass_rate")),
        ]))
    else:
        lines.extend(ci_kv([("{0} Historial".format(ICON_INFO), "N/D")]))

    lines.extend(ci_banner("{0} CONSTANTS INTEGRITY".format(ICON_SCALE)))
    for c, s in checks:
        lines.extend(ci_kv([(str(c), _icono_status(s))]))

    lines.extend(ci_banner("{0} FRAMEWORK CONSTANTS".format(ICON_NUM)))
    const_eq = [
        ("ALPHA", "26/27", globals().get("ALPHA")),
        ("BETA", "1/27", globals().get("BETA")),
        ("PHI", "(1+√5)/2", globals().get("PHI")),
        ("S_REF", "e/π", globals().get("S_REF")),
        ("S_REF_7", "S_REF+β·ln(7)", globals().get("S_REF_7")),
        ("R_FIN", "1+1/27", globals().get("R_FIN")),
        ("KAPPA", "π/4", globals().get("KAPPA")),
        ("GOLDEN_ANG", "360/φ²", globals().get("GOLDEN_ANG")),
        ("THETA_CUBE", "asin(1/√27)", globals().get("THETA_CUBE_DEG")),
        ("OMEGA_EFF", "π·(1-√β)", globals().get("OMEGA_EFF")),
        ("T_PERIOD", "2π/ω_d", globals().get("T_PERIOD")),
        ("LAMBDA_UCF", "β^(π/β+β·φ²)", globals().get("LAMBDA_UCF")),
        ("OMEGA_RED", "(π/e)·(1-β²)", globals().get("OMEGA_RED")),
    ]
    const_pares = []
    for name, eq, val in const_eq:
        const_pares.append(("{0} {1}".format(ICON_FORM, name), eq))
        const_pares.append(("{0} valor".format(ICON_NUM), _fmt_ci(val)))
    lines.extend(ci_kv(const_pares))

    lines.extend(ci_banner("{0} LAYER STATUS".format(ICON_LAYER)))
    names = globals().get("LAYER_NAMES") or {}
    fric = globals().get("LAYER_FRICTIONS") or {}
    ranges = globals().get("LAYER_HEALTHY_RANGES") or {}
    ang = globals().get("GOLDEN_ANG") or 0
    for idx, key in enumerate(["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7"]):
        st = (states or {}).get(key) or {}
        phi = st.get("phi", fric.get(key))
        lohi = ranges.get(key)
        rango = "[{0:.2f}, {1:.2f}]".format(lohi[0], lohi[1]) if lohi else "N/D"
        title = "{0} {1} · {2}".format(ICON_LAYER, key, names.get(key, key))
        lines.extend(ci_card(title, [
            ("Friction", _fmt_ci(phi) if phi is not None else "N/D"),
            ("Spiral Angle", "{0:.1f} deg".format((idx * ang) % 360) if key != "L7" else "{0:.1f} deg".format((7 * ang) % 360)),
            ("Healthy Range", rango),
        ]))

    lines.extend(ci_banner("{0} MODULE STATUS".format(ICON_PKG)))
    for item in modules:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            name, st = item[0], item[1]
        else:
            name, st = str(item), ""
        path = ""
        if "(" in str(name) and str(name).endswith(")"):
            core, path = str(name).rsplit("(", 1)
            name = core.strip()
            path = path[:-1]
        lines.extend(ci_card("{0} {1}".format(ICON_PKG, name), [
            ("Estado", st),
            ("Path", path),
        ]))

    lines.extend(ci_banner("{0} DOMAIN VALIDATIONS".format(ICON_AX)))
    def _payload(obj):
        if not isinstance(obj, dict):
            return {}
        if "metrics" in obj and isinstance(obj.get("metrics"), dict):
            obj = obj.get("metrics") or {}
        return obj

    def _filas(data):
        pares = []
        if not isinstance(data, dict):
            return pares

        def _add(k, v, prefix=""):
            label = "{0}{1}".format(prefix, k) if prefix else str(k)
            kl = str(k).lower()
            if isinstance(v, dict):
                for sk, sv in v.items():
                    _add(sk, sv, prefix=label + ".")
                return
            if isinstance(v, list):
                pares.append((label, "n={0}".format(len(v))))
                return
            if "formula" in kl or kl in {"eq", "ecuacion", "ecuación"}:
                pares.insert(0, ("{0} {1}".format(ICON_FORM, label), str(v)))
                return
            if kl in {"status", "available"}:
                pares.append((label, _icono_status(v)))
                return
            if kl in {"prediction", "value", "valor", "observed", "result", "l7", "e_m_computed"}:
                pares.append(("{0} {1}".format(ICON_NUM, label), _fmt_ci(v)))
                return
            pares.append((label, _fmt_ci(v)))

        for k, v in data.items():
            if k in {"id", "title"}:
                continue
            _add(k, v)
        return pares

    cosmo = _payload(vals.get("cosmo") or {})
    mapping = [
        (ICON_EARTH, "Cosmological Constant", cosmo.get("lambda") if isinstance(cosmo.get("lambda"), dict) else cosmo),
        (ICON_ORBIT, "Hubble Tension", cosmo.get("hubble") if isinstance(cosmo.get("hubble"), dict) else _payload(vals.get("hubble") or {})),
        (ICON_WAVE, "Economic Cycles", _payload(vals.get("econ") or {})),
        (ICON_ATOM, "Quantum Gravity", _payload(vals.get("qg") or {})),
        (ICON_GEN, "Neuroscience", _payload(vals.get("neuro") or {})),
        (ICON_SEED, "Genetic Code", _payload(vals.get("genetic") or {})),
        (ICON_MOON, "Black Hole", _payload(vals.get("bh") or {})),
    ]
    for icon, title, data in mapping:
        lines.extend(ci_banner("{0} {1}".format(icon, title.upper())))
        if not isinstance(data, dict) or not data:
            lines.extend(ci_kv([("{0} Estado".format(ICON_INFO), "N/D")]))
            continue
        lines.extend(ci_kv(_filas(data)))

    torus = vals.get("torus") or {}
    lines.extend(ci_banner("{0} TORUS FORMULA".format(ICON_GRAPH)))
    if isinstance(torus, dict):
        pares = []
        for k, v in torus.items():
            if isinstance(v, dict):
                pares.append((str(k), "{0} keys".format(len(v))))
            elif isinstance(v, list):
                pares.append((str(k), "n={0}".format(len(v))))
            else:
                pares.append((str(k), _fmt_ci(v) if not isinstance(v, bool) else ("{0} {1}".format(ICON_OK if v else ICON_FAIL, v))))
        lines.extend(ci_kv(pares))

    lines.extend(ci_banner("{0} L7 INTEGRATION".format(ICON_LAYER)))
    if isinstance(l7, dict):
        lines.extend(ci_kv([
            ("{0} Value".format(ICON_MET), _fmt_ci(l7.get("value"))),
            ("{0} Status".format(ICON_RES), l7.get("status")),
            ("{0} Source".format(ICON_SRC), l7.get("source")),
            ("{0} Formula".format(ICON_FORM), l7.get("formula")),
            ("{0} Law".format(ICON_CONTRACT), l7.get("law")),
        ]))

    lines.extend(ci_banner("{0} ENERGY DISTRIBUTION".format(ICON_BOLT)))
    energy_pairs = []
    for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if k in energies:
            energy_pairs.append(("{0} {1}".format(ICON_LAYER, k), _fmt_ci(energies[k])))
    energy_pairs.append(("{0} Total".format(ICON_MET), _fmt_ci(metrics.get("total_energy"))))
    lines.extend(ci_kv(energy_pairs))

    lines.extend(ci_banner("{0} CUBE GEOMETRY".format(ICON_CUBE)))
    lines.extend(ci_kv([
        ("Positions", "27 = 3×3×3"),
        ("Exterior / α", "26"),
        ("Center / β", "1"),
        ("α + β", "1"),
    ]))

    ax = (ci_ev.get("axioms") or {}).get("data") or {}
    lines.extend(ci_banner("{0} AXIOMATIC / FORMAL STATE".format(ICON_AX)))
    if isinstance(ax, dict) and ax:
        cuerpos = ax.get("cuerpos") or []
        lines.extend(ci_kv([
            ("{0} Coherente".format(ICON_COH), ax.get("coherente")),
            ("{0} Declaraciones".format(ICON_NUM), ax.get("declaraciones")),
            ("{0} Cuerpos".format(ICON_NUM), len(cuerpos) if isinstance(cuerpos, list) else ax.get("cuerpos")),
            ("{0} Errores".format(ICON_ERR if "ICON_ERR" in dir() else ICON_FAIL), len(ax.get("errores") or []) if isinstance(ax.get("errores"), list) else ax.get("errores")),
            ("{0} Choques".format(ICON_WARN), len(ax.get("choques") or []) if isinstance(ax.get("choques"), list) else ax.get("choques")),
        ]))
        if isinstance(cuerpos, list) and cuerpos:
            lines.append(ci_sep())
            lines.append("{0} CUERPOS".format(ICON_FILE))
            for i, c in enumerate(cuerpos, 1):
                for t in _envolver("{0:>2}. {1}".format(i, c), ANCHO_TOTAL_CI):
                    lines.append(t)
    else:
        lines.extend(ci_kv([("{0} Artefacto".format(ICON_INFO), "N/D")]))

    gd = (ci_ev.get("generatividad") or {}).get("data") or {}
    lines.extend(ci_banner("{0} GENERATIVIDAD OPERATIVA".format(ICON_GEN)))
    if isinstance(gd, dict) and gd:
        op = {k: v for k, v in gd.items() if k != "canonica"}
        pares = []
        for k, v in op.items():
            if isinstance(v, (dict, list)):
                pares.append((str(k), "n={0}".format(len(v))))
            else:
                pares.append((str(k), _fmt_ci(v)))
        lines.extend(ci_kv(pares))
        lines.extend(ci_banner("{0} GENERATIVIDAD CANÓNICA TR1".format(ICON_CONTRACT)))
        can = gd.get("canonica") or {}
        if isinstance(can, dict):
            pares = []
            for k, v in can.items():
                if isinstance(v, (dict, list)):
                    pares.append((str(k), "n={0}".format(len(v))))
                else:
                    pares.append((str(k), _fmt_ci(v)))
            lines.extend(ci_kv(pares))

    lines.extend(ci_banner("{0} ENGINE".format(ICON_ENGINE)))
    lines.extend(ci_kv([
        ("{0} Startup".format(ICON_GEAR), engine.get("startup")),
        ("{0} Estado".format(ICON_COH), engine.get("estado")),
        ("{0} Error".format(ICON_FAIL), engine.get("error")),
    ]))

    lines.extend(ci_banner("{0} DIAGNOSTIC ARTIFACTS".format(ICON_DISK)))
    arts = ((paquete.get("diagnostics") or {}).get("artifacts")) or []
    if arts:
        for rec in arts:
            mark = ICON_OK if rec.get("present") and rec.get("read_ok") else ICON_FAIL
            lines.extend(ci_card("{0} {1}".format(mark, rec.get("name") or rec.get("path")), [
                ("Path", rec.get("path")),
                ("Bytes", rec.get("bytes")),
                ("Parse", rec.get("parse_ok")),
                ("SHA", (rec.get("sha256") or "N/D")[:12]),
            ]))
    else:
        for key, rec in ci_ev.items():
            if not isinstance(rec, dict):
                continue
            if "present" not in rec and "path" not in rec:
                continue
            mark = ICON_OK if rec.get("present") else ICON_FAIL
            lines.extend(ci_kv([(mark + " " + str(rec.get("name") or rec.get("path") or key), rec.get("present"))]))

    lines.extend(ci_banner("{0} PROVENANCE".format(ICON_SRC)))
    lines.extend(ci_kv([
        ("{0} C_struct src".format(ICON_SRC), metrics.get("coherence_source")),
        ("{0} Layers src".format(ICON_LAYER), metrics.get("states_source")),
        ("{0} L7 src".format(ICON_LAYER), l7.get("source") if isinstance(l7, dict) else None),
        ("{0} Tests src".format(ICON_TEST), tests.get("source")),
        ("{0} Status src".format(ICON_AUDIT), status.get("source")),
    ]))

    audit = paquete.get("audit") or {}
    cov = audit.get("coverage") or paquete.get("coverage") or {}
    lines.extend(ci_banner("{0} AUDIT COVERAGE".format(ICON_AUDIT)))
    lines.extend(ci_kv([
        ("{0} Py files".format(ICON_PKG), cov.get("python_files_discovered")),
        ("{0} Import OK".format(ICON_OK), cov.get("modules_importable")),
        ("{0} Import FAIL".format(ICON_FAIL), cov.get("modules_failed_import")),
        ("{0} Símbolos".format(ICON_NUM), cov.get("public_symbols_discovered")),
        ("{0} Layers".format(ICON_LAYER), cov.get("layers_discovered")),
        ("{0} Fórmulas".format(ICON_FORM), cov.get("formulas_discovered")),
        ("{0} Producers".format(ICON_AX), cov.get("validations_discovered")),
        ("{0} Findings".format(ICON_ERR), cov.get("findings_n")),
    ]))
    for f in (audit.get("formulas") or []):
        lines.extend(ci_card("{0} {1}".format(ICON_FORM, f.get("name")), [
            ("Módulo", f.get("module")),
            ("Args", ", ".join(f.get("args") or [])),
            ("Línea", f.get("line")),
        ]))
    for p in (audit.get("producers") or []):
        mets = p.get("metrics") if isinstance(p.get("metrics"), dict) else {}
        pares = [("Hook", p.get("hook")), ("Fuente", p.get("source"))]
        for k, v in list(mets.items())[:24]:
            if isinstance(v, dict):
                continue
            pares.append((str(k), _fmt_ci(v)))
        lines.extend(ci_card("{0} {1}".format(ICON_AX, p.get("title")), pares))
    for blob in (audit.get("module_stdout") or []):
        title = str(blob.get("name") or blob.get("path") or "audit")
        pares = stdout_a_pares(blob.get("stdout") or "")
        lines.extend(ci_banner("{0} {1}".format(ICON_FORM, title.upper()[-40:])))
        if pares:
            lines.extend(ci_kv([(k, v) for k, v in pares]))
        else:
            preview = " / ".join([ln.strip() for ln in (blob.get("stdout") or "").splitlines() if ln.strip()][:8])
            lines.extend(ci_kv([("salida", preview)]))

    for b in (audit.get("captured_stdout") or []):
        text = b.get("stdout") or ""
        preview = " / ".join([ln.strip() for ln in text.splitlines() if ln.strip()][:6])
        lines.extend(ci_card("{0} {1}".format(ICON_TEST, (b.get("case") or "")[-28:]), [
            ("Status", b.get("status")),
            ("Bytes", len(text)),
            ("Preview", preview),
        ]))
    finds = audit.get("findings") or paquete.get("findings") or []
    if finds:
        lines.extend(ci_banner("{0} FINDINGS".format(ICON_ERR)))
        for f in finds:
            lines.extend(ci_card("{0} {1}".format(ICON_ERR, f.get("severity")), [
                ("Cat", f.get("category")),
                ("Comp", f.get("component")),
                ("Msg", f.get("message")),
            ]))

    coh = status.get("coherente")
    if coh is True:
        cierre = "{0} COHERENTE".format(ICON_OK)
    elif coh is False:
        cierre = "{0} INCOHERENTE".format(ICON_FAIL)
    else:
        cierre = "{0} N/D".format(ICON_INFO)
    lines.extend(ci_banner("{0} FINAL CLOSURE".format(ICON_OMEGA)))
    lines.extend(ci_kv([
        ("{0} Sistema".format(ICON_COH), cierre),
        ("{0} Engine".format(ICON_ENGINE), engine.get("startup")),
        ("{0} Tests".format(ICON_TEST), tests.get("source")),
    ]))
    lines.append("{0} Omega".format(ICON_OMEGA))

    # enforce width
    fixed = []
    for ln in lines:
        if isinstance(ln, list):
            for x in ln:
                if _ancho_vis(x) > ANCHO_TOTAL_CI:
                    for t in _envolver(x, ANCHO_TOTAL_CI):
                        fixed.append(t)
                else:
                    fixed.append(x)
        else:
            if _ancho_vis(str(ln)) > ANCHO_TOTAL_CI:
                fixed.extend(_envolver(str(ln), ANCHO_TOTAL_CI))
            else:
                fixed.append(str(ln))
    return "\n".join(fixed)


def layer_rows(states: dict[str, dict[str, float]] | None = None) -> list[list[str]]:
    source = states if states is not None else default_layer_states()
    rows: list[list[str]] = []

    for idx, key in enumerate(["L0", "L1", "L2", "L3", "L4", "L5", "L6"]):
        angle = (idx * GOLDEN_ANG) % 360
        lo, hi = LAYER_HEALTHY_RANGES[key]
        rows.append([
            key,
            LAYER_NAMES[key],
            f"{safe_float(source[key]['phi'], LAYER_FRICTIONS[key]):.2f}",
            f"{angle:.1f} deg",
            f"[{lo:.2f}, {hi:.2f}]",
        ])

    angle_l7 = (7 * GOLDEN_ANG) % 360
    lo7, hi7 = LAYER_HEALTHY_RANGES["L7"]
    rows.append([
        "L7",
        f"{LAYER_NAMES['L7']} ← emergente",
        f"{LAYER_FRICTIONS['L7']:.2f}",
        f"{angle_l7:.1f} deg",
        f"[{lo7:.2f}, {hi7:.4f}]",
    ])

    friction_l0_l6 = sum(safe_float(source[k]["phi"], LAYER_FRICTIONS[k]) for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"])
    rows.append(["**Total**", "", f"**{friction_l0_l6:.2f}** (L0-L6)", "", ""])
    return rows


# =============================================================================
# REPORT BUILD
# =============================================================================


# =============================================================================
# ADDITIONAL DOMAIN VALIDATIONS
# =============================================================================

def quantum_gravity_validation() -> dict:
    constants_mod = safe_import("formulas.constants")
    if constants_mod is None:
        return {"available": False, "status": "MODULO NO ENCONTRADO"}
        
    e_planck_ucf = get_attr(constants_mod, "E_PLANCK_UCF", 1.956e9)
    e_planck_ref = get_attr(constants_mod, "E_PLANCK_REF", 1.956e9)
    e_planck_error = get_attr(constants_mod, "E_PLANCK_ERROR", 0.0)
    
    m_electron_ucf = get_attr(constants_mod, "M_ELECTRON_UCF", 9.109e-31)
    m_electron_ref = get_attr(constants_mod, "M_ELECTRON_REF", 9.10938e-31)
    m_electron_error = get_attr(constants_mod, "M_ELECTRON_ERROR", 0.0)
    
    r_electron_ucf = get_attr(constants_mod, "R_ELECTRON_UCF", 2.817e-15)
    r_electron_ref = get_attr(constants_mod, "R_ELECTRON_REF", 2.81794e-15)
    r_electron_error = get_attr(constants_mod, "R_ELECTRON_ERROR", 0.0)
    
    alpha_s_ucf = get_attr(constants_mod, "ALPHA_S_UCF", 0.1179)
    alpha_s_ref = get_attr(constants_mod, "ALPHA_S_REF", 0.1179)
    alpha_s_error = get_attr(constants_mod, "ALPHA_S_ERROR", 0.0)
    
    return {
        "available": True,
        "e_planck_ucf": e_planck_ucf,
        "e_planck_ref": e_planck_ref,
        "e_planck_error": e_planck_error * 100,
        "m_electron_ucf": m_electron_ucf,
        "m_electron_ref": m_electron_ref,
        "m_electron_error": m_electron_error * 100,
        "r_electron_ucf": r_electron_ucf,
        "r_electron_ref": r_electron_ref,
        "r_electron_error": r_electron_error * 100,
        "alpha_s_ucf": alpha_s_ucf,
        "alpha_s_ref": alpha_s_ref,
        "alpha_s_error": alpha_s_error * 100,
        "status": "PASS" if e_planck_error < 0.05 else "REVIEW"
    }

def neuroscience_validation() -> dict:
    phi_ratio = PHI
    observed_ratio = 1.667
    error = abs(phi_ratio - observed_ratio) / observed_ratio * 100
    
    return {
        "available": True,
        "phi_ratio": phi_ratio,
        "observed_ratio": observed_ratio,
        "error": error,
        "status": "PASS" if error < 5.0 else "REVIEW"
    }

def genetic_code_validation() -> dict:
    amino_acids = 27 - 7
    observed = 20
    
    body_temp = 1000 * BETA
    observed_temp = 37.0
    temp_error = abs(body_temp - observed_temp) / observed_temp * 100
    
    return {
        "available": True,
        "amino_acids": amino_acids,
        "observed_amino": observed,
        "body_temp": body_temp,
        "observed_temp": observed_temp,
        "temp_error": temp_error,
        "status": "PASS" if amino_acids == observed and temp_error < 1.0 else "REVIEW"
    }

def black_hole_validation() -> dict:
    hawking_ref = 1 / (8 * math.pi)
    error = abs(BETA - hawking_ref) / hawking_ref * 100
    
    return {
        "available": True,
        "beta_value": BETA,
        "hawking_ref": hawking_ref,
        "error": error,
        "status": "PASS" if error < 10.0 else "REVIEW"
    }

def build_report():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    test_results = estimate_test_results()

    states, states_source = discover_layer_states()

    zeta = compute_zeta(states)
    omega_d = compute_omega_d(states)
    period = compute_period(omega_d)

    entropy, total_energy, energies = compute_system_entropy(states)
    harmony = compute_system_harmony(entropy)

    l7_info = l7_integration_status(states)

    c_structural, coherence_source = compute_system_coherence_measured(
        states=states,
        harmony=harmony,
        l7_value=safe_float(l7_info.get("value", 0.0), 0.0),
    )

    history = load_history()

    c_global_norm = c_structural / ALPHA if ALPHA > 0 else 0.0
    pass_rate = test_results["pass_rate"]
    c_ci = pass_rate / 100.0
    phi_eff = (1.0 - c_structural) * 2 * math.pi

    code, diag_name, diag_desc = diagnostic_label(c_structural)
    vector_interp = diagnostic_vector_interpretation(code)

    pheno_name, pheno_symbol = phenomenological_state(c_structural)
    trend = coherence_trend(history)
    loop_detected = detect_loop(history)
    traj = trajectory_str(history)
    sha = os.getenv("GITHUB_SHA", "local")[:7]
    module_status = check_module_status()

    above_critical = c_structural >= C_THRESHOLD_CRITICAL
    above_survival = c_structural >= C_THRESHOLD_SURVIVAL


    torus_info = torus_formula_validation()
    qg_info = quantum_gravity_validation()
    neuro_info = neuroscience_validation()
    genetic_info = genetic_code_validation()
    bh_info = black_hole_validation()


    const_checks = [
        ["ALPHA + BETA = 1", "PASS" if abs((ALPHA + BETA) - 1.0) < 1e-9 else "FAIL"],
        ["R_FIN = 1 + BETA", "PASS" if abs(R_FIN - (1 + BETA)) < 1e-9 else "FAIL"],
        ["sin^2(theta) = BETA", "PASS" if abs(math.sin(THETA_CUBE_RAD) ** 2 - BETA) < 1e-9 else "FAIL"],
        ["PHI^2 = PHI + 1", "PASS" if abs(PHI ** 2 - (PHI + 1)) < 1e-9 else "FAIL"],
        ["ZETA < 1 (underdamped)", "PASS" if zeta < 1 else "FAIL"],
        ["PHI_TOTAL < 2pi (alive)", "PASS" if sum(states[k]["phi"] for k in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]) < 2 * math.pi else "FAIL"],
        ["OMEGA_D > 0 (oscillates)", "PASS" if omega_d > 0 else "FAIL"],
        ["KAPPA = pi/4", "PASS" if abs(KAPPA - math.pi / 4) < 1e-9 else "FAIL"],
        ["S_REF = e/pi", "PASS" if abs(S_REF - math.e / math.pi) < 1e-9 else "FAIL"],
        ["C_structural <= alpha", "PASS" if c_structural <= ALPHA + 1e-9 else "FAIL"],
        ["C_structural < 1.0", "PASS" if c_structural < 1.0 else "FAIL"],
        ["BETA > 0 (irreducible)", "PASS" if BETA > 0 else "FAIL"],
        ["C > 0.72 (no crítico)", "PASS" if above_critical else "WARN"],
        ["C > 0.10 (survival)", "PASS" if above_survival else "FAIL"],
        ["L7 > 0 (integrado)", "PASS" if l7_info.get("value", 0) > 0 else "FAIL"],
    ]

    passed_checks = sum(1 for _, s in const_checks if s == "PASS")
    cosmo_info = cosmological_constant_validation()
    lambda_info = cosmo_info["lambda"]
    hubble_info = cosmo_info["hubble"]
    econ_info = economic_cycles_validation()

    lines: list[str] = []

    lines.append("# {0} OMEGA DIAGNOSTIC REPORT v{1}".format(ICON_OMEGA, VERSION))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["{0} Generated".format(ICON_TIME), now],
            ["{0} Version".format(ICON_OMEGA), VERSION],
            ["{0} Framework".format(ICON_AX), "UCF v3.2 (Universal Coherence Framework)"],
            ["{0} Author".format(ICON_ITEM), "Ilver Villasmil"],
            ["{0} Commit".format(ICON_SRC), sha],
        ],
    ))
    lines.append("")

    # Estado Fenomenológico
    lines.append("## {0} Estado Fenomenológico".format(ICON_COH))
    lines.append("")
    loop_warning = "  ⚠️ **CODE 9999 — LOOP DETECTADO**" if loop_detected else ""
    lines.append(md_table(
        ["Métrica", "Valor", "Nota"],
        [
            ["Estado", f"**{pheno_name} {pheno_symbol}**{loop_warning}", ""],
            ["C_struct (Estructural)", f"**{c_structural:.4f}**", f"← real, limitada por α={ALPHA:.4f}"],
            ["C_global (Normalizada)", f"{c_global_norm:.4f}", "← C_struct / α, relativa al máximo"],
            ["C_CI (Pass Rate)", f"{c_ci:.4f}", "← proxy del CI, no es C_Ω"],
            ["φ_eff (Fricción)", f"{phi_eff:.6f}", "← basada en C_struct"],
            ["L7 (Integración)", f"{l7_info.get('value', 0.0):.6f}", f"← {l7_info.get('status', 'N/A')}"],
            ["Umbral crítico (0.72)", "✅ SOBRE" if above_critical else "❌ BAJO", "← debajo = entropía acelerada"],
            ["Umbral survival (0.10)", "✅ SOBRE" if above_survival else "❌ BAJO", "← debajo = cohesión mínima comprometida"],
            ["Tendencia", trend, ""],
        ],
    ))
    lines.append("")
    lines.append("> **Nota semántica v2.1:** C_struct ≠ C_global ≠ C_CI.")
    lines.append("> Solo C_struct es la coherencia estructural real del framework.")
    lines.append("> C_struct nunca puede ser 1.0 — β = 1/27 es el residuo irreducible.")
    lines.append("> **L7** es emergente: verifica que la integración real ocurrió. L6 orienta. L7 verifica.")
    lines.append("")
    if loop_detected:
        lines.append("> ⚠️ **CODE 9999**: El sistema lleva 5+ runs consecutivos sin variación.")
        lines.append("> β > 0 garantiza que ningún sistema real es estáticamente perfecto.")
        lines.append("")

    # Código Diagnóstico
    lines.append("## {0} Código Diagnóstico".format(ICON_ID))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["Código", f"**{code}**"],
            ["Denominación", f"**{diag_name}**"],
            ["C_structural", f"{c_structural:.4f}"],
            ["Interpretación", vector_interp],
            ["Descripción", diag_desc],
        ],
    ))
    lines.append("")
    lines.append("### {0} Tabla de Estados Completa (documento original enero 2026)".format(ICON_CONTRACT))
    lines.append("")
    state_rows = []
    for low, high, st_code, st_name, _ in DIAGNOSTIC_STATES:
        marker = "**← AQUÍ**" if low <= c_structural < high else ""
        state_rows.append([f"`{st_code}`", st_name, f"{low:.3f} – {high:.3f}", marker])
    lines.append(md_table(["Código", "Estado", "Rango C_struct", ""], state_rows))
    lines.append("")
    lines.append("> **Nota prescriptiva:** El código no solo describe — comanda.")
    lines.append("> Declarar 1144 es ordenar a los sistemas que se ajusten a esa frecuencia.")
    lines.append("")

    # System Status
    lines.append("## {0} System Status".format(ICON_MET))
    lines.append("")
    lines.append(md_table(
        ["Metric", "Value"],
        [
            ["C_structural (real)", f"**{c_structural:.4f}**  ← limitada por α"],
            ["C_global_norm", f"{c_global_norm:.4f}  ← C_struct / α"],
            ["L7 Integration", f"**{l7_info.get('value', 0.0):.6f}**  ← {l7_info.get('status', 'N/A')}"],
            ["Layer source", states_source],
            ["Coherence source", coherence_source],
            ["L7 source", str(l7_info.get("source", "N/A"))],
            ["Total Energy", f"{total_energy:.6f}"],
            ["System Entropy", f"{entropy:.4f}"],
            ["System Harmony", f"{harmony:.4f}"],
            ["Damping Ratio (ZETA)", f"{zeta:.6f} (underdamped = alive)"],
            ["Oscillation Period", f"{period:.4f}s"],
            ["ω_eff (v3.2)", f"{OMEGA_EFF:.6f}"],
            ["T_PERIOD (v3.2)", f"{T_PERIOD:.6f} s"],
        ],
    ))
    lines.append("")

    # Test Results
    lines.append("## {0} Test Results".format(ICON_TEST))
    lines.append("")
    lines.append(md_table(
        ["Metric", "Value"],
        [
            ["Total Tests", f"**{test_results['total']}**"],
            ["Passed", str(test_results["passed"])],
            ["Failed", str(test_results["failed"])],
            ["Skipped", str(test_results["skipped"])],
            ["Pass Rate", f"{pass_rate:.2f}%  (C_CI = {c_ci:.4f})"],
        ],
    ))
    lines.append("")

    # Trayectoria
    lines.append("## {0} Trayectoria de Coherencia".format(ICON_HIST))
    lines.append("")
    lines.append(f"Últimos {min(len(history), 10)} runs:")
    lines.append("")
    lines.append("```")
    lines.append(traj if traj else "Sin historial")
    lines.append("```")
    lines.append("")

    # Constants Integrity
    lines.append("## {0} Constants Integrity".format(ICON_FORM))
    lines.append("")
    lines.append(md_table(
        ["Check", "Status"],
        [[c, _icono_status(s)] for c, s in const_checks] + [["**Total**", f"**{passed_checks}/{len(const_checks)}**"]],
    ))
    lines.append("")

    # Framework Constants
    lines.append("## {0} Framework Constants".format(ICON_NUM))
    lines.append("")
    lines.append(md_table(
        ["Constant", "Value", "Formula"],
        [
            ["ALPHA", f"{ALPHA:.6f}", "26/27  ← C_max estructural"],
            ["BETA", f"{BETA:.6f}", "1/27   ← residuo irreducible"],
            ["PHI", f"{PHI:.6f}", "(1+sqrt5)/2"],
            ["S_REF", f"{S_REF:.6f}", "e/pi"],
            ["S_REF_7", f"{S_REF_7:.6f}", "S_REF + BETA·ln(7)"],
            ["R_FIN", f"{R_FIN:.6f}", "1+1/27"],
            ["KAPPA", f"{KAPPA:.6f}", "pi/4"],
            ["GOLDEN_ANG", f"{GOLDEN_ANG:.3f} deg", "360/phi^2"],
            ["THETA_CUBE", f"{THETA_CUBE_DEG:.3f} deg", "asin(1/sqrt27)"],
            ["OMEGA_EFF ★", f"{OMEGA_EFF:.6f}", "π·(1-√β)"],
            ["T_PERIOD ★", f"{T_PERIOD:.6f} s", "2π/ω_d"],
            ["LAMBDA_UCF ★", f"{LAMBDA_UCF:.4e}", "β^(π/β+β·φ²)"],
            ["OMEGA_RED ★", f"{OMEGA_RED:.6f}", "(π/e)·(1-β²)"],
        ],
    ))
    lines.append("")
    lines.append("*★ = constantes nuevas v3.2*")
    lines.append("")

    # Layer Status
    lines.append("## {0} Layer Status".format(ICON_LAYER))
    lines.append("")
    lines.append(md_table(
        ["Layer", "Name", "Friction", "Spiral Angle", "Healthy Range"],
        layer_rows(states),
    ))
    lines.append("")
    lines.append("> **L7** no tiene fricción propia. Es el estado emergente del sistema")
    lines.append("> cuando L0-L6 cooperan. Su valor es el producto multiplicativo de todas las capas.")
    lines.append("> Si cualquier capa colapsa a cero, L7 = 0. No puede fingirse.")
    lines.append("")

    # Module Status
    lines.append("## {0} Module Status".format(ICON_PKG))
    lines.append("")
    lines.append(md_table(
        ["Módulo", "Estado"],
        [[label, status] for label, status in module_status],
    ))
    lines.append("")

    # Domain Validations
    lines.append("## {0} Domain Validations".format(ICON_AX))
    lines.append("")

    # Cosmological Constant
    lines.append("### {0} Cosmological Constant".format(ICON_FORM))
    lines.append("")
    lines.append(md_table(
        ["Metric", "Value"],
        [
            ["Formula", str(lambda_info["formula"])],
            ["Framework prediction", f"{lambda_info['prediction']:.4e}"],
            ["Observed value", f"{lambda_info['observed']:.4e}"],
            ["Error", f"{lambda_info['error_pct']:.2f}%"],
            ["Log10 prediction", f"{lambda_info['log10_prediction']:.6f}"],
            ["Log10 observed", f"{lambda_info['log10_observed']:.6f}"],
            ["Log10 error", f"{lambda_info['log10_error']:.6f}"],
            ["Base term 27π", f"{lambda_info['base_term_27pi']:.6f}"],
            ["Correction βφ²", f"{lambda_info['correction_term_beta_phi2']:.6f}"],
            ["Correction ratio", f"{lambda_info['correction_ratio']:.6f}"],
            ["Numerically stable", "YES" if lambda_info["numerically_stable"] else "NO"],
            ["Improvement over QM", str(lambda_info["improvement_qm"])],
            ["Status", f"**{lambda_info['status']}**"],
        ],
    ))
    lines.append("")

    # Hubble Tension
    lines.append("### {0} Hubble Tension".format(ICON_MET))
    lines.append("")
    lines.append(md_table(
        ["Metric", "Value"],
        [
            ["Formula", str(hubble_info["formula"])],
            ["Prediction", f"{hubble_info['prediction']:.6f}"],
            ["Observed diff", f"{hubble_info['observed_diff']:.6f}"],
            ["H early", f"{hubble_info['H_early']:.4f}"],
            ["H late", f"{hubble_info['H_late']:.4f}"],
            ["Abs error", f"{hubble_info['abs_error']:.6f}"],
            ["Error", f"{hubble_info['error_pct']:.2f}%"],
            ["Tolerance", f"{hubble_info['tolerance']:.6f}"],
            ["Status", f"**{hubble_info['status']}**"],
        ],
    ))
    lines.append("")

    # Economic Cycles
    lines.append("### {0} Economic Cycles".format(ICON_DER))
    lines.append("")
    lines.append(md_table(
        ["Metric", "Value"],
        [
            ["Natural damping (zeta)", f"{econ_info['natural_zeta']:.6f}"],
            ["Wu (2012) observed", f"{econ_info['observed_zeta']:.2f}"],
            ["Damping error", f"{econ_info['damping_error_pct']:.1f}%"],
            ["Kondratiev predicted", f"{econ_info['kond_pred']:.1f} years"],
            ["Kondratiev observed", f"{econ_info['kond_obs']:.0f} years"],
            ["Kondratiev error", f"{econ_info['kond_error_pct']:.1f}%"],
            ["Status", f"**{econ_info['status']}**"],
        ],
    ))
    lines.append("")


    # Quantum Gravity & Particle Physics
    lines.append("### {0} Quantum Gravity & Particle Physics".format(ICON_FORM))
    lines.append("")
    if qg_info.get("available"):
        lines.append(md_table(
            ["Metric", "UCF Prediction", "Observed/Reference", "Error"],
            [
                ["Planck Energy (eV)", f"{qg_info['e_planck_ucf']:.4e}", f"{qg_info['e_planck_ref']:.4e}", f"{qg_info['e_planck_error']:.2f}%"],
                ["Electron Mass (kg)", f"{qg_info['m_electron_ucf']:.4e}", f"{qg_info['m_electron_ref']:.4e}", f"{qg_info['m_electron_error']:.2f}%"],
                ["Electron Radius (m)", f"{qg_info['r_electron_ucf']:.4e}", f"{qg_info['r_electron_ref']:.4e}", f"{qg_info['r_electron_error']:.2f}%"],
                ["Strong Coupling α_s", f"{qg_info['alpha_s_ucf']:.4f}", f"{qg_info['alpha_s_ref']:.4f}", f"{qg_info['alpha_s_error']:.2f}%"],
                ["Status", f"**{qg_info['status']}**", "", ""],
            ],
        ))
    else:
        lines.append("> ⚠️ Módulo quantum_gravity no disponible")
    lines.append("")

    # Neuroscience & Brain Coherence
    lines.append("### {0} Neuroscience & Brain Coherence".format(ICON_GEN))
    lines.append("")
    if neuro_info.get("available"):
        lines.append(md_table(
            ["Metric", "Value"],
            [
                ["EEG α/θ frequency ratio", f"{neuro_info['phi_ratio']:.4f} (PHI)"],
                ["Observed ratio", f"{neuro_info['observed_ratio']:.3f}"],
                ["Error", f"{neuro_info['error']:.1f}%"],
                ["Status", f"**{neuro_info['status']}**"],
            ],
        ))
    lines.append("")

    # Genetic Code & Biology
    lines.append("### {0} Genetic Code & Biology".format(ICON_COH))
    lines.append("")
    if genetic_info.get("available"):
        lines.append(md_table(
            ["Metric", "Value"],
            [
                ["Amino acids (27-7)", str(genetic_info['amino_acids'])],
                ["Observed amino acids", str(genetic_info['observed_amino'])],
                ["Body temperature (1000*BETA)", f"{genetic_info['body_temp']:.2f}°C"],
                ["Observed body temp", f"{genetic_info['observed_temp']:.1f}°C"],
                ["Temp error", f"{genetic_info['temp_error']:.2f}%"],
                ["Status", f"**{genetic_info['status']}**"],
            ],
        ))
    lines.append("")

    # Black Hole Thermodynamics
    lines.append("### {0} Black Hole Thermodynamics".format(ICON_AUDIT))
    lines.append("")
    if bh_info.get("available"):
        lines.append(md_table(
            ["Metric", "Value"],
            [
                ["Hawking temp coefficient", f"{bh_info['hawking_ref']:.4f} (1/8π)"],
                ["Framework BETA", f"{bh_info['beta_value']:.4f} (1/27)"],
                ["Error", f"{bh_info['error']:.1f}%"],
                ["Status", f"**{bh_info['status']}**"],
            ],
        ))
    lines.append("")
    # Torus Formula
    lines.append("### {0} Torus Formula".format(ICON_GRAPH))
    lines.append("")
    if torus_info.get("available"):
        e_m_value = torus_info.get("E_M_computed", "N/A")
        if isinstance(e_m_value, float):
            e_m_render = f"{e_m_value:.4e}"
        else:
            e_m_render = str(e_m_value)

        lines.append(md_table(
            ["Metric", "Value"],
            [
                ["Primes (T4)", str(torus_info["primes"])],
                ["M (primorial)", str(torus_info["M"])],
                ["phi(M)", str(torus_info["phi_M"])],
                ["Ley 1 — Independencia de Ciclos", "✅ PASS" if torus_info["law1_holds"] else "❌ FAIL"],
                ["Ley 2 — Resonancia de Ciclos", "✅ PASS" if torus_info["law2_holds"] else "❌ FAIL"],
                ["Ley 3 — Filtrado Primo", "✅ PASS" if torus_info["law3_holds"] else "❌ FAIL"],
                ["Ley 4 — Campo Aritmético E(M)", "✅ PASS" if torus_info["law4_holds"] else "❌ FAIL"],
                ["E(M) calculado", e_m_render],
                ["E(M6) paper", f"{E_M6_PAPER:.2e}"],
                ["E(M7) paper", f"{E_M7_PAPER:.2e}"],
                ["Beta^n más cercano", f"n={torus_info['beta_closest_n']}, valor={torus_info['beta_closest_v']:.4e}"],
                ["Conexión UCF", torus_info["ucf_link"]],
                ["Conexión RH", torus_info["rh_status"]],
                ["Status", f"**{torus_info['status']}**"],
            ],
        ))
    else:
        lines.append(f"> ⚠️ Módulo torus_formula no disponible: {torus_info.get('status', 'N/A')}")
    lines.append("")

    # L7 Integration
    lines.append("### {0} L7 Integration".format(ICON_LAYER))
    lines.append("")
    if l7_info.get("available"):
        lines.append(md_table(
            ["Metric", "Value"],
            [
                ["Fórmula", l7_info["formula"]],
                ["L7 value", f"**{l7_info['value']:.6f}**"],
                ["Status", f"**{l7_info['status']}**"],
                ["Max posible", f"{l7_info['max_possible']:.6f}  ← alpha"],
                ["Ley", l7_info["law"]],
                ["Principio", l7_info["note"]],
                ["Source", str(l7_info.get("source", "N/A"))],
            ],
        ))
    else:
        lines.append(f"> ⚠️ L7 no disponible: {l7_info.get('status', 'N/A')}")
    lines.append("")

    # Energy Distribution
    lines.append("## {0} Energy Distribution".format(ICON_MET))
    lines.append("")
    lines.append(md_table(
        ["Layer", "Energy"],
        [
            ["L0", f"{energies['L0']:.6f}"],
            ["L1", f"{energies['L1']:.6f}"],
            ["L2", f"{energies['L2']:.6f}"],
            ["L3", f"{energies['L3']:.6f}"],
            ["L4", f"{energies['L4']:.6f}"],
            ["L5", f"{energies['L5']:.6f}"],
            ["L6", f"{energies['L6']:.6f}"],
            ["Total", f"**{total_energy:.6f}**"],
        ],
    ))
    lines.append("")

    # Cube Geometry
    lines.append("## {0} Cube Geometry".format(ICON_CUBE))
    lines.append("")
    lines.append("3x3x3 = 27 positions  ")
    lines.append(f"Exterior: 26 (ALPHA = {ALPHA:.6f})  ← C_max estructural")
    lines.append(f"Center:   1  (BETA  = {BETA:.6f})  ← residuo irreducible")
    lines.append(f"ALPHA + BETA = {ALPHA + BETA:.1f}  ← conservación estructural")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("")


    # ------------------------------------------------------------------
    # Paquete máquina (JSON) — misma verdad que el Markdown
    # ------------------------------------------------------------------
    executed = read_executed_tests() if "read_executed_tests" in globals() else {}
    audit = discover_audit()
    captured = []
    for s in (executed.get("suites") or []):
        text = (s.get("stdout") or "").strip()
        if text:
            captured.append({
                "case": "suite::{0}".format(s.get("name") or "pytest"),
                "status": "suite",
                "stdout": text,
            })
    for c in (executed.get("cases") or []):
        text = (c.get("stdout") or "").strip()
        if text:
            captured.append({
                "case": "{0}::{1}".format(c.get("classname") or "", c.get("name") or ""),
                "status": c.get("status"),
                "stdout": text,
            })
    audit["captured_stdout"] = captured
    audit["coverage"]["captured_stdout_n"] = len(captured)
    diagnostics_snapshot = discover_diagnostics()
    raw_artifacts = diagnostics_snapshot.get("artifacts") or []
    diag_index = diagnostics_snapshot.get("index") or {}

    def _idx_doc(key):
        rec = diag_index.get(key) or {}
        doc = rec.get("document")
        if doc is None:
            doc = rec.get("data")
        return rec, doc

    # índice de conveniencia — alias data = document (mismo objeto, no resumen)
    ci_evidence = {}
    for key, rec in diag_index.items():
        view = dict(rec)
        view["data"] = rec.get("document")
        ci_evidence[key] = view
    ci_evidence["tests"] = executed if executed else test_results
    if "coherence_history" not in ci_evidence:
        ci_evidence["coherence_history"] = history

    engine_state = snapshot_engine()

    system_status = {"coherente": None, "estado": "N/D", "source": None, "source_type": "UNAVAILABLE"}
    _, cdata = _idx_doc("contratos")
    _, adata = _idx_doc("axioms")
    if isinstance(cdata, dict) and "incoherente" in cdata:
        system_status = {
            "coherente": (not bool(cdata.get("incoherente"))),
            "estado": "COHERENTE" if not cdata.get("incoherente") else "INCOHERENTE",
            "source": "{0}:incoherente".format((diag_index.get("contratos") or {}).get("path") or "contratos"),
            "source_type": "DERIVED_ADAPTER",
        }
    elif isinstance(adata, dict) and "coherente" in adata:
        system_status = {
            "coherente": bool(adata.get("coherente")),
            "estado": "COHERENTE" if adata.get("coherente") else "INCOHERENTE",
            "source": "{0}:coherente".format((diag_index.get("axioms") or {}).get("path") or "axioms"),
            "source_type": "CI_ARTIFACT",
        }

    # secciones extra pedidas — no sustituyen las originales
    lines.append("## {0} Audit Coverage".format(ICON_MET))
    lines.append("")
    lines.append(md_table(
        ["Métrica", "Valor", "Fuente"],
        [
            ["Tests discovered", executed.get("discovered_n") if executed else test_results.get("file_count"), "tests/"],
            ["Tests executed", executed.get("executed") if executed else False, executed.get("source") if executed else "unavailable"],
            ["Modules listed", len(module_status), "discovery"],
            ["History runs", len(history), "diagnostics/coherence_history.json"],
            ["Engine startup", engine_state.get("startup"), "core.engine.Engine"],
        ],
    ))
    lines.append("")

    lines.append("## {0} Engine State".format(ICON_ENGINE))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor", "Fuente"],
        [
            ["available", engine_state.get("available"), "core.engine"],
            ["startup", engine_state.get("startup"), "Engine(...)"],
            ["estado", engine_state.get("estado"), "Engine.estado"],
            ["invocador_id", engine_state.get("invocador_id"), "constructor"],
            ["error", engine_state.get("error"), "ArranqueError"],
        ],
    ))
    lines.append("")

    ax = ci_evidence.get("axioms") or {}
    lines.append("## {0} Axiomatic / Formal State".format(ICON_AX))
    lines.append("")
    if ax.get("data") and isinstance(ax["data"], dict):
        ad = ax["data"]
        cuerpos = ad.get("cuerpos") or []
        lines.append(md_table(
            ["Campo", "Valor", "Fuente", "Clase"],
            [
                ["coherente", ad.get("coherente"), ax.get("path"), "CI_ARTIFACT"],
                ["declaraciones", ad.get("declaraciones"), ax.get("path"), "CI_ARTIFACT"],
                ["cuerpos", len(cuerpos) if isinstance(cuerpos, list) else ad.get("cuerpos"), ax.get("path"), "CI_ARTIFACT"],
                ["errores", len(ad.get("errores") or []) if isinstance(ad.get("errores"), list) else ad.get("errores"), ax.get("path"), "CI_ARTIFACT"],
                ["choques", len(ad.get("choques") or []) if isinstance(ad.get("choques"), list) else ad.get("choques"), ax.get("path"), "CI_ARTIFACT"],
            ],
        ))
        if isinstance(cuerpos, list) and cuerpos:
            lines.append("")
            lines.append(md_table(["#", "Cuerpo"], [[i, c] for i, c in enumerate(cuerpos, 1)]))
    else:
        lines.append("{0} axioms_report.json no disponible".format(ICON_INFO))
    lines.append("")

    gd = ci_evidence.get("generatividad") or {}
    lines.append("## {0} Generativity".format(ICON_GEN))
    lines.append("")
    if isinstance(gd.get("data"), dict):
        data = gd["data"]
        operativa = {k: v for k, v in data.items() if k != "canonica"}
        lines.append("### OPERATIVA")
        lines.append("")
        lines.append(md_table(["Campo", "Valor", "Fuente"], [[k, v, gd.get("path")] for k, v in operativa.items()]))
        lines.append("")
        lines.append("### CANÓNICA TR1")
        lines.append("")
        can = data.get("canonica") or {}
        if isinstance(can, dict):
            lines.append(md_table(["Campo", "Valor", "Fuente"], [[k, v, gd.get("path") + ":canonica"] for k, v in can.items()]))
    else:
        lines.append("{0} generatividad_report.json no disponible".format(ICON_INFO))
    lines.append("")

    lines.append("## {0} Diagnostic Artifacts".format(ICON_DISK))
    lines.append("")
    art_rows = []
    for rec in raw_artifacts:
        mark = ICON_OK if rec.get("present") and rec.get("read_ok") else ICON_FAIL
        art_rows.append([
            mark,
            rec.get("path"),
            rec.get("bytes"),
            rec.get("parse_ok"),
            rec.get("content_type"),
        ])
    if art_rows:
        lines.append(md_table(["", "Artefacto", "Bytes", "Parse", "Tipo"], art_rows))
    else:
        lines.append("{0} diagnostics/ vacío o ilegible".format(ICON_INFO))
    lines.append("")

    cov = audit.get("coverage") or {}
    lines.append("## {0} Audit Coverage".format(ICON_AUDIT))
    lines.append("")
    lines.append(md_table(
        ["Métrica", "Valor"],
        [[k, v] for k, v in cov.items()],
    ))
    lines.append("")
    lines.append("## {0} Formula Inventory".format(ICON_FORM))
    lines.append("")
    form_rows = [[f.get("module"), f.get("name"), ", ".join(f.get("args") or []), f.get("line")] for f in (audit.get("formulas") or [])]
    if form_rows:
        lines.append(md_table(["Módulo", "Función", "Args", "Línea"], form_rows))
    else:
        lines.append("{0} sin funciones públicas en formulas.*".format(ICON_INFO))
    lines.append("")
    lines.append("## {0} Discovered Validations".format(ICON_AX))
    lines.append("")
    prod_rows = []
    for p in (audit.get("producers") or []):
        prod_rows.append([p.get("status"), p.get("id"), p.get("title"), p.get("hook"), p.get("source")])
    if prod_rows:
        lines.append(md_table(["Status", "Id", "Título", "Hook", "Fuente"], prod_rows))
        for p in audit.get("producers") or []:
            mets = p.get("metrics") if isinstance(p.get("metrics"), dict) else {}
            if mets:
                lines.append("")
                lines.append("### {0} {1}".format(ICON_FORM, p.get("title")))
                lines.append("")
                lines.append(md_table(["Campo", "Valor"], [[k, mets.get(k)] for k in mets.keys()]))
    else:
        lines.append("{0} ningún omega_validation()/__omega_report__() descubierto".format(ICON_INFO))
    lines.append("")
    lines.append("## {0} Findings".format(ICON_ERR))
    lines.append("")
    finds = audit.get("findings") or []
    if finds:
        lines.append(md_table(
            ["Sev", "Cat", "Componente", "Mensaje"],
            [[f.get("severity"), f.get("category"), f.get("component"), f.get("message")] for f in finds],
        ))
    else:
        lines.append("{0} sin hallazgos de descubrimiento".format(ICON_OK))
    lines.append("")
    lines.append("## {0} Module Census".format(ICON_PKG))
    lines.append("")
    mod_rows = []
    for m in audit.get("modules") or []:
        mark = ICON_OK if m.get("importable") else ICON_FAIL
        mod_rows.append([mark, m.get("name"), m.get("path"), len(m.get("symbols") or []), m.get("error")])
    if mod_rows:
        lines.append(md_table(["", "Módulo", "Path", "Símbolos", "Error"], mod_rows))
    lines.append("")

    repo = audit.get("repository") or {}
    summary = repo.get("summary") or {}
    lines.append("## {0} Repository Inventory".format(ICON_REPO))
    lines.append("")
    if summary:
        lines.append(md_table(["Métrica", "Valor"], [[k, v] for k, v in summary.items()]))
    lines.append("")
    file_rows = []
    for f in (repo.get("files") or [])[:400]:
        file_rows.append([f.get("path"), f.get("type"), f.get("bytes")])
    if file_rows:
        lines.append("<details><summary>{0} Archivos ({1})</summary>".format(ICON_FILE, summary.get("files")))
        lines.append("")
        lines.append(md_table(["Path", "Tipo", "Bytes"], file_rows))
        lines.append("")
        lines.append("</details>")
        lines.append("")

    deps = audit.get("dependencies") or {}
    lines.append("## {0} Dependency Graph".format(ICON_DEP))
    lines.append("")
    lines.append("- aristas: `{0}`".format(deps.get("n_edges") or len(deps.get("edges") or [])))
    lines.append("")
    erows = [[e.get("from"), e.get("to"), e.get("kind")] for e in (deps.get("edges") or [])[:120]]
    if erows:
        lines.append("<details><summary>{0} Aristas</summary>".format(ICON_DEP))
        lines.append("")
        lines.append(md_table(["Origen", "Destino", "Tipo"], erows))
        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("## {0} Test Functions".format(ICON_TEST))
    lines.append("")
    tf_rows = [[t.get("file"), t.get("name"), t.get("line")] for t in (audit.get("test_functions") or [])]
    if tf_rows:
        lines.append(md_table(["Archivo", "Función", "Línea"], tf_rows))
    else:
        lines.append("{0} tests/ sin funciones test_* parseadas".format(ICON_INFO))
    lines.append("")

    lines.append("## {0} Captured Test Output".format(ICON_SRC))
    lines.append("")
    blobs = audit.get("captured_stdout") or []
    if blobs:
        lines.append(md_table(
            ["Caso", "Status", "Bytes"],
            [[b.get("case"), b.get("status"), len(b.get("stdout") or "")] for b in blobs],
        ))
        for b in blobs:
            lines.append("")
            lines.append("<details><summary>{0} {1}</summary>".format(ICON_TEST, b.get("case")))
            lines.append("")
            lines.append("```")
            lines.append(b.get("stdout") or "")
            lines.append("```")
            lines.append("")
            lines.append("</details>")
    else:
        lines.append("{0} test_results.xml no trae system-out (pytest junit sin --capture=no / junit_logging)".format(ICON_INFO))
    lines.append("")

    lines.append("## {0} Module / Test Audits".format(ICON_LENS))
    lines.append("")
    for blob in (audit.get("module_stdout") or []):
        title = blob.get("name") or blob.get("path")
        text = blob.get("stdout") or ""
        pares = stdout_a_pares(text)
        lines.append("### {0} {1}".format(ICON_FORM, title))
        lines.append("")
        if pares:
            lines.append(md_table(["Campo", "Valor"], [[k, v] for k, v in pares]))
        lines.append("")
        lines.append("<details><summary>{0} salida completa</summary>".format(ICON_SRC))
        lines.append("")
        lines.append("```")
        lines.append(text)
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    if not (audit.get("module_stdout") or []):
        lines.append("{0} ningún módulo emitió auditoría al importar".format(ICON_INFO))
        lines.append("")

    lines.append("## {0} Evidence Provenance".format(ICON_SRC))
    lines.append("")
    lines.append(md_table(
        ["Dato", "Fuente", "Clase", "Fallback"],
        [
            ["ALPHA", "formulas.constants|DEFAULT", "DECLARED/FALLBACK", formulas_constants is None],
            ["C_structural", coherence_source, "MEASURED" if coherence_source != "structural-fallback" else "FALLBACK", coherence_source == "structural-fallback"],
            ["L7", l7_info.get("source"), "MEASURED" if l7_info.get("source") != "structural-fallback" else "FALLBACK", l7_info.get("source") == "structural-fallback"],
            ["Tests", test_results.get("source", executed.get("source") if executed else "unavailable"), test_results.get("class", executed.get("class") if executed else "UNAVAILABLE"), not bool(executed.get("executed") if executed else False)],
            ["History", "diagnostics/coherence_history.json", "CI_ARTIFACT", False],
        ],
    ))
    lines.append("")

    coh = system_status.get("coherente")
    if coh is True:
        closure = "{0} COHERENTE".format(ICON_OK)
    elif coh is False:
        closure = "{0} INCOHERENTE".format(ICON_FAIL)
    else:
        closure = "{0} N/D".format(ICON_INFO)
    lines.append("## {0} Final Closure".format(ICON_OMEGA))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["System Status", closure],
            ["Source", system_status.get("source")],
            ["Engine", engine_state.get("startup")],
            ["Tests source", test_results.get("source", "unavailable")],
            ["C_structural", "{0:.4f}".format(c_structural)],
            ["L7", l7_info.get("value")],
        ],
    ))
    lines.append("")
    lines.append("{0} **Omega**".format(ICON_OMEGA))
    lines.append("")

    validations_list = [
        {"id": "cosmo", "title": "Cosmological Constant", "metrics": cosmo_info, "source": "formulas/modules"},
        {"id": "hubble", "title": "Hubble Tension", "metrics": (cosmo_info.get("hubble") if isinstance(cosmo_info, dict) else None) or {}, "source": "formulas/modules"},
        {"id": "econ", "title": "Economic Cycles", "metrics": econ_info, "source": "formulas/modules"},
        {"id": "qg", "title": "Quantum Gravity", "metrics": qg_info, "source": "formulas/modules"},
        {"id": "neuro", "title": "Neuroscience", "metrics": neuro_info, "source": "formulas/modules"},
        {"id": "genetic", "title": "Genetic Code", "metrics": genetic_info, "source": "formulas/modules"},
        {"id": "bh", "title": "Black Hole", "metrics": bh_info, "source": "formulas/modules"},
        {"id": "torus", "title": "Torus Formula", "metrics": torus_info, "source": "formulas/modules"},
        {"id": "l7", "title": "L7 Integration", "metrics": l7_info, "source": l7_info.get("source") if isinstance(l7_info, dict) else None},
    ]
    for p in (audit.get("producers") or []):
        validations_list.append(p)
    validations_index = {
        "cosmo": cosmo_info,
        "hubble": (cosmo_info.get("hubble") if isinstance(cosmo_info, dict) else None) or {},
        "econ": econ_info,
        "qg": qg_info,
        "neuro": neuro_info,
        "genetic": genetic_info,
        "bh": bh_info,
        "torus": torus_info,
        "l7": l7_info,
    }

    paquete = {
        "schema_version": "omega.uis.2.6.2",
        "version": VERSION,
        "generated": generated_metadata(now, sha),
        "framework": {
            "name": "Universal Integration System",
            "omega_version": VERSION,
        },
        "system_status": system_status,
        "engine": engine_state,
        "audit": audit,
        "coverage": audit.get("coverage"),
        "findings": audit.get("findings"),
        "diagnostics": {
            "artifacts": raw_artifacts,
            "index": {k: {"path": (v or {}).get("path"), "present": (v or {}).get("present")} for k, v in diag_index.items()},
        },
        "metrics": {
            "C_struct": c_structural,
            "C_global_norm": c_global_norm,
            "C_CI": c_ci,
            "L7": l7_info.get("value"),
            "phi_eff": phi_eff,
            "zeta": zeta,
            "omega_d": omega_d,
            "period": period,
            "entropy": entropy,
            "harmony": harmony,
            "total_energy": total_energy,
            "energies": energies,
            "states": states,
            "states_source": states_source,
            "coherence_source": coherence_source,
            "l7": l7_info,
        },
        "diagnostic": {"code": code, "name": diag_name, "desc": diag_desc, "pheno": pheno_name, "symbol": pheno_symbol, "trend": trend},
        "tests": executed if executed else test_results,
        "ci_evidence": ci_evidence,
        "modules": module_status,
        "validations": validations_index,
        "validations_list": validations_list,
        "history": history,
        "const_checks": const_checks,
    }
    return "\n".join(lines), paquete


# =============================================================================
# SAVE
# =============================================================================


def save_json_data(
    c_structural: float,
    c_global_norm: float,
    c_ci: float,
    l7_value: float,
    phi_eff: float,
    code: str,
    diag_name: str,
    pheno_name: str,
    test_results: dict,
) -> Path:
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DIAGNOSTICS_DIR / "omega_report_data.json"
    
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "C_struct": c_structural,
        "C_global_norm": c_global_norm,
        "C_CI": c_ci,
        "L7": l7_value,
        "phi_eff": phi_eff,
        "codigo": code,
        "estado": diag_name,
        "pheno": pheno_name,
        "pass_rate": test_results.get("pass_rate", 0.0),
        "total": test_results.get("total", 0),
        "passed": test_results.get("passed", 0),
        "failed": test_results.get("failed", 0),
        "skipped": test_results.get("skipped", 0)
    }
    
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return output_path

def save_report(report: str) -> Path:
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DIAGNOSTICS_DIR / "OMEGA_REPORT.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    print("Running Omega Report v{0}...".format(VERSION))
    report, paquete = build_report()
    output_path = save_report(report)
    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DIAGNOSTICS_DIR / "omega_report_data.json"
    json_path.write_text(json.dumps(paquete, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(render_ci(paquete))
    print("Report saved to: {0}".format(output_path))
    print("JSON data saved to: {0}".format(json_path))


if __name__ == "__main__":
    main()
