import pygame
from utils import GameObject

# PYGAME RESOURCES
pygame.init()

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Asteroids')
IMG_EARTH = pygame.image.load('earth.png').convert()
IMG_ASTEROID_BIG = pygame.image.load('asteroid-big.png').convert_alpha()
CLOCK = pygame.time.Clock()

# GAME CLASSES AND METHODS
class PyladiesGameObject(GameObject):
    def draw(self, surface):
        surface.blit(IMG_ASTEROID_BIG, self.pos)

# GAME INIT
done = False
pgm = PyladiesGameObject((200, 200), 50, 2, 0)

while not done:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # LOGIC

    # DRAWING
    pgm.animate()

    SCREEN.blit(IMG_EARTH, (0, 0))
    pgm.draw(SCREEN)

    pygame.display.flip()
    CLOCK.tick(60)
