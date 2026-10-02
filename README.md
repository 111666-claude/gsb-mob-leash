# mob-leash

怪物脱战与回归：脱战半径、回归计时、重置回满与攻击禁用，只用 Python 标准库。

```
python3 -m leash.cli --sample edge
python3 -m leash.cli --sample reset
python3 -m leash.cli --sample full
python3 -m leash.cli --sample attack
python3 -m leash.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **脱战判定**：与出生点距离大于 `leash_radius` 才进入 `leashing`；
  距离正好等于半径仍算追击。
- **回归**：回到出生点（距离不超过 1）后进入 `returned`，连续待满
  `reset_ms` 才变成 `idle`；期间离开要重新计时。
- **重置内容**：变成 `idle` 时血量回满、仇恨清零。
- **攻击**：`leashing` 与 `returned` 状态下不能攻击，其它状态可以。
- **不变量**：同一串移动序列重复执行结果相同；脱战期间仇恨必须是 0。
- **查询代价**：移动一个怪物不许遍历全部怪物，`scanned_count` 不随怪物数线性增长。
- **规模**：10 万怪物、每秒 10 万次移动，单次摊还 O(1)。

## 输出契约（不改格式）

```
state=..
hp=..
can_attack=..
scanned=..
```

## 目录

```
leash/core.py   脱战、回归与重置
leash/cli.py    命令行入口
tests/          unittest 用例
```
