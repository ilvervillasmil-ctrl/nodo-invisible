#!/usr/bin/env python3
"""
omega_ui.py — Ventana gráfica del Agente Omega
Detecta el OS. Abre ventana. Si falta algo, lo instala.
"""

import os, sys, threading, subprocess, platform
from pathlib import Path

OS   = platform.system()
REPO = Path(__file__).parent.resolve()
PY   = sys.executable
sys.path.insert(0, str(REPO))

# ── Auto-instalar dependencias UI ──────────────
def pip(pkg):
    subprocess.run([PY,"-m","pip","install",pkg,"-q"], capture_output=True)

try:
    import tkinter as tk
    from tkinter import scrolledtext
    HAS_TK = True
except ImportError:
    pip("tk"); HAS_TK = False

# ── Importar agente ────────────────────────────
try:
    from omega_agent import OmegaAgent, BETA, LAMBDA_UCF, EPSILON_OBSERVER
    AGENT_OK = True
except Exception as e:
    print(f"[ERROR] {e}")
    AGENT_OK = False


# ══════════════════════════════════════════════
# SPEAKER
# ══════════════════════════════════════════════
class Speaker:
    def __init__(self):
        self.mode = "none"
        if OS == "Darwin":
            self.mode = "say"
        else:
            try:
                import pyttsx3; self.mode = "pyttsx3"
            except ImportError:
                pip("pyttsx3")
                try:
                    import pyttsx3; self.mode = "pyttsx3"
                except Exception:
                    pass

    def speak(self, text):
        if not text.strip(): return
        try:
            if self.mode == "say":
                subprocess.Popen(["say", text])
            elif self.mode == "pyttsx3":
                def _run():
                    import pyttsx3
                    e = pyttsx3.init(); e.say(text[:200]); e.runAndWait()
                threading.Thread(target=_run, daemon=True).start()
        except Exception: pass


# ══════════════════════════════════════════════
# LISTENER
# ══════════════════════════════════════════════
class Listener:
    def __init__(self):
        self.ok = False
        try:
            import speech_recognition as sr
            self.sr = sr
            self.rec = sr.Recognizer()
            self.ok = True
        except ImportError:
            pip("SpeechRecognition")
            try:
                import speech_recognition as sr
                self.sr = sr; self.rec = sr.Recognizer(); self.ok = True
            except Exception: pass

    def listen(self, timeout=6) -> str:
        if not self.ok: return ""
        try:
            with self.sr.Microphone() as src:
                self.rec.adjust_for_ambient_noise(src, duration=0.3)
                audio = self.rec.listen(src, timeout=timeout)
            try:    return self.rec.recognize_google(audio, language="es-ES")
            except: return self.rec.recognize_google(audio, language="en-US")
        except Exception: return ""


