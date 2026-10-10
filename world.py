import pygame
from settings import TILE_SIZE, WIDTH, HEIGHT
from tiles import get_tile


def load_map(path):
    # reads the map file and returns (rows, spawn_col, spawn_row)
    with open(path, "r") as f:
        rows = [line.rstrip("\n") for line in f if line.strip() != ""]

    # if one row is shorter than the others, fill the end with floor
    # so a typo doesnt crash the whole game
    widest = max(len(row) for row in rows)
    rows = [row.ljust(widest, ".") for row in rows]

    spawn_col, spawn_row = 1, 1
    for row_index, row in enumerate(rows):
        for col_index, char in enumerate(row):
            if char == "S":
                spawn_col, spawn_row = col_index, row_index

    return rows, spawn_col, spawn_row


class World:
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])

        # one rect per solid tile so the player can bump into them
        self.walls = []
        # where every sign is, in reading order (left to right, top to bottom)
        self.sign_positions = []

        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                if get_tile(char)["solid"]:
                    self.walls.append(self.make_tile_rect(col_index, row_index))
                if char == "I":
                    self.sign_positions.append((col_index, row_index))

    def make_tile_rect(self, col, row):
        return pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def get_char_at(self, col, row):
        # outside the map counts as wall so nothing can walk off the edge
        if col < 0 or row < 0 or row >= self.rows or col >= self.cols:
            return "#"
        return self.layout[row][col]

    def speed_at(self, x, y):
        # what speed multiplier is the tile at this world position
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        return get_tile(self.get_char_at(col, row))["speed"]

    def find_sign_near(self, x, y):
        # checks the tile you are on and the 8 tiles around it
        # returns the sign number (0 for the first sign) or None if no sign is close
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)

        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                spot = (col + d_col, row + d_row)
                if spot in self.sign_positions:
                    return self.sign_positions.index(spot)
        return None

    def draw(self, surface, camera):
        # only draw the tiles that are actually on the screen
        start_col = max(0, int(camera.x // TILE_SIZE))
        end_col = min(self.cols, int((camera.x + WIDTH) // TILE_SIZE) + 2)
        start_row = max(0, int(camera.y // TILE_SIZE))
        end_row = min(self.rows, int((camera.y + HEIGHT) // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = get_tile(self.layout[row][col])
                rect = camera.apply(self.make_tile_rect(col, row))

                pygame.draw.rect(surface, tile["color"], rect)
                pygame.draw.rect(surface, tile["edge"], rect, tile["edge_width"]) 