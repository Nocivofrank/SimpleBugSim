import numpy as np
import secrets

# architecture
input_size = 4
hidden_size = 10
output_size = 2

def random_range(a, b):
    return a + (b - a) * (secrets.randbits(52) / (1 << 52))

# weights and biases
W1 = np.array([
    [random_range(-1, 1) for _ in range(input_size)]
    for _ in range(hidden_size)
])
b1 = np.array([random_range(-1, 1) for _ in range(hidden_size)])

W2 = np.random.uniform(-1, 1, (output_size, hidden_size))
b2 = np.random.uniform(-1, 1, output_size)

# activation
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# forward pass
def forward(x):
    z1 = np.dot(W1, x) + b1
    a1 = sigmoid(z1)

    z2 = np.dot(W2, a1) + b2
    a2 = sigmoid(z2)

    return a2  # 4 outputs

def random_np_ranges(low , high, neuronLayers, neuronsPerLayer):
    random_range(low, high)

# test input
x = np.array([0.3, -0.8, 0.5, 1.0])
print(W1)
print("Network output:", forward(x))
