import unittest

import pygame

from enemy import Enemy
from main import CRIT_SHOW_TIME, Game, combo_hit_stats
from player import ATTACK_DAMAGE
from projectile import (
    REFLECT_COLOR,
    REFLECT_LIFETIME,
    REFLECT_SPEED_MULT,
    Projectile,
)


class DamageLog:
    def __init__(self):
        self.amounts = []

    def add(self, x, y, amount):
        self.amounts.append(amount)


class TestPlayer:
    x = 100
    y = 100

    def __init__(self, hitbox):
        self.hitbox = hitbox

    def try_attack(self):
        return self.hitbox


class TestEnemy:
    x = 110
    y = 110
    size = 20

    def __init__(self):
        self.health = 1000
        self.damages = []

    def is_alive(self):
        return self.health > 0

    def get_rect(self):
        return pygame.Rect(100, 100, 24, 24)

    def take_damage(self, amount):
        self.damages.append(amount)
        self.health -= amount

    def knockback(self, from_x, from_y):
        pass


class CombatTests(unittest.TestCase):
    def make_game(self, hitbox):
        game = object.__new__(Game)
        game.player = TestPlayer(hitbox)
        game.enemy_shots = []
        game.enemies = [TestEnemy()]
        game.damage_texts = DamageLog()
        game.combo = 0
        game.combo_timer = 0.0
        game.crit_timer = 0.0
        game.on_enemy_died = lambda enemy: None
        return game

    def test_combo_damage_and_fifth_hit_crit(self):
        base = ATTACK_DAMAGE
        expected = [base, base + 1, base + 2, base + 3, (base + 3) * 2]
        self.assertEqual([combo_hit_stats(i)[0] for i in range(5)], expected)
        self.assertFalse(combo_hit_stats(3)[1])
        self.assertTrue(combo_hit_stats(4)[1])

        game = self.make_game(pygame.Rect(100, 100, 40, 40))
        for _ in range(5):
            game.player_attack()

        self.assertEqual(game.damage_texts.amounts, expected)
        self.assertEqual(game.combo, 5)
        self.assertEqual(game.crit_timer, CRIT_SHOW_TIME)

    def test_missed_swing_resets_combo(self):
        game = self.make_game(pygame.Rect(0, 0, 20, 20))
        game.combo = 4
        game.combo_timer = 1.0

        game.player_attack()

        self.assertEqual(game.combo, 0)
        self.assertEqual(game.combo_timer, 0.0)

    def test_reflected_shot_reverses_and_speeds_up(self):
        shot = Projectile(100, 100, 0, 100, speed=240, lifetime=2.5)
        old_vx = shot.vx
        old_vy = shot.vy

        shot.reflect()

        self.assertTrue(shot.reflected)
        self.assertAlmostEqual(shot.vx, -old_vx * REFLECT_SPEED_MULT)
        self.assertAlmostEqual(shot.vy, -old_vy * REFLECT_SPEED_MULT)
        self.assertEqual(shot.lifetime, REFLECT_LIFETIME)
        self.assertEqual(shot.color, REFLECT_COLOR)

    def test_spitter_stays_still_and_only_shoots_with_clear_sight(self):
        spitter = Enemy(0, 0, "spitter")
        player = type("Point", (), {"x": 100, "y": 0})()
        wall = pygame.Rect(48, -4, 8, 8)

        spitter.update(0.1, player, [])
        self.assertFalse(spitter.chasing)
        self.assertEqual(spitter.x, 0)
        self.assertFalse(spitter.try_shoot(player, [wall]))
        self.assertTrue(spitter.try_shoot(player, []))
        self.assertFalse(spitter.try_shoot(player, []))


if __name__ == "__main__":
    unittest.main()
