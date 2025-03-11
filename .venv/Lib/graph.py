import matplotlib.pyplot as plt

# Дано
frequency = [7, 76, 760, 7600, 76000]
amplitude = [439.133, 99.333, 0.319116, 102.852, 658.036]

# Побудова графіка
plt.figure(figsize=(8, 6))
plt.plot(frequency, amplitude, marker='o', linestyle='-', color='b')

# Додавання підписів
plt.title("Залежність амплітуди від частоти")
plt.xlabel("Частота (Гц)")
plt.ylabel("Амплітуда")

# Логарифмічна шкала для осі X
plt.xscale('log')

# Відображення графіка
plt.grid(True)
plt.show()