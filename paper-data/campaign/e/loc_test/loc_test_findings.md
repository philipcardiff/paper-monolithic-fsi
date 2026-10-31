# FSI3 gate item 1: localisation of the 3x->4x change (agent B, 31 Oct 2026)

Follows the wake test (`../wake_test/`, wake not the bottleneck). Philip's go, 31 Oct.
Same protocol and binary as `sm_3x` (aee0c8e3, tmpl8x, src4x, dt 1/3000, five periods
ending at 30.2 s). Mesh: `ht_mesh_local.py` = `ht_mesh_smooth.py` level 3 with the
chains of one region at their level-4 division counts, gradings unchanged (at fine
level 3 it reproduces sm_3x byte for byte). Mx 5405635 (p201136), 1 h 54 min.

| case | region at 4x | cells | ExecutionTime |
|---|---|---:|---:|
| sml_3x_ring | ring radial + circumferential chains (incl. x-columns upstream of the ring, inlet-column y) | 129 696 | 4944 s |
| sml_3x_flag | y-rows y 0.12-0.28 m along the channel + along the flag (incl. cylinder root arcs 11-12/17-18) | 143 184 | 6411 s |

Region interfaces carry 4:3 size jumps (audit max 1.51 ring, 1.46 flag).

| case | Q_in | Q_quad | lift amp | drag | phase |
|---|---:|---:|---:|---:|---:|
| sm_3x | 75.631 | -0.108 | 155.182 | -17.776 | 59.77 |
| ring - 3x | -0.095 | +0.463 | +0.876 | +0.093 | -0.10 |
| flag - 3x | +0.147 | +0.340 | +0.892 | +0.213 | +0.55 |
| sum | +0.052 | +0.803 | +1.768 | +0.306 | +0.45 |
| 4x - 3x | +0.914 | +0.886 | +2.422 | +0.019 | -0.10 |

Reading:
- Lift amplitude: ring and flag/band rows each carry about 36-37 % of the 3x->4x
  change; together 73 %. No single region dominates: the error is spread over the
  near field.
- Q_quad: 52 % + 38 % = 91 %, close to additive.
- Q_in: neither region (sum 6 %). Its 3x->4x change sits in what both leave at 3x
  (channel-wall rows y < 0.12 and > 0.28, inlet x-columns; the wake was excluded by the
  wake test) or in non-additive/interface effects. Time step accounts for < 0.1 N/m.
- Drag (+0.2) and phase (+0.55 deg, flag) move against the 4x direction by more than
  4x-3x itself: likely the 4:3 interface jumps on y = 0.12/0.28 (the lines where the
  ring+box jumps sat); treat those two as artefacts of the diagnostic.
