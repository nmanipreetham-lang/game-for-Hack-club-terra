import pygame
from settings import TILE_SIZE, WIDTH, HEIGHT, TEXT_COLOR

GRID_COLOR = (70, 70, 80)


class DebugOverlay:
    def __init__(self):
        self.visible = False
        self.font = pygame.font.SysFont(None, 22)

    def toggle(self):
        self.visible = not self.visible

    def draw_grid(self, surface, camera):
        start_x = (-int(round(camera.x))) % TILE_SIZE
        for x in range(start_x, WIDTH, TILE_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))

        start_y = (-int(round(camera.y))) % TILE_SIZE
        for y in range(start_y, HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

    def draw_info(self, surface, clock, player, world, camera, extra_lines=None):
        tile_col = int(player.x // TILE_SIZE)
        tile_row = int(player.y // TILE_SIZE)

        lines = [
            f"fps: {int(clock.get_fps())}",
            f"player: {int(player.x)}, {int(player.y)}",
            f"tile: col {tile_col}, row {tile_row}",
            f"camera: {int(camera.x)}, {int(camera.y)}",
            f"map: {world.cols} x {world.rows} tiles",
            f"walls: {len(world.walls)}",
        ]

        if extra_lines:
            lines.append("-- enemies --")
            lines.extend(extra_lines)

        box = pygame.Surface((220, 20 * len(lines) + 10))
        box.set_alpha(170)
        box.fill((0, 0, 0))
        surface.blit(box, (8, 36))

        y = 42
        for line in lines:
            text = self.font.render(line, True, TEXT_COLOR)
            surface.blit(text, (14, y))
            y += 20 