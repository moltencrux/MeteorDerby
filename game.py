import pygame

# PYGAME RESOURCES
pygame.init()

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Asteroids')
CLOCK = pygame.time.Clock()

IMG_EARTH = pygame.image.load('earth.png').convert()

# GAME CLASSES AND METHODS

# GAME INIT
done = False

while not done:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # LOGIC

    # DRAWING
    SCREEN.blit(IMG_EARTH, (0, 0))

    pygame.display.flip()
    CLOCK.tick(60)
