#!/usr/bin/env python3
"""R4/R5: build one run directory (FSI3 or 3dTube) for the task farm.

Usage (Python >= 3.10; the solids4foam tree is $QM_S4F, default
/project/home/p201287/philip/qm-final/solids4foam; nothing in it is written):

    qm_setup.py fsi3 DEST --coupling mono|iqn --level 1|2|4 --ranks N
                [--end 7] [--tol SPEC]
    qm_setup.py tube DEST --coupling mono|robin --level 1|2|3 --ranks N
                [--end 0.02] [--tol SPEC] [--write-interval 0.004]
    qm_setup.py restart SRC DEST --from T --end T1 [--ranks N] [--tol SPEC]
                [--pc SPEC] [--write-final-only]

fsi3: TurekHron2006 FSI3 on the conformal interface meshes of the
  quasi-monolithic variant (1x/2x/4x as `Allverify --coupling monolithic`).
  The case is configured with the verification driver's own configure_case()
  (mesh refinement, Δt, end time, forces on plate+cylinder per unit depth,
  St Venant-Kirchhoff plate, scotch decomposition), imported from the tree.
  mono: the tutorial's `Allrun monolithic` variant.
  iqn:  partitioned IQN-ILS (tutorial `Allrun iqnils`) on the SAME conformal
        meshes (blockMeshDict.monolithic copied over blockMeshDict). The fluid
        mesh motion stays the tutorial's velocityLaplacian with the quadratic
        inverseDistance(plate cylinder) diffusivity: the partitioned
        fluidSolidInterface::moveFluidMesh() supports only pointMotionU/RBF
        motion solvers, not the solids4foamSolidModel pseudo-solid of the
        monolithic variant (FatalError "Problem with fluid mesh motion solver
        selection"), and solver changes are out of scope.
        Strict test: requireAllResidualMeasures yes; nOuterCorr 100.
tube: 3dTube with the verification driver's prepare steps (refinement, Δt,
  backward in fluid and solid, monitors), solid preconditioner B1 S1
  BoomerAMG (membraneRoof settings) in both the monolithic solid block and
  the partitioned solid solver, monolithic runs decomposed with
  decomposeParMonolithic (one graph over both regions), Robin runs with the
  per-region scotch decomposition of the driver.
restart: copy a run directory with only the time directory T (and 0,
  constant), no logs or postProcessing, and continue to T1, optionally with
  other tolerances, PC options or rank count (a new rank count re-decomposes
  from the reconstructed time: not implemented, the rank count must match).

--tol SPEC, comma-separated key=value:
  mono: snes_rtol, snes_stol, ksp_rtol, ksp_max_it (UpU block; the fluid-only
        Up block of FSI3 gets the same snes/ksp tolerances)
  iqn/robin: ctol (outerCorrTolerance), fluid_tol (p, U, cellMotionU
        absolute tolerances), solid_rtol (solid SNES snes_rtol and snes_stol),
        solid_ksp_rtol, nouter (nOuterCorr)
--pc SPEC (mono only): named variants for the R5 ablation, see PC_VARIANTS.

Every run directory gets qm_run.json, read by run_task.sh and qm_post.py.
All fields are written in binary (exact restarts).
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

S4F = Path(os.environ.get("QM_S4F",
                          "/project/home/p201287/philip/qm-final/solids4foam"))
TUT = S4F / "tutorials" / "fluidSolidInteraction"

# B1 S1 (campaign/scripts/b1_setup.py, membraneRoof solid settings)
BOOMERAMG = [
    ("pc_type", "hypre"),
    ("pc_hypre_type", "boomeramg"),
    ("pc_hypre_boomeramg_max_iter", '"1"'),
    ("pc_hypre_boomeramg_strong_threshold", '"0.7"'),
    ("pc_hypre_boomeramg_grid_sweeps_up", '"1"'),
    ("pc_hypre_boomeramg_grid_sweeps_down", '"1"'),
    ("pc_hypre_boomeramg_agg_nl", '"1"'),
    ("pc_hypre_boomeramg_agg_num_paths", '"1"'),
    ("pc_hypre_boomeramg_max_levels", '"25"'),
    ("pc_hypre_boomeramg_coarsen_type", "HMIS"),
    ("pc_hypre_boomeramg_interp_type", "ext+i"),
    ("pc_hypre_boomeramg_P_max", '"1"'),
    ("pc_hypre_boomeramg_truncfactor", '"0.3"'),
]
S1 = [("ksp_type", "preonly")] + BOOMERAMG
S0 = [("ksp_type", "preonly"), ("pc_type", "redundant"),
      ("redundant_pc_type", "lu")]

MONOLITHIC_DECOMPOSITION = """
monolithicCoeffs
{
    regions (fluid solid);

    // DOF-based, as decomposeParMonolithic's README: fluid 4, solid 3
    regionWeights
    {
        fluid   4;
        solid   3;
    }

    interfaces
    (
        {
            regionA     fluid;
            patchA      wall;
            regionB     solid;
            patchB      inner-wall;
        }
    );
}
"""


def die(msg):
    sys.exit(f"qm_setup: {msg}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def ignore_outputs(directory, names):
    skip = set()
    for n in names:
        if n.startswith(("processor", "log.", "postProcessing")) \
                or n in ("work", "__pycache__", ".solids4FoamCaseVariant",
                         "images", "regressionTests", "case.foam"):
            skip.add(n)
        elif re.fullmatch(r"[0-9.eE+-]+", n) and n != "0" \
                and Path(directory).name not in ("constant",):
            skip.add(n)
    return skip


def set_entry(path, key, value, count=1, top=False):
    """Set `key value;` entries (top: only unindented)."""
    path = Path(path)
    text = path.read_text()
    ind = "" if top else r"[ \t]*"
    new, n = re.subn(rf"^({ind}{re.escape(key)}\s+)[^;\n]*;",
                     lambda m: f"{m.group(1)}{value};", text,
                     flags=re.MULTILINE)
    if count is not None and n != count:
        die(f"{path}: expected {count} '{key}' entries, found {n}")
    path.write_text(new)
    return n


def options_block(text, solver):
    """(start, end) of the body of solvers/<solver>/options { ... }."""
    m = re.search(rf"^\s*\"?{re.escape(solver)}\"?\s*(//[^\n]*)?\n\s*\{{",
                  text, flags=re.MULTILINE)
    if not m:
        return None
    o = re.compile(r"\boptions\s*\{").search(text, m.end())
    if not o:
        return None
    depth, i = 1, o.end()
    while depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return o.end(), i - 1


def set_petsc_options(path, solver, values, drop_prefix=None, add=None,
                      note=None):
    """Set PETSc options in solvers/<solver>/options of a fvSolution file.

    values: {key: value}; replaced if present, appended otherwise.
    drop_prefix: remove every option starting with this prefix first.
    add: list of (key, value) appended (after drop_prefix)."""
    path = Path(path)
    text = path.read_text()
    span = options_block(text, solver)
    if span is None:
        die(f"no {solver} options in {path}")
    body = text[span[0]:span[1]]
    lines = body.split("\n")
    if drop_prefix:
        lines = [ln for ln in lines
                 if not re.match(rf"\s*{re.escape(drop_prefix)}\w", ln)]
    indent = "            "
    for key, val in values.items():
        for k, ln in enumerate(lines):
            if re.match(rf"\s*{re.escape(key)}(\s|;)", ln):
                lines[k] = f'{indent}{key} {val};' if val is not None \
                    else ""
                break
        else:
            if val is not None:
                lines.append(f'{indent}{key} {val};')
    if add:
        if note:
            lines.append(f"{indent}// {note}")
        lines += [f"{indent}{k} {v};" for k, v in add]
    body = "\n".join(ln for ln in lines).rstrip() + "\n        "
    path.write_text(text[:span[0]] + body + text[span[1]:])


def q(v):
    return f'"{v:g}"' if isinstance(v, float) else f'"{v}"'


def parse_tol(spec):
    out = {}
    if not spec:
        return out
    for item in spec.split(","):
        k, v = item.split("=")
        out[k.strip()] = int(v) if k.strip() in ("ksp_max_it", "nouter") \
            else float(v)
    return out


def set_restart_flag(path):
    """restart yes in the coefficients block of the file's solid model."""
    path = Path(path)
    text = path.read_text()
    model = re.search(r"^solidModel\s+(\w+);", text, flags=re.MULTILINE)
    if not model:
        die(f"no solidModel in {path}")
    if re.search(r"^\s*restart\s", text, flags=re.MULTILINE):
        return
    coeffs = re.search(rf'^"?[^\n{{]*\b{model.group(1)}Coeffs\b[^\n{{]*\s*\{{',
                       text, flags=re.MULTILINE)
    if not coeffs:
        die(f"no {model.group(1)}Coeffs in {path}")
    path.write_text(text[:coeffs.end()] + "\n    restart yes;"
                    + text[coeffs.end():])


