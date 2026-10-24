#!/usr/bin/env python3
"""Collect agent A's runs into runs.csv, qois.csv and provenance/<run_id>.json.

    ma_collect.py RUNS_DIR OUT_DIR [--stream ma-b1] [--machine Mx]

RUNS_DIR holds <run_id>/ma_result.json and provenance.json (from ma_run.py;
a local rsync of those files is enough, plus constant/*/polyMesh/owner for
the cell counts). Columns as HANDOFF §6 (paper-data/campaign/r0).

QoIs. ringAddedMass: wet or dry frequency error against the exact linear
solution, amplitude loss per period, and for wet runs the error of the
wet/dry frequency ratio against the exact ratio, with the dry ring (standard
solid) of the same mesh and steps. womersleyTube: the driver's relative
errors against the exact linear solution.
"""
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
WOM_QOIS = ["profile", "flow_amp", "flow_phase", "wallMid_amp",
            "wallMid_phase", "speed", "attenuation", "pressure",
            "periodicity"]
COUPLING = {"monolithic": "NewtonQuasiMonolithic", "iqnils": "IQNILS",
            "aitken": "Aitken",
            "robin": "Robin-Neumann", "": "none (dry solid)"}
STUDY = {"1a": "1a ring QM sweep", "1d": "1d ring couplings (standard solid)",
         "1e": "1e Womersley QM cells", "1b": "1b ring zeroGradient pressure",
         "1c": "1c ring non-conformal (AMI)", "2a": "2a cavity QM L1-L4",
         "2b": "2b cavity interpolate(U) linear", "5b": "5b blob QM time steps",
         "2c": "2c cavity partitioned strict rerun (checkMesh)",
         "fix": "vST fix verification (build 63d2cc8a9)",
         "5a": "5a blob QM steady x1/x2/x4"}
CASE = {"ram": "ringAddedMass", "wom": "womersleyTube",
        "cav": "cavityFlexibleBottom", "cavpart": "cavityFlexibleBottom",
        "blob": "blobInTreacle"}
RHO = {"weak": 14.0, "moderate": 140.0, "strong": 1400.0}


def ncells(case, region):
    f = case / "constant" / region / "polyMesh" / "owner"
    if not f.is_file():
        f = case / "constant" / "polyMesh" / "owner"
    if not f.is_file():
        return ""
    m = re.search(r"nCells:\s*(\d+)", f.read_text(errors="replace"))
    return int(m.group(1)) if m else ""


