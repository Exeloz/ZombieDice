import math

def sigmoid_activation_multiple_integers(z):
    if z < 0:
        return 0
    if z >= 0 and z <= 1:
        return 1.0 / (1.0 + math.exp(-12*(z-0.5)))
    else:
        return sigmoid_activation_multiple_integers(z-1)+1

#config.genome_config.add_activation('my_sigmoid', sigmoid_activation_multiple_integers)
