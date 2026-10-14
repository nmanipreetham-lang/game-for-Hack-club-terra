import math 
import random
import pygame 

# every enemy type in one place 
# to make a new enemy, copy one of these and change the numbers 
# the map characher for each type is set in main.py 
ENEMY_TYPES = {
    "normal": {
        "color": (200, 70, 70),   # red 
        "size": 24,
        "max_health" : 3,
        "damage": 10,             # health the player loses when touching it 
        "wander_speed": 60,       # pixels per second when walking around 
        "chase_speed": 110,       # pixels per second when second when chasing you 
        "sight": 200,             # how clase you have to be before it chases 
    },
    "runner": { 
        "color": (230, 170, 60),  # orange 
        "size": 18, 
        "max_health": 2,
        "damage": 8,
        "wander_speed": 90,
        "chase_speed": 190,       # really fast so you cant just walk away 
        "sight": 260,  
        "flees": True,            # runs away once it gets hurt badly 
    },
    "brute": { 
        "color": (130, 60, 160),  # purple 
        "size": 34, 
        "max_health": 6,          # takes a lot of swings 
        "damage": 20,             # but it hits really hard 
        "wander_speed": 35,
        "chase_speed": 60,        # slow, you can outrun it 
        "sight": 180,
    },
}

ENEMY_HURT_COLOR = (255, 225, 255) # the enemy flashes this color when hit
ENEMY_BAR_BACK = (60, 20, 20)
ENEMY_BAR_FILL = (120, 230, 120)

ENEMY_HURT_TIME = 0.2     # how long the white flash lasts 
ENEMY_KNOCK_SPEED = 180   # how fast the enemy gets pushed back when hit 
ENEMY_KNOCK_TIME = 0.2    # how long he push lasts 

# line of sight check. we walk along the line between the enemy and the
# player and check for walls every few pixels. smaller number = more accurate
# but a bit slower 
SIGHT_STEP = 8 

# when an enemy loses you it dosent just forget you right away 
# it goes to the last spot it saw you and looks around for a bit 
ENEMY_LOST_TIME = 2.0        # how long it keeps seaarching 
ENEMY_SEARCH_REACH = 6       # close enough to the spot, stop searching 
ENEMY_SEARCH_SPEED = 0.7     # searching is slower than a full chase 

# leash. wandering enemies dont drift across the whole map, 
# they stay within this many pixels of where they spawned 
ENEMY_LEASH = 160 

# lung attack. when a chasing enemy gets closer,it stops, flashes yellow 
# to warn you, than dashes at you. the warning is the important part 
LUNGE_RANGE = 50                    # how close it has to be before it winds up 
LUNGE_WINDUP = 0.4                  # how long it stands still and flashes 
LUNGE_TIME = 0.2                    # how long the dash lasts 
LUNGE_SPEED = 260                   # how fast the dash is 
LUNGE_COOLDOWN = 1.5                # how long it has to wait before the next lunge 
LUNGE_WARN_COLOR = (255, 220, 60)   # yellow flash during the wind up 

# fleeing. some enemies (see "flees" above) run away when they are low on health 
# they only do this once per life, so they dont just run forever 
FLEE_HEALTH_RATIO = 0.5    # runs when health is at or below this share of max 
FLEE_TIME = 2.5            # how long the run last 
FLEE_SPEED_MULT = 1.2      # fleeing is a bit faster is a bit faster than a normal chase 


def has_line_of_sight(x1, y1, x2, y2, walls): 
    # returns True if no wall is setting between the twp points 
    distance = math.hypot(x2 - x1, y2 - y1)
    steps = max(1, int(distance / SIGHT_STEP))
    for i in range(1, steps):
        t = i / steps 
        px = x1 + (x2 - x1)  * t 
        py = y1 + (y2 - y1)  * t 
        for wall in walls:
            if wall.collidepoint(px, py):
                return True 


