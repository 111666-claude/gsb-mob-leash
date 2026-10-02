"""脱战边界、回归计时、重置回满与攻击禁用。"""
import unittest

from leash.core import Mobs


class LeashBoundaryTest(unittest.TestCase):
    def test_distance_equal_radius_stays_chase(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 100, 0, 0), "chase")
        self.assertEqual(mobs.state("m1"), "chase")

    def test_distance_equal_radius_diagonal_stays_chase(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 60, 80, 0), "chase")

    def test_distance_beyond_radius_leashes(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertEqual(mobs.move("m1", 101, 0, 0), "leashing")

    def test_leashing_clears_threat(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 50)
        mobs.move("m1", 200, 0, 0)
        self.assertEqual(mobs.threat("m1"), 0)

    def test_threat_ignored_while_leashing(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.add_threat("m1", 50)
        self.assertEqual(mobs.threat("m1"), 0)


class ReturnTimerTest(unittest.TestCase):
    def _leashed(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        return mobs

    def test_arriving_home_enters_returned(self):
        mobs = self._leashed()
        self.assertEqual(mobs.move("m1", 0, 0, 100), "returned")

    def test_stays_returned_before_reset_ms(self):
        mobs = self._leashed()
        mobs.move("m1", 0, 0, 100)
        self.assertEqual(mobs.move("m1", 0, 0, 1099), "returned")

    def test_becomes_idle_after_reset_ms(self):
        mobs = self._leashed()
        mobs.move("m1", 0, 0, 100)
        self.assertEqual(mobs.move("m1", 0, 0, 1100), "idle")

    def test_leaving_home_restarts_timer(self):
        mobs = self._leashed()
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 50, 0, 500)
        mobs.move("m1", 0, 0, 600)
        self.assertEqual(mobs.move("m1", 0, 0, 1599), "returned")
        self.assertEqual(mobs.move("m1", 0, 0, 1600), "idle")

    def test_home_edge_distance_counts_as_home(self):
        mobs = self._leashed()
        self.assertEqual(mobs.move("m1", 1, 0, 100), "returned")
        self.assertEqual(mobs.move("m1", 0.5, 0.5, 1100), "idle")


class ResetTest(unittest.TestCase):
    def test_reset_refills_hp(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.damage("m1", 60)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        self.assertEqual(mobs.hp("m1"), 100)

    def test_reset_clears_threat(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 30)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.add_threat("m1", 10)
        mobs.move("m1", 0, 0, 1100)
        self.assertEqual(mobs.threat("m1"), 0)

    def test_no_reset_before_timer_done(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.damage("m1", 60)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1099)
        self.assertEqual(mobs.hp("m1"), 40)


class AttackTest(unittest.TestCase):
    def test_cannot_attack_while_leashing(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        self.assertFalse(mobs.can_attack("m1"))

    def test_cannot_attack_while_returned(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        self.assertFalse(mobs.can_attack("m1"))

    def test_can_attack_while_chase_and_idle(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        self.assertTrue(mobs.can_attack("m1"))
        mobs.move("m1", 50, 0, 0)
        self.assertTrue(mobs.can_attack("m1"))
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        self.assertTrue(mobs.can_attack("m1"))

    def test_unknown_mob_cannot_attack(self):
        self.assertFalse(Mobs(100, 1000).can_attack("ghost"))


class InvariantTest(unittest.TestCase):
    SEQUENCE = [(200, 0, 0), (0, 0, 100), (0, 0, 1099), (50, 0, 1200),
                (0, 0, 1300), (0, 0, 2300), (100, 0, 2400), (150, 0, 2500)]

    def test_same_sequence_same_result(self):
        def run():
            mobs = Mobs(100, 1000)
            mobs.spawn("m1", 0, 0)
            return [mobs.move("m1", x, y, t) for x, y, t in self.SEQUENCE]

        self.assertEqual(run(), run())

    def test_threat_stays_zero_while_leashing(self):
        mobs = Mobs(100, 1000)
        mobs.spawn("m1", 0, 0)
        mobs.add_threat("m1", 99)
        mobs.move("m1", 200, 0, 0)
        for step in range(5):
            mobs.add_threat("m1", 10)
            mobs.move("m1", 200 + step, 0, step)
            self.assertEqual(mobs.threat("m1"), 0)


class ScanCostTest(unittest.TestCase):
    def test_scanned_counts_moves_not_mobs(self):
        mobs = Mobs(100, 1000)
        for index in range(3000):
            mobs.spawn("m-%d" % index, index, 0)
        for index in range(3000):
            mobs.move("m-%d" % index, index, 0, index)
        self.assertEqual(mobs.scanned_count(), 3000)

    def test_scanned_independent_of_population(self):
        def run(count):
            mobs = Mobs(100, 1000)
            for index in range(count):
                mobs.spawn("m-%d" % index, index, 0)
            for index in range(10):
                mobs.move("m-%d" % index, index, 0, index)
            return mobs.scanned_count()

        self.assertEqual(run(10), run(100000))

    def test_hundred_thousand_mobs_scale(self):
        mobs = Mobs(100, 1000)
        for index in range(100000):
            mobs.spawn("m-%d" % index, index, 0)
        for step in range(100000):
            mobs.move("m-%d" % (step % 100000), step, 0, step)
        self.assertEqual(mobs.scanned_count(), 100000)


if __name__ == "__main__":
    unittest.main()