def binary_writes(control, interval=None):
    set_entry(control, "writeFormat", "binary", top=True)
    set_entry(control, "purgeWrite", "0", top=True)
    if interval is not None:
        set_entry(control, "writeInterval", str(interval), top=True)


# ---------------------------------------------------------------------------
# Tolerances
# ---------------------------------------------------------------------------

def apply_mono_tol(case, tol, blocks):
    """blocks: list of (fvSolution path, solver name)."""
    vals = {}
    for k in ("snes_rtol", "snes_stol", "ksp_rtol"):
        if k in tol:
            vals[k] = q(tol[k])
    if "ksp_max_it" in tol:
        vals["ksp_max_it"] = q(tol["ksp_max_it"])
    if vals:
        for path, solver in blocks:
            set_petsc_options(path, solver, vals)


def apply_partitioned_tol(case, tol, fsi_props, coeffs_hint):
    if "ctol" in tol:
        set_entry(fsi_props, "outerCorrTolerance", f"{tol['ctol']:g}")
    if "nouter" in tol:
        n = set_entry(fsi_props, "nOuterCorr", str(tol["nouter"]), count=None)
        if n == 0:
            add_coeff(fsi_props, coeffs_hint, f"nOuterCorr {tol['nouter']};")
    if "fluid_tol" in tol:
        fv = case / "system/fluid/fvSolution"
        text = fv.read_text()
        for solver in ('"p|pFinal"', "cellMotionU", '"U|UFinal"'):
            m = re.search(rf"^\s*{re.escape(solver)}\s*\n\s*\{{(.*?)\}}",
                          text, flags=re.MULTILINE | re.DOTALL)
            if not m:
                continue
            body = re.sub(r"(\btolerance\s+)[^;]+;",
                          rf"\g<1>{tol['fluid_tol']:g};", m.group(1))
            text = text[:m.start(1)] + body + text[m.end(1):]
        fv.write_text(text)
    vals = {}
    if "solid_rtol" in tol:
        vals["snes_rtol"] = q(tol["solid_rtol"])
        vals["snes_stol"] = q(tol["solid_rtol"])
    if "solid_ksp_rtol" in tol:
        vals["ksp_rtol"] = q(tol["solid_ksp_rtol"])
    if vals:
        set_petsc_options(case / "system/solid/fvSolution", "D", vals)


