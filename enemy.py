import math
import random
import pygame

ENEMY_COLOR = (200, 70, 70)
ENEMY_HURT_COLOR = (255, 255, 255)  # the enemy flashes this color when hit
ENEMY_BAR_BACK = (60, 20, 20)
ENEMY_BAR_FILL = (120, 230, 120)
ENEMY_SIZE = 24

ENEMY_MAX_HEALTH = 3
ENEMY_DAMAGE = 10  # how much health the player loses when touching an enemy

ENEMY_WANDER_SPEED = 60   # pixels per second when just walking around
ENEMY_CHASE_SPEED = 110   # pixels per second when chasing the player
ENEMY_SIGHT = 200         # how close (in pixels) the player has to be to get chased

ENEMY_HURT_TIME = 0.2     # how long the white flash lasts
ENEMY_KNOCK_SPEED = 180   # how fast the enemy gets pushed back when hit
ENEMY_KNOCK_TIME = 0.2    # how long the push lasts


class Enemy:
    def __init__(self, x, y):
        # x and y are the CENTER of the enemy, in world space
        self.x = float(x)
        self.y = float(y)
        self.size = ENEMY_SIZE
        self.health = ENEMY_MAX_HEALTH

        self.direction = (0, 0)
        self.change_timer = 0.0
        self.chasing = False

        self.hurt_timer = 0.0
        self.knock_x = 0.0
        self.knock_y = 0.0
        self.knock_timer = 0.0

        self.pick_direction()

    def pick_direction(self):
        # random direction for wandering, sometimes it just stands still for a bit
        choices = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        self.direction = random.choice(choices)
        self.change_timer = random.uniform(1.0, 3.0)

    def is_alive(self):
        return self.health > 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.hurt_timer = ENEMY_HURT_TIME

    def knockback(self, from_x, from_y):
        # push the enemy directly away from the spot the hit came from
        push_x = self.x - from_x
        push_y = self.y - from_y
        length = math.hypot(push_x, push_y)
        if length == 0:
            push_x, push_y, length = 1, 0, 1

        self.knock_x = push_x / length * ENEMY_KNOCK_SPEED
        self.knock_y = push_y / length * ENEMY_KNOCK_SPEED
        self.knock_timer = ENEMY_KNOCK_TIME

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def update(self, dt, player, walls):
        if not self.is_alive():
            return

        if self.hurt_timer > 0:
            self.hurt_timer -= dt

        # while being pushed back the enemy doesnt think, it just slides
        if self.knock_timer > 0:
            self.knock_timer -= dt
            self.x += self.knock_x * dt
            self.hit_wall_x(walls, self.knock_x)
            self.y += self.knock_y * dt
            self.hit_wall_y(walls, self.knock_y)
            return

        to_x = player.x - self.x
        to_y = player.y - self.y
        distance = math.hypot(to_x, to_y)

        if 0 < distance < ENEMY_SIGHT:
            # the player is close, so walk straight at them
            self.chasing = True
            dx = to_x / distance
            dy = to_y / distance
            speed = ENEMY_CHASE_SPEED
        else:
            # nobody nearby, so wander in a random direction for a few seconds
            self.chasing = False
            self.change_timer -= dt
            if self.change_timer <= 0:
                self.pick_direction()
            dx, dy = self.direction
            speed = ENEMY_WANDER_SPEED

        # same axis by axis movement as the player so walls work the same way
        self.x += dx * speed * dt
        blocked = self.hit_wall_x(walls, dx)

        self.y += dy * speed * dt
        blocked = self.hit_wall_y(walls, dy) or blocked

        # walked into a wall while wandering, so turn around to a new direction
        if blocked and not self.chasing:
            self.pick_direction()

    def hit_wall_x(self, walls, dx):
        rect = self.get_rect()
        hit = False
        for wall in walls:
            if rect.colliderect(wall):
                hit = True
                if dx > 0:
                    self.x = wall.left - self.size / 2
                elif dx < 0:
                    self.x = wall.right + self.size / 2
                rect = self.get_rect()
        return hit

    def hit_wall_y(self, walls, dy):
        rect = self.get_rect()
        hit = False
        for wall in walls:
            if rect.colliderect(wall):
                hit = True
                if dy > 0:
                    self.y = wall.top - self.size / 2
                elif dy < 0:
                    self.y = wall.bottom + self.size / 2
                rect = self.get_rect()
        return hit

    def draw(self, surface, camera):
        if not self.is_alive():
            return

        # flash white for a moment after getting hit
        color = ENEMY_HURT_COLOR if self.hurt_timer > 0 else ENEMY_COLOR

        screen_rect = camera.apply(self.get_rect())
        pygame.draw.rect(surface, color, screen_rect, border_radius=4)

        # only show the health bar once the enemy got hit
        if self.health < ENEMY_MAX_HEALTH:
            back = pygame.Rect(screen_rect.x, screen_rect.y - 8, screen_rect.width, 4)
            fill_width = int(screen_rect.width * self.health / ENEMY_MAX_HEALTH)
            fill = pygame.Rect(screen_rect.x, screen_rect.y - 8, fill_width, 4)
            pygame.draw.rect(surface, ENEMY_BAR_BACK, back)
            pygame.draw.rect(surface, ENEMY_BAR_FILL, fill) 