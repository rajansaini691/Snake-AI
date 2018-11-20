import logic
import copy
import pygame
import random
import numpy as np

class Snake:

    # Appearance
    FOOD_COLOR = (255, 0, 0)
    
    def __init__(self, weights):
        # Game variables
        self.coords = [[0, 5], [0, 4], [0, 3], [0, 2]]
        self.food = [15, 15]
        self.cur_dir = 1
        self.COLOR = (0, 0, 255)

        # AI variables
        self.fitness = 0
        self.alive = True 
        self.weights = weights 
        self.cpu = logic.Network(weights)

    def move(self, PX_HEIGHT, win_w, win_h):
        # Only moves when snake is alive
        if self.alive:
            # Copies initial coord
            head = copy.copy(self.coords[0])

            # Checking for death
            if head[0] < 0 or head[0] > win_w / PX_HEIGHT or head[1] < 0 or head[1] > win_h / PX_HEIGHT:
                self.alive = False

			# Experiment 2a: Seeing the effect commenting this line out has
			#		Result:		Initially, the snake did choose to go left, confirming my hypothesis. However, that trait died out when they tried to suicide. I believe this is because
			#					
            #for pixel in self.coords[1:]:
            #    if head == pixel:
            #        self.alive = False
        
            # Gets prediction from AI
			# Experiments for input vector: 
			# 1. Passing in head coordinate and distance from food 
            # 		ai_dir = self.cpu.getDirection([self.coords[0][0], self.coords[0][1], self.coords[0][0] - self.food[0], self.coords[0][1] - self.food[1]])
			#		Results: 	Snake only reliably eats the first piece of food; fitness ranges from 130 to 300)
			# 2. Passing in values that act like booleans: Is food above? Is food below? Is food to the left? Is food to the right?
			# 		We want a function that maps to 1 for high values of distance, and 0 for negative values of distance. This is so that everything is normalized. Sigmoid!
			#		Results: 	Snake aims for multiple pieces of food now, consistently getting scores of > 200. 
			#					This means that it knows to aim for food when it randomly changes location; major improvement over centering on a single spot
			#					The problem is that the snakes don't know to go left, so they keep running into the wall.  
			#					My theory is that the ones that go left run into themselves early on, so natural selection will breed against that trait. 
			#					If we remove the death upon hitting oneself, then they may be willing to go left. Let's test this in an experiment 2a. 
            ai_dir = self.cpu.getDirection([self.sigmoid(-self.coords[0][0] + self.food[0]), self.sigmoid(-self.food[0] + self.coords[0][0]), self.sigmoid(self.coords[0][1] - self.food[1]), self.sigmoid(self.food[1] - self.coords[0][1])])
           
            # Checks AI's decision before obeying it 
            if (ai_dir < 2 and self.cur_dir > 1) or (ai_dir > 1 and self.cur_dir < 2):
                self.cur_dir = ai_dir

            # Assigning direction
            if(self.cur_dir == 0): head[1] -= 1
            if(self.cur_dir == 1): head[1] += 1
            if(self.cur_dir == 2): head[0] -= 1
            if(self.cur_dir == 3): head[0] += 1

            # Punish fitness if moving in wrong direction
            if((head[0] - self.food[0]) ** 2 + (head[1] - self.food[1]) ** 2 > (self.coords[0][0] - self.food[0]) ** 2 + (self.coords[0][1] - self.food[1]) ** 2):
                self.fitness -= 1.5

            # Reward living
            self.fitness += 1

            # Move the snake
            self.coords.insert(0, head)

            if head != self.food:
                self.coords.pop()
            else:
                self.fitness += 100
                self.food = [random.randint(0, win_w / PX_HEIGHT), random.randint(0, win_h / PX_HEIGHT)]

    def draw(self, screen, PX_HEIGHT):
        # Draw the snake
        for coord in self.coords:
            pygame.draw.rect(screen, self.COLOR, [coord[0] * PX_HEIGHT, coord[1] * PX_HEIGHT, PX_HEIGHT, PX_HEIGHT])

        # Draw the food
        pygame.draw.rect(screen, self.FOOD_COLOR, [self.food[0] * PX_HEIGHT, self.food[1] * PX_HEIGHT, PX_HEIGHT, PX_HEIGHT]) 

    def reset(self):
        self.coords = [[0, 5], [0, 4], [0, 3], [0, 2]]
        self.fitness = 0
        self.alive = True
        self.cur_dir = 1
        self.food = [15, 15]

    def sigmoid(self, x): 
        return 1 / (1 + np.exp(-x))
