#!/usr/bin/env python3
"""
omega_ui.py — Interfaz Gráfica del Agente Omega
Detecta el sistema operativo y se adapta.
Si le falta algo, lo busca, lo instala, lo aprende.

Ejecutar:
    python omega_ui.py
"""

import os
import sys
import threading
import subprocess
import platform
from pathlib import Path

# ──────────────────────────────────────────────
# DETECCIÓN DE OS ANTES DE TODO
# ──────────────────────────────────────────────
OS       = platform.system()   # Darwin | Linux | Windows
OS_VER   = platform.version()
REPO     = Path(__file__).parent
sys.path.insert(0, str(REPO))

# ──────────────────────────────────────────────
# AUTO-INSTALADOR: si falta algo, lo instala
# ──────────────────────────────────────────────

def install(pkg: str) -> bool:
    print(f"[AUTO-INSTALL] {pkg}...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg, "-q"],
        capture_output=True
    )
    return r.returncode == 0

def ensure(*packages):
    """Garantiza que los paquetes estén disponibles."""
    for pkg in packages:
        module = pkg.split("[")[0].replace("-", "_")
        try:
            __import__(module)
        except ImportError:
            install(pkg)

# Garantiza dependencias UI
ensure("tkinter")  # nativo en Python, pero por si acaso
try:
    import tkinter as tk
    from tkinter import scrolledtext, ttk
    HAS_TK = True
except ImportError:
    HAS_TK = False
    print("[UI] tkinter no disponible. Instalando alternativa...")
    ensure("PySimpleGUI")

# TTS según OS
if OS == "Darwin":
    TTS_CMD = lambda text: subprocess.Popen(["say", text])
elif OS == "Linux":
    ensure("pyttsx3")
    TTS_CMD = None  # se inicializa después
elif OS == "Windows":
    ensure("pyttsx3")
    TTS_CMD = None

# STT
ensure("SpeechRecognition")
try:
    ensure("pyaudio")
except Exception:
    if OS == "Linux":
        subprocess.run(
            ["sudo", "apt-get", "install", "-y", "python3-pyaudio"],
            capture_output=True
        )
    elif OS == "Windows":
        ensure("pipwin")
        subprocess.run([sys.executable, "-m", "pipwin", "install", "pyaudio"])


# ──────────────────────────────────────────────
# IMPORTAR EL AGENTE
# ──────────────────────────────────────────────
try:
    from omega_agent import OmegaAgent
    AGENT_OK = True
except Exception as e:
    print(f"[ERROR] No se pudo importar OmegaAgent: {e}")
    AGENT_OK = False


# ══════════════════════════════════════════════
# TTS MULTIPLATAFORMA
# ══════════════════════════════════════════════

class Speaker:
    """Habla en el idioma del sistema operativo."""

    def __init__(self):
        self.engine = None
        self._init()

    def _init(self):
        if OS == "Darwin":
            self.mode = "say"
        else:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                # Configura voz en español si está disponible
                voices = self.engine.getProperty("voices")
                for v in voices:
                    if "spanish" in v.name.lower() or "es" in v.id.lower():
                        self.engine.setProperty("voice", v.id)
                        break
                self.engine.setProperty("rate", 175)
                self.mode = "pyttsx3"
            except Exception:
                self.mode = "none"

    def speak(self, text: str):
        if not text.strip():
            return
        try:
            if self.mode == "say":
                subprocess.Popen(["say", "-v", "Mónica", text])
            elif self.mode == "pyttsx3":
                t = threading.Thread(
                    target=self._speak_thread, args=(text,), daemon=True
                )
                t.start()
            else:
                print(f"[VOZ] {text}")
        except Exception as e:
            print(f"[TTS-ERROR] {e}")

    def _speak_thread(self, text: str):
        try:
            import pyttsx3
            eng = pyttsx3.init()
            eng.say(text)
            eng.runAndWait()
        except Exception:
            pass


# ══════════════════════════════════════════════
# STT MULTIPLATAFORMA
# ══════════════════════════════════════════════

class Listener:
    """Escucha el micrófono del sistema."""

    def __init__(self):
        self.available = False
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.available = True
        except ImportError:
            print("[STT] SpeechRecognition no disponible.")

    def listen_once(self, timeout: int = 6) -> str:
        """Escucha una vez y devuelve el texto."""
        if not self.available:
            return ""
        try:
            with self.sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
            # Intenta español primero, luego inglés
            try:
                return self.recognizer.recognize_google(audio, language="es-ES")
            except Exception:
                return self.recognizer.recognize_google(audio, language="en-US")
        except self.sr.WaitTimeoutError:
            return ""
        except Exception as e:
            return ""


