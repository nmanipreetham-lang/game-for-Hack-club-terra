import pygame
from settings import (
    TILE_SIZE, WIDTH, HEIGHT, FLOOR_COLOR, FLOOR_LINE_COLOR,
    WALL_COLOR, WALL_EDGE_COLOR, WATER_COLOR, WATER_EDGE_COLOR,
)

# every tile character and if the player can walk through it
SOLID_TILES = {"#", "~"}
FLOOR_TILES = {".", "S"}


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
        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                if char in SOLID_TILES:
                    self.walls.append(self.make_tile_rect(col_index, row_index))

    def make_tile_rect(self, col, row):
        return pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def draw(self, surface, camera):
        # only draw the tiles that are actually on the screen
        start_col = max(0, int(camera.x // TILE_SIZE))
        end_col = min(self.cols, int((camera.x + WIDTH) // TILE_SIZE) + 2)
        start_row = max(0, int(camera.y // TILE_SIZE))
        end_row = min(self.rows, int((camera.y + HEIGHT) // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                char = self.layout[row][col]
                rect = camera.apply(self.make_tile_rect(col, row))

                if char == "#":
                    pygame.draw.rect(surface, WALL_COLOR, rect)
                    pygame.draw.rect(surface, WALL_EDGE_COLOR, rect, 2)
                elif char == "~":
                    pygame.draw.rect(surface, WATER_COLOR, rect)
                    pygame.draw.rect(surface, WATER_EDGE_COLOR, rect, 2)
                else:
                    # floor and the spawn tile look the same
                    pygame.draw.rect(surface, FLOOR_COLOR, rect)
                    pygame.draw.rect(surface, FLOOR_LINE_COLOR, rect, 1)
