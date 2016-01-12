import math

array = sorted([float(line) for line in open("data1", "r")])

min_value, max_value = None, None
N = len(array)

Mx = 0.0
Dx = 0.0

for value in array:
    if not min_value or value < min_value:
        min_value = value
    if not max_value or value > max_value:
        max_value = value

    Mx += value / N

for value in array:
    Dx += ((value - Mx) ** 2) / N

Dx = N * Dx / (N - 1)

sigma = math.sqrt(Dx)

print("Max value =", max_value)
print("Min value=", min_value)
print("Mx =", Mx)
print("Dx =", Dx)
print("Sigma = ", sigma)
print("Min theoretical =", Mx - 3 * sigma)
print("Max theoretical =", Mx + 3 * sigma)