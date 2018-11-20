import logic
import copy
import pygame
import random

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
        self.alive = True self.weights = weights self.cpu = logic.Network(weights)

    def move(self, PX_HEIGHT, win_w, win_h):
        # Only moves when snake is alive
        if self.alive:
            # Copies initial coord
            head = copy.copy(self.coords[0])

            # Checking for death
            if head[0] < 0 or head[0] > win_w / PX_HEIGHT or head[1] < 0 or head[1] > win_h / PX_HEIGHT:
                self.alive = False

            for pixel in self.coords[1:]:
                if head == pixel:
                    self.alive = False
        
            # Gets prediction from AI. Currently passing in head coordinate and distance from food. 
            ai_dir = self.cpu.getDirection([self.coords[0][0], self.coords[0][1], self.coords[0][0] - self.food[0], self.coords[0][1] - self.food[1]])
           
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
