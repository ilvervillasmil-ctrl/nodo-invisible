#!/usr/bin/env python3
"""
OMEGA REPORT — Extreme Audit Renderer
Universal Integration System

Contrato:
  1. Descubrir / pedir paquete estructurado.
  2. Serializar el MISMO paquete a JSON.
  3. Renderizar el MISMO paquete a Markdown.
  4. Emitir un resumen compacto a stdout CI.
  Nunca: Markdown → regex → JSON.

Omega no inventa el estado. Si Engine.paquete_omega() existe, esa es la autoridad.
Si no, Omega construye un paquete de descubrimiento local y lo etiqueta como tal.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import math
import os
import platform
import sys
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =============================================================================
# PATH
# =============================================================================

CURRENT_FILE = Path(__file__).resolve()
DIAGNOSTICS_DIR = CURRENT_FILE.parent
REPO_ROOT = DIAGNOSTICS_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OMEGA_VERSION = "3.0-extreme-audit"
SCHEMA_VERSION = "omega.paquete.1"

SKIP_DIR_NAMES = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".venv", "venv", "node_modules", ".tox",
}
SECRET_MARKERS = (
    "TOKEN", "SECRET", "PASSWORD", "PASSWD", "APIKEY", "API_KEY",
    "PRIVATE_KEY", "CREDENTIAL", "AWS_SECRET", "AUTHORIZATION",
)

ICON_OK = "✅"
ICON_FAIL = "❌"
ICON_WARN = "⚠️"
ICON_INFO = "ℹ️"
ICON_ITEM = "🔹"
ICON_ENGINE = "🧩"
ICON_REPO = "📦"
ICON_MOD = "📜"
ICON_VAR = "🔢"
ICON_TEST = "🧪"
ICON_LAYER = "📶"
ICON_FIND = "🚨"
ICON_HIST = "❤️"
ICON_GRAPH = "🔗"
ICON_FORM = "📐"
ICON_LOCK = "🔐"
ICON_SRC = "📡"
ICON_COV = "📊"
ICON_DOM = "📚"
ICON_OMEGA = "Ω"

W = "════════════════════════════════════════════"
S = "────────────────────────────────────────────"


# =============================================================================
# FINDINGS
# =============================================================================

FINDINGS: list[dict[str, Any]] = []


def finding(
    severity: str,
    category: str,
    component: str,
    message: str,
    source: str = "omega",
    evidence: Any = None,
) -> None:
    entry = {
        "severity": severity,
        "category": category,
        "component": component,
        "source": source,
        "message": message,
    }
    if evidence is not None:
        entry["evidence"] = _safe(evidence)
    FINDINGS.append(entry)


def pv(value: Any, source: str, source_type: str, measured: bool, fallback: bool = False, raw: Any = None) -> dict[str, Any]:
    return {
        "value": value,
        "raw": raw if raw is not None else value,
        "source": source,
        "source_type": source_type,
        "measured": measured,
        "fallback": fallback,
    }


# =============================================================================
# SAFE HELPERS — nunca silencian
# =============================================================================

def _is_secret_name(name: str) -> bool:
    up = name.upper()
    return any(m in up for m in SECRET_MARKERS)


def _safe(value: Any, name: str = "") -> Any:
    if _is_secret_name(name):
        return "[REDACTED]"
    if value is None or isinstance(value, (bool, int, float, str)):
        if isinstance(value, str) and len(value) > 4000:
            return value[:4000] + "…"
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return [_safe(x) for x in list(value)[:200]]
    if isinstance(value, dict):
        return {str(k): _safe(v, str(k)) for k, v in list(value.items())[:200]}
    try:
        json.dumps(value, default=str)
        return value
    except Exception:
        return {"type": type(value).__name__, "repr": repr(value)[:300]}


def try_import(module_name: str) -> dict[str, Any]:
    try:
        mod = importlib.import_module(module_name)
        return {"success": True, "module": mod, "error_type": None, "error_message": None}
    except Exception as e:
        finding("ERROR", "module_import", module_name, "{0}: {1}".format(type(e).__name__, e))
        return {
            "success": False,
            "module": None,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }


# =============================================================================
# STATIC INVENTORY
# =============================================================================

def _iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        base = Path(dirpath)
        for name in filenames:
            out.append(base / name)
    return out


def _sha256(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        finding("WARNING", "hash", str(path), str(e))
        return None


def _ext_bucket(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".py":
        return "python"
    if ext == ".md":
        return "markdown"
    if ext == ".json":
        return "json"
    if ext in {".yml", ".yaml"}:
        return "yaml"
    if ext == ".toml":
        return "toml"
    if ext == ".txt":
        return "txt"
    if ext in {".so", ".bin", ".exe", ".dll", ".dylib", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}:
        return "binary"
    return "other"


def _parse_python(path: Path) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "path": str(path.relative_to(REPO_ROOT)),
        "lines": 0,
        "classes": [],
        "functions": [],
        "public_assigns": [],
        "imports": [],
        "parse_ok": False,
        "parse_error": None,
    }
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        rec["parse_error"] = str(e)
        finding("ERROR", "read", rec["path"], str(e))
        return rec
    rec["lines"] = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
    try:
        tree = ast.parse(text)
        rec["parse_ok"] = True
    except SyntaxError as e:
        rec["parse_error"] = "SyntaxError: {0}".format(e)
        finding("ERROR", "parse", rec["path"], rec["parse_error"])
        return rec
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                rec["imports"].append({"kind": "import", "name": a.name})
        elif isinstance(node, ast.ImportFrom):
            rec["imports"].append({
                "kind": "from",
                "module": node.module,
                "names": [a.name for a in node.names],
            })
        elif isinstance(node, ast.ClassDef):
            rec["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "bases": [ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "?") for b in node.bases],
                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")],
                "doc": ast.get_docstring(node) or "",
            })
        elif isinstance(node, ast.FunctionDef):
            rec["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "args": [a.arg for a in node.args.args],
                "public": not node.name.startswith("_"),
                "doc": (ast.get_docstring(node) or "")[:240],
            })
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and not t.id.startswith("_"):
                    rec["public_assigns"].append({"name": t.id, "line": node.lineno})
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if not node.target.id.startswith("_"):
                rec["public_assigns"].append({"name": node.target.id, "line": node.lineno})
    return rec


def build_repository_inventory() -> dict[str, Any]:
    files = _iter_files(REPO_ROOT)
    summary = {
        "files": 0,
        "directories": 0,
        "python": 0,
        "markdown": 0,
        "json": 0,
        "yaml": 0,
        "toml": 0,
        "txt": 0,
        "binary": 0,
        "other": 0,
        "bytes": 0,
        "hashed": 0,
        "unreadable": 0,
    }
    dirs = set()
    file_rows: list[dict[str, Any]] = []
    python_rows: list[dict[str, Any]] = []
    for path in files:
        rel = str(path.relative_to(REPO_ROOT))
        dirs.add(str(path.parent.relative_to(REPO_ROOT)))
        bucket = _ext_bucket(path)
        try:
            size = path.stat().st_size
        except Exception:
            size = 0
            summary["unreadable"] += 1
        summary["files"] += 1
        summary["bytes"] += size
        summary[bucket] = summary.get(bucket, 0) + 1
        digest = None
        if bucket in {"python", "json", "yaml"} or path.parts[0] in {"core", "formulas", "layers", "diagnostics", "tests"}:
            digest = _sha256(path)
            if digest:
                summary["hashed"] += 1
        row = {
            "path": rel,
            "type": bucket,
            "bytes": size,
            "sha256": digest,
        }
        file_rows.append(row)
        if bucket == "python":
            python_rows.append(_parse_python(path))
    summary["directories"] = len(dirs)
    return {
        "summary": summary,
        "files": file_rows,
        "directories": sorted(dirs),
        "python": python_rows,
    }


def module_name_from_path(rel: str) -> str | None:
    if not rel.endswith(".py"):
        return None
    parts = Path(rel).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return None
    return ".".join(parts)


def collect_public_symbols(mod: Any, module_name: str) -> list[dict[str, Any]]:
    symbols: list[dict[str, Any]] = []
    names = [n for n in dir(mod) if not n.startswith("_")]
    for name in names:
        try:
            val = getattr(mod, name)
        except Exception as e:
            finding("WARNING", "getattr", "{0}.{1}".format(module_name, name), str(e))
            continue
        kind = type(val).__name__
        if callable(val) and not isinstance(val, type):
            category = "function"
            shown = getattr(val, "__name__", name)
        elif isinstance(val, type):
            category = "class"
            shown = name
        else:
            category = "variable"
            shown = "[REDACTED]" if _is_secret_name(name) else _safe(val, name)
        symbols.append({
            "name": name,
            "module": module_name,
            "category": category,
            "type": kind,
            "value": shown,
            "redacted": _is_secret_name(name),
        })
    return symbols


def build_module_census(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    census: list[dict[str, Any]] = []
    for py in inventory.get("python") or []:
        rel = py.get("path") or ""
        name = module_name_from_path(rel)
        if not name:
            continue
        imported = try_import(name)
        entry = {
            "name": name,
            "path": rel,
            "importable": imported["success"],
            "import_error_type": imported["error_type"],
            "import_error": imported["error_message"],
            "static_functions": py.get("functions") or [],
            "static_classes": py.get("classes") or [],
            "static_assigns": py.get("public_assigns") or [],
            "static_imports": py.get("imports") or [],
            "lines": py.get("lines") or 0,
            "symbols": [],
        }
        if imported["success"] and imported["module"] is not None:
            entry["docstring"] = (imported["module"].__doc__ or "")[:400]
            entry["symbols"] = collect_public_symbols(imported["module"], name)
        census.append(entry)
    return census


def build_dependency_graph(census: list[dict[str, Any]]) -> dict[str, Any]:
    internal = {c["name"] for c in census}
    internal_roots = {n.split(".")[0] for n in internal}
    edges: list[dict[str, Any]] = []
    unresolved: list[str] = []
    stdlib_hint = set(getattr(sys, "stdlib_module_names", set()))
    for c in census:
        src = c["name"]
        for imp in c.get("static_imports") or []:
            target = imp.get("name") if imp.get("kind") == "import" else imp.get("module")
            if not target:
                continue
            root = target.split(".")[0]
            if root in internal or target in internal or root in internal_roots:
                kind = "internal"
                resolved = True
            elif root in stdlib_hint:
                kind = "stdlib"
                resolved = True
            else:
                kind = "third-party"
                resolved = root in sys.modules or True
            edges.append({"from": src, "to": target, "kind": kind, "resolved": resolved})
    return {
        "nodes": sorted(internal),
        "edges": edges,
        "unresolved": unresolved,
        "cycles": [],
    }


# =============================================================================
# ENGINE PACKAGE
# =============================================================================

def try_engine_package() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    state = {
        "available": False,
        "class": None,
        "estado": None,
        "error": None,
        "paquete_from_engine": False,
    }
    imported = try_import("core.engine")
    if not imported["success"]:
        state["error"] = imported["error_message"]
        return None, state
    mod = imported["module"]
    engine_cls = None
    for cand in ("Engine", "OmegaEngine"):
        if hasattr(mod, cand):
            engine_cls = getattr(mod, cand)
            state["class"] = cand
            break
    if engine_cls is None:
        state["error"] = "no Engine/OmegaEngine"
        return None, state
    try:
        try:
            eng = engine_cls(Path("modules"), invocador_id="omega", strict=True)
        except TypeError:
            try:
                eng = engine_cls()
            except Exception:
                eng = engine_cls(invocador_id="omega")
    except Exception as e:
        state["error"] = "{0}: {1}".format(type(e).__name__, e)
        finding("ERROR", "engine_start", "core.engine", state["error"])
        return None, state
    state["available"] = True
    state["estado"] = getattr(eng, "estado", None)
    state["invocador_id"] = getattr(eng, "invocador_id", None)
    state["errores_arranque"] = list(getattr(eng, "errores_arranque", []) or [])
    attrs = {}
    for name in dir(eng):
        if name.startswith("_"):
            continue
        try:
            val = getattr(eng, name)
        except Exception:
            continue
        if callable(val):
            continue
        attrs[name] = _safe(val, name)
    state["public_attrs"] = attrs
    if hasattr(eng, "paquete_omega") and callable(eng.paquete_omega):
        try:
            pkg = eng.paquete_omega()
            if isinstance(pkg, dict):
                state["paquete_from_engine"] = True
                return pkg, state
        except Exception as e:
            finding("ERROR", "paquete_omega", "core.engine", str(e))
    return None, state


# =============================================================================
# TESTS / HISTORY — solo artefactos reales
# =============================================================================

def read_test_results() -> dict[str, Any]:
    xml_path = DIAGNOSTICS_DIR / "test_results.xml"
    static_files = []
    tests_dir = REPO_ROOT / "tests"
    if tests_dir.exists():
        static_files = [str(p.relative_to(REPO_ROOT)) for p in tests_dir.rglob("test_*.py")]
    discovered = {
        "files": static_files,
        "n_files": len(static_files),
    }
    if not xml_path.exists():
        finding("WARNING", "tests", "diagnostics/test_results.xml", "artefacto ausente")
        return {
            "source": "unavailable",
            "executed": False,
            "discovered": discovered,
            "total": None,
            "passed": None,
            "failures": None,
            "errors": None,
            "failed": None,
            "skipped": None,
            "rate": None,
            "suites": [],
            "cases": [],
        }
    try:
        root = ET.parse(xml_path).getroot()
    except Exception as e:
        finding("ERROR", "tests", "diagnostics/test_results.xml", str(e))
        return {
            "source": "unavailable",
            "executed": False,
            "discovered": discovered,
            "error": str(e),
        }
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = failures = errors = skipped = 0
    suite_rows = []
    cases = []
    for s in suites:
        t = int(s.get("tests", 0) or 0)
        f = int(s.get("failures", 0) or 0)
        e = int(s.get("errors", 0) or 0)
        k = int(s.get("skipped", 0) or 0)
        total += t
        failures += f
        errors += e
        skipped += k
        suite_rows.append({
            "name": s.get("name"),
            "tests": t,
            "failures": f,
            "errors": e,
            "skipped": k,
            "time": s.get("time"),
        })
        for tc in s.iter("testcase"):
            status = "passed"
            detail = None
            if tc.find("failure") is not None:
                status = "failure"
                detail = (tc.find("failure").get("message") or "")[:300]
            elif tc.find("error") is not None:
                status = "error"
                detail = (tc.find("error").get("message") or "")[:300]
            elif tc.find("skipped") is not None:
                status = "skipped"
            cases.append({
                "classname": tc.get("classname"),
                "name": tc.get("name"),
                "time": tc.get("time"),
                "status": status,
                "detail": detail,
            })
    failed = failures + errors
    passed = total - failed - skipped
    rate = (passed / total * 100.0) if total else None
    return {
        "source": "diagnostics/test_results.xml",
        "executed": True,
        "discovered": discovered,
        "total": total,
        "passed": passed,
        "failures": failures,
        "errors": errors,
        "failed": failed,
        "skipped": skipped,
        "rate": rate,
        "suites": suite_rows,
        "cases": cases,
    }


def read_coherence_history() -> list[dict[str, Any]]:
    path = DIAGNOSTICS_DIR / "coherence_history.json"
    if not path.exists():
        finding("INFO", "history", "diagnostics/coherence_history.json", "ausente")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:
        finding("ERROR", "history", "diagnostics/coherence_history.json", str(e))
        return []


def discover_artifacts() -> dict[str, Any]:
    names = [
        "test_results.xml",
        "coherence_history.json",
        "axioms_report.json",
        "generatividad_report.json",
        "contratos_report.json",
        "evaluaciones.json",
        "OMEGA_REPORT.md",
        "omega_report_data.json",
    ]
    items = []
    for name in names:
        p = DIAGNOSTICS_DIR / name
        items.append({
            "name": name,
            "present": p.exists(),
            "bytes": p.stat().st_size if p.exists() else None,
        })
    return {"items": items, "present": sum(1 for i in items if i["present"]), "missing": sum(1 for i in items if not i["present"])}


# =============================================================================
# LAYERS / METRICS — sin fingir medición
# =============================================================================

def discover_layers() -> list[dict[str, Any]]:
    layers_dir = REPO_ROOT / "layers"
    found: list[dict[str, Any]] = []
    if not layers_dir.exists():
        finding("INFO", "layers", "layers/", "directorio ausente")
        return found
    for path in sorted(layers_dir.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        rel = str(path.relative_to(REPO_ROOT))
        name = module_name_from_path(rel)
        entry = {
            "id": path.stem,
            "path": rel,
            "module": name,
            "contract": None,
            "activation_raw": None,
            "friction_raw": None,
            "source": rel,
            "source_type": "repository",
            "measured": False,
        }
        if not name:
            found.append(entry)
            continue
        imported = try_import(name)
        if not imported["success"]:
            entry["import_error"] = imported["error_message"]
            found.append(entry)
            continue
        mod = imported["module"]
        contract = None
        for attr in ("__omega__", "OMEGA_LAYER", "LAYER_ID"):
            if hasattr(mod, attr):
                contract = attr
                entry["contract"] = attr
                meta = getattr(mod, attr)
                if isinstance(meta, dict):
                    entry.update({k: _safe(v, k) for k, v in meta.items()})
                else:
                    entry["contract_value"] = _safe(meta)
        for inst_name in dir(mod):
            obj = getattr(mod, inst_name, None)
            if isinstance(obj, type):
                if hasattr(obj, "describe") or hasattr(obj, "report") or hasattr(obj, "__omega__"):
                    entry["type"] = obj.__name__
                    contract = contract or obj.__name__
        entry["measured"] = contract is not None
        if contract is None:
            finding(
                "WARNING",
                "layers",
                name,
                "módulo de layers/ sin contrato explícito (__omega__/describe/report)",
            )
        found.append(entry)
    return found


def collect_declared_constants() -> list[dict[str, Any]]:
    imported = try_import("formulas.constants")
    if not imported["success"]:
        finding("ERROR", "constants", "formulas.constants", imported["error_message"] or "no importable")
        return []
    mod = imported["module"]
    rows = []
    for name in dir(mod):
        if name.startswith("_"):
            continue
        try:
            val = getattr(mod, name)
        except Exception as e:
            finding("WARNING", "constants", name, str(e))
            continue
        if callable(val):
            continue
        rows.append({
            "name": name,
            "value": "[REDACTED]" if _is_secret_name(name) else _safe(val, name),
            "type": type(val).__name__,
            "source": "formulas.constants.{0}".format(name),
            "source_type": "repository",
            "class": "DECLARED",
            "measured": True,
            "fallback": False,
            "redacted": _is_secret_name(name),
        })
    return rows


def collect_domain_validations() -> list[dict[str, Any]]:
    """
    Productores dinámicos: cualquier módulo formulas.* o layers.*
    que exponga omega_validation() / __omega_report__().
    El renderer no conoce cosmología ni toroide.
    """
    reports: list[dict[str, Any]] = []
    roots = []
    for folder in ("formulas", "layers"):
        d = REPO_ROOT / folder
        if d.exists():
            roots.append(d)
    seen = set()
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if path.name == "__init__.py":
                continue
            rel = str(path.relative_to(REPO_ROOT))
            name = module_name_from_path(rel)
            if not name or name in seen:
                continue
            seen.add(name)
            imported = try_import(name)
            if not imported["success"]:
                continue
            mod = imported["module"]
            producer = None
            for attr in ("omega_validation", "__omega_report__", "omega_report"):
                if hasattr(mod, attr) and callable(getattr(mod, attr)):
                    producer = getattr(mod, attr)
                    break
            if producer is None:
                continue
            try:
                payload = producer()
            except Exception as e:
                finding("ERROR", "validation", name, "{0}: {1}".format(type(e).__name__, e))
                reports.append({
                    "id": name,
                    "title": name,
                    "status": "ERROR",
                    "source": name,
                    "findings": [{"message": str(e)}],
                })
                continue
            if isinstance(payload, dict):
                payload.setdefault("id", name)
                payload.setdefault("title", name)
                payload.setdefault("source", name)
                reports.append(payload)
            else:
                reports.append({
                    "id": name,
                    "title": name,
                    "status": "INFO",
                    "source": name,
                    "metrics": {"value": _safe(payload)},
                })
    return reports


# =============================================================================
# PACKAGE
# =============================================================================

def build_paquete() -> dict[str, Any]:
    FINDINGS.clear()
    engine_pkg, engine_state = try_engine_package()
    inventory = build_repository_inventory()
    modules = build_module_census(inventory)
    symbols = []
    for m in modules:
        symbols.extend(m.get("symbols") or [])
    variables = [s for s in symbols if s.get("category") == "variable"]
    layers = discover_layers()
    tests = read_test_results()
    history = read_coherence_history()
    artifacts = discover_artifacts()
    constants = collect_declared_constants()
    validations = collect_domain_validations()
    deps = build_dependency_graph(modules)

    var_stats = {
        "total_public_symbols": len(symbols),
        "variables": len(variables),
        "functions": sum(1 for s in symbols if s.get("category") == "function"),
        "classes": sum(1 for s in symbols if s.get("category") == "class"),
        "redacted": sum(1 for s in symbols if s.get("redacted")),
        "numeric": sum(1 for s in variables if isinstance(s.get("value"), (int, float))),
        "boolean": sum(1 for s in variables if isinstance(s.get("value"), bool)),
        "string": sum(1 for s in variables if isinstance(s.get("value"), str) and not s.get("redacted")),
    }

    coverage = {
        "python_files_discovered": inventory["summary"].get("python", 0),
        "python_files_parsed": sum(1 for p in inventory.get("python") or [] if p.get("parse_ok")),
        "modules_importable": sum(1 for m in modules if m.get("importable")),
        "modules_failed_import": sum(1 for m in modules if not m.get("importable")),
        "public_symbols_discovered": len(symbols),
        "public_symbols_rendered": len(symbols),
        "diagnostic_artifacts_read": artifacts["present"],
        "diagnostic_artifacts_missing": artifacts["missing"],
        "layers_discovered": len(layers),
        "validations_discovered": len(validations),
        "engine_paquete": engine_state.get("paquete_from_engine", False),
    }

    generated = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "omega_version": OMEGA_VERSION,
        "schema_version": SCHEMA_VERSION,
        "sha": (os.environ.get("GITHUB_SHA") or "local")[:12],
        "ref": os.environ.get("GITHUB_REF") or "",
        "run_id": os.environ.get("GITHUB_RUN_ID") or "",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repository": str(REPO_ROOT.name),
    }

    local = {
        "schema_version": SCHEMA_VERSION,
        "generated": generated,
        "engine": engine_state,
        "repository": inventory,
        "modules": modules,
        "symbols": {"items": symbols, "stats": var_stats},
        "variables": {"items": variables, "stats": var_stats},
        "constants": constants,
        "layers": layers,
        "tests": tests,
        "coherence_history": history,
        "validations": validations,
        "dependencies": deps,
        "artifacts": artifacts,
        "coverage": coverage,
        "findings": list(FINDINGS),
    }

    if engine_pkg:
        merged = dict(engine_pkg)
        merged.setdefault("schema_version", SCHEMA_VERSION)
        merged.setdefault("generated", generated)
        for key, val in local.items():
            if key not in merged:
                merged[key] = val
        merged["omega_discovery"] = {
            "used": True,
            "note": "campos locales añadidos solo si Engine no los entregó",
        }
        merged["findings"] = list(FINDINGS) + list(merged.get("findings") or [])
        return merged
    local["authority"] = "omega-discovery"
    local["omega_discovery"] = {
        "used": True,
        "note": "Engine.paquete_omega() no disponible; paquete construido por descubrimiento local",
    }
    return local


# =============================================================================
# RENDER — formas, no semánticas
# =============================================================================

def md_table(headers: list[str], rows: list[list[str]]) -> str:
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join([line1, line2] + body)


def _icon_status(status: Any) -> str:
    s = str(status or "").upper()
    if s in {"PASS", "OK", "TRUE", "COHERENTE", "INTEGRATED", "OPERATIVO", "STABLE", "IMPROVEMENT"}:
        return ICON_OK
    if s in {"FAIL", "ERROR", "FALSE", "INCOHERENTE", "COLLAPSED", "REGRESSION"}:
        return ICON_FAIL
    if s in {"WARN", "WARNING", "REVIEW", "UNAVAILABLE"}:
        return ICON_WARN
    return ICON_ITEM


def _fmt(value: Any) -> str:
    if value is None:
        return "N/D"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        if abs(value) >= 1e6 or (abs(value) < 1e-4 and value != 0):
            return "{0:.4e}".format(value)
        return "{0:.6f}".format(value)
    return str(value)


def render_unknown(key: str, value: Any, lines: list[str], depth: int = 0) -> None:
    indent = "  " * depth
    if value is None or isinstance(value, (bool, int, float, str)):
        lines.append("{0}- {1} {2}: `{3}`".format(indent, ICON_ITEM, key, _fmt(value)))
        return
    if isinstance(value, list):
        if not value:
            lines.append("{0}- {1} {2}: `[]`".format(indent, ICON_ITEM, key))
            return
        if all(isinstance(x, dict) for x in value):
            keys: list[str] = []
            for x in value:
                for k in x.keys():
                    if k not in keys:
                        keys.append(str(k))
            show = keys[:6]
            rows = []
            for x in value[:40]:
                rows.append([_fmt(x.get(k))[:48] for k in show])
            lines.append("{0}- {1} {2} ({3})".format(indent, ICON_ITEM, key, len(value)))
            lines.append(md_table(show, rows))
            if len(value) > 40:
                lines.append("{0}  {1} … {2} más".format(indent, ICON_INFO, len(value) - 40))
            return
        if all(not isinstance(x, (dict, list)) for x in value):
            lines.append("{0}- {1} {2} ({3})".format(indent, ICON_ITEM, key, len(value)))
            for i, x in enumerate(value[:80], 1):
                lines.append("{0}  {1:>3}. {2}".format(indent, i, _fmt(x)))
            return
        lines.append("{0}- {1} {2} ({3})".format(indent, ICON_ITEM, key, len(value)))
        for i, x in enumerate(value[:20], 1):
            render_unknown("#{0}".format(i), x, lines, depth + 1)
        return
    if isinstance(value, dict):
        lines.append("{0}- {1} **{2}**".format(indent, ICON_ITEM, key))
        for k, v in list(value.items())[:40]:
            render_unknown(str(k), v, lines, depth + 1)
        return
    lines.append("{0}- {1} {2}: `{3}`".format(indent, ICON_ITEM, key, _fmt(_safe(value))))


def render_markdown(pkg: dict[str, Any]) -> str:
    lines: list[str] = []
    gen = pkg.get("generated") or {}
    eng = pkg.get("engine") or {}
    cov = pkg.get("coverage") or {}
    tests = pkg.get("tests") or {}
    findings = pkg.get("findings") or []
    layers = pkg.get("layers") or []
    modules = pkg.get("modules") or []
    constants = pkg.get("constants") or []
    validations = pkg.get("validations") or []
    history = pkg.get("coherence_history") or []
    repo = pkg.get("repository") or {}
    summary = repo.get("summary") or {}
    artifacts = pkg.get("artifacts") or {}
    deps = pkg.get("dependencies") or {}
    symbols = (pkg.get("symbols") or {}).get("items") or []
    stats = (pkg.get("symbols") or {}).get("stats") or {}

    errors_n = sum(1 for f in findings if str(f.get("severity", "")).upper() == "ERROR")
    warns_n = sum(1 for f in findings if str(f.get("severity", "")).upper() == "WARNING")
    coherent = errors_n == 0 and bool(eng.get("available") or pkg.get("authority") == "omega-discovery")

    lines.append("# {0} OMEGA DIAGNOSTIC REPORT".format(ICON_OMEGA))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["{0} Generated".format(ICON_INFO), _fmt(gen.get("utc"))],
            ["{0} Omega".format(ICON_OMEGA), _fmt(gen.get("omega_version"))],
            ["{0} Schema".format(ICON_MOD), _fmt(pkg.get("schema_version"))],
            ["{0} SHA".format(ICON_SRC), _fmt(gen.get("sha"))],
            ["{0} Ref".format(ICON_SRC), _fmt(gen.get("ref"))],
            ["{0} Python".format(ICON_ITEM), _fmt(gen.get("python"))],
            ["{0} Platform".format(ICON_ITEM), _fmt(gen.get("platform"))],
            ["{0} Repository".format(ICON_REPO), _fmt(gen.get("repository"))],
            ["{0} Authority".format(ICON_ENGINE), "Engine.paquete_omega" if (eng.get("paquete_from_engine")) else "omega-discovery"],
        ],
    ))
    lines.append("")

    lines.append("## {0} Executive Status".format(ICON_HIST))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["{0} Cierre".format(ICON_OK if coherent else ICON_FAIL), "SYSTEM COHERENT" if coherent else "SYSTEM INCOHERENT"],
            ["{0} Engine".format(ICON_ENGINE), _fmt(eng.get("estado") or ("disponible" if eng.get("available") else "N/D"))],
            ["{0} Tests ejecutados".format(ICON_TEST), _fmt(tests.get("executed"))],
            ["{0} Passed".format(ICON_OK), _fmt(tests.get("passed"))],
            ["{0} Failed".format(ICON_FAIL), _fmt(tests.get("failed"))],
            ["{0} Findings error".format(ICON_FIND), str(errors_n)],
            ["{0} Findings warn".format(ICON_WARN), str(warns_n)],
        ],
    ))
    lines.append("")

    lines.append("## {0} Audit Coverage".format(ICON_COV))
    lines.append("")
    lines.append(md_table(
        ["Métrica", "Valor"],
        [[k, _fmt(v)] for k, v in cov.items()],
    ))
    lines.append("")

    lines.append("## {0} Repository Inventory".format(ICON_REPO))
    lines.append("")
    lines.append(md_table(
        ["Métrica", "Valor"],
        [[k, _fmt(v)] for k, v in summary.items()],
    ))
    lines.append("")
    lines.append("<details><summary>{0} Archivos ({1})</summary>".format(ICON_ITEM, summary.get("files", 0)))
    lines.append("")
    file_rows = []
    for f in (repo.get("files") or [])[:300]:
        file_rows.append([
            str(f.get("path", ""))[:60],
            str(f.get("type", "")),
            str(f.get("bytes", "")),
            str(f.get("sha256") or "")[:12],
        ])
    if file_rows:
        lines.append(md_table(["Path", "Tipo", "Bytes", "SHA256"], file_rows))
    lines.append("")
    lines.append("</details>")
    lines.append("")

    lines.append("## {0} Engine State".format(ICON_ENGINE))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["available", _fmt(eng.get("available"))],
            ["class", _fmt(eng.get("class"))],
            ["estado", _fmt(eng.get("estado"))],
            ["invocador_id", _fmt(eng.get("invocador_id"))],
            ["paquete_from_engine", _fmt(eng.get("paquete_from_engine"))],
            ["error", _fmt(eng.get("error"))],
        ],
    ))
    if eng.get("public_attrs"):
        lines.append("")
        lines.append("<details><summary>{0} Atributos públicos del Engine</summary>".format(ICON_ITEM))
        lines.append("")
        render_unknown("public_attrs", eng.get("public_attrs"), lines)
        lines.append("")
        lines.append("</details>")
    lines.append("")

    lines.append("## {0} Python Module Census".format(ICON_MOD))
    lines.append("")
    mod_rows = []
    for m in modules:
        st = ICON_OK if m.get("importable") else ICON_FAIL
        mod_rows.append([
            st,
            str(m.get("name", "")),
            str(m.get("path", ""))[:40],
            str(m.get("lines", "")),
            str(len(m.get("symbols") or [])),
            str(m.get("import_error_type") or ""),
        ])
    if mod_rows:
        lines.append(md_table(["", "Módulo", "Path", "Líneas", "Símbolos", "Error"], mod_rows))
    lines.append("")
    lines.append("<details><summary>{0} Detalle por módulo</summary>".format(ICON_ITEM))
    lines.append("")
    for m in modules:
        lines.append("### `{0}`".format(m.get("name")))
        lines.append("")
        lines.append("- {0} path: `{1}`".format(ICON_SRC, m.get("path")))
        lines.append("- {0} importable: `{1}`".format(ICON_OK if m.get("importable") else ICON_FAIL, m.get("importable")))
        if m.get("import_error"):
            lines.append("- {0} error: `{1}`".format(ICON_FIND, m.get("import_error")))
        if m.get("symbols"):
            rows = []
            for s in m["symbols"][:80]:
                rows.append([
                    str(s.get("category")),
                    str(s.get("name")),
                    str(s.get("type")),
                    _fmt(s.get("value"))[:40],
                ])
            lines.append(md_table(["Cat", "Nombre", "Tipo", "Valor"], rows))
        lines.append("")
    lines.append("</details>")
    lines.append("")

    lines.append("## {0} Symbol / Variable Census".format(ICON_VAR))
    lines.append("")
    lines.append(md_table(["Métrica", "Valor"], [[k, _fmt(v)] for k, v in stats.items()]))
    lines.append("")
    var_rows = []
    for s in symbols[:200]:
        if s.get("category") != "variable":
            continue
        icon = ICON_LOCK if s.get("redacted") else ICON_VAR
        var_rows.append([icon, s.get("module", ""), s.get("name", ""), s.get("type", ""), _fmt(s.get("value"))[:40]])
    if var_rows:
        lines.append(md_table(["", "Módulo", "Nombre", "Tipo", "Valor"], var_rows[:120]))
    lines.append("")

    lines.append("## {0} Framework Constants".format(ICON_FORM))
    lines.append("")
    if constants:
        lines.append(md_table(
            ["Nombre", "Valor", "Tipo", "Clase", "Fuente"],
            [[
                c.get("name", ""),
                _fmt(c.get("value")),
                str(c.get("type", "")),
                str(c.get("class", "")),
                str(c.get("source", "")),
            ] for c in constants],
        ))
    else:
        lines.append("{0} formulas.constants no disponible".format(ICON_WARN))
    lines.append("")

    lines.append("## {0} Formula Inventory".format(ICON_FORM))
    lines.append("")
    fn_rows = []
    for m in modules:
        if not str(m.get("name", "")).startswith("formulas"):
            continue
        for fn in m.get("static_functions") or []:
            if not fn.get("public"):
                continue
            fn_rows.append([
                str(m.get("name")),
                str(fn.get("name")),
                ", ".join(fn.get("args") or []),
                str(fn.get("line")),
            ])
    if fn_rows:
        lines.append(md_table(["Módulo", "Función", "Args", "Línea"], fn_rows))
    else:
        lines.append("{0} sin funciones públicas descubiertas en formulas.*".format(ICON_INFO))
    lines.append("")

    lines.append("## {0} Layer State".format(ICON_LAYER))
    lines.append("")
    if layers:
        lines.append(md_table(
            ["Id", "Módulo", "Contrato", "Medido", "Error"],
            [[
                str(L.get("id", "")),
                str(L.get("module", "")),
                str(L.get("contract") or "N/D"),
                _fmt(L.get("measured")),
                str(L.get("import_error") or ""),
            ] for L in layers],
        ))
        lines.append("")
        lines.append("<details><summary>{0} Detalle de capas</summary>".format(ICON_ITEM))
        lines.append("")
        for L in layers:
            render_unknown(str(L.get("id")), L, lines)
        lines.append("")
        lines.append("</details>")
    else:
        lines.append("{0} ninguna capa con contrato descubierta".format(ICON_WARN))
    lines.append("")

    lines.append("## {0} Tests".format(ICON_TEST))
    lines.append("")
    lines.append(md_table(
        ["Campo", "Valor"],
        [
            ["source", _fmt(tests.get("source"))],
            ["executed", _fmt(tests.get("executed"))],
            ["discovered files", _fmt((tests.get("discovered") or {}).get("n_files"))],
            ["total", _fmt(tests.get("total"))],
            ["passed", _fmt(tests.get("passed"))],
            ["failures", _fmt(tests.get("failures"))],
            ["errors", _fmt(tests.get("errors"))],
            ["failed", _fmt(tests.get("failed"))],
            ["skipped", _fmt(tests.get("skipped"))],
            ["rate", _fmt(tests.get("rate"))],
        ],
    ))
    cases = tests.get("cases") or []
    bad = [c for c in cases if c.get("status") in {"failure", "error"}]
    if bad:
        lines.append("")
        lines.append("### {0} Fallos individuales".format(ICON_FAIL))
        lines.append("")
        lines.append(md_table(
            ["Status", "Clase", "Nombre", "Detalle"],
            [[c.get("status"), str(c.get("classname") or "")[-40:], str(c.get("name") or ""), str(c.get("detail") or "")[:60]] for c in bad[:40]],
        ))
    lines.append("")

    lines.append("## {0} Coherence History".format(ICON_HIST))
    lines.append("")
    if history:
        rows = []
        for h in history[-20:]:
            rows.append([
                str(h.get("utc") or h.get("timestamp") or "")[:19],
                str(h.get("sha") or ""),
                _fmt(h.get("total")),
                _fmt(h.get("passed")),
                _fmt(h.get("failed")),
                _fmt(h.get("skipped")),
                _fmt(h.get("rate") or h.get("pass_rate")),
                str(h.get("estado") or ""),
            ])
        lines.append(md_table(["utc", "sha", "total", "passed", "failed", "skipped", "rate", "estado"], rows))
    else:
        lines.append("{0} historial no disponible (Omega no lo escribe)".format(ICON_INFO))
    lines.append("")

    lines.append("## {0} Domain Validations".format(ICON_DOM))
    lines.append("")
    if validations:
        lines.append(md_table(
            ["", "Id", "Título", "Status", "Fuente"],
            [[
                _icon_status(v.get("status")),
                str(v.get("id", "")),
                str(v.get("title", "")),
                str(v.get("status", "")),
                str(v.get("source", "")),
            ] for v in validations],
        ))
        lines.append("")
        for v in validations:
            lines.append("### {0} {1}".format(_icon_status(v.get("status")), v.get("title") or v.get("id")))
            lines.append("")
            metrics = v.get("metrics")
            if isinstance(metrics, dict) and metrics:
                lines.append(md_table(["Métrica", "Valor"], [[str(k), _fmt(val)] for k, val in metrics.items()]))
                lines.append("")
            rest = {k: val for k, val in v.items() if k not in {"id", "title", "status", "source", "metrics"}}
            if rest:
                lines.append("<details><summary>{0} evidencia</summary>".format(ICON_ITEM))
                lines.append("")
                render_unknown("evidence", rest, lines)
                lines.append("")
                lines.append("</details>")
                lines.append("")
    else:
        lines.append("{0} ningún productor `omega_validation()` / `__omega_report__()` descubierto".format(ICON_INFO))
        lines.append("")

    lines.append("## {0} Dependency Graph".format(ICON_GRAPH))
    lines.append("")
    edges = deps.get("edges") or []
    lines.append("- nodos: `{0}`".format(len(deps.get("nodes") or [])))
    lines.append("- aristas: `{0}`".format(len(edges)))
    lines.append("")
    if edges:
        lines.append("<details><summary>{0} Aristas</summary>".format(ICON_ITEM))
        lines.append("")
        lines.append(md_table(
            ["Origen", "Dependencia", "Tipo"],
            [[e.get("from", ""), e.get("to", ""), e.get("kind", "")] for e in edges[:80]],
        ))
        lines.append("")
        lines.append("</details>")
    lines.append("")

    lines.append("## {0} Diagnostic Artifacts".format(ICON_SRC))
    lines.append("")
    items = artifacts.get("items") or []
    if items:
        lines.append(md_table(
            ["", "Artefacto", "Bytes"],
            [[ICON_OK if i.get("present") else ICON_FAIL, i.get("name", ""), _fmt(i.get("bytes"))] for i in items],
        ))
    lines.append("")

    lines.append("## {0} Findings".format(ICON_FIND))
    lines.append("")
    if findings:
        lines.append(md_table(
            ["Sev", "Categoría", "Componente", "Mensaje"],
            [[
                str(f.get("severity", "")),
                str(f.get("category", "")),
                str(f.get("component", "")),
                str(f.get("message", ""))[:80],
            ] for f in findings[:80]],
        ))
    else:
        lines.append("{0} sin hallazgos registrados".format(ICON_OK))
    lines.append("")

    known = {
        "schema_version", "generated", "engine", "repository", "modules",
        "symbols", "variables", "constants", "layers", "tests",
        "coherence_history", "validations", "dependencies", "artifacts",
        "coverage", "findings", "authority", "omega_discovery",
    }
    extra = [k for k in pkg.keys() if k not in known]
    lines.append("## {0} Evidence / campos adicionales".format(ICON_ITEM))
    lines.append("")
    if extra:
        for k in extra:
            render_unknown(k, pkg[k], lines)
    else:
        lines.append("{0} sin campos extra respecto al contrato base".format(ICON_INFO))
    lines.append("")

    lines.append("---")
    lines.append("")
    if coherent:
        lines.append("{0} **SYSTEM COHERENT** — sin errores de descubrimiento bloqueantes.".format(ICON_OK))
    else:
        lines.append("{0} **SYSTEM INCOHERENT**".format(ICON_FAIL))
        for f in findings:
            if str(f.get("severity", "")).upper() == "ERROR":
                lines.append("- {0} [{1}] {2}: {3}".format(ICON_FAIL, f.get("category"), f.get("component"), f.get("message")))
    lines.append("")
    lines.append("**Omega**")
    lines.append("")
    return "\n".join(lines)


def render_ci(pkg: dict[str, Any]) -> str:
    gen = pkg.get("generated") or {}
    eng = pkg.get("engine") or {}
    cov = pkg.get("coverage") or {}
    tests = pkg.get("tests") or {}
    findings = pkg.get("findings") or []
    errors_n = sum(1 for f in findings if str(f.get("severity", "")).upper() == "ERROR")
    warns_n = sum(1 for f in findings if str(f.get("severity", "")).upper() == "WARNING")
    lines = [
        W,
        "{0} OMEGA — AUDITORÍA EXTREMA".format(ICON_OMEGA),
        W,
        "{0} SHA                   {1}".format(ICON_SRC, gen.get("sha")),
        "{0} Authority             {1}".format(ICON_ENGINE, "Engine" if eng.get("paquete_from_engine") else "discovery"),
        "{0} Engine                {1}".format(ICON_ENGINE, eng.get("estado") or ("sí" if eng.get("available") else "N/D")),
        S,
        "{0} Py files              {1}".format(ICON_REPO, cov.get("python_files_discovered")),
        "{0} Import OK             {1}".format(ICON_OK, cov.get("modules_importable")),
        "{0} Import FAIL           {1}".format(ICON_FAIL, cov.get("modules_failed_import")),
        "{0} Símbolos              {1}".format(ICON_VAR, cov.get("public_symbols_discovered")),
        "{0} Layers                {1}".format(ICON_LAYER, cov.get("layers_discovered")),
        "{0} Validaciones          {1}".format(ICON_DOM, cov.get("validations_discovered")),
        S,
        "{0} Tests src             {1}".format(ICON_TEST, tests.get("source")),
        "{0} Passed                {1}".format(ICON_OK, tests.get("passed")),
        "{0} Failed                {1}".format(ICON_FAIL, tests.get("failed")),
        "{0} Findings              {1} err / {2} warn".format(ICON_FIND, errors_n, warns_n),
        S,
        "{0} JSON                  diagnostics/omega_report_data.json".format(ICON_SRC),
        "{0} Markdown              diagnostics/OMEGA_REPORT.md".format(ICON_MOD),
        W,
    ]
    return "\n".join(str(x) for x in lines)


# =============================================================================
# SAVE / MAIN
# =============================================================================

def _json_ready(obj: Any) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_json_ready(x) for x in obj]
    return _safe(obj)


def main() -> int:
    print("Running Omega Report...")
    paquete = build_paquete()
    markdown = render_markdown(paquete)
    compact = render_ci(paquete)

    DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = DIAGNOSTICS_DIR / "OMEGA_REPORT.md"
    js_path = DIAGNOSTICS_DIR / "omega_report_data.json"
    md_path.write_text(markdown, encoding="utf-8")
    js_path.write_text(json.dumps(_json_ready(paquete), indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    print(compact)
    print("\nReport saved to: {0}".format(md_path))
    print("JSON data saved to: {0}".format(js_path))
    errors_n = sum(1 for f in (paquete.get("findings") or []) if str(f.get("severity", "")).upper() == "ERROR")
    return 0 if errors_n == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
