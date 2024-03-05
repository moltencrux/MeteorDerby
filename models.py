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


UP = Vector2(0, -1)

class GameObject:
    _id_counter = count()
    _sprites_loaded = False
    _sprites = None
    _registry = None

    def __init__(self, surface, sprite=None, pos=None, velocity=None,
                 registry=None):
        self.id = next(self._id_counter)
        self._load_sprites()
        self.surface = surface
        self.sprite = self._sprites[None] if sprite is None else sprite
        self.pos = Vector2() if pos is None else pos
        self.velocity = Vector2() if velocity is None else velocity
        self.direction = Vector2(UP)
        self._registry = registry
        self._register()

    @classmethod
    def _load_sprites(cls):
        if not cls._sprites_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._sprites = {None, None}
            cls._sprites_loaded = True

    def destroy(self):
        self._unregister()
        del self

    def _register(self):
        if self._registry is not None:
            self._registry[self.id] = self

    def _unregister(self):
        if self._registry is not None:
            del self._registry[self.id]

    def draw(self):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        self.surface.blit(rotated_surface, self.pos)

    def move(self):
        self.pos += self.velocity

class WrappedGameObject(GameObject):

    def draw(self):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for offset_x, offset_y in self._get_mirror_offsets():
            mirror_position = self.pos + Vector2(offset_x, offset_y)
            blit_position = mirror_position - rotated_surface_size * 0.5
            self.surface.blit(rotated_surface, blit_position)

    def move(self):
        self.pos += self.velocity
        self._wrap_position()

    def _get_mirror_offsets(self):
        size = self.surface.get_size()
        offsets = [(0, 0)]  # Default offset for no wrapping

        if self.pos.x - self.sprite.get_rect().width / 2 < 0:
            offsets.append((size[0], 0))  # Wrap horizontally to the left
        elif self.pos.x + self.sprite.get_rect().width / 2 > size[0]:
            offsets.append((-size[0], 0))   # Wrap horizontally to the right

        if self.pos.y - self.sprite.get_rect().height / 2 < 0:
            offsets.append((0, size[1]))  # Wrap vertically upwards
        elif self.pos.y + self.sprite.get_rect().height / 2 > size[1]:
            offsets.append((0, -size[1]))   # Wrap vertically downwards

        # Check if object overlaps both horizontal and vertical edges (screen corners)
        if len(offsets) == 3:
            corner_offset = (offsets[1][0], offsets[2][1])  # Combine horizontal and vertical offsets
            offsets.append(corner_offset)  # Add screen corner offset

        return offsets

    def _wrap_position(self):
        x, y = self.pos
        w, h = self.surface.get_size()
        self.pos = Vector2(x % w, y % h)

    def animate(self):
        self.pos = list(map(operator.add, self.pos, self.dir))

    def collides_with(self, other_obj):
        self_rect = self.sprite.get_rect(center=self.pos)
        other_rect = other_obj.sprite.get_rect(center=other_obj.pos)
        
        for offset_x, offset_y in self._get_mirror_offsets():
            mirrored_self_rect = self_rect.move(offset_x, offset_y)
            overlap_rect = mirrored_self_rect.clip(other_rect)

            for x in range(overlap_rect.width):
                for y in range(overlap_rect.height):
                    self_pixel_pos = (overlap_rect.left - mirrored_self_rect.left + x, overlap_rect.top - mirrored_self_rect.top + y)
                    other_pixel_pos = (overlap_rect.left - other_rect.left + x, overlap_rect.top - other_rect.top + y)
            
                    self_pixel_color = self.sprite.get_at(self_pixel_pos)
                    other_pixel_color = other_obj.sprite.get_at(other_pixel_pos)

                    if self_pixel_color[3] > 0 and other_pixel_color[3] > 0:
                        return True  # Collision detected

        return False  # No collision detected



class Starship(WrappedGameObject):

    def __init__(self, surface, pos=None, velocity=None):
        self._load_sprites()
        pos = Vector2(surface.get_size()) / 2.0 if pos is None else pos
        super().__init__(surface, None, pos, velocity)
        self.acceleration = 0.5
        self.laser = pygame.mixer.Sound('laser.wav')

    @classmethod
    def _load_sprites(cls):
        if not cls._sprites_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._sprites = {None: pygame.image.load('starship.png').convert_alpha()}
            cls._sprites_loaded = True

    def _rotate(self, clockwise=True):
        delta = 3
        self.direction.rotate_ip(delta * (1.0 if clockwise else -1))
        self.direction.normalize_ip()
        _, self.angle = self.direction.as_polar()

    def accelerate(self):
        self.velocity += self.direction * self.acceleration

    def fire(self, bullet_registry):
        bullet_velocity = self.velocity + (self.direction * 2.0)
        bullet_pos = Vector2(self.pos)
        Bullet(self.surface, bullet_pos, bullet_velocity, bullet_registry)
        self.laser.play()

    def rotate_clockwise(self):
        self._rotate(True)

    def rotate_counterclockwise(self):
        self._rotate(False)

    def contain(self):
        orig_pos = tuple(self.pos)
        x, y = self.pos
        w, h = self.surface.get_size()
        self.pos = Vector2(x % w, y % h)
        if self.pos != orig_pos:
            print('pos altered!')
            print(f'  {w = } {h = }!')
            print(f'  {self.pos = } {orig_pos = }!')
        return self.pos != orig_pos

class Asteroid(WrappedGameObject):

    def __init__(self, surface, pos=None, velocity=None, registry=None, size='big'):
        self._load_sprites()
        sprite = self._sprites.get(size, self._sprites['big'])
        pos = get_random_pos(surface) if pos is None else pos
        velocity = get_random_vel() if velocity is None else velocity
        super().__init__(surface, sprite, pos, velocity, registry)

    @classmethod
    def _load_sprites(cls):
        if not cls._sprites_loaded:
            # Ensure pygame has been initialized
            if not pygame.get_init():
                pygame.init()

            # Load sprites
            cls._sprites = {size: pygame.image.load(path).convert_alpha() for size, path in 
                            (('small', 'asteroid-small.png'),
                            ('medium', 'asteroid-medium.png'),
                            ('big', 'asteroid-big.png'))}
            cls._sprites[''] = cls._sprites['big']
            cls._sprites[None] = cls._sprites['big']
            cls._sprites_loaded = True

    """                        
    def draw(self):
        print(f"drawing asteroid at, {self.pos}")
        WrappedGameObject.draw(self)
        super().draw()
    """                        

    def split(self):

        if self.sprite is not self._sprites['small']:
            size = 'medium'
            if self.sprite is self._sprites['small']:
                size = 'small'

            for _ in range(2):
                Asteroid(self.surface, self.pos, self.velocity, self._registry, size)

        del self


class Bullet(GameObject):
    def __init__(self, surface, pos, velocity, registry=None):
        super().__init__(surface, None, pos, velocity, registry)
    
    @classmethod
    def _load_sprites(cls):
        if not cls._sprites_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._sprites = {None: pygame.image.load('bullet.png').convert_alpha()}
            cls._sprites_loaded = True