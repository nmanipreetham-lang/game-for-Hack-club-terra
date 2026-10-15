import math
from enemy import ENEMY_LOST_TIME

SEPARATE_GAP = 4
SEPARATE_RATE = 0.5
SEPARATE_PASSES = 2
MAX_PUSH = 8.0
GRID_CELL = 64
CROWD_RADIUS = 60
CROWD_MIN_NEIGHBORS = 2

MASS = {
    "normal": 1.0,
    "runner": 0.7,
    "brute": 2.5,
}
DEFAULT_MASS = 1.0

ALERT_RADIUS = 200

SHOCK_PUSH = 120
SHOCK_FALLOFF = 0.6

MAX_REPORT_LINES = 6


def get_mass(enemy):
    return MASS.get(enemy.kind, DEFAULT_MASS)


def living(enemies):
    return [enemy for enemy in enemies if enemy.is_alive()]


def build_grid(enemies):
    grid = {}
    for enemy in enemies:
        key = (int(enemy.x // GRID_CELL), int(enemy.y // GRID_CELL))
        if key not in grid:
            grid[key] = []
        grid[key].append(enemy)
    return grid


def neighbor_pairs(enemies):
    grid = build_grid(enemies)
    seen = set()

    for (col, row), cell_enemies in grid.items():
        for d_col in (-1, 0, 1):
            for d_row in (-1, 0, 1):
                other_cell = grid.get((col + d_col, row + d_row))
                if other_cell is None:
                    continue

                for a in cell_enemies:
                    for b in other_cell:
                        if a is b:
                            continue
                        pair_id = (min(id(a), id(b)), max(id(a), id(b)))
                        if pair_id in seen:
                            continue
                        seen.add(pair_id)
                        yield a, b


def nudge(enemy, move_x, move_y, walls):
    if move_x != 0:
        enemy.x += move_x
        enemy.hit_wall_x(walls, move_x)
    if move_y != 0:
        enemy.y += move_y
        enemy.hit_wall_y(walls, move_y)


def push_pair(a, b, walls):
    dx = b.x - a.x
    dy = b.y - a.y
    distance = math.hypot(dx, dy)

    min_distance = (a.size + b.size) / 2 + SEPARATE_GAP
    if distance >= min_distance:
        return False

    if distance == 0:
        dx, dy, distance = 1.0, 0.0, 1.0

    overlap = (min_distance - distance) * SEPARATE_RATE
    nx = dx / distance
    ny = dy / distance

    mass_a = get_mass(a)
    mass_b = get_mass(b)
    total = mass_a + mass_b
    share_a = mass_b / total
    share_b = mass_a / total

    push_a = min(MAX_PUSH, overlap * share_a)
    push_b = min(MAX_PUSH, overlap * share_b)

    nudge(a, -nx * push_a, -ny * push_a, walls)
    nudge(b, nx * push_b, ny * push_b, walls)
    return True


def separate_enemies(enemies, walls):
    alive = living(enemies)
    if len(alive) < 2:
        return

    for _ in range(SEPARATE_PASSES):
        for a, b in neighbor_pairs(alive):
            push_pair(a, b, walls)


def count_crowded(enemies):
    alive = living(enemies)
    neighbor_count = {id(enemy): 0 for enemy in alive}

    for a, b in neighbor_pairs(alive):
        distance = math.hypot(b.x - a.x, b.y - a.y)
        if distance <= CROWD_RADIUS:
            neighbor_count[id(a)] += 1
            neighbor_count[id(b)] += 1

    crowded = 0
    for enemy in alive:
        if neighbor_count[id(enemy)] >= CROWD_MIN_NEIGHBORS:
            crowded += 1
    return crowded


def alert_nearby_enemies(enemies, player, walls):
    alive = living(enemies)

    spotters = [enemy for enemy in alive if enemy.can_see(player, walls)]

    for spotter in spotters:
        for other in alive:
            if other is spotter:
                continue

            if other.lunge_state != "none" or other.fleeing:
                continue

            if other.can_see(player, walls):
                continue

            distance = math.hypot(other.x - spotter.x, other.y - spotter.y)
            if distance > ALERT_RADIUS:
                continue

            other.last_seen_x = player.x
            other.last_seen_y = player.y
            other.lost_timer = ENEMY_LOST_TIME


def group_center(enemies):
    alive = living(enemies)
    if not alive:
        return None

    total_x = sum(enemy.x for enemy in alive)
    total_y = sum(enemy.y for enemy in alive)
    count = len(alive)
    return total_x / count, total_y / count


def closest_enemy(enemies, x, y):
    alive = living(enemies)
    best = None
    best_distance = None

    for enemy in alive:
        distance = math.hypot(enemy.x - x, enemy.y - y)
        if best is None or distance < best_distance:
            best = enemy
            best_distance = distance

    return best


def enemies_in_radius(enemies, x, y, radius):
    found = []
    for enemy in living(enemies):
        if math.hypot(enemy.x - x, enemy.y - y) <= radius:
            found.append(enemy)
    return found


def shock_push(enemies, x, y, radius, walls):
    hit = []
    for enemy in enemies_in_radius(enemies, x, y, radius):
        dx = enemy.x - x
        dy = enemy.y - y
        distance = math.hypot(dx, dy)

        if distance == 0:
            dx, dy, distance = 1.0, 0.0, 1.0

        closeness = 1 - (distance / radius) * SHOCK_FALLOFF
        push = SHOCK_PUSH * closeness

        move_x = dx / distance * push * 0.1
        move_y = dy / distance * push * 0.1
        nudge(enemy, move_x, move_y, walls)
        hit.append(enemy)

    return hit


def crowd_report(enemies):
    alive = living(enemies)
    counts = {}
    for enemy in alive:
        counts[enemy.kind] = counts.get(enemy.kind, 0) + 1

    lines = []
    for kind in sorted(counts):
        lines.append(f"{kind}: {counts[kind]}")
    lines.append(f"crowded: {count_crowded(alive)}")

    center = group_center(alive)
    if center is not None:
        lines.append(f"center: {int(center[0])}, {int(center[1])}")

    return lines[:MAX_REPORT_LINES] 