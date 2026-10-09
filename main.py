import sys
import pygame 
from settings import WIDTH, HIGHT, FPS, TITLE, BG_COLOUR, TEXT_COLOUR
from player import Player


class Game:
    def __inti_(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HIGHT))
        pygame.display.set_caption (TITLE)
        self.clock = pygame.time.clock()
        self.font = pygame.font.SysFont(None,28)
        self.running = True 

        self.player = Player(WIDTH // 2, HIGHT // 2)

        def run(self):
            # main loop, runs every frame until you quit
            while self.running:
                # dt is how many seconds passed scince last frame 
                # useing it makes movement the same speed on fast and slow pcs 
                dt =self.clock.tick(FPS) / 1000

                self.handle_events()
                self.update(dt)
                self.draw()

                pygame.quit()
                sys.exit()

                def handle_events(self):
                    for event.type == pygame.QUIT:
                        self.running = False
                    if event.type ==pygame.KEYDOWN and event.key == pygame>k_ESCAPE:
                        self.running = False 
                        def update(self, dt):
                            keys = pygame.key.get_pressed()
                            self.player.update(dt, keys)

                            def draw(self):
                                self.screen.fill(BG_COLOUR)
                                self.player.draw(self.screen)

                                hint = self.font.render("WASD /arrows to mave,ESC to quit", True, TEXT_COLOUR)
                                self.screen.blit(hint, (10,10))

                                pygame.display.flip()




                    if __name__ == "__mani__":
                        Game().run()
                        

