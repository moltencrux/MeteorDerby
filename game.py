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

FONT = pygame.font.Font(None, 64)
LASER = pygame.mixer.Sound('laser.wav')

# GAME CLASSES AND METHODS

# GAME INIT
done = False
shots_status = 0


class MeteorDerby:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.background = pygame.image.load('earth.png').convert()
        self.clock = pygame.time.Clock()
        self.asteroids = [Asteroid( get_random_pos(SCREEN.get_width(),
                                                   SCREEN.get_height()), 50)
                          for _ in range(6)]
        self.bullets = []
        self.starship = Starship((400, 300))
        self.status_text = ''


    def mainloop(self):
        done = False

        while not done:
            # EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    done = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not self.starship:
                        continue
                    v = self.starship.dir
                    velocity = math.sqrt(v[0]**2 + v[1]**2)
                    bullet = Bullet(self.starship.pos, 5, velocity + 2.0, self.starship.angle)
                    while bullet.collides_with(self.starship):
                        bullet.animate()
                    self.bullets.append(bullet)
                    LASER.play()

            # LOGIC

            if self.starship:
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    self.starship.rotate_clockwise()
                elif pygame.key.get_pressed()[pygame.K_LEFT]:
                    self.starship.rotate_counterclockwise()
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.starship.move()

            for asteroid in self.asteroids:
                if self.starship and asteroid.collides_with(self.starship):
                    self.status_text = 'You lost!'
                    self.starship = None

            for bullet in self.bullets:
                if self.starship and bullet.collides_with(self.starship) and not self.status_text:
                    self.status_text = 'You lost!'
                    self.starship = None
                for asteroid in self.asteroids:
                    if asteroid.collides_with(bullet):
                        if asteroid.image != IMG_ASTEROID_SMALL:
                            if asteroid.image == IMG_ASTEROID_BIG:
                                new_image = IMG_ASTEROID_MEDIUM
                            else:
                                new_image = IMG_ASTEROID_SMALL
                            new_radius = new_image.get_width() / 2
                            for _ in range(2):
                                self.asteroids.append(Asteroid(
                                    asteroid.pos, new_radius, new_image
                                ))
                        self.asteroids.remove(asteroid)
                        if not self.asteroids and not self.status_text:
                            self.status_text = 'You won!'
                        self.bullets.remove(bullet)
                        break

            # DRAWING

            SCREEN.blit(self.background, (0, 0))

            for obj in chain(self.asteroids, self.bullets, (self.starship,) if self.starship else ()):
                obj.animate()
                obj.contain(SCREEN)
                obj.draw(SCREEN)

            if self.status_text:
                print_text(SCREEN, self.status_text, FONT)

            if self.starship is not None:
                shots_left = 0
                for asteroid in self.asteroids:
                    if asteroid.image == IMG_ASTEROID_BIG:
                        shots_left += 7
                    elif asteroid.image == IMG_ASTEROID_MEDIUM:
                        shots_left += 3
                    else:
                        shots_left += 1
                shots_status = shots_left

            print_text(SCREEN, str(shots_status), FONT, (0, 0))

            pygame.display.flip()
            self.clock.tick(60)

        for obj in chain(self.asteroids, self.bullets, (self.starship,) if self.starship else ()):
            obj.animate()
            obj.contain(SCREEN)
            obj.draw(SCREEN)

        if self.status_text:
            print_text(SCREEN, self.status_text, FONT)

        if self.starship is not None:
            shots_left = 0
            for asteroid in self.asteroids:
                if asteroid.image == IMG_ASTEROID_BIG:
                    shots_left += 7
                elif asteroid.image == IMG_ASTEROID_MEDIUM:
                    shots_left += 3
                else:
                    shots_left += 1
            shots_status = shots_left

        print_text(SCREEN, str(shots_status), FONT, (0, 0))

        pygame.display.flip()
        self.clock.tick(60)