def add_coeff(path, block_regex, line):
    path = Path(path)
    text = path.read_text()
    m = re.search(rf'^"?[^\n{{]*{block_regex}[^\n{{]*\s*\{{', text,
                  flags=re.MULTILINE)
    if not m:
        die(f"no {block_regex} block in {path}")
    path.write_text(text[:m.end()] + f"\n    {line}" + text[m.end():])


# ---------------------------------------------------------------------------
# FSI3
# ---------------------------------------------------------------------------

def setup_fsi3(args):
    src = TUT / "TurekHron2006"
    drv = load("hron_drv", src / "verification/scripts/hron_turek_verification.py")
    spec = json.loads(drv.REFERENCE_FILE.read_text())
    factor = args.level
    idx = spec["mesh"]["refinementFactors"].index(factor)
    dt = spec["mesh"]["deltaTs"][idx]
    dest = Path(args.dest)
    if dest.exists():
        die(f"{dest} exists")
    shutil.copytree(src, dest, symlinks=True, ignore=ignore_outputs)
    shutil.rmtree(dest / "verification")
    # The driver's configuration (writes into the copy only). Fields every
    # 1 s of simulated time (restarts and timing windows start from them).
    every = round(1.0 / dt)
    drv.configure_case(dest, spec, factor, dt, args.end, every, args.ranks)
    binary_writes(dest / "system/controlDict")
    tol = parse_tol(args.tol)
    meta = {"case": "TurekHron2006", "benchmark": "fsi3", "level": factor,
            "dt": dt, "t_end": args.end, "ranks": args.ranks,
            "write_every_steps": every, "edits": []}
    if args.coupling == "mono":
        apply_mono_tol(dest, tol, [(dest / "system/fvSolution.monolithic", "UpU"),
                                   (dest / "system/fluid/fvSolution.monolithic", "Up")])
        set_restart_flag(dest / "constant/solid/solidProperties.monolithic")
        set_restart_flag(dest / "constant/fluid/solidProperties.monolithic")
        meta.update(coupling="NewtonQuasiMonolithic", allrun="monolithic",
                    decompose="regions", solid_pc="redundant+lu (S0)")
        meta["edits"] += ["restart yes in solid and fluid mesh-motion solid"]
    else:
        for region in ("fluid", "solid"):
            shutil.copy(dest / f"system/{region}/blockMeshDict.monolithic",
                        dest / f"system/{region}/blockMeshDict")
        props = dest / "constant/fsiProperties.iqnils"
        add_coeff(props, "IQNILSCoeffs", "requireAllResidualMeasures yes;")
        tol.setdefault("nouter", 100)
        apply_partitioned_tol(dest, tol, props, "IQNILSCoeffs")
        set_restart_flag(dest / "constant/solid/solidProperties")
        meta.update(coupling="IQNILS", allrun="iqnils", decompose="regions",
                    solid_pc="bjacobi+lu (tutorial partitioned solid)")
        meta["edits"] += [
            "conformal monolithic blockMeshDicts used for both regions",
            "fluid mesh motion: tutorial velocityLaplacian, quadratic "
            "inverseDistance(plate cylinder) (pseudo-solid not supported by "
            "the partitioned interface)",
            "requireAllResidualMeasures yes", "restart yes in solid"]
    meta["tol"] = tol
    finish(dest, meta, args)


