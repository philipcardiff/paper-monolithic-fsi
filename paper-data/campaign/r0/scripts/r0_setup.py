#!/usr/bin/env python3
"""R0: prepare one quasi-monolithic run of a paper case at tutorial resolution.

Usage (inside the campaign environment, WM_PROJECT_USER_DIR = qm-head):

    r0_setup.py <case_key> <run_dir> [--ranks N] [--ddt-u backward|Euler]

Copies the tutorial of the solids4foam tree at $WM_PROJECT_USER_DIR/solids4foam
(the branch head that was built), including its verification driver, into
<run_dir>, without verification/work and postProcessing, and applies the R0
edits to the copy only:

- fluid ddt(U) in system/fluid/fvSchemes.monolithic set to --ddt-u
  (collapsibleChannel, cavityFlexibleBottom and blobInTreacle use Euler in
  the tutorial; the others already use backward);
- foilInWind: system/controlDict.monolithic with deltaT = 0.0025 s, taken
  verbatim from solids4foam b157ecaf3 (branch
  fix/foilInWind-monolithic-timestep, PR #602, not yet on the head), and the
  monolithic decomposition set to --ranks subdomains;
- 3dTube (run through its verification driver): the driver's BoomerAMG
  replacement of the solid block is changed, in the copied driver, to the B1
  S1 options (campaign/scripts/b1_setup.py CONFIGS["S1"], prefix
  fieldsplit_solid_);

Writes <run_dir>/r0_setup.json with the edits made.
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
S4F = Path(os.environ.get("WM_PROJECT_USER_DIR", "")) / "solids4foam"
TUT = S4F / "tutorials" / "fluidSolidInteraction"

CASES = {
    "ram": "ringAddedMass",
    "wom": "womersleyTube",
    "coll": "collapsibleChannel",
    "cav": "cavityFlexibleBottom",
    "blob": "blobInTreacle",
    "foil": "foilInWind",
    "tube": "3dTube",
    "fsi3": "TurekHron2006",
    "fsi1": "TurekHron2006",
}
# Cases run through their verification driver: the driver sets the time
# scheme itself (3dTube: --time-scheme; TurekHron2006: backward in the
# tutorial)
DRIVER = {"tube", "fsi3", "fsi1"}

# B1 S1 (campaign/scripts/b1_setup.py), prefix fieldsplit_solid_
S1 = [
    ("ksp_type", "preonly"),
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


def ignore(directory, names):
    skip = set()
    for n in names:
        if n.startswith(("processor", "log.", "postProcessing")) \
                or n in ("work", "__pycache__", ".solids4FoamCaseVariant"):
            skip.add(n)
        elif re.fullmatch(r"[0-9.eE+-]+", n) and n != "0" \
                and Path(directory).name != "constant":
            skip.add(n)
    return skip


def sub_entry(path, key, value, count=1):
    text = path.read_text()
    new, n = re.subn(rf"^(\s*{re.escape(key)}\s+)[^;]*;", rf"\g<1>{value};",
                     text, flags=re.MULTILINE)
    if n != count:
        sys.exit(f"{path}: expected {count} '{key}' entries, found {n}")
    path.write_text(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("case", choices=sorted(CASES))
    ap.add_argument("run_dir")
    ap.add_argument("--ranks", type=int, default=1)
    ap.add_argument("--ddt-u", default="backward", choices=("backward", "Euler"))
    args = ap.parse_args()

    src = TUT / CASES[args.case]
    dst = Path(args.run_dir)
    if dst.exists():
        sys.exit(f"{dst} exists; use a new run id")
    shutil.copytree(src, dst, symlinks=True, ignore=ignore)
    edits = []

    schemes = dst / "system/fluid/fvSchemes.monolithic"
    old = re.search(r"^\s*ddt\(U\)\s+(\w+);", schemes.read_text(),
                    flags=re.MULTILINE).group(1)
    if args.case not in DRIVER:
        if old != args.ddt_u:
            sub_entry(schemes, "ddt(U)", args.ddt_u)
            edits.append(f"fvSchemes.monolithic ddt(U) {old} -> {args.ddt_u}")
        else:
            edits.append(f"fvSchemes.monolithic ddt(U) {old} (tutorial)")

    if args.case == "foil":
        cd = dst / "system/controlDict.monolithic"
        if cd.exists():
            edits.append("controlDict.monolithic present on the head; kept")
        else:
            shutil.copy(HERE / "foilInWind.controlDict.monolithic.b157ecaf3", cd)
            edits.append("system/controlDict.monolithic from b157ecaf3 "
                         "(deltaT 0.0025, endTime 12)")
        # The project file quota (1e6 inodes, shared) cannot hold 100
        # retained writes x 128 processor directories: the first attempt
        # (r0-foil-backward-d) aborted at t = 0.14 s when mkDir failed.
        # The QoIs come from the function objects, written every step.
        sub_entry(cd, "writeInterval", "1")
        sub_entry(cd, "purgeWrite", "2")
        edits.append("controlDict.monolithic writeInterval 0.01 -> 1, "
                     "purgeWrite 100 -> 2 (file quota)")
        if args.ranks > 1:
            sub_entry(dst / "system/decomposeParDict.monolithic",
                      "numberOfSubdomains", str(args.ranks))
            edits.append(f"decomposeParDict.monolithic numberOfSubdomains "
                         f"{args.ranks} (method scotch, tutorial)")

    if args.case == "coll":
        # setPoiseuilleFlow's Make/options finds the solids4foam root by
        # searching upwards from the utility, which fails outside the tree;
        # point it at the built tree
        mo = dst / "setPoiseuilleFlow/Make/options"
        text = mo.read_text()
        new, n = re.subn(r"^SOLIDS4FOAM_ROOT := .*$",
                         "SOLIDS4FOAM_ROOT := " + str(S4F), text,
                         flags=re.MULTILINE)
        if n != 1:
            sys.exit(f"{mo}: SOLIDS4FOAM_ROOT line not found")
        mo.write_text(new)
        shutil.rmtree(dst / "setPoiseuilleFlow/Make" / os.environ.get(
            "WM_OPTIONS", "none"), ignore_errors=True)
        edits.append("setPoiseuilleFlow/Make/options: SOLIDS4FOAM_ROOT set "
                     "to the built tree (copy is outside the tree)")

    if args.case == "tube":
        drv = dst / "verification/scripts/tube_3d_verification.py"
        text = drv.read_text()
        anchor = ('"fieldsplit_solid_pc_type hypre;\\n"\n'
                  '            "            fieldsplit_solid_pc_hypre_type boomeramg;\\n"\n'
                  '            \'            fieldsplit_solid_pc_hypre_boomeramg_max_iter "1";\\n\'\n'
                  '            \'            fieldsplit_solid_pc_hypre_boomeramg_strong_threshold \'\n'
                  '            \'"0.7";\',')
        if text.count(anchor) != 1:
            sys.exit(f"{drv}: solid-block BoomerAMG replacement not found")
        s1 = "\\n            ".join(f"fieldsplit_solid_{k} {v};" for k, v in S1[1:])
        s1 = s1.replace('"', '\\"')
        text = text.replace(anchor, '"' + s1 + '",')
        drv.write_text(text)
        edits.append("copied 3dTube driver: monolithic solid block = B1 S1 "
                     "BoomerAMG options (fieldsplit_solid_*)")

    json.dump({"case": CASES[args.case], "key": args.case,
               "source": str(src), "ranks": args.ranks,
               "ddt_U_requested": args.ddt_u, "ddt_U_tutorial": old,
               "edits": edits}, open(dst / "r0_setup.json", "w"), indent=1)
    print("\n".join(edits))


if __name__ == "__main__":
    main()