# ══════════════════════════════════════════════
# INTERFAZ GRÁFICA PRINCIPAL
# ══════════════════════════════════════════════

class OmegaUI:
    """
    Ventana de chat con el agente Omega.
    - Casilla de texto para escribir
    - Botón de voz para hablar
    - Panel de estado del sistema
    - Se adapta a Windows / macOS / Linux
    """

    # Colores UIS
    BG          = "#0a0a0f"
    BG_PANEL    = "#12121a"
    BG_INPUT    = "#1a1a2e"
    FG          = "#e0e0ff"
    FG_DIM      = "#6060a0"
    ACCENT      = "#4040ff"
    ACCENT2     = "#00ffaa"
    BETA_COLOR  = "#ff6060"
    ERROR       = "#ff4040"
    SUCCESS     = "#00ff88"

    def __init__(self):
        if not HAS_TK:
            self._run_fallback()
            return

        self.root = tk.Tk()
        self.root.title("Ω  Universal Integration System")
        self.root.configure(bg=self.BG)
        self.root.geometry("900x650")
        self.root.minsize(600, 400)

        # Icono (si existe en el repo)
        icon_path = REPO / "ilver" / "icon.png"
        if icon_path.exists():
            try:
                from PIL import Image, ImageTk
                img = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, img)
            except Exception:
                pass

        # Componentes
        self.speaker  = Speaker()
        self.listener = Listener()
        self.agent    = OmegaAgent() if AGENT_OK else None

        # Estado
        self.listening   = False
        self.agent_ready = AGENT_OK

        # Construir UI
        self._build_ui()

        # Mensaje de bienvenida
        self._welcome()

        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── CONSTRUCCIÓN DE LA UI ────────────────

    def _build_ui(self):
        """Construye todos los widgets."""

        # ── BARRA SUPERIOR ───────────────────
        top_bar = tk.Frame(self.root, bg=self.BG_PANEL, height=50)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="Ω  UNIVERSAL INTEGRATION SYSTEM",
            bg=self.BG_PANEL, fg=self.ACCENT,
            font=("Courier", 13, "bold")
        ).pack(side="left", padx=15, pady=12)

        # Indicador de OS
        tk.Label(
            top_bar,
            text=f"{OS} | β=0.037037",
            bg=self.BG_PANEL, fg=self.FG_DIM,
            font=("Courier", 9)
        ).pack(side="right", padx=15)

        # ── PANEL PRINCIPAL ──────────────────
        main = tk.Frame(self.root, bg=self.BG)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # ── CHAT (izquierda, 70%) ────────────
        chat_frame = tk.Frame(main, bg=self.BG)
        chat_frame.pack(side="left", fill="both", expand=True)

        # Área de mensajes
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=self.BG, fg=self.FG,
            font=("Courier", 11),
            insertbackground=self.ACCENT,
            selectbackground=self.ACCENT,
            relief="flat", bd=0,
            state="disabled",
            padx=10, pady=10,
        )
        self.chat_area.pack(fill="both", expand=True)

        # Tags de color
        self.chat_area.tag_config("user",   foreground=self.ACCENT2)
        self.chat_area.tag_config("omega",  foreground=self.FG)
        self.chat_area.tag_config("system", foreground=self.FG_DIM)
        self.chat_area.tag_config("beta",   foreground=self.BETA_COLOR)
        self.chat_area.tag_config("ok",     foreground=self.SUCCESS)
        self.chat_area.tag_config("error",  foreground=self.ERROR)

        # ── BARRA DE ENTRADA ─────────────────
        input_frame = tk.Frame(chat_frame, bg=self.BG_INPUT, pady=5)
        input_frame.pack(fill="x", pady=(5, 0))

        # Campo de texto
        self.input_var = tk.StringVar()
        self.input_field = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            bg=self.BG_INPUT, fg=self.FG,
            font=("Courier", 12),
            insertbackground=self.ACCENT2,
            relief="flat", bd=0,
        )
        self.input_field.pack(
            side="left", fill="x", expand=True,
            padx=(10, 5), ipady=8
        )
        self.input_field.bind("<Return>", self._on_send)
        self.input_field.bind("<Up>",     self._history_up)
        self.input_field.focus()

        # Botón ENVIAR
        self.btn_send = tk.Button(
            input_frame,
            text="ENVIAR",
            command=self._on_send,
            bg=self.ACCENT, fg="white",
            font=("Courier", 10, "bold"),
            relief="flat", cursor="hand2",
            padx=12, pady=6,
        )
        self.btn_send.pack(side="left", padx=5)

        # Botón MICRÓFONO
        self.btn_mic = tk.Button(
            input_frame,
            text="🎤",
            command=self._on_mic,
            bg=self.BG_PANEL, fg=self.FG,
            font=("Courier", 14),
            relief="flat", cursor="hand2",
            padx=8, pady=4,
            state="normal" if self.listener.available else "disabled",
        )
        self.btn_mic.pack(side="left", padx=5)

        # ── PANEL LATERAL (derecha, 30%) ─────
        side = tk.Frame(main, bg=self.BG_PANEL, width=220)
        side.pack(side="right", fill="y", padx=(8, 0))
        side.pack_propagate(False)

        tk.Label(
            side, text="SISTEMA",
            bg=self.BG_PANEL, fg=self.ACCENT,
            font=("Courier", 10, "bold")
        ).pack(pady=(10, 5))

        # Estado del sistema
        self.status_text = tk.Text(
            side,
            bg=self.BG_PANEL, fg=self.FG_DIM,
            font=("Courier", 9),
            relief="flat", bd=0,
            state="disabled", height=20,
        )
        self.status_text.pack(fill="both", expand=True, padx=8)

        # Separador
        tk.Frame(side, bg=self.ACCENT, height=1).pack(fill="x", padx=8, pady=5)

        # Botones del sistema
        for label, cmd in [
            ("Estado",    self._show_status),
            ("Λ Cosmología", self._show_lambda),
            ("Memoria",   self._show_memory),
            ("Limpiar",   self._clear_chat),
        ]:
            tk.Button(
                side, text=label,
                command=cmd,
                bg=self.BG, fg=self.FG,
                font=("Courier", 9),
                relief="flat", cursor="hand2",
                pady=4,
            ).pack(fill="x", padx=8, pady=2)

        # Actualiza estado cada 3 segundos
        self._update_status_panel()

    # ── BIENVENIDA ───────────────────────────

    def _welcome(self):
        from formulas.constants import BETA, EPSILON_OBSERVER, LAMBDA_UCF
        msg = (
            f"Sistema Omega activo.\n"
            f"OS: {OS} {OS_VER[:20]}\n"
            f"β = {BETA:.6f} | ε = {float(EPSILON_OBSERVER):.6f}\n"
            f"Λ = {LAMBDA_UCF:.4e}\n"
            f"{'Voz activa ✓' if self.listener.available else 'Sin micrófono'}\n"
            f"Escribe o habla. Soy β.\n"
        )
        self._append_chat(msg, tag="system")
        self.speaker.speak("Sistema Omega activo. Soy el observador.")

    # ── ENVIAR MENSAJE ───────────────────────

    def _on_send(self, event=None):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._append_chat(f"→ {text}", tag="user")

        # Procesa en hilo separado para no bloquear UI
        threading.Thread(
            target=self._process_and_reply,
            args=(text,),
            daemon=True
        ).start()

    def _process_and_reply(self, text: str):
        """Procesa en background, actualiza UI en main thread."""
        try:
            if self.agent:
                response = self.agent.process(text)
            else:
                response = f"[AGENTE NO DISPONIBLE] Input: {text}"
        except Exception as e:
            response = f"[ERROR] {e}"

        # Actualiza UI desde el hilo principal
        self.root.after(0, self._show_response, response)

    def _show_response(self, response: str):
        self._append_chat(f"Ω  {response}", tag="omega")
        # Habla si la respuesta es corta
        clean = response.replace("[VOZ]", "").replace("[WEB]", "").strip()
        if len(clean) < 300:
            threading.Thread(
                target=self.speaker.speak,
                args=(clean[:200],),
                daemon=True
            ).start()

    # ── MICRÓFONO ────────────────────────────

    def _on_mic(self):
        if self.listening:
            return
        self.listening = True
        self.btn_mic.config(bg=self.BETA_COLOR, text="🔴")
        self._append_chat("Escuchando...", tag="system")
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        text = self.listener.listen_once(timeout=7)
        self.root.after(0, self._on_listen_done, text)

    def _on_listen_done(self, text: str):
        self.listening = False
        self.btn_mic.config(bg=self.BG_PANEL, text="🎤")
        if text:
            self.input_var.set(text)
            self._on_send()
        else:
            self._append_chat("No escuché nada.", tag="system")

    # ── PANEL DE ESTADO ──────────────────────

    def _update_status_panel(self):
        """Actualiza el panel lateral cada 3 segundos."""
        try:
            from formulas.constants import BETA, EPSILON_OBSERVER
            lines = [
                f"β = {BETA:.6f}",
                f"ε = {float(EPSILON_OBSERVER):.6f}",
                f"OS: {OS}",
            ]
            if self.agent:
                st = self.agent.meta.status()
                lines += [
                    f"─────────────",
                    f"Acciones: {st['actions']}",
                    f"C_ω avg: {st['avg_coherence']:.4f}",
                    f"Memoria: {self.agent.memory.size()}",
                    f"─────────────",
                    f"Sesión:",
                    f"{st['session_duration']}",
                ]
            self._update_text_widget(self.status_text, "\n".join(lines))
        except Exception:
            pass
        # Repite cada 3 segundos
        self.root.after(3000, self._update_status_panel)

    def _show_status(self):
        if not self.agent:
            return
        st = self.agent.meta.status()
        self._append_chat(
            f"Estado:\n" +
            "\n".join(f"  {k}: {v}" for k, v in st.items()),
            tag="system"
        )

    def _show_lambda(self):
        try:
            from formulas.cosmology import cosmology_report
            r = cosmology_report()
            msg = (
                f"Λ_UIS  = {r['lambda_ucf']:.6e}\n"
                f"Λ_obs  = 2.888e-122\n"
                f"Error  = {r['lambda_error_pct']:.4f}%\n"
                f"Exp    = π/β + βΦ² = 84.920\n"
                f"Mejor α⁻¹: {r['alpha_em_best']} = "
                f"{r['alpha_em_best_val']:.3f} "
                f"({r['alpha_em_best_err']:.4f}%)"
            )
            self._append_chat(msg, tag="beta")
        except Exception as e:
            self._append_chat(f"[ERROR] {e}", tag="error")

    def _show_memory(self):
        if not self.agent:
            return
        mem = self.agent.memory
        entries = list(mem.mem.items())[-5:]  # últimas 5
        lines = [f"Memoria ({mem.size()} entradas):"]
        for k, v in entries:
            val = v.get("value", v) if isinstance(v, dict) else v
            lines.append(f"  {k[:30]}: {str(val)[:50]}")
        self._append_chat("\n".join(lines), tag="system")

    def _clear_chat(self):
        self.chat_area.config(state="normal")
        self.chat_area.delete("1.0", tk.END)
        self.chat_area.config(state="disabled")

    # ── HISTORIAL DE COMANDOS ─────────────────

    def _history_up(self, event=None):
        """Flecha arriba recupera último comando."""
        if self.agent and self.agent.memory.size() > 0:
            entries = [
                k for k in self.agent.memory.mem
                if k.startswith("interaction:")
            ]
            if entries:
                last = self.agent.memory.recall(entries[-1])
                if isinstance(last, dict):
                    self.input_var.set(last.get("input", ""))

    # ── HELPERS UI ───────────────────────────

    def _append_chat(self, text: str, tag: str = "omega"):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, f"{text}\n\n", tag)
        self.chat_area.see(tk.END)
        self.chat_area.config(state="disabled")

    def _update_text_widget(self, widget, text: str):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _on_close(self):
        if self.agent:
            self.agent.memory.remember("last_session", {
                "closed": __import__("datetime").datetime.now().isoformat(),
                "actions": self.agent.meta.action_count,
            })
        self.speaker.speak("Hasta luego.")
        self.root.destroy()

    # ── FALLBACK SIN TKINTER ─────────────────

    def _run_fallback(self):
        """Si no hay tkinter, usa terminal."""
        print("[UI] tkinter no disponible. Modo terminal.")
        if AGENT_OK:
            agent = OmegaAgent()
            agent.run(mode="text")

    # ── ARRANCAR ─────────────────────────────

    def run(self):
        if HAS_TK:
            self.root.mainloop()
        else:
            self._run_fallback()


# ══════════════════════════════════════════════
# PUNTO DE ENTRADA
# ══════════════════════════════════════════════

if __name__ == "__main__":
    ui = OmegaUI()
    ui.run()