def g(x, fmt="{:.6g}"):
    return "" if x is None or x != x else fmt.format(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--stream", default="ma-b1")
    ap.add_argument("--machine", default="MeluXina cpu")
    ap.add_argument("--pattern", default="ma-*")
    args = ap.parse_args()
    (args.out / "provenance").mkdir(parents=True, exist_ok=True)
    rows, qrows, res = [], [], {}
    for d in sorted(args.runs.glob(args.pattern)):
        rf = d / "ma_result.json"
        if not rf.is_file():
            continue
        r = json.loads(rf.read_text())
        res[r["run_id"]] = r
        pf = d / "provenance.json"
        p = json.loads(pf.read_text()) if pf.is_file() else {}
        p["case_settings"] = r["def"]
        (args.out / "provenance" / f"{r['run_id']}.json").write_text(
            json.dumps(p, indent=2) + "\n")
        df = r["def"]
        ring = df["case"] == "ram"
        coupling = df.get("coupling", "") or \
            ("monolithic" if df["case"] in ("cav", "blob") else
             "aitken" if df["case"] == "cavpart" else "")
        qm = coupling == "monolithic"
        opts = p.get("petsc_options") or {}
        petsc = (opts.get("system/fvSolution") or {}).get("UpU", {})
        lib = p.get("libraries") or {}
        comp = p.get("compiler") or {}
        s4f = p.get("solids4foam") or {}
        slurm = p.get("slurm") or {}
        if ring:
            level = (f"{df['level']} " if df.get("level") else "dry ") + \
                f"m{df['factor']} n{df['steps']}" + \
                (f" nc{df['solidCells']}" if df.get("solidCells") else "")
        elif df["case"] == "wom":
            level = f"m{df['factor']} n{df['steps']}"
        elif df["case"] in ("cav", "cavpart"):
            level = f"L{df['level']}"
        else:
            level = f"x{df['level']} dt {df['dt']:g}"
        row = dict.fromkeys(COLS, "")
        row.update(
            run_id=r["run_id"], stream=args.stream,
            case=CASE[df["case"]],
            study=STUDY[df["item"]], coupling=COUPLING[coupling],
            scheme="quasi-monolithic JFNK" if qm else
            ("partitioned" if coupling else "solid only"),
            level=level, interface="non-conformal (AMI)"
            if df.get("solidCells") else "conformal (directMap)",
            rho_ratio=RHO.get(df.get("level", ""), "") if ring else "",
            ranks=df["ranks"], cores=df["ranks"], nodes=1,
            node_type=f"{args.machine} ({p.get('cpu_model', '')})",
            exclusive="no (shared node, farm of up to 77 serial runs; "
            "timings indicative)",
            code_commit=f"{s4f.get('describe', '')} {s4f.get('commit', '')}".strip(),
            of_version=(p.get("openfoam") or {}).get("version", ""),
            petsc_version=lib.get("petsc_version", ""),
            hypre_version=lib.get("hypre_version", ""),
            compiler=comp.get("compiler_version", ""),
            compile_flags=comp.get("compile_flags", ""),
            ddt_U="Euler (steady)" if df["case"] in ("cav", "cavpart")
            else "backward",
            status=r["status"], repeats=1,
            window="full run")
        notes = []
        if slurm.get("slurm_job_id"):
            notes.append(f"Slurm {slurm['slurm_job_id']} on "
                         f"{slurm.get('slurm_job_nodelist', '')}")
        if qm:
            row.update(snes_rtol=petsc.get("snes_rtol", ""),
                       snes_stol=petsc.get("snes_stol", ""),
                       ksp_rtol=petsc.get("ksp_rtol", ""),
                       convergence_test="SNES rtol/stol",
                       solid_pc="redundant+lu")
            notes.append("transpose viscous term always on (#618)"
                         if df.get("vst") is None
                         else f"viscousStressTranspose {df['vst']}")
            if df.get("tutorial_schemes"):
                notes.append("tutorial fvSchemes as merged (#617: ddt "
                             "backward, linearUpwind grad(U), interpolate(U) "
                             "as the partitioned file)")
            elif df["case"] in ("ram", "wom"):
                notes.append("schemes as tutorial fvSchemes.monolithic (= "
                             "partitioned: Gauss linear, leastSquares, "
                             "ddt(U) backward, ddt(dU) Euler)")
            elif df["case"] == "cav":
                notes.append("div(phi,U) Gauss linearUpwind grad(U), "
                             f"interpolate(U) {df['interp']}, ddt(U) Euler "
                             "(steady, as partitioned), dt 0.5 to 300 s, inlet "
                             "ramp 20 s")
            else:
                notes.append("div(phi,U) Gauss linearUpwind grad(U), ddt(U) "
                             "backward (tutorial Euler), ddt(dU) Euler")
            if df.get("p_interface"):
                notes.append(f"interface p {df['p_interface']}")
            if df.get("conservative"):
                notes.append(f"conservativeTractionTransfer {df['conservative']}")
        elif coupling:
            row.update(coupling_tol="outerCorrTolerance 1e-6",
                       convergence_test="strict (requireAllResidualMeasures)")
            notes.append("couplingReuse 0" if coupling == "iqnils" else
                         "robinPressureTolerance 1e-5, robinFluxTolerance 5e-3")
        if ring:
            notes.append(f"solid {df['solid']}")
        if r["status"] != "completed":
            notes.append(r.get("error", ""))
            row["notes"] = "; ".join(notes)
            rows.append(row)
            continue
        wall = r["wall_s"]
        if df["case"] == "cavpart":
            notes.append(f"Aitken tol 1e-5, nOuterCorr {df['n_outer']}"
                         + (f", fluid solvers {df['fluid_tol']}" if df.get("fluid_tol") else "")
                         + "; end 200 s as the README partitioned_strict rows")
            notes.append(f"coupling iterations last 10% {r['iters_mean_last10']:.3g}")
        if df["case"] in ("cav", "blob", "cavpart"):
            dt = 0.5 if df["case"] == "cav" else df["dt"]
            n_steps = r["n_steps"]
            t_end = n_steps * dt
            row.update(dt=f"{dt:.8g}", t_end=f"{t_end:.8g}", n_steps=n_steps,
                       fluid_cells=ncells(d, "fluid"),
                       solid_cells=ncells(d, "solid"),
                       iters_mean=g(r.get("iters_mean"), "{:.4g}"),
                       iters_max=r.get("iters_max", ""),
                       ksp_per_newton_mean=g(r.get("ksp_per_newton_mean"), "{:.4g}"),
                       wall_s=f"{wall:.1f}",
                       wall_s_per_step=f"{wall / n_steps:.4g}",
                       core_h=f"{wall * df['ranks'] / 3600:.4g}",
                       core_h_per_sim_s=f"{wall * df['ranks'] / 3600 / t_end:.4g}",
                       notes="; ".join(notes))
            rows.append(row)
            continue
        if ring:
            n_steps = df["steps"] * r["periods"]
            dt = r["period"] / df["steps"]
            t_end = n_steps * dt
            row.update(fluid_cells=ncells(d, "fluid") if df["kind"] == "wet"
                       else "", solid_cells=ncells(d, "solid"))
        else:
            n_steps, t_end, dt = 6 * df["steps"], 300.0, 300.0 / 6 / df["steps"]
            row.update(fluid_cells=ncells(d, "fluid"),
                       solid_cells=ncells(d, "solid"))
        row.update(dt=f"{dt:.8g}", t_end=f"{t_end:.8g}", n_steps=n_steps,
                   iters_mean=g(r.get("mean_iterations"), "{:.4g}"),
                   iters_max=r.get("max_iterations", ""),
                   ksp_per_newton_mean=g(r.get("ksp_per_newton_mean"),
                                         "{:.4g}") if qm else "",
                   wall_s=f"{wall:.1f}",
                   wall_s_per_step=f"{wall / n_steps:.4g}",
                   core_h=f"{wall / 3600:.4g}",
                   core_h_per_sim_s=f"{wall / 3600 / t_end:.4g}",
                   notes="; ".join(notes))
        rows.append(row)

    for rid, r in sorted(res.items()):
        if r["status"] != "completed":
            continue
        df = r["def"]
        if df["case"] == "cavpart":
            ref = {1: -0.202499, 2: -0.22883, 3: -0.235636, 4: -0.237307}[df["level"]]
            qrows.append(dict(run_id=rid, qoi="uy_monitor", value=f"{r['uy']:.6g}",
                              reference=f"{ref:.6g}", reference_source=
                              "four_level_partitioned_monolithic.csv partitioned_strict (MS, 0698d55cd)",
                              rel_error=f"{(r['uy'] - ref) / abs(ref):.4e}",
                              notes="t = 200 s"))
            qrows.append(dict(run_id=rid, qoi="fy_interface", value=f"{r['fy']:.7g}"))
            continue
        if df["case"] == "cav":
            ref = {1: -0.201546, 2: -0.228468, 3: -0.235448, 4: -0.237187}[df["level"]]
            qrows.append(dict(run_id=rid, qoi="uy_monitor", value=f"{r['uy']:.6g}",
                              reference=f"{ref:.6g}", reference_source=
                              "four_level_partitioned_monolithic.csv monolithic_597 (E597, Euler)",
                              rel_error=f"{(r['uy'] - ref) / abs(ref):.4e}",
                              notes=f"t = 300 s; spread over last 10% {r['uy_spread']:.2e}"))
            qrows.append(dict(run_id=rid, qoi="fy_interface", value=f"{r['fy']:.7g}",
                              notes=f"spread {r['fy_spread']:.2e}"))
            for rel in ("0.001", "0.0001"):
                qrows.append(dict(run_id=rid, qoi=f"t_steady_{rel}",
                                  value=f"{r['t_steady_' + rel]:g}",
                                  notes=f"last time |uy - uy_final| > {rel} |uy_final|; "
                                  f"{r['steps_to_steady_' + rel]} steps, "
                                  f"{r['newton_to_steady_' + rel]} Newton iterations"))
            continue
        if df["case"] == "blob" and df["item"] == "5a":
            ref = {1: 0.117231, 2: 0.119691, 4: 0.120206}[df["level"]]
            qrows.append(dict(run_id=rid, qoi="ux_top", value=f"{r['ux']:.8g}",
                              reference=f"{ref:.8g}", reference_source=
                              "WP0 IQN-ILS strict, same level (MS, 85b0c1de6)",
                              rel_error=f"{(r['ux'] - ref) / abs(ref):.4e}",
                              notes="t = 3 s steady top point"))
            qrows.append(dict(run_id=rid, qoi="uy_top", value=f"{r['uy']:.8g}",
                              notes="t = 3 s steady top point"))
            continue
        if df["case"] == "blob":
            for q in ("ux", "uy"):
                qrows.append(dict(run_id=rid, qoi=f"{q}_top_t1", value=f"{r[q]:.8g}",
                                  notes="t = 1 s top point"))
            continue
        if df["case"] == "ram":
            src = "exact linear solution (ring_exact_frequencies.py)"
            qrows.append(dict(run_id=rid, qoi="omega", value=f"{r['omega']:.8g}",
                              reference=f"{r['omega_exact']:.8g}",
                              reference_source=src,
                              rel_error=f"{r['error']:.6e}"))
            qrows.append(dict(run_id=rid, qoi="loss_per_period",
                              value=f"{r['loss_per_period']:.6e}",
                              notes="amplitude loss per period (exact 0)"))
            if df["kind"] == "wet":
                pre = rid.split("-ram-")[0]
                dry = res.get(f"{pre}-ram-dry-m{df['factor']}-n{df['steps']}"
                              + (f"-nc{df['solidCells']}" if df.get("solidCells") else ""))
                if dry and dry["status"] == "completed":
                    ratio = r["omega"] / dry["omega"]
                    exact = r["omega_exact"] / dry["omega_exact"]
                    qrows.append(dict(
                        run_id=rid, qoi="wet_dry_ratio", value=f"{ratio:.8g}",
                        reference=f"{exact:.8g}", reference_source=src,
                        rel_error=f"{ratio / exact - 1:.6e}",
                        notes=f"dry: {dry['run_id']} (standard solid)"))
        else:
            for q in WOM_QOIS:
                if r.get(q) is not None:
                    qrows.append(dict(
                        run_id=rid, qoi=q, value=f"{r[q]:.6e}",
                        reference="0" if q != "periodicity" else "",
                        reference_source="exact linear solution "
                        "(womersley_exact.py); value is the relative error"
                        if q != "periodicity" else "",
                        rel_error=f"{r[q]:.6e}" if q != "periodicity" else "",
                        notes="phase errors in radians" if "phase" in q else ""))
    for name, cols, data in (("runs.csv", COLS, rows), ("qois.csv", QCOLS, qrows)):
        with (args.out / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore",
                               lineterminator="\n")
            w.writeheader()
            w.writerows(data)
    print(f"{len(rows)} runs, {len(qrows)} QoIs -> {args.out}")


if __name__ == "__main__":
    main()
