import numpy as np
import secrets

class Brain:

    #brian row and columns
    input_size = 12
    hidden_size = 10
    output_size = 4
    
    def __init__(self):
        # weights and biases
        self.W1 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.input_size)]
            for _ in range(Brain.hidden_size)])

        self.b1 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.hidden_size)])

        self.W2 = np.array([[Brain.random_range(-1, 1) for _ in range(Brain.hidden_size)]
            for _ in range(Brain.output_size)])

        self.b2 = np.array([Brain.random_range(-1, 1) for _ in range(Brain.output_size)])
        
        self.information = np.array([0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0 , 0])
        # 0 size
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


    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def brainThink(self, x = np.array([0,0,0,0,0,0,0,0,0,0,0,0])):
        # Shared hidden layer
        z1 = np.dot(self.W1, x) + self.b1
        hidden = Brain.sigmoid(z1)

        # Output head 1
        z2 = np.dot(self.W2, hidden) + self.b2
        out = Brain.sigmoid(z2)
        if out[0] > out[1]:
            self.direction[0] = out[0]
        else:
            self.direction[0] = -out[1]

        if out[2] > out[3]:
            self.direction[1] = out[2]
        else:
            self.direction[1] = -out[3]

    def random_range(a, b):
        return a + (b - a) * (secrets.randbits(52) / (1 << 52))