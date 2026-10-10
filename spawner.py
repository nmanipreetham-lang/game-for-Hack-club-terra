import math
import random
from enemy import Enemy

# the spawner keeps the level from running out of enemies
# every RESPAWN_TIME seconds it tries to bring one back at one of the spawn points

RESPAWN_TIME = 20.0    # seconds between respawn attempts
MAX_ENEMIES = 6        # never have more than this many enemies alive at once
SAFE_DISTANCE = 300    # enemies never appear this close to the player (pixels)
CROWD_DISTANCE = 40    # if an enemy is this close to the spawn point, wait


class EnemySpawner:
    def __init__(self, spawn_points):
        # spawn_points is a list of (kind, x, y), one per enemy in the map file
        self.spawn_points = spawn_points
        self.timer = RESPAWN_TIME

    def update(self, dt, enemies, player):
        # returns a new Enemy when it is time to spawn one, otherwise None
        self.timer -= dt
        if self.timer > 0:
            return None

        # the timer restarts every time, even if we dont spawn anything
        self.timer = RESPAWN_TIME

        if len(enemies) >= MAX_ENEMIES:
            return None

        # only use spawn points that are far enough away from the player
        options = []
        for kind, x, y in self.spawn_points:
            if math.hypot(x - player.x, y - player.y) > SAFE_DISTANCE:
                options.append((kind, x, y))

        if not options:
            return None

        kind, x, y = random.choice(options)

        # dont put a new enemy on top of one that is already standing there
        for enemy in enemies:
            if math.hypot(enemy.x - x, enemy.y - y) < CROWD_DISTANCE:
                return None

        return Enemy(x, y, kind)