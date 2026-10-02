import unittest

from leash.core import Mobs


class BasicTest(unittest.TestCase):
    def test_spawn_has_full_hp(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.hp("m1"), 100)

    def test_unknown_mob_move(self):
        self.assertEqual(Mobs(100, 1000).move("ghost", 0, 0, 0), "unknown")

    def test_spawned_mob_can_attack(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertTrue(mobs.can_attack("m1"))

    def test_damage_reduces_hp(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.damage("m1", 30), 70)

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Mobs(100, 1000).scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
