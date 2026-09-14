class LayerPurpose:
    def __init__(self):
        self.L = 1.0      # Purpose is always fully active by definition
        self.phi = 0.0    # Always 0.0 — no friction in purpose
        self.name = "Purpose"

    def activate(self, L, phi=0.0):
        """
        Sets magnitude for the Purpose layer.
        Friction (phi) is forced to 0.0 always.
        L must be > 0 — purpose cannot be zero.
        """
        if L <= 0.0:
            raise ValueError(
                f"L6 Purpose magnitude must be > 0.0, got {L}. "
                f"A system without purpose cannot integrate."
            )
        self.L   = L
        self.phi = 0.0

    def export(self):
        return {'L': self.L, 'phi': self.phi, 'name': self.name}
