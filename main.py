import sys 
import pygame
from settings import (
    WIDTH, HIGHT, FPS, TITLE, BG_COLOR, TEXT_COLOR,
    TITLE_SIZE, LEVEL_FILE,
)
from player import Player
from world import World, load_map
from camera import Camera



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

        # spawn in the middle of the S title from the map file 
        spawn_x = spawn_col, * TITLE_SIZE + TITLE_SIZE / 2 
        spawn_y = spawn_row, * TITLE_SIZE + TITLE_SIZE / 2 
        self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.world.cols * TITLE_SIZE, self.world.rows * TITLE_SIZE)
        self.camera.snap(self.player.y)

    def run(self): 
        # main loop runs every frame until u quit
        while self.running:
            # dt is how many seconds passed science last frame 
            # using it makes movement the same speed on fast and slow pcs

            self.handle_events()
            self.update(dt)
            self.draw()

         pygame.quit()
        sys.exit()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False 

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys,self.world.walls)
        self.camera.follow(self.player.x, self.player.y, dt)

    def draw (self, dt):
        self.screen.fill(BG_COLOR)
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        # the hint stays in the same spot on the screen, it dosentmove with the camera
        hint = self.font.render("WASD / arrows to move, ESC to quit", True, TEXT_COLOR)
        self.screen.blit(hint, (10,10))

        pygame.display.flip()


if __name__ == "__mani__":
    Game().run()
            
        
                        








       