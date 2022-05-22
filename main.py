# -> imports
import pygame
import random
import bird
import sys

pygame.init()

def clone(bestBird, x, y):
    child = bird.Bird(x, y)
    child.network = bestBird.network
    return child

def getFontObject(msg, fontSize=24, colour=(0, 0, 0)):
    # -> pygame wrapper to speed up text creation
    font = pygame.font.SysFont('Consolas', fontSize)
    fontSurface = font.render(msg, True, colour)
    return fontSurface

class Environment:
    def __init__(self, screenSize, populationSize, mutationRate=0.2):
        # -> pygame setup
        self.mutationRate = mutationRate
        self.populationSize = populationSize
        if screenSize == 'FULLSCREEN':
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screenSize = self.screen.get_size()
        else:
            self.screenSize = screenSize
            self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption('flAIppy bird - Francis Lee')
        self.clock = pygame.time.Clock()
        self.run()

    def generatePipe(self, x):
        gapSize = random.randint(150, 200)
        gapStart = random.randint(int((gapSize // 2) * 1.2), int(self.screenSize[1] - gapSize * 1.2))
        pipe = bird.Pipe(x, -50, 50, gapStart + 50, x, gapStart + gapSize, 50, self.screenSize[1] - (gapStart + gapSize) + 50, gapSize)
        return pipe
    
    def generatePool(self, size, bestBird = None):
        spawnPos = (self.screenSize[0] // 2, self.screenSize[1] // 2)
        if bestBird:
            birds = [bestBird.reproduce(spawnPos[0], spawnPos[1], self.mutationRate) for _ in range(size)]
        else:
            birds = [bird.Bird(spawnPos[0], spawnPos[1]) for _ in range(size)]
        return birds

    def metaSetup(self):
        self.generation = 0
        self.setup()

    def setup(self, bestBird = None):
        if bestBird:
            self.birds = self.generatePool(self.populationSize - 1, bestBird)
            kingBird = clone(bestBird, self.screenSize[0] // 2, self.screenSize[1] // 2)
            kingBird.crowned = True
            kingBird.lifetime += 1
            self.birds.append(kingBird)
        else:
            self.birds = self.generatePool(self.populationSize)
        self.pipes = []
        self.deadBirds = []
        for x in range(0, self.screenSize[0], self.screenSize[0] // 5):
            self.pipes.append(self.generatePipe(self.screenSize[0] + x))
        self.generation += 1
        self.ticks = 0

    def run(self):
        # -> game setup
        self.metaSetup()
        self.bestBird = random.choice(self.birds)
        bg = pygame.transform.scale(pygame.image.load('Assets/background.png'), self.screenSize)
        
        # -> game loop
        while True:
            # -> event loop
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            # -> updates
            if not self.birds:
                self.setup(self.bestBird)
            self.bestBird = max(self.birds, key=lambda bird: bird.lifetime)

            for bird in self.birds:
                bird.update(self.pipes)
            for pipe in self.pipes:
                pipe.update()
            for idx, deadBird in sorted(enumerate(self.deadBirds), reverse=True):
                deadBird.update(self.pipes)
                if deadBird.rect.y >= self.screenSize[1]:
                    self.deadBirds.pop(idx)
            
            # ->> handline bird deaths
            for idx, bird in sorted(enumerate(self.birds), reverse=True):
                if not self.bestBird == bird:
                    bird.image.set_alpha(100)
                else:
                    bird.image.set_alpha(255)
                for pipe in self.pipes:
                    if pipe.topRect.colliderect(bird.rect) or pipe.bottomRect.colliderect(bird.rect):
                        self.birds.pop(idx)
                        self.deadBirds.append(bird)
                        bird.dead = True
                        break
                if bird.rect.y >= self.screenSize[1]:
                    self.birds.pop(idx)
                    self.deadBirds.append(bird)
                    bird.dead = True

            # -> infinitly creating pipes
            if self.pipes[0].bottomRect.x <= 0:
                self.pipes.append(self.generatePipe(self.screenSize[0]))
                self.pipes.pop(0)

            # -> render
            self.screen.blit(bg, (0, 0))
            for pipe in self.pipes:
                pipe.draw()
            for bird in self.birds:
                bird.draw()
                bird.lifetime += 1
            for deadBird in self.deadBirds:
                deadBird.draw()
            if self.bestBird in self.birds: self.bestBird.drawCrown()
            # --> text render
            generationText = getFontObject('Generation: ' + str(self.generation), 32, (255, 255, 255))
            aliveText = getFontObject('Alive: ' + str(len(self.birds)), 32, (255, 255, 255))
            elapsedText = getFontObject('Elapsed: ' + str(round(self.ticks / 60, 2)), 32, (255, 255, 255))
            self.screen.blit(generationText, (0, 0))
            self.screen.blit(aliveText, (0, 0 + generationText.get_height() * 1.1))
            self.screen.blit(elapsedText, (0, 0 + generationText.get_height() * 1.1 + aliveText.get_height() * 1.1))

            # -> clean up
            pygame.display.update()
            self.clock.tick(60)
            self.ticks += 1

env = Environment('FULLSCREEN', 1000)