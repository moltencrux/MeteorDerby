import pygame
import math
from itertools import chain

# PYGAME RESOURCES
pygame.mixer.init(buffer=1024)
pygame.init()
SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Asteroids')

from utils import get_random_pos, change_dir, print_text
from models import GameObject, Starship, Asteroid, Bullet
from models import IMG_ASTEROID_BIG, IMG_ASTEROID_MEDIUM, IMG_ASTEROID_SMALL

IMG_EARTH = pygame.image.load('earth.png').convert()
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 64)
LASER = pygame.mixer.Sound('laser.wav')

# GAME CLASSES AND METHODS

# GAME INIT
done = False
status_text = ''
shots_status = 0

asteroids = []
bullets = []

for _ in range(6):
    asteroids.append(Asteroid(
        get_random_pos(SCREEN.get_width(), SCREEN.get_height()), 50)
    )

starship = Starship((400, 300))

while not done:
    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not starship:
                continue
            v = starship.dir
            velocity = math.sqrt(v[0]**2 + v[1]**2)
            bullet = Bullet(starship.pos, 5, velocity + 2.0, starship.angle)
            while bullet.collides_with(starship):
                bullet.animate()
            bullets.append(bullet)
            LASER.play()

    # LOGIC

    if starship:
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            starship.rotate_clockwise()
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            starship.rotate_counterclockwise()
        if pygame.key.get_pressed()[pygame.K_UP]:
            starship.move()

    for asteroid in asteroids:
        if starship and asteroid.collides_with(starship):
            status_text = 'You lost!'
            starship = None

    for bullet in bullets:
        if starship and bullet.collides_with(starship) and not status_text:
            status_text = 'You lost!'
            starship = None
        for asteroid in asteroids:
            if asteroid.collides_with(bullet):
                if asteroid.image != IMG_ASTEROID_SMALL:
                    if asteroid.image == IMG_ASTEROID_BIG:
                        new_image = IMG_ASTEROID_MEDIUM
                    else:
                        new_image = IMG_ASTEROID_SMALL
                    new_radius = new_image.get_width() / 2
                    for _ in range(2):
                        asteroids.append(Asteroid(
                            asteroid.pos, new_radius, new_image
                        ))
                asteroids.remove(asteroid)
                if not asteroids and not status_text:
                    status_text = 'You won!'
                bullets.remove(bullet)
                break

    # DRAWING

    SCREEN.blit(IMG_EARTH, (0, 0))

    for obj in chain(asteroids, bullets, (starship,) if starship else ()):
        obj.animate()
        obj.contain(SCREEN)
        obj.draw(SCREEN)

    if status_text:
        print_text(SCREEN, status_text, FONT)

    if starship is not None:
        shots_left = 0
        for asteroid in asteroids:
            if asteroid.image == IMG_ASTEROID_BIG:
                shots_left += 7
            elif asteroid.image == IMG_ASTEROID_MEDIUM:
                shots_left += 3
            else:
                shots_left += 1
        shots_status = shots_left

    print_text(SCREEN, str(shots_status), FONT, (0, 0))

    pygame.display.flip()
    CLOCK.tick(60)
