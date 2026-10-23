#!/usr/bin/env python3
"""1f BDF2 start-up check on ringAddedMass: the frequency and the amplitude
loss with a start-up window excluded.

The QM runs start the backward (BDF2) scheme with one Euler step (no
old-old time level at t = 0). The driver fits the zero crossings after the
first one; here the same fit is repeated on the history from t = T (one
exact period) onwards, for every 1a run and its dry ring, and the
differences are reported. If the start-up step mattered, the frequency,
the wet/dry ratio and the loss would change when it is excluded.

    ma_1f.py RUNS_DIR S4F_TUTORIALS OUT_CSV
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

runs, tut, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
spec = importlib.util.spec_from_file_location(
    "ram", tut / "ringAddedMass/verification/scripts/"
    "ring_added_mass_verification.py")
ram = importlib.util.module_from_spec(spec)
sys.modules["ram"] = ram
spec.loader.exec_module(ram)
ram.WORK_ROOT = runs


def fit(r, skip_periods):
    times, values = ram.read_histories(runs / r["run_id"], r)
    t0 = skip_periods * r["period"]
    keep = [(t, v) for t, v in zip(times, values) if t >= t0 - 1e-12]
    return ram.frequency_and_damping([k[0] for k in keep],
                                     [k[1] for k in keep],
                                     r["periods"] - skip_periods)


res = {}
for f in runs.glob("ma-ram-*/ma_result.json"):
    r = json.loads(f.read_text())
    if r["status"] == "completed" and r["def"]["item"] == "1a" \
            and "tight" not in r["run_id"]:
        res[r["run_id"]] = r

rows = []
for rid, r in sorted(res.items()):
    if r["kind"] != "wet":
        continue
    df = r["def"]
    dry = res[f"ma-ram-dry-m{df['factor']}-n{df['steps']}"]
    a, b = fit(r, 0), fit(r, 1)
    da, db = fit(dry, 0), fit(dry, 1)
    exact = r["omega_exact"] / dry["omega_exact"]
    rows.append(dict(
        run_id=rid, level=df["level"], mesh=df["factor"], steps=df["steps"],
        omega_default=a["omega"], omega_skip1T=b["omega"],
        omega_rel_change=b["omega"] / a["omega"] - 1,
        ratio_err_default=a["omega"] / da["omega"] / exact - 1,
        ratio_err_skip1T=b["omega"] / db["omega"] / exact - 1,
        loss_default=a["loss_per_period"], loss_skip1T=b["loss_per_period"],
        dry_loss_default=da["loss_per_period"],
        dry_loss_skip1T=db["loss_per_period"]))
with out.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
mx = lambda k: max(abs(r[k]) for r in rows)
print(f"{len(rows)} wet runs")
print(f"max |omega change| {mx('omega_rel_change'):.2e}")
print("max |ratio err change| "
      f"{max(abs(r['ratio_err_skip1T'] - r['ratio_err_default']) for r in rows):.2e}")
print("max |loss change| "
      f"{max(abs(r['loss_skip1T'] - r['loss_default']) for r in rows):.2e}")
for r in rows:
    if r["mesh"] == 2 and r["level"] == "strong":
        print(r["steps"], f"{r['omega_rel_change']:+.2e}",
              f"ratio {100*r['ratio_err_default']:+.4f}/{100*r['ratio_err_skip1T']:+.4f}%",
              f"loss {100*r['loss_default']:.4f}/{100*r['loss_skip1T']:.4f}%")
