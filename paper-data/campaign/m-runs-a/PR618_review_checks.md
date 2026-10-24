# PR solids4foam#618 review checks (agent A)

Final PR head bcf29f8d3 (all CI checks green, 24 Oct 2026). Copy of the PR test and review sections; run directories on MeluXina under /project/home/p201136/philip-ma/runs/{pr618,cost,bcf,tgv}; job scripts in jobs/ (ma_pr618_checks.sh, ma_timing_builds.sh, ma_timing_build_step.sh, ma_cost_job.sh, ma_fsi3_head_decomp.sh, ma_tgv_repro.sh, ma_verify_bcf.sh); ma_cost.py with a measurement-only timing patch of foamPetscSnesSolver.C (not committed).

## Test Cases and Results 📊

All runs are QM, at the commit given.

- **blobInTreacle, steady u_x, QM minus partitioned IQN-ILS strict (x1/x2/x4; mac-studio):**

  | Code | x1 | x2 | x4 |
  |---|---|---|---|
  | Head, vST no | −0.33% | −0.29% | −0.16% |
  | Head, vST yes | −2.34% | −1.04% | −0.44% |
  | Transpose term in the wall pressure gradient | −1.31% | −0.56% | −0.22% |
  | Plus wall-velocity evaluation | −0.71% | −0.39% | −0.18% |
  | Same, with `interpolate(U) linear` (not in this PR) | −0.20% | −0.23% | −0.14% |

  - All series extrapolate within 0.08% of the partitioned value.
  - With a zeroGradient interface pressure (as in the partitioned set-up), the difference is +0.31/+0.11/+0.06%.
  - Serial and 2-rank runs are identical.

- **womersleyTube n200, QM minus Robin–Neumann (MeluXina; run with `interpolate(U) linear`, which is also the partitioned setting there):**

  | Mesh | Wall phase (this PR) | Wall phase (head, vST no) | Wall amplitude (this PR) |
  |---|---|---|---|
  | m1 | −4.6e-5 | −5.2e-4 | +8.6e-5 |
  | m2 | −2.9e-5 | −4.8e-4 | −1.5e-4 |
  | m4 | −3.6e-5 | −4.8e-4 | −1.7e-4 |

  - Attenuation and wave speed are within 3e-5 of RN from m2 onwards.
  - The remaining wall-amplitude offset is the size of the Robin–Neumann/IQN-ILS spread.

- **ringAddedMass, 3 levels × mesh 1/2/4, 100 steps per period:** wet/dry ratio errors unchanged or slightly smaller (strong m1 −0.0324% → −0.0312%). The frequency on 4 ranks equals serial; the amplitude loss is within 4e-6.

- **TurekHron2006 FSI3, conformal 1x mesh (2 009 cells), against the head:**

  | Change | u_y amplitude | Drag mean | Lift amplitude | u_x mean |
  |---|---|---|---|---|
  | This PR (tutorial `skewCorrected linear`) | −0.8% | −0.4% | −0.9% | −1.8% |
  | With `interpolate(U) linear` (not in this PR) | −11.2% | −1.2% | −12.0% | −18% |

- **Review checks (coordinator), MeluXina, final code:**
  - *Cost* (3dTube L2, 8 ranks, 20 steps, exclusive node, timing builds that time every residual evaluation; same tutorial, Newton 40 and Krylov 878 in all runs; two rounds within 1%):

    | Build | per residual evaluation | Up solve | total wall |
    |---|---|---|---|
    | head 85b0c1de6 | 95 ms | 88 s | 138 s |
    | this PR without caching (aa77c2084) | 112 ms (+18%) | 99 s | 148 s (+7%) |
    | this PR with caching (11a352315) | 103 ms (+8%) | 93 s | 141 s (+2%) |

    The caching commit computes grad(U), the transpose stress with its wall values, its divergence, the Laplacian and ddt(U) once per velocity state (validity checked by an O(N) comparison of U, time index, deltaT and mesh points, plus explicit invalidation), and precomputes the surface-fit geometry per patch; it is bit-identical to the uncached code (serial and 2 ranks). The remaining +8% is the transpose term itself and the cache being evaluated twice per coupled residual (once after the coupler maps the interface velocity, once after the fluid unpacks the state); removing the second would need a reordering in the coupler.
  - *Decomposition*: 3dTube L1 serial vs 8 ranks, whole point-A history within 1.4e-5 relative (output precision), Newton 2.00 in both. TurekHron2006 conformal 1x serial vs 4 ranks, full 7 s, relative |np1 − np4| of the drag mean / u_y mean: head 7.8e-7 / 1.8e-5; this PR before bcf29f8d3 7.3e-5 / 1.4e-4 (one-sided fit at processor cuts); **with bcf29f8d3 2.6e-7 / 1.8e-5** (amplitudes and frequency 1e-5–6e-5, as head). bcf29f8d3 takes the fit neighbours from the global patch on patches split across processors (serial unchanged, bit-identical); with tight solver tolerances the serial and 4-rank wall states agree to round-off (first residual norms 6e-13 relative, forces to all printed digits).
  - *CI fix* (bcf29f8d3): `decayingTaylorGreenVortex` failed with the caching commits (line search) because its wall condition reads the registered `grad(U)` in `snGrad()` and the cached Laplacian was evaluated before `grad(U)` was updated; the cache now sets `grad(U)` first. The tutorial converges in 2 Newton iterations per step (Linux/GCC and macOS/Clang) and passes its regression test. Cost after bcf29f8d3: 103 ms per residual evaluation (unchanged).
  - *interpolate(U) skewCorrected vs linear*, QM-AMI on the tutorial meshes against the verification paper's IQN-ILS (u_x mean / u_y amplitude / drag mean / lift amplitude): 1x skewCorrected +6.4% / −4.6% / −0.6% / −4.4%, linear +18.3% / −11.2% / −1.3% / −13.4%; 2x skewCorrected +7.5% / −4.0% / −0.2% / −2.9%, linear +12.8% / −6.9% / −0.7% / −7.6%. linear moves QM further from the partitioned solution on FSI3, so the tutorial schemes are left unchanged here.
- **Remaining:** verification README tables (blobInTreacle, womersleyTube) still need rerunning on this code.
