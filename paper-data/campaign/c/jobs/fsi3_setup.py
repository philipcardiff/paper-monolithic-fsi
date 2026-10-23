#!/usr/bin/env python3
"""Copy the TurekHron2006 tutorial into a run directory and apply the
agent C 1x-check variant edits to the quasi-monolithic files.

  fsi3_setup.py SRC DEST --div {cellLimited,aligned} --vst {yes,no}
"""
import argparse, json, re, shutil, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dest")
ap.add_argument("--div", choices=("cellLimited", "aligned"), required=True)
ap.add_argument("--vst", choices=("yes", "no"), required=True)
a = ap.parse_args()
src, dest = Path(a.src), Path(a.dest)
if dest.exists():
    sys.exit(f"{dest} exists")
shutil.copytree(src, dest, symlinks=True,
                ignore=shutil.ignore_patterns("work", "postProcessing"))
edits = []

sch = dest / "system/fluid/fvSchemes.monolithic"
t = sch.read_text()
old = "Gauss linearUpwind cellLimited leastSquares 1;"
assert old in t, "unexpected div(phi,U) in fvSchemes.monolithic"
assert re.search(r"ddt\(U\)\s+backward;", t), "ddt(U) is not backward"
assert re.search(r"gradSchemes\s*\{\s*default\s+leastSquares;", t)
if a.div == "aligned":
    t = t.replace(old, "Gauss linearUpwind grad(U);")
    sch.write_text(t)
    edits.append("system/fluid/fvSchemes.monolithic: div(phi,U) Gauss linearUpwind grad(U)")

fp = dest / "constant/fluid/fluidProperties.monolithic"
t = fp.read_text()
assert "viscousStressTranspose" not in t
t, n = re.subn(r"(newtonIcoFluidCoeffs\s*\{\n)",
               r"\1    // Agent C 1x check: set explicitly\n"
               rf"    viscousStressTranspose {a.vst};\n\n", t, count=1)
assert n == 1
fp.write_text(t)
edits.append(f"constant/fluid/fluidProperties.monolithic: viscousStressTranspose {a.vst}")

(dest / "agentC_setup.json").write_text(json.dumps(
    {"source": str(src), "div_phi_U": a.div, "viscousStressTranspose": a.vst,
     "edits": edits}, indent=1) + "\n")
print("\n".join(edits))
