#!/usr/bin/env python3
"""Hessenthaler Phase I: voxel-averaged against pointwise model velocity at the MRI
voxels (t = 40-45 s). Usage: hessenthaler_voxel_check.py ANALYSIS_DIR phaseI_velocity.csv
Prints the mean velocity difference from MRI (relative to 630 mm/s) for both and the
point-voxel difference of v_z; writes pointwise.json (summarised in
paper-data/hessenthaler/velocity_check.csv)."""
import csv, math, statistics, sys, json
from pathlib import Path
A, REF = Path(sys.argv[1]), Path(sys.argv[2])  # analysis dir with runs/*/postProcessing/voxelHistory; phaseI_velocity.csv
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
for run in ("QM_rF0","QM_rF1","P_rF0","P_rF1","P_rF2"):
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
    print(f"{run}: n_t={len(times)} d_mean avg={da:.4f} pointwise={dp:.4f} (n={n}); |vz_pt - vz_avg| mean={statistics.fmean(dd):.1f} max={max(dd):.1f} mm/s")
json.dump(out, open("pointwise.json","w"))
