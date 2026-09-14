# layers/l7_integration.py

from formulas.constants import ALPHA


class LayerIntegration:
    """
    L7 -- Integracion Total del Sistema

    L7 es emergente. No se declara. No se activa directamente.
    Es la consecuencia inevitable del producto multiplicativo
    de todas las capas L0-L6.

    L6 orienta. L7 verifica.

    Si cualquier capa es cero, L7 = 0.
    Si todas las capas cooperan, L7 > 0.
    L7 no puede fingirse.

    Ley 8: Integracion Total
    TODO LO QUE NO SE INTEGRA COLAPSA
    """

    def __init__(self):
        self.name  = "Integration"
        self.value = 0.0
        self.phi   = 0.0  # L7 no tiene friccion -- es resultado, no proceso

    def compute(self, layers_data):
        """
        Calcula L7 como el producto multiplicativo de L0-L6.

        layers_data: lista de 7 dicts con keys 'L' y 'phi'
        correspondientes a L0, L1, L2, L3, L4, L5, L6.

        Retorna el valor de integracion total entre 0 y ALPHA.
        """
        if len(layers_data) != 7:
            raise ValueError(
                f"L7 requiere exactamente 7 capas (L0-L6), "
                f"recibio {len(layers_data)}"
            )

        product = 1.0
        for i, layer in enumerate(layers_data):
            L   = layer['L']
            phi = layer['phi']
            contribution = L * (1 - phi)
            if contribution < 0:
                raise ValueError(
                    f"Capa L{i}: contribucion negativa imposible. "
                    f"L={L}, phi={phi}"
                )
            product *= contribution

        # L7 nunca puede superar ALPHA -- beta es irreducible
        self.value = min(ALPHA, product)
        return self.value

    def is_integrated(self):
        """
        El sistema esta integrado si L7 > 0.
        Si L7 = 0, alguna capa colapso.
        """
        return self.value > 0.0

    def export(self):
        return {
            'L':    self.value,
            'phi':  self.phi,
            'name': self.name,
        }
