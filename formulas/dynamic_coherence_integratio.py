"""
Universal Coherence Framework v4.0
Dynamic Interaction Field Model

Author: Ilver Villasmil
Extended by dynamic coherence integration
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional
from collections import deque


# ============================================================
# CORE CONSTANTS
# ============================================================

THETA_CUBE     = 11.096
PHI_CRITICAL   = 2 * math.pi
BETA           = 1e-5

MAX_COHERENCE  = 1.0
MEMORY_DECAY   = 0.92
ADAPT_RATE     = 0.05

LOOP_WINDOW    = 5
LOOP_VARIANCE  = 1e-4
LOOP_THRESHOLD = 0.95


# ============================================================
# VECTOR COHERENCE
# ============================================================

@dataclass
class CoherenceVector:
    logical:   float = 0.0
    semantic:  float = 0.0
    temporal:  float = 0.0
    reflective: float = 0.0

    def magnitude(self) -> float:
        return math.sqrt(
            self.logical**2 +
            self.semantic**2 +
            self.temporal**2 +
            self.reflective**2
        )

    def normalize(self):
        mag = self.magnitude()
        if mag < BETA:
            return self
        return CoherenceVector(
            self.logical / mag,
            self.semantic / mag,
            self.temporal / mag,
            self.reflective / mag,
        )

    def dot(self, other) -> float:
        return (
            self.logical * other.logical +
            self.semantic * other.semantic +
            self.temporal * other.temporal +
            self.reflective * other.reflective
        )


# ============================================================
# GEOMETRIC INTERACTION
# ============================================================

class DynamicInteraction:

    @staticmethod
    def angle(v1: CoherenceVector,
              v2: CoherenceVector) -> float:

        mag = v1.magnitude() * v2.magnitude()

        if mag < BETA:
            return math.pi / 2

        cos_theta = max(-1.0, min(1.0, v1.dot(v2) / mag))
        return math.acos(cos_theta)

    @staticmethod
    def interference(c1: float,
                     c2: float,
                     theta: float) -> float:

        value = (
            c1**2 +
            c2**2 +
            2 * c1 * c2 * math.cos(theta)
        )

        return math.sqrt(max(0.0, value))

    @staticmethod
    def saturate(c: float) -> float:
        return math.tanh(c)


# ============================================================
# DYNAMIC OSCILLATOR
# ============================================================

@dataclass
class DynamicState:

    theta: float = THETA_CUBE
    velocity: float = 0.0
    phi: float = 0.5
    coherence: float = 0.0

    def evolve(self,
               force: float,
               dt: float = 1.0):

        acceleration = (
            force
            - self.phi * self.velocity
            - math.pi**2 * (self.theta - THETA_CUBE)
        )

        self.velocity += acceleration * dt
        self.theta += self.velocity * dt

        return self.theta


# ============================================================
# SESSION FIELD
# ============================================================

@dataclass
class SessionField:

    state: DynamicState = field(default_factory=DynamicState)

    memory: float = 0.0

    history: deque = field(
        default_factory=lambda: deque(maxlen=100)
    )

    def update(self,
               self_vector: CoherenceVector,
               external_vector: CoherenceVector):

        c1 = self_vector.magnitude()
        c2 = external_vector.magnitude()

        theta = DynamicInteraction.angle(
            self_vector,
            external_vector
        )

        interaction = DynamicInteraction.interference(
            c1,
            c2,
            theta
        )

        interaction = DynamicInteraction.saturate(interaction)

        # Temporal memory integration
        self.memory = (
            MEMORY_DECAY * self.memory +
            (1 - MEMORY_DECAY) * interaction
        )

        # Adaptive friction
        alignment = 1.0 - theta / math.pi

        self.state.phi += (
            ADAPT_RATE * (1.0 - alignment)
        )

        self.state.phi = max(
            0.01,
            min(self.state.phi, PHI_CRITICAL)
        )

        # Dynamic evolution
        theta_state = self.state.evolve(
            force=self.memory
        )

        self.state.coherence = interaction

        self.history.append({
            "theta": theta_state,
            "coherence": interaction,
            "alignment": alignment,
            "phi": self.state.phi,
        })

        return interaction

    def detect_loop(self):

        if len(self.history) < LOOP_WINDOW:
            return False

        recent = [
            h["coherence"]
            for h in list(self.history)[-LOOP_WINDOW:]
        ]

        variance = max(recent) - min(recent)

        return (
            min(recent) > LOOP_THRESHOLD and
            variance < LOOP_VARIANCE
        )

    def regime(self):

        if abs(self.state.phi - PHI_CRITICAL) < BETA:
            return "CRITICAL"

        if self.state.phi < PHI_CRITICAL:
            return "ALIVE"

        return "DEAD"