# ══════════════════════════════════════════════
# INTERFAZ GRÁFICA
# ══════════════════════════════════════════════
class OmegaUI:
    BG      = "#07070f"
    BG2     = "#0f0f1a"
    BG3     = "#16162a"
    FG      = "#d0d0ff"
    DIM     = "#5050a0"
    ACCENT  = "#3355ff"
    GREEN   = "#00ffaa"
    RED     = "#ff4455"
    GOLD    = "#ffcc00"
    FONT    = ("Courier", 11)
    FONT_SM = ("Courier", 9)
    FONT_LG = ("Courier", 13, "bold")

    def __init__(self):
        if not HAS_TK:
            self._fallback(); return

        self.root = tk.Tk()
        self.root.title("Ω  Universal Integration System")
        self.root.configure(bg=self.BG)
        self.root.geometry("960x660")
        self.root.minsize(700, 450)

        self.speaker   = Speaker()
        self.listener  = Listener()
        self.agent     = OmegaAgent() if AGENT_OK else None
        self.listening = False
        self._cmd_hist = []
        self._hist_idx = 0

        self._build()
        self._welcome()
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # ── CONSTRUIR UI ──────────────────────────
    def _build(self):

        # BARRA SUPERIOR
        top = tk.Frame(self.root, bg=self.BG2, height=48)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="Ω  UNIVERSAL INTEGRATION SYSTEM",
                 bg=self.BG2, fg=self.ACCENT, font=self.FONT_LG
                 ).pack(side="left", padx=15, pady=10)

        self.lbl_coh = tk.Label(top, text="C_ω = ···",
                                bg=self.BG2, fg=self.DIM, font=self.FONT_SM)
        self.lbl_coh.pack(side="right", padx=15)

        tk.Label(top, text=f"β=1/27  |  {OS}",
                 bg=self.BG2, fg=self.DIM, font=self.FONT_SM
                 ).pack(side="right", padx=5)

        # CUERPO PRINCIPAL
        body = tk.Frame(self.root, bg=self.BG)
        body.pack(fill="both", expand=True, padx=8, pady=6)

        # ── CHAT (izquierda) ──────────────────
        left = tk.Frame(body, bg=self.BG)
        left.pack(side="left", fill="both", expand=True)

        self.chat = scrolledtext.ScrolledText(
            left, wrap=tk.WORD,
            bg=self.BG, fg=self.FG, font=self.FONT,
            insertbackground=self.GREEN,
            selectbackground=self.ACCENT,
            relief="flat", bd=0,
            state="disabled", padx=10, pady=8,
        )
        self.chat.pack(fill="both", expand=True)

        # Tags
        self.chat.tag_config("user",   foreground=self.GREEN)
        self.chat.tag_config("omega",  foreground=self.FG)
        self.chat.tag_config("sys",    foreground=self.DIM)
        self.chat.tag_config("beta",   foreground=self.GOLD)
        self.chat.tag_config("ok",     foreground=self.GREEN)
        self.chat.tag_config("err",    foreground=self.RED)

        # INPUT
        inp_frame = tk.Frame(left, bg=self.BG3, pady=4)
        inp_frame.pack(fill="x", pady=(4,0))

        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            inp_frame, textvariable=self.input_var,
            bg=self.BG3, fg=self.FG,
            font=("Courier", 12),
            insertbackground=self.GREEN,
            relief="flat", bd=0,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(10,4), ipady=8)
        self.entry.bind("<Return>", self._send)
        self.entry.bind("<Up>",     self._hist_up)
        self.entry.bind("<Down>",   self._hist_down)
        self.entry.focus()

        tk.Button(inp_frame, text="ENVIAR",
                  command=self._send,
                  bg=self.ACCENT, fg="white",
                  font=("Courier", 10, "bold"),
                  relief="flat", cursor="hand2",
                  padx=12, pady=6,
                  ).pack(side="left", padx=4)

        self.btn_mic = tk.Button(
            inp_frame, text="🎤",
            command=self._mic,
            bg=self.BG2, fg=self.FG,
            font=("Courier", 14),
            relief="flat", cursor="hand2",
            padx=8, pady=4,
            state="normal" if self.listener.ok else "disabled",
        )
        self.btn_mic.pack(side="left", padx=4)

        # ── PANEL LATERAL (derecha) ───────────
        right = tk.Frame(body, bg=self.BG2, width=210)
        right.pack(side="right", fill="y", padx=(8,0))
        right.pack_propagate(False)

        tk.Label(right, text="SISTEMA", bg=self.BG2,
                 fg=self.ACCENT, font=("Courier",10,"bold")
                 ).pack(pady=(10,4))

        self.status_box = tk.Text(
            right, bg=self.BG2, fg=self.DIM,
            font=self.FONT_SM,
            relief="flat", bd=0,
            state="disabled", height=16,
        )
        self.status_box.pack(fill="both", expand=True, padx=6)

        tk.Frame(right, bg=self.ACCENT, height=1).pack(fill="x", padx=6, pady=4)

        # Botones laterales
        btns = [
            ("Estado",       self._show_status),
            ("Λ Cosmología", self._show_lambda),
            ("Memoria",      self._show_memory),
            ("Repo",         self._show_repo),
            ("Limpiar",      self._clear),
        ]
        for label, cmd in btns:
            tk.Button(right, text=label, command=cmd,
                      bg=self.BG, fg=self.FG,
                      font=self.FONT_SM,
                      relief="flat", cursor="hand2", pady=4,
                      ).pack(fill="x", padx=6, pady=2)

        # Actualiza panel cada 3s
        self._tick()

    # ── BIENVENIDA ────────────────────────────
    def _welcome(self):
        msg = (
            f"Sistema Omega activo.\n"
            f"OS: {OS}\n"
            f"β = {float(BETA):.6f}  "
            f"ε = {float(EPSILON_OBSERVER):.5f}\n"
            f"Λ = {LAMBDA_UCF:.3e}\n"
            f"Todo el repositorio está indexado como memoria.\n"
            f"Escribe, habla o usa los botones.\n"
        )
        self._append(msg, "sys")
        self.speaker.speak("Sistema Omega activo. Soy el observador.")

    # ── ENVIAR ────────────────────────────────
    def _send(self, event=None):
        text = self.input_var.get().strip()
        if not text: return
        self._cmd_hist.append(text)
        self._hist_idx = len(self._cmd_hist)
        self.input_var.set("")
        self._append(f"→ {text}", "user")
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text):
        try:
            resp = self.agent.process(text) if self.agent else "[Sin agente]"
        except Exception as e:
            resp = f"[ERROR] {e}"
        self.root.after(0, self._reply, resp)

    def _reply(self, resp):
        self._append(f"Ω  {resp}", "omega")
        # Actualiza indicador de coherencia
        if self.agent and self.agent.meta.coh_hist:
            c = self.agent.meta.coh_hist[-1]
            self.lbl_coh.config(text=f"C_ω = {c:.4f}")
        # Habla si es corto
        clean = resp[:200].replace("[VOZ]","").replace("[WEB]","").strip()
        if len(clean) < 250:
            threading.Thread(
                target=self.speaker.speak, args=(clean,), daemon=True
            ).start()

    # ── MICRÓFONO ─────────────────────────────
    def _mic(self):
        if self.listening: return
        self.listening = True
        self.btn_mic.config(bg=self.RED, text="🔴")
        self._append("Escuchando...", "sys")
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        text = self.listener.listen(timeout=7)
        self.root.after(0, self._listen_done, text)

    def _listen_done(self, text):
        self.listening = False
        self.btn_mic.config(bg=self.BG2, text="🎤")
        if text:
            self.input_var.set(text)
            self._send()
        else:
            self._append("No escuché nada.", "sys")

    # ── PANEL LATERAL ─────────────────────────
    def _tick(self):
        try:
            lines = [
                f"β = {float(BETA):.6f}",
                f"ε = {float(EPSILON_OBSERVER):.5f}",
                f"Λ = {LAMBDA_UCF:.2e}",
                "─────────────",
            ]
            if self.agent:
                st = self.agent.meta.status()
                m  = self.agent.memory
                lines += [
                    f"Acc: {st['acciones']}",
                    f"Coh: {st['coherencia_avg']}",
                    f"Mem: {m.size}",
                    f"Idx: {m.index_size}",
                    f"Fml: {len(FORMULAS)}",
                    "─────────────",
                    f"{st['sesion']}",
                ]
            self._update_text(self.status_box, "\n".join(lines))
        except Exception:
            pass
        self.root.after(3000, self._tick)

    def _show_status(self):
        if not self.agent: return
        self._append(self.agent.process("estado"), "beta")

    def _show_lambda(self):
        if not self.agent: return
        self._append(self.agent.process("calcula lambda"), "beta")

    def _show_memory(self):
        if not self.agent: return
        m = self.agent.memory
        items = list(m._mem.items())[-5:]
        lines = [f"Memoria ({m.size} entradas):"]
        for k, v in items:
            val = v.get("value","") if isinstance(v,dict) else v
            lines.append(f"  {k[:28]}: {str(val)[:50]}")
        self._append("\n".join(lines), "sys")

    def _show_repo(self):
        if not self.agent: return
        self._append(self.agent.process("qué tienes"), "sys")

    def _clear(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.config(state="disabled")

    # ── HISTORIAL ─────────────────────────────
    def _hist_up(self, e=None):
        if not self._cmd_hist: return
        self._hist_idx = max(0, self._hist_idx-1)
        self.input_var.set(self._cmd_hist[self._hist_idx])

    def _hist_down(self, e=None):
        if not self._cmd_hist: return
        self._hist_idx = min(len(self._cmd_hist), self._hist_idx+1)
        val = self._cmd_hist[self._hist_idx] if self._hist_idx < len(self._cmd_hist) else ""
        self.input_var.set(val)

    # ── HELPERS ───────────────────────────────
    def _append(self, text, tag="omega"):
        self.chat.config(state="normal")
        self.chat.insert(tk.END, f"{text}\n\n", tag)
        self.chat.see(tk.END)
        self.chat.config(state="disabled")

    def _update_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def _close(self):
        if self.agent:
            self.agent.memory.remember("last_session", {
                "ts": __import__("datetime").datetime.now().isoformat(),
                "actions": self.agent.meta.actions,
            })
        self.speaker.speak("Hasta luego.")
        self.root.destroy()

    def _fallback(self):
        if AGENT_OK:
            OmegaAgent().run(mode="text")

    def run(self):
        if HAS_TK:
            self.root.mainloop()
        else:
            self._fallback()


if __name__ == "__main__":
    OmegaUI().run()
