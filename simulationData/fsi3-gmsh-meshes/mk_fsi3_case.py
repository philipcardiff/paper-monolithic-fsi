#!/usr/bin/env python3
"""FSI3 coupled case on the gmsh tip-only fluid mesh family (t1-t4).

From the a421f063d TurekHron2006 tutorial (extracted in ./tut):
  fluid mesh   gmsh level L (~/claude-runs/agent-b-gmsh/tL/constant/polyMesh);
  solid mesh   the tutorial plate geometry, uniform cells of about the fluid
               plate spacing (430 x 24 at L1, x sqrt2 per level);
  transfer     AMI (the interfaces are non-conformal);
  mesh motion  solids4foamSolidModel, diffusionElastic, linear inverseDistance
               2(plate cylinder) (the gate that passed L2-L4), solid model
               --motion: meshMotionTotalDisplacement (accepted by both
               couplings) or linearGeometryTotalDisplacement (QM only);
  coupling     qm: the *.monolithic variant; iqn: IQN-ILS, outerCorrTolerance
               --iqn-tol, requireAllResidualMeasures yes.
Run control: 0-2 s rigid (coupled no) at --dt-rigid, then coupled to --end at
--dt (run_fsi3.sh switches the time step at 2 s).

    python3 mk_fsi3_case.py --level 1 --coupling qm --out runs/qm_1 --ranks 8
"""
import argparse
import math
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TUT = HERE / "tut"
GMSH = Path(os.environ.get("FSI3_GMSH", Path.home() / "claude-runs/agent-b-gmsh"))


def rm(p):
    if p.is_symlink() or p.exists():
        p.unlink()


def sub(path, pattern, repl, count=1, flags=re.M):
    t = path.read_text()
    t2, n = re.subn(pattern, repl, t, count=count, flags=flags)
    if n == 0:
        raise SystemExit(f"{path}: no match for {pattern!r}")
    path.write_text(t2)


def header(cls, obj):
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {cls};\n    object      {obj};\n}}\n\n")


def block(text, name):
    """The '    name ... { ... }' entry of a solvers dictionary."""
    i = text.index(f"    {name}")
    depth, j = 0, text.index("{", i)
    for k in range(j, len(text)):
        depth += text[k] == "{"
        depth -= text[k] == "}"
        if depth == 0:
            return text[i:k + 1]
    raise SystemExit(f"{name} not closed")


