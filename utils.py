import math
import random
from pygame import Surface
from pygame.math import Vector2


def get_random_pos(surface: Surface):
    angle = 2 * math.pi * random.random()
    #angle = 360 * random.random()
    hw = int(surface.get_width() / 2)
    hh = int(surface.get_height() / 2)
    rad = min(hw, hh)
    return Vector2(hw + rad * math.sin(angle), hh + rad * math.cos(angle))

    return Vector2(surface.get_height() * random.random(),
                    surface.get_width() * random.random()) 

def get_random_vel():

    return Vector2(1.0 * (random.random() - 0.5),
                   1.0 * (random.random() - 0.5))


def change_dir(direction, angle_deg, acceleration):
    angle = math.radians(angle_deg)
    direction[0] += math.cos(angle) * acceleration
    direction[1] += math.sin(angle) * acceleration


def print_text(surface, text, font, pos=None):
    w, h = surface.get_size()
    text_surface = font.render(text, 1, (200, 200, 0))
    rect = text_surface.get_rect()
    rect.center = [w / 2, h / 2]

    if pos is None:
        surface.blit(text_surface, rect)
    else:
        surface.blit(text_surface, pos)


