import pygame
from pygame.math import Vector2
from pygame.sprite import Group
import math
from itertools import chain

# PYGAME RESOURCES

from utils import print_text
from models import Starship, Asteroid, Bullet

#self.font = pygame.font.Font(None, 64)

# GAME CLASSES AND METHODS

class MeteorDerby:
    def __init__(self):
        pygame.mixer.init(buffer=1024)
        pygame.init()
        pygame.display.set_caption('Asteroids')
        self.screen = pygame.display.set_mode((800, 600))
        self.background = pygame.image.load('earth.png').convert()
        self.clock = pygame.time.Clock()

    def _new_game(self):
        self.asteroids = Group()
        for _ in range(6):
            Asteroid(self.screen, groups=[self.asteroids])
        self.bullets = Group()
        self.starship = Starship(self.screen)
        self.status_text = ''
        self.font = pygame.font.Font(None, 64)
        self.shots_status = 0
        self.game_over = False

    def mainloop(self):

        self._new_game()
        self.run = True
        while self.run:
            self._process_input()
            self._process_game_logic()
            self._draw()
        pygame.quit()


    def _get_game_objects(self):
        return list(chain(self.asteroids, self.bullets,
                     (self.starship,) if self.starship else ()))

    def _process_input(self):
        # EVENTS
        for event in pygame.event.get():
            if (self.game_over and event.type == pygame.KEYDOWN and
                event.key == pygame.K_TAB):
                self._new_game()
            elif event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.starship:
                    continue
                self.starship.fire(self.bullets)

        pressed = pygame.key.get_pressed()
        if self.starship:
            if pressed[pygame.K_RIGHT]:
                self.starship.rotate_clockwise()
            elif pressed[pygame.K_LEFT]:
                self.starship.rotate_counterclockwise()
            if pressed[pygame.K_UP]:
                self.starship.accelerate()

    def _process_game_logic(self):

        #for obj in self._get_game_objects():
        #    obj.update()
        self.asteroids.update()
        self.bullets.update()
        if self.starship is not None:
            self.starship.update()

        # LOGIC

        for asteroid in self.asteroids:
            if self.starship and asteroid.collides_with(self.starship):
                self.status_text = 'You lost!'
                self.game_over = True
                self.starship = None

        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if asteroid.collides_with(bullet):
                    asteroid.split()
                    bullet.kill()

                    if not self.asteroids and not self.status_text:
                        self.game_over = True
                        self.status_text = 'You won!'
                    break

    def _draw(self):
        # DRAWING

        self.screen.blit(self.background, (0, 0))

        #for obj in self._get_game_objects():
            #obj.draw(self.screen)

        self.asteroids.draw(self.screen)
        self.bullets.draw(self.screen)
        if self.starship is not None:
            self.starship.draw(self.screen)

        if self.status_text:
            print_text(self.screen, self.status_text, self.font)

        if self.starship is not None:
            shots_left = 0

            """  # broken for now
            for asteroid in self.asteroids:
                if asteroid.image == IMG_ASTEROID_BIG:
                    shots_left += 7
                elif asteroid.image == IMG_ASTEROID_MEDIUM:
                    shots_left += 3
                else:
                    shots_left += 1
            """

            self.shots_status = shots_left

        print_text(self.screen, str(self.shots_status), self.font, (0, 0))

        pygame.display.flip()
        self.clock.tick(60)

