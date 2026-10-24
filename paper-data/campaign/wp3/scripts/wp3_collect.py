#!/usr/bin/env python3
"""Collect WP3 runs into runs.csv, qois.csv and provenance/<run_id>.json.

  wp3_collect.py RUNS_DIR OUT_DIR [--map 3a|3b] [--include-smoke]

Reads <run>/wp3_case.json (wp3_setup.py), wp3_result.json (wp3_post.py),
run_meta.json and provenance.json (wp3_farm.sh). Columns as HANDOFF §6
(plus cores and ddt_U, as WP0), with the WP3 extras status (failure
class) and t_reached in the notes.
"""
import os
import sys

if sys.version_info < (3, 9):
    for candidate in ("/usr/bin/python3.12", "/usr/bin/python3.11"):
        if os.access(candidate, os.X_OK):
            os.execv(candidate, [candidate] + sys.argv)

import argparse
import csv
import json
import re
from pathlib import Path

COLS = ("run_id,stream,case,study,coupling,scheme,level,fluid_cells,"
        "solid_cells,interface,dt,rho_ratio,ranks,cores,nodes,node_type,"
        "exclusive,code_commit,tag,of_version,petsc_version,hypre_version,"
        "compiler,compile_flags,snes_rtol,snes_stol,ksp_rtol,coupling_tol,"
        "convergence_test,solid_pc,ddt_U,status,t_end,n_steps,iters_mean,"
        "iters_max,ksp_per_newton_mean,wall_s,wall_s_per_step,core_h,"
        "core_h_per_sim_s,peak_mem_gb,window,repeats,notes").split(",")
QCOLS = ["run_id", "qoi", "value", "reference", "reference_source",
         "rel_error", "uncertainty_of_reference", "notes"]
COUPLING = {"aitken": "Aitken", "iqn": "IQNILS", "rn": "Robin-Neumann",
            "qm": "NewtonQuasiMonolithic"}


def g(x, fmt="{:.6g}"):
    return "" if x is None else fmt.format(x)


def ncells(case, region):
    owner = case / "constant" / region / "polyMesh" / "owner"
    if not owner.is_file():
        return ""
    with owner.open(errors="replace") as f:
        head = f.read(4000)
    m = re.search(r"nCells:\s*(\d+)", head)
    return int(m.group(1)) if m else ""


