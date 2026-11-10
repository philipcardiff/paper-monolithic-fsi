#!/bin/bash
# Run on MeluXina: per-step table for every coupled log of every fsi3g run:
#   log time dclock newton krylov iqn
# newton = SNES iterations of the coupled Up system (QM) or, for IQN-ILS, the
# number of coupling iterations; krylov = linear iterations in that system.
cd /project/home/p201136/philip-ht/fsi3g/runs || exit 1
for c in qm_1 iqn_1 qm_2 iqn_2 qm_3 iqn_3 qm_2_dt1e-4 qm_2_dt2e-4 qm_2_sf2; do
  for f in $(ls $c/log.solids4Foam.coupled* | sort -V); do
    awk -v lg="$(basename $f)" -v run="$c" '
      /^Time = [0-9.e+-]+$/ { t = $3; nit = 0; kry = 0; inUp = 0; iqn = 0; next }
      /^Time = .*, iteration: / { split($0, a, "iteration: "); iqn = a[2] + 0; next }
      /Solving the monolithic momentum-continuity system/ { inUp = 1; next }
      inUp && /Linear solve converged due to/ { kry += $NF }
      inUp && /Nonlinear solve (converged|did not converge)/ { nit = $NF; inUp = 0 }
      /^ExecutionTime = / {
        clk = $(NF-1);
        if (t != "") print run, lg, t, clk - prev, nit, kry, iqn;
        prev = clk
      }
    ' "$f"
  done
done
