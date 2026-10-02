"""怪物脱战与回归：脱战半径、回归计时、重置回满与攻击禁用。

口径（README 为准）：
- 距离大于 leash_radius 才进入 leashing，正好等于半径仍算 chase。
- 回到出生点（距离不超过 1）进入 returned，连续待满 reset_ms 才变
  idle，中途离开重新计时。
- 变成 idle 时血量回满、仇恨清零；脱战（leashing/returned）期间仇恨
  保持 0。
- leashing 与 returned 不能攻击，其它状态可以。
- 移动一个怪物只访问它自己，单次摊还 O(1)。
"""

import math

_LEASH_STATES = ("leashing", "returned")


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
        if mob is None:
            return
        if mob["state"] in _LEASH_STATES:
            return  # 脱战期间仇恨必须保持 0
        mob["threat"] += amount

    def move(self, mob_id, x, y, now_ms):
        """移动一个怪物，返回它的状态。只访问该怪物，摊还 O(1)。"""
        self.scanned += 1
        mob = self.mobs.get(mob_id)
        if mob is None:
            return "unknown"
        distance = math.hypot(x - mob["home_x"], y - mob["home_y"])
        mob["x"], mob["y"] = x, y
        if distance > self.leash_radius:
            mob["state"] = "leashing"
            mob["threat"] = 0
            mob["home_since"] = None
        elif distance <= 1:
            if mob["state"] != "idle":
                if mob["home_since"] is None:
                    mob["home_since"] = now_ms
                if now_ms - mob["home_since"] >= self.reset_ms:
                    mob["state"] = "idle"
                    mob["hp"] = mob["max_hp"]
                    mob["threat"] = 0
                    mob["home_since"] = None
                else:
                    mob["state"] = "returned"
        else:
            mob["state"] = "chase"
            mob["home_since"] = None
        return mob["state"]

    def can_attack(self, mob_id):
        mob = self.mobs.get(mob_id)
        if mob is None:
            return False
        return mob["state"] not in _LEASH_STATES

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
