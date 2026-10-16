import pygame
from settings import PLAYER_SPEED, PLAYER_SIZE, PLAYER_COLOR

PLAYER_MAX_HEALTH = 100
HURT_INVINCIBLE_TIME = 1.0

ATTACK_DAMAGE = 1
ATTACK_COOLDOWN = 0.4
ATTACK_REACH = 30
ATTACK_SIZE = 36
SWING_SHOW_TIME = 0.15
SWING_COLOR = (255, 230, 120)

ROLL_SPEED = 520
ROLL_TIME = 0.3
ROLL_COOLDOWN = 1.0
ROLL_COLOR = (180, 225, 255)


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.size = PLAYER_SIZE
        self.base_speed = PLAYER_SPEED

        self.max_health = PLAYER_MAX_HEALTH
        self.health = PLAYER_MAX_HEALTH
        self.hurt_timer = 0.0

        self.facing_x = 1
        self.facing_y = 0
        self.attack_cooldown = 0.0
        self.swing_timer = 0.0
        self.swing_rect = None

        self.roll_timer = 0.0
        self.roll_cooldown = 0.0
        self.roll_dx = 0.0
        self.roll_dy = 0.0

    def is_rolling(self):
        return self.roll_timer > 0

    def take_damage(self, amount):
        if self.is_rolling() or self.hurt_timer > 0 or not self.is_alive():
            return

        self.health = max(0, self.health - amount)
        self.hurt_timer = HURT_INVINCIBLE_TIME

    def is_alive(self):
        return self.health > 0

    def try_roll(self):
        if self.roll_cooldown > 0 or self.is_rolling() or not self.is_alive():
            return False

        length = (self.facing_x ** 2 + self.facing_y ** 2) ** 0.5
        if length == 0:
            return False

        self.roll_dx = self.facing_x / length
        self.roll_dy = self.facing_y / length
        self.roll_timer = ROLL_TIME
        self.roll_cooldown = ROLL_COOLDOWN
        return True

    def try_attack(self):
        if self.attack_cooldown > 0 or not self.is_alive():
            return None

        self.attack_cooldown = ATTACK_COOLDOWN
        self.swing_timer = SWING_SHOW_TIME

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
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.swing_timer > 0:
            self.swing_timer -= dt
        if self.roll_cooldown > 0:
            self.roll_cooldown -= dt

        if self.is_rolling():
            self.roll_timer -= dt
            speed = ROLL_SPEED * world.speed_at(self.x, self.y)
            self.x += self.roll_dx * speed * dt
            self.check_wall_x(world.walls, self.roll_dx)
            self.y += self.roll_dy * speed * dt
            self.check_wall_y(world.walls, self.roll_dy)
            return

        dx, dy = self.get_direction(keys)

        if dx != 0 or dy != 0:
            self.facing_x = dx
            self.facing_y = dy

        if dx != 0 and dy != 0:
            dx *= 0.7
            dy *= 0.7

        speed = self.base_speed * world.speed_at(self.x, self.y)

        self.x += dx * speed * dt
        self.check_wall_x(world.walls, dx)

        self.y += dy * speed * dt
        self.check_wall_y(world.walls, dy)

    def check_wall_x(self, walls, dx):
        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                if dx > 0:
                    self.x = wall.left - self.size / 2
                elif dx < 0:
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
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def draw(self, surface, camera):
        if self.is_rolling():
            screen_rect = camera.apply(self.get_rect())
            pygame.draw.rect(surface, ROLL_COLOR, screen_rect, border_radius=6)
        elif not (self.hurt_timer > 0 and int(self.hurt_timer * 10) % 2 == 0):
            screen_rect = camera.apply(self.get_rect())
            pygame.draw.rect(surface, PLAYER_COLOR, screen_rect, border_radius=6)

        if self.swing_timer > 0 and self.swing_rect is not None:
            swing_screen = camera.apply(self.swing_rect)
            pygame.draw.rect(surface, SWING_COLOR, swing_screen, 3)