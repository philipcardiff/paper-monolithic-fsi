"""Post-process tl-cav-qmlin-L{1..4}-r{1..3}: final u_y(A), F_y, Newton/step, Krylov/Newton,
time to steady (1e-4 relative), clock and execution times; medians per level."""
import re, sys, json, statistics as st
from pathlib import Path
sys.path.insert(0, "/project/home/p201287/philip/qm-a421/solids4foam/tutorials/fluidSolidInteraction/cavityFlexibleBottom/verification/scripts")
import cavity_flexible_bottom_verification as cav
R = Path(sys.argv[1] if len(sys.argv) > 1 else "/project/home/p201136/philip-ma/cavlin/runs")
def tts(h, rel):
    final = h[-1][1]; t = h[0][0]
    for ti, v in h:
        if abs(v - final) > rel * abs(final): t = ti
    return t
rows = []
for d in sorted(R.glob("tl-cav-qmlin-L*-r*")):
    f = d / "log.solids4Foam"
    if not f.exists():
        print("skip", d.name); continue
    partial = "\nEnd" not in f.read_text(errors="replace")
    log = f.read_text(errors="replace")
    times = [float(t) for t in re.findall(r"^Time = ([0-9.eE+-]+)", log, re.M)]
    n = [int(x) for x in re.findall(r"^Solving the monolithic momentum-continuity system.*?Nonlinear solve \w+ due to \w+ iterations (\d+)", log, re.M | re.S)]
    k = [int(x) for x in re.findall(r"Linear solve converged due to \w+ iterations (\d+)", log)]
    ex = re.findall(r"ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s", log)
    disp = cav.read_displacement_history(d); force = cav.read_force_history(d)
    t_ss = 167.5 if partial else tts(disp, 1e-4); kss = sum(1 for t in times if t <= t_ss + 1e-9)
    blocks = re.findall(r"^Time = ([0-9.eE+-]+)\n(.*?)ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s", log, re.M | re.S)
    tc = {float(b[0]): float(b[3]) for b in blocks}
    clock_ss = max((c for t, c in tc.items() if t <= t_ss + 1e-9), default=None)
    r = dict(id=d.name, level=int(d.name.split("-L")[1][0]), t_end=times[-1] if times else None,
             uy=disp[-1][1], fy=force[-1][1], n_steps=len(n), newton_per_step=sum(n)/len(n),
             ksp_per_newton=sum(k)/len(k), t_steady=t_ss, steps_to_steady=kss,
             exec_s=float(ex[-1][0]), clock_s=float(ex[-1][1]), clock_to_steady=clock_ss, partial=partial)
    rows.append(r); print(json.dumps(r))
for L in (1, 2, 3, 4):
    rr = [r for r in rows if r["level"] == L]
    print(f"L{L} clock_to_steady={[r['clock_to_steady'] for r in rr]} partial={[r['partial'] for r in rr]} median={st.median(r['clock_to_steady'] for r in rr) if rr else None}")
    if not rr: continue
    c = st.median(r["clock_s"] for r in rr); e = st.median(r["exec_s"] for r in rr)
    print(f"L{L}: n={len(rr)} uy={[r['uy'] for r in rr]} fy={[r['fy'] for r in rr]} newton/step={rr[0]['newton_per_step']:.3f} "
          f"ksp/newton={rr[0]['ksp_per_newton']:.1f} steps_to_steady={[r['steps_to_steady'] for r in rr]} t_ss={rr[0]['t_steady']} "
          f"median clock={c} exec={e} spread={max(r['clock_s'] for r in rr)/min(r['clock_s'] for r in rr)-1:.4f} "
          f"cost_to_steady_clock={c*rr[0]['steps_to_steady']/rr[0]['n_steps']:.1f}")
