"""怪物脱战与回归：脱战半径、回归计时、重置回满与攻击禁用。

口径（README 为准）：
- 脱战判定：与出生点距离大于 leash_radius 才进入 leashing，等于半径仍算追击。
- 回归：回到出生点（距离不超过 1）进入 returned，连续待满 reset_ms 才变成
  idle，中途离开重新计时。
- 重置内容：变成 idle 时血量回满、仇恨清零。
- 攻击：leashing 与 returned 状态下不能攻击，其它状态可以。
- 不变量：同一串移动序列重复执行结果相同；脱战期间仇恨必须是 0。
- 代价：移动一个怪物只动它自己，单次摊还 O(1)。
"""


class Mobs:
    """怪物脱战台账。"""

    def __init__(self, leash_radius, reset_ms):
        self.leash_radius = leash_radius
        self.reset_ms = reset_ms
        self._leash_radius_sq = leash_radius * leash_radius
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
        if mob is None or mob["state"] == "leashing":
            return
        mob["threat"] += amount

    def move(self, mob_id, x, y, now_ms):
        """移动一个怪物，返回它的状态。"""
        self.scanned += 1
        mob = self.mobs.get(mob_id)
        if mob is None:
            return "unknown"
        dx = x - mob["home_x"]
        dy = y - mob["home_y"]
        distance_sq = dx * dx + dy * dy
        mob["x"], mob["y"] = x, y
        if distance_sq > self._leash_radius_sq:
            mob["state"] = "leashing"
            mob["threat"] = 0
            mob["home_since"] = None
        elif distance_sq > 1:
            mob["state"] = "chase"
            mob["home_since"] = None
        else:
            state = mob["state"]
            if state == "idle":
                pass
            elif state == "returned":
                if now_ms - mob["home_since"] >= self.reset_ms:
                    self._reset(mob)
            else:
                mob["state"] = "returned"
                mob["home_since"] = now_ms
        return mob["state"]

    def _reset(self, mob):
        mob["state"] = "idle"
        mob["hp"] = mob["max_hp"]
        mob["threat"] = 0
        mob["home_since"] = None

    def can_attack(self, mob_id):
        mob = self.mobs.get(mob_id)
        return mob is not None and mob["state"] not in ("leashing", "returned")

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
