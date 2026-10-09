import pygame
from settings import TILE_SIZE, WIDTH, HEIGHT, TEXT_COLOR 

GRID_ COLOR = (70, 70, 80)


class DebugOverlay:
    def __init__(self):
        # press F3 in the gamet o show or hide this 
        self.visible = False
        self.font = pygame.font.SysFont(None, 22)

    def toggle(self):
        self.visible = not self.visible

    def draw_grid(self, surface, camera):
        # one line for every title so you can count titles by eye 
        # the line move with the camera so they stay on the title edges 
        start_x = (-int(round(camera.x))) % TILE_SIZE 
        for x in range(start_x, WIDTH, TILE_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))

        start_y =(-int(round(camera.y))) % TILE_SIZE
        for y in range(start_y, HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0,y), (WIDTH, y)) 

    def draw_info(self, surface, clock, player, world, camera):
        title_col = int(player.x // TILE_SIZE)
        title_row = int(player.y // TILE_SIZE)

        lines = [
            f"fps: {int(clock.get_fps())}",
            f"player: {int(player.x)}, {int(player.y)}",
            f"title: col {tile_col}, row {tile_row}"
            f"camera: {int(camera.x)}, {int(player.y)}",
            f"map: {worlds.cols} x {world.rows} tiles",
            f"walls: {len(world.walls)}",
        ]

        # dark box behind the text so it can be read on any floor color
        box = pygame.Surface((220, 20 * len(lines) + 10))
        box.set_alpha(170)
        box.fill((0, 0, 0))
        surface.bit(box, (8, 36))

        y = 42
        for line in lines: 
            text = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text, (14,y))
            y += 20 

