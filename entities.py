import logic
import math
import copy
import pygame
import random
import numpy as np
import sys

class Snake:

    # Appearance
    FOOD_COLOR = (255, 0, 0)
    
    def __init__(self, weights, PX_HEIGHT, win_w, win_h):
        # Game variables
        self.coords = [[0, 5], [0, 4], [0, 3], [0, 2]]
        self.food = [random.randint(0, win_w/PX_HEIGHT), random.randint(0, win_h/PX_HEIGHT)]
        self.cur_dir = 1
        self.COLOR = (0, 0, 255)

		# Window variables
        self.PX_HEIGHT = PX_HEIGHT
        self.win_w = win_w
        self.win_h = win_h

        # AI variables
        self.fitness = 0
        self.alive = True 
        self.weights = weights 
        self.cpu = logic.Network(weights)

		# Needed for experiment 2c, which raises the reward with each food eaten.
        self.food_count = 0

		# For experiment 2d, which punishes snake by a diminishing amount for running into the wall
        self.frames_survived = 0
		
		# Separates scores before adding together
        self.pills_eaten = 0
        self.dir_punishment = 0
        self.collision_punishment = 0

    def move(self):
        # Only moves when snake is alive
        if self.alive:
            # Copies initial coord
            head = copy.copy(self.coords[0])

            # Checking for death
            if head[0] < 0 or head[0] > self.win_w / self.PX_HEIGHT or head[1] < 0 or head[1] > self.win_h / self.PX_HEIGHT:
                #self.fitness -= 200 / (self.frames_survived + 20)
				
                self.alive = False

			# Experiment 2a: Seeing the effect commenting this line out has
			#		Result:		Initially, the snake did choose to go left, confirming my hypothesis. However, that trait died out later on when they started consistently scoring higher.
			#					I believe this is because they were trying to suicide, since I lowered their score every time they moved away from the food. Rather than aim towards
			#					it, they chose to minimize their punishment i.e., they get stuck in a local minimum. Experiment 2b will take away that punishment.
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
			# 3. Passing in information about whether there exists an obstacle is redundant. We need a new way to reward positive movements other than relying on random chance
            ai_dir = self.cpu.getDirection([self.sigmoid(-self.coords[0][0] + self.food[0]), self.sigmoid(-self.food[0] + self.coords[0][0]), self.sigmoid(self.coords[0][1] - self.food[1]), self.sigmoid(self.food[1] - self.coords[0][1]), self.sigmoid(-self.win_w / (self.PX_HEIGHT * 2) + self.coords[0][0]), self.sigmoid(-self.win_h / (self.PX_HEIGHT * 2) - self.coords[0][1])])
           
            # Checks AI's decision before obeying it 
            if (ai_dir < 2 and self.cur_dir > 1) or (ai_dir > 1 and self.cur_dir < 2):
                self.cur_dir = ai_dir

            # Assigning direction
            if(self.cur_dir == 0): head[1] -= 1
            if(self.cur_dir == 1): head[1] += 1
            if(self.cur_dir == 2): head[0] -= 1
            if(self.cur_dir == 3): head[0] += 1

            # Punish fitness if moving in wrong direction. Taken away by Experiment 2b. Results: Snakes were no longer incentivized to move towards the food, resulting in
			# getting trapped in a local minimum sooner. This is required. I think what needs to be done instead is reduce the impact this has the more points the snake gets.
			# To do that, we reward each additional food by a square rather than linear relationship.
            #if((head[0] - self.food[0]) ** 2 + (head[1] - self.food[1]) ** 2 > (self.coords[0][0] - self.food[0]) ** 2 + (self.coords[0][1] - self.food[1]) ** 2):
                #self.dir_punishment += 1
                #self.fitness -= 1.15

            # Reward living
            #self.fitness += 1

            # Move the snake
            self.coords.insert(0, head)
			
			# For debugging:
            self.frames_survived += 1

            if head != self.food:
                self.coords.pop()
            else:
				# Experiment 2c: Raise the food count and increase the fitness by it
				#		Results: Not very successful; the snakes didn't go for more than 2 foods, and that was probably random. Incentivizing aiming for food is definitely optimal
                self.fitness += 200
                self.food = [random.randint(0, self.win_w / self.PX_HEIGHT), random.randint(0, self.win_h / self.PX_HEIGHT)]
				# For debugging:
                self.pills_eaten += 1

    def draw(self, screen):
		# Only draws the best performing snake
        #if self.COLOR == (0, 0, 0):
			# Input neuron values
        	#pygame.draw.rect(screen, (0, 0, math.floor(self.sigmoid(-self.win_w / (self.PX_HEIGHT * 2) + self.coords[0][0]) * 255)), [0, 0, 200, 200]);
        	#pygame.draw.rect(screen, (0, 0, math.floor(self.sigmoid(-self.win_h / (self.PX_HEIGHT * 2) + self.coords[0][1]) * 255)), [200, 0, 200, 200]);

			# Draw the snake
        	for coord in self.coords:
        	    pygame.draw.rect(screen, self.COLOR, [coord[0] * self.PX_HEIGHT, coord[1] * self.PX_HEIGHT, self.PX_HEIGHT, self.PX_HEIGHT])

        	# Draw the food
        	pygame.draw.rect(screen, self.FOOD_COLOR, [self.food[0] * self.PX_HEIGHT, self.food[1] * self.PX_HEIGHT, self.PX_HEIGHT, self.PX_HEIGHT]) 

    
    def print_score(self):
		print("Frames survived: " + str(self.frames_survived))
		print("Frames survived: " + str(self.frames_survived) + "\nPills eaten: " + str(self.pills_eaten) + "              \nPunishment for wrong direction: " + str(self.dir_punishment))


    def reset(self):
        self.coords = [[0, 5], [0, 4], [0, 3], [0, 2]]
        self.fitness = 0
        self.alive = True
        self.cur_dir = 1
        self.food = [random.randint(0, self.win_w / self.PX_HEIGHT), random.randint(0, self.win_h / self.PX_HEIGHT)]
        self.food_count = 0
        self.frames_survived = 0
        self.pills_eaten = 0
        self.dir_punishment = 0

    def sigmoid(self, x): 
		# Multiplier of 1/5.0 good for food inputs
        return 1 / (1 + np.exp(-x/10.))
