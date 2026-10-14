import pygame 

# little numbers that pop up over an enemy when you hit it 
# so you can actually see how much damage each swing did 

DAMAGE_TEXT_TIME = 0.6        # how long the number sstayes on screen 
DAMAGE_TEXT_RISE = 40         # how many pixels per second it floats up 
DAMAGE_TEXT_COLOR = (225, 225, 225)
DAMAGE_TEXT_FONT_SIZE = 22 


class FloatingText:
    def __init__(self, x, y, text):
        # x and y are in world space, same as everything else 
        self.x = float(x)
        self.y = float(y)
        self.text = text 
        self.timer = DAMAGE_TEXT_TIME 


class DamageTextList: 
    def __init__(self):
        self.items = []
        self.font = None  # made the first time we draw, pygame needs to be ready first 

    def add(self, x, y, amount):
        # make a new number above the spot that got hit 
        self.items.append(FloatingText(x, y, str(amount)))

    def update(self, dt):
        for item in self.items:
            item.timer -=dt
            item.y -= DAMAGE_TEXT_RISE * dt 

        # throw away the ones that are done 
        self.items = [item for item in self.items if item.timer > 0]

    def draw(self, surface, camera):
        if self.font is None: 
            self.font = pygame.font.SysFont(None, DAMAGE_TEXT_FONT_SIZE)

        for item in self.items:
            # turn the world positions into a screen position 
            spot = camera.apply(pygame.Rect(int(item.x), int(item.y), 0, 0))

            text = self.font.render(item.text, True, DAMAGE_TEXT_COLOR)

            # fade out as the timer runs down 
            fade = int(255 * max(0, item.timer) / DAMAGE_TEXT_TIME)
            text.set_alpha(fade)
            # center the number over the spot 
            surface.blit(text, (spot.x - text.get_width()  // 2, spot.y))                            