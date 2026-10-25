#!/usr/bin/env python3
"""Task farm inside one exclusive node allocation (R4/R5).

Usage:  farm.py TASKFILE --state STATE.json [--cores 0-127] [--poll 20]

TASKFILE, one task per line (re-read every poll, so tasks may be appended
while the farm runs; '#' starts a comment):

    <task_id> <ranks> <after> <command ...>

<after> is '-' or a comma-separated list of task ids that must have finished
with rc 0 first (a task whose dependency failed is marked 'skipped').
Tasks start in file order whenever enough cores are free. Each task gets its
own cores (env FARM_CORES, comma-separated), chosen inside one 16-core NUMA
domain when it fits (best fit), else whole free domains, else any free cores.
The farm ends when nothing runs and nothing can start. A file STOP next to
TASKFILE stops new launches.

Memory: every poll samples VmRSS of the solids4Foam processes, summed per
working directory; the per-directory peak is kept in STATE.
"""

import argparse
import json
import os
import shlex
import subprocess
import time
from pathlib import Path

DOMAIN = 16


def parse_cores(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def read_tasks(path):
    tasks = []
    for line in Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        tid, ranks, after, cmd = line.split(None, 3)
        tasks.append({"id": tid, "ranks": int(ranks),
                      "after": [] if after == "-" else after.split(","),
                      "cmd": cmd})
    return tasks


def choose(free, n, all_cores):
    domains = {}
    for c in all_cores:
        domains.setdefault(c // DOMAIN, []).append(c)
    if n <= DOMAIN:
        best = None
        for d, cs in domains.items():
            f = [c for c in cs if c in free]
            if len(f) >= n and (best is None or len(f) < len(best)):
                best = f
        if best:
            return best[:n]
    whole = [cs for cs in domains.values() if all(c in free for c in cs)]
    if len(whole) * DOMAIN >= n:
        flat = [c for cs in whole for c in cs]
        return flat[:n]
    if len(free) >= n and n > DOMAIN:
        return sorted(free)[:n]
    return None


def sample_memory(state):
    peaks = state.setdefault("mem_peak_kb", {})
    per = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if Path(f"/proc/{pid}/comm").read_text().strip() != "solids4Foam":
                continue
            cwd = os.readlink(f"/proc/{pid}/cwd")
            for ln in Path(f"/proc/{pid}/status").read_text().splitlines():
                if ln.startswith("VmRSS:"):
                    per[cwd] = per.get(cwd, 0) + int(ln.split()[1])
        except OSError:
            continue
    for cwd, kb in per.items():
        peaks[cwd] = max(peaks.get(cwd, 0), kb)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("taskfile")
    ap.add_argument("--state", required=True)
    ap.add_argument("--cores", default="0-127")
    ap.add_argument("--poll", type=float, default=20)
    args = ap.parse_args()
    all_cores = parse_cores(args.cores)
    free = set(all_cores)
    taskfile = Path(args.taskfile).resolve()
    logdir = taskfile.parent / "farm-logs"
    logdir.mkdir(exist_ok=True)
    state = {"job": os.environ.get("SLURM_JOB_ID"), "host": os.uname()[1],
             "tasks": {}}
    running = {}

    def save():
        tmp = Path(args.state + ".tmp")
        tmp.write_text(json.dumps(state, indent=1))
        tmp.replace(args.state)

    while True:
        # Reap
        for tid, (proc, cores) in list(running.items()):
            rc = proc.poll()
            if rc is not None:
                free.update(cores)
                st = state["tasks"][tid]
                st.update(state="done" if rc == 0 else "failed", rc=rc,
                          end=time.time(),
                          elapsed_s=round(time.time() - st["start"], 1))
                del running[tid]
        tasks = read_tasks(taskfile)
        stop = (taskfile.parent / "STOP").exists()
        launched_or_possible = False
        for t in tasks:
            tid = t["id"]
            if tid in state["tasks"]:
                continue
            deps = [state["tasks"].get(d, {}).get("state") for d in t["after"]]
            if any(s in ("failed", "skipped") for s in deps) or \
                    any(d not in {x["id"] for x in tasks} and d not in state["tasks"]
                        for d in t["after"]):
                state["tasks"][tid] = {"state": "skipped", "cmd": t["cmd"],
                                       "reason": "dependency failed or missing"}
                continue
            if not all(s == "done" for s in deps):
                launched_or_possible = True     # may start later
                continue
            if stop:
                continue
            if t["ranks"] > len(all_cores):
                state["tasks"][tid] = {"state": "skipped", "cmd": t["cmd"],
                                       "reason": "more ranks than cores"}
                continue
            cores = choose(free, t["ranks"], all_cores)
            if cores is None:
                launched_or_possible = True
                continue
            free.difference_update(cores)
            env = dict(os.environ, FARM_CORES=",".join(map(str, cores)),
                       FARM_TASK_ID=tid)
            out = open(logdir / f"{tid}.out", "w")
            proc = subprocess.Popen(["bash", "-c", t["cmd"]], env=env,
                                    stdout=out, stderr=subprocess.STDOUT,
                                    cwd=taskfile.parent)
            running[tid] = (proc, cores)
            state["tasks"][tid] = {"state": "running", "cmd": t["cmd"],
                                   "ranks": t["ranks"], "cores": cores,
                                   "start": time.time()}
            launched_or_possible = True
        sample_memory(state)
        state["free_cores"] = len(free)
        state["updated"] = time.time()
        save()
        if not running and not (launched_or_possible and not stop):
            break
        time.sleep(args.poll)
    state["finished"] = time.time()
    save()


if __name__ == "__main__":
    main()
