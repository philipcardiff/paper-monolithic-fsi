#!/usr/bin/env python3
"""Write provenance.json into an OpenFOAM/solids4foam case directory.

Usage (inside the run environment, after sourcing OpenFOAM and PETSc):

    provenance.py <case_dir> --ranks N [--run-id ID] [--s4f DIR] [--out FILE]

Records the solids4foam commit (git describe --always --dirty and the full
hash), OpenFOAM version, PETSc/HYPRE/MUMPS versions, compiler and flags,
host, CPU model, rank count, Slurm allocation (exclusive or shared), date,
and every PETSc `options { ... }` block found in the case's fvSolution files.
"""

import argparse
import datetime
import glob
import json
import os
import re
import socket
import subprocess


def run(cmd, cwd=None):
    try:
        out = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, timeout=60)
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def header_define(paths, name, numeric_parts=None):
    """Return the value of a #define from the first header that has it."""
    for path in paths:
        if not os.path.isfile(path):
            continue
        text = open(path, errors="replace").read()
        if numeric_parts:
            vals = []
            for part in numeric_parts:
                m = re.search(r"#define\s+%s\s+(\S+)" % part, text)
                if not m:
                    break
                vals.append(m.group(1))
            else:
                return ".".join(vals), path
        else:
            m = re.search(r"#define\s+%s\s+\"?([^\"\n]+)\"?" % name, text)
            if m:
                return m.group(1).strip(), path
    return None, None


def petsc_include_dirs():
    pdir = os.environ.get("PETSC_DIR", "")
    parch = os.environ.get("PETSC_ARCH", "")
    dirs = [os.path.join(pdir, parch, "include"), os.path.join(pdir, "include")]
    for var in ("EBROOTHYPRE", "EBROOTMUMPS"):
        if os.environ.get(var):
            dirs.append(os.path.join(os.environ[var], "include"))
    return [d for d in dirs if os.path.isdir(d)]


def library_versions():
    incs = petsc_include_dirs()
    petsc, _ = header_define(
        [os.path.join(d, "petscversion.h") for d in incs], None,
        ["PETSC_VERSION_MAJOR", "PETSC_VERSION_MINOR",
         "PETSC_VERSION_SUBMINOR"])
    hypre, _ = header_define(
        [os.path.join(d, "HYPRE_config.h") for d in incs],
        "HYPRE_RELEASE_VERSION")
    mumps, _ = header_define(
        [os.path.join(d, "dmumps_c.h") for d in incs], "MUMPS_VERSION")
    conf = [os.path.join(d, "petscconf.h") for d in incs]
    have = {}
    for key in ("HYPRE", "MUMPS", "SUPERLU_DIST"):
        val, _ = header_define(conf, "PETSC_HAVE_%s" % key)
        have[key.lower()] = val == "1"
    return {
        "petsc_dir": os.environ.get("PETSC_DIR"),
        "petsc_arch": os.environ.get("PETSC_ARCH"),
        "petsc_version": petsc,
        "hypre_version": hypre,
        "mumps_version": mumps,
        "petsc_has": have,
    }


def compiler_info():
    cc = os.environ.get("WM_CXX") or "g++"
    version = run([cc, "--version"])
    flags = run("wmake -show-cxxflags 2>/dev/null")
    return {
        "wm_compiler": os.environ.get("WM_COMPILER"),
        "wm_cxx": cc,
        "compiler_version": version.splitlines()[0] if version else None,
        "wm_compile_option": os.environ.get("WM_COMPILE_OPTION"),
        "wm_options": os.environ.get("WM_OPTIONS"),
        "wm_mplib": os.environ.get("WM_MPLIB"),
        "compile_flags": flags,
    }


def cpu_model():
    out = run(["lscpu"]) or ""
    for line in out.splitlines():
        if line.startswith("Model name:"):
            return line.split(":", 1)[1].strip()
    return None


