#!/usr/bin/env python3
"""R0: build runs.csv and qois.csv from the per-run records.

Usage:
    r0_collect.py <records_dir> <out_dir>

<records_dir> holds, per run, <run_id>/r0_summary.json (r0_post.py),
<run_id>/provenance.json (provenance.py) and <run_id>/cells.json (cell
counts read from the polyMesh owner headers), copied from MeluXina.
Writes <out_dir>/runs.csv (HANDOFF Section 6 columns plus ddt_U, solid_pc,
cores), <out_dir>/qois.csv and <out_dir>/provenance/<run_id>.json.
"""

import csv
import json
import shutil
import sys
from pathlib import Path

COLS = ["run_id", "stream", "case", "study", "coupling", "scheme", "level",
        "fluid_cells", "solid_cells", "interface", "dt", "rho_ratio", "ranks",
        "cores", "nodes", "node_type", "exclusive", "code_commit", "tag",
        "of_version", "petsc_version", "hypre_version", "compiler",
        "compile_flags", "snes_rtol", "snes_stol", "ksp_rtol", "coupling_tol",
        "convergence_test", "solid_pc", "ddt_U", "status", "t_end", "n_steps",
        "iters_mean", "iters_max", "ksp_per_newton_mean", "wall_s",
        "wall_s_per_step", "core_h", "core_h_per_sim_s", "peak_mem_gb",
        "window", "repeats", "notes"]

# Per case: level label, dt, interface, notes on schemes (HANDOFF Section 4
# "Schemes"), from the tutorial files at the head
CASE_INFO = {
    "ram": ("tutorial (factor 1), moderate rho_f=140", 0.035, "conformal"),
    "wom": ("tutorial (m2)", 0.5, "conformal"),
    "coll": ("tutorial fluid L1, solid 80x8", 0.025, "conformal"),
    "cav": ("tutorial L1", 0.5, "conformal"),
    "blob": ("tutorial x1", 0.01, "conformal"),
    "foil": ("tutorial", 0.0025, "conformal"),
    "tube": ("driver level 1 (tutorial mesh)", 2.5e-5, "conformal"),
    "fsi3": ("driver conformal 1x", 1e-3, "conformal (monolithic meshes)"),
    "fsi1": ("driver conformal 1x", 0.025, "conformal (monolithic meshes)"),
}


def find_opts(prov):
    """The monolithic SNES options block among the recorded fvSolution
    options: the one with a fieldsplit preconditioner."""
    found = {}
    for f, blocks in (prov.get("petsc_options") or {}).items():
        for name, opts in (blocks or {}).items():
            if isinstance(opts, dict) and opts.get("pc_type") == "fieldsplit":
                if "fieldsplit_solid_pc_type" in opts:
                    return opts
                found = found or opts
    return found


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    (out / "provenance").mkdir(parents=True, exist_ok=True)
    runs, qois = [], []
    for d in sorted(p for p in src.iterdir() if p.is_dir()):
        s = json.load(open(d / "r0_summary.json"))
        prov = json.load(open(d / "provenance.json")) \
            if (d / "provenance.json").is_file() else {}
        cells = json.load(open(d / "cells.json")) \
            if (d / "cells.json").is_file() else {}
        if prov:
            shutil.copy(d / "provenance.json",
                        out / "provenance" / f"{s['run_id']}.json")
        meta = s.get("meta") or {}
        key = s.get("key")
        level, dt, iface = CASE_INFO.get(key, ("", "", ""))
        o = find_opts(prov)
        solid_pc = o.get("fieldsplit_solid_pc_type", "")
        if solid_pc == "redundant":
            solid_pc += "+" + o.get("fieldsplit_solid_redundant_pc_type", "")
        elif solid_pc == "hypre":
            solid_pc += "/" + o.get("fieldsplit_solid_pc_hypre_type", "")
        lib = prov.get("libraries") or {}
        comp = prov.get("compiler") or {}
        ranks = meta.get("ranks")
        wall = meta.get("wall_s")
        steps = s.get("n_steps") or 0
        t_end = s.get("t_last")
        cores_n = ranks or 1
        core_h = round(wall * cores_n / 3600, 4) if wall else ""
        notes = list(s.get("edits") or [])
        notes.append(f"core range {meta.get('cores')}")
        if s.get("snes_not_converged"):
            notes.append(f"SNES not converged in {s['snes_not_converged']} "
                         f"steps: {s.get('snes_fail_reasons')}")
        if s.get("fatal"):
            notes.append("fatal: " + s["fatal"])
        if meta.get("rc") not in (0, None):
            notes.append(f"Allrun/driver rc {meta.get('rc')}")
        runs.append({
            "run_id": s["run_id"], "stream": "r0", "case": s.get("case"),
            "study": "R0 runs-at-head", "coupling": "NewtonQuasiMonolithic",
            "scheme": "quasi-monolithic JFNK", "level": level,
            "fluid_cells": cells.get("fluid", ""),
            "solid_cells": cells.get("solid", ""), "interface": iface,
            "dt": dt, "rho_ratio": "", "ranks": ranks,
            "cores": meta.get("cores"), "nodes": 1,
            "node_type": f"MeluXina cpu ({prov.get('cpu_model', '')})",
            "exclusive": "node exclusive, shared by the R0 farm",
            "code_commit": (prov.get("solids4foam") or {}).get("describe", ""),
            "tag": "",
            "of_version": (prov.get("openfoam") or {}).get("version", ""),
            "petsc_version": lib.get("petsc_version", ""),
            "hypre_version": lib.get("hypre_version", ""),
            "compiler": comp.get("compiler_version", ""),
            "compile_flags": comp.get("compile_flags", ""),
            "snes_rtol": o.get("snes_rtol", ""),
            "snes_stol": o.get("snes_stol", ""),
            "ksp_rtol": o.get("ksp_rtol", ""), "coupling_tol": "",
            "convergence_test": "SNES rtol/stol", "solid_pc": solid_pc,
            "ddt_U": meta.get("ddt_U", ""), "status": s.get("status"),
            "t_end": t_end, "n_steps": steps,
            "iters_mean": s.get("iters_mean"), "iters_max": s.get("iters_max"),
            "ksp_per_newton_mean": s.get("ksp_per_newton_mean"),
            "wall_s": wall,
            "wall_s_per_step": round(wall / steps, 3) if wall and steps else "",
            "core_h": core_h,
            "core_h_per_sim_s": round(core_h / float(t_end), 4)
            if core_h and t_end and float(t_end) > 0 else "",
            "peak_mem_gb": s.get("peak_mem_gb") or "", "window": "full run",
            "repeats": 1, "notes": "; ".join(notes)})
        for q in s.get("qois") or []:
            name, val, ref, refsrc, note = q
            rel = (val / ref - 1) if (ref not in (None, 0) and val is not None
                                       and not name.endswith("_err")) else ""
            qois.append({"run_id": s["run_id"], "qoi": name, "value": val,
                         "reference": "" if ref is None else ref,
                         "reference_source": refsrc,
                         "rel_error": rel if rel == "" else f"{rel:.4e}",
                         "uncertainty_of_reference": "", "notes": note})
    with open(out / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(runs)
    with open(out / "qois.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["run_id", "qoi", "value", "reference",
                                          "reference_source", "rel_error",
                                          "uncertainty_of_reference", "notes"])
        w.writeheader()
        w.writerows(qois)
    print(f"{len(runs)} runs, {len(qois)} QoI rows")


if __name__ == "__main__":
    main()
