import pygame
from pygame import Surface
import pygame.image
import random
import math
import operator
from itertools import count
from utils import get_random_pos, get_random_vel
from pygame.math import Vector2
from pygame.transform import rotozoom
from pygame.sprite import Sprite


UP = Vector2(0, -1)

class GameObject(Sprite):
    _id_counter = count()
    _images_loaded = False
    _images = None

    def __init__(self, screen, image=None, pos=None, velocity=None, groups=()):
        super().__init__(*groups)
        self.id = next(self._id_counter)
        self._load_images()
        self.screen = screen
        self.image = self._images[None] if image is None else image
        self.pos = Vector2() if pos is None else pos
        self.rect = self.image.get_rect()
        self.velocity = Vector2() if velocity is None else velocity
        self.direction = Vector2(UP)

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._images = {None, None}
            cls._images_loaded = True

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.image, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        self.surface.blit(rotated_surface, self.pos)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos

class WrappedGameObject(GameObject):

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.image, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for offset_x, offset_y in self._get_mirror_offsets():
            mirror_position = self.pos + Vector2(offset_x, offset_y)
            blit_position = mirror_position - rotated_surface_size * 0.5
            surface.blit(rotated_surface, blit_position)

    def update(self):
        super().update()
        self._wrap_position()

    def _get_mirror_offsets(self):
        size = self.screen.get_size()
        offsets = [(0, 0)]  # Default offset for no wrapping

        if self.pos.x - self.image.get_rect().width / 2 < 0:
            offsets.append((size[0], 0))  # Wrap horizontally to the left
        elif self.pos.x + self.image.get_rect().width / 2 > size[0]:
            offsets.append((-size[0], 0))   # Wrap horizontally to the right

        if self.pos.y - self.image.get_rect().height / 2 < 0:
            offsets.append((0, size[1]))  # Wrap vertically upwards
        elif self.pos.y + self.image.get_rect().height / 2 > size[1]:
            offsets.append((0, -size[1]))   # Wrap vertically downwards

        # Check if object overlaps both horizontal and vertical edges (screen corners)
        if len(offsets) == 3:
            corner_offset = (offsets[1][0], offsets[2][1])  # Combine horizontal and vertical offsets
            offsets.append(corner_offset)  # Add screen corner offset

        return offsets

    def _wrap_position(self):
        x, y = self.pos
        w, h = self.screen.get_size()
        self.pos = Vector2(x % w, y % h)

    def animate(self):
        self.pos = list(map(operator.add, self.pos, self.dir))

    def collides_with(self, other_obj):
        self_rect = self.image.get_rect(center=self.pos)
        other_rect = other_obj.image.get_rect(center=other_obj.pos)
        
        for offset_x, offset_y in self._get_mirror_offsets():
            mirrored_self_rect = self_rect.move(offset_x, offset_y)
            overlap_rect = mirrored_self_rect.clip(other_rect)

            for x in range(overlap_rect.width):
                for y in range(overlap_rect.height):
                    self_pixel_pos = (overlap_rect.left - mirrored_self_rect.left + x, overlap_rect.top - mirrored_self_rect.top + y)
                    other_pixel_pos = (overlap_rect.left - other_rect.left + x, overlap_rect.top - other_rect.top + y)
            
                    self_pixel_color = self.image.get_at(self_pixel_pos)
                    other_pixel_color = other_obj.image.get_at(other_pixel_pos)

                    if self_pixel_color[3] > 0 and other_pixel_color[3] > 0:
                        return True  # Collision detected

        return False  # No collision detected


class Starship(WrappedGameObject):

    def __init__(self, screen, pos=None, velocity=None):
        self._load_images()
        pos = Vector2(screen.get_size()) / 2.0 if pos is None else pos
        super().__init__(screen, None, pos, velocity)
        self.acceleration = 0.1
        self.laser = pygame.mixer.Sound('laser.wav')

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._images = {None: pygame.image.load('starship.png').convert_alpha()}
            cls._images_loaded = True

    def _rotate(self, clockwise=True):
        delta = 3
        self.direction.rotate_ip(delta * (1.0 if clockwise else -1))
        self.direction.normalize_ip()
        _, self.angle = self.direction.as_polar()

    def accelerate(self):
        self.velocity += self.direction * self.acceleration

    def fire(self, bullet_group):
        bullet_velocity = self.velocity + (self.direction * 8.0)
        bullet_pos = Vector2(self.pos)
        Bullet(self.screen, bullet_pos, bullet_velocity, [bullet_group])
        self.laser.play()

    def rotate_clockwise(self):
        self._rotate(True)

    def rotate_counterclockwise(self):
        self._rotate(False)

class Asteroid(WrappedGameObject):

    def __init__(self, screen, pos=None, velocity=None, size='big', groups=()):
        self._load_images()
        image = self._images.get(size, self._images['big'])
        pos = get_random_pos(screen) if pos is None else pos
        velocity = get_random_vel() if velocity is None else velocity
        self.size = size
        super().__init__(screen, image, pos, velocity, groups)

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            # Ensure pygame has been initialized
            if not pygame.get_init():
                pygame.init()

            # Load images
            cls._images = {size: pygame.image.load(path).convert_alpha() for size, path in 
                            (('small', 'asteroid-small.png'),
                            ('medium', 'asteroid-medium.png'),
                            ('big', 'asteroid-big.png'))}
            cls._images[''] = cls._images['big']
            cls._images[None] = cls._images['big']
            cls._images_loaded = True

    def split(self):

        if self.size != 'small':
            size = 'medium'
            if self.size != 'medium':
                size = 'small'

            for _ in range(2):
                Asteroid(self.screen, self.pos, None, size, self.groups())
        self.kill()


class Bullet(GameObject):
    def __init__(self, screen, pos, velocity, groups=()):
        super().__init__(screen, None, pos, velocity, groups)
    
    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._images = {None: pygame.image.load('bullet.png').convert_alpha()}
            cls._images_loaded = True

    def update(self):
        super().update()
        if not self.image.get_rect().colliderect(self.screen.get_rect()):
            self.kill()
