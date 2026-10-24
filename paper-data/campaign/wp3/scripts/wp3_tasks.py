#!/usr/bin/env python3
"""Write the WP3 task lists (run_id and wp3_setup.py arguments), longest
runs first.

  wp3_tasks.py 3a > tasks_3a.txt
  wp3_tasks.py 3b > tasks_3b.txt
  wp3_tasks.py smoke > tasks_smoke.txt
  wp3_tasks.py qm618 > tasks_qm618.txt
"""
import sys

COUPLINGS = ("aitken", "iqn", "rn", "qm")
LEVELS = ("extended", "strong", "moderate", "weak")
STEPS = (200, 100, 50, 25, 12)
DTS = (0.003125, 0.00625, 0.0125, 0.025)
RHOS = (10, 1, 0.1, 0.01, 0)


def ring(c, lvl, n, tag=""):
    return f"wp3-ram-{c}-{lvl}-n{n}{tag} ring --coupling {c} --level {lvl} --steps {n}"


def coll(c, dt, rho, tag=""):
    return (f"wp3-coll-{c}-dt{dt:g}-rho{rho:g}{tag} coll --coupling {c} "
            f"--dt {dt:g} --rho-ratio {rho:g}")


what = sys.argv[1]
if what == "3a":
    lines = [ring(c, l, n) for n in STEPS for l in LEVELS for c in COUPLINGS]
elif what == "3b":
    lines = [coll(c, dt, r) for dt in DTS for r in RHOS for c in COUPLINGS]
elif what == "qm618":
    # QM arms of 3b and 3a on the #618 build (collapsible first: longer)
    lines = [coll("qm", dt, r, "-r618") for dt in DTS for r in RHOS] + \
            [ring("qm", l, n, "-r618") for n in STEPS for l in LEVELS]
elif what == "qm618mm":
    # 3b QM arm with the fixed mesh motion (predictor + diffusionHyperElastic
    # with a quadratic inverse-distance diffusivity)
    lines = [coll("qm", dt, r, "-r618mm") + " --mesh-predictor "
             "--mesh-motion diffusion" for dt in DTS for r in RHOS]
elif what == "smoke":
    lines = [ring(c, "strong", 12, "-smoke") for c in COUPLINGS] + \
            [coll(c, 0.025, 1, "-smoke") for c in COUPLINGS]
print("\n".join(lines))
