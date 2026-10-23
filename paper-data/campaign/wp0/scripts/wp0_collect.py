#!/usr/bin/env python3
"""Collect the WP0 runs into runs.csv, qois.csv and provenance/<run_id>.json.

    wp0_collect.py OUT_DIR

Reads runs/<run_id>/wp0_result.json and provenance.json (written by
wp0_run.py). QoIs: blobInTreacle steady top-point displacement (u_x, u_y at
t = 3 s, the partitioned run of the same level as reference);
womersleyTube errors against the exact linear solution (driver metrics).
"""
import csv
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
OUT = Path(sys.argv[1])

COLS = ("run_id,stream,case,study,coupling,scheme,level,fluid_cells,"
        "solid_cells,interface,dt,rho_ratio,ranks,cores,nodes,node_type,"
        "exclusive,code_commit,tag,of_version,petsc_version,hypre_version,"
        "compiler,compile_flags,snes_rtol,snes_stol,ksp_rtol,coupling_tol,"
        "convergence_test,solid_pc,ddt_U,status,t_end,n_steps,iters_mean,"
        "iters_max,ksp_per_newton_mean,wall_s,wall_s_per_step,core_h,"
        "core_h_per_sim_s,peak_mem_gb,window,repeats,notes").split(",")
QCOLS = ["run_id", "qoi", "value", "reference", "reference_source",
         "rel_error", "uncertainty_of_reference", "notes"]
WOM_QOIS = ["profile", "flow_amp", "flow_phase", "wallMid_amp",
            "wallMid_phase", "speed", "attenuation", "pressure",
            "periodicity"]
CPU = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                     capture_output=True, text=True).stdout.strip()


def ncells(case, region):
    import re
    text = (case / "constant" / region / "polyMesh" / "owner").read_text(errors="replace")
    return int(re.search(r"nCells:\s*(\d+)", text).group(1))


def g(x, fmt="{:.6g}"):
    return "" if x is None else fmt.format(x)


