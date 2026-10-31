"""Womersley §5 diagnosis: compare the velocity profiles (first harmonic at
x ~ L/2) of the quasi-monolithic and partitioned runs directly, not their
max-error norms. Reuses the tutorial driver's analyse()."""
import importlib.util, json, math, sys
from pathlib import Path

S4F = Path("/project/home/p201136/philip-ma/rfix/solids4foam")
drv = S4F / "tutorials/fluidSolidInteraction/womersleyTube/verification/scripts/womersley_tube_verification.py"
spec_ = importlib.util.spec_from_file_location("womdrv", drv)
wom = importlib.util.module_from_spec(spec_); sys.modules["womdrv"] = wom
spec_.loader.exec_module(wom)
ref = json.load(open(wom.REFERENCE_FILE))
BASE = Path("/project/home/p201136/philip-ma")
RUNS = {"qm": ("runs-rfix", "rf-wom-qm-{}", "monolithic"),
        "qmold": ("runs", "ma-wom-qm-vstno-{}", "monolithic"),
        "rn": ("runs", "ma-wom-rn-{}", "robin"),
        "iqn": ("runs", "ma-wom-iqn-{}", "iqnils")}


def profile(key, cell):
    d, pat, coupling = RUNS[key]
    f, n = cell.split("-")
    spec = {"coupling": coupling, "factor": int(f[1:]), "steps": int(n[1:]),
            "name": pat.format(cell)}
    wom.WORK_ROOT = BASE / d
    row = wom.analyse(spec, ref)
    exact = wom.Exact(ref)
    mesh = wom.mesh_divisions(spec["factor"], ref)
    x = 0.5 * exact.L + 0.5 * exact.L / mesh["axial"]
    dr = exact.R / mesh["fluidRadial"]
    c = math.cos(math.radians(0.5))
    radii = [c * 2 / 3 * ((j + 1)**3 - j**3) * dr / ((j + 1)**2 - j**2)
             for j in range(mesh["fluidRadial"])]
    ue = [exact.velocity(r, x) for r in radii]
    s = max(abs(u) for u in ue)
    return row, [u for u in row["_profile"]], [u / s for u in ue], radii, exact.R


for cell in ["m1-n200", "m2-n100", "m2-n200", "m2-n400", "m4-n200"]:
    P = {k: profile(k, cell) for k in RUNS}
    ue, radii, R = P["qm"][2], P["qm"][3], P["qm"][4]
    n = len(radii)
    out = [cell, f"n={n}"]
    for a, b in (("qm", "rn"), ("qmold", "rn"), ("iqn", "rn")):
        d = [p - q for p, q in zip(P[a][1], P[b][1])]
        j = max(range(n), key=lambda i: abs(d[i]))
        # area-weighted mean of the difference (flux-like) and centreline
        w = [r for r in radii]
        mean = sum(di * wi for di, wi in zip(d, w)) / sum(w)
        out.append(f"{a}-{b}: max|d|={abs(d[j]):.2e}@r/R={radii[j]/R:.2f} "
                   f"axis={abs(d[0]):.2e} wall={abs(d[-1]):.2e} "
                   f"mean={abs(mean):.2e}")
    for k in ("qm", "rn"):
        e = [p - q for p, q in zip(P[k][1], ue)]
        j = max(range(n), key=lambda i: abs(e[i]))
        out.append(f"err {k}: max={abs(e[j]):.4e}@r/R={radii[j]/R:.2f} "
                   f"(norm {P[k][0]['profile']:.4e})")
    print("\n  ".join(out))
