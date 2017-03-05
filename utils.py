import math
import operator
import random


class GameObject:
    def __init__(self, pos, radius, speed, angle_deg):
        self.pos = pos
        angle_rad = math.radians(angle_deg)
        self.dir = [speed*math.cos(angle_rad), speed*math.sin(angle_rad)]
        self.radius = radius

    def draw(self, surface):
        raise Exception('Not implemented yet!')

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


def get_random_pos(width, height):
    angle = 2 * math.pi * random.random()
    hw = int(width / 2)
    hh = int(height / 2)
    rad = min(hw, hh)
    return [hw + rad * math.sin(angle), hh + rad * math.cos(angle)]


def change_dir(direction, angle_deg, acceleration):
    angle = math.radians(angle_deg)
    direction[0] += math.cos(angle) * acceleration
    direction[1] += math.sin(angle) * acceleration
