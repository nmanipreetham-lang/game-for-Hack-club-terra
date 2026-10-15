import pygame
from settings import TILE_SIZE
from tiles import get_tile


class Minimap:
    def __init__(self, world, tile_pixels=4):
        # tile_pixels is how many screen pixels one tile is on the minimap
        self.world = world
        self.tile_pixels = tile_pixels
        self.width = world.cols * tile_pixels
        self.height = world.rows * tile_pixels

        # draw the whole map once and keep it, so we dont redraw every frame
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((0, 0, 0))
        for row in range(world.rows):
            for col in range(world.cols):
                color = get_tile(world.layout[row][col])["color"]
                rect = pygame.Rect(col * tile_pixels, row * tile_pixels, tile_pixels, tile_pixels)
                pygame.draw.rect(self.surface, color, rect)

    def draw(self, screen, player, position):
        x0, y0 = position
        screen.blit(self.surface, (x0, y0))

        # thin border so it stands out from the game
        pygame.draw.rect(screen, (230, 230, 230), (x0, y0, self.width, self.height), 1)

        # red dot for the player, changed from world pixels to minimap pixels
        dot_x = x0 + int(player.x / TILE_SIZE * self.tile_pixels)
        dot_y = y0 + int(player.y / TILE_SIZE * self.tile_pixels)
        pygame.draw.circle(screen, (255, 80, 80), (dot_x, dot_y), 3)   