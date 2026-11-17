"""3dTube strong-scaling rerun: per-run and median timings from the logs.
usage: analyse.py LOGDIR OUTDIR
Per run (log <case>-n<N>-r<rep>.log): steps, final ExecutionTime/ClockTime,
window times over steps 2..N (differences from the end of step 1, which
excludes start-up), QM Newton iterations per step and Krylov iterations per
Newton iteration of the monolithic Up system, RN coupling iterations per step.
Only complete runs (50 steps, no FOAM FATAL or DIVERGED) are used. Medians
over the repeats; spread = (max - min)/median of the window."""
import csv, glob, os, re, statistics as st, sys
logdir, outdir = sys.argv[1], sys.argv[2]
tpat = re.compile(r"ExecutionTime = (\S+) s\s+ClockTime = (\S+) s")
runs = []
for f in sorted(glob.glob(os.path.join(logdir, "*-n*-r*.log"))):
    b = os.path.basename(f)
    case, n, rep = b.split("-n")[0], int(b.split("-n")[1].split("-")[0]), int(b.split("-r")[-1][:-4])
    rows, newton, ksp, coup = [], [], [], {}
    in_up, k_step, step = False, 0, None
    fatal = div = 0
    for line in open(f, errors="replace"):
        if line.startswith("Time = "):
            step = line.split()[2].rstrip(",")
            m = re.search(r"iteration: (\d+)", line)
            if m:
                coup[step] = max(coup.get(step, 0), int(m.group(1)))
            continue
        if "monolithic momentum-continuity system" in line:
            in_up, k_step = True, 0
        elif in_up and "Linear solve converged" in line:
            k_step += int(line.split()[-1])
        elif in_up and "Nonlinear solve converged" in line:
            newton.append(int(line.split()[-1])); ksp.append(k_step); in_up = False
        elif "DIVERGED" in line:
            div += 1
        elif "FOAM FATAL" in line:
            fatal += 1
        m = tpat.search(line)
        if m:
            rows.append(tuple(map(float, m.groups())))
    if len(rows) != 50 or fatal or div:
        print(f"excluded {b}: {len(rows)} timed steps, {fatal} fatal, {div} diverged", file=sys.stderr)
        continue
    (e1, c1), (en, cn) = rows[0], rows[-1]
    runs.append(dict(case=case, ranks=n, rep=rep, steps=len(rows), exec_final=en, clock_final=cn,
                     exec_win=en - e1, clock_win=cn - c1,
                     newton_per_step=sum(newton) / len(newton) if newton else "",
                     ksp_per_newton=sum(ksp) / sum(newton) if newton else "",
                     coupling_it_per_step=sum(coup.values()) / len(coup) if coup else "",
                     coupling_it_max=max(coup.values()) if coup else "", fatal=fatal, diverged=div))
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "tube3d_scaling_rerun_runs.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(runs[0])); w.writeheader(); w.writerows(runs)
coupling = {"qm": "mono", "rn": "robin"}
med = []
for case in sorted({r["case"] for r in runs}):
    rs = [r for r in runs if r["case"] == case]
    for n in sorted({r["ranks"] for r in rs}):
        g = [r for r in rs if r["ranks"] == n]
        m = lambda k: st.median(r[k] for r in g)
        win = [r["clock_win"] for r in g]; ewin = [r["exec_win"] for r in g]
        med.append(dict(coupling=coupling[case[:2]], level=case[2:], ranks=n, repeats=len(g),
                        median_exec_s=round(m("exec_final"), 1), median_clock_s=round(m("clock_final")),
                        median_exec_win_s=round(m("exec_win"), 1), median_elapsed_win_s=round(m("clock_win")),
                        spread_elapsed_pct=round(100 * (max(win) - min(win)) / st.median(win), 1),
                        spread_exec_pct=round(100 * (max(ewin) - min(ewin)) / st.median(ewin), 1),
                        newton_per_step=round(m("newton_per_step"), 2) if g[0]["newton_per_step"] != "" else "",
                        ksp_per_newton=round(m("ksp_per_newton"), 2) if g[0]["ksp_per_newton"] != "" else "",
                        coupling_it_per_step=round(m("coupling_it_per_step"), 2) if g[0]["coupling_it_per_step"] != "" else ""))
for c in {(r["coupling"], r["level"]) for r in med}:
    g = sorted([r for r in med if (r["coupling"], r["level"]) == c], key=lambda r: r["ranks"])
    t0, n0 = g[0]["median_elapsed_win_s"], g[0]["ranks"]
    for r in g:
        r["speedup_vs_min"] = round(t0 / r["median_elapsed_win_s"], 2)
        r["efficiency"] = round(t0 * n0 / (r["median_elapsed_win_s"] * r["ranks"]), 3)
        t16 = [x["median_elapsed_win_s"] for x in g if x["ranks"] == 16]
        r["efficiency_vs16"] = round(t16[0] * 16 / (r["median_elapsed_win_s"] * r["ranks"]), 3) if t16 and r["ranks"] >= 16 else ""
med.sort(key=lambda r: (r["coupling"], r["level"], r["ranks"]))
with open(os.path.join(outdir, "tube3d_scaling_rerun_medians.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(med[0])); w.writeheader(); w.writerows(med)
for r in med:
    print(r)
