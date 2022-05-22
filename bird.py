# -> imports
from pygame.locals import *
import numpy as np
import network
import pygame
import random

pygame.init()

def rotateAroundCenter(image, angle, x, y):
    rotatedImage = pygame.transform.rotate(image, angle)
    rotatedRect = rotatedImage.get_rect(center = image.get_rect(center = (x, y)).center)
    return rotatedImage, rotatedRect

def clamp(x, upper, lower):
    if x > upper:
        return upper
    if x < lower:
        return lower
    return x

crownImage = pygame.transform.scale(pygame.image.load('Assets/crown2.png'), (28, 20))

class Bird:
    def __init__(self, x, y):
        # -> general setup
        self.lifetime = 0
        self.screen = pygame.display.get_surface()
        self.image = pygame.transform.scale(pygame.image.load('Assets/bird.png').convert_alpha(), (25, 20))
        self.score = 0

        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2()
        self.crowned = False
        self.dead = False

        # -> building the network
        self.network = network.Network()
        self.network.add(network.FCLayer(3, 5))
        self.network.add(network.FCLayer(5, 4))
        self.network.add(network.FCLayer(4, 2))
        self.network.add(network.ActivationLayer(network.sigmoid))
    
    def getNearestPipe(self, pipes):
        nearest = pipes[0]
        for pipe in pipes:
            if nearest.centerPoint[0] < self.rect.x:
                nearest = pipe
                continue
            if self.rect.x < pipe.centerPoint[0]:
                if pipe.centerPoint[0] - self.rect.x < nearest.centerPoint[0] - self.rect.x:
                    nearest = pipe
        return nearest

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] or keys[K_w] or keys[K_UP]:
            self.flap()

    def draw(self):
        angle = -(self.vel.y / 10) * 60
        image, rect = rotateAroundCenter(self.image, angle, self.rect.centerx, self.rect.centery)
        if self.dead:
            colouredImage = pygame.Surface(self.image.get_size()).convert_alpha()
            colouredImage.fill((245, 72, 66))
            image.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(image, rect)

    def drawCrown(self):
        self.screen.blit(crownImage, (self.rect.centerx - crownImage.get_width() / 2, self.rect.centery - self.image.get_height() * 1.5))

    def flap(self):
        self.vel.y = -6

    def update(self, pipes):
        if self.dead:
            self.vel.y += 0.6
        else:
            self.nearest = self.getNearestPipe(pipes)
            # -> apply gravity
            self.vel.y += 0.4
            # -> getting stuff from network
            deltaX = self.nearest.centerPoint[0] - self.rect.centerx
            deltaY = self.nearest.centerPoint[1] - self.rect.centery
            velY = self.vel.y
            jump = self.network.predict([np.array([deltaX, deltaY, velY])])[0]
            if jump[0] > jump[1]:
                self.flap()

        # -> apply velocity
        self.rect.x += self.vel.x
        self.rect.y += self.vel.y

        if self.rect.centery <= -25:
            self.rect.centery = -25
    
    def reproduce(self, x, y, mutationRate):
        child = Bird(x, y)
        childNetwork = child.network
        if random.random() < mutationRate: # -> 20 % chance of mutation
            for _ in range(3): # -> mutate 3 times
                layer = random.choice([layer for layer in childNetwork.layers if not isinstance(layer, network.ActivationLayer)])
                if random.random() < 0.5:
                    # -> mutate weights
                    if random.random() < 0.5:
                        layer.weights[random.randint(0, len(layer.weights) - 1)] = 0.5 - random.random()
                    else:
                        layer.weights[random.randint(0, len(layer.weights) - 1)] += 0.5 - random.random()
                else:
                    # -> mutate biases
                    if random.random() < 0.5:
                        layer.bias[random.randint(0, len(layer.bias) - 1)] = 0.5 - random.random()
                    else:
                        layer.bias[random.randint(0, len(layer.bias) - 1)] += 0.5 - random.random()
        return child

class Pipe:
    def __init__(self, x, y, width, height, x1, y1, width1, height1, gapSize):
        self.gapSize = gapSize
        self.width = width
        self.screen = pygame.display.get_surface()
        self.topImage = pygame.Surface((width, height))
        self.topImage.fill((117, 190, 49))
        self.bottomImage = pygame.Surface((width1, height1))
        self.bottomImage.fill((147, 190, 49))

        self.topRect = self.topImage.get_rect(topleft = (x, y))
        self.bottomRect = self.bottomImage.get_rect(topleft = (x1, y1))
        self.centerPoint = (self.bottomRect.x + 50, self.bottomRect.y - self.gapSize * 0.5)

    def update(self):
        self.topRect.x -= 2
        self.bottomRect.x -= 2
        self.centerPoint = (self.bottomRect.x + 25, self.bottomRect.y - self.gapSize * 0.5)

    def draw(self):
        self.screen.blit(self.topImage, self.topRect)
        self.screen.blit(self.bottomImage, self.bottomRect)
        pygame.draw.rect(self.screen, (5, 5, 13), self.topRect, 2)
        pygame.draw.rect(self.screen, (5, 5, 13), self.bottomRect, 2)