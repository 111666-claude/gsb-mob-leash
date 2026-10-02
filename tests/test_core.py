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




class LeashEdgeTest(unittest.TestCase):
    def test_exact_radius_still_chases(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 100, 0, 0), "chase")

    def test_diagonal_exact_radius_still_chases(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 60, 80, 0), "chase")

    def test_beyond_radius_leashes(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 100.000001, 0, 0), "leashing")

    def test_inside_home_band_is_chase_not_idle(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 1.5, 0, 0), "chase")


class ReturnTimerTest(unittest.TestCase):
    def _leashed_mob(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 200, 0, 0), "leashing")
        return mobs

    def test_home_enters_returned(self):
        mobs = self._leashed_mob()
        self.assertEqual(mobs.move("m1", 0, 0, 100), "returned")

    def test_still_returned_before_reset_ms(self):
        mobs = self._leashed_mob()
        mobs.move("m1", 0, 0, 100)
        self.assertEqual(mobs.move("m1", 0, 0, 1099), "returned")

    def test_idle_exactly_at_reset_ms(self):
        mobs = self._leashed_mob()
        mobs.move("m1", 0, 0, 100)
        self.assertEqual(mobs.move("m1", 0, 0, 1100), "idle")

    def test_leaving_home_restarts_timer(self):
        mobs = self._leashed_mob()
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 50, 0, 600)
        mobs.move("m1", 0, 0, 700)
        self.assertEqual(mobs.move("m1", 0, 0, 1699), "returned")
        self.assertEqual(mobs.move("m1", 0, 0, 1700), "idle")

    def test_distance_one_still_counts_as_home(self):
        mobs = self._leashed_mob()
        self.assertEqual(mobs.move("m1", 1, 0, 100), "returned")

    def test_idle_never_left_stays_idle_near_home(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 0.5, 0, 0), "idle")


class ResetTest(unittest.TestCase):
    def test_hp_refills_when_idle(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.damage("m1", 60)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        self.assertEqual(mobs.hp("m1"), 100)

    def test_hp_not_refilled_during_returned(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.damage("m1", 60)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        self.assertEqual(mobs.hp("m1"), 40)

    def test_threat_cleared_on_leashing(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 50)
        self.assertEqual(mobs.threat("m1"), 50)
        mobs.move("m1", 200, 0, 0)
        self.assertEqual(mobs.threat("m1"), 0)

    def test_threat_stays_zero_during_leash_states(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.add_threat("m1", 50)
        self.assertEqual(mobs.threat("m1"), 0)
        mobs.move("m1", 0, 0, 100)
        mobs.add_threat("m1", 50)
        self.assertEqual(mobs.threat("m1"), 0)

    def test_threat_cleared_when_idle(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 50)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        self.assertEqual(mobs.threat("m1"), 0)

    def test_threat_accumulates_again_after_reset(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 50)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        mobs.move("m1", 50, 0, 1200)
        mobs.add_threat("m1", 7)
        self.assertEqual(mobs.threat("m1"), 7)


class AttackGateTest(unittest.TestCase):
    def test_leashing_cannot_attack(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        self.assertFalse(mobs.can_attack("m1"))

    def test_returned_cannot_attack(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        self.assertFalse(mobs.can_attack("m1"))

    def test_chase_can_attack(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 50, 0, 0)
        self.assertTrue(mobs.can_attack("m1"))

    def test_idle_can_attack_after_reset(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        self.assertTrue(mobs.can_attack("m1"))


class ScanCostTest(unittest.TestCase):
    def test_scanned_within_budget_for_3000_mobs(self):
        mobs = Mobs(100, 1000)
        for index in range(3000):
            mobs.spawn("m-%d" % index, index, 0)
        for index in range(3000):
            mobs.move("m-%d" % index, index, 0, index)
        self.assertLessEqual(mobs.scanned_count(), 6000)

    def test_scanned_independent_of_population(self):
        def run(population):
            mobs = Mobs(100, 1000)
            for index in range(population):
                mobs.spawn("m-%d" % index, index, 0)
            before = mobs.scanned_count()
            mobs.move("m-0", 0, 0, 0)
            return mobs.scanned_count() - before
        self.assertEqual(run(10), run(10000))


class DeterminismTest(unittest.TestCase):
    def test_same_sequence_same_result(self):
        script = [(0, 0, 0), (200, 0, 10), (0, 0, 20),
                  (50, 0, 500), (0, 0, 600), (0, 0, 1600)]

        def run():
            mobs = Mobs(100, 1000)
            mobs.spawn("m1", 0, 0)
            mobs.damage("m1", 30)
            mobs.add_threat("m1", 10)
            states = [mobs.move("m1", x, y, now) for x, y, now in script]
            return states, mobs.hp("m1"), mobs.threat("m1")

        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
