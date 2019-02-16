import pygame
import sys
import random
import numpy as np
import copy

import logic
import entities

# Function definitions
def restart():
    global snake
    snake = [[0, 5], [0, 4], [0, 3], [0, 2]]
    
    global food
    food = [15, 15]

    global cur_dir
    cur_dir = 1
    
    # Only mutate if AI improves; otherwise, revert
    global oldFitness
    global best_weights
    global weights
    global fitness

    if fitness > oldFitness:
        oldFitness = fitness
        best_weights = weights
        mutate(weights)
        print("We improved!")
    else:
        weights = best_weights[:] 
        mutate(weights)
    
    fitness = 0
    
# Returns a new weights matrix with 1/4 of values mutated
def mutate(snake):
    weights = copy.deepcopy(snake.weights)

    for layer in weights:
        # Array of booleans with same shape as layer. Values that are true get mutated. 
        mask = np.logical_not(np.random.randint(0, 4, size = layer.shape).astype(np.bool))

        # Array of random values
        r = np.random.rand(*layer.shape) * 20 - 10

        # Indices where mask is true get mutated
        layer[mask] += r[mask]

    return weights 

# Returns a new matrix with randomly chosen values from the two given
def breed(s1, s2):
	w1 = copy.deepcopy(s1.weights)
	w2 = copy.deepcopy(s2.weights)
	for l1, l2 in zip(w1, w2):
		mask = np.logical_not(np.random.randint(0, 1, size = l1.shape).astype(np.bool))
		l1[mask] = l2[mask]

	return w1
	

def on_death():
	# Process the snakes' fitnesses
	snakes.sort(key = lambda snake : snake.fitness, reverse = True)

	snakes[0].print_score();
	print("Highest fitness score: " + str(snakes[0].fitness))
 
	snakes[0].COLOR = (0, 0, 0)
	snakes[0].reset()
	snakes[1].COLOR = (0, 0, 0)
	snakes[1].reset()
    
	# Sets all snakes to a bred version of the top two ones, then mutates them for variability
	for snake in snakes[2:]:
		snake.weights[:] = breed(snakes[0], snakes[1]) 
		snake.weights[:] = mutate(snake)
		snake.reset()
		snake.COLOR = (0, 0, 255)
    
# Game initializations
pygame.init()

size = (1000, 2000)
screen = pygame.display.set_mode(size)

win_w, win_h = pygame.display.get_surface().get_size()

done = False

clock = pygame.time.Clock()

# Constants
PX_HEIGHT = 15
dir_mapping = {0: "up", 1: "down", 2: "left", 3: "right"}

# Making snakes
snakes = []
for i in range(0, 20):
    # AI weights
    weights = []
    shape = (6, 5, 4)

    for i in range(0, len(shape) - 1):
        w = np.random.rand(shape[i] + 1, shape[i + 1] )
        w *= 24
        w -= 12
        w[-1] *= 1.5

        weights.append(w)

    # Adding a new snake
    snakes.append(entities.Snake(weights, PX_HEIGHT, win_w, win_h))
   

while not done:

    # User events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    
    # Key input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_v]:             # Kills all snakes if user presses V
        for snake in snakes:
            snake.alive = False

    # Updating
    for snake in snakes:
        snake.move()
    
    # Drawing
    screen.fill((255, 255, 255))
    for snake in snakes:
        snake.draw(screen)

    # Checking deaths
    anyAlive = False
    for snake in snakes:
        anyAlive = anyAlive or snake.alive
    
    if anyAlive == False:
        on_death()

    # Pygame stuff
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

