import sys
import pygame
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BG_COLOR, TEXT_COLOR,
    TILE_SIZE, LEVEL_FILE,
)
from player import Player
from world import World, load_map
from camera import Camera
from debug import DebugOverlay


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.running = True

        rows, spawn_col, spawn_row = load_map(LEVEL_FILE)
        self.world = World(rows)

        # spawn in the middle of the S tile from the map file
        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE / 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE / 2
        self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.world.cols * TILE_SIZE, self.world.rows * TILE_SIZE)
        self.camera.snap(self.player.x, self.player.y)

        self.debug = DebugOverlay()

    def run(self):
        # main loop, runs every frame until you quit
        while self.running:
            # dt is how many seconds passed since last frame
            # using it makes movement the same speed on fast and slow pcs
            dt = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_F3:
                    self.debug.toggle()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.world)
        self.camera.follow(self.player.x, self.player.y, dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # the hint stays in the same spot on screen, it doesnt move with the camera
        hint = self.font.render("WASD / arrows to move, F3 debug, ESC to quit", True, TEXT_COLOR)
        self.screen.blit(hint, (10, 10))

        if self.debug.visible:
            self.debug.draw_grid(self.screen, self.camera)
            self.debug.draw_info(self.screen, self.clock, self.player, self.world, self.camera)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run() 