#!/usr/bin/env python3
"""R4: tables and the work-precision figure from runs.csv and qois.csv.

Usage:  r4_analysis.py R4_DIR

Writes, in R4_DIR/tables/:
  accuracy.csv     QoI, error against Featflow, per coupling and level, and
                   the monolithic-minus-IQN-ILS difference per level
  order.csv        observed orders: against Featflow (2x->4x, 1x->2x) and
                   reference-free from the three levels
  sweep.csv        2x tolerance sweep: QoI difference from the tight
                   reference against 5% of the 2x->4x change of the same
                   coupling (HANDOFF Section 10 rule), with cost
  timing.csv       timing windows: median over repeats per coupling/level
and R4_DIR/figures/work_precision.{pdf,png}: |error| against core-hours per
simulated second, one panel per QoI, both couplings, points per level.
The cost axis uses the timing-window rows (study 'timing'); while those are
missing it falls back to the accuracy runs (marked in the title).
"""

import csv
import math
import statistics
import sys
from pathlib import Path

PRIMARY = ["ux_mean", "ux_amplitude", "uy_amplitude", "uy_frequency",
           "drag_mean", "drag_amplitude", "lift_amplitude",
           "lift_amplitude_smoothed"]
LABEL = {"ux_mean": "u_x mean", "ux_amplitude": "u_x amplitude",
         "uy_amplitude": "u_y amplitude", "uy_frequency": "u_y frequency",
         "drag_mean": "drag mean", "drag_amplitude": "drag amplitude",
         "lift_amplitude": "lift amplitude",
         "lift_amplitude_smoothed": "lift amplitude (smoothed)"}
COUP = {"NewtonQuasiMonolithic": "mono", "IQNILS": "iqn"}


def read(p):
    with open(p) as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


def write(p, rows, cols):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v)
                        for k, v in r.items()})


def main():
    d = Path(sys.argv[1])
    runs = {r["run_id"]: r for r in read(d / "runs.csv")}
    q = {}
    for r in read(d / "qois.csv"):
        q.setdefault(r["run_id"], {})[r["qoi"]] = r
    acc = {}
    for rid, r in runs.items():
        if r.get("study") == "accuracy" and r["status"] == "completed" and rid in q:
            acc[(COUP[r["coupling"]], r["level"])] = rid

    # A. accuracy
    rows = []
    for lv in ("1x", "2x", "4x"):
        for name in PRIMARY:
            row = {"level": lv, "qoi": name}
            for c in ("mono", "iqn"):
                rid = acc.get((c, lv))
                e = q.get(rid, {}).get(name, {})
                row[f"{c}_value"] = fnum(e.get("value"))
                row[f"{c}_error"] = fnum(e.get("rel_error"))
                row[f"{c}_run"] = rid or ""
            row["reference"] = fnum(e.get("reference")) if e else math.nan
            mv, iv = row["mono_value"], row["iqn_value"]
            row["mono_minus_iqn_rel"] = (mv - iv) / abs(iv) if iv else math.nan
            rows.append(row)
    write(d / "tables/accuracy.csv", rows,
          ["level", "qoi", "reference", "mono_value", "mono_error",
           "iqn_value", "iqn_error", "mono_minus_iqn_rel", "mono_run", "iqn_run"])

    # B. order
    orows = []
    for c in ("mono", "iqn"):
        for name in PRIMARY:
            v = {lv: fnum(q.get(acc.get((c, lv)), {}).get(name, {}).get("value"))
                 for lv in ("1x", "2x", "4x")}
            e = {lv: fnum(q.get(acc.get((c, lv)), {}).get(name, {}).get("rel_error"))
                 for lv in ("1x", "2x", "4x")}

            def lg(a, b):
                return math.log2(abs(a) / abs(b)) if a and b and \
                    all(map(math.isfinite, (a, b))) else math.nan
            orows.append({
                "coupling": c, "qoi": name,
                "err_1x": e["1x"], "err_2x": e["2x"], "err_4x": e["4x"],
                "p_featflow_1x_2x": lg(e["1x"], e["2x"]),
                "p_featflow_2x_4x": lg(e["2x"], e["4x"]),
                "change_2x_4x_rel": (v["4x"] - v["2x"]) / abs(v["4x"])
                if v["4x"] else math.nan,
                "p_reference_free": lg(v["2x"] - v["1x"], v["4x"] - v["2x"]),
                "same_sign_changes": (v["2x"] - v["1x"]) * (v["4x"] - v["2x"]) > 0
                if all(map(math.isfinite, v.values())) else ""})
    write(d / "tables/order.csv", orows, list(orows[0].keys()))
    change = {(r["coupling"], r["qoi"]): r["change_2x_4x_rel"] for r in orows}

    # C. sweep
    srows = []
    for c in ("mono", "iqn"):
        ref = f"r4-fsi3-{c}-2x-sref"
        for rid, r in sorted(runs.items()):
            if not rid.startswith(f"r4-fsi3-{c}-2x-s"):
                continue
            for name in PRIMARY:
                a = fnum(q.get(rid, {}).get(name, {}).get("value"))
                b = fnum(q.get(ref, {}).get(name, {}).get("value"))
                diff = abs(a - b) / abs(b) if b else math.nan
                disc = abs(change.get((c, name), math.nan))
                srows.append({
                    "coupling": c, "run_id": rid, "qoi": name,
                    "tolerance": rid.rsplit("-s", 1)[1],
                    "status": r["status"], "rel_diff_vs_ref": diff,
                    "disc_change_2x_4x": disc,
                    "ratio_to_disc": diff / disc if disc else math.nan,
                    "passes_5pct_rule": diff <= 0.05 * disc
                    if math.isfinite(diff) and math.isfinite(disc) else "",
                    "iters_mean": fnum(r["iters_mean"]),
                    "ksp_per_newton_mean": fnum(r["ksp_per_newton_mean"]),
                    "wall_s_per_step": fnum(r["wall_s_per_step"]),
                    "core_h_per_sim_s": fnum(r["core_h_per_sim_s"])})
    if srows:
        write(d / "tables/sweep.csv", srows, list(srows[0].keys()))

    # D. timing and work-precision
    trows, cost = [], {}
    tim = [r for r in runs.values() if r.get("study") == "timing"
           and r["status"] == "completed"]
    source = "timing windows"
    groups = {}
    for r in tim:
        groups.setdefault((COUP[r["coupling"]], r["level"]), []).append(r)
    for (c, lv), rs in sorted(groups.items()):
        med = statistics.median(fnum(r["core_h_per_sim_s"]) for r in rs)
        cost[(c, lv)] = med
        trows.append({"coupling": c, "level": lv, "repeats": len(rs),
                      "ranks": rs[0]["ranks"],
                      "core_h_per_sim_s_median": med,
                      "wall_s_per_step_median": statistics.median(
                          fnum(r["wall_s_per_step"]) for r in rs),
                      "spread_rel": (max(fnum(r["wall_s_per_step"]) for r in rs)
                                     - min(fnum(r["wall_s_per_step"]) for r in rs))
                      / statistics.median(fnum(r["wall_s_per_step"]) for r in rs),
                      "runs": " ".join(r["run_id"] for r in rs)})
    if trows:
        write(d / "tables/timing.csv", trows, list(trows[0].keys()))
    if not cost:
        source = "accuracy runs (provisional)"
        for (c, lv), rid in acc.items():
            cost[(c, lv)] = fnum(runs[rid]["core_h_per_sim_s"])
    plot(d, acc, q, cost, source)


