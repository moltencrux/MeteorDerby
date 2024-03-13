import pygame
from pygame.math import Vector2
from pygame.sprite import Group, OrderedUpdates, LayeredUpdates
import math
from itertools import chain

# PYGAME RESOURCES

from utils import print_text, load_and_scale
from models import Starship, Asteroid, Bullet

#self.font = pygame.font.Font(None, 64)

# GAME CLASSES AND METHODS

class MeteorDerby:
    def __init__(self):
        pygame.mixer.init(buffer=1024)
        pygame.init()
        pygame.display.set_caption('Asteroids')
        self.screen = pygame.display.set_mode((1024, 768))
        self.background = pygame.image.load('background.jpg').convert()
        self.clock = pygame.time.Clock()
        self.framerate = 60

    def _new_game(self):
        self.asteroids = Group()
        for _ in range(6):
            Asteroid(self.screen, groups=[self.asteroids])
        self.bullets = Group()
        self.starship = Starship(self.screen)
        self.starships = self.starship.mirrors
        self.status_text = ''
        self.font = pygame.font.Font(None, 64)
        self.shots_status = 0
        self.game_over = False
        self.paused = False

    def mainloop(self):

        self._new_game()
        self.run = True
        while self.run:
            self._process_input()
            self._process_game_logic()
            self._draw()
        pygame.quit()

    def _process_input(self):
        # EVENTS
        for event in pygame.event.get():
            if (self.game_over and event.type == pygame.KEYDOWN and
                event.key == pygame.K_TAB):
                self._new_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused ^= True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.framerate = 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.framerate = 60
            elif event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not self.starship or not self.starship.alive:
                    continue
                self.starship.fire(self.bullets)

        pressed = pygame.key.get_pressed()
        if self.starship and self.starship.alive:
            if pressed[pygame.K_RIGHT]:
                self.starship.rotate_clockwise()
            elif pressed[pygame.K_LEFT]:
                self.starship.rotate_counterclockwise()
            if pressed[pygame.K_UP]:
                self.starship.accelerate()
            #elif pressed[pygame.K_SPACE]:
            #    # set up rapid fire here
            #    if self.starship:
            #        self.starship.fire(self.bullets)

    def _process_game_logic(self):

        #for obj in self._get_game_objects():
        #    obj.update()
        if not self.paused:

            self.asteroids.update()
            self.bullets.update()
            if self.starship is not None:
                self.starship.update()

            # LOGIC
            if self.starship and self.starship.alive:
                for ship in self.starship.mirrors:
                    possible_hits = pygame.sprite.spritecollide(ship, self.asteroids, False)
                    verified_hits = pygame.sprite.spritecollide(ship, possible_hits, False, pygame.sprite.collide_mask)
                    for asteroid in verified_hits:
                        asteroid.split()
                        ship.explode()
                        self.status_text = 'You lost!'
                        self.game_over = True
                        break

            for bullet in self.bullets:
                possible_hits = pygame.sprite.spritecollide(bullet, self.asteroids, False)
                verified_hits = pygame.sprite.spritecollide(bullet, possible_hits, False, pygame.sprite.collide_mask)
                for asteroid in verified_hits:
                    asteroid.split()
                    bullet.kill()
                    if not self.asteroids and not self.status_text:
                        self.game_over = True
                        self.status_text = 'You won!'
                    break

    def _draw(self):
        # DRAWING

        self.screen.blit(self.background, (0, 0))

        self.asteroids.draw(self.screen)
        self.bullets.draw(self.screen)
        self.starships.draw(self.screen)

        if self.status_text:
            print_text(self.screen, self.status_text, self.font)

        if self.starship is not None:
            shots_left = 0

            # broken for now
            for asteroid in self.asteroids:
                if isinstance(asteroid, Asteroid):
                    if asteroid.size == 'big':
                        shots_left += 13
                    elif asteroid.size == 'medium':
                        shots_left += 4
                    else:
                        shots_left += 1

            self.shots_status = shots_left

        print_text(self.screen, str(self.shots_status), self.font, (0, 0))

        if not self.paused:
            pygame.display.flip()
        self.clock.tick(self.framerate)


class GameTest(MeteorDerby):

    def _new_game(self):
        self.asteroids = OrderedUpdates()
        for _ in range(1):
            self.main_asteroid = Asteroid(self.screen, groups=[self.asteroids])
        self.bullets = Group()
        self.starship = Starship(self.screen)
        self.starships = self.starship.mirrors
        self.status_text = ''
        self.font = pygame.font.Font(None, 64)
        self.shots_status = 0
        self.game_over = False
        self.paused = False

    def _process_input(self):
        # EVENTS
        for event in pygame.event.get():
            if (self.game_over and event.type == pygame.KEYDOWN and
                event.key == pygame.K_TAB):
                self._new_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused ^= True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                self.framerate = 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.framerate = 60
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

