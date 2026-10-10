import math
import pygame

# how many coins each enemy type drops when it dies
COIN_VALUES = {
    "normal": 1,
    "runner": 1,
    "brute": 3,
}

# the chance (0.0 to 1.0) that an enemy drops a heart when it dies
# 0.25 means about 1 out of every 4 deaths
HEART_DROP_CHANCE = {
    "normal": 0.20,
    "runner": 0.30,
    "brute": 0.60,
}

HEART_HEAL_AMOUNT = 20  # how much health a heart gives back

COIN_COLOR = (250, 210, 60)
COIN_EDGE = (180, 140, 30)
COIN_RADIUS = 7
COIN_BOB_HEIGHT = 3   # how far up and down the coin bobs (pixels)
COIN_BOB_SPEED = 4    # how fast it bobs

HEART_COLOR = (230, 50, 80)
HEART_EDGE = (150, 25, 45)
HEART_SIZE = 16       # the heart fits inside a box this many pixels wide


class Coin:
    def __init__(self, x, y, value=1):
        # x and y are the CENTER of the coin, in world space
        self.x = float(x)
        self.y = float(y)
        self.value = value
        self.time = 0.0  # used for the bobbing animation

    def update(self, dt):
        self.time += dt

    def get_rect(self):
        return pygame.Rect(
            int(self.x - COIN_RADIUS),
            int(self.y - COIN_RADIUS),
            COIN_RADIUS * 2,
            COIN_RADIUS * 2,
        )

    def draw(self, surface, camera):
        # the coin bobs up and down so it looks alive
        bob = math.sin(self.time * COIN_BOB_SPEED) * COIN_BOB_HEIGHT

        screen_x = int(round(self.x - camera.x))
        screen_y = int(round(self.y - camera.y + bob))

        pygame.draw.circle(surface, COIN_COLOR, (screen_x, screen_y), COIN_RADIUS)
        pygame.draw.circle(surface, COIN_EDGE, (screen_x, screen_y), COIN_RADIUS, 2)


class Heart:
    def __init__(self, x, y, heal=HEART_HEAL_AMOUNT):
        # x and y are the CENTER of the heart, in world space
        self.x = float(x)
        self.y = float(y)
        self.heal = heal
        self.time = 0.0
        self.picked = False

    def update(self, dt):
        self.time += dt

    def get_rect(self):
        return pygame.Rect(
            int(self.x - HEART_SIZE / 2),
            int(self.y - HEART_SIZE / 2),
            HEART_SIZE,
            HEART_SIZE,
        )

    def draw(self, surface, camera):
        # hearts pulse a little so they are easy to spot
        pulse = 1 + 0.08 * math.sin(self.time * 6)
        size = HEART_SIZE * pulse

        cx = int(round(self.x - camera.x))
        cy = int(round(self.y - camera.y))
        half = size / 2
        radius = int(size / 4)

        # a heart is two circles on top and a triangle pointing down
        left_circle = (int(cx - half / 2), int(cy - half / 3))
        right_circle = (int(cx + half / 2), int(cy - half / 3))
        bottom_point = (cx, int(cy + half))
        top_left = (int(cx - half), int(cy - half / 3))
        top_right = (int(cx + half), int(cy - half / 3))

        pygame.draw.circle(surface, HEART_COLOR, left_circle, radius)
        pygame.draw.circle(surface, HEART_COLOR, right_circle, radius)
        pygame.draw.polygon(surface, HEART_COLOR, [top_left, top_right, bottom_point])
        pygame.draw.polygon(surface, HEART_EDGE, [top_left, top_right, bottom_point], 2) 