def plot(d, acc, q, cost, source):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colours = {"mono": "#2a78d6", "iqn": "#eb6834"}
    markers = {"mono": "o", "iqn": "s"}
    names = {"mono": "quasi-monolithic", "iqn": "IQN-ILS (strict)"}
    panels = [n for n in PRIMARY]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.2), sharex=True)
    for ax, name in zip(axes.flat, panels):
        for c in ("mono", "iqn"):
            pts = []
            for lv in ("1x", "2x", "4x"):
                rid = acc.get((c, lv))
                e = fnum(q.get(rid, {}).get(name, {}).get("rel_error"))
                x = cost.get((c, lv), math.nan)
                if math.isfinite(e) and math.isfinite(x) and e != 0:
                    pts.append((x, abs(e), lv))
            if not pts:
                continue
            xs, ys, ls = zip(*pts)
            ax.plot(xs, ys, color=colours[c], lw=2, marker=markers[c], ms=8,
                    markeredgecolor="white", markeredgewidth=1.5,
                    label=names[c])
            for x, y, lv in pts:
                ax.annotate(lv, (x, y), textcoords="offset points",
                            xytext=(5, 4), fontsize=8, color="#555555")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(LABEL[name], fontsize=10)
        ax.grid(True, which="major", color="#e4e4e4", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for ax in axes[1]:
        ax.set_xlabel("core-hours per simulated second")
    for ax in axes[:, 0]:
        ax.set_ylabel("|relative error| vs Featflow")
    axes.flat[0].legend(frameon=False, fontsize=9)
    fig.suptitle(f"Hron-Turek FSI3, conformal meshes 1x/2x/4x: work-precision "
                 f"(cost from {source})", fontsize=11)
    fig.tight_layout()
    out = d / "figures"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "work_precision.pdf")
    fig.savefig(out / "work_precision.png", dpi=150)


if __name__ == "__main__":
    main()
