import math
import pygame

# how many coins each enemy type drops when it dies
COIN_VALUES = {
    "normal": 1,
    "runner": 1,
    "brute": 3,
}

COIN_COLOR = (250, 210, 60)
COIN_EDGE = (180, 140, 30)
COIN_RADIUS = 7
COIN_BOB_HEIGHT = 3   # how far up and down the coin bobs (pixels)
COIN_BOB_SPEED = 4    # how fast it bobs


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