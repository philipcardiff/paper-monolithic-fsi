#!/usr/bin/env python3
"""Run agent A, batch 1: ringAddedMass (1a, 1d) and womersleyTube (1e).

Each run is a fresh copy of the tutorial at the solver head, set up with the
tutorials' own verification drivers (configure, analyse); only case files
are edited (viscousStressTranspose, coupling test, couplingReuse, PETSc
tolerances). All runs are serial; at most --cores run at once. Results go to
<runs>/<run_id>/ma_result.json.

    ma_run.py --s4f DIR --runs DIR [--cores N] [--only ID,ID] [--list]
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIGHT = {"snes_rtol": "1e-8", "snes_stol": "1e-8", "ksp_rtol": "1e-6"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Case-file edits
# ---------------------------------------------------------------------------

def sub1(path, pattern, repl, flags=re.MULTILINE):
    text, n = re.subn(pattern, repl, path.read_text(), count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f"no match for {pattern!r} in {path}")
    path.write_text(text)


def set_vst(case, value):
    sub1(case / "constant/fluid/fluidProperties.monolithic",
         r"(newtonIcoFluidCoeffs\s*\{\n)",
         rf"\g<1>    viscousStressTranspose {value};\n\n")


def set_petsc(case, options):
    path = case / "system/fvSolution.monolithic"
    for key, value in options.items():
        sub1(path, rf"(^\s*{key}\s+)\"?[^;\"]*\"?;", rf'\g<1>"{value}";')


def set_partitioned(case, coupling):
    """Strict coupling test; IQN-ILS reuse pinned to the head default 0."""
    extra = "    requireAllResidualMeasures yes;\n"
    if coupling == "iqnils":
        extra += "    couplingReuse 0;\n"
    sub1(case / f"constant/fsiProperties.{coupling}",
         r"(^\s*writeResidualsToFile\s+yes;\n)", rf"\g<1>{extra}")


# ---------------------------------------------------------------------------
# Run definitions
# ---------------------------------------------------------------------------

def definitions(rfix=True):
    out = []
    # 1a: ring QM, 3 levels x mesh 1/2/4 x 25/50/100/200 steps per period,
    # with the dry (standard solid) ring for the wet/dry ratio
    for f in (1, 2, 4):
        for n in (25, 50, 100, 200):
            out.append(dict(id=f"ma-ram-dry-m{f}-n{n}", item="1a",
                            case="ram", kind="dry", solid="standard",
                            factor=f, steps=n))
            for lvl in ("weak", "moderate", "strong"):
                out.append(dict(id=f"ma-ram-qm-{lvl}-m{f}-n{n}", item="1a",
                                case="ram", kind="wet", level=lvl,
                                coupling="monolithic", solid="standard",
                                factor=f, steps=n, vst="no", petsc={}))
    # B1 iterative-error check: tight PETSc tolerances, m2 n100
    for lvl in ("weak", "moderate", "strong"):
        out.append(dict(id=f"ma-ram-qm-{lvl}-m2-n100-tight", item="1a",
                        case="ram", kind="wet", level=lvl,
                        coupling="monolithic", solid="standard", factor=2,
                        steps=100, vst="no", petsc=TIGHT))
    # 1d: partitioned, standard solid, strong, mesh 2 (QM is in 1a)
    for coupling, tag in (("iqnils", "iqn"), ("robin", "rn")):
        for n in (25, 50, 100):
            out.append(dict(id=f"ma-ram-{tag}-strong-m2-n{n}", item="1d",
                            case="ram", kind="wet", level="strong",
                            coupling=coupling, solid="standard", factor=2,
                            steps=n))
    # 1e: Womersley QM with the transpose term on and off; RN and IQN-ILS at
    # the head with the strict test (m2 n50 of all four is in WP0)
    cells = [(1, 200), (2, 200), (4, 200), (2, 100), (2, 400)]
    for f, n in cells:
        for vst in ("no", "yes"):
            out.append(dict(id=f"ma-wom-qm-vst{vst}-m{f}-n{n}", item="1e",
                            case="wom", coupling="monolithic", factor=f,
                            steps=n, vst=vst, petsc=TIGHT))
        for coupling, tag in (("robin", "rn"), ("iqnils", "iqn")):
            out.append(dict(id=f"ma-wom-{tag}-m{f}-n{n}", item="1e",
                            case="wom", coupling=coupling, factor=f,
                            steps=n))
    for r in out:
        r["ranks"] = 1
        r["batch"] = 1
    return out + definitions2(rfix)


def definitions2(rfix=True):
    out = []
    # 2a: cavity QM L1-L4, steady (ddt(U) Euler as the partitioned file),
    # dt 0.5 to 300 s with the 20 s inlet ramp, as the #597 rerun;
    # 2b: L2, L3 with interpolate(U) linear
    for lvl in (1, 2, 3, 4):
        out.append(dict(id=f"ma-cav-qm-L{lvl}", item="2a", case="cav",
                        level=lvl, vst="no", interp="skewCorrected linear",
                        ranks=4 if lvl == 4 else 1))
    for lvl in (2, 3):
        out.append(dict(id=f"ma-cav-qm-L{lvl}-interplinear", item="2b",
                        case="cav", level=lvl, vst="no", interp="linear",
                        ranks=1))
    # 5b: blob QM x1 time-step study to t = 1 s (tight tolerances: the
    # changes at the finest steps are ~1e-5 m)
    for dt in (0.25, 0.125, 0.0625, 0.03125):
        out.append(dict(id=f"ma-blob-qm-x1-dt{dt:g}", item="5b", case="blob",
                        level=1, dt=dt, end_time=1.0, vst="no", petsc=TIGHT,
                        ranks=1))
    # 1b: ring QM with a zeroGradient interface pressure
    for lvl in ("moderate", "strong"):
        for f in (1, 2, 4):
            out.append(dict(id=f"ma-ram-qm-{lvl}-m{f}-n100-pzg", item="1b",
                            case="ram", kind="wet", level=lvl,
                            coupling="monolithic", solid="standard",
                            factor=f, steps=100, vst="no", petsc={},
                            p_interface="zeroGradient", ranks=1))
    # 1c: ring QM non-conformal (AMI), solid coarser (32) and finer (72
    # circumferential cells per factor; fluid 48), interpolated and
    # conservative traction transfer; conformal baseline in 1a (n100)
    for f in (1, 2, 4):
        for nc in (32 * f, 72 * f):
            out.append(dict(id=f"ma-ram-dry-m{f}-n100-nc{nc}", item="1c",
                            case="ram", kind="dry", solid="standard",
                            factor=f, steps=100, solidCells=nc, ranks=1))
            for lvl in ("weak", "moderate", "strong"):
                for cons in ("no", "yes"):
                    tag = "cons" if cons == "yes" else "interp"
                    out.append(dict(
                        id=f"ma-ram-qm-{lvl}-m{f}-n100-nc{nc}-{tag}",
                        item="1c", case="ram", kind="wet", level=lvl,
                        coupling="monolithic", solid="standard", factor=f,
                        steps=100, solidCells=nc, vst="no", petsc={},
                        conservative=cons, ranks=1))
    for r in out:
        r["batch"] = 2
    return (out + definitions3() + definitions4()
            + definitions4(prefix="mafinal", batch=5)
            + definitions4(prefix="mafinal4", batch=6)
            + (definitionsRfix() + definitionsTiming() if rfix else []))


def definitionsRfix():
    """R-fix reruns (#618 + #617 merged, 1252bd2e5): every QM run of agent
    A with the tutorials' own schemes and no viscousStressTranspose entry
    (the term is always on). Partitioned runs are not repeated."""
    out = []
    base = [r for r in definitions(rfix=False)
            if r.get("batch") in (1, 2)
            and (r["case"] in ("cav", "blob")
                 or r.get("kind") == "dry"
                 or r.get("coupling") == "monolithic")]
    seen = set()
    for r in base:
        r = dict(r)
        rid = r["id"].replace("ma-", "rf-", 1).replace("-vstno", "")
        if "-vstyes" in rid or rid in seen:
            continue
        seen.add(rid)
        r.update(id=rid, batch=7, tutorial_schemes=True)
        if "vst" in r:
            r["vst"] = None
        out.append(r)
    # Womersley m2 n50 (WP0 cell)
    out.append(dict(id="rf-wom-qm-m2-n50", item="1e", case="wom",
                    coupling="monolithic", factor=2, steps=50, vst=None,
                    petsc=TIGHT, ranks=1, batch=7, tutorial_schemes=True))
    # blob steady x1/x2/x4 (0b/5a), as WP0: dt 0.01/0.01/0.005 to 3 s
    for lvl, dt, np in ((1, 0.01, 1), (2, 0.01, 2), (4, 0.005, 4)):
        out.append(dict(id=f"rf-blob-qm-x{lvl}", item="5a", case="blob",
                        level=lvl, dt=dt, end_time=3.0, vst=None, petsc={},
                        ranks=np, batch=7, tutorial_schemes=True))
    return out


def definitionsTiming(repeats=3):
    """Timing rows (batch 8, Mx exclusive node): 1d ring strong m2
    n25/50/100 QM, IQN-ILS, RN and 2a cavity L1-L4 QM and Aitken, each the
    exact definition of its accuracy run (QM: R-fix batch 7; partitioned:
    batches 1 and 3), repeated; run with --pin."""
    base = definitions(rfix=False)
    rfix = definitionsRfix()
    pick = ([r for r in rfix if r["case"] == "cav" and r["item"] == "2a"]
            + [r for r in rfix if r["case"] == "ram"
               and r.get("kind") == "wet" and r.get("level") == "strong"
               and r["factor"] == 2 and r["steps"] in (25, 50, 100)
               and r["item"] == "1a" and "tight" not in r["id"]]
            + [r for r in base if r["item"] == "1d"]
            + [r for r in base if r["item"] == "2c"])
    out = []
    for k in range(1, repeats + 1):
        for r in pick:
            r = dict(r)
            rid = re.sub(r"^(ma|rf)-", "tm-", r["id"])
            item = "2a" if r["case"] in ("cav", "cavpart") else "1d"
            r.update(id=f"{rid}-r{k}", item=f"{item} timing", batch=8)
            out.append(r)
    return out


def definitions4(prefix="mafix", batch=4):
    """Verification of the vST fix build (transpose always on, also in the
    wall pressure gradient): Womersley m1/m2/m4 n200 (against the head RN
    runs of 1e) and ring QM n100, 3 levels x mesh 1/2/4 (against 1a; the
    dry rings of 1a are unchanged by the fluid fix)."""
    out = []
    for f in (1, 2, 4):
        out.append(dict(id=f"{prefix}-wom-qm-m{f}-n200", item="fix",
                        case="wom", coupling="monolithic", factor=f,
                        steps=200, vst=None, petsc=TIGHT))
        for lvl in ("weak", "moderate", "strong"):
            out.append(dict(id=f"{prefix}-ram-qm-{lvl}-m{f}-n100", item="fix",
                            case="ram", kind="wet", level=lvl,
                            coupling="monolithic", solid="standard",
                            factor=f, steps=100, vst=None, petsc={}))
    for r in out:
        r.update(ranks=1, batch=batch)
    return out


def definitions3():
    """2c: partitioned (Aitken, strict) cavity L1-L4 at the head, as the
    README's partitioned_strict rows, for checkMesh on the final states."""
    out = []
    for lvl, dt in ((1, 0.5), (2, 0.25), (3, 0.125), (4, 0.0625)):
        out.append(dict(id=f"ma-cav-aitken-L{lvl}", item="2c", case="cavpart",
                        level=lvl, dt=dt, end_time=200.0,
                        n_outer=40 if lvl == 4 else 20,
                        fluid_tol="1e-08" if lvl == 4 else None,
                        ranks=4 if lvl == 4 else 1, batch=3))
    return out


def cost(r):
    """Rough relative cost, to start the long runs first."""
    if r["case"] in ("cav", "cavpart"):
        return 4 ** r["level"] * 1000
    if r["case"] == "blob":
        return 100 / r["dt"]
    c = r["factor"] ** 2 * r["steps"]
    if r["case"] == "wom":
        c *= 6
    if r.get("coupling") in ("iqnils", "robin"):
        c *= 3
    return c


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

PIN = threading.local()   # cores of the current run (--pin), or None


def run_cmd(cmd, case, log_name):
    cpus = getattr(PIN, "cpus", None)
    if cpus:
        cmd = ["taskset", "-c", cpus] + list(cmd)
    with (case / log_name).open("w") as log:
        t0 = time.time()
        res = subprocess.run(cmd, cwd=case, stdout=log,
                             stderr=subprocess.STDOUT)
        return res.returncode, time.time() - t0


def ksp_per_newton(case):
    text = (case / "log.solids4Foam").read_text(errors="replace")
    k = [int(n) for n in re.findall(
        r"Linear solve converged due to \w+ iterations (\d+)", text)]
    return sum(k) / len(k) if k else None


def run_ram(ctx, r):
    ram = ctx["ram"]
    ref = ctx["ram_ref"]
    exact = ref["exact"]
    omega = exact["dry"]["omega"] if r["kind"] == "dry" \
        else exact["levels"][r["level"]]["omega"]
    periods = ref["study"]["periods"]
    spec = {"kind": r["kind"], "level": r.get("level", ""),
            "coupling": r.get("coupling", ""), "solid": r["solid"],
            "factor": r["factor"], "steps": r["steps"], "periods": periods,
            "omega_exact": omega, "period": 2 * 3.141592653589793 / omega,
            "name": r["id"]}
    if r.get("solidCells"):
        spec["solidCells"] = r["solidCells"]
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    ram.configure(case, spec, ref)
    cmd = ["./Allrun"]
    if r["kind"] == "wet":
        cmd += [r["coupling"], r["solid"]]
        if r["coupling"] == "monolithic":
            if r["vst"] is not None:
                set_vst(case, r["vst"])
            set_petsc(case, r["petsc"])
            if r.get("p_interface") == "zeroGradient":
                sub1(case / "0/fluid/p.monolithic",
                     r"(interface\s*\{[^}]*?)type\s+fixedGradient;\s*"
                     r"gradient\s+uniform 0;",
                     r"\g<1>type            zeroGradient;")
            if r.get("conservative"):
                sub1(case / "constant/fsiProperties.monolithic",
                     r"(^\s*passViscousStress\s+\w+;\n)",
                     rf"\g<1>    conservativeTractionTransfer "
                     rf"{r['conservative']};\n")
        else:
            set_partitioned(case, r["coupling"])
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    log = case / "log.solids4Foam"
    text = log.read_text(errors="replace") if log.is_file() else ""
    if re.search(r"FOAM FATAL|FOAM aborting", text) or \
            not re.search(r"^End\s*$", text, re.MULTILINE):
        raise RuntimeError(f"solver did not complete (rc {rc})")
    row = ram.analyse(spec)
    row.update(wall_s=wall, ksp_per_newton_mean=ksp_per_newton(case))
    return case, row


def run_wom(ctx, r):
    wom = ctx["wom"]
    ref = ctx["wom_ref"]
    spec = {"coupling": r["coupling"], "factor": r["factor"],
            "steps": r["steps"], "name": r["id"]}
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    wom.configure(case, spec, ref)
    if r["coupling"] == "monolithic":
        if r["vst"] is not None:
            set_vst(case, r["vst"])
        set_petsc(case, r["petsc"])
    else:
        set_partitioned(case, r["coupling"])
    rc, wall = run_cmd(["./Allrun", r["coupling"]], case, "log.Allrun")
    problem = wom.solver_log_problem(case)
    if problem:
        raise RuntimeError(f"{problem} (rc {rc})")
    row = wom.analyse(spec, ref)
    row.pop("_profile", None)
    row.update(wall_s=wall, ksp_per_newton_mean=ksp_per_newton(case))
    return case, row


def newton_counts(text):
    return [int(n) for n in re.findall(
        r"^Solving the monolithic momentum-continuity system.*?"
        r"Nonlinear solve \w+ due to \w+ iterations (\d+)",
        text, re.MULTILINE | re.DOTALL)]


def time_to_steady(history, rel):
    """First time after which the value stays within rel of the final."""
    final = history[-1][1]
    t_ss = history[0][0]
    for t, v in history:
        if abs(v - final) > rel * abs(final):
            t_ss = t
    return t_ss


def run_cav(ctx, r):
    cav = ctx["cav"]
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(cav.CASE_DIR, case, ignore=cav.ignored, symlinks=True)
    factor = 2 ** (r["level"] - 1)
    cav.refine_mesh(case / "system/fluid/blockMeshDict", factor)
    cav.refine_mesh(case / "system/solid/blockMeshDict", factor)
    cav.set_control(case, "endTime", 300.0)
    cav.set_control(case, "deltaT", 0.5)
    cav.ramp_inlet(case, 20.0)
    if r["vst"] is not None:
        set_vst(case, r["vst"])
    schemes = case / "system/fluid/fvSchemes.monolithic"
    # Same schemes as the partitioned fvSchemes (no limiter; #553)
    if not r.get("tutorial_schemes"):
        sub1(schemes, r"(^\s*div\(phi,U\)\s+)[^;]+;",
             r"\g<1>Gauss linearUpwind grad(U);")
    sub1(schemes, r"(^\s*interpolate\(U\)\s+)[^;]+;",
         rf"\g<1>{r['interp']};")
    cmd = ["./Allrun", "monolithic"]
    if r["ranks"] > 1:
        for d in (case / "system").rglob("decomposeParDict*"):
            text = re.sub(r"(numberOfSubdomains\s+)\d+;",
                          rf"\g<1>{r['ranks']};", d.read_text())
            d.write_text(text)
        # Fluid mesh motion: redundant LU in parallel (as the #597 L4 run)
        mm = case / "system/fluid/fvSolution.monolithic"
        sub1(mm, r"(^\s*pc_type\s+)bjacobi;", r"\g<1>redundant;")
        sub1(mm, r"(^\s*)sub_pc_type(\s+)lu;", r"\g<1>redundant_pc_type\g<2>lu;")
        cmd.append("parallel")
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    cav.check_solver_log(case / "log.solids4Foam", 300.0, r["id"])
    disp = cav.read_displacement_history(case)
    force = cav.read_force_history(case)
    uy, uy_spread = cav.steady_value(disp, 0.1)
    fy, fy_spread = cav.steady_value(force, 0.1)
    text = (case / "log.solids4Foam").read_text(errors="replace")
    n = newton_counts(text)
    times = [float(t) for t in re.findall(r"^Time = ([0-9.eE+-]+)", text,
                                          re.MULTILINE)]
    out = dict(uy=uy, uy_spread=uy_spread, fy=fy, fy_spread=fy_spread,
               wall_s=wall, n_steps=len(n), iters_mean=sum(n) / len(n),
               iters_max=max(n), newton_total=sum(n),
               ksp_per_newton_mean=ksp_per_newton(case))
    clock = re.findall(r"ClockTime\s*=\s*([0-9.eE+-]+)", text)
    out["clock_s"] = float(clock[-1]) if clock else None
    for rel in (1e-3, 1e-4):
        t_ss = time_to_steady(disp, rel)
        k = sum(1 for t in times if t <= t_ss + 1e-9)
        out[f"t_steady_{rel:g}"] = t_ss
        out[f"newton_to_steady_{rel:g}"] = sum(n[:k])
        out[f"steps_to_steady_{rel:g}"] = k
    return case, out


def check_mesh(case):
    out = {}
    for region in ("fluid", "solid"):
        for when, flag in (("constant", "-constant"), ("final", "-latestTime")):
            res = subprocess.run(["checkMesh", "-region", region, flag],
                                 cwd=case, capture_output=True, text=True)
            (case / f"log.checkMesh.{region}.{when}").write_text(res.stdout)
            # -constant also loops over the time directories that hold a
            # mesh: keep the first block, which is the constant mesh
            text = res.stdout
            if when == "constant":
                blocks = text.split("\nTime = ")
                text = blocks[1] if len(blocks) > 2 else text
            sk = re.findall(r"Max skewness = ([0-9.eE+-]+)", text)
            no = re.findall(r"Mesh non-orthogonality Max: ([0-9.eE+-]+) "
                            r"average: ([0-9.eE+-]+)", text)
            pick = (lambda v: v[0]) if when == "constant" else (lambda v: v[-1])
            out[f"{region}_{when}"] = dict(
                max_skewness=float(pick(sk)) if sk else None,
                max_nonortho=float(pick(no)[0]) if no else None,
                avg_nonortho=float(pick(no)[1]) if no else None,
                ok="Failed" not in text)
    return out


def run_cavpart(ctx, r):
    cav = ctx["cav"]
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(cav.CASE_DIR, case, ignore=cav.ignored, symlinks=True)
    factor = 2 ** (r["level"] - 1)
    cav.refine_mesh(case / "system/fluid/blockMeshDict", factor)
    cav.refine_mesh(case / "system/solid/blockMeshDict", factor)
    cav.set_control(case, "endTime", r["end_time"])
    cav.set_control(case, "deltaT", r["dt"])
    fsi = case / "constant/fsiProperties"
    sub1(fsi, r"(^\s*writeResidualsToFile\s+yes;\n)",
         r"\g<1>    requireAllResidualMeasures yes;\n")
    sub1(fsi, r"(^\s*nOuterCorr\s+)\d+;", rf"\g<1>{r['n_outer']};")
    if r.get("fluid_tol"):
        path = case / "system/fluid/fvSolution"
        text, n = re.subn(r"(^\s*tolerance\s+)1e-0?6;",
                          rf"\g<1>{r['fluid_tol']};", path.read_text(),
                          flags=re.MULTILINE)
        if n < 3:
            raise RuntimeError(f"expected 3 fluid tolerances, found {n}")
        path.write_text(text)
    cmd = ["./Allrun"]
    if r["ranks"] > 1:
        for d in (case / "system").rglob("decomposeParDict*"):
            d.write_text(re.sub(r"(numberOfSubdomains\s+)\d+;",
                                rf"\g<1>{r['ranks']};", d.read_text()))
        cmd.append("parallel")
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    cav.check_solver_log(case / "log.solids4Foam", r["end_time"], r["id"])
    uy, uy_spread = cav.steady_value(cav.read_displacement_history(case), 0.1)
    fy, fy_spread = cav.steady_value(cav.read_force_history(case), 0.1)
    per = {}
    for line in (case / "postProcessing/fsiResiduals.dat").read_text().splitlines()[1:]:
        f = line.split()
        if len(f) >= 2:
            per[f[0]] = max(per.get(f[0], 0), int(f[1]))
    n = list(per.values())
    out = dict(uy=uy, uy_spread=uy_spread, fy=fy, fy_spread=fy_spread,
               wall_s=wall, n_steps=len(n), iters_mean=sum(n) / len(n),
               iters_max=max(n), iters_mean_last10=sum(n[-len(n) // 10:])
               / len(n[-len(n) // 10:]), checkmesh=check_mesh(case))
    return case, out


def run_blob(ctx, r):
    blob = ctx["blob"]
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(blob.CASE_DIR, case, ignore=blob.ignored, symlinks=True)
    if r.get("level", 1) != 1:
        for region in ("fluid", "solid"):
            blob.refine_mesh(case / "system" / region / "blockMeshDict",
                             r["level"])
    control = case / "system/controlDict"
    blob.set_entry(control, "endTime", f"{r['end_time']:.10g}")
    blob.set_entry(control, "deltaT", f"{r['dt']:.10g}")
    if not r.get("tutorial_schemes"):
        sub1(case / "system/fluid/fvSchemes.monolithic",
             r"(ddt\(U\)\s+)Euler;", r"\g<1>backward;")
        sub1(case / "system/fluid/fvSchemes.monolithic",
             r"(^\s*div\(phi,U\)\s+)[^;]+;",
             r"\g<1>Gauss linearUpwind grad(U);")
    if r.get("p_interface") == "zeroGradient":
        sub1(case / "0/fluid/p.monolithic",
             r"(interface\s*\{[^}]*?)type\s+fixedGradient;\s*"
             r"gradient\s+uniform 0;", r"\g<1>type            zeroGradient;")
    if r.get("interp"):
        sub1(case / "system/fluid/fvSchemes.monolithic",
             r"(^\s*interpolate\(U\)\s+)[^;]+;", rf"\g<1>{r['interp']};")
    for key, value in r.get("fluid_props", {}).items():
        sub1(case / "constant/fluid/fluidProperties.monolithic",
             r"(newtonIcoFluidCoeffs\s*\{\n)", rf"\g<1>    {key} {value};\n")
    if r["vst"] is not None:
        set_vst(case, r["vst"])
    set_petsc(case, r["petsc"])
    cmd = ["./Allrun", "monolithic"]
    if r["ranks"] > 1:
        blob.set_cores(case, r["ranks"])
        cmd.append("parallel")
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    blob.check_solver_log(case / "log.solids4Foam", r["end_time"], r["id"])
    hist = blob.displacement_history(case)
    _, ux, uy = blob.value_at(hist, r["end_time"])
    try:
        pts = [list(v) for v in blob.interface_vertices(case, r["end_time"])]
    except RuntimeError:
        pts = []
    text = (case / "log.solids4Foam").read_text(errors="replace")
    n = newton_counts(text)
    out = dict(ux=ux, uy=uy, interface_vertices=pts, wall_s=wall,
               n_steps=len(n), iters_mean=sum(n) / len(n), iters_max=max(n),
               ksp_per_newton_mean=ksp_per_newton(case))
    return case, out


def execute(ctx, r):
    case = ctx["runs"] / r["id"]
    try:
        case, out = {"ram": run_ram, "wom": run_wom, "cav": run_cav,
                     "cavpart": run_cavpart,
                     "blob": run_blob}[r["case"]](ctx, r)
        out["status"] = "completed"
        log = case / "log.solids4Foam"
        if log.is_file():
            text = log.read_text(errors="replace")
            for key, word in (("solver_clock_s", "ClockTime"),
                              ("solver_exec_s", "ExecutionTime")):
                v = re.findall(rf"{word}\s*=\s*([0-9.eE+-]+)", text)
                out[key] = float(v[-1]) if v else None
        out["cpus"] = getattr(PIN, "cpus", None)
    except Exception as error:  # record and carry on
        out = {"status": "failed", "error": str(error),
               "traceback": traceback.format_exc()}
    out["run_id"] = r["id"]
    out["def"] = r
    if case.is_dir():
        subprocess.run([sys.executable, str(ctx["provenance"]), str(case),
                        "--ranks", str(r["ranks"]), "--run-id", r["id"],
                        "--s4f", str(ctx["s4f"])],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (case / "ma_result.json").write_text(
            json.dumps(out, indent=2, default=str))
    print(f"{time.strftime('%H:%M:%S')} {r['id']}: {out['status']}",
          flush=True)


def run_pinned(ctx, todo, starts, width):
    """One run per slot; a slot is `width` consecutive cores from each start
    (one core complex), and every run gets the whole slot as its mask: a
    run pinned to as many cores as ranks shares them with the MPI helper
    process, which costs clock time outside the solver's CPU time."""
    import queue
    free = queue.Queue()
    for c in starts:
        free.put(c)
    threads = []

    def worker(r, c):
        PIN.cpus = f"{c}-{c + width - 1}"
        try:
            execute(ctx, r)
        finally:
            free.put(c)

    for r in todo:
        if r["ranks"] > width:
            raise SystemExit(f"{r['id']}: {r['ranks']} ranks > slot width")
        c = free.get()
        print(f"{time.strftime('%H:%M:%S')} start {r['id']} on core {c}",
              flush=True)
        t = threading.Thread(target=worker, args=(r, c))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s4f", required=True, type=Path)
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--provenance", type=Path,
                    default=HERE / "provenance.py")
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--only")
    ap.add_argument("--batch", type=int)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--pin", help="first cores of the pinning slots, e.g. "
                    "0,16,32 (one run per slot; replaces --cores)")
    ap.add_argument("--slot-width", type=int, default=4)
    args = ap.parse_args()
    todo = definitions()
    if args.batch:
        todo = [r for r in todo if r["batch"] == args.batch]
    if args.only:
        keep = set(args.only.split(","))
        todo = [r for r in todo if r["id"] in keep]
    if args.list:
        for r in todo:
            print(r["item"], r["id"])
        print(len(todo), "runs")
        return
    fsi = args.s4f / "tutorials" / "fluidSolidInteraction"
    ram = load("ramdrv", fsi / "ringAddedMass/verification/scripts/"
               "ring_added_mass_verification.py")
    wom = load("womdrv", fsi / "womersleyTube/verification/scripts/"
               "womersley_tube_verification.py")
    cav = load("cavdrv", fsi / "cavityFlexibleBottom/verification/scripts/"
               "cavity_flexible_bottom_verification.py")
    blob = load("blobdrv", fsi / "blobInTreacle/verification/scripts/"
                "blob_in_treacle_verification.py")
    args.runs.mkdir(parents=True, exist_ok=True)
    ram.WORK_ROOT = args.runs
    wom.WORK_ROOT = args.runs
    ctx = dict(ram=ram, wom=wom, cav=cav, blob=blob, runs=args.runs,
               s4f=args.s4f,
               provenance=args.provenance,
               ram_ref=json.loads(ram.REFERENCE_FILE.read_text()),
               wom_ref=json.loads(wom.REFERENCE_FILE.read_text()))
    todo = sorted(todo, key=lambda r: -cost(r))
    threads = []
    if args.pin:
        run_pinned(ctx, todo, [int(c) for c in args.pin.split(",")],
                   args.slot_width)
        return
    sem = threading.Semaphore(args.cores)

    def worker(r):
        try:
            execute(ctx, r)
        finally:
            for _ in range(r["ranks"]):
                sem.release()

    # Only this loop acquires, so multi-rank runs cannot deadlock
    for r in todo:
        for _ in range(r["ranks"]):
            sem.acquire()
        print(f"{time.strftime('%H:%M:%S')} start {r['id']}", flush=True)
        t = threading.Thread(target=worker, args=(r,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