# ---------------------------------------------------------------------------
# 3dTube
# ---------------------------------------------------------------------------

def setup_tube(args):
    src = TUT / "3dTube"
    drv = load("tube_drv", src / "verification/scripts/tube_3d_verification.py")
    ref = json.loads(drv.REFERENCE_FILE.read_text())
    factor = {1: 1, 2: 2, 3: 4}[args.level]
    dt = 2.5e-5 / factor
    dest = Path(args.dest)
    if dest.exists():
        die(f"{dest} exists")
    shutil.copytree(src, dest, symlinks=True, ignore=drv.ignored)
    drv.refine_mesh(drv.block_mesh_dict(dest, "fluid"), factor)
    drv.refine_mesh(drv.block_mesh_dict(dest, "solid"), factor)
    control = dest / "system/controlDict"
    drv.replace_entry(control, "deltaT", f"{dt:.10g}", True)
    drv.replace_entry(control, "endTime", f"{args.end:.10g}", True)
    drv.replace_entry(control, "writeInterval", f"{args.write_interval:.10g}",
                      True)
    binary_writes(control)
    drv.configure_time_scheme(dest, "backward")
    drv.configure_solid_preconditioner(dest, "hypre")
    if args.exact_arcs:
        exact_wall_arcs(dest)
        meta_edits = ["exact wall arc coordinates in both blockMeshDicts "
                      "(the tutorial's 4-digit values are not conformal within "
                      "the directMap tolerance at level 3)"]
    else:
        meta_edits = []
    coupling = {"mono": "monolithic", "robin": "robin"}[args.coupling]
    drv.configure_coupling(dest, coupling)
    drv.add_monitors(dest, ref)
    tol = parse_tol(args.tol)
    meta = {"case": "3dTube", "level": args.level, "factor": factor, "dt": dt,
            "t_end": args.end, "ranks": args.ranks, "edits": meta_edits}
    for d in [dest / "system/decomposeParDict"] \
            + list(dest.glob("system/*/decomposeParDict")):
        set_entry(d, "numberOfSubdomains", str(args.ranks), top=True)
    if args.coupling == "mono":
        fvs = dest / "system/fvSolution.monolithic"
        # B1 S1: the driver's two-option BoomerAMG replaced by the full set
        set_petsc_options(fvs, "UpU", {}, drop_prefix="fieldsplit_solid_",
                          add=[("fieldsplit_solid_" + k, v) for k, v in S1],
                          note="solid block: B1 S1 BoomerAMG")
        apply_mono_tol(dest, tol, [(fvs, "UpU")])
        dpd = dest / "system/decomposeParDict"
        dpd.write_text(dpd.read_text().rstrip() + "\n" + MONOLITHIC_DECOMPOSITION)
        set_restart_flag(dest / "constant/solid/solidProperties.monolithic")
        set_restart_flag(dest / "constant/fluid/solidProperties.monolithic")
        meta.update(coupling="NewtonQuasiMonolithic", allrun="monolithic",
                    decompose="monolithic", solid_pc="hypre/boomeramg (S1)")
        if args.pc:
            apply_pc_variant(dest, args.pc, meta)
    else:
        # Partitioned solid: the driver's hypre replacement, completed to S1
        sfv = dest / "system/solid/fvSolution"
        set_petsc_options(sfv, "D", {}, drop_prefix="pc_hypre",
                          add=BOOMERAMG[2:], note="B1 S1 BoomerAMG settings")
        apply_partitioned_tol(dest, tol, dest / "constant/fsiProperties.robin",
                              "fixedRelaxationCoeffs")
        set_restart_flag(dest / "constant/solid/solidProperties")
        meta.update(coupling="Robin-Neumann", allrun="", decompose="regions",
                    solid_pc="hypre/boomeramg (S1 settings)")
        for d in dest.glob("system/*/decomposeParDict"):
            set_entry(d, "method", "scotch", top=True)
    meta["tol"] = tol
    finish(dest, meta, args)


