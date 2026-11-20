#!/usr/bin/env python3
"""Hessenthaler Phase I, rF family: QM vs partitioned (pimpleFluid IQN-ILS).
Window statistics of the tip deflection, mean centreline vs MRI, voxel-averaged
velocity vs MRI (tutorial validation functions), partitioned coupling
iterations. Usage: hv_analysis.py ANALYSIS_DIR VALIDATION_SCRIPT OUT_JSON [RUN ...]
Restart segments postProcessing/<t0>/ are stitched in numerical order of t0; where
segments overlap, the later one wins. QM Newton iterations per step are counted
from the run's log.solids4Foam* files (the last SNES block of each step)."""
import importlib.util, json, math, re, statistics, sys
from pathlib import Path
A, V, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
RUNS = sys.argv[4:] or ["QM_rF0", "QM_rF1", "QM_rF2", "P_rF0", "P_rF1", "P_rF2"]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("hv", V); hv = importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)
REF = V.parents[1] / "reference"
meas_line = hv.read_csv(REF / "phaseI_centreline.csv")
meas_vel = hv.read_csv(REF / "phaseI_velocity.csv")
W = (40.0, 45.0)

def series(run, name):
    rows = []
    for d in segments(run):
        f = d / f"solidPointDisplacement_{name}.dat"
        if f.exists():
            rows += hv.numeric_rows(f)
    return {round(r[0], 9): r for r in rows}   # later segments override

def segments(run):
    """Restart segments of a run's postProcessing, in numerical order of start time."""
    dirs = [d for d in (A / "runs" / run / "postProcessing").glob("[0-9]*") if d.is_dir()]
    return sorted(dirs, key=lambda d: float(d.name))

def newton_its(run):
    """Newton iterations per step from the QM logs (last SNES block of each step)."""
    its = {}
    for f in sorted((A / "runs" / run).glob("log.solids4Foam*"), key=lambda p: (p.name == "log.solids4Foam", int(p.suffix[1:]) if p.suffix[1:].isdigit() else 0)):  # .1, .2, ..., then the latest
        t, blocks = None, []
        for line in open(f, errors="ignore"):
            m = re.match(r"^Time = ([0-9.eE+-]+)\s*$", line)
            if m:
                if t is not None and blocks: its[t] = blocks[-1]
                t, blocks = round(float(m.group(1)), 6), []; continue
            m = re.match(r"^\s+(\d+) SNES Function norm", line)
            if m:
                k = int(m.group(1))
                if k == 0: blocks.append(0)
                elif blocks: blocks[-1] = k
        if t is not None and blocks: its[t] = blocks[-1]
    return its

def window(d, w=W):
    return [d[t] for t in sorted(d) if w[0] - 1e-9 <= t <= w[1] + 1e-9]

