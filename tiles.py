# every kind of tile in the game lives here
# to add a new tile, add one more line to TILE_TYPES and put its character in the map file
#
# solid = True means you cant walk through it
# speed = how fast you move on it (1.0 is normal, 0.5 is half speed)

TILE_TYPES = {
    "#": {
        "name": "wall",
        "color": (92, 86, 80),
        "edge": (62, 57, 53),
        "edge_width": 2,
        "solid": True,
        "speed": 1.0,
    },
    "~": {
        "name": "water",
        "color": (40, 88, 140),
        "edge": (30, 66, 108),
        "edge_width": 2,
        "solid": True,
        "speed": 1.0,
    },
    ".": {
        "name": "floor",
        "color": (52, 62, 46),
        "edge": (44, 53, 39),
        "edge_width": 1,
        "solid": False,
        "speed": 1.0,
    },
    "S": {
        # spawn point, looks and acts like normal floor
        "name": "spawn",
        "color": (52, 62, 46),
        "edge": (44, 53, 39),
        "edge_width": 1,
        "solid": False,
        "speed": 1.0,
    },
    "g": {
        "name": "grass",
        "color": (58, 110, 60),
        "edge": (46, 90, 48),
        "edge_width": 1,
        "solid": False,
        "speed": 0.7,  # grass slows you down a bit
    },
    "s": {
        "name": "sand",
        "color": (150, 130, 80),
        "edge": (125, 108, 66),
        "edge_width": 1,
        "solid": False,
        "speed": 0.5,  # sand is slow
    },
    "D": {
        # walking onto a door takes you to the next level
        "name": "door",
        "color": (120, 80, 40),
        "edge": (80, 52, 24),
        "edge_width": 3,
        "solid": False,
        "speed": 1.0,
    },
    "I": {
        # a sign you can read by standing next to it and pressing E
        "name": "sign",
        "color": (110, 84, 52),
        "edge": (70, 52, 30),
        "edge_width": 2,
        "solid": True,
        "speed": 1.0,
    },
}

# if a map has a character we dont know, it becomes floor
DEFAULT_TILE = TILE_TYPES["."]


def get_tile(char):
    return TILE_TYPES.get(char, DEFAULT_TILE)   