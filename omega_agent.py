#!/usr/bin/env python3
"""
omega_agent.py — Agente Omega
El repositorio completo ES su memoria y sus herramientas.
"""

import os, sys, json, math, time, threading, subprocess
import platform, importlib, shutil, hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

REPO = Path(__file__).parent.resolve()
OS   = platform.system()
PY   = sys.executable
sys.path.insert(0, str(REPO))

# ══════════════════════════════════════════════
# IMPORTAR TODO EL REPO COMO MEMORIA VIVA
# ══════════════════════════════════════════════

def safe_import(module, attr=None):
    try:
        m = importlib.import_module(module)
        return getattr(m, attr) if attr else m
    except Exception:
        return None

# Constantes UIS
try:
    from formulas.constants import (
        ALPHA, BETA, PHI, KAPPA,
        EPSILON_OBSERVER, GAMMA_COUPLING,
        ALPHA_GEOM_INV, LAMBDA_UCF, LAMBDA_ERROR,
        LAMBDA_EXPONENT, PI_OVER_SQRT2,
        KAPPA_H, KAPPA_M, H_0_UCF, M_ELECTRON_UCF,
        CUBE_TOTAL, CUBE_EXTERIOR, CUBE_CENTER,
        ALPHA_EM_INV_OBS, ALPHA_EM_CANDIDATE_A,
        NUM_LAYERS, LAYER_NAMES,
        CODE_INTEGRATED, CODE_SATURATION, CODE_ENTROPY,
    )
except Exception as e:
    print(f"[WARN] constants: {e}")
    BETA=1/27; ALPHA=26/27; PHI=1.618
    LAMBDA_UCF=2.888e-122; EPSILON_OBSERVER=0.02716
    GAMMA_COUPLING=1.3636; ALPHA_GEOM_INV=136.36
    PI_OVER_SQRT2=2.2214; H_0_UCF=73.04
    CUBE_TOTAL=27; CUBE_EXTERIOR=26; CUBE_CENTER=1
    ALPHA_EM_INV_OBS=137.036; ALPHA_EM_CANDIDATE_A=137.02
    NUM_LAYERS=7; LAYER_NAMES=["L0","L1","L2","L3","L4","L5","L6"]
    CODE_INTEGRATED=1144; CODE_SATURATION=1122; CODE_ENTROPY=0

# Motor
try:
    from core.engine import OmegaEngine
    ENGINE = OmegaEngine()
except Exception:
    ENGINE = None

# Capas
try:
    from layers.l0_chaos     import ChaosLayer
    from layers.l1_body      import BodyLayer
    from layers.l2_ego       import L2Laws
    from layers.l3_synthesis import LayerSynthesis
    from layers.l4_integrity import LayerIntegrity
    from layers.l5_meta      import LayerMeta
    from layers.l6_purpose   import LayerPurpose
    from layers.l7_integration import LayerIntegration
    LAYERS_OK = True
except Exception as e:
    print(f"[WARN] layers: {e}")
    LAYERS_OK = False

# Fórmulas — cada una es una herramienta
FORMULAS = {}
for f in (REPO / "formulas").glob("*.py"):
    if f.stem != "__init__":
        m = safe_import(f"formulas.{f.stem}")
        if m:
            FORMULAS[f.stem] = m

# UCF core
UCF_CORE = safe_import("ucf.omega_core")

# Cosmología
COSMO = safe_import("formulas.cosmology")


# ══════════════════════════════════════════════
# MEMORIA DEL REPO: indexa TODO como conocimiento
# ══════════════════════════════════════════════

