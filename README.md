# Terra Quest

Terra Quest is a top-down exploration and survival game made with Python and Pygame for Hack Club Terra. It is a work in progress, built one coding session at a time.

## Run from source

You need Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
python main.py
```

Run the commands from the project folder. The game window is 960 × 640.

## Controls

| Key | Action |
| --- | --- |
| WASD or arrow keys | Move |
| SPACE | Swing your sword |
| R | Throw a rock toward the mouse pointer |
| SHIFT | Dodge roll in the direction you are facing |
| E | Read a nearby sign, or close its message |
| M | Show or hide the minimap |
| F3 | Show or hide the debug overlay |
| ESC | Close a message, or quit when no message is open |

## What is in the current build

- Two tile-map levels connected by doors. The second door loops back to the first level.
- Walls and water block movement; grass and sand slow the player down.
- Signs show short messages when you stand nearby and press E.
- A minimap and an optional F3 debug overlay.
- Three enemy types that wander, chase, search for the player, and can alert nearby enemies.
- Sword attacks, thrown rocks, dodge rolls, health, knockback, and floating damage numbers.
- Coins and hearts dropped by enemies, plus enemy respawns.

There is no save system, sound, or boss fight yet.

## Windows download

This is a desktop Pygame game, not a browser game. Download the Windows executable directly: [**TerraQuest.exe**](https://github.com/nmanipreetham-lang/game-for-Hack-club-terra/releases/download/v0.1.0/TerraQuest.exe).

If your browser says the download failed, open that direct download link in an Incognito or Private window and retry. The [release page](https://github.com/nmanipreetham-lang/game-for-Hack-club-terra/releases/tag/v0.1.0) has the controls and notes.

The `Windows release build` GitHub Actions workflow builds `TerraQuest.exe` when a version tag beginning with `v` is published. To build it yourself on Windows, run these commands from the project folder:

```powershell
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --noconsole --name TerraQuest --add-data "maps;maps" main.py
```

The executable will be in `dist\TerraQuest.exe`.

## Progress

- Sessions 1–5: project setup, movement, and the camera.
- Sessions 6–8: tile maps, collisions, signs, and the dialog box.
- Sessions 9–10: minimap and animated water.
- Sessions 11–18: health, enemies, attacks, pickups, respawns, and enemy sight/search.
- Sessions 19–27: crowd behavior, enemy tactics, damage numbers, rock projectiles, and dodge rolling.
