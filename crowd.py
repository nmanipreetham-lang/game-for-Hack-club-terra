import math

# enemies used to stack on top of each other and look like one big blob
# this file pushes them apart a little every frame
#
# how it works:
#   1. sort every living enemy into little grid cells so we only compare
#      enemies that are actually near each other (way faster with lots of enemies)
#   2. for every close pair, push them apart. heavier enemies (brutes) get
#      pushed less than light ones (runners)
#   3. do a few passes per frame so the spreading finishes quickly
#   4. walls always win, nobody gets pushed through one

# ----- tuning numbers -----
SEPARATE_GAP = 4          # extra space we want between two enemies, in pixels
SEPARATE_RATE = 0.5       # how much of the overlap gets fixed in one pass
SEPARATE_PASSES = 2       # how many times we run the push per frame
MAX_PUSH = 8.0            # the most one enemy can get shoved in one pass, keeps things smooth
GRID_CELL = 64            # size of the grid cells in pixels, bigger = fewer cells to check
CROWD_RADIUS = 60         # how close counts as "in a crowd" for the debug count
CROWD_MIN_NEIGHBORS = 2   # how many friends nearby before an enemy counts as crowded

# how heavy each enemy type feels when pushed
# a brute barely moves, a runner gets bumped around a lot
MASS = {
    "normal": 1.0,
    "runner": 0.7,
    "brute": 2.5,
}
DEFAULT_MASS = 1.0


def get_mass(enemy):
    # look up how heavy this enemy is, default if we dont know the type
    return MASS.get(enemy.kind, DEFAULT_MASS)


def build_grid(enemies):
    # put each enemy into the cell it sits in
    # the key is a (col, row) pair and the value is a list of enemies in that cell
    grid = {}
    for enemy in enemies:
        key = (int(enemy.x // GRID_CELL), int(enemy.y // GRID_CELL))
        if key not in grid:
            grid[key] = []
        grid[key].append(enemy)
    return grid


def neighbor_pairs(enemies):
    # yields every pair of enemies that could possibly be touching
    # only looks at its own cell and the 8 cells around it
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
                        # make sure each pair only shows up once
                        pair_id = (min(id(a), id(b)), max(id(a), id(b)))
                        if pair_id in seen:
                            continue
                        seen.add(pair_id)
                        yield a, b


def nudge(enemy, move_x, move_y, walls):
    # move an enemy a little, axis by axis, so walls still stop it
    if move_x != 0:
        enemy.x += move_x
        enemy.hit_wall_x(walls, move_x)
    if move_y != 0:
        enemy.y += move_y
        enemy.hit_wall_y(walls, move_y)


def push_pair(a, b, walls):
    # push two overlapping enemies apart
    # returns True if they were actually overlapping
    dx = b.x - a.x
    dy = b.y - a.y
    distance = math.hypot(dx, dy)

    min_distance = (a.size + b.size) / 2 + SEPARATE_GAP
    if distance >= min_distance:
        return False

    # two enemies on the exact same spot, pick a direction so we dont divide by zero
    if distance == 0:
        dx, dy, distance = 1.0, 0.0, 1.0

    overlap = (min_distance - distance) * SEPARATE_RATE
    nx = dx / distance
    ny = dy / distance

    # the lighter enemy takes more of the push
    mass_a = get_mass(a)
    mass_b = get_mass(b)
    total = mass_a + mass_b
    share_a = mass_b / total    # a moves away from b by this share
    share_b = mass_a / total    # b moves away from a by this share

    push_a = min(MAX_PUSH, overlap * share_a)
    push_b = min(MAX_PUSH, overlap * share_b)

    nudge(a, -nx * push_a, -ny * push_a, walls)
    nudge(b, nx * push_b, ny * push_b, walls)
    return True


def separate_enemies(enemies, walls):
    # main entry point, main.py calls this once per frame
    # only living enemies take part
    alive = [enemy for enemy in enemies if enemy.is_alive()]
    if len(alive) < 2:
        return

    for _ in range(SEPARATE_PASSES):
        for a, b in neighbor_pairs(alive):
            push_pair(a, b, walls)


def count_crowded(enemies):
    # how many enemies have at least CROWD_MIN_NEIGHBORS friends close by
    # handy for the debug overlay if you want to see how packed things get
    alive = [enemy for enemy in enemies if enemy.is_alive()]
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