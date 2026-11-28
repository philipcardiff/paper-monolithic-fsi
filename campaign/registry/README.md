# Shared run registry (solver paper M and verification paper V)

`registry.csv` lists every simulation run whose result one of the two papers
uses or plans to use: done, running and claimed. Its purpose is to stop two
agents (or two people) running the same case on xenosim, MeluXina or the
mac-studio, and to say where each result lives.

## Rules

1. **Check before you run.** Search the registry for the case with
   `registry.py check <case> [filters]`, or open the CSV. A row matches when
   case, coupling, mesh_family, level, dt, ddt_fluid, solid_model, rho_ratio,
   couplingReuse, convergence_test and code_class agree. If a matching row is
   `done` or `running`, reuse it. If it is `claimed` by someone else, ask
   them before running.
2. **Claim before you submit.** Add a row with `status = claimed`, your
   owner name and today's date, commit and push it, then submit. Add the job
   ID when you have one and set `status = running`.
3. **Claims lapse.** A claim with no job ID after 24 hours, or a `running`
   row with no update after 7 days, may be taken over by someone else (note it
   in `notes`).
4. **Close the row.** When a run finishes, set `status = done` (or `failed`)
   and fill `result_path` as `repo:branch:path` (or a machine path if the
   result is not pushed yet, prefixed with the machine name).
5. **Timing rows.** A cost or timing result counts only from a MeluXina
   exclusive node (`machine = Mx`). On MeluXina use project p201136
   (Amirhossein and Colm) first, the "xenosim" project only if needed, and
   never the project used by Petar and Simon for the Hron–Turek runs.
6. **Code class.** `code_class` says which code a result belongs to:
   `pre546`, `dev`, `dev+546`, `pre597`, `E597` (#597 present, the
   transpose term off: solver commits `257b2e564` to `85b0c1de6`), or
   `head` (the solver branch head at run time; give the commit in `notes`
   or the run directory). The M coordinator decides when a code change makes
   a class stale and marks those rows `superseded`.
7. **Status values:** `claimed`, `running`, `done`, `failed`, `superseded`.

## Columns

`case, coupling, mesh_family, level, solid_mesh, interface_transfer, dt,
ddt_fluid, solid_model, rho_ratio, couplingReuse, convergence_test,
tolerances, solid_pc, vST, code_class, purpose, machine, ranks, owner,
branch, job_id, status, result_path, date, notes`

- coupling: `QM` (quasi-monolithic Newton), `QM-AMI`, `IQN`, `Aitken`, `RN`
  (Robin–Neumann), `fixed`.
- vST: `viscousStressTranspose` in newtonIcoFluid (QM only).
- convergence_test: `strict` (`requireAllResidualMeasures yes`) or `legacy`.
- machine: `Xe` (xenosim), `Mx` (MeluXina), `MS` (mac-studio), `M1`, `Linux`,
  `macOS`.
- level: free text, but use the case's own level names (L1, x2, m2 n100 …).

The rows were seeded on 23 October 2026 from
`paper-data/reuse_map.md` (branch `evidence/reuse-map`). Rows marked
`claimed` by "M run agent" are the solver paper's planned reruns
(`paper-data/submission_plan.md`, branch `manuscript/submission-plan`).
