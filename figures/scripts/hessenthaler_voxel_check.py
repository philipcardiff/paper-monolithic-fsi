#!/usr/bin/env python3
"""Hessenthaler Phase I: voxel-averaged against pointwise model velocity at the MRI
voxels (t = 40-45 s). Usage: hessenthaler_voxel_check.py ANALYSIS_DIR phaseI_velocity.csv
Prints the mean velocity difference from MRI (relative to 630 mm/s) for both and the
point-voxel difference of v_z; writes pointwise.json (summarised in
paper-data/hessenthaler/velocity_check.csv)."""
import csv, math, statistics, sys, json
from pathlib import Path
A, REF = Path(sys.argv[1]), Path(sys.argv[2])
RUNS = sys.argv[3:] or ["QM_rF0", "QM_rF1", "QM_rF2", "P_rF0", "P_rF1", "P_rF2"]  # analysis dir with runs/*/postProcessing/voxelHistory; phaseI_velocity.csv
meas = list(csv.DictReader(l for l in open(REF) if not l.startswith("#")))
meas = [{k: float(v) for k, v in r.items()} for r in meas]
S = (4, 4, 12); SZ = (1.302e-3, 1.302e-3, 6.0e-3)
def off(n, d): return ((n + 0.5) / S[d] - 0.5) * SZ[d]
key = lambda p: tuple(round(v * 1e5) for v in p)
pts = {}  # key -> (voxel index, inner?)
for i, r in enumerate(meas):
    c = (1e-3*r["x_mm"], 1e-3*r["y_mm"], 1e-3*r["z_mm"])
    for a in range(4):
        for b in range(4):
            for k in range(12):
                p = (c[0]+off(a,0), c[1]+off(b,1), c[2]+off(k,2))
                pts[key(p)] = (i, a in (1,2) and b in (1,2) and k in (5,6))
out = {}
for run in RUNS:
    vdir = A/"runs"/run/"postProcessing"/"voxelHistory"/"fluid"
    times = [d for d in vdir.iterdir() if 40-1e-9 <= float(d.name) <= 45+1e-9]
    acc = {}
    for d in times:
        for l in open(d/"voxels_U.xy"):
            if l.startswith("#") or not l.strip(): continue
            v = [float(x) for x in l.split()]
            a = acc.setdefault(key(v[:3]), [0,0,0,0]); 
            for j in range(3): a[j] += v[3+j]
            a[3] += 1
    vox = [[0,0,0,0] for _ in meas]; inn = [[0,0,0,0] for _ in meas]
    for kk, a in acc.items():
        if kk not in pts: continue
        i, inner = pts[kk]
        for tgt in ([vox[i]] + ([inn[i]] if inner else [])):
            for j in range(3): tgt[j] += a[j]/a[3]
            tgt[3] += 1
    res = []
    for r, s, q in zip(meas, vox, inn):
        e = {"x": r["x_mm"], "y": r["y_mm"], "z": r["z_mm"], "vz_mri": r["vz_mm_s"],
             "avg": [1e3*s[j]/s[3] for j in range(3)] if s[3] >= 0.5*192 else None,
             "pt": [1e3*q[j]/q[3] for j in range(3)] if q[3] == 8 else None}
        res.append(e)
    out[run] = {"n_t": len(times), "rows": res}
    def dmean(kind):
        ds = []
        for r, e in zip(meas, res):
            if e["avg"] is None or e[kind] is None: continue
            ds.append(math.dist(e[kind], (r["vx_mm_s"], r["vy_mm_s"], r["vz_mm_s"])))
        return statistics.fmean(ds)/630, len(ds)
    da, n = dmean("avg"); dp, _ = dmean("pt")
    dd = [abs(e["pt"][2]-e["avg"][2]) for e in res if e["avg"] and e["pt"]]
    print(f"{run}: n_t={len(times)} d_mean avg={da:.4f} pointwise={dp:.4f} (n={n}); |vz_pt - vz_avg| mean={statistics.fmean(dd):.2f} max={max(dd):.2f} mm/s")
    # plane flow rates over the 5 mm MRI grid (v_z x 25 mm^2, l/min), model voxel-centre values vs MRI, and the MRI/model jet (|y| >= 15 mm) flow ratio
    fl = {}
    for z in (10.0, 30.0):
        both = [(r, e) for r, e in zip(meas, res) if abs(r["z_mm"] - z) < 1e-6 and e["avg"] is not None and e["pt"] is not None]
        q = lambda vals: sum(vals) * 25e-6 * 1e-3 * 6e4   # mm/s x mm^2 -> l/min
        fl[z] = (q(e["pt"][2] for r, e in both), q(r["vz_mm_s"] for r, e in both),
                 sum(r["vz_mm_s"] for r, e in both if abs(r["y_mm"]) >= 15) / sum(e["pt"][2] for r, e in both if abs(r["y_mm"]) >= 15))
    print(f"   flux z10 model={fl[10.0][0]:.2f} mri={fl[10.0][1]:.2f} jet ratio={fl[10.0][2]:.3f}; z30 model={fl[30.0][0]:.2f} mri={fl[30.0][1]:.2f} jet ratio={fl[30.0][2]:.3f}")
json.dump(out, open("pointwise.json","w"))
