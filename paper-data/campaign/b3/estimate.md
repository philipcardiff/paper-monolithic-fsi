# B3: Jaiman/Liu cases — estimate only (no runs)

Handoff Section 3, B3: estimate the cost of the blobInTreacle monolithic
temporal study and the effort of building the block-with-tail case of Jaiman
and Joshi (2022). Nothing here was run.

Source of every cost number: `tutorials/fluidSolidInteraction/blobInTreacle/
verification/README.md` at solids4foam `257b2e564` ("Reference results",
partitioned IQN-ILS, OpenFOAM v2512, Linux).

## 1. blobInTreacle (Liu, Jaiman and Gurugubelli 2014), monolithic arm (R6)

### What exists

- Partitioned time-step study on the tutorial mesh (x1: 480 fluid, 120 solid
  cells) to t = 1 s, Δt = 0.25, 0.125, 0.0625, 0.03125 s; observed order of
  the top-point u_x 2.39, 2.54 from successive differences (no reference
  solution needed).
- Monolithic mesh study x1, x2, x4 to t = 3 s (README, "Quasi-monolithic
  coupling" table; macOS, before #611 and the tag).
- No monolithic time-step study.

### Settings to change for R6

- The monolithic variant uses `ddt(U) Euler` (and `ddt(dU)`, `ddt(p)` Euler)
  in `system/fluid/fvSchemes.monolithic`; the solid already uses `backward`.
  Per the 20 Oct decision the fluid must be `backward` for the temporal
  study, otherwise the observed order is capped at 1.
- Tolerances: `snes_rtol 1e-6`, `ksp_rtol 1e-4` (tutorial). The partitioned
  README notes changes of ~1e-5 m below Δt = 0.03125 s are at the coupling
  tolerance level; the monolithic Δt sequence should stop at the same Δt.

### Cost

| Item | Steps | Basis | Estimate |
|---|---:|---|---|
| Temporal study, 4 Δt to t = 1 s, x1, serial | 4 + 8 + 16 + 32 = 60 | partitioned x1: 91 s / 300 steps ≈ 0.3 s per step; allow the monolithic step ≤ 3× that | ≤ 1 min per coupling |
| Same, 3 timing repeats, both couplings | 360 | as above | < 0.1 core-h |
| Mesh study rerun from the tag (x1, x2, x4 to t = 3 s), monolithic | 300 + 300 + 600 | partitioned: 91 s (1 core) + 376 s (4) + 1430 s (4) = 7 315 core-s ≈ 2.0 core-h | ≈ 2 core-h, assuming monolithic ≈ partitioned |
| Same, timed: 3 repeats of both couplings | | 2 couplings × 3 × 2.0 | ≈ 12 core-h (upper bound; the timing repeats could be limited to x4) |

**R6 blobInTreacle total: about 2–12 core-h**, dominated by the timed mesh
study, not the temporal study. Risks: the Newton solve at Δt = 0.25 s (25
times the tutorial step) during the inflow ramp is untested; if it fails,
start the sequence at 0.125 s and say so. Set-up effort: a monolithic switch
in the existing driver (`blob_in_treacle_verification.py` runs partitioned
only) or a campaign wrapper as for B1 — about half a day.

## 2. Block with flexible tail (Jaiman and Joshi 2022)

### What exists

Nothing (A1): no 2D block-with-flexible-tail case on any branch; foilInWind
is the only block-with-flag case (3D, no benchmark cited).

### Effort to build (estimate, not verified against the book)

I do not have the text of Jaiman and Joshi (2022) here, so the geometry,
material, Reynolds number and the published quantities (tail-tip amplitude
and frequency) are not yet checked; the items below are the work any such
case needs.

| Task | Effort |
|---|---|
| Extract geometry, material, inflow and published QoIs from the book; decide what is comparable | 0.5 day |
| Fluid and solid blockMesh (block with tail slot, O-type or multi-block around the tail), interface patches, decomposeParMonolithic dictionary | 1 day |
| Partitioned and monolithic variants, monitors (tail tip), verification driver | 1 day |
| Shake-down runs: onset of oscillation, Δt, Newton robustness | 0.5–1 day |
| **Total set-up** | **3–3.5 person-days** |

Run cost (order of magnitude): a periodic self-excited oscillation needs
the transient to die out, typically 10–20 periods; at roughly 10k–50k
fluid cells and a few thousand steps per mesh/Δt level, a 3-level mesh plus
3-level Δt study of both couplings is **about 20–60 core-h**. This is a
guess from the 2D case sizes above, not a measurement.

### Recommendation for G1

- Run the blobInTreacle monolithic temporal study in R6 (cheap, no new case,
  direct comparison with the formulation the solver is based on).
- The block with tail adds a new, unverified case of 3–3.5 days set-up plus
  20–60 core-h; it is optional and only worth it if the paper needs a
  self-excited oscillation benchmark that Hron–Turek FSI3 does not already
  provide. Decision for Philip at G1.