def exact_wall_arcs(dest):
    """3dTube: put the fluid wall and the solid inner wall on the same exact
    circle (r = 5 mm). The tutorial writes the wall vertices and arc points
    to 4 significant digits ((0.003536 0.003536), (0.004619 0.001913)); the
    fluid wall is two 45-degree arcs and the solid inner wall one 90-degree
    arc, so the rounded arcs are slightly different curves. At level 3 the
    face centres then differ by more than the directMap matching tolerance
    (1% of the smallest edge) and the run stops at start-up ("interfaces are
    not conformal"). With exact coordinates both arcs lie on one circle and
    blockMesh places the same points on both (uniform spacing along each arc,
    40 + 40 against 80 cells per quarter)."""
    c45 = "0.00353553390593274"
    c22, s22 = "0.00461939766255643", "0.00191341716182545"
    reps = {
        "system/fluid/blockMeshDict": [
            ("(0.003536 0.003536 0)", f"({c45} {c45} 0)"),
            ("(0.003536 0.003536 0.05)", f"({c45} {c45} 0.05)"),
            ("(0.004619 0.001913 0)", f"({c22} {s22} 0)"),
            ("(0.001913 0.004619 0)", f"({s22} {c22} 0)"),
            ("(0.004619 0.001913 0.05)", f"({c22} {s22} 0.05)"),
            ("(0.001913 0.004619 0.05)", f"({s22} {c22} 0.05)")],
        "system/solid/blockMeshDict": [
            ("arc 0 3 (0.003536 0.003536 0)", f"arc 0 3 ({c45} {c45} 0)"),
            ("arc 4 7 (0.003536 0.003536 0.05)", f"arc 4 7 ({c45} {c45} 0.05)")],
    }
    for rel, pairs in reps.items():
        p = dest / rel
        text = p.read_text()
        for old, new in pairs:
            if text.count(old) != 1:
                die(f"{p}: expected one '{old}'")
            text = text.replace(old, new)
        p.write_text(text)


# R5 preconditioner ablation variants (monolithic, 3dTube)
PC_VARIANTS = {
    "schur-upper": {"fieldsplit_fluid_pc_fieldsplit_schur_fact_type": "upper"},
    "lag1": {"snes_lag_jacobian": q(1), "snes_lag_preconditioner": q(1)},
    "ksp1e-4": {"ksp_rtol": q(1e-4)},
    "vel-amg": {"fieldsplit_fluid_fieldsplit_0_pc_type": "hypre",
                "fieldsplit_fluid_fieldsplit_0_pc_hypre_type": "boomeramg",
                "fieldsplit_fluid_fieldsplit_0_sub_pc_type": None,
                "fieldsplit_fluid_fieldsplit_0_sub_pc_factor_levels": None},
    "assembled": {"snes_mf_operator": None},
}


def apply_pc_variant(dest, name, meta):
    fvs = dest / "system/fvSolution.monolithic"
    if name == "solid-S0":
        set_petsc_options(fvs, "UpU", {}, drop_prefix="fieldsplit_solid_",
                          add=[("fieldsplit_solid_" + k, v) for k, v in S0],
                          note="ablation: solid block S0 redundant LU")
        meta["solid_pc"] = "redundant+lu (S0)"
    elif name in PC_VARIANTS:
        set_petsc_options(fvs, "UpU", PC_VARIANTS[name])
    else:
        die(f"unknown --pc {name}")
    meta["pc_variant"] = name


# ---------------------------------------------------------------------------
# Restart copies
# ---------------------------------------------------------------------------

