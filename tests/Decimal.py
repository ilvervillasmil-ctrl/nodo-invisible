from decimal import Decimal, getcontext
import mpmath

# Configuramos la precisión para manejar números con miles de dígitos
getcontext().prec = 10000  # Precisión de 10,000 dígitos (suficiente para 1000 dígitos finales)

# Calculamos sqrt(pi) con alta precisión usando mpmath
mpmath.mp.dps = 10000  # Dígitos de precisión en mpmath
sqrt_pi = Decimal(str(mpmath.sqrt(mpmath.pi)))

# Calculamos 11^37 y 37^37
a = Decimal(11) ** 37
b = Decimal(37) ** 37 * sqrt_pi

# Suma
suma = a + b

# Convertimos a string para extraer los últimos 1000 dígitos
suma_str = str(suma)

# Mostramos los últimos 1000 dígitos
ultimos_1000 = suma_str[-1000:]
print("Últimos 1000 dígitos de la suma:")
print(ultimos_1000)
