import pygame
from settings import PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLOR


class Player:
    def __init__(self, x, y):
        # x and y are the CENTER of the player
        self.x = float(x)
        self.y = float(y)
        self.size = PLAYER_SIZE
        self.base_speed = PLAYER_SPEED

    def get_direction(self, keys):
        # returns a direction like (-1, 0) for left
        dx = 0
        dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        return dx, dy

    def update(self, dt, keys, world):
        dx, dy = self.get_direction(keys)

        # if you go diagonal you would be faster than straight
        # so i multiply by 0.7 (about 1/sqrt(2))
        if dx != 0 and dy != 0:
            dx *= 0.7
            dy *= 0.7

        # the tile under you decides how fast you walk (grass, sand, etc)
        speed = self.base_speed * world.speed_at(self.x, self.y)

        # i move one axis at a time so you can slide along a wall
        # instead of getting stuck on it when going diagonal
        self.x += dx * speed * dt
        self.check_wall_x(world.walls, dx)

        self.y += dy * speed * dt
        self.check_wall_y(world.walls, dy)

    def check_wall_x(self, walls, dx):
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if dx > 0:
                    # was moving right, so push back to the left side of the wall
                    self.x = wall.left - self.size / 2
                elif dx < 0:
                    # was moving left, so push back to the right side of the wall
                    self.x = wall.right + self.size / 2
                rect = self.get_rect()

    def check_wall_y(self, walls, dy):
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if dy > 0:
                    self.y = wall.top - self.size / 2
                elif dy < 0:
                    self.y = wall.bottom + self.size / 2
                rect = self.get_rect()

    def get_rect(self):
        # this rect is in WORLD space (the whole map), not the screen
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def draw(self, surface, camera):
        # camera.apply moves the player to where it shows up on screen
        screen_rect = camera.apply(self.get_rect())
        pygame.draw.rect(surface, PLAYER_COLOR, screen_rect, border_radius=6)
        