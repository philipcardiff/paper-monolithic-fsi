#!/usr/bin/env python3
"""Export Hessenthaler rF results for the paper:
hv_export.py ANALYSIS_DIR RESULTS_JSON VALIDATION_SCRIPT OUTDIR [RUN ...]"""
import csv, importlib.util, json, math, sys
from pathlib import Path
A, J, V, O = map(Path, sys.argv[1:5]); O.mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("hv", V); hv = importlib.util.module_from_spec(spec); spec.loader.exec_module(hv)
res = json.loads(J.read_text())
RUNS = sys.argv[5:] or ["QM_rF0", "QM_rF1", "QM_rF2", "P_rF0", "P_rF1", "P_rF2"]
CELLS = {"rF0": 122435, "rF1": 312180, "rF2": 832552}
# tip history, decimated to 0.02 s
hist = {}
for run in RUNS:
    d = {}
    for p in sorted([q for q in (A / "runs" / run / "postProcessing").glob("[0-9]*") if q.is_dir()], key=lambda q: float(q.name)):
        f = p / "solidPointDisplacement_flapTip.dat"
        if f.exists():
            for r in hv.numeric_rows(f):
                d[round(r[0], 6)] = 1e3 * r[2]
    hist[run] = {t: v for t, v in d.items() if abs(t / 0.02 - round(t / 0.02)) < 1e-6}
times = sorted(set().union(*[set(h) for h in hist.values()]))
with open(O / "tip_history.csv", "w", newline="") as h:
    h.write("# Hessenthaler Phase I, rF meshes: tip deflection u_y (mm) every 0.02 s; QM = quasi-monolithic\n# (MeluXina, build-bf697), P = partitioned pimpleFluid IQN-ILS (UCD Sonic); empty = not run\n")
    w = csv.writer(h); w.writerow(["t"] + RUNS)
    for t in times: w.writerow([f"{t:g}"] + [f"{hist[r][t]:.5f}" if t in hist[r] else "" for r in RUNS])
with open(O / "summary.csv", "w", newline="") as h:
    h.write("# window statistics (t = 40-45 s unless noted); centreline errors vs MRI (mm); velocity d = mean voxel velocity\n# difference / 630 mm/s; its = Newton (QM) or coupling (P) iterations per step\n")
    w = csv.writer(h); w.writerow(["run", "coupling", "mesh", "fluid_cells", "t_end", "tip_mean_40_45", "tip_min", "tip_max", "tip_mean_20_25", "tip_mean_5_10", "line_rms", "line_max", "line_mean", "vel_d_mean", "vel_d_z10", "vel_d_z30", "its_window", "its_all"])
    for run in RUNS:
        r = res[run]; c, m = run.split("_")
        g = lambda k, f: (f"{r[k][f]:.4f}" if k in r else "")
        ce = r.get("centreline_err", {}); ve = r.get("velocity_err", {}); it = r.get("coupling_its") or r.get("newton_its") or {}
        w.writerow([run, c, m, CELLS[m], f"{r['t_end']:.3f}", g("tipDy_40_45", "mean"), g("tipDy_40_45", "min"), g("tipDy_40_45", "max"), g("tipDy_20_25", "mean"), g("tipDy_5_10", "mean"),
                    f"{ce['rms_mm']:.3f}" if ce else "", f"{ce['max_mm']:.3f}" if ce else "", f"{ce['mean_mm']:.3f}" if ce else "",
                    f"{ve['d_mean']:.4f}" if ve else "", f"{ve['d_mean_z10']:.4f}" if ve else "", f"{ve['d_mean_z30']:.4f}" if ve else "",
                    f"{it['window_mean']:.2f}" if it.get("window_mean") else "", f"{it['all_mean']:.2f}" if it else ""])
with open(O / "centreline.csv", "w", newline="") as h:
    h.write("# mean deformed centreline (z, y in mm) over t = 40-45 s\n"); w = csv.writer(h); w.writerow(["run", "z_mm", "y_mm"])
    for run in RUNS:
        for z, y in res[run].get("centreline", []): w.writerow([run, f"{z:.4f}", f"{y:.4f}"])
with open(O / "profiles.csv", "w", newline="") as h:
    h.write("# v_z (mm/s) on the line x = 0 of the MRI planes z = 10 and 30 mm: measured and voxel-averaged, t = 40-45 s\n")
    w = csv.writer(h); have = [r for r in RUNS if "voxels" in res[r]]; w.writerow(["z_mm", "y_mm", "vz_mri"] + have)
    base = res[have[0]]["voxels"]
    for i, v in enumerate(base):
        if abs(v["x_mm"]) < 0.7:
            w.writerow([f"{v['z_mm']:g}", f"{v['y_mm']:g}", f"{v['vz_mm_s']:.2f}"] + [("" if res[r]["voxels"][i]["vz_sim_mm_s"] is None else f"{res[r]['voxels'][i]['vz_sim_mm_s']:.2f}") for r in have])
print("written", sorted(p.name for p in O.iterdir()))
