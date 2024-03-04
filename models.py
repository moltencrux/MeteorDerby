import pygame
import pygame.image
import random
import math
import operator

IMG_STARSHIP = pygame.image.load('starship.png').convert_alpha()
IMG_ASTEROID_BIG = pygame.image.load('asteroid-big.png').convert_alpha()
IMG_ASTEROID_MEDIUM = pygame.image.load('asteroid-medium.png').convert_alpha()
IMG_ASTEROID_SMALL = pygame.image.load('asteroid-small.png').convert_alpha()
IMG_BULLET = pygame.image.load('bullet.png').convert_alpha()


class GameObject:
    def __init__(self, pos, radius, speed, angle_deg):
        self.pos = pos
        angle_rad = math.radians(angle_deg)
        self.dir = [speed*math.cos(angle_rad), speed*math.sin(angle_rad)]
        self.radius = radius

    def draw(self, surface):
        blit_pos = [coord - self.radius for coord in self.pos]
        surface.blit(self.image, blit_pos)

    def contain(self, surface):
        orig_pos = tuple(self.pos)
        x, y = self.pos
        w, h = surface.get_size()
        self.pos = (x % w, y % h)
        return self.pos != orig_pos

    def animate(self):
        self.pos = list(map(operator.add, self.pos, self.dir))

    def collides_with(self, other_obj):
        distance = math.sqrt(
            (self.pos[0] - other_obj.pos[0])**2 +
            (self.pos[1] - other_obj.pos[1])**2
        )
        return distance < self.radius + other_obj.radius



class Starship(GameObject):
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

class Asteroid(GameObject):
    def __init__(self, pos, radius, image=IMG_ASTEROID_BIG):
        speed = max(1, random.random() * 3)
        angle = random.randrange(0, 360)
        self.image = image
        super().__init__(pos, radius, speed, angle)


class Bullet(GameObject):
    image = IMG_BULLET