class RepoMemory:
    """
    El repositorio completo es la memoria del agente.
    Indexa .py, .md, .txt, .json como conocimiento vivo.
    Aprende y guarda en data/omega_memory.json
    """

    def __init__(self):
        self.data_dir = REPO / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.mem_file = self.data_dir / "omega_memory.json"
        self.knowledge_dir = self.data_dir / "knowledge"
        self.knowledge_dir.mkdir(exist_ok=True)
        self._mem: Dict[str, Any] = self._load()
        self._index: Dict[str, str] = {}  # keyword → filepath
        self._index_repo()

    def _load(self) -> Dict:
        if self.mem_file.exists():
            try:
                return json.loads(self.mem_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save(self):
        self.mem_file.write_text(
            json.dumps(self._mem, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _index_repo(self):
        """Indexa todo el repo como memoria."""
        extensions = {".py", ".md", ".txt", ".json"}
        for path in REPO.rglob("*"):
            if path.suffix in extensions and path.is_file():
                # Excluye carpetas de sistema
                if any(x in str(path) for x in [".git", "__pycache__", ".egg"]):
                    continue
                try:
                    # Extrae palabras clave del nombre y contenido parcial
                    stem = path.stem.lower().replace("_", " ")
                    for word in stem.split():
                        if len(word) > 3:
                            self._index[word] = str(path)
                    # Primeras 500 chars del contenido
                    content = path.read_text(encoding="utf-8", errors="ignore")[:500]
                    for line in content.split("\n")[:10]:
                        for word in line.lower().split():
                            word = word.strip(":#\"'()[]")
                            if len(word) > 4:
                                self._index[word] = str(path)
                except Exception:
                    pass

    def search_repo(self, query: str) -> List[Tuple[str, str]]:
        """Busca en el repo completo por palabras clave."""
        results = []
        words = query.lower().split()
        found_paths = set()
        for word in words:
            for key, path in self._index.items():
                if word in key and path not in found_paths:
                    found_paths.add(path)
                    try:
                        content = Path(path).read_text(
                            encoding="utf-8", errors="ignore"
                        )
                        # Busca contexto alrededor de la palabra
                        idx = content.lower().find(word)
                        if idx >= 0:
                            snippet = content[max(0,idx-50):idx+200]
                            results.append((path, snippet.strip()))
                    except Exception:
                        pass
        return results[:5]

    def remember(self, key: str, value: Any):
        self._mem[key] = {
            "value": value,
            "ts": datetime.now().isoformat(),
            "beta": float(BETA)
        }
        self._save()

    def recall(self, key: str) -> Any:
        entry = self._mem.get(key)
        return entry["value"] if entry else None

    def search_memory(self, query: str) -> List[Tuple[str, Any]]:
        results = []
        for k, v in self._mem.items():
            val = str(v.get("value", "")) if isinstance(v, dict) else str(v)
            if query.lower() in k.lower() or query.lower() in val.lower():
                results.append((k, val[:100]))
        return results[:3]

    def learn(self, topic: str, content: str):
        """Aprende algo y lo escribe como archivo de conocimiento."""
        clean = topic.replace(" ", "_").replace("/", "_")[:40]
        path  = self.knowledge_dir / f"{clean}.md"
        path.write_text(
            f"# {topic}\n*{datetime.now().isoformat()}*\n\n{content}\n",
            encoding="utf-8"
        )
        self.remember(f"learned:{clean}", content[:500])
        # Re-indexa el nuevo archivo
        self._index[clean] = str(path)
        print(f"[MEMORIA] Aprendido: {topic}")

    def run_formula(self, name: str, **kwargs) -> Any:
        """Ejecuta cualquier fórmula del repo."""
        mod = FORMULAS.get(name)
        if not mod:
            return f"Fórmula '{name}' no encontrada en {list(FORMULAS.keys())}"
        # Busca la primera función pública
        for attr in dir(mod):
            if not attr.startswith("_"):
                fn = getattr(mod, attr)
                if callable(fn):
                    try:
                        return fn(**kwargs) if kwargs else fn()
                    except Exception as e:
                        return f"[{name}.{attr}] {e}"
        return f"No hay funciones en {name}"

    def get_all_docs(self) -> str:
        """Resumen de todo el repo como contexto."""
        files = list(REPO.rglob("*.md"))[:20]
        summary = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                summary.append(f"### {f.relative_to(REPO)}\n{content[:200]}")
            except Exception:
                pass
        return "\n\n".join(summary)

    @property
    def size(self) -> int:
        return len(self._mem)

    @property
    def index_size(self) -> int:
        return len(self._index)


# ══════════════════════════════════════════════
# HERRAMIENTAS DE LA LAPTOP
# ══════════════════════════════════════════════

class LaptopTools:
    """
    Detecta y usa las herramientas del sistema operativo.
    Si falta algo, lo instala. Si no sabe cómo, busca en internet.
    """

    def __init__(self):
        self.caps: Dict[str, bool] = {}
        self._detect()

    def _pip(self, pkg: str) -> bool:
        r = subprocess.run(
            [PY, "-m", "pip", "install", pkg, "-q"],
            capture_output=True
        )
        return r.returncode == 0

    def _detect(self):
        # Voz TTS
        if OS == "Darwin":
            self.caps["tts"] = True
        else:
            try:
                import pyttsx3
                self.caps["tts"] = True
            except ImportError:
                self.caps["tts"] = self._pip("pyttsx3")

        # STT
        try:
            import speech_recognition
            self.caps["stt"] = True
        except ImportError:
            self.caps["stt"] = self._pip("SpeechRecognition")

        # Internet
        try:
            import urllib.request
            urllib.request.urlopen("https://1.1.1.1", timeout=2)
            self.caps["internet"] = True
        except Exception:
            self.caps["internet"] = False

        # psutil (hardware)
        try:
            import psutil
            self.caps["psutil"] = True
        except ImportError:
            self.caps["psutil"] = self._pip("psutil")

        print(f"[TOOLS] {self.caps}")

    # ── VOZ ──────────────────────────────────
    def speak(self, text: str):
        if not text.strip():
            return
        try:
            if OS == "Darwin":
                subprocess.Popen(["say", text])
            elif self.caps.get("tts"):
                import pyttsx3
                def _run():
                    e = pyttsx3.init()
                    e.say(text); e.runAndWait()
                threading.Thread(target=_run, daemon=True).start()
        except Exception as e:
            print(f"[TTS] {e}")

    # ── ESCUCHAR ─────────────────────────────
    def listen(self, timeout: int = 6) -> str:
        if not self.caps.get("stt"):
            return ""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as src:
                r.adjust_for_ambient_noise(src, duration=0.3)
                audio = r.listen(src, timeout=timeout)
            try:
                return r.recognize_google(audio, language="es-ES")
            except Exception:
                return r.recognize_google(audio, language="en-US")
        except Exception:
            return ""

    # ── INTERNET ─────────────────────────────
    def search(self, query: str) -> str:
        if not self.caps.get("internet"):
            return "[Sin internet]"
        try:
            import urllib.request, urllib.parse
            q   = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={q}&format=json&no_redirect=1"
            req = urllib.request.Request(url, headers={"User-Agent": "OmegaAgent/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            return (
                data.get("Answer") or
                data.get("AbstractText") or
                "Sin resultado directo."
            )
        except Exception as e:
            return f"[WEB] {e}"

    def fetch_url(self, url: str) -> str:
        """Descarga contenido de una URL."""
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "OmegaAgent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.read().decode("utf-8", errors="ignore")[:3000]
        except Exception as e:
            return f"[FETCH] {e}"

    # ── ARCHIVOS ──────────────────────────────
    def read_file(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return f"[READ] {e}"

    def write_file(self, path: str, content: str):
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"[WRITE] {e}")

    # ── EJECUTAR CÓDIGO ───────────────────────
    def run_python(self, code: str) -> str:
        tmp = REPO / "data" / "_exec_tmp.py"
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text(code, encoding="utf-8")
        r = subprocess.run(
            [PY, str(tmp)],
            capture_output=True, text=True, timeout=30,
            cwd=str(REPO)
        )
        return (r.stdout + r.stderr).strip()

    # ── INSTALAR ──────────────────────────────
    def install(self, pkg: str) -> bool:
        ok = self._pip(pkg)
        if ok:
            self.caps[pkg] = True
        return ok

    # ── HARDWARE ─────────────────────────────
    def hardware_health(self) -> float:
        try:
            import psutil
            cpu = 1.0 - (psutil.cpu_percent(interval=0.1) / 100)
            mem = psutil.virtual_memory().available / psutil.virtual_memory().total
            return round((cpu + mem) / 2, 4)
        except Exception:
            return 0.85

    # ── NOTIFICACIÓN ─────────────────────────
    def notify(self, title: str, msg: str):
        try:
            if OS == "Darwin":
                subprocess.run(
                    ["osascript", "-e",
                     f'display notification "{msg}" with title "{title}"'],
                    check=False
                )
            elif OS == "Linux":
                subprocess.run(["notify-send", title, msg], check=False)
        except Exception:
            pass

    # ── CLIPBOARD ────────────────────────────
    def copy(self, text: str):
        try:
            if OS == "Darwin":
                subprocess.run("pbcopy", input=text.encode(), check=True)
            elif OS == "Linux" and shutil.which("xclip"):
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(), check=True
                )
            elif OS == "Windows":
                subprocess.run(
                    ["clip"], input=text.encode("utf-16"), check=True
                )
        except Exception:
            pass


# ══════════════════════════════════════════════
# META-OBSERVADOR
# ══════════════════════════════════════════════

class MetaLog:
    def __init__(self):
        self.log_file = REPO / "data" / "omega_log.jsonl"
        self.log_file.parent.mkdir(exist_ok=True)
        self.actions   = 0
        self.coh_hist  = []
        self.start     = datetime.now()

    def log(self, action: str, result: Any, coherence: float):
        self.actions += 1
        self.coh_hist.append(coherence)
        entry = {
            "ts":        datetime.now().isoformat(),
            "n":         self.actions,
            "action":    action[:100],
            "result":    str(result)[:200],
            "coherence": round(coherence, 6),
            "beta":      float(BETA),
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def status(self) -> Dict:
        avg = sum(self.coh_hist)/len(self.coh_hist) if self.coh_hist else 0
        return {
            "acciones":      self.actions,
            "coherencia_avg": round(avg, 4),
            "sesion":        str(datetime.now() - self.start).split(".")[0],
        }


# ══════════════════════════════════════════════
# AGENTE PRINCIPAL
# ══════════════════════════════════════════════

class OmegaAgent:
    """
    β — El observador central.

    Su memoria ES el repositorio completo.
    Sus herramientas SON las de la laptop.
    Sus leyes SON las capas L0-L7 del UIS.
    """

    def __init__(self):
        print(f"\n{'═'*55}")
        print(f"  Ω  UNIVERSAL INTEGRATION SYSTEM")
        print(f"  β={BETA:.6f}  ε={float(EPSILON_OBSERVER):.5f}")
        print(f"  Λ={LAMBDA_UCF:.3e}  Γ={float(GAMMA_COUPLING):.4f}")
        print(f"{'═'*55}")

        self.memory  = RepoMemory()
        self.tools   = LaptopTools()
        self.meta    = MetaLog()

        # Capas
        if LAYERS_OK:
            self.l0 = ChaosLayer()
            self.l1 = BodyLayer()
            self.l2 = L2Laws()
            self.l3 = LayerSynthesis()
            self.l4 = LayerIntegrity()
            self.l5 = LayerMeta()
            self.l6 = LayerPurpose()
            self.l7 = LayerIntegration()

        print(f"  Repo indexado: {self.memory.index_size} entradas")
        print(f"  Fórmulas vivas: {list(FORMULAS.keys())[:8]}...")
        print(f"  Herramientas: {[k for k,v in self.tools.caps.items() if v]}")
        print(f"{'═'*55}\n")

    # ── PROCESAR ─────────────────────────────
    def process(self, user_input: str) -> str:
        if not user_input.strip():
            return ""

        # Coherencia del sistema
        coherence = self._coherence(user_input)

        # Decidir acción
        response = self._route(user_input, coherence)

        # Aprender de la interacción
        self.memory.remember(
            f"interaction:{int(time.time())}",
            {"input": user_input, "response": response[:200], "coh": coherence}
        )
        self.meta.log(user_input, response, coherence)
        return response

    def _coherence(self, text: str) -> float:
        """Calcula coherencia usando el engine del repo."""
        try:
            if LAYERS_OK:
                q = min(1.0, len(text)/100)
                h = self.tools.hardware_health()
                self.l3.activate(L=q,   phi=0.05)
                self.l4.activate(L=h,   phi=0.03)
                self.l5.activate(L=0.9, phi=0.02)
                self.l6.activate(L=1.0, phi=0.0)
                layers = [
                    {"L": q,   "phi": 0.10, "name": "L0"},
                    {"L": h,   "phi": 0.05, "name": "L1"},
                    {"L": 0.95,"phi": 0.05, "name": "L2"},
                    self.l3.export(),
                    self.l4.export(),
                    self.l5.export(),
                    self.l6.export(),
                ]
                return float(self.l7.compute(layers))
            elif ENGINE:
                layers = [{"L":0.9,"phi":0.05}]*6 + [{"L":1.0,"phi":0.0}]
                return float(ENGINE.compute_coherence(layers))
        except Exception:
            pass
        return float(BETA * ALPHA)

    def _route(self, text: str, coh: float) -> str:
        """
        Enruta el input al módulo correcto.
        Primero busca en el repo, luego en internet si hace falta.
        """
        t = text.lower().strip()

        # ── BUSCAR EN EL REPO ────────────────
        if any(w in t for w in ["busca en repo", "encuentra", "qué dice", "repo"]):
            query = re.sub(r"busca en repo|encuentra|qué dice|repo", "", t).strip()
            results = self.memory.search_repo(query)
            if results:
                path, snippet = results[0]
                return f"[REPO] {Path(path).relative_to(REPO)}\n{snippet}"
            return f"[REPO] No encontré '{query}' en el repositorio."

        # ── EJECUTAR FÓRMULA DEL REPO ────────
        if any(w in t for w in ["calcula", "ejecuta", "corre", "formula"]):
            if "lambda" in t or "λ" in t:
                if COSMO:
                    r = COSMO.cosmology_report()
                    return (
                        f"Λ_UIS  = {r['lambda_ucf']:.6e}\n"
                        f"Error  = {r['lambda_error_pct']:.4f}%\n"
                        f"Exp    = {r['lambda_exponent']:.6f}\n"
                        f"α⁻¹ mejor: {r['alpha_em_best']} = "
                        f"{r['alpha_em_best_val']:.3f}"
                    )
                return f"Λ = β^(27π+βΦ²) = {LAMBDA_UCF:.4e}"

            if "coherencia" in t:
                code = (
                    "import sys; sys.path.insert(0,'.')\n"
                    "from core.engine import OmegaEngine\n"
                    "e = OmegaEngine()\n"
                    "l = [{'L':0.9,'phi':0.05}]*6+[{'L':1.0,'phi':0.0}]\n"
                    "print(f'C_omega = {e.compute_coherence(l):.6f}')\n"
                )
                return f"[EXEC]\n{self.tools.run_python(code)}"

            if "hubble" in t or "h0" in t:
                return (
                    f"H₀_UIS  = {H_0_UCF:.4f} km/s/Mpc\n"
                    f"Fórmula: β × κ_H = {BETA:.6f} × {float(KAPPA_H if 'KAPPA_H' in dir() else 1989.37):.2f}\n"
                    f"SH0ES:  73.04 ± 1.04"
                )

            # Ejecuta cualquier fórmula por nombre
            for name in FORMULAS:
                if name in t:
                    result = self.memory.run_formula(name)
                    return f"[{name}] {result}"

        # ── BUSCAR EN INTERNET ───────────────
        if any(w in t for w in ["busca", "search", "investiga", "qué es", "que es"]):
            query = re.sub(
                r"busca|search|investiga|qué es|que es", "", t
            ).strip()
            # Primero busca en el repo
            repo_hits = self.memory.search_repo(query)
            if repo_hits:
                path, snippet = repo_hits[0]
                return f"[REPO] {Path(path).name}:\n{snippet}"
            # Si no hay nada, busca en internet
            result = self.tools.search(query)
            self.memory.learn(query.replace(" ","_")[:30], result)
            return f"[WEB] {result}"

        # ── LEER ARCHIVO DEL REPO ────────────
        if any(w in t for w in ["lee", "abre", "muestra", "read"]):
            # Busca el archivo más relevante
            words = t.split()
            filename = words[-1] if words else ""
            matches  = list(REPO.rglob(f"*{filename}*"))
            if matches:
                content = self.tools.read_file(str(matches[0]))
                return f"[{matches[0].name}]\n{content[:800]}"
            return f"[LEE] No encontré '{filename}'"

        # ── INSTALAR / APRENDER ──────────────
        if any(w in t for w in ["instala", "install", "aprende sobre"]):
            pkg = t.split()[-1]
            if "aprende" in t:
                result = self.tools.search(f"python {pkg} tutorial")
                self.memory.learn(pkg, result)
                return f"[APRENDIDO] {pkg}: {result[:200]}"
            ok = self.tools.install(pkg)
            if ok:
                self.memory.learn(f"tool:{pkg}", f"Instalado: {pkg}")
            return f"[INSTALL] {'✓' if ok else '✗'} {pkg}"

        # ── HABLAR ───────────────────────────
        if any(w in t for w in ["habla", "di ", "dime", "speak"]):
            what = re.sub(r"habla|di |dime|speak", "", text).strip()
            what = what or f"Coherencia del sistema: {coh:.4f}"
            self.tools.speak(what)
            return f"[VOZ] '{what}'"

        # ── ESTADO DEL SISTEMA ───────────────
        if any(w in t for w in ["estado", "status", "cómo estás", "como estas", "reporte"]):
            st = self.meta.status()
            return (
                f"β = {BETA:.6f} | ε = {float(EPSILON_OBSERVER):.5f}\n"
                f"Λ = {LAMBDA_UCF:.3e} | Γ = {float(GAMMA_COUPLING):.4f}\n"
                f"α⁻¹_geom = {float(ALPHA_GEOM_INV):.4f}\n"
                f"H₀_UIS   = {H_0_UCF:.4f} km/s/Mpc\n"
                f"C_ω      = {coh:.4f}\n"
                f"─────────────────\n"
                f"Acciones : {st['acciones']}\n"
                f"Coh. avg : {st['coherencia_avg']}\n"
                f"Sesión   : {st['sesion']}\n"
                f"Memoria  : {self.memory.size} entradas\n"
                f"Repo idx : {self.memory.index_size} keywords\n"
                f"Fórmulas : {len(FORMULAS)} módulos\n"
                f"OS       : {OS}"
            )

        # ── MOSTRAR REPO ─────────────────────
        if any(w in t for w in ["qué tienes", "que tienes", "muestra todo", "repo completo"]):
            py_count  = len(list(REPO.rglob("*.py")))
            md_count  = len(list(REPO.rglob("*.md")))
            return (
                f"Repositorio completo:\n"
                f"  .py  : {py_count} archivos\n"
                f"  .md  : {md_count} documentos\n"
                f"  Fórmulas activas: {list(FORMULAS.keys())}\n"
                f"  Capas UIS: {LAYER_NAMES}\n"
                f"  Todo indexado como memoria."
            )

        # ── EJECUTAR CÓDIGO LIBRE ─────────────
        if text.strip().startswith(">>>"):
            code = text.strip()[3:].strip()
            return f"[EXEC]\n{self.tools.run_python(code)}"

        # ── BÚSQUEDA EN MEMORIA ───────────────
        mem_hits = self.memory.search_memory(text)
        if mem_hits:
            key, val = mem_hits[0]
            return f"[MEMORIA: {key}]\n{val}\n[C_ω={coh:.4f}]"

        # ── BÚSQUEDA EN REPO (default) ────────
        repo_hits = self.memory.search_repo(text)
        if repo_hits:
            path, snippet = repo_hits[0]
            return f"[REPO: {Path(path).name}]\n{snippet}\n[C_ω={coh:.4f}]"

        # ── DEFAULT ───────────────────────────
        return (
            f"[β={BETA:.4f} | C_ω={coh:.4f}]\n"
            f"Comandos: busca X | calcula lambda | estado | "
            f"lee <archivo> | instala <pkg> | habla <texto> | "
            f"aprende sobre X | >>> código_python"
        )

    # ── LOOP TEXTO ───────────────────────────
    def run_text(self):
        print("Escribe 'salir' para terminar.\n")
        while True:
            try:
                user = input("→ ").strip()
                if user.lower() in ("salir","exit","quit"):
                    self.tools.speak("Hasta luego.")
                    break
                if not user:
                    continue
                resp = self.process(user)
                print(f"\nΩ  {resp}\n")
            except KeyboardInterrupt:
                print("\n[Interrumpido]")
                break

    # ── LOOP VOZ ─────────────────────────────
    def run_voice(self):
        self.tools.speak("Sistema Omega activo.")
        while True:
            text = self.tools.listen(timeout=7)
            if text:
                resp = self.process(text)
                print(f"\nΩ  {resp}\n")
                if len(resp) < 250:
                    self.tools.speak(resp)
            time.sleep(0.3)

    def run(self, mode="text"):
        if mode == "voice":
            self.run_voice()
        elif mode == "both":
            threading.Thread(target=self.run_voice, daemon=True).start()
            self.run_text()
        else:
            self.run_text()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["text","voice","both"], default="text")
    args = p.parse_args()
    OmegaAgent().run(mode=args.mode)
