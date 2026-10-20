#!/usr/bin/env python3
"""Set up (and, for the static wall, run) the B2 collapsibleChannel cases.

The case set-up reuses the tutorial's own verification driver,
verification/scripts/collapsible_channel_verification.py, imported read-only
from the solids4foam tree: its static-wall procedure (run_static_case,
evaluate_static) and its FSI case configuration (configure_case: block
divisions of the fluid level and solid mesh, deltaT, endTime, AMI when the
interface faces do not match). Nothing is written into the solids4foam tree
(bytecode writing is disabled).

Usage (inside a job, after sourcing env.sh):

  b2_setup.py static <runs_dir> <run_id> <nx> <ny>
      Runs the static wall (linear partitioned solid, 20 load steps) in
      <runs_dir>/<run_id> and writes static_result.json there.

  b2_setup.py fsi <run_dir> --level L --solid NX NY --dt DT --end T
                  [--conservative]
      Copies the tutorial to <run_dir> and configures a monolithic case.
      AMI is selected by the driver when NX != 80*L; --conservative adds
      conservativeTractionTransfer yes (NewtonQuasiMonolithicCoeffs) and
      useUndeformedArea yes (solid D, interface patch).
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_TUTORIAL = (
    "/project/home/p201287/philip/qm-paper/solids4foam/tutorials/"
    "fluidSolidInteraction/collapsibleChannel"
)


def load_driver(tutorial: Path):
    path = tutorial / "verification" / "scripts" / \
        "collapsible_channel_verification.py"
    spec = importlib.util.spec_from_file_location("ccv", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cmd_static(args, driver):
    refs = driver.load_references()
    runs_dir = Path(args.runs_dir).resolve()
    runs_dir.mkdir(parents=True, exist_ok=True)
    driver.WORK_DIR = runs_dir
    case = {
        "name": args.run_id,
        "solid": (args.nx, args.ny),
        "solidType": "linear",
        "static": True,
    }
    status = "completed"
    row = {}
    try:
        run_dir = driver.run_static_case(case, refs, reuse=False)
        row = driver.evaluate_static(case, run_dir, refs)
    except RuntimeError as error:
        status = f"failed: {error}"
    result = {
        "run_id": args.run_id,
        "solid_mesh": f"{args.nx}x{args.ny}",
        "solid_type": "linear (partitioned solidProperties.linear)",
        "reference_wallMid": refs["studies"]["static"]["reference"]["wallMid"],
        "status": status,
        **row,
    }
    (runs_dir / args.run_id / "static_result.json").write_text(
        json.dumps(result, indent=1, default=str) + "\n"
    )
    print(json.dumps(result, default=str))
    return 0 if status == "completed" else 1


def cmd_fsi(args, driver):
    run_dir = Path(args.run_dir).resolve()
    if run_dir.exists():
        shutil.rmtree(run_dir)
    shutil.copytree(driver.CASE_DIR, run_dir, ignore=driver.ignored,
                    symlinks=True)
    case = {
        "name": run_dir.name,
        "fluid": args.level,
        "solid": (args.nx, args.ny),
        "dt": args.dt,
        "solidType": "linear",
        "coupling": "monolithic",
    }
    driver.configure_case(run_dir, case, args.end)

    fsi = run_dir / "constant" / "fsiProperties.monolithic"
    text = fsi.read_text()
    method = re.search(r"^\s*interfaceTransferMethod\s+(\w+);", text,
                       re.MULTILINE).group(1)
    if args.conservative:
        driver.replace_once(
            fsi,
            r"^(\s*interfaceTransferMethod\s+\w+;)",
            r"\g<1>\n\n    // B2: conservative force transfer through AMI\n"
            r"    conservativeTractionTransfer yes;",
        )
        driver.replace_once(
            run_dir / "0" / "solid" / "D",
            r"^(\s*interface\s*\n\s*\{\s*\n\s*type\s+solidTraction;)",
            r"\g<1>\n        useUndeformedArea yes;",
        )
    meta = {
        "level": args.level,
        "solid_mesh": f"{args.nx}x{args.ny}",
        "dt": args.dt,
        "end_time": args.end,
        "interfaceTransferMethod": method,
        "conservativeTractionTransfer": bool(args.conservative),
    }
    (run_dir / "b2_case.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--tutorial", default=DEFAULT_TUTORIAL)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("static")
    p.add_argument("runs_dir")
    p.add_argument("run_id")
    p.add_argument("nx", type=int)
    p.add_argument("ny", type=int)
    p = sub.add_parser("fsi")
    p.add_argument("run_dir")
    p.add_argument("--level", type=int, required=True)
    p.add_argument("--solid", nargs=2, type=int, required=True,
                   metavar=("NX", "NY"))
    p.add_argument("--dt", type=float, required=True)
    p.add_argument("--end", type=float, required=True)
    p.add_argument("--conservative", action="store_true")
    args = parser.parse_args()
    driver = load_driver(Path(args.tutorial))
    if args.cmd == "static":
        return cmd_static(args, driver)
    args.nx, args.ny = args.solid
    return cmd_fsi(args, driver)


if __name__ == "__main__":
    sys.exit(main())
