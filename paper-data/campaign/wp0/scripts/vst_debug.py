#!/usr/bin/env python3
"""vST yes debugging on blobInTreacle: QM variants against the WP0
partitioned runs (same machine, build and set-up as WP0: Δt 0.01, 0.01,
0.005 s at x1, x2, x4, to t = 3 s, backward, ranks 1/2/4).

    vst_debug.py EXPERIMENT [--cores 8]

Each experiment is a list of QM variants; results go to
runs/<id>/ma_result.json and a table against the partitioned u_x, u_y.
"""
import argparse
import importlib.util
import json
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
WP0 = Path("/Volumes/OpenFOAM/philipc-v2512/claude-runs/m-wp0")
WORK = Path("/Volumes/OpenFOAM/philipc-v2512/claude-runs/m-runs-a-work/vst")
MA = HERE.parents[1] / "m-runs-a/scripts/ma_run.py"
DT = {1: 0.01, 2: 0.01, 4: 0.005}
RANKS = {1: 1, 2: 2, 4: 4}

spec = importlib.util.spec_from_file_location("ma_run", MA)
ma = importlib.util.module_from_spec(spec)
sys.modules["ma_run"] = ma
spec.loader.exec_module(ma)


def variants(name):
    out = []
    levels = (1, 2, 4)
    if name == "E1":          # interpolate(U) linear, both vST settings
        for vst in ("yes", "no"):
            for lvl in levels:
                out.append(dict(tag=f"E1-vst{vst}-lin", level=lvl, vst=vst,
                                interp="linear"))
    if name == "E2":          # zeroGradient interface pressure (as pimple)
        for vst in ("yes", "no"):
            for lvl in levels:
                out.append(dict(tag=f"E2-vst{vst}-pzg", level=lvl, vst=vst,
                                p_interface="zeroGradient"))
    if name == "E3":          # zeroGradient interface p + interpolate(U) linear
        for vst in ("yes", "no"):
            for lvl in levels:
                out.append(dict(tag=f"E3-vst{vst}-pzg-lin", level=lvl, vst=vst,
                                p_interface="zeroGradient", interp="linear"))
    if name == "E4":          # fixed build (transpose always on, wall p
        for lvl in levels:    # gradient with it), tutorial set-up
            out.append(dict(tag="E4-fix", level=lvl, vst=None))
    if name == "E5":          # fixed build + interpolate(U) linear
        for lvl in levels:
            out.append(dict(tag="E5-fix-lin", level=lvl, vst=None,
                            interp="linear"))
    if name == "E6":          # fixed build + zeroGradient interface p
        for lvl in levels:
            out.append(dict(tag="E6-fix-pzg", level=lvl, vst=None,
                            p_interface="zeroGradient"))
    if name == "E7":          # fixed build + zeroGradient p + linear
        for lvl in levels:
            out.append(dict(tag="E7-fix-pzg-lin", level=lvl, vst=None,
                            p_interface="zeroGradient", interp="linear"))
    if name == "E8":          # fix + wall-velocity transpose evaluation
        for lvl in levels:
            out.append(dict(tag="E8-fixwall", level=lvl, vst=None))
    if name == "E9":          # E8 build + zeroGradient p + linear
        for lvl in levels:
            out.append(dict(tag="E9-fixwall-pzg-lin", level=lvl, vst=None,
                            p_interface="zeroGradient", interp="linear"))
    if name == "E8b":         # E8 with synced uniform point averages
        for lvl in levels:
            out.append(dict(tag="E8b-fixwall", level=lvl, vst=None))
        out.append(dict(tag="E8b-fixwall-serial", level=2, vst=None,
                        serial=True))
    if name == "E8c":         # least-squares surface gradient version
        for lvl in levels:
            out.append(dict(tag="E8c-fixls", level=lvl, vst=None))
        out.append(dict(tag="E8c-fixls-serial", level=2, vst=None,
                        serial=True))
    if name == "E10":         # final code + interpolate(U) linear (new tutorial)
        for lvl in levels:
            out.append(dict(tag="E10-final-lin", level=lvl, vst=None,
                            interp="linear"))
    if name == "E11":         # review fixes (wedge reflection, eigen reg.)
        for lvl in levels:
            out.append(dict(tag="E11-review", level=lvl, vst=None))
    if name == "E12":         # evaluation on all fixed-velocity boundaries
        for lvl in levels:
            out.append(dict(tag="E12-allfv-lin", level=lvl, vst=None,
                            interp="linear"))
    if name == "E13":         # cache refactor build (same set-up as E11)
        for lvl in levels:
            out.append(dict(tag="E13-cache", level=lvl, vst=None))
    for r in out:
        r.update(id=f"vst-{r['tag']}-x{r['level']}", case="blob", item="vst",
                 dt=DT[r["level"]], end_time=3.0,
                 ranks=1 if r.get("serial") else RANKS[r["level"]],
                 petsc={})
    return out


def partitioned(level):
    r = json.loads((WP0 / f"runs/wp0-blob-iqn-x{level}/wp0_result.json")
                   .read_text())
    return r["ux"], r["uy"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    todo = variants(a.experiment)
    if not a.report:
        s4f = WP0 / "s4f-qm-head"
        fsi = s4f / "tutorials/fluidSolidInteraction"
        blob = ma.load("blobdrv", fsi / "blobInTreacle/verification/scripts/"
                       "blob_in_treacle_verification.py")
        WORK.mkdir(parents=True, exist_ok=True)
        ctx = dict(blob=blob, runs=WORK, s4f=s4f,
                   provenance=WP0 / "scripts/provenance.py")
        sem = threading.Semaphore(a.cores)
        threads = []

        def work(r):
            try:
                ma.execute(ctx, r)
            finally:
                for _ in range(r["ranks"]):
                    sem.release()
        for r in sorted(todo, key=lambda r: -r["level"]):
            for _ in range(r["ranks"]):
                sem.acquire()
            t = threading.Thread(target=work, args=(r,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    print(f"{'run':28s} {'u_x':>10s} {'d u_x':>8s} {'u_y':>11s} {'d u_y':>8s} Newton")
    for r in todo:
        f = WORK / r["id"] / "ma_result.json"
        res = json.loads(f.read_text()) if f.is_file() else {"status": "missing"}
        if res.get("status") != "completed":
            print(f"{r['id']:28s} {res.get('status')} {res.get('error', '')[:80]}")
            continue
        px, py = partitioned(r["level"])
        print(f"{r['id']:28s} {res['ux']:10.6f} {100*(res['ux']-px)/abs(px):+7.3f}% "
              f"{res['uy']:11.6f} {100*(res['uy']-py)/abs(py):+7.3f}% "
              f"{res['iters_mean']:.2f}")


if __name__ == "__main__":
    main()
