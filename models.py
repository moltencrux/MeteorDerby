import pygame
from pygame import Surface, Rect
import pygame.image
import random
#import operator
from itertools import count
from utils import (get_random_pos, get_random_vel, load_sprite_sheet,
                   load_and_scale, get_random_spin)
from pygame.math import Vector2
from pygame.transform import rotozoom, rotate
from pygame.sprite import Sprite, Group


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
        self.orig_image = self.image
        self.pos = Vector2() if pos is None else pos
        self.rect = self.image.get_rect()
        self.rect.center = tuple(self.pos)
        self.velocity = Vector2() if velocity is None else velocity
        self.direction = Vector2(UP)
        self._previous_direction = Vector2()
        self.mask = pygame.mask.from_surface(self.image)
        self._animate = False
        self._repeat = False

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._images = {None, None}
            cls._images_loaded = True


    def animate(self, name, frame_duration=1, repeat=False, on_finish=None):
        self.frames = self._animations[name]
        self._repeat_animation = repeat
        self.current_frame = 0
        self.last_frame_time = pygame.time.get_ticks()
        self._animate = True
        self._frame_duration = frame_duration
        self._on_finish = on_finish

    def update(self):

        if self._animate is True:

            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time > self._frame_duration:
                self.current_frame += 1
                if self.current_frame >= len(self.frames) - 1:
                    if self._repeat:
                        self.current_frame = 0
                    else:
                        self._animate = False
                        if self._on_finish is not None:
                            self._on_finish()

                self.orig_image = self.frames[self.current_frame]
                self._previous_direction = Vector2() # trigger re-rotation
                self.last_frame_time = current_time

        if self._previous_direction != self.direction:
            angle = self.direction.angle_to(UP)
            prev_center = self.rect.center
            #self.orig_image
            #self.image = rotozoom(self.orig_image, angle, 1.0)
            self.image = rotate(self.orig_image, angle)
            self.image.get_rect().center = prev_center
            self._previous_direction.update(self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

        self.pos += self.velocity
        self.rect.center = self.pos


class MirrorSprite(Sprite):

    def __init__(self, master, bearing, groups=()):
        self.master = master
        self.screen = master.screen
        self.bearing = Vector2(bearing)
        self._pos = Vector2()
        self._mirror_rect = Rect(master.rect)
        self._mirror_rect.center = master.pos
        super().__init__(groups)
        # there should be 3 mirrors for an object that needs to be mirrored
        # horizontal, vertical, diagonal
        # we can determine the position based on screen size.. and mod
        # i.e. add ht to x % size, or

    @property
    def rect(self):
        self._mirror_rect.size = self.master.rect.size
        self._mirror_rect.center = self._apply_offsets(self.master.rect.center)
        return self._mirror_rect

    @property
    def image(self):
        return self.master.image

    @property
    def mask(self):
        return self.master.mask

    @property
    def pos(self):
        self._pos.update(self._apply_offsets(self.master.pos))
        return self._pos

    def _apply_offsets(self, p):
        w, h = self.screen.get_size()
        p = Vector2(p)
        xcoef = 1 if abs(p.x) < abs(w - p.x) else -1
        ycoef = 1 if abs(p.y) < abs(h - p.y) else -1
        offset = Vector2(w * xcoef * self.bearing[0], h * ycoef * self.bearing[1])
        return tuple(p + offset)

    @property
    def image(self):
        return self.master.image

    def kill(self):
        super().kill()  # maybe if we call this first, no infinite loop
        self.master.kill()
        
    def __getattr__(self, attr):
        return getattr(self.master, attr)

class MirroredGameObject(GameObject):

    def __init__(self, screen, image=None, pos=None, velocity=None, clone=False,
                 groups=()):
        self.mirrors = Group()
        super().__init__(screen, image, pos, velocity, groups)
        groups = (self.mirrors, *groups)
        # create clones & add them to group

        for bearing in ((0, 1), (1, 0), (1, 1)):
            MirrorSprite(self, bearing, (self.mirrors, *groups))

    def _wrap_position(self):
        x, y = self.pos
        w, h = self.screen.get_size()
        self.pos = Vector2(x % w, y % h)

    def update(self):
        super().update()
        self._wrap_position()

    def kill(self):
        if not hasattr(self, '_destroyed'):
            self._destroyed = True
            for mirror in self.mirrors:
                if mirror is not self:
                    mirror.kill()
        super().kill()


class Starship(MirroredGameObject):
    _animations = {}

    def __init__(self, screen, pos=None, velocity=None):
        self._load_images()
        pos = Vector2(screen.get_size()) / 2.0 if pos is None else pos
        super().__init__(screen, None, pos, velocity)
        self.acceleration = 0.2
        self.laser = pygame.mixer.Sound('lasercannon.flac')
        self.boom_sound = pygame.mixer.Sound("explosion.flac")
        self.mirrors.add(self)
        self.alive = True

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            cls._images = {None: load_and_scale('starship.png', (50, 50)).convert_alpha()}
            cls._images_loaded = True

        explosion = load_sprite_sheet('explosion.png', (8, 8))
        explosion.append(pygame.Surface((0, 0), pygame.SRCALPHA))
        cls._animations['explosion'] = explosion




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

    def draw_center_dot(self):
        # Draw a red dot at the center of the sprite's image
        dot_radius = 3
        dot_color = (255, 0, 0)
        dot_center = self.rect.center
        pygame.draw.circle(self.screen, dot_color, dot_center, dot_radius)

    def explode(self):
        self.alive = False
        self.animate('explosion', on_finish=self.kill)
        self.boom_sound.play()

class Asteroid(MirroredGameObject):

    def __init__(self, screen, pos=None, velocity=None, size='big', groups=()):
        self._load_images()
        image = self._images.get(size, self._images['big'])
        pos = get_random_pos(screen) if pos is None else pos
        velocity = get_random_vel() if velocity is None else velocity
        self.size = size
        super().__init__(screen, image, pos, velocity, False, groups)
        self.counter = count()
        self.angular_velocity = get_random_spin(5)

    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            # Ensure pygame has been initialized
            if not pygame.get_init():
                pygame.init()

            # Load images
            cls._images = {size: load_and_scale(path, dims).convert_alpha() for size, path, dims in 
                            (('small', 'asteroid.png', (40, 40)),
                            ('medium', 'asteroid.png',(95, 95)),
                            ('big', 'asteroid.png', (120, 120)))}
            cls._images[''] = cls._images['big']
            cls._images[None] = cls._images['big']
            cls._images_loaded = True


    def split(self):

        size = {'big':'medium', 'medium':'small', 'small':None}.get(self.size)
        if size is not None:
            for _ in range(3):
                Asteroid(self.screen, self.pos, None, size, self.groups())
        self.kill()

    def update(self):
        self._count = next(self.counter)
        self.direction = self.direction.rotate(self.angular_velocity)
        super().update()



class Bullet(GameObject):
    def __init__(self, screen, pos, velocity, groups=()):
        super().__init__(screen, None, pos, velocity, groups)
        self.direction = self.velocity
    
    @classmethod
    def _load_images(cls):
        if not cls._images_loaded:
            if not pygame.get_init():
                pygame.init()
            #cls._images = {None: pygame.image.load('beam.png').convert_alpha()}
            cls._images = {None: load_and_scale('beam.png', (30, 54)).convert_alpha()}
            cls._images_loaded = True

    def update(self):
        super().update()
        if not self.rect.colliderect(self.screen.get_rect()):
            self.kill()