def setup_restart(args):
    src, dest = Path(args.src), Path(args.dest)
    if dest.exists():
        die(f"{dest} exists")
    smeta = json.loads((src / "qm_run.json").read_text())
    t0 = args.from_time

    def is_time(n):
        return re.fullmatch(r"[0-9.eE+-]+", n) is not None

    def keep_time(n):
        return n == "0" or abs(float(n) - t0) < 1e-12

    def ignore(directory, names):
        skip = set()
        d = Path(directory)
        for n in names:
            if n.startswith(("log.", "postProcessing")) or n in (
                    "qm_result.json", "run_meta.json", "provenance.json",
                    "slurm", "steps.csv", "Allrun.prepare.done"):
                skip.add(n)
            elif is_time(n) and (d == src or d.parent == src
                                 and d.name.startswith("processor")):
                if not keep_time(n):
                    skip.add(n)
        return skip

    shutil.copytree(src, dest, symlinks=True, ignore=ignore)
    have = [p for p in dest.iterdir() if p.name.startswith("processor")] \
        or [dest]
    for p in have:
        if not any(is_time(n.name) and keep_time(n.name) and n.name != "0"
                   for n in p.iterdir()):
            die(f"{src}: time {t0:g} not written in {p.name}")
    control = dest / "system/controlDict"
    set_entry(control, "startFrom", "latestTime", top=True)
    set_entry(control, "endTime", f"{args.end:.10g}", top=True)
    if args.write_final_only:
        dt = float(smeta["dt"])
        steps = round((args.end - t0) / dt)
        if smeta["case"] == "3dTube":
            set_entry(control, "writeInterval", f"{args.end - t0:.10g}",
                      top=True)
        else:
            set_entry(control, "writeInterval", str(steps), top=True)
    meta = dict(smeta)
    meta.update(restart_from=str(src), t_start=t0, t_end=args.end,
                prepare=False)
    meta["edits"] = list(smeta.get("edits", [])) + [f"restart from t = {t0:g}"]
    if args.ranks and args.ranks != smeta["ranks"]:
        die("rank count of a restart must match its source")
    tol = parse_tol(args.tol)
    if tol:
        if smeta["coupling"] == "NewtonQuasiMonolithic":
            blocks = [(dest / "system/fvSolution.monolithic", "UpU")]
            if smeta["case"] == "TurekHron2006":
                blocks.append((dest / "system/fluid/fvSolution.monolithic", "Up"))
            apply_mono_tol(dest, tol, blocks)
        elif smeta["coupling"] == "IQNILS":
            apply_partitioned_tol(dest, tol, dest / "constant/fsiProperties.iqnils",
                                  "IQNILSCoeffs")
        else:
            apply_partitioned_tol(dest, tol, dest / "constant/fsiProperties.robin",
                                  "fixedRelaxationCoeffs")
        meta["tol"] = dict(smeta.get("tol", {}), **tol)
    if args.pc:
        apply_pc_variant(dest, args.pc, meta)
    (dest / "qm_run.json").write_text(json.dumps(meta, indent=1))
    print(dest)


def finish(dest, meta, args):
    meta["prepare"] = True
    meta["setup_args"] = vars(args)
    (dest / "qm_run.json").write_text(json.dumps(meta, indent=1, default=str))
    print(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("fsi3")
    a.add_argument("dest")
    a.add_argument("--coupling", choices=("mono", "iqn"), required=True)
    a.add_argument("--level", type=int, choices=(1, 2, 4), required=True)
    a.add_argument("--ranks", type=int, required=True)
    a.add_argument("--end", type=float, default=7.0)
    a.add_argument("--tol")
    b = sub.add_parser("tube")
    b.add_argument("dest")
    b.add_argument("--coupling", choices=("mono", "robin"), required=True)
    b.add_argument("--level", type=int, choices=(1, 2, 3), required=True)
    b.add_argument("--ranks", type=int, required=True)
    b.add_argument("--end", type=float, default=0.02)
    b.add_argument("--write-interval", type=float, default=0.004)
    b.add_argument("--tol")
    b.add_argument("--pc")
    b.add_argument("--exact-arcs", action="store_true")
    c = sub.add_parser("restart")
    c.add_argument("src")
    c.add_argument("dest")
    c.add_argument("--from", dest="from_time", type=float, required=True)
    c.add_argument("--end", type=float, required=True)
    c.add_argument("--ranks", type=int)
    c.add_argument("--tol")
    c.add_argument("--pc")
    c.add_argument("--write-final-only", action="store_true")
    args = ap.parse_args()
    {"fsi3": setup_fsi3, "tube": setup_tube, "restart": setup_restart}[args.cmd](args)


if __name__ == "__main__":
    main()
