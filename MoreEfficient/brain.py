import numpy as np
import secrets

class Brain():

    #brian row and columns
    input_size = 16
    hidden_size = 20
    hidden2_size = 20
    hidden3_size = 20
    output_size = 4
    
    def __init__(self):
        # weights and biases
        #for input size
        self.W1 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.input_size)]
            for _ in range(Brain.hidden_size)])

        self.b1 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.hidden_size)])

        #for hidden 1
        self.W2 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.hidden_size)] 
            for _ in range(Brain.hidden2_size)])

        self.b2 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.hidden2_size)])

        #for hidden 2
        self.W3 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.hidden2_size)]
            for _ in range(Brain.hidden3_size)])

        self.b3 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.hidden3_size)])

        #for output
        self.W4 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.hidden3_size)]
            for _ in range(Brain.output_size)])

        self.b4 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.output_size)])


        
        self.information = np.array([0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0])
        # 0 amount near
        # 1 direction 1
        # 2 direction 2
        # 3 speed
        # 4 other bug pos 1
        # 5 other bug pos 2
        # 6 other bug color
        # 7 other bug attack
        # 8 other bug defense
        # 9 self attack
        # 10 self defense
        # 11 accuracy 
        # 12 amount reproduced
        # 13 time alive
        # 14 mouse x
        # 15 mouse y

    def sigmoid(x):
        return np.where(
            x >= 0,
            1 / (1 + np.exp(-x)),
            np.exp(x) / (1 + np.exp(x))
        )

    def brainThink(self):
        # Layer 1
        z1 = np.dot(self.W1, self.information) + self.b1
        h1 = Brain.sigmoid(z1)

        # Layer 2
        z2 = np.dot(self.W2, h1) + self.b2
        h2 = Brain.sigmoid(z2)

        # Layer 3
        z3 = np.dot(self.W3, h2) + self.b3
        h3 = Brain.sigmoid(z3)

        # Output layer
        z4 = np.dot(self.W4, h3) + self.b4
        out = Brain.sigmoid(z4)

        z5 = np.dot(self.W4, h3) + self.b4
        action = Brain.sigmoid(z5)

        return out, action

    def brainMutate(self, chance = 0.1, strength = 0.2):
        layers = [
            self.W1, self.b1,
            self.W2, self.b2,
            self.W3, self.b3,
            self.W4, self.b4
        ]

        for layer in layers:
            mask = np.random.rand(*layer.shape) < chance

            mutation = np.random.uniform(-strength, strength, layer.shape)
            
            layer += mask * mutation

    def random_range(a, b):
        return a + (b - a) * (secrets.randbits(52) / (1 << 52))