def main():
    (OUT / "provenance").mkdir(parents=True, exist_ok=True)
    rows, qrows, res = [], [], {}
    for d in sorted(RUNS.glob("wp0-*")):
        rf = d / "wp0_result.json"
        if not rf.is_file():
            continue
        r = json.loads(rf.read_text())
        res[r["run_id"]] = r
        p = json.loads((d / "provenance.json").read_text())
        p["cpu_model"] = p.get("cpu_model") or CPU
        p["os"] = platform.platform()
        p["case_settings"] = r["def"]
        (OUT / "provenance" / f"{r['run_id']}.json").write_text(
            json.dumps(p, indent=2) + "\n")
        df = r["def"]
        qm = df["coupling"] == "monolithic"
        blob = df["case"] == "blob"
        opts = (p.get("petsc_options") or {})
        petsc = (opts.get("system/fvSolution") or {}).get("UpU", {})
        lib = p.get("libraries") or {}
        comp = p.get("compiler") or {}
        row = dict.fromkeys(COLS, "")
        row.update(
            run_id=r["run_id"], stream="wp0",
            case="blobInTreacle" if blob else "womersleyTube",
            study="0b viscousStressTranspose" if blob
            else "0c viscousStressTranspose",
            coupling={"monolithic": "NewtonQuasiMonolithic",
                      "partitioned": "IQNILS", "iqnils": "IQNILS",
                      "robin": "Robin-Neumann"}[df["coupling"]],
            scheme="quasi-monolithic JFNK" if qm else "partitioned",
            level=f"x{df['level']}" if blob else "m2 n50",
            interface="conformal", ranks=df["ranks"], cores=df["ranks"],
            nodes=1, node_type=f"mac-studio ({p['cpu_model']})",
            exclusive="no (shared workstation; timings indicative)",
            code_commit=(p["solids4foam"]["describe"] or "") + " "
            + (p["solids4foam"]["commit"] or ""),
            of_version=p["openfoam"]["version"],
            petsc_version=lib.get("petsc_version", ""),
            hypre_version=lib.get("hypre_version", ""),
            compiler=comp.get("compiler_version", ""),
            compile_flags=comp.get("compile_flags", ""),
            ddt_U="backward", status=r["status"], repeats=1, window="full run",
        )
        if qm:
            row.update(snes_rtol=petsc.get("snes_rtol", ""),
                       snes_stol=petsc.get("snes_stol", ""),
                       ksp_rtol=petsc.get("ksp_rtol", ""),
                       convergence_test="SNES rtol/stol",
                       solid_pc="redundant+lu",
                       notes=f"viscousStressTranspose {df['vst']}")
        else:
            row.update(coupling_tol="outerCorrTolerance 1e-6",
                       convergence_test="strict (requireAllResidualMeasures)"
                       + (" + outerCorrAbsoluteTolerance 1e-9 m" if blob else ""),
                       notes="couplingReuse 0" if df["coupling"] != "robin"
                       else "robinPressureTolerance 1e-5, robinFluxTolerance 5e-3")
        if blob:
            row["notes"] += ("; fvSchemes.monolithic ddt(U) Euler -> backward"
                             if qm else "")
        if r["status"] != "completed":
            row["notes"] += "; " + r.get("error", "")
            rows.append(row)
            continue
        wall = r["wall_s"]
        if blob:
            n_steps, t_end = r["n_steps"], r["t_end"]
            row.update(fluid_cells=r["fluid_cells"], solid_cells=r["solid_cells"],
                       dt=r["dt"])
            row["notes"] += f"; steady spread over last 0.5 s {r['steady_spread_0p5']:.2e}"
        else:
            n_steps, t_end = 300, 300.0
            row.update(dt=1.0, fluid_cells=ncells(d, "fluid"), solid_cells=ncells(d, "solid"))
        row.update(t_end=t_end, n_steps=n_steps,
                   iters_mean=g(r.get("iters_mean", r.get("mean_iterations")), "{:.4g}"),
                   iters_max=r.get("iters_max", r.get("max_iterations")),
                   ksp_per_newton_mean=g(r.get("ksp_per_newton_mean"), "{:.4g}") if qm else "",
                   wall_s=f"{wall:.1f}", wall_s_per_step=f"{wall / n_steps:.4g}",
                   core_h=f"{wall * df['ranks'] / 3600:.4g}",
                   core_h_per_sim_s=f"{wall * df['ranks'] / 3600 / t_end:.4g}")
        rows.append(row)

    # QoIs
    for rid, r in sorted(res.items()):
        if r["status"] != "completed":
            continue
        df = r["def"]
        if df["case"] == "blob":
            ref_id = f"wp0-blob-iqn-x{df['level']}"
            ref = res.get(ref_id)
            for q, key in (("ux_top", "ux"), ("uy_top", "uy")):
                row = dict(run_id=rid, qoi=q, value=f"{r[key]:.8g}")
                if ref and ref["status"] == "completed" and rid != ref_id:
                    row.update(reference=f"{ref[key]:.8g}",
                               reference_source=f"{ref_id} (IQN-ILS strict, same level, head)",
                               rel_error=f"{(r[key] - ref[key]) / abs(ref[key]):.4e}")
                row["notes"] = "t = 3 s steady top point"
                qrows.append(row)
        else:
            for q in WOM_QOIS:
                if q in r and r[q] is not None:
                    qrows.append(dict(
                        run_id=rid, qoi=q, value=f"{r[q]:.6e}", reference="0",
                        reference_source="exact linear solution (womersley_exact.py); value is the relative error"
                        if q != "periodicity" else "",
                        rel_error=f"{r[q]:.6e}" if q != "periodicity" else "",
                        notes="phase errors in radians" if "phase" in q else ""))
    for name, cols, data in (("runs.csv", COLS, rows), ("qois.csv", QCOLS, qrows)):
        with (OUT / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)
    print(f"{len(rows)} runs, {len(qrows)} QoIs -> {OUT}")


if __name__ == "__main__":
    main()