def schemes_note(meta):
    f = meta.get("fluid_schemes", {})
    parts = [f"{k} {v}" for k, v in f.items()]
    s = meta.get("solid_schemes", {})
    if s:
        parts.append("solid ddt " + s.get("ddtSchemes default", "?"))
    return "fluid " + ", ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs")
    ap.add_argument("out")
    ap.add_argument("--map", choices=("3a", "3b"))
    ap.add_argument("--include-smoke", action="store_true")
    ap.add_argument("--only", help="regex on run_id")
    a = ap.parse_args()
    runs, out = Path(a.runs), Path(a.out)
    (out / "provenance").mkdir(parents=True, exist_ok=True)
    rows, qrows = [], []
    for d in sorted(runs.glob("wp3-*")):
        if not d.is_dir() or not (d / "wp3_result.json").is_file():
            continue
        if d.name.endswith("-smoke") and not a.include_smoke:
            continue
        if a.only and not re.search(a.only, d.name):
            continue
        meta = json.loads((d / "wp3_case.json").read_text())
        if a.map and meta["map"] != a.map:
            continue
        res = json.loads((d / "wp3_result.json").read_text())
        rmeta = json.loads((d / "run_meta.json").read_text())
        prov = json.loads((d / "provenance.json").read_text()) \
            if (d / "provenance.json").is_file() else {}
        prov["case_settings"] = meta
        prov["run_meta"] = rmeta
        (out / "provenance" / f"{d.name}.json").write_text(
            json.dumps(prov, indent=1) + "\n")
        xe = "xenosim" in str(rmeta.get("node", "")).lower()
        qm = meta["coupling"] == "qm"
        ring = meta["map"] == "3a"
        lib = prov.get("libraries") or {}
        comp = prov.get("compiler") or {}
        s4f = prov.get("solids4foam") or {}
        row = dict.fromkeys(COLS, "")
        row.update(
            run_id=d.name, stream="wp3", case=meta["case"],
            study=f"{meta['map']} robustness map",
            coupling=COUPLING[meta["coupling"]],
            scheme="quasi-monolithic JFNK" if qm else "partitioned",
            level=(f"{meta['level']} m2 n{meta['steps_per_period']}" if ring
                   else f"fluid L{meta['fluid_level']}"),
            fluid_cells=ncells(d, "fluid"), solid_cells=ncells(d, "solid"),
            interface=meta["interface"] + (" (conservative traction)"
                                           if qm and not ring else ""),
            dt=f"{meta['deltaT']:.10g}",
            rho_ratio=(f"{meta['rho_ratio']:g}" if not ring else
                       f"rhoF {meta['rhoFluid']:g} (mu {meta['massRatio']:.4g})"),
            ranks=1, cores=1, nodes=1,
            node_type=(f"XenoSim ({prov.get('cpu_model', '')})" if xe else
                       f"MeluXina cpu ({prov.get('cpu_model', '')})"),
            exclusive=("no (shared XenoSim node, no binding; timings "
                       "indicative)" if xe else
                       "node exclusive, shared with other WP3 runs "
                       "(timings indicative)"),
            code_commit=f"{s4f.get('describe', '')} {s4f.get('commit', '')}"
                        .strip(),
            of_version=(prov.get("openfoam") or {}).get("version", ""),
            petsc_version=lib.get("petsc_version", ""),
            hypre_version=lib.get("hypre_version", ""),
            compiler=comp.get("compiler_version", ""),
            compile_flags=comp.get("compile_flags", ""),
            ddt_U=meta["fluid_schemes"].get(
                "ddt(U)", meta["fluid_schemes"].get("ddtSchemes default", "")),
            status=res["status"], t_end=meta["end_time"],
            n_steps=res["n_steps_done"],
            iters_mean=g(res["iters_mean"], "{:.4g}"),
            iters_max=g(res["iters_max"], "{}"),
            ksp_per_newton_mean=g(res.get("ksp_per_newton_mean"), "{:.4g}"),
            window="full run" if res["status"] == "pass" else
            f"to failure at t = {res['t_reached']}",
            repeats=1,
        )
        if qm:
            p = meta["petsc"]
            row.update(snes_rtol=p["snes_rtol"], snes_stol=p["snes_stol"],
                       ksp_rtol=p["ksp_rtol"],
                       convergence_test="SNES rtol/stol, snes_max_it "
                       + p["snes_max_it"], solid_pc="redundant+lu")
        else:
            row.update(coupling_tol=meta["coupling_tol"],
                       convergence_test=meta["convergence_test"]
                       + f", nOuterCorr {meta['caps']['nOuterCorr']}")
        notes = [f"status {res['status']}, t_reached {res['t_reached']}"
                 f" of {meta['end_time']:.6g}", schemes_note(meta)]
        if qm:
            # #618 (merge 4ae081609) removed viscousStressTranspose and
            # hard-coded the transpose wall treatment; earlier QM rows are
            # superseded
            if meta.get("viscousStressTranspose", "no") == "no":
                notes.append("viscousStressTranspose no; pre-#618 "
                             "(superseded)")
            else:
                notes.append("#618 build, transpose term always on")
        if meta["coupling"] == "iqn":
            notes.append("couplingReuse 0")
        if "relaxationFactor" in meta:
            notes.append(f"initial relaxation {meta['relaxationFactor']}")
        if res.get("coupled_snes_fail"):
            notes.append(f"coupled SNES failure {res['coupled_snes_fail']}")
        if res.get("other_snes_fail"):
            notes.append(f"inner SNES non-convergence {res['other_snes_fail']}")
        if res.get("fatal"):
            notes.append("fatal: " + res["fatal"][:120])
        if not ring:
            notes.append(f"solid {meta['solid']} {meta['solid_mesh']}, "
                         f"rho_s {meta['rho_solid']:g}")
        wall = rmeta.get("wall_s")
        if wall:
            n = max(res["n_steps_done"] or 0, 1)
            row.update(wall_s=f"{wall:.1f}", wall_s_per_step=f"{wall / n:.4g}",
                       core_h=f"{wall / 3600:.4g}",
                       core_h_per_sim_s=(f"{wall / 3600 / res['t_reached']:.4g}"
                                         if res.get("t_reached") else ""))
        row["notes"] = "; ".join(notes)
        rows.append(row)

        def q(name, value, ref="", src="", rel="", note=""):
            qrows.append(dict(run_id=d.name, qoi=name, value=value,
                              reference=ref, reference_source=src,
                              rel_error=rel, uncertainty_of_reference="",
                              notes=note))

        q("status", res["status"], note="WP3 failure criterion (README)")
        q("t_reached", g(res["t_reached"], "{:.8g}"))
        if ring and "omega" in res:
            q("omega", f"{res['omega']:.8g}", f"{meta['omega_exact']:.10g}",
              "exact linear (ring_exact_frequencies.py)",
              f"{res['omega_error']:.4e}", "two periods; first crossing "
              "skipped (driver method)")
            q("loss_per_period", f"{res['loss_per_period']:.5g}")
        if not ring and "trough_value" in res:
            q("trough_wallMid", f"{res['trough_value']:.8g}",
              g(res.get("trough_reference"), "{:.8g}"),
              res.get("trough_reference_source", ""),
              g(res.get("trough_error"), "{:.4e}"),
              f"trough at t = {res['trough_time']:.5g} s")
    with (out / "runs.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows(rows)
    with (out / "qois.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, QCOLS)
        w.writeheader()
        w.writerows(qrows)
    print(f"{len(rows)} runs, {len(qrows)} QoI rows -> {out}")


if __name__ == "__main__":
    main()
