import pygame
import random
import math
from itertools import chain
from utils import GameObject, get_random_pos, change_dir

# PYGAME RESOURCES
pygame.mixer.init(buffer=1024)
pygame.init()

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Asteroids')
IMG_EARTH = pygame.image.load('earth.png').convert()
IMG_ASTEROID_BIG = pygame.image.load('asteroid-big.png').convert_alpha()
IMG_ASTEROID_MEDIUM = pygame.image.load('asteroid-medium.png').convert_alpha()
IMG_ASTEROID_SMALL = pygame.image.load('asteroid-small.png').convert_alpha()
IMG_STARSHIP = pygame.image.load('starship.png').convert_alpha()
IMG_BULLET = pygame.image.load('bullet.png').convert_alpha()
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 64)
LASER = pygame.mixer.Sound('laser.wav')

# GAME CLASSES AND METHODS
def print_text(surface, text, pos=None):
    w, h = surface.get_size()
    text_surface = FONT.render(text, 1, (200, 200, 0))
    rect = text_surface.get_rect()
    rect.center = [w / 2, h / 2]

    if not pos:
        surface.blit(text_surface, rect)
    else:
        surface.blit(text_surface, pos)


class PyladiesGameObject(GameObject):
    def draw(self, surface):
        blit_pos = [coord - self.radius for coord in self.pos]
        surface.blit(self.image, blit_pos)


class Asteroid(PyladiesGameObject):
    def __init__(self, pos, radius, image=IMG_ASTEROID_BIG):
        speed = max(1, random.random() * 3)
        angle = random.randrange(0, 360)
        self.image = image
        super().__init__(pos, radius, speed, angle)


class Bullet(PyladiesGameObject):
    image = IMG_BULLET


class Starship(PyladiesGameObject):
    image = IMG_STARSHIP

    def __init__(self, pos):
        super().__init__(pos, 20, 0.0, 0.0)
        self.angle = -90.0

    def _rotate(self, clockwise=True):
        delta = 3
        if clockwise:
            direction = 1
        else:
            direction = -1
        self.angle += delta * direction

    def rotate_clockwise(self):
        self._rotate(True)

    def rotate_counterclockwise(self):
        self._rotate(False)

    def move(self):
        change_dir(self.dir, self.angle, 0.5)

    def draw(self, surface):
        rotated_surf = pygame.transform.rotozoom(self.image, -90 - self.angle, 1.0)

        half_width = rotated_surf.get_width() / 2
        half_height = rotated_surf.get_height() / 2
        blit_pos = [self.pos[0] - half_width, self.pos[1] - half_height]

        surface.blit(rotated_surf, blit_pos)


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
        print_text(SCREEN, status_text)

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

    print_text(SCREEN, str(shots_status), (0, 0))

    pygame.display.flip()
    CLOCK.tick(60)
