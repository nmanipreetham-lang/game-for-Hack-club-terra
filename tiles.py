# every kind of title in the game lives here
# to add a new tile, add onemore to TILE_TYPES and put its character in the map file 
#
# solid = True means you cant walk thorough it 
#speed = how fast you move on it (1.0is normal,0.5 is half speed )

TILE_TYPES = {
    "#": {
        "name": "wall",
        "color": (92, 86, 80),
        "edge": (62, 57, 53 ),
        "edge_width":2,
        "solid": True,
        "speed": 1.0,
        

    },
       "~": {
           "name": "water",
           "color": (40, 88, 140),
           "edge": (30, 66, 108),
           "edge_width": 2,
           "solid" : True,
           "speed": 1.0,
       },       
       ".": {
           "name": "floor",
           "color": (52,62, 46),
           "edge":(44, 53, 39),
           "edge_width": 1,
           "solid": False,
           "speed": 1.0,
       },
       "S" {
           #spawn point,looks and acts like normal floor 
           "name": "floor",
           "color":(52, 62, 46),
           "edge": (44, 53, 39),
           "edge_wide": 1,
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
             "edge"_width": 1,
             "solid": False,
             "speed": 0.5,   # sand is slow     
         },
}
DEFAULT_TILE = TILE_TYPES["."]


def get_tile(char):
    return TILE_TYPES.get(char,DEFAULT_TILE)
