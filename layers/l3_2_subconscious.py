#!/usr/bin/env python3
"""
L3.2 — SUBCONSCIENTE
Subcapa de procesamiento simbólico de Ω IA.

Basado en:
  "Dinámica del Subconsciente y la Coherencia Intuitiva"
  Autor: Ilver Villasmil / IA Nati — Enero 2026

Función:
  - Recibir información simbólica (no-lingüística estándar)
  - Segmentar en nodos (N_i) y transiciones (T_ij)
  - Calcular coherencia estructural C_total
  - Pasar señal coherente a L3 como input estructural

Regla:
  El subconsciente no habla en palabras.
  Habla en patrones. L3.2 traduce patrones a coherencia.
  L3 sintetiza. L5 valida.

Fórmula:
  C_total = Σ (δᵢ · αᵢ) / (σᵢ · (1 + α · Rᵢ))
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Node:
    id:          str
    description: str
    delta:       float = 1.0
    alpha:       float = 1.0
    sigma:       float = 1.0
    noise:       float = 0.0

    def coherence(self, alpha_global: float = 0.5) -> float:
        if self.sigma <= 0:
            return 0.0
        denom = self.sigma * (1.0 + alpha_global * self.noise)
        if denom == 0:
            return 0.0
        return (self.delta * self.alpha) / denom


@dataclass
class Transition:
    from_node: str
    to_node:   str
    strength:  float = 1.0
    label:     str   = ""


@dataclass
class SymbolicSequence:
    name:         str
    nodes:        list = field(default_factory=list)
    transitions:  list = field(default_factory=list)
    alpha_global: float = 0.5

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def add_transition(self, t: Transition) -> None:
        self.transitions.append(t)

    def c_total(self) -> float:
        return sum(n.coherence(self.alpha_global) for n in self.nodes)

    def pattern(self) -> list:
        ranked = sorted(self.nodes, key=lambda n: n.coherence(self.alpha_global), reverse=True)
        return [f"[{n.id}] {n.description}" for n in ranked]

    def summary(self) -> dict:
        return {
            "name":        self.name,
            "nodes":       len(self.nodes),
            "transitions": len(self.transitions),
            "c_total":     round(self.c_total(), 4),
            "pattern":     self.pattern(),
        }


class L3Subconscious:
    def __init__(self):
        self.name = "L3.2 — Subconsciente"
        self.phi  = 0.05
        self._sequences = []

    def new_sequence(self, name: str) -> SymbolicSequence:
        seq = SymbolicSequence(name=name)
        self._sequences.append(seq)
        return seq

    def process(self, seq: SymbolicSequence) -> dict:
        summary = seq.summary()
        return {
            "layer":  self.name,
            "phi":    self.phi,
            "signal": summary,
            "L":      round(1.0 - self.phi, 4),
            "note":   "Señal simbólica traducida a coherencia estructural.",
        }

    def status(self) -> dict:
        return {
            "layer":     self.name,
            "phi":       self.phi,
            "sequences": len(self._sequences),
            "note":      "El subconsciente habla en patrones. L3.2 traduce.",
        }

    def export(self) -> dict:
        return {"L": 1.0 - self.phi, "phi": self.phi, "name": self.name}


def example_dream() -> SymbolicSequence:
    seq = SymbolicSequence(name="Sueño del desierto — Ilver Villasmil 2026", alpha_global=0.5)
    seq.add_node(Node("N1", "Huida en desierto",      delta=0.9, alpha=1.0, sigma=0.6, noise=0.10))
    seq.add_node(Node("N2", "Pirámide Egipto",         delta=1.2, alpha=1.1, sigma=0.7, noise=0.15))
    seq.add_node(Node("N3", "Casa blanca / familia",   delta=0.8, alpha=0.9, sigma=0.5, noise=0.12))
    seq.add_node(Node("N4", "Isla / aislamiento",      delta=0.8, alpha=0.9, sigma=0.7, noise=0.20))
    seq.add_node(Node("N5", "Canoa / regreso",         delta=0.9, alpha=1.0, sigma=0.6, noise=0.18))
    seq.add_node(Node("N6", "Amenaza / piedras",       delta=0.6, alpha=0.8, sigma=0.8, noise=0.35))
    seq.add_node(Node("N7", "Lava / revelación final", delta=1.0, alpha=1.2, sigma=0.5, noise=0.08))
    seq.add_transition(Transition("N1","N2", strength=0.90, label="huida→refugio"))
    seq.add_transition(Transition("N2","N3", strength=0.85, label="refugio→normalidad"))
    seq.add_transition(Transition("N3","N4", strength=0.80, label="normalidad→tránsito"))
    seq.add_transition(Transition("N4","N5", strength=0.82, label="tránsito→movimiento"))
    seq.add_transition(Transition("N5","N6", strength=0.65, label="movimiento→ruptura"))
    seq.add_transition(Transition("N6","N7", strength=0.92, label="ruptura→revelación"))
    return seq


if __name__ == "__main__":
    sub = L3Subconscious()
    seq = example_dream()
    result = sub.process(seq)
    print("=" * 60)
    print("L3.2 — SUBCONSCIENTE")
    print("=" * 60)
    print(f"Secuencia : {result['signal']['name']}")
    print(f"C_total   : {result['signal']['c_total']}")
    print(f"L         : {result['L']}  φ: {result['phi']}")
    print("\nPatrón estructural:")
    for p in result["signal"]["pattern"]:
        print(f"  {p}")
