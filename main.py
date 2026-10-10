import sys 
import pygame
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BG_COLOR, TEXT_COLOR, TILE_SIZE
)

from player import Player
from world import World,load_map
from camera import Camera 
from debug import DebugOverlay
from dialog import DialogBox
from signs import SIGN_MESSAGES
from minimap import Minimap

# the levels in order, walking onto a door moves you to the next one
# the last level loops back to the first one
LEVEL_FILES = [
    "maps/level_01.txt",
    "maps/level_02.txt",
]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.running = True

        self.debug = DebugOverlay()
        self.dialog = DialogBox()
        self.minimap_visible = True
        self.level_index = 0
        self.load_level(0)

    def load_level(self, index):
        # loads a map, puts the player on its spawn tile and resets the camera
        self.level_index = index
        rows, spawn_col, spawn_row = load_map(LEVEL_FILES[index])
        self.world = World(rows)

        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE / 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE / 2
        self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.world.cols * TILE_SIZE, self.world.rows * TILE_SIZE)
        self.camera.snap(self.player.x, self.player.y)

        # the minimap is built once per level
        self.minimap = Minimap(self.world)

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
                    # first ESC closes the sign box, second ESC quits
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.running = False

                elif event.key == pygame.K_F3:
                    self.debug.toggle()

                elif event.key == pygame.K_m:
                    self.minimap_visible = not self.minimap_visible

                elif event.key == pygame.K_e:
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.try_read_sign()

    def try_read_sign(self):
        sign_number = self.world.find_sign_near(self.player.x, self.player.y)
        if sign_number is None:
            return

        messages = SIGN_MESSAGES.get(self.level_index, [])
        if sign_number < len(messages):
            self.dialog.open(messages[sign_number])
        else:
            self.dialog.open("this sign is blank")

    def update(self, dt):
        # while the sign box is open the player stands still
        if not self.dialog.is_open():
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.world)

            # check if the player is standing on a door
            tile_col = int(self.player.x // TILE_SIZE)
            tile_row = int(self.player.y // TILE_SIZE)
            if self.world.get_char_at(tile_col, tile_row) == "D":
                next_index = (self.level_index + 1) % len(LEVEL_FILES)
                self.load_level(next_index)
                return

        self.camera.follow(self.player.x, self.player.y, dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # the hint stays in the same spot on screen, it doesnt move with the camera
        hint = self.font.render(
            "WASD / arrows to move, E sign, M minimap, F3 debug, ESC quit", True, TEXT_COLOR
        )
        self.screen.blit(hint, (10, 10))

        level_text = self.font.render(f"level {self.level_index + 1}", True, TEXT_COLOR)
        self.screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        if self.minimap_visible:
            minimap_x = WIDTH - self.minimap.width - 10
            self.minimap.draw(self.screen, self.player, (minimap_x, 40))

        if self.debug.visible:
            self.debug.draw_grid(self.screen, self.camera)
            self.debug.draw_info(self.screen, self.clock, self.player, self.world, self.camera)

        self.dialog.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
