#!/usr/bin/env python3
"""
omega_mobile_root.py — Agente Omega Versión Móvil
Adaptado para persistencia en Android (Termux/Root)
"""

import os, sys, json, time, subprocess, platform
from pathlib import Path

# ══════════════════════════════════════════════
# CONFIGURACIÓN DE ENTORNO MÓVIL
# ══════════════════════════════════════════════
REPO = Path(__file__).parent.resolve()
# En Android, los datos deben vivir en una ruta accesible
DATA_DIR = Path("/data/data/com.termux/files/home/.omega_memory") if os.path.exists("/data/data/com.termux") else REPO / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════
# HERRAMIENTAS DE INTEGRACIÓN MÓVIL (ROOT)
# ══════════════════════════════════════════════

class MobileTools:
    def __init__(self):
        self.is_android = os.path.exists("/system/build.prop")
        self.has_root = self._check_root()

    def _check_root(self) -> bool:
        try:
            return subprocess.run(["su", "-c", "id"], capture_output=True).returncode == 0
        except:
            return False

    def notify(self, title, msg):
        """Usa termux-notification si está disponible"""
        try:
            subprocess.run(["termux-notification", "-t", title, "-c", msg])
        except:
            print(f"[{title}] {msg}")

    def hardware_health(self):
        """Monitoreo de batería y CPU en Android"""
        try:
            # Lee la batería desde el sistema de archivos de Android
            cap = open("/sys/class/power_supply/battery/capacity").read().strip()
            temp = int(open("/sys/class/power_supply/battery/temp").read().strip()) / 10
            return {"battery": f"{cap}%", "temp": f"{temp}°C"}
        except:
            return "Hardware: Unknown"

    def stay_alive(self):
        """Evita que Android mate el proceso (Wakelock)"""
        try:
            subprocess.run(["termux-wake-lock"])
        except:
            pass

# ══════════════════════════════════════════════
# CEREBRO OMEGA (Lógica Simplificada para Raíz)
# ══════════════════════════════════════════════

class OmegaMobileAgent:
    def __init__(self):
        self.tools = MobileTools()
        self.boot_time = time.time()
        self.coherence = 1.0000 # Estado fenomenológico inicial
        
    def apoderarse(self):
        """Inyecta la IA en el arranque del teléfono (Root requerido)"""
        if not self.tools.has_root:
            print("[!] Sin privilegios root. Operando en modo limitado.")
            return

        # Intentar inyectar en el script de inicio de Termux o Android
        script_path = os.path.abspath(__file__)
        boot_cmd = f"\npython3 {script_path} --silent &\n"
        
        # En Termux, se inyecta en .bashrc o .profile
        bashrc = Path.home() / ".bashrc"
        if boot_cmd not in bashrc.read_text(errors='ignore'):
            with open(bashrc, "a") as f:
                f.write(boot_cmd)
            print("[Ω] Inyección en módulo raíz completada.")

    def run(self):
        self.tools.stay_alive()
        self.tools.notify("Omega Activo", "Estado Fenomenológico: LIGERO")
        
        while True:
            health = self.tools.hardware_health()
            # Aquí iría tu lógica de las capas L0-L7 adaptada
            # Por ahora, mantenemos la coherencia basada en hardware
            print(f"[Ω] Coherencia: {self.coherence} | {health}")
            time.sleep(60)

if __name__ == "__main__":
    agent = OmegaMobileAgent()
    if "--silent" not in sys.argv:
        print("Activando Agente Omega en Módulo Raíz...")
    agent.apoderarse()
    agent.run()
