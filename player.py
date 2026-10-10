import pygame
from settings import PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLOR

PLAYER_MAX_HEALTH = 100
HURT_INVINCIBLE_TIME = 1.0  # seconds you are safe after getting hit

# combat settings
ATTACK_DAMAGE = 1       # how much health one swing takes off an enemy
ATTACK_COOLDOWN = 0.4   # seconds you have to wait between swings
ATTACK_REACH = 30       # how far in front of your center the swing lands (pixels)
ATTACK_SIZE = 36        # width and height of the swing hitbox
SWING_SHOW_TIME = 0.15  # how long the swing is drawn on screen
SWING_COLOR = (255, 230, 120)


class Player:
    def __init__(self, x, y):
        # x and y are the CENTER of the player
        self.x = float(x)
        self.y = float(y)
        self.size = PLAYER_SIZE
        self.base_speed = PLAYER_SPEED

        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.hurt_timer = 0.0  # counts down after a hit

        # which way you are facing, so the swing goes the right way
        self.facing_x = 1
        self.facing_y = 0
        self.attack_cooldown = 0.0
        self.swing_timer = 0.0
        self.swing_rect = None

    def take_damage(self, amount):
        # while the hurt timer is running you cant get hit again
        # without this, one enemy would take all your health in a single frame
        if self.hurt_timer > 0 or not self.is_alive():
            return

        self.health = max(0, self.health - amount)
        self.hurt_timer = HURT_INVINCIBLE_TIME

    def is_alive(self):
        return self.health > 0

    def try_attack(self):
        # returns the hitbox of the swing, or None if you cant swing right now
        if self.attack_cooldown > 0 or not self.is_alive():
            return None

        self.attack_cooldown = ATTACK_COOLDOWN
        self.swing_timer = SWING_SHOW_TIME

        # the hitbox sits in front of the player, in the direction they face
        center_x = self.x + self.facing_x * ATTACK_REACH
        center_y = self.y + self.facing_y * ATTACK_REACH
        self.swing_rect = pygame.Rect(
            int(center_x - ATTACK_SIZE / 2),
            int(center_y - ATTACK_SIZE / 2),
            ATTACK_SIZE,
            ATTACK_SIZE,
        )
        return self.swing_rect

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
        # count down all the timers
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.swing_timer > 0:
            self.swing_timer -= dt

        dx, dy = self.get_direction(keys)

        # remember which way the player last moved, before we change dx and dy below
        if dx != 0 or dy != 0:
            self.facing_x = dx
            self.facing_y = dy

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
        # blink while you are invincible so you can see that you got hit
        if not (self.hurt_timer > 0 and int(self.hurt_timer * 10) % 2 == 0):
            screen_rect = camera.apply(self.get_rect())
            pygame.draw.rect(surface, PLAYER_COLOR, screen_rect, border_radius=6)

        # draw the swing for a short moment after attacking
        if self.swing_timer > 0 and self.swing_rect is not None:
            swing_screen = camera.apply(self.swing_rect)
            pygame.draw.rect(surface, SWING_COLOR, swing_screen, 3)
        