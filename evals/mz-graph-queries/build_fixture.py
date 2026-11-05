#!/usr/bin/env python3
"""Emit fixture SQL on stdout.

  build_fixture.py --small [--schema S]                 the skill's example world
  build_fixture.py --eval --seed N --scale N [--no-traps] --schema S
  build_fixture.py --eval ... --manifest                 print params as JSON instead of SQL
"""
import argparse, json, sys
from decimal import Decimal
import fixture as fx


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--small", action="store_true")
    g.add_argument("--eval", action="store_true")
    ap.add_argument("--schema", default=None, help="omit to emit unqualified names for the current schema")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--no-traps", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    a = ap.parse_args()
    f = fx.small_fixture() if a.small else fx.eval_fixture(a.seed, a.scale, traps=not a.no_traps)
    if a.manifest:
        json.dump(f.params, sys.stdout, indent=2, default=lambda v: str(v) if isinstance(v, Decimal) else v)
        print()
    else:
        sys.stdout.write(fx.to_sql(f, a.schema))
    return 0


if __name__ == "__main__":
    sys.exit(main())
