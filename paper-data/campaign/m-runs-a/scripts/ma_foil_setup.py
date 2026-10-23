#!/usr/bin/env python3
"""7a foilInWind set-up: QM at a given time step to 0.2 s, or IQN-ILS.

QM: the R0 set-up (r0_setup.py foil: controlDict.monolithic from b157ecaf3,
128-rank decomposition, writeInterval 1, purgeWrite 2), then deltaT and
endTime 0.2 s, viscousStressTranspose no, div(phi,U) linearUpwind grad(U).
The tutorial's snes_monitor gives the Newton histories.

IQN-ILS: a copy of the tutorial (default variant), deltaT, endTime 0.2 s,
the strict coupling test (couplingReuse 0 is in the tutorial), the same
convection entry, 128 subdomains and the end time as the only write.

    ma_foil_setup.py {qm|iqn} RUN_DIR --dt DT --ranks N --qm-root DIR
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def sub1(path, pattern, repl):
    text, n = re.subn(pattern, repl, path.read_text(), count=1,
                      flags=re.MULTILINE)
    if n != 1:
        raise RuntimeError(f"no match for {pattern!r} in {path}")
    path.write_text(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coupling", choices=("qm", "iqn"))
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--dt", type=float, required=True)
    ap.add_argument("--end", type=float, default=0.2)
    ap.add_argument("--ranks", type=int, default=128)
    ap.add_argument("--qm-root", type=Path, required=True)
    a = ap.parse_args()
    d = a.run_dir
    if d.exists():
        shutil.rmtree(d)
    if a.coupling == "qm":
        subprocess.run([sys.executable,
                        str(a.qm_root / "campaign/scripts/r0_setup.py"),
                        "foil", str(d), "--ranks", str(a.ranks),
                        "--ddt-u", "backward"], check=True)
        cd = d / "system/controlDict.monolithic"
        sub1(d / "constant/fluid/fluidProperties.monolithic",
             r"(newtonIcoFluidCoeffs\s*\{\n)",
             r"\g<1>    viscousStressTranspose no;\n\n")
        schemes = d / "system/fluid/fvSchemes.monolithic"
    else:
        src = a.qm_root / "solids4foam/tutorials/fluidSolidInteraction/foilInWind"
        shutil.copytree(src, d, symlinks=True)
        cd = d / "system/controlDict"
        sub1(cd, r"(^writeInterval\s+)[^;]+;", rf"\g<1>{a.end:g};")
        sub1(d / "constant/fsiProperties",
             r"(^\s*writeResidualsToFile\s+yes;\n)",
             r"\g<1>    requireAllResidualMeasures yes;\n")
        for p in [d / "system/decomposeParDict",
                  *d.glob("system/*/decomposeParDict")]:
            sub1(p, r"(numberOfSubdomains\s+)\d+;", rf"\g<1>{a.ranks};")
        schemes = d / "system/fluid/fvSchemes"
    sub1(cd, r"(^deltaT\s+)[^;]+;", rf"\g<1>{a.dt:g};")
    sub1(cd, r"(^endTime\s+)[^;]+;", rf"\g<1>{a.end:g};")
    # Same convection entry for both; the cellLimited word never applied a
    # limiter (solids4foam #553)
    sub1(schemes, r"(^\s*div\(phi,U\)\s+)[^;]+;",
         r"\g<1>Gauss linearUpwind grad(U);")
    print(f"set up {d}")


if __name__ == "__main__":
    main()
