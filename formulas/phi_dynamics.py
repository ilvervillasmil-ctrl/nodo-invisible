from formulas.constants import PHI
import math

class PhiDynamics:
    @staticmethod
    def golden_spiral(radius: float, angle_step: float = 137.507764) -> list:
        """
        Computes the golden spiral points.
        
        radius: The initial radius.
        angle_step: Golden angle in degrees (default ≈ 137.5°).
        """
        points = []
        angle = 0
        for _ in range(100):  # Limit to 100 points for now
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            points.append((x, y))
            angle += angle_step
            radius *= PHI  # Expand the radius using the golden ratio
        return points

    @staticmethod
    def phi_scaling(series: list) -> list:
        """
        Scales a given series based on the golden ratio.
        """
        return [value * PHI for value in series]
