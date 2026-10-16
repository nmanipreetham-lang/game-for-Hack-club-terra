import math
import pygame

PROJECTILE_SPEED = 420
PROJECTILE_LIFETIME = 1.2
PROJECTILE_DAMAGE = 1
PROJECTILE_SIZE = 8
PROJECTILE_COLOR = (200, 200, 210)
THROW_COOLDOWN = 0.6


class Projectile:
    def __init__(self, x, y, target_x, target_y):
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance == 0:
            dx, dy, distance = 1.0, 0.0, 1.0

        self.x = float(x)
        self.y = float(y)
        self.vx = dx / distance * PROJECTILE_SPEED
        self.vy = dy / distance * PROJECTILE_SPEED
        self.size = PROJECTILE_SIZE
        self.lifetime = PROJECTILE_LIFETIME
        self.alive = True

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def update(self, dt, walls):
        if not self.alive:
            return

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        rect = self.get_rect()
        for wall in walls:
            if rect.colliderect(wall):
                self.alive = False
                return

    def check_enemies(self, enemies, damage):
        if not self.alive:
            return None

        rect = self.get_rect()
        for enemy in enemies:
            if enemy.is_alive() and rect.colliderect(enemy.get_rect()):
                enemy.take_damage(damage)
                enemy.knockback(self.x, self.y)
                self.alive = False
                return enemy

        return None

    def draw(self, surface, camera):
        if not self.alive:
            return

        screen_rect = camera.apply(self.get_rect())
        pygame.draw.rect(surface, PROJECTILE_COLOR, screen_rect, border_radius=2)    