res = {}
for run in RUNS:
    tip = series(run, "flapTip")
    r = {"t_end": max(tip)}
    for w in ((40.0, 45.0), (20.0, 25.0), (5.0, 10.0)):
        win = window(tip, w)
        if win and win[-1][0] >= w[1] - 1e-6:
            dy = [1e3 * x[2] for x in win]
            r[f"tipDy_{w[0]:g}_{w[1]:g}"] = {"mean": statistics.fmean(dy), "min": min(dy), "max": max(dy), "std": statistics.pstdev(dy)}
    if r["t_end"] >= W[1] - 1e-6:
        line = [(0.0, 0.0)]
        for k in range(65):
            win = window(series(run, f"flapCentrelineN{k:02d}"))
            z0 = k + 1.0
            line.append((z0 + 1e3 * statistics.fmean(x[3] for x in win), 1e3 * statistics.fmean(x[2] for x in win)))
        r["centreline"] = line
        r["centreline_err"] = hv.centreline_errors(sorted(line), meas_line)
        # voxel velocities, time-averaged over the window
        vdir = A / "runs" / run / "postProcessing" / "voxelHistory" / "fluid"
        times = [d for d in vdir.iterdir() if W[0] - 1e-9 <= float(d.name) <= W[1] + 1e-9] if vdir.exists() else []
        if times:
            def key(p): return tuple(round(v * 1.0e5) for v in p)
            acc = {}
            for d in times:
                for row in hv.numeric_rows(d / "voxels_U.xy"):
                    a = acc.setdefault(key(row[:3]), [0.0, 0.0, 0.0, 0]); a[0] += row[3]; a[1] += row[4]; a[2] += row[5]; a[3] += 1
            pts = hv.voxel_points(meas_vel); sums = [[0.0, 0.0, 0.0, 0] for _ in meas_vel]
            for i, p in pts:
                a = acc.get(key(p))
                if a:
                    for d in range(3): sums[i][d] += a[d] / a[3]
                    sums[i][3] += 1
            per = math.prod(hv.VOXEL_SAMPLES); vox = []
            for row, s in zip(meas_vel, sums):
                e = dict(row); e["fluid_fraction"] = s[3] / per
                for d, k in enumerate(("vx", "vy", "vz")):
                    e[f"{k}_sim_mm_s"] = 1e3 * s[d] / s[3] if s[3] >= 0.5 * per else None
                vox.append(e)
            r["velocity_err"] = hv.velocity_errors(vox, 630.0); r["voxel_times"] = len(times)
            r["voxels"] = vox
    if run.startswith("P_"):
        f = A / "runs" / run / "postProcessing" / "fsiResiduals.dat"
        it = {}
        for row in hv.numeric_rows(f):
            it[round(row[0], 9)] = max(it.get(round(row[0], 9), 0), int(row[1]))
        w = [it[t] for t in it if W[0] <= t <= W[1]]; a = list(it.values())
        r["coupling_its"] = {"window_mean": statistics.fmean(w) if w else None, "all_mean": statistics.fmean(a), "max": max(a)}
    if run.startswith("QM_"):
        it = newton_its(run)
        if it:
            win = [it[t] for t in it if W[0] < t <= W[1] + 1e-9]; first = [it[t] for t in it if t <= 5.0 + 1e-9]
            r["newton_its"] = {"window_mean": statistics.fmean(win) if win else None, "all_mean": statistics.fmean(it.values()),
                               "first5s_steps_ge3": sum(1 for x in first if x >= 3), "max": max(it.values()),
                               "first_single_iteration_t": min((t for t in it if it[t] == 1), default=None)}
    res[run] = r
OUT.write_text(json.dumps(res, indent=1))
for run, r in res.items():
    s = f"{run:7s} t_end={r['t_end']:.3f}"
    for k in ("tipDy_40_45", "tipDy_20_25", "tipDy_5_10"):
        if k in r: s += f" {k}={r[k]['mean']:.3f}[{r[k]['min']:.3f},{r[k]['max']:.3f}]"
    if "centreline_err" in r: c = r["centreline_err"]; s += f" | line rms={c['rms_mm']:.2f} max={c['max_mm']:.2f} mean={c['mean_mm']:+.2f}"
    if "velocity_err" in r: v = r["velocity_err"]; s += f" | vel d_mean={v['d_mean']:.4f} (z10 {v['d_mean_z10']:.4f}, z30 {v['d_mean_z30']:.4f}) voxels={v['voxels']}/{v['voxels_total']} n_t={r['voxel_times']}"
    if "coupling_its" in r: s += f" | IQN its window={r['coupling_its']['window_mean']:.2f} all={r['coupling_its']['all_mean']:.2f} max={r['coupling_its']['max']}"
    if "newton_its" in r: n = r["newton_its"]; s += f" | Newton window={n['window_mean']} all={n['all_mean']:.3f} >=3 in first 5 s={n['first5s_steps_ge3']} one-iteration from t={n['first_single_iteration_t']}"
    print(s)
