"""命令行入口：跑怪物脱战样例。"""

import argparse

from .core import Mobs


def build_parser():
    parser = argparse.ArgumentParser(prog="mob-leash", description="怪物脱战回归")
    parser.add_argument("--sample", default="edge",
                        help="edge / reset / full / attack / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "edge":
        mobs = Mobs(leash_radius=100, reset_ms=1000)
        mobs.spawn("m1", 0, 0)
        print("state=%s" % mobs.move("m1", 100, 0, 0))
    elif args.sample == "reset":
        mobs = Mobs(leash_radius=100, reset_ms=1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        print("state=%s" % mobs.move("m1", 0, 0, 1099))
    elif args.sample == "full":
        mobs = Mobs(leash_radius=100, reset_ms=1000)
        mobs.spawn("m1", 0, 0)
        mobs.damage("m1", 60)
        mobs.move("m1", 200, 0, 0)
        mobs.move("m1", 0, 0, 100)
        mobs.move("m1", 0, 0, 1100)
        print("hp=%d" % mobs.hp("m1"))
    elif args.sample == "attack":
        mobs = Mobs(leash_radius=100, reset_ms=1000)
        mobs.spawn("m1", 0, 0)
        mobs.move("m1", 200, 0, 0)
        print("can_attack=%s" % str(mobs.can_attack("m1")).lower())
    elif args.sample == "scan":
        mobs = Mobs(leash_radius=100, reset_ms=1000)
        for index in range(3000):
            mobs.spawn("m-%d" % index, index, 0)
        for index in range(3000):
            mobs.move("m-%d" % index, index, 0, index)
        print("scanned=%d" % mobs.scanned_count())
    else:
        raise SystemExit("需要 --sample edge|reset|full|attack|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
