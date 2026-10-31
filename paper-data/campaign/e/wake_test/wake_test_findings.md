# FSI3 gate item 1(a): wake test (agent B, 31 Oct 2026)

Question (Philip, 29 Oct, board 6496649549): is wake resolution the reason the lift
amplitude of the smooth-family fluid-only replay is still rising at 4x?

Set-up: identical to `sm_3x` of `verification/hronturek-smooth-mesh` (25062dbad):
same study binary (aee0c8e3), template (tmpl8x), mapped 25 s state (src4x), replay
table, dt 1/3000, five-period window ending at 30.2 s. Only the x-sizes of the wake
columns (x > 0.6 m) change; y-divisions are shared with the upstream rows and are
**not** refined. Cases built with `ht_smooth_case.py --level 3 --h-wake W --h-out O`.
Mx 5404658 (p201136), one node, 1 h 56 min.

| case | h_wake / h_out (1x, mm, before scale 1.1) | cells | ranks | ExecutionTime |
|---|---|---:|---:|---:|
| sm_3x | 8 / 150 | 113 112 | 28 | 6688 s |
| smw_3x_wake2 | 4 / 75 | 143 379 | 36 | 5537 s |
| smw_3x_cap10 | 4 / 10 | 224 091 | 56 | 6474 s |

Mesh audit: max neighbour ratio 1.133 (ring corner) in both, no face > 1.2;
deformed mesh at 30.2 s: non-orth 28.25 deg, skewness 0.378.

Results (N/m, deg; `second_order_analysis.analyse`, `wake_test.json`):

| case | Q_in | Q_quad | lift amp | drag mean | lift phase |
|---|---:|---:|---:|---:|---:|
| sm_3x | 75.631 | -0.108 | 155.182 | -17.776 | 59.77 |
| wake2 | 75.656 | -0.172 | 155.140 | -17.901 | 59.69 |
| cap10 | 75.698 | -0.106 | 155.163 | -17.878 | 59.69 |
| sm_4x | 76.545 | 0.778 | 157.604 | -17.757 | 59.68 |
| cap10 - 3x | +0.067 | +0.002 | -0.019 | -0.102 | -0.08 |
| 4x - 3x | +0.914 | +0.886 | +2.422 | +0.019 | -0.10 |

Reading:
- Refining the wake streamwise, even capping the far wake at ~3.7 mm at 3x (45x finer
  than the 3x outlet), moves Q_in by 7% and the lift amplitude by -1% (wrong sign) of
  the 3x->4x difference. **Streamwise wake resolution is not the bottleneck.**
- The far-wake field differences seen in the snapshot comparison do not feed back to
  the flag loads.
- Mean drag moves by -0.10 N/m, about the size of its time-step and tail sensitivities.
- What remains: the 3x->4x change comes from what both variants share with sm_3x:
  the cylinder ring, the flag rows, and the y-resolution of every row (including the
  vortex street, y 0.12-0.28 m). Time step: the 2x dt/2 check (+0.39 N/m lift amp at
  2x) scales to ~0.2 N/m at 3x, a minor part of 2.4.
