#!/usr/bin/env python3
"""R4/R5: build runs.csv, qois.csv and provenance/ from the run records.

Usage:  collect.py RECORDS_DIR OUT_DIR --stream r4|r5 [--registry FILE]

RECORDS_DIR/<run_id>/ holds, copied from MeluXina (fetch_records.sh):
qm_run.json (qm_setup.py), run_meta.json (run_task.sh), provenance.json
(campaign/scripts/provenance.py), qm_result.json (qm_post.py);
RECORDS_DIR/farm_state.*.json hold the per-run peak memory (farm.py).
--registry: a CSV (run_id, study, window, repeats, notes, status_override)
with the study label and notes of every planned run, so that planned runs
without records still get a row (status 'not run' or the override).

Columns: HANDOFF Section 6 plus cores, ddt_U and (R4) lift smoothing.
Every value comes from the records; nothing is typed in here except the
reference values, which are read from the drivers' reference JSON copies
stored with the records (qm_result.json "reference").
"""

import argparse
import csv
import json
import math
import shutil
from pathlib import Path

COLS = ["run_id", "stream", "case", "study", "coupling", "scheme", "level",
        "fluid_cells", "solid_cells", "interface", "dt", "rho_ratio", "ranks",
        "cores", "nodes", "node_type", "exclusive", "code_commit", "tag",
        "of_version", "petsc_version", "hypre_version", "compiler",
        "compile_flags", "snes_rtol", "snes_stol", "ksp_rtol", "coupling_tol",
        "convergence_test", "solid_pc", "ddt_U", "status", "t_start", "t_end",
        "n_steps", "iters_mean", "iters_max", "ksp_per_newton_mean", "wall_s",
        "wall_s_per_step", "core_h", "core_h_per_sim_s", "peak_mem_gb",
        "window", "repeats", "notes"]

# Tutorial cell counts at refinement factor 1 (conformal FSI3 meshes:
# TurekHron2006 system/*/blockMeshDict.monolithic; 3dTube README table)
CELLS = {"TurekHron2006": (1859, 150, 2), "3dTube": (16000, 6400, 3)}
SCHEMES = {
    "TurekHron2006": "fluid ddt backward, div(phi,U) Gauss linearUpwind "
                     "grad(U), interpolate(U) skewCorrected linear; solid "
                     "backward; monolithic solid stabilisation "
                     "diffStencilLaplacian 0.5",
    "3dTube": "fluid and solid ddt/d2dt2 backward (driver), tutorial "
              "convection and stabilisation schemes",
}
FSI3_QOIS = ["ux_mean", "ux_amplitude", "uy_amplitude", "uy_frequency",
             "drag_mean", "drag_amplitude", "lift_amplitude",
             "lift_amplitude_smoothed", "ux_frequency", "uy_mean", "lift_mean"]
TUBE_QOIS = ["ur_max_A_m", "t_ur_max_A_s", "uz_min_A_m", "t_arrival_A_s",
             "wave_speed_pressure_m_s", "ur_min_late_A_m"]


def jl(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, ValueError):
        return {}


def fmt(v):
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return ""
    if isinstance(v, float):
        return f"{v:.6g}"
    return v


def mono_opts(prov):
    for f, blocks in (prov.get("petsc_options") or {}).items():
        for name, opts in (blocks or {}).items():
            if isinstance(opts, dict) and "fieldsplit_solid_pc_type" in opts:
                return opts
    return {}