def slurm_info():
    keys = ["SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID",
            "SLURM_JOB_PARTITION", "SLURM_JOB_NODELIST", "SLURM_JOB_NUM_NODES",
            "SLURM_NTASKS", "SLURM_CPUS_PER_TASK", "SLURM_CPU_BIND",
            "SLURM_DISTRIBUTION"]
    info = {k.lower(): os.environ.get(k) for k in keys if os.environ.get(k)}
    jid = os.environ.get("SLURM_JOB_ID")
    if jid:
        out = run(["scontrol", "show", "job", jid]) or ""
        m = re.search(r"OverSubscribe=(\S+)", out)
        info["oversubscribe"] = m.group(1) if m else None
        # OverSubscribe=NO means the job holds its nodes exclusively
        info["exclusive"] = (m.group(1) == "NO") if m else None
    else:
        info["exclusive"] = None
    return info


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def petsc_option_blocks(case):
    """Return {file: {solver: {option: value}}} for every `options` block."""
    result = {}
    files = sorted(set(glob.glob(os.path.join(case, "system", "fvSolution"))
                       + glob.glob(os.path.join(case, "system", "*",
                                                "fvSolution"))))
    for path in files:
        text = strip_comments(open(path, errors="replace").read())
        blocks = {}
        for m in re.finditer(r"([\"\w|()\-.*]+)\s*\{", text):
            name = m.group(1).strip('"')
            # Find the matching brace of this entry
            depth, i = 1, m.end()
            while depth and i < len(text):
                depth += {"{": 1, "}": -1}.get(text[i], 0)
                i += 1
            body = text[m.end():i - 1]
            # `solver petsc;` must be a direct entry, not in a sub-dictionary
            top = body
            while re.search(r"\{[^{}]*\}", top):
                top = re.sub(r"\{[^{}]*\}", "", top)
            if not re.search(r"\bsolver\s+petsc\s*;", top):
                continue
            om = re.search(r"\boptions\s*\{", body)
            if not om:
                continue
            depth, j = 1, om.end()
            while depth and j < len(body):
                depth += {"{": 1, "}": -1}.get(body[j], 0)
                j += 1
            opts = {}
            for line in body[om.end():j - 1].split(";"):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 1)
                opts[parts[0]] = parts[1].strip('"') if len(parts) > 1 else ""
            blocks[name] = opts
        if blocks:
            result[os.path.relpath(path, case)] = blocks
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("case")
    ap.add_argument("--ranks", type=int, required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--s4f", help="solids4foam source tree "
                    "(default: $WM_PROJECT_USER_DIR/solids4foam)")
    ap.add_argument("--out", help="output file (default: <case>/provenance.json)")
    args = ap.parse_args()

    case = os.path.abspath(args.case)
    s4f = args.s4f or os.path.join(os.environ.get("WM_PROJECT_USER_DIR", ""),
                                   "solids4foam")
    data = {
        "run_id": args.run_id or os.path.basename(case),
        "case": case,
        "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "solids4foam": {
            "path": s4f,
            "describe": run(["git", "describe", "--always", "--dirty"], s4f),
            "commit": run(["git", "rev-parse", "HEAD"], s4f),
            "tags_at_head": run(["git", "tag", "--points-at", "HEAD"], s4f),
        },
        "openfoam": {
            "version": os.environ.get("WM_PROJECT_VERSION"),
            "dir": os.environ.get("WM_PROJECT_DIR"),
            "foam_api": os.environ.get("FOAM_API"),
        },
        "libraries": library_versions(),
        "compiler": compiler_info(),
        "host": socket.gethostname(),
        "cpu_model": cpu_model(),
        "ranks": args.ranks,
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "slurm": slurm_info(),
        "petsc_options": petsc_option_blocks(case),
    }
    out = args.out or os.path.join(case, "provenance.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")
    print(out)


if __name__ == "__main__":
    main()