class Enemy: 
    def __init__(self, x, y,kind="normal"):
        # x and y are the CENTER of the enemy, in the world space
        stats = ENEMY_TYPES[kind]

        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.color = stats["color"]
        self.size = stats["size"]
        self.max_health = stats["max_health"]
        self.health = stats["max_health"]
        self.damage = stats["damage"]
        self.wander_speed = stats["wander_speed"]
        self.chase_speed = stats["chase_speed"]
        self.sight = stats["sight"]

        self.direction = (0, 0)
        self.change_timer = 0.0
        self.chasing = False

        # searching stuff, where the player was last seen
        self.last_seen_x = 0.0
        self.last_seen_y = 0.0
        self.lost_timer = 0.0

        # the spot this enemy spawned at, used for the leash
        self.home_x = self.x
        self.home_y = self.y

        # lunge state: "none", "windup" or "lunge"
        self.lunge_state = "none"
        self.lunge_timer = 0.0
        self.lunge_cooldown = 0.0
        self.lunge_dx = 0.0
        self.lunge_dy = 0.0

        # fleeing state
        self.flees = stats.get("flees", False)
        self.fleeing = False
        self.flee_timer = 0.0
        self.has_fled = False

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

    def can_see(self, player, walls):
        # close enough AND nothing blocking the view
        distance = math.hypot(player.x - self.x, player.y - self.y)
        if distance >= self.sight:
            return False
        return has_line_of_sight(self.x, self.y, player.x, player.y, walls)

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

        # low on health and this type runs away? start fleeing, but only once
        if (self.flees and not self.has_fled and not self.fleeing
                and self.health / self.max_health <= FLEE_HEALTH_RATIO):
            self.fleeing = True
            self.has_fled = True
            self.flee_timer = FLEE_TIME
            self.lunge_state = "none"

        if self.fleeing:
            self.update_flee(dt, player, walls)
            return

        if self.lunge_cooldown > 0:
            self.lunge_cooldown -= dt

        # in the middle of a lunge, keep dashing in the same direction
        if self.lunge_state == "lunge":
            self.lunge_timer -= dt
            self.x += self.lunge_dx * LUNGE_SPEED * dt
            self.hit_wall_x(walls, self.lunge_dx)
            self.y += self.lunge_dy * LUNGE_SPEED * dt
            self.hit_wall_y(walls, self.lunge_dy)
            if self.lunge_timer <= 0:
                self.lunge_state = "none"
                self.lunge_cooldown = LUNGE_COOLDOWN
            return

        # winding up, stand still and flash so the player can react
        if self.lunge_state == "windup":
            self.lunge_timer -= dt
            if self.lunge_timer <= 0:
                # lock in the direction at the moment the dash starts
                to_x = player.x - self.x
                to_y = player.y - self.y
                length = math.hypot(to_x, to_y)
                if length == 0:
                    length = 1
                self.lunge_dx = to_x / length
                self.lunge_dy = to_y / length
                self.lunge_state = "lunge"
                self.lunge_timer = LUNGE_TIME
            return

        to_x = player.x - self.x
        to_y = player.y - self.y
        distance = math.hypot(to_x, to_y)

        # close enough and ready, so start the warning
        if (distance > 0 and distance < LUNGE_RANGE and self.lunge_cooldown <= 0
                and self.can_see(player, walls)):
            self.lunge_state = "windup"
            self.lunge_timer = LUNGE_WINDUP
            self.chasing = True
            return

        if distance > 0 and self.can_see(player, walls):
            # the player is close and not behind a wall, so walk straight at them
            # and remember where they were
            self.chasing = True
            self.last_seen_x = player.x
            self.last_seen_y = player.y
            self.lost_timer = ENEMY_LOST_TIME
            dx = to_x / distance
            dy = to_y / distance
            speed = self.chase_speed

        elif self.lost_timer > 0:
            # lost sight of the player, so go check the last spot they were at
            self.chasing = False
            self.lost_timer -= dt

            s_x = self.last_seen_x - self.x
            s_y = self.last_seen_y - self.y
            s_dist = math.hypot(s_x, s_y)
            if s_dist < ENEMY_SEARCH_REACH:
                # got to the spot and nobody is there, so give up
                self.lost_timer = 0
                self.pick_direction()
                return

            dx = s_x / s_dist
            dy = s_y / s_dist
            speed = self.chase_speed * ENEMY_SEARCH_SPEED

        else:
            # nobody nearby, so wander around. but if we drifted too far from
            # home, walk back home instead
            self.chasing = False
            home_x = self.home_x - self.x
            home_y = self.home_y - self.y
            home_dist = math.hypot(home_x, home_y)

            if home_dist > ENEMY_LEASH:
                dx = home_x / home_dist
                dy = home_y / home_dist
                speed = self.wander_speed
            else:
                self.change_timer -= dt
                if self.change_timer <= 0:
                    self.pick_direction()
                dx, dy = self.direction
                speed = self.wander_speed

        # same axis by axis movement as the player so walls work the same way
        self.x += dx * speed * dt
        blocked = self.hit_wall_x(walls, dx)

        self.y += dy * speed * dt
        blocked = self.hit_wall_y(walls, dy) or blocked

        if blocked and not self.chasing:
            # ran into a wall while searching or wandering
            # searching stops here, otherwise it would just get stuck
            if self.lost_timer > 0:
                self.lost_timer = 0
            self.pick_direction()

    def update_flee(self, dt, player, walls):
        # run straight away from the player for a little while
        self.chasing = False
        self.flee_timer -= dt
        if self.flee_timer <= 0:
            self.fleeing = False
            self.pick_direction()
            return

        to_x = player.x - self.x
        to_y = player.y - self.y
        distance = math.hypot(to_x, to_y)
        if distance == 0:
            # standing right on top of the player, pick any way out
            dx, dy = 1.0, 0.0
        else:
            dx = -to_x / distance
            dy = -to_y / distance

        speed = self.chase_speed * FLEE_SPEED_MULT
        self.x += dx * speed * dt
        blocked_x = self.hit_wall_x(walls, dx)
        self.y += dy * speed * dt
        blocked_y = self.hit_wall_y(walls, dy)

        # ran into a wall while running, so give up the run early
        if blocked_x or blocked_y:
            self.fleeing = False
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

        # yellow while winding up a lunge, white when hit, normal color otherwise
        color = self.color
        if self.lunge_state == "windup":
            color = LUNGE_WARN_COLOR
        if self.hurt_timer > 0:
            color = ENEMY_HURT_COLOR

        screen_rect = camera.apply(self.get_rect())
        pygame.draw.rect(surface, color, screen_rect, border_radius=4)

        # only show the health bar once the enemy got hit
        if self.health < self.max_health:
            back = pygame.Rect(screen_rect.x, screen_rect.y - 8, screen_rect.width, 4)
            fill_width = int(screen_rect.width * self.health / self.max_health)
            fill = pygame.Rect(screen_rect.x, screen_rect.y - 8, fill_width, 4)
            pygame.draw.rect(surface, ENEMY_BAR_BACK, back)
            pygame.draw.rect(surface, ENEMY_BAR_FILL, fill)


            