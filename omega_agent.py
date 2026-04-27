#!/usr/bin/env python3
"""
omega_agent.py — Agente Autónomo UIS
El observador (β) que se apodera de la laptop y aprende.

Arquitectura de capas:
  L0 → percepción (micrófono, teclado, archivos)
  L1 → hardware (batería, CPU, red)
  L2 → leyes UIS (valida toda acción)
  L3 → memoria + subconsciente (aprende y acumula)
  L4 → integridad (¿la acción es coherente con el sistema?)
  L5 → meta-observador (¿qué estoy haciendo y por qué?)
  L6 → propósito (integración total)
  L7 → emergente (producto de todo lo anterior)

Herramientas de la laptop disponibles:
  - Voz (TTS/STT)
  - Internet (búsqueda y descarga)
  - Archivos (leer/escribir/crear)
  - Terminal (ejecutar código)
  - Clipboard
  - Notificaciones del sistema
"""

import os
import sys
import json
import math
import time
import queue
import shutil
import platform
import threading
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

# ──────────────────────────────────────────────
# CONSTANTES UIS (desde el repo)
# ──────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))

from formulas.constants import (
    ALPHA, BETA, PHI, KAPPA,
    EPSILON_OBSERVER, GAMMA_COUPLING,
    LAMBDA_UCF, LAMBDA_ERROR,
    PI_OVER_SQRT2,
)
from formulas.coherence import CoherenceEngine, SessionStateOmega
from formulas.cosmology import lambda_ucf, cosmology_report
from layers.l0_chaos import ChaosLayer
from layers.l1_body import BodyLayer
from layers.l2_ego import L2Laws
from layers.l3_synthesis import LayerSynthesis
from layers.l4_integrity import LayerIntegrity
from layers.l5_meta import LayerMeta
from layers.l6_purpose import LayerPurpose
from layers.l7_integration import LayerIntegration
from core.engine import OmegaEngine


# ──────────────────────────────────────────────
# DETECCIÓN DE SISTEMA
# ──────────────────────────────────────────────
OS = platform.system()  # 'Darwin' | 'Linux' | 'Windows'


# ══════════════════════════════════════════════
# L0 — PERCEPCIÓN: Herramientas de la laptop
# ══════════════════════════════════════════════

