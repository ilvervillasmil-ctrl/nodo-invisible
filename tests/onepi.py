import math
import pytest

A = 11
B = 37
n = 37

resultado = ((A**n + B**n)**(1/n)) / math.sqrt(math.pi)

if abs(resultado - 1.0) > 1e-12:
    raise ValueError(f"ERROR: el resultado es {resultado}, no es 1.")

print("Resultado correcto:", resultado)
