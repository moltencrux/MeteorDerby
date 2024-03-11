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

    return Vector2(2.0 * (random.random() - 0.5),
                   2.0 * (random.random() - 0.5))


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


import pygame

def load_and_scale(image_path, target_size):
    """
    Load an image from the given path and scale it to fit within the target size
    while preserving aspect ratio.
    
    Args:
        image_path (str): The path to the image file.
        target_size (tuple): A tuple containing the target width and height
        (target_width, target_height).
        
    Returns:
        pygame.Surface: The scaled image surface.
    """
    original_image = pygame.image.load(image_path).convert_alpha()
    original_size = original_image.get_size()
    target_width, target_height = target_size
    
    # Calculate the scaling factors for width and height
    width_scale = target_width / original_size[0]
    height_scale = target_height / original_size[1]
    
    # Choose the smaller scaling factor to ensure the image fits within the target size
    scale_factor = min(width_scale, height_scale)
    
    # Scale the image while preserving aspect ratio
    scaled_width = int(original_size[0] * scale_factor)
    scaled_height = int(original_size[1] * scale_factor)
    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    
    return scaled_image

def get_random_spin(max_spin):
    angle = random.randrange(-max_spin + 1, max_spin)
    return angle


import pygame



def load_sprite_sheet(source, dimensions, scale=None):

    if isinstance(source, str):
        sheet = pygame.image.load(source).convert_alpha()
    elif isinstance(source, pygame.Surface):
        sheet = source
    else:
        raise ValueError("source is not a filename or a Surface.")
    sheet = pygame.image.load(source).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    rows, cols = dimensions
    cell_width = sheet_width // cols
    cell_height = sheet_height // rows
    frames = []
    for row in range(rows):
        for col in range(cols):
            cell_rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
            cell_image = sheet.subsurface(cell_rect)
            if scale:
                cell_image = pygame.transform.scale(cell_image, scale)
            frames.append(cell_image)
    return frames
