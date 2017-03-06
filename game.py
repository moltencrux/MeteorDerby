import pygame
import random
from utils import GameObject, get_random_pos

# PYGAME RESOURCES
pygame.init()

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Asteroids')
IMG_EARTH = pygame.image.load('earth.png').convert()
IMG_ASTEROID_BIG = pygame.image.load('asteroid-big.png').convert_alpha()
IMG_STARSHIP = pygame.image.load('starship.png').convert_alpha()
CLOCK = pygame.time.Clock()

# GAME CLASSES AND METHODS
class PyladiesGameObject(GameObject):
    def draw(self, surface):
        blit_pos = [coord - self.radius for coord in self.pos]
        surface.blit(self.image, blit_pos)


class Asteroid(PyladiesGameObject):
    image = IMG_ASTEROID_BIG

    def __init__(self, pos, radius):
        speed = max(1, random.random() * 3)
        angle = random.randrange(0, 360)
        super().__init__(pos, radius, speed, angle)


class Starship(PyladiesGameObject):
    image = IMG_STARSHIP


# GAME INIT
done = False

asteroids = []
for _ in range(6):
    asteroids.append(Asteroid(
        get_random_pos(SCREEN.get_width(), SCREEN.get_height()), 50)
    )

starship = Starship((400, 300), 20, 0, 0)

while not done:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # LOGIC
    for asteroid in asteroids:
        asteroid.animate()
        asteroid.contain(SCREEN)
        if asteroid.collides_with(starship):
            done = True

    # DRAWING

    SCREEN.blit(IMG_EARTH, (0, 0))
    for asteroid in asteroids:
        asteroid.draw(SCREEN)

    starship.draw(SCREEN)

    pygame.display.flip()
    CLOCK.tick(60)
