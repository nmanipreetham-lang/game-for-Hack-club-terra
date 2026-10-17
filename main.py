import os
import sys
import random
import pygame
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BG_COLOR, TEXT_COLOR, TILE_SIZE,
)
from player import Player, ATTACK_DAMAGE
from enemy import Enemy
from world import World, load_map
from camera import Camera
from debug import DebugOverlay
from dialog import DialogBox
from signs import SIGN_MESSAGES
from minimap import Minimap
from hud import draw_health_bar
from pickups import Coin, Heart, COIN_VALUES, HEART_DROP_CHANCE
from spawner import EnemySpawner
from crowd import separate_enemies, alert_nearby_enemies, crowd_report
from damage import DamageTextList
from projectile import (
    Projectile, PROJECTILE_DAMAGE, THROW_COOLDOWN,
    ENEMY_SHOT_SPEED, ENEMY_SHOT_LIFETIME, ENEMY_SHOT_DAMAGE, ENEMY_SHOT_COLOR,
    REFLECT_DAMAGE,
)

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

COMBO_WINDOW = 1.5
COMBO_MAX_BONUS = 3

LEVEL_FILES = [
    "maps/level_01.txt",
    "maps/level_02.txt",
]

ENEMY_SPAWN_CHARS = {
    "E": "normal",
    "R": "runner",
    "B": "brute",
    "P": "spitter",
}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.running = True

        self.debug = DebugOverlay()
        self.dialog = DialogBox()
        self.minimap_visible = True
        self.kills = 0
        self.coins = 0
        self.deflects = 0
        self.combo = 0
        self.combo_timer = 0.0
        self.damage = DamageTextList()
        self.projectiles = []
        self.enemy_shots = []
        self.rock_cooldown = 0.0
        self.level_index = 0
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        rows, spawn_col, spawn_row = load_map(os.path.join(BASE_DIR, LEVEL_FILES[index]))
        self.world = World(rows)

        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE / 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE / 2
        self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.world.cols * TILE_SIZE, self.world.rows * TILE_SIZE)
        self.camera.snap(self.player.x, self.player.y)

        self.minimap = Minimap(self.world)

        self.enemies = []
        spawn_points = []
        for row_index, row in enumerate(rows):
            for col_index, char in enumerate(row):
                if char in ENEMY_SPAWN_CHARS:
                    kind = ENEMY_SPAWN_CHARS[char]
                    x = col_index * TILE_SIZE + TILE_SIZE / 2
                    y = row_index * TILE_SIZE + TILE_SIZE / 2
                    self.enemies.append(Enemy(x, y, kind))
                    spawn_points.append((kind, x, y))

        self.spawner = EnemySpawner(spawn_points)

        self.ground_coins = []
        self.ground_hearts = []
        self.projectiles = []
        self.enemy_shots = []
        self.combo = 0
        self.combo_timer = 0.0

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.running = False

                elif event.key == pygame.K_F3:
                    self.debug.toggle()

                elif event.key == pygame.K_r:
                    self.throw_rock()

                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    if not self.dialog.is_open():
                        self.player.try_roll()

                elif event.key == pygame.K_m:
                    self.minimap_visible = not self.minimap_visible

                elif event.key == pygame.K_e:
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.try_read_sign()

                elif event.key == pygame.K_SPACE:
                    if not self.dialog.is_open():
                        self.player_attack()

    def try_read_sign(self):
        sign_number = self.world.find_sign_near(self.player.x, self.player.y)
        if sign_number is None:
            return

        messages = SIGN_MESSAGES.get(self.level_index, [])
        if sign_number < len(messages):
            self.dialog.open(messages[sign_number])
        else:
            self.dialog.open("this sign is blank")

    def throw_rock(self):
        if self.rock_cooldown > 0 or self.dialog.is_open():
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_x = mouse_x + int(round(self.camera.x))
        target_y = mouse_y + int(round(self.camera.y))
        self.projectiles.append(Projectile(self.player.x, self.player.y, target_x, target_y))
        self.rock_cooldown = THROW_COOLDOWN

    def update_projectiles(self, dt):
        if self.rock_cooldown > 0:
            self.rock_cooldown -= dt

        for projectile in self.projectiles:
            projectile.update(dt, self.world.walls)
            hit = projectile.check_enemies(self.enemies, PROJECTILE_DAMAGE)
            if hit is not None:
                self.damage_texts.add(hit.x, hit.y - hit.size / 2, PROJECTILE_DAMAGE)
                if not hit.is_alive():
                    self.on_enemy_died(hit)

        self.projectiles = [projectile for projectile in self.projectiles if projectile.alive]

    def update_enemy_shots(self, dt):
        for shot in self.enemy_shots:
            shot.update(dt, self.world.walls)

            if shot.reflected:
                hit = shot.check_enemies(self.enemies, REFLECT_DAMAGE)
                if hit is not None:
                    self.damage_texts.add(hit.x, hit.y - hit.size / 2, REFLECT_DAMAGE)
                    if not hit.is_alive():
                        self.on_enemy_died(hit)
            else:
                shot.check_player(self.player, ENEMY_SHOT_DAMAGE)

        self.enemy_shots = [shot for shot in self.enemy_shots if shot.alive]

    def fire_enemy_shots(self):
        for enemy in self.enemies:
            if enemy.try_shoot(self.player, self.world.walls):
                shot = Projectile(
                    enemy.x, enemy.y, self.player.x, self.player.y,
                    speed=ENEMY_SHOT_SPEED, lifetime=ENEMY_SHOT_LIFETIME,
                )
                shot.color = ENEMY_SHOT_COLOR
                self.enemy_shots.append(shot)

    def player_attack(self):
        hitbox = self.player.try_attack()
        if hitbox is None:
            return

        for shot in self.enemy_shots:
            if not shot.reflected and shot.alive and hitbox.colliderect(shot.get_rect()):
                shot.reflect()
                self.deflects += 1

        # every hit you land in a row adds a little damage, up to a cap
        bonus = min(self.combo, COMBO_MAX_BONUS)
        damage = ATTACK_DAMAGE + bonus
        landed = False

        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            if hitbox.colliderect(enemy.get_rect()):
                enemy.take_damage(damage)
                self.damage_texts.add(enemy.x, enemy.y - enemy.size / 2, damage)
                enemy.knockback(self.player.x, self.player.y)
                landed = True
                if not enemy.is_alive():
                    self.on_enemy_died(enemy)

        # a swing that connects keeps the combo alive, a miss does not
        if landed:
            self.combo += 1
            self.combo_timer = COMBO_WINDOW

    def on_enemy_died(self, enemy):
        self.kills += 1

        value = COIN_VALUES.get(enemy.kind, 1)
        self.ground_coins.append(Coin(enemy.x, enemy.y, value))

        chance = HEART_DROP_CHANCE.get(enemy.kind, 0.0)
        if random.random() < chance:
            self.ground_hearts.append(Heart(enemy.x, enemy.y))

    def update(self, dt):
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo = 0

        if not self.dialog.is_open():
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.world)

            tile_col = int(self.player.x // TILE_SIZE)
            tile_row = int(self.player.y // TILE_SIZE)
            if self.world.get_char_at(tile_col, tile_row) == "D":
                next_index = (self.level_index + 1) % len(LEVEL_FILES)
                self.load_level(next_index)
                return

            alert_nearby_enemies(self.enemies, self.player, self.world.walls)

            for enemy in self.enemies:
                enemy.update(dt, self.player, self.world.walls)
                if enemy.is_alive() and enemy.get_rect().colliderect(self.player.get_rect()):
                    self.player.take_damage(enemy.damage)

            self.fire_enemy_shots()
            self.update_enemy_shots(dt)

            separate_enemies(self.enemies, self.world.walls)

            self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]

            new_enemy = self.spawner.update(dt, self.enemies, self.player)
            if new_enemy is not None:
                self.enemies.append(new_enemy)

            self.update_pickups(dt)
            self.damage_texts.update(dt)
            self.update_projectiles(dt)

            if not self.player.is_alive():
                self.load_level(self.level_index)
                return

        self.camera.follow(self.player.x, self.player.y, dt)

    def update_pickups(self, dt):
        player_rect = self.player.get_rect()

        for coin in self.ground_coins:
            coin.update(dt)
            if coin.get_rect().colliderect(player_rect):
                self.coins += coin.value
                coin.value = 0
        self.ground_coins = [coin for coin in self.ground_coins if coin.value > 0]

        for heart in self.ground_hearts:
            heart.update(dt)
            if heart.get_rect().colliderect(player_rect):
                self.player.health = min(
                    self.player.max_health,
                    self.player.health + heart.heal,
                )
                heart.picked = True
        self.ground_hearts = [heart for heart in self.ground_hearts if not heart.picked]

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.world.draw(self.screen, self.camera)

        for coin in self.ground_coins:
            coin.draw(self.screen, self.camera)

        for heart in self.ground_hearts:
            heart.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        self.damage_texts.draw(self.screen, self.camera)

        for projectile in self.projectiles:
            projectile.draw(self.screen, self.camera)

        for shot in self.enemy_shots:
            shot.draw(self.screen, self.camera)

        self.player.draw(self.screen, self.camera)

        hint = self.font.render(
            "WASD move, SPACE swing, R rock, Shift roll, E sign, M minimap, F3 debug, ESC quit", True, TEXT_COLOR
        )
        self.screen.blit(hint, (10, 10))

        level_text = self.font.render(f"level {self.level_index + 1}", True, TEXT_COLOR)
        self.screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        if self.minimap_visible:
            minimap_x = WIDTH - self.minimap.width - 10
            self.minimap.draw(self.screen, self.player, (minimap_x, 40))

        draw_health_bar(self.screen, self.font, self.player.health, self.player.max_health)

        coins_text = self.font.render(f"coins: {self.coins}", True, TEXT_COLOR)
        self.screen.blit(coins_text, (WIDTH - coins_text.get_width() - 10, HEIGHT - 54))

        kills_text = self.font.render(f"kills: {self.kills}", True, TEXT_COLOR)
        self.screen.blit(kills_text, (WIDTH - kills_text.get_width() - 10, HEIGHT - 30))

        deflect_text = self.font.render(f"deflects: {self.deflects}", True, TEXT_COLOR)
        self.screen.blit(deflect_text, (WIDTH - deflect_text.get_width() - 10, HEIGHT - 78))

        if self.combo > 0:
            combo_text = self.font.render(
                f"combo x{self.combo}  +{min(self.combo, COMBO_MAX_BONUS)} dmg", True, TEXT_COLOR
            )
            self.screen.blit(combo_text, (10, HEIGHT - 30))

        if self.debug.visible:
            self.debug.draw_grid(self.screen, self.camera)
            self.debug.draw_info(self.screen, self.clock, self.player, self.world, self.camera, crowd_report(self.enemies))

        self.dialog.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run() 