def insert_after_open(text, key, add):
    i = text.index("{", text.index(key)) + 1
    return text[:i] + "\n" + add + text[i:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--coupling", choices=("qm", "iqn"), required=True)
    ap.add_argument("--motion", default="meshMotionTotalDisplacement",
                    choices=("meshMotionTotalDisplacement", "linearGeometryTotalDisplacement"))
    ap.add_argument("--dt", type=float, help="coupled time step (default 2e-4/sqrt2^(L-1))")
    ap.add_argument("--dt-rigid", type=float, help="0-2 s time step (default 2.5 dt)")
    ap.add_argument("--end", type=float, default=6.0)
    ap.add_argument("--write", type=float, default=0.5)
    ap.add_argument("--iqn-tol", type=float, default=1e-6)
    ap.add_argument("--solid-factor", type=float, default=1.0, help="solid cells per direction relative to the level default")
    ap.add_argument("--ranks", type=int, default=1)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    s = math.sqrt(2) ** (a.level - 1)
    dt = a.dt or 2e-4 / s
    dtr = a.dt_rigid or 2.5 * dt
    c = a.out
    if c.exists():
        raise SystemExit(f"{c} exists")
    shutil.copytree(TUT, c, symlinks=True)
    for f in ("Allrun", "Allclean", "regressionTest.sh", "deflection.gnuplot", "force.gnuplot", "README.md"):
        rm(c / f)

    # coupling variant
    if a.coupling == "qm":
        for v in sorted(c.rglob("*.monolithic")):
            rm(v.with_suffix(""))
            shutil.copyfile(v, v.with_suffix(""))
        fsi = c / "constant/fsiProperties"
        sub(fsi, r"interfaceTransferMethod\s+directMap;", "interfaceTransferMethod AMI;")
    else:
        for name, var in (("constant/fsiProperties", "fsiProperties.iqnils"),
                          ("0/fluid/U", "U.dirichletNeumann"), ("0/fluid/p", "p.dirichletNeumann")):
            rm(c / name)
            shutil.copyfile((c / name).parent / var, c / name)
        fsi = c / "constant/fsiProperties"
        sub(fsi, r"outerCorrTolerance\s+[^;]*;", f"outerCorrTolerance   {a.iqn_tol:g};")
        sub(fsi, r"nOuterCorr\s+[^;]*;", "nOuterCorr           50;\n    requireAllResidualMeasures yes;")
        # mesh motion fields and settings from the monolithic variant
        # the same plate block structure as the monolithic solid mesh
        shutil.copyfile(c / "system/solid/blockMeshDict.monolithic", c / "system/solid/blockMeshDict")
        for f in ("0/fluid/D", "0/fluid/pointD", "0/fluid/pointDisplacement"):
            shutil.copyfile(c / f"{f}.monolithic", c / f)
        (c / "0/fluid/pointMotionU").unlink()
        fs = c / "system/fluid/fvSolution"
        dblk = block((c / "system/fluid/fvSolution.monolithic").read_text(), "D // fluid mesh motion")
        fs.write_text(insert_after_open(fs.read_text(), "solvers", dblk + "\n"))
        sc = c / "system/fluid/fvSchemes"
        t = sc.read_text()
        t = insert_after_open(t, "ddtSchemes", "    d2dt2(D) steadyState;\n")
        t = insert_after_open(t, "gradSchemes", "    grad(D) leastSquaresS4f;\n")
        t = re.sub(r"(laplacianSchemes\s*\{\s*)default none;", r"\1default Gauss linear corrected;", t)
        t += "\nd2dt2Schemes\n{\n    default steadyState;\n}\n"
        sc.write_text(t)
    for v in sorted(c.rglob("*.monolithic")) + sorted(c.rglob("*.robin")) + sorted(c.rglob("*.dirichletNeumann")) \
            + [c / "constant/fsiProperties.iqnils"]:
        rm(v)

    # mesh motion: diffusionElastic, linear inverse distance
    cf = c / "constant/fluid"
    (cf / "dynamicMeshDict").write_text(header("dictionary", "dynamicMeshDict") + (
        "dynamicFvMesh   dynamicMotionSolverFvMesh;\n"
        "motionSolverLibs (solids4FoamModels fvMotionSolvers);\n"
        "motionSolver    solids4foamSolidModel;\n"
        "regionName      fluid;\n"
        "diffusivity     inverseDistance 2(plate cylinder);\n"
        "writeStiffScaleFactor no;\n"))
    (cf / "solidProperties").write_text(header("dictionary", "solidProperties") + (
        f"solidModel      {a.motion};\n{a.motion}Coeffs\n{{\n    solutionAlgorithm PETScSNES;\n}}\n"))
    (cf / "mechanicalProperties").write_text(header("dictionary", "mechanicalProperties") + (
        "planeStress     no;\nmechanical\n(\n    rubber\n    {\n        type        diffusionElastic;\n"
        "        rho         rho [1 -3 0 0 0 0 0] 1;\n        mu          mu [1 -1 -2 0 0 0 0] 1;\n"
        "        K           K [1 -1 -2 0 0 0 0] 3;\n    }\n);\n"))
    # the interior mesh only needs to be smooth: loose Krylov tolerance (31 Oct)
    fs = c / "system/fluid/fvSolution"
    sub(fs, r"(    D // fluid mesh motion[\s\S]*?ksp_type lgmres;)", r'\1\n            ksp_rtol "1e-2";')
    sc = c / "system/fluid/fvSchemes"
    sc.write_text(insert_after_open(sc.read_text(), "laplacianSchemes",
                                    "    laplacian(interpolate(impK),D) Gauss linear corrected;\n"))

    # the run restarts at the switch to coupling (and after any requeue): the
    # solid models must write their restart fields
    for sp in (c / "constant/solid/solidProperties", cf / "solidProperties"):
        sub(sp, r"(Coeffs\"?\s*\{)", r"\1\n    restart yes;")

    # fluid mesh: gmsh level L
    pm = cf / "polyMesh"
    shutil.rmtree(pm, ignore_errors=True)
    shutil.copytree(GMSH / f"t{a.level}/constant/polyMesh", pm)
    rm(c / "system/fluid/blockMeshDict")

    # solid mesh: about the fluid plate spacing (430 along, 24 across at L1)
    n1, n2, ny = (round(v * s * a.solid_factor) for v in (62, 368, 24))
    bm = c / "system/solid/blockMeshDict"
    sub(bm, r"hex \(0 1 4 5 6 7 10 11\) \(\d+ \d+ 1\)", f"hex (0 1 4 5 6 7 10 11) ({n1} {ny} 1)")
    sub(bm, r"hex \(1 2 3 4 7 8 9 10\) \(\d+ \d+ 1\)", f"hex (1 2 3 4 7 8 9 10) ({n2} {ny} 1)")

    # run control: rigid phase first
    cd = c / "system/controlDict"
    sub(cd, r"^deltaT\s+[^;]*;", f"deltaT          {dtr:.10g};")
    sub(cd, r"^endTime\s+[^;]*;", "endTime         2;")
    sub(cd, r"^writeControl\s+[^;]*;", "writeControl    adjustableRunTime;")
    sub(cd, r"^writeInterval\s+[^;]*;", f"writeInterval   {a.write:g};")
    sub(cd, r"^timePrecision\s+[^;]*;", "timePrecision   8;")
    for d in (c / "system/fluid/decomposeParDict", c / "system/solid/decomposeParDict", c / "system/decomposeParDict"):
        if d.exists():
            t = re.sub(r"(?m)^numberOfSubdomains\s+\d+;", f"numberOfSubdomains {a.ranks};", d.read_text())
            t = re.sub(r"(?m)^method\s+\w+;", "method          scotch;", t)
            d.write_text(t)
    (c / "case.env").write_text(f"LEVEL={a.level}\nCOUPLING={a.coupling}\nMOTION={a.motion}\nDT={dt:.10g}\n"
                                f"DT_RIGID={dtr:.10g}\nEND={a.end:g}\nRANKS={a.ranks}\nSOLID=\"{n1}+{n2} x {ny}\"\n")
    print(c, f"L{a.level} {a.coupling} dt {dt:.4g} rigid {dtr:.4g} solid {n1}+{n2}x{ny}")


if __name__ == "__main__":
    main()
