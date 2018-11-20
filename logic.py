import numpy as np
import random

class Network:
    # Follows a feedforward network model. If given an array, set weights to the array. If given a tuple, initialize network with random weights and tuple's shape 
    def __init__(self, weights):
        self.weights = weights

    # Inputs is the input vector passed to the network. The direction is computed with the weights the network was given 
    # Returns 0 - UP, 1 - DOWN, 2 - LEFT, 3 - RIGHT
    def getDirection(self, inputs):

        # Helper function used to normalize weighted sum
        def sigmoid(num):
            return 1 / (1 + np.exp(-num))

        prev_input = np.copy(inputs)
        new_input = np.array([])

        for layer in self.weights:
            # Separate bias vector from weights; 0th column is bias
            bias = layer[-1, :]
            W = layer[:-1, :]

            # Compute weighted sum
            new_input = np.dot(W.transpose(), prev_input) + bias 
            
            # Apply sigmoid to normalize each value of the new vector
            new_input = np.vectorize(sigmoid)(new_input)
            
            # Store that vector so it can be used as an input to the next layer
            prev_input = new_input

        # Returns the highest index of the output matrix
        return np.argmax(new_input) 

    def test():
        # Stores the network's weights as a list of numpy arrays
        weights = []

        # Number of neurons in each layer: 8 in input layer, 5 in hidden layer, and 4 in output layer
        shape = (8, 5, 4)

        for i in range(0, len(shape) - 1): 
            # Initializes a matrix with shape (prev x curr) with random values
            w = np.random.rand(shape[i], shape[i + 1]) 
            
            # Scales the random values to go between -5 and 5
            w = np.multiply(w, -10) + 5
            
            # Stores the weights matrix in the global weight matrix
            weights.append(w)
            
        # Prints the output
        print("Output: ")
        print(getDirection(weights, np.array([24, -3, 10, 24, 0, 0, 0, 1])))

        # Prints the input
        print("Input matrix: ")
        print(weights)
