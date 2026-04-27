#!/usr/bin/env python3
"""
setup.py — Auto-instalador y lanzador
Se ejecuta solo al descargar el repo.

    python setup.py        ← instala todo y abre la UI
    python setup.py --cli  ← solo terminal
"""

import os, sys, subprocess, platform, shutil
from pathlib import Path

OS   = platform.system()
REPO = Path(__file__).parent.resolve()
PY   = sys.executable

# ── Colores ────────────────────────────────────
G="\033[92m"; Y="\033[93m"; R="\033[91m"
B="\033[94m"; W="\033[97m"; X="\033[0m"; BD="\033[1m"
if OS == "Windows": G=Y=R=B=W=X=BD=""

def banner():
    print(f"""
{B}{BD}
  ╔══════════════════════════════════════════════════╗
  ║   Ω  UNIVERSAL INTEGRATION SYSTEM               ║
  ║   Villasmil-Omega Framework  v3.3               ║
  ║   β=1/27  ε=0.02716  Λ=2.888e-122              ║
  ╚══════════════════════════════════════════════════╝
{X}""")

def log(msg, level="info"):
    icon = {"info":f"{B}→{X}", "ok":f"{G}✓{X}",
            "warn":f"{Y}!{X}", "err":f"{R}✗{X}"}
    print(f"  {icon.get(level,'→')} {msg}")

def pip(pkg):
    r = subprocess.run(
        [PY,"-m","pip","install",pkg,"-q"],
        capture_output=True
    )
    return r.returncode == 0

# ── Verificar Python ───────────────────────────
def check_python():
    log("Verificando Python...")
    v = sys.version_info
    if v.major < 3 or v.minor < 9:
        log(f"Python {v.major}.{v.minor} detectado. Necesitas 3.9+", "err")
        if OS=="Darwin":  log("brew install python3","warn")
        elif OS=="Linux": log("sudo apt install python3.11","warn")
        else:             log("https://python.org","warn")
        sys.exit(1)
    log(f"Python {v.major}.{v.minor} ✓", "ok")

# ── Instalar dependencias ──────────────────────
DEPS = [
    "requests", "psutil", "Pillow",
    "pyttsx3", "SpeechRecognition",
    "numpy", "scipy",
]

def install_all():
    log("Instalando dependencias...")
    subprocess.run([PY,"-m","pip","install","--upgrade","pip","-q"],
                   capture_output=True)
    for pkg in DEPS:
        ok = pip(pkg)
        log(pkg, "ok" if ok else "warn")
    _pyaudio()
    log("Dependencias listas", "ok")

def _pyaudio():
    try:
        import pyaudio; log("pyaudio","ok"); return
    except ImportError: pass
    log("Instalando pyaudio...")
    if OS == "Darwin":
        if shutil.which("brew"):
            subprocess.run(["brew","install","portaudio"],capture_output=True)
        pip("pyaudio")
    elif OS == "Linux":
        subprocess.run(
            ["sudo","apt-get","install","-y","python3-pyaudio","portaudio19-dev"],
            capture_output=True
        )
        pip("pyaudio")
    elif OS == "Windows":
        pip("pipwin")
        subprocess.run([PY,"-m","pipwin","install","pyaudio"],capture_output=True)

# ── Crear lanzador nativo ──────────────────────
def create_launcher():
    log("Creando lanzador...")
    if OS == "Darwin":
        app = REPO / "OmegaAgent.app" / "Contents" / "MacOS"
        app.mkdir(parents=True, exist_ok=True)
        exe = app / "OmegaAgent"
        exe.write_text(
            f"#!/bin/bash\ncd '{REPO}'\n{PY} '{REPO}/omega_ui.py'\n"
        )
        exe.chmod(0o755)
        plist = app.parent / "Info.plist"
        plist.write_text(
            '<?xml version="1.0"?>\n'
            '<plist version="1.0"><dict>\n'
            '<key>CFBundleName</key><string>OmegaAgent</string>\n'
            '<key>CFBundleExecutable</key><string>OmegaAgent</string>\n'
            '</dict></plist>\n'
        )
        log("OmegaAgent.app → doble clic para abrir","ok")

    elif OS == "Linux":
        d = Path.home()/"Desktop"/"OmegaAgent.desktop"
        d.write_text(
            "[Desktop Entry]\nType=Application\nName=Omega Agent\n"
            f"Exec={PY} {REPO}/omega_ui.py\nPath={REPO}\n"
            "Terminal=false\nCategories=Science;\n"
        )
        d.chmod(0o755)
        log("Acceso directo creado en Desktop","ok")

    elif OS == "Windows":
        # .bat visible
        bat = REPO / "OmegaAgent.bat"
        bat.write_text(
            f'@echo off\ncd /d "{REPO}"\n"{PY}" "{REPO}\\omega_ui.py"\n'
        )
        # .vbs sin ventana de terminal
        vbs = REPO / "OmegaAgent.vbs"
        vbs.write_text(
            f'Set ws = CreateObject("WScript.Shell")\n'
            f'ws.Run Chr(34) & "{REPO}\\OmegaAgent.bat" & Chr(34), 0\n'
        )
        log("OmegaAgent.bat y .vbs creados → doble clic","ok")

# ── Crear start scripts ────────────────────────
def create_scripts():
    # macOS / Linux
    sh = REPO / "start.sh"
    sh.write_text(
        f'#!/bin/bash\ncd "$(dirname "$0")"\n{PY} omega_ui.py\n'
    )
    sh.chmod(0o755)

    # Windows
    bat = REPO / "start.bat"
    bat.write_text(
        f'@echo off\ncd /d "%~dp0"\n"{PY}" omega_ui.py\npause\n'
    )
    log("start.sh y start.bat creados","ok")

# ── LANZAR ─────────────────────────────────────
def launch(cli=False):
    log("Iniciando Omega Agent...")
    if cli:
        subprocess.run([PY, str(REPO/"omega_agent.py")])
    else:
        subprocess.run([PY, str(REPO/"omega_ui.py")])

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--cli",     action="store_true", help="Solo terminal")
    p.add_argument("--install", action="store_true", help="Solo instalar")
    args = p.parse_args()

    banner()
    check_python()
    install_all()
    create_scripts()
    create_launcher()

    if not args.install:
        log("Todo listo. Abriendo...\n", "ok")
        launch(cli=args.cli)
