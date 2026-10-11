import pygame 
from settings import HEIGHT, TEXT_COLOR

BAR_X = 10
BAR_Y = HEIGHT - 30
BAR_WIDTH = 200
BAR_HEIGHT = 16
BAR_BACK = (60, 20, 20)
BAR_FILL = (220, 60, 60)
BAR_BORDER = (230, 230, 230)


def draw_health_bar(surface, font, current, maximum):
    # the red part shrinks as you take damage
    ratio = max(0, current / maximum)

    back = pygame.Rect(BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT)
    fill = pygame.Rect(BAR_X, BAR_Y, int(BAR_WIDTH * ratio), BAR_HEIGHT)

    pygame.draw.rect(surface, BAR_BACK, back)
    pygame.draw.rect(surface, BAR_FILL, fill)
    pygame.draw.rect(surface, BAR_BORDER, back,2)

    text = font.render(f"hp {current}/{maximum}", True, TEXT_COLOR)
    surface.blit(text, (BAR_X + BAR_WIDTH + 10, BAR_Y - 2)) 