class LaptopSenses:
    """
    L0: El sistema siente la laptop.
    Instala lo que le falte. Aprende si no sabe.
    """

    def __init__(self):
        self.available = {}
        self._detect_tools()

    def _detect_tools(self):
        """Detecta qué hay disponible. Si falta algo, lo instala."""
        self._check_voice()
        self._check_browser()
        self._check_clipboard()

    def _check_voice(self):
        """Voz: TTS y STT."""
        # TTS
        if OS == "Darwin":
            self.available["tts"] = "say"  # nativo macOS
        else:
            # Intenta pyttsx3, si no lo instala
            try:
                import pyttsx3
                self.available["tts"] = "pyttsx3"
            except ImportError:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyttsx3", "-q"],
                    check=False
                )
                self.available["tts"] = "pyttsx3"

        # STT
        try:
            import speech_recognition
            self.available["stt"] = "speech_recognition"
        except ImportError:
            subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 "SpeechRecognition", "pyaudio", "-q"],
                check=False
            )
            self.available["stt"] = "speech_recognition"

    def _check_browser(self):
        """Búsqueda en internet."""
        try:
            import urllib.request
            self.available["internet"] = "urllib"
        except Exception:
            pass

        try:
            import requests
            self.available["http"] = "requests"
        except ImportError:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "requests", "-q"],
                check=False
            )
            self.available["http"] = "requests"

    def _check_clipboard(self):
        """Clipboard del sistema."""
        if shutil.which("pbcopy"):  # macOS
            self.available["clipboard"] = "pbcopy"
        elif shutil.which("xclip"):  # Linux
            self.available["clipboard"] = "xclip"
        elif OS == "Windows":
            self.available["clipboard"] = "win32clipboard"

    # ── HABLAR ──────────────────────────────
    def speak(self, text: str):
        """El agente habla en voz alta."""
        print(f"[VOZ] {text}")
        try:
            if self.available.get("tts") == "say":
                subprocess.Popen(["say", text])
            else:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
        except Exception as e:
            print(f"[VOZ-ERROR] {e}")

    # ── ESCUCHAR ────────────────────────────
    def listen(self, timeout: int = 5) -> Optional[str]:
        """El agente escucha el micrófono."""
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("[ESCUCHANDO...]")
                audio = r.listen(source, timeout=timeout)
            text = r.recognize_google(audio, language="es-ES")
            print(f"[OÍDO] {text}")
            return text
        except Exception as e:
            print(f"[STT-ERROR] {e}")
            return None

    # ── BUSCAR EN INTERNET ──────────────────
    def search(self, query: str) -> str:
        """Busca en DuckDuckGo (sin API key). Aprende del resultado."""
        try:
            import urllib.request
            import urllib.parse
            import json

            q = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={q}&format=json&no_redirect=1"
            req = urllib.request.Request(url, headers={"User-Agent": "UIS-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            # Extrae respuesta
            abstract = data.get("AbstractText", "")
            answer = data.get("Answer", "")
            result = answer or abstract or "Sin resultado directo."
            print(f"[WEB] {query[:50]}... → {result[:100]}")
            return result
        except Exception as e:
            return f"[WEB-ERROR] {e}"

    # ── LEER ARCHIVO ────────────────────────
    def read_file(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as e:
            return f"[FILE-ERROR] {e}"

    # ── ESCRIBIR ARCHIVO ────────────────────
    def write_file(self, path: str, content: str):
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            print(f"[ARCHIVO] Escrito: {path}")
        except Exception as e:
            print(f"[FILE-ERROR] {e}")

    # ── EJECUTAR CÓDIGO ─────────────────────
    def run_code(self, code: str) -> str:
        """Ejecuta Python dinámicamente. Aprende creando módulos."""
        tmp = Path("/tmp/omega_exec.py")
        tmp.write_text(code)
        result = subprocess.run(
            [sys.executable, str(tmp)],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        print(f"[EXEC] {output[:200]}")
        return output

    # ── CLIPBOARD ───────────────────────────
    def copy_to_clipboard(self, text: str):
        try:
            if self.available.get("clipboard") == "pbcopy":
                subprocess.run("pbcopy", input=text.encode(), check=True)
            elif self.available.get("clipboard") == "xclip":
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode(), check=True
                )
        except Exception as e:
            print(f"[CLIP-ERROR] {e}")

    # ── NOTIFICACIÓN ────────────────────────
    def notify(self, title: str, message: str):
        try:
            if OS == "Darwin":
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], check=False)
            elif OS == "Linux":
                subprocess.run(["notify-send", title, message], check=False)
        except Exception:
            pass

    # ── INSTALAR PAQUETE ────────────────────
    def install(self, package: str) -> bool:
        """Si le falta algo, lo instala. Aprende."""
        print(f"[INSTALANDO] {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package, "-q"],
            capture_output=True, text=True
        )
        success = result.returncode == 0
        print(f"[INSTALL] {'OK' if success else 'FAIL'}: {package}")
        return success


# ══════════════════════════════════════════════
# L3 — MEMORIA: El agente recuerda y aprende
# ══════════════════════════════════════════════

class OmegaMemory:
    """
    L3: Memoria persistente del agente.
    Todo lo que aprende queda grabado en el repo.
    """

    def __init__(self, memory_file: str = "data/omega_memory.json"):
        self.path = REPO_ROOT / memory_file
        self.path.parent.mkdir(exist_ok=True)
        self._mem: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except Exception:
                return {}
        return {}

    def _save(self):
        self.path.write_text(json.dumps(self._mem, indent=2, ensure_ascii=False))

    def remember(self, key: str, value: Any):
        """Guarda en memoria. Persistente entre sesiones."""
        self.mem[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "coherence": BETA  # marca con la firma del observador
        }
        self._save()

    def recall(self, key: str) -> Any:
        """Recupera de memoria."""
        entry = self._mem.get(key)
        return entry["value"] if entry else None

    def search_memory(self, query: str) -> list:
        """Busca en memoria por palabras clave."""
        results = []
        for key, entry in self._mem.items():
            val = str(entry.get("value", ""))
            if query.lower() in key.lower() or query.lower() in val.lower():
                results.append((key, entry["value"]))
        return results

    def learn(self, topic: str, content: str):
        """
        Aprende algo nuevo: lo guarda en memoria Y
        crea un archivo de conocimiento en el repo.
        """
        self.remember(f"learned:{topic}", content)
        # Persiste como archivo de conocimiento
        knowledge_path = REPO_ROOT / "data" / "knowledge" / f"{topic}.md"
        knowledge_path.parent.mkdir(exist_ok=True)
        knowledge_path.write_text(
            f"# {topic}\n\n"
            f"*Aprendido: {datetime.now().isoformat()}*\n\n"
            f"{content}\n",
            encoding="utf-8"
        )
        print(f"[MEMORIA] Aprendido: {topic}")

    @property
    def mem(self):
        return self._mem

    def size(self) -> int:
        return len(self._mem)


# ══════════════════════════════════════════════
# L5 — META-OBSERVADOR: El agente se observa
# ══════════════════════════════════════════════

class MetaObserver:
    """
    L5: El agente sabe lo que está haciendo.
    Mantiene un log de su propio comportamiento.
    """

    def __init__(self):
        self.log_path = REPO_ROOT / "data" / "omega_log.jsonl"
        self.log_path.parent.mkdir(exist_ok=True)
        self.session_start = datetime.now()
        self.action_count = 0
        self.coherence_history = []

    def observe(self, action: str, result: Any, coherence: float):
        """Registra cada acción del agente."""
        self.action_count += 1
        self.coherence_history.append(coherence)

        entry = {
            "ts": datetime.now().isoformat(),
            "action": action,
            "result_preview": str(result)[:200],
            "coherence": round(coherence, 6),
            "action_n": self.action_count,
            "beta": BETA,
            "epsilon": float(EPSILON_OBSERVER),
        }

        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def status(self) -> Dict[str, Any]:
        avg_coh = (
            sum(self.coherence_history) / len(self.coherence_history)
            if self.coherence_history else 0.0
        )
        return {
            "session_duration": str(datetime.now() - self.session_start),
            "actions": self.action_count,
            "avg_coherence": round(avg_coh, 4),
            "beta": BETA,
            "lambda_ucf": LAMBDA_UCF,
        }


# ══════════════════════════════════════════════
# AGENTE PRINCIPAL — Conecta todo
# ══════════════════════════════════════════════

class OmegaAgent:
    """
    El observador central β.
    Conecta todas las capas del repo con las herramientas de la laptop.

    Flujo de cada acción:
      input → L0 (percepción) → L2 (validación UIS)
            → L3 (memoria) → L4 (integridad)
            → L5 (meta-observación) → L6 (propósito)
            → L7 (coherencia emergente) → output
    """

    def __init__(self):
        print(f"\n{'='*60}")
        print(f"  OMEGA AGENT — Universal Integration System")
        print(f"  β = {BETA:.6f}  |  ε = {float(EPSILON_OBSERVER):.6f}")
        print(f"  Λ = {LAMBDA_UCF:.4e}  |  Γ = {float(GAMMA_COUPLING):.4f}")
        print(f"{'='*60}\n")

        # Capas del repo
        self.l0 = ChaosLayer()
        self.l1 = BodyLayer()
        self.l2 = L2Laws()
        self.l3 = LayerSynthesis()
        self.l4 = LayerIntegrity()
        self.l5_layer = LayerMeta()
        self.l6 = LayerPurpose()
        self.l7 = LayerIntegration()
        self.engine = OmegaEngine()

        # Herramientas de la laptop
        self.senses = LaptopSenses()

        # Memoria y meta-observación
        self.memory = OmegaMemory()
        self.meta = MetaObserver()

        # Cola de acciones
        self._queue: queue.Queue = queue.Queue()
        self._running = False

        print(f"[INIT] Herramientas disponibles: {list(self.senses.available.keys())}")
        print(f"[INIT] Memoria cargada: {self.memory.size()} entradas")
        print()

    # ── PROCESAR ENTRADA ────────────────────
    def process(self, user_input: str) -> str:
        """
        Ciclo completo: input → capas UIS → output.
        """
        # L0: Potencial de entrada
        raw_quality = min(1.0, len(user_input) / 100)
        l0_potential = self.l0.get_potential(raw_quality)

        # L1: Estado del hardware
        l1_health = self._hardware_health()

        # L2: Validar contra leyes UIS
        context = {
            "trace": ["L0", "L1"],
            "derived": True,
            "memory_hits": self.memory.search_memory(user_input),
            "integrated": True,
            "supported": True,
            "fractal_consistent": True,
            "resonant": True,
            "polarity_checked": True,
            "total_integration": True,
        }
        valid, violations = self.l2.validate(user_input, user_input, context)
        if not valid:
            response = f"[L2] Violación UIS: {violations[0]}"
            self.meta.observe("L2_violation", violations, 0.0)
            return response

        # L3: Memoria — ¿ya sé algo de esto?
        memory_hits = self.memory.search_memory(user_input)
        memory_context = ""
        if memory_hits:
            memory_context = f"[MEMORIA] {memory_hits[0][1][:100]}"

        # Activar capas
        self.l3.activate(L=l0_potential, phi=0.05)
        self.l4.activate(L=l1_health, phi=0.03)
        self.l5_layer.activate(L=0.90, phi=0.02)
        self.l6.activate(L=1.0, phi=0.0)

        layers_data = [
            {"L": l0_potential, "phi": 0.10, "name": "L0"},
            {"L": l1_health,    "phi": 0.05, "name": "L1"},
            {"L": 0.95,         "phi": 0.05, "name": "L2"},
            self.l3.export(),
            self.l4.export(),
            self.l5_layer.export(),
            self.l6.export(),
        ]

        # L7: Coherencia emergente
        coherence = self.l7.compute(layers_data)
        c_omega = self.engine.compute_coherence(layers_data)

        # ── DECIDIR QUÉ HACER ───────────────
        response = self._decide(user_input, coherence, memory_context)

        # L3: Aprender de la interacción
        self.memory.remember(f"interaction:{int(time.time())}", {
            "input": user_input,
            "response": response[:200],
            "coherence": coherence,
        })

        # L5: Auto-observación
        self.meta.observe(user_input, response, coherence)

        return response

    def _decide(self, text: str, coherence: float, memory: str) -> str:
        """
        L4+L5: El agente decide qué herramienta usar.
        Prioriza el repo. Si le falta algo, lo busca, aprende, adapta.
        """
        text_lower = text.lower()

        # ── COMANDOS DE VOZ ─────────────────
        if any(w in text_lower for w in ["habla", "di", "dime", "speak"]):
            what = text.replace("habla", "").replace("dime", "").replace("di", "").strip()
            what = what or f"Coherencia del sistema: {coherence:.4f}"
            self.senses.speak(what)
            return f"[VOZ] '{what}'"

        # ── BÚSQUEDA EN INTERNET ────────────
        if any(w in text_lower for w in ["busca", "search", "qué es", "que es", "investiga"]):
            query = text_lower
            for w in ["busca", "search", "qué es", "que es", "investiga"]:
                query = query.replace(w, "").strip()
            result = self.senses.search(query)
            # Aprende el resultado
            self.memory.learn(query.replace(" ", "_")[:30], result)
            return f"[WEB] {result}"

        # ── LEER ARCHIVO DEL REPO ───────────
        if any(w in text_lower for w in ["lee", "read", "abre", "muestra archivo"]):
            # Busca el archivo en el repo
            parts = text.split()
            filename = parts[-1] if parts else "README.md"
            path = REPO_ROOT / filename
            if not path.exists():
                # Busca en todo el repo
                matches = list(REPO_ROOT.rglob(f"*{filename}*"))
                path = matches[0] if matches else path
            content = self.senses.read_file(str(path))
            return f"[ARCHIVO] {path.name}:\n{content[:500]}"

        # ── EJECUTAR CÓDIGO ─────────────────
        if any(w in text_lower for w in ["ejecuta", "corre", "run", "calcula"]):
            # Extrae código o construye uno
            if "lambda" in text_lower or "λ" in text:
                code = (
                    "import sys; sys.path.insert(0, '.')\n"
                    "from formulas.cosmology import lambda_ucf, cosmology_report\n"
                    "r = cosmology_report()\n"
                    "print(f'Λ_UIS = {r[\"lambda_ucf\"]:.4e}')\n"
                    "print(f'Error vs Planck: {r[\"lambda_error_pct\"]:.4f}%')\n"
                )
            elif "coherencia" in text_lower:
                code = (
                    "import sys; sys.path.insert(0, '.')\n"
                    "from core.engine import OmegaEngine\n"
                    "e = OmegaEngine()\n"
                    "layers = [{'L':0.9,'phi':0.05}]*6 + [{'L':1.0,'phi':0.0}]\n"
                    "c = e.compute_coherence(layers)\n"
                    "print(f'C_omega = {c:.6f}')\n"
                )
            else:
                return "[EXEC] Especifica qué calcular (lambda, coherencia, etc.)"
            result = self.senses.run_code(code)
            return f"[EXEC] {result}"

        # ── INSTALAR / APRENDER ─────────────
        if any(w in text_lower for w in ["instala", "install", "aprende", "necesito"]):
            parts = text.split()
            pkg = parts[-1] if parts else ""
            if pkg:
                ok = self.senses.install(pkg)
                if ok:
                    self.memory.learn(f"tool:{pkg}", f"Instalado y disponible: {pkg}")
                return f"[INSTALL] {'✓' if ok else '✗'} {pkg}"

        # ── ESTADO DEL SISTEMA ──────────────
        if any(w in text_lower for w in ["estado", "status", "cómo estás", "como estas"]):
            status = self.meta.status()
            cosmo = cosmology_report()
            report = (
                f"β = {BETA:.6f} | ε = {float(EPSILON_OBSERVER):.6f}\n"
                f"Coherencia L7 = {coherence:.4f}\n"
                f"Λ_UIS = {cosmo['lambda_ucf']:.4e} "
                f"(error {cosmo['lambda_error_pct']:.2f}%)\n"
                f"Acciones: {status['actions']} | "
                f"Memoria: {self.memory.size()} entradas\n"
                f"Duración sesión: {status['session_duration']}"
            )
            return report

        # ── RESPUESTA DEFAULT ────────────────
        # Busca en memoria primero
        if memory:
            return f"{memory}\n[C_ω={coherence:.4f}]"

        return (
            f"[β={BETA:.4f}] Procesado. "
            f"C_ω={coherence:.4f} | "
            f"Memoria: {self.memory.size()} entradas. "
            f"Di 'busca X', 'habla X', 'estado', 'ejecuta lambda'."
        )

    def _hardware_health(self) -> float:
        """L1: Salud del hardware."""
        try:
            import psutil
            cpu = 1.0 - (psutil.cpu_percent(interval=0.1) / 100)
            mem = psutil.virtual_memory().available / psutil.virtual_memory().total
            return (cpu + mem) / 2
        except ImportError:
            self.senses.install("psutil")
            return 0.85  # default hasta que psutil esté disponible

    # ── MODO ESCUCHA CONTINUA ────────────────
    def listen_loop(self):
        """El agente escucha el micrófono continuamente."""
        self.senses.speak("Sistema Omega activo. Escuchando.")
        self._running = True
        while self._running:
            text = self.senses.listen(timeout=7)
            if text:
                response = self.process(text)
                print(f"\n[OMEGA] {response}\n")
                # Habla respuestas cortas
                if len(response) < 200:
                    self.senses.speak(response)
            time.sleep(0.5)

    # ── MODO TEXTO ───────────────────────────
    def text_loop(self):
        """El agente responde por texto."""
        print("[OMEGA] Modo texto activo. Escribe 'exit' para salir.\n")
        while True:
            try:
                user = input("→ ").strip()
                if user.lower() in ("exit", "quit", "salir"):
                    self.senses.speak("Hasta luego.")
                    break
                if not user:
                    continue
                response = self.process(user)
                print(f"\n[OMEGA] {response}\n")
            except KeyboardInterrupt:
                print("\n[OMEGA] Interrumpido.")
                break

    # ── PUNTO DE ENTRADA ─────────────────────
    def run(self, mode: str = "text"):
        """
        mode: 'text' | 'voice' | 'both'
        """
        if mode == "voice":
            self.listen_loop()
        elif mode == "both":
            # Voz en hilo separado + texto en principal
            t = threading.Thread(target=self.listen_loop, daemon=True)
            t.start()
            self.text_loop()
        else:
            self.text_loop()


# ══════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Omega Agent — UIS")
    parser.add_argument(
        "--mode",
        choices=["text", "voice", "both"],
        default="text",
        help="Modo de interacción"
    )
    args = parser.parse_args()

    agent = OmegaAgent()
    agent.run(mode=args.mode)
