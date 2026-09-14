import math
from formulas.energy import LayerEnergy
from formulas.constants import PHI, NUM_LAYERS, LAYER_FRICTION


def test_frequency_layer_0():
    """Layer 0 frequency = PHI^0 = 1.0"""
    assert LayerEnergy.frequency(0) == 1.0


def test_frequency_layer_3():
    """Layer 3 frequency = PHI^(3/2)"""
    expected = PHI ** (3 / 2)
    assert abs(LayerEnergy.frequency(3) - expected) < 1e-10


def test_frequency_increases_with_layer():
    """Higher layers vibrate faster."""
    freqs = LayerEnergy.all_frequencies()
    for i in range(len(freqs) - 1):
        assert freqs[i] < freqs[i + 1]


def test_compute_full_activation_no_friction():
    """E = 1.0 * (1-0) * freq = freq"""
    for i in range(NUM_LAYERS):
        e = LayerEnergy.compute(1.0, 0.0, i)
        assert abs(e - LayerEnergy.frequency(i)) < 1e-10


def test_compute_zero_activation():
    """Zero activation = zero energy."""
    for i in range(NUM_LAYERS):
        assert LayerEnergy.compute(0.0, 0.1, i) == 0.0


def test_compute_full_friction():
    """Full friction = zero energy."""
    for i in range(NUM_LAYERS):
        assert LayerEnergy.compute(1.0, 1.0, i) == 0.0


def test_compute_all_default_frictions():
    """compute_all uses LAYER_FRICTION by default."""
    activations = [1.0] * NUM_LAYERS
    energies = LayerEnergy.compute_all(activations)
    assert len(energies) == NUM_LAYERS
    for i, e in enumerate(energies):
        expected = (1.0 - LAYER_FRICTION[i]) * LayerEnergy.frequency(i)
        assert abs(e - expected) < 1e-10


def test_compute_all_custom_frictions():
    """compute_all with custom frictions."""
    activations = [0.5] * NUM_LAYERS
    frictions = [0.0] * NUM_LAYERS
    energies = LayerEnergy.compute_all(activations, frictions)
    for i, e in enumerate(energies):
        expected = 0.5 * LayerEnergy.frequency(i)
        assert abs(e - expected) < 1e-10


def test_all_frequencies_length():
    """all_frequencies returns 7 values."""
    assert len(LayerEnergy.all_frequencies()) == NUM_LAYERS
