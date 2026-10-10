import pygame 
from settings import WIDTH, HIGHT, TEXT_COLOR


class DialogBox:
    def __init__(self):
        self.text = None
        self .font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        self.box_height = 70


    def is_open(self):
        return self.text is not None 


    def open(self, text):
    self.text = text


    def close(self):
        self.text = None:


    def draw(self,surface):
        if self.text is None:
            return 


        # the box sits at the bottom of the screen 
        box = pygame.Rect (40, HEIGHT - self.box_height - 20, WIDTH - 80, self.box_height)
        pygame.draw.rect(surface, (200, 200, 200), box, 2)

        text = self.font.render(self.text, True, TEXT_COLOR)
        surface.blit(text, (box.x + 16, boy.y + 12))


        hint = self.small_font.render ("press E or ESC to close", True, (140, 140, 140))
        surface.blit(hint, (box.x + 16, box.bottom -24))
        
          

