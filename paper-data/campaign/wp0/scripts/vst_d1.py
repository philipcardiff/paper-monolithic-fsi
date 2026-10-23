#!/usr/bin/env python3
"""vST diagnostic D1: continue a converged quasi-monolithic blobInTreacle
state with the partitioned coupling (pimpleFluid, IQN-ILS, strict test).

The partitioned case is a copy of the converged WP0 partitioned run at the
same level (same mesh, schemes and set-up). Its last time directory is
overwritten with the QM state: the deformed fluid mesh points, fluid U, p,
meshPhi, V0 and the solid displacement fields (the solid is linear elastic
in both). The face velocity Uf and the flux phi are removed so that
pimpleFluid rebuilds them from U. The run then continues for --extra
seconds at the same time step; the drift of the top-point displacement
shows whether the partitioned discretisation keeps the QM state.

    vst_d1.py --qm QM_RUN --part PART_RUN --out NEW_RUN [--extra 1.0]
"""
import argparse
import re
import shutil
import subprocess
from pathlib import Path

FLUID = ["U", "U_0", "p", "meshPhi", "V0"]
FLUID_DROP = ["Uf", "Uf_0", "phi", "phi_0"]
SOLID = ["D", "D_0", "D_0_0", "D_0_0_0", "pointD", "sigma", "sigmaEq",
         "epsilon", "epsilonEq"]


def splice(src, dst):
    """Copy the internalField of src into dst, keeping dst's boundary
    conditions (the coupled patches differ between the formulations); a
    field without a boundaryField (V0) is copied whole."""
    a, b = src.read_text(), dst.read_text() if dst.is_file() else ""

    def cut(text):
        i = text.find("internalField")
        j = text.find("boundaryField")
        return i, j
    ia, ja = cut(a)
    ib, jb = cut(b)
    if ja < 0 or jb < 0:
        shutil.copy(src, dst)
        return
    dst.write_text(b[:ib] + a[ia:ja] + b[jb:])


def latest(case):
    return max((d for d in case.iterdir() if re.fullmatch(r"[0-9.]+", d.name)
                and d.name != "0"), key=lambda d: float(d.name))


def set_entry(path, key, value):
    text, n = re.subn(rf"^(\s*{key}\s+)[^;]+;", rf"\g<1>{value};",
                      path.read_text(), count=1, flags=re.MULTILINE)
    if n != 1:
        raise RuntimeError(f"no {key} in {path}")
    path.write_text(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qm", type=Path, required=True)
    ap.add_argument("--part", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--extra", type=float, default=1.0)
    ap.add_argument("--self", action="store_true",
                    help="control: continue the partitioned state itself")
    args = ap.parse_args()
    if args.out.exists():
        shutil.rmtree(args.out)
    shutil.copytree(args.part, args.out, symlinks=True)
    t = latest(args.out)
    for d in args.out.iterdir():
        if re.fullmatch(r"[0-9.]+", d.name) and d.name not in ("0", t.name):
            shutil.rmtree(d)
    for name in ("postProcessing",):
        shutil.rmtree(args.out / name, ignore_errors=True)
    for log in args.out.glob("log.solids4Foam*"):
        log.rename(log.with_name(log.name + ".orig"))
    if not args.self:
        q = latest(args.qm)
        if q.name != t.name:
            raise RuntimeError(f"time mismatch: QM {q.name}, partitioned {t.name}")
        tf, qf = t / "fluid", q / "fluid"
        shutil.copy(qf / "polyMesh/points", tf / "polyMesh/points")
        for name in FLUID:
            splice(qf / name, tf / name)
        splice(qf / "p", tf / "p_0")
        for name in FLUID_DROP:
            (tf / name).unlink(missing_ok=True)
        for name in SOLID:
            if (q / "solid" / name).is_file():
                splice(q / "solid" / name, t / "solid" / name)
    # linearElastic is a total-strain law: no incremental restart fields
    sp = args.out / "constant/solid/solidProperties"
    text, n = re.subn(r"(linearGeometryTotalDisplacementCoeffs\s*\{\n)",
                      r"\g<1>    restart no;\n", sp.read_text(), count=1)
    if n != 1:
        raise RuntimeError(f"no solid coefficients in {sp}")
    sp.write_text(text)
    control = args.out / "system/controlDict"
    set_entry(control, "startFrom", "latestTime")
    set_entry(control, "endTime", f"{float(t.name) + args.extra:.10g}")
    with (args.out / "log.solids4Foam").open("w") as log:
        subprocess.run(["solids4Foam"], cwd=args.out, stdout=log,
                       stderr=subprocess.STDOUT, check=False)


if __name__ == "__main__":
    main()
