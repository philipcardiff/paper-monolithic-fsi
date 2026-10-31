#!/usr/bin/env python3
"""Check or claim rows of the shared run registry (registry.csv).

    registry.py check CASE [key=value ...]   list rows for CASE matching the filters
    registry.py claim CASE key=value ...      append a claimed row (then commit and push)

Filters and values use the column names of registry.csv; a filter matches
when its value occurs in the cell (case-insensitive).
"""
import csv
import datetime
import sys
from pathlib import Path

CSV = Path(__file__).with_name("registry.csv")


def rows():
    with CSV.open(newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def parse(args):
    kv = {}
    for a in args:
        k, v = a.split("=", 1)
        kv[k] = v
    return kv


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("check", "claim"):
        raise SystemExit(__doc__)
    cmd, case, kv = sys.argv[1], sys.argv[2], parse(sys.argv[3:])
    fields, data = rows()
    bad = [k for k in kv if k not in fields]
    if bad:
        raise SystemExit(f"unknown column(s): {bad}")
    if cmd == "check":
        for row in data:
            if case.lower() not in row["case"].lower():
                continue
            if all(v.lower() in row[k].lower() for k, v in kv.items()):
                print(" | ".join(row[k] for k in (
                    "coupling", "level", "dt", "ddt_fluid", "solid_model",
                    "code_class", "machine", "owner", "status",
                    "result_path")))
        return
    row = {k: "" for k in fields}
    row.update(kv, case=case, status="claimed",
               date=datetime.date.today().isoformat())
    if not row["owner"]:
        raise SystemExit("claim needs owner=NAME")
    with CSV.open("a", newline="") as f:
        csv.DictWriter(f, fieldnames=fields).writerow(row)
    print("claimed; commit and push registry.csv before submitting")


if __name__ == "__main__":
    main()
