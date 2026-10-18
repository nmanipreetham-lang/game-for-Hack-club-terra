import math
import pygame

PROJECTILE_SPEED = 420
PROJECTILE_LIFETIME = 1.2
PROJECTILE_DAMAGE = 1
PROJECTILE_SIZE = 8
PROJECTILE_COLOR = (200, 200, 210)
THROW_COOLDOWN = 0.6

ENEMY_SHOT_SPEED = 240
ENEMY_SHOT_LIFETIME = 2.5
ENEMY_SHOT_DAMAGE = 8
ENEMY_SHOT_COLOR = (120, 230, 140)

REFLECT_SPEED_MULT = 1.4
REFLECT_LIFETIME = 1.5
REFLECT_DAMAGE = 3
REFLECT_COLOR = (255, 230, 120)


class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=PROJECTILE_SPEED, lifetime=PROJECTILE_LIFETIME):
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance == 0:
            dx, dy, distance = 1.0, 0.0, 1.0

        self.x = float(x)
        self.y = float(y)
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed
        self.size = PROJECTILE_SIZE
        self.lifetime = lifetime
        self.color = PROJECTILE_COLOR
        self.alive = True
        self.reflected = False

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def reflect(self):
        self.vx = -self.vx * REFLECT_SPEED_MULT
        self.vy = -self.vy * REFLECT_SPEED_MULT
        self.lifetime = REFLECT_LIFETIME
        self.color = REFLECT_COLOR
        self.reflected = True

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

    def check_player(self, player, damage):
        if not self.alive:
            return False

        if self.get_rect().colliderect(player.get_rect()):
            player.take_damage(damage)
            self.alive = False
            return True

        return False

    def draw(self, surface, camera):
        if not self.alive:
            return

        screen_rect = camera.apply(self.get_rect())
        pygame.draw.rect(surface, self.color, screen_rect, border_radius=2)