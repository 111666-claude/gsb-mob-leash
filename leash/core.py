"""怪物脱战与回归：脱战半径、回归计时、重置回满与攻击禁用。

缺陷：脱战判定用大于等于（正好等于半径就脱战）、回归计时不生效、
重置不回满血也不清仇恨、脱战期间还能攻击、每次移动扫描全部怪物。
"""

import math


class Mobs:
    """怪物脱战台账。"""

    def __init__(self, leash_radius, reset_ms):
        self.leash_radius = leash_radius
        self.reset_ms = reset_ms
        self.mobs = {}
        self.scanned = 0

    def spawn(self, mob_id, x, y, max_hp=100):
        self.mobs[mob_id] = {"id": mob_id, "x": x, "y": y, "home_x": x, "home_y": y,
                             "state": "idle", "max_hp": max_hp, "hp": max_hp,
                             "threat": 0, "home_since": None}

    def damage(self, mob_id, amount):
        mob = self.mobs.get(mob_id)
        if mob is None:
            return 0
        mob["hp"] = max(0, mob["hp"] - amount)
        return mob["hp"]

    def add_threat(self, mob_id, amount):
        mob = self.mobs.get(mob_id)
        if mob is not None:
            mob["threat"] += amount

    def move(self, mob_id, x, y, now_ms):
        """移动一个怪物，返回它的状态。"""
        self.scanned += len(self.mobs)
        mob = self.mobs.get(mob_id)
        if mob is None:
            return "unknown"
        distance = math.hypot(x - mob["home_x"], y - mob["home_y"])
        mob["x"], mob["y"] = x, y
        if distance >= self.leash_radius:
            mob["state"] = "leashing"
        elif distance <= 1:
            mob["state"] = "idle"
        else:
            mob["state"] = "chase"
        return mob["state"]

    def can_attack(self, mob_id):
        return mob_id in self.mobs

    def hp(self, mob_id):
        mob = self.mobs.get(mob_id)
        return 0 if mob is None else mob["hp"]

    def threat(self, mob_id):
        mob = self.mobs.get(mob_id)
        return 0 if mob is None else mob["threat"]

    def state(self, mob_id):
        mob = self.mobs.get(mob_id)
        return "unknown" if mob is None else mob["state"]

    def scanned_count(self):
        return self.scanned
