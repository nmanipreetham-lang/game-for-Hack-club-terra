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
from debug  import DebugOverlay
from dialog import DialogBox 
from signs import SIGN_MESSAGES 
from minimap import Minimap 
from hud import draw_health_bar
from pickups import Coin, Heart, COIN_VALUES, HEART_DROP_CHANCE
from spawner import EnemySpawner 

# the levels in order, walking onto a door moves you to the next one 
# the last level loops back to first one 
LEVEL_FILES = [
    "maps/level_01.txt",
    "maps/level_02.txt",

]
# which map character spawns which enemy type 
ENEMY_SPAWN_CHARS = {
    "E": "normal",
    "R": "runner",
    "B": "brute",
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
        self.kills = 0  # counts every enemy you have killed in this game
        self.coins = 0  # your total coins, this stays the same when you change levels
        self.level_index = 0
        self.load_level(0)

    def load_level(self, index):
        # loads a map, puts the player on its spawn tile and resets the camera
        self.level_index = index
        rows, spawn_col, spawn_row = load_map(LEVEL_FILES[index])
        self.world = World(rows)

        spawn_x = spawn_col * TILE_SIZE + TILE_SIZE / 2
        spawn_y = spawn_row * TILE_SIZE + TILE_SIZE / 2
        self.player = Player(spawn_x, spawn_y)

        self.camera = Camera(self.world.cols * TILE_SIZE, self.world.rows * TILE_SIZE)
        self.camera.snap(self.player.x, self.player.y)

        # the minimap is built once per level
        self.minimap = Minimap(self.world)

        # every enemy character in the map file becomes an enemy of that type
        # we also remember where each one started, the spawner uses these later
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

        # coins and hearts lying on the ground, cleared when the level restarts
        self.ground_coins = []
        self.ground_hearts = []

    def run(self):
        # main loop, runs every frame until you quit
        while self.running:
            # dt is how many seconds passed since last frame
            # using it makes movement the same speed on fast and slow pcs
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
                    # first ESC closes the sign box, second ESC quits
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.running = False

                elif event.key == pygame.K_F3:
                    self.debug.toggle()

                elif event.key == pygame.K_m:
                    self.minimap_visible = not self.minimap_visible

                elif event.key == pygame.K_e:
                    if self.dialog.is_open():
                        self.dialog.close()
                    else:
                        self.try_read_sign()

                elif event.key == pygame.K_SPACE:
                    # you cant swing while the sign box is open
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

    def player_attack(self):
        # ask the player for a swing, the player says no if the cooldown isnt done
        hitbox = self.player.try_attack()
        if hitbox is None:
            return

        # check every living enemy, if the swing touches it then it gets hurt
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            if hitbox.colliderect(enemy.get_rect()):
                enemy.take_damage(ATTACK_DAMAGE)
                enemy.knockback(self.player.x, self.player.y)
                if not enemy.is_alive():
                    self.on_enemy_died(enemy)

    def on_enemy_died(self, enemy):
        self.kills += 1

        # every enemy drops coins
        value = COIN_VALUES.get(enemy.kind, 1)
        self.ground_coins.append(Coin(enemy.x, enemy.y, value))

        # some enemies also drop a heart, the chance depends on the enemy type
        chance = HEART_DROP_CHANCE.get(enemy.kind, 0.0)
        if random.random() < chance:
            self.ground_hearts.append(Heart(enemy.x, enemy.y))

    def update(self, dt):
        # while the sign box is open everything in the world stops
        if not self.dialog.is_open():
            keys = pygame.key.get_pressed()
            self.player.update(dt, keys, self.world)

            # check if the player is standing on a door
            tile_col = int(self.player.x // TILE_SIZE)
            tile_row = int(self.player.y // TILE_SIZE)
            if self.world.get_char_at(tile_col, tile_row) == "D":
                next_index = (self.level_index + 1) % len(LEVEL_FILES)
                self.load_level(next_index)
                return

            # enemies move, and touching one hurts the player by that enemy's damage
            for enemy in self.enemies:
                enemy.update(dt, self.player, self.world.walls)
                if enemy.is_alive() and enemy.get_rect().colliderect(self.player.get_rect()):
                    self.player.take_damage(enemy.damage)

            # dead enemies get removed from the list
            self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]

            # the spawner can bring one enemy back every so often
            new_enemy = self.spawner.update(dt, self.enemies, self.player)
            if new_enemy is not None:
                self.enemies.append(new_enemy)

            self.update_pickups(dt)

            # you died, so the level starts over from the spawn point
            if not self.player.is_alive():
                self.load_level(self.level_index)
                return

        self.camera.follow(self.player.x, self.player.y, dt)

    def update_pickups(self, dt):
        player_rect = self.player.get_rect()

        # coins: walking over one adds its value to your total
        for coin in self.ground_coins:
            coin.update(dt)
            if coin.get_rect().colliderect(player_rect):
                self.coins += coin.value
                coin.value = 0
        self.ground_coins = [coin for coin in self.ground_coins if coin.value > 0]

        # hearts: walking over one heals you, but never above your max health
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

        self.player.draw(self.screen, self.camera)

        # the hint stays in the same spot on screen, it doesnt move with the camera
        hint = self.font.render(
            "WASD move, SPACE swing, E sign, M minimap, F3 debug, ESC quit", True, TEXT_COLOR
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

        if self.debug.visible:
            self.debug.draw_grid(self.screen, self.camera)
            self.debug.draw_info(self.screen, self.clock, self.player, self.world, self.camera)

        self.dialog.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run() 