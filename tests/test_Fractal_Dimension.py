import pytest
import math
from formulas.fractality import Fractality
from formulas.constants import PHI


class TestFractalDimension:
    def test_level_one(self):
        """Level 1 = log(PHI)."""
        result = Fractality.calculate_fractal_dimension(1)
        assert math.isclose(result, math.log(PHI), rel_tol=1e-9)

    def test_level_seven(self):
        """7 layers = 7 * log(PHI)."""
        result = Fractality.calculate_fractal_dimension(7)
        assert math.isclose(result, 7 * math.log(PHI), rel_tol=1e-9)

    def test_custom_base(self):
        """Custom base works correctly."""
        result = Fractality.calculate_fractal_dimension(3, base=2.0)
        assert math.isclose(result, 3 * math.log(2.0), rel_tol=1e-9)

    def test_level_zero_raises(self):
        """Level 0 raises ValueError."""
        with pytest.raises(ValueError):
            Fractality.calculate_fractal_dimension(0)

    def test_negative_level_raises(self):
        """Negative level raises ValueError."""
        with pytest.raises(ValueError):
            Fractality.calculate_fractal_dimension(-1)

    def test_scaling_is_linear(self):
        """Fractal dimension scales linearly with level."""
        d2 = Fractality.calculate_fractal_dimension(2)
        d4 = Fractality.calculate_fractal_dimension(4)
        assert math.isclose(d4, 2 * d2, rel_tol=1e-9)


class TestFractalEnergyDistribution:
    def test_seven_levels(self):
        """7 levels produce 7 energy values."""
        result = Fractality.fractal_energy_distribution(1.0, 7)
        assert len(result) == 7

    def test_energies_decrease(self):
        """Each level gets less energy than the previous."""
        result = Fractality.fractal_energy_distribution(1.0, 7)
        for i in range(len(result) - 1):
            assert result[i] > result[i + 1]

    def test_total_less_than_input(self):
        """Sum of distributed energies < total (some remains)."""
        result = Fractality.fractal_energy_distribution(1.0, 5)
        assert sum(result) < 1.0

    def test_first_energy_is_total_over_phi(self):
        """First level gets total/PHI."""
        result = Fractality.fractal_energy_distribution(10.0, 3)
        assert math.isclose(result[0], 10.0 / PHI, rel_tol=1e-9)

    def test_zero_energy_raises(self):
        """Zero energy raises ValueError."""
        with pytest.raises(ValueError):
            Fractality.fractal_energy_distribution(0, 3)

    def test_negative_energy_raises(self):
        """Negative energy raises ValueError."""
        with pytest.raises(ValueError):
            Fractality.fractal_energy_distribution(-1.0, 3)

    def test_zero_iterations_raises(self):
        """Zero iterations raises ValueError."""
        with pytest.raises(ValueError):
            Fractality.fractal_energy_distribution(1.0, 0)
