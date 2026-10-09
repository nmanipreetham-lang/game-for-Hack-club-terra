import pygame 
from settings import PLAYER_SPEED,PLAYER_SIZE,PLAYER_COLOR,WIDTH,HEIGHT

class Player:
    def __init__(self,x,y):
        # x and y are the CENTER of the player 
        self.x = float(x)
        self.y =float(y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED

        def get_directions(self, keys):
            #returns a direction like (1,0) for left 
            dx = 0
            dy = 0 
            if keys [pygame.K_a] or keys [pygame.K_LEFT]:
                dx -= 1
                if keys [pygame.K_d] or keys[pygame.K_RIGHT]:
                    dx += 1
                    if keys [pygame>K_w] or keys [pygame.K_UP]:
                        dy -= 1
                        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                            dy += 1
                            return dx, dy
                        def update(self,dt,keys):
                            dx,dy = self.get_direction(keys)
if dx !=0 and dy !=0:
    dx *= 0.7 
    dy *= 0.7
    self.x += dx * self.speed * dt
    self.y += dy * self.speed * dt

    # dont let the player leave the screen 
    half = self.size /2 
    self.x = max(half, min(WIDTH - half, self.x))
    self.y = max(half, min(HEIGHT -half, self.y))

def  get_rect(self):
    return pygame.rect(
        self.x -self.size / 2,
        self.y - self.size /2,
        self.size,
        self.size,

    )

def draw (self,surface):
    pygame.draw.rect(surface,PLAYER_COLOR< self.grt_rect(), border_radius=6)
     

                        

