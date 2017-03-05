import pygame

# PYGAME RESOURCES
pygame.init()

SCREEN = pygame.display.set_mode((800, 600))
CLOCK = pygame.time.Clock()

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
    pygame.display.flip()
    CLOCK.tick(60)
