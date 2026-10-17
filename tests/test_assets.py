import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame

from enemy import Enemy, has_line_of_sight
from main import ENEMY_SPAWN_CHARS, LEVEL_FILES, asset_path
from settings import TILE_SIZE
from world import World, load_map


class AssetPathTests(unittest.TestCase):
    def test_source_run_uses_the_project_folder(self):
        expected_root = Path(__file__).resolve().parents[1]
        self.assertEqual(asset_path(LEVEL_FILES[0]), expected_root / LEVEL_FILES[0])

    def test_pyinstaller_run_uses_the_extracted_bundle_folder(self):
        with tempfile.TemporaryDirectory() as bundle_dir:
            with patch.object(sys, "_MEIPASS", bundle_dir, create=True):
                self.assertEqual(
                    asset_path(LEVEL_FILES[0]),
                    Path(bundle_dir) / LEVEL_FILES[0],
                )

    def test_every_level_loads_and_has_valid_enemy_spawns(self):
        spawn_types = set()
        for level_file in LEVEL_FILES:
            with self.subTest(level_file=level_file):
                path = asset_path(level_file)
                self.assertTrue(path.is_file(), f"Missing map file: {path}")

                rows, spawn_col, spawn_row = load_map(path)
                self.assertTrue(rows)
                self.assertEqual(len({len(row) for row in rows}), 1)
                self.assertEqual(rows[spawn_row][spawn_col], "S")

                world = World(rows)
                self.assertGreater(world.rows, 0)
                self.assertGreater(world.cols, 0)
                self.assertIn("D", "".join(rows))

                level_spawns = 0
                for row_index, row in enumerate(rows):
                    for col_index, char in enumerate(row):
                        if char not in ENEMY_SPAWN_CHARS:
                            continue

                        level_spawns += 1
                        spawn_types.add(char)
                        kind = ENEMY_SPAWN_CHARS[char]
                        enemy = Enemy(
                            col_index * TILE_SIZE + TILE_SIZE / 2,
                            row_index * TILE_SIZE + TILE_SIZE / 2,
                            kind,
                        )
                        self.assertFalse(
                            any(enemy.get_rect().colliderect(wall) for wall in world.walls),
                            f"{kind} spawn overlaps a wall in {level_file}",
                        )

                self.assertGreater(level_spawns, 0)

        self.assertEqual(spawn_types, set(ENEMY_SPAWN_CHARS))

    def test_enemy_sight_is_clear_until_a_wall_blocks_it(self):
        self.assertTrue(has_line_of_sight(0, 0, 100, 0, []))
        wall = pygame.Rect(48, -4, 8, 8)
        self.assertFalse(has_line_of_sight(0, 0, 100, 0, [wall]))

        enemy = Enemy(0, 0, "normal")
        player = type("Point", (), {"x": 100, "y": 0})()
        self.assertTrue(enemy.can_see(player, []))
        self.assertFalse(enemy.can_see(player, [wall]))

    def test_enemy_chases_on_an_open_path(self):
        enemy = Enemy(0, 0, "normal")
        player = type("Point", (), {"x": 100, "y": 0})()
        enemy.update(0.1, player, [])
        self.assertTrue(enemy.chasing)
        self.assertGreater(enemy.x, 0)

        blocked_enemy = Enemy(0, 0, "normal")
        wall = pygame.Rect(48, -4, 8, 8)
        blocked_enemy.update(0.1, player, [wall])
        self.assertFalse(blocked_enemy.chasing)


if __name__ == "__main__":
    unittest.main()
