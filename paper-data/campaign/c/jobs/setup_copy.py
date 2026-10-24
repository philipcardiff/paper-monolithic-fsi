#!/usr/bin/env python3
"""Copy a tutorial into a run directory for agent C (fix build).

  setup_copy.py SRC DEST [--tube-write-env]

The tutorial files are used as they are (solids4foam 1252bd2e5: #618 and
the #617 schemes). Checks that no run-copy file sets the removed
viscousStressTranspose option. --tube-write-env makes the 3dTube driver
take writeInterval from $AGENTC_WRITE_INTERVAL (s, runTime) instead of
writing only at the end time, for the 5 ms restart state and field images.
"""
import argparse, json, shutil, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dest")
ap.add_argument("--tube-write-env", action="store_true")
a = ap.parse_args()
src, dest = Path(a.src), Path(a.dest)
if dest.exists():
    sys.exit(f"{dest} exists")
shutil.copytree(src, dest, symlinks=True,
                ignore=shutil.ignore_patterns("work", "postProcessing"))
edits = []
hits = [str(f.relative_to(dest)) for f in dest.rglob("*")
        if f.is_file() and not f.is_symlink() and f.suffix not in (".png", ".pdf")
        and "viscousStressTranspose" in f.read_text(errors="ignore")
        and "/verification/" not in str(f) and not f.name.endswith(".md")]
assert not hits, f"viscousStressTranspose set in {hits}"
if a.tube_write_env:
    p = dest / "verification/scripts/tube_3d_verification.py"
    t = p.read_text()
    old = 'replace_entry(control, "writeInterval", f"{end_time:.10g}", True)'
    assert t.count(old) == 1
    t = t.replace(old, 'replace_entry(control, "writeInterval", '
                  'os.environ.get("AGENTC_WRITE_INTERVAL", f"{end_time:.10g}"), True)')
    if "\nimport os\n" not in t:
        t = t.replace("\nimport ", "\nimport os\nimport ", 1)
    p.write_text(t)
    edits.append("verification/scripts/tube_3d_verification.py: writeInterval from $AGENTC_WRITE_INTERVAL")
(dest / "agentC_setup.json").write_text(json.dumps(
    {"source": str(src), "edits": edits}, indent=1) + "\n")
print("\n".join(edits) or "no edits")