def peaks(records):
    out = {}
    for f in records.rglob("farm_state.*.json"):
        for cwd, kb in (jl(f).get("mem_peak_kb") or {}).items():
            rid = Path(cwd).name
            out[rid] = max(out.get(rid, 0), kb)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("records")
    ap.add_argument("out")
    ap.add_argument("--stream", required=True)
    ap.add_argument("--registry")
    args = ap.parse_args()
    rec, out = Path(args.records), Path(args.out)
    (out / "provenance").mkdir(parents=True, exist_ok=True)
    reg = {}
    if args.registry:
        with open(args.registry) as f:
            for r in csv.DictReader(f):
                reg[r["run_id"]] = r
    mem = peaks(rec)
    rows, qrows = [], []
    ids = sorted({p.name for p in rec.iterdir() if p.is_dir()} | set(reg))
    for rid in ids:
        d = rec / rid
        run, meta = jl(d / "qm_run.json"), jl(d / "run_meta.json")
        prov, res = jl(d / "provenance.json"), jl(d / "qm_result.json")
        r = reg.get(rid, {})
        if not run:
            rows.append({"run_id": rid, "stream": args.stream,
                         "study": r.get("study", ""),
                         "status": r.get("status_override") or "not run",
                         "notes": r.get("notes", "")})
            continue
        case = run["case"]
        f1, s1, dim = CELLS[case]
        fac = run.get("factor", run["level"])
        tol = run.get("tol", {})
        mono = run["coupling"] == "NewtonQuasiMonolithic"
        opts = mono_opts(prov) if mono else {}
        lib = prov.get("libraries", {})
        comp = prov.get("compiler", {})
        it = res.get("iterations", {})
        tm = res.get("timing", {})
        ranks = int(run["ranks"])
        wall = meta.get("solver_wall_s")
        t0 = float(run.get("t_start", 0.0))
        dt = float(run["dt"])
        status = res.get("status") or ("failed (rc %s)" % meta.get("rc")
                                       if meta else "not run")
        if r.get("status_override"):
            status = r["status_override"]
        if mono:
            conv = "SNES rtol/stol"
            ctol = ""
        else:
            conv = ("strict (requireAllResidualMeasures yes)"
                    if case == "TurekHron2006" else
                    "Robin: displacement, pressure-change, leakage-flux")
            ctol = tol.get("ctol", 1e-5 if case == "TurekHron2006" else "")
        cps = tm.get("clock_s_per_step")
        notes = "; ".join(run.get("edits", []))
        if not mono and tol:
            notes += "; inner: " + ", ".join(f"{k}={v:g}" for k, v in
                                               tol.items() if k != "ctol")
        if run.get("pc_variant"):
            notes += f"; PC variant {run['pc_variant']}"
        if r.get("notes"):
            notes += "; " + r["notes"]
        notes += "; " + SCHEMES[case]
        rows.append({
            "run_id": rid, "stream": args.stream, "case": case,
            "study": r.get("study", ""),
            "coupling": run["coupling"],
            "scheme": "quasi-monolithic JFNK" if mono else
            ("IQN-ILS" if run["coupling"] == "IQNILS" else "Robin-Neumann"),
            "level": f"{fac}x" if case == "TurekHron2006" else f"L{run['level']}",
            "fluid_cells": f1 * fac ** dim, "solid_cells": s1 * fac ** dim,
            "interface": "conformal" + (" (monolithic meshes)"
                                        if case == "TurekHron2006" else ""),
            "dt": dt, "rho_ratio": 1.0 if case == "TurekHron2006" else 1.2,
            "ranks": ranks, "cores": meta.get("cores", ""), "nodes": 1,
            "node_type": f"MeluXina cpu ({prov.get('cpu_model', '')})",
            "exclusive": "node exclusive, shared by own farm runs only; "
                         "one core per rank",
            "code_commit": (prov.get("solids4foam") or {}).get("describe", ""),
            "tag": "", "of_version": (prov.get("openfoam") or {}).get("version", ""),
            "petsc_version": lib.get("petsc_version", ""), "hypre_version": lib.get("hypre_version", ""),
            "compiler": comp.get("compiler_version", ""), "compile_flags": comp.get("compile_flags", ""),
            "snes_rtol": opts.get("snes_rtol", ""), "snes_stol": opts.get("snes_stol", ""),
            "ksp_rtol": opts.get("ksp_rtol", ""), "coupling_tol": ctol,
            "convergence_test": conv, "solid_pc": run.get("solid_pc", ""),
            "ddt_U": "backward", "status": status, "t_start": t0,
            "t_end": run["t_end"], "n_steps": it.get("n_steps"),
            "iters_mean": it.get("iters_mean"), "iters_max": it.get("iters_max"),
            "ksp_per_newton_mean": it.get("ksp_per_newton_mean"),
            "wall_s": wall, "wall_s_per_step": cps,
            "core_h": ranks * wall / 3600 if wall else None,
            "core_h_per_sim_s": ranks * cps / dt / 3600 if cps else None,
            "peak_mem_gb": mem.get(rid, 0) / 2**20 if rid in mem else None,
            "window": r.get("window") or (
                "coupled steps t > 2 s" if case == "TurekHron2006" and t0 < 2
                else f"all steps t = {t0:g}-{run['t_end']:g} s"),
            "repeats": r.get("repeats", 1), "notes": notes,
        })
        if prov:
            shutil.copy(d / "provenance.json", out / "provenance" / f"{rid}.json")
        q = res.get("qoi", {})
        refs = res.get("reference", {})
        names = FSI3_QOIS if case == "TurekHron2006" else TUBE_QOIS
        for name in names:
            if name not in q:
                continue
            refkey = "lift_amplitude" if name == "lift_amplitude_smoothed" else name
            ref = refs.get(refkey)
            qrows.append({
                "run_id": rid, "qoi": name, "value": q[name],
                "reference": ref if ref is not None else "",
                "reference_source": "Featflow FSI3 level 4+0, dt 0.00025 s "
                "(TurekHron2006 verification reference JSON)" if ref is not None
                else "",
                "rel_error": (q[name] - ref) / abs(ref) if ref else "",
                "uncertainty_of_reference": "category C (V: Featflow level-4 "
                "table; FSI2 levels 3-4 change 0.9-2.5%, ~1%)" if ref is not None
                else "",
                "notes": ("21-sample-equivalent 0.01 s centred moving average"
                          if name == "lift_amplitude_smoothed" else
                          "driver periodic statistics over the closing 1 s"
                          if case == "TurekHron2006" else
                          "3dTube driver extract()"),
            })
    with open(out / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        for row in rows:
            w.writerow({k: fmt(row.get(k)) for k in COLS})
    qc = ["run_id", "qoi", "value", "reference", "reference_source",
          "rel_error", "uncertainty_of_reference", "notes"]
    with open(out / "qois.csv", "w", newline="") as f:
        w = csv.DictWriter(f, qc)
        w.writeheader()
        for row in qrows:
            w.writerow({k: fmt(row.get(k)) for k in qc})
    print(f"{len(rows)} runs, {len(qrows)} QoI rows -> {out}")


if __name__ == "__main__":
    main()
