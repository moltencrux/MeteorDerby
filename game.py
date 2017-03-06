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
        blit_pos = [coord - self.radius for coord in self.pos]
        surface.blit(self.image, blit_pos)


class Asteroid(PyladiesGameObject):
    image = IMG_ASTEROID_BIG

# GAME INIT
done = False
pgm = Asteroid((200, 200), 50, 2, 17)

while not done:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # LOGIC

    # DRAWING
    pgm.animate()
    pgm.contain(SCREEN)

    SCREEN.blit(IMG_EARTH, (0, 0))
    pgm.draw(SCREEN)

    pygame.display.flip()
    CLOCK.tick(60)
