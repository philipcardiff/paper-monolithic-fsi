#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --output=/project/home/p201136/philip-tube-scaling/timing.%x.%j.out
# usage: sbatch -J tsr-<case> --time=H timing.sh <case> <mono|robin> <endTime> <n1,n2,...> [repeat labels, default "1 2 3"]
# 3dTube strong-scaling rerun (paper Section 6.4), build qm-a421 (a421f063d),
# exact-arc meshes for both couplings. Protocol as timing row 6b: 50-step
# window restarted from t = 5 ms, slab decomposition (simple, 1 1 N), one run
# at a time on this exclusive node, ranks bound to cores 0..N-1, 3 repeats
# (repeat loop outermost). Everything runs in node-local memory (no Lustre
# I/O during the runs); only the logs are copied back, between runs.
C=$1; KIND=$2; END=$3; NS=${4//,/ }; REPS=${5:-1 2 3}
W=/project/home/p201136/philip-tube-scaling
SRC=$W/work/$C; OUT=$W/logs; mkdir -p $OUT
source /project/home/p201287/philip/qm-a421/env.sh > /dev/null 2>&1
T=/tmp; [ "$(stat -f -c %T /tmp)" = lustre ] && T=/dev/shm
T=$T/tsr-$SLURM_JOB_ID; mkdir -p $T
echo "$C $KIND end=$END ranks=$NS job $SLURM_JOB_ID $(hostname) $(date) tmp=$T ($(stat -f -c %T $T))"
lscpu | grep -E "Model name|NUMA node\(s\)"; which solids4Foam mpirun
for n in $NS; do
  D=$T/$C-n$n; mkdir -p $D; cp -a $SRC/. $D/; rm -f $D/log.*
  sed -i -e "s/^startFrom .*/startFrom       latestTime;/" -e "s/^endTime .*/endTime         $END;/" \
         -e "s/^writeControl .*/writeControl    timeStep;/" -e "s/^writeInterval .*/writeInterval   1000000;/" $D/system/controlDict
  for f in $D/system/decomposeParDict $D/system/fluid/decomposeParDict $D/system/solid/decomposeParDict; do
    [ -f $f ] && sed -i -e "/^simpleCoeffs/d" -e "s/^numberOfSubdomains .*/numberOfSubdomains $n;/" \
      -e "s/^method .*/method simple;\nsimpleCoeffs { n (1 1 $n); delta 0.001; }/" $f
  done
  if [ $n -gt 1 ]; then
    if [ $KIND = mono ]; then ( cd $D && decomposeParMonolithic -force > log.decompose 2>&1 ) || echo "DECOMPOSE FAIL $D"
    else for r in fluid solid; do ( cd $D && decomposePar -force -region $r > log.decompose.$r 2>&1 ) || echo "DECOMPOSE FAIL $D $r"; done; fi
    rm -rf $D/0.005
    cp $D/log.decompose* $OUT/ 2>/dev/null; for f in $D/log.decompose*; do cp $f $OUT/$C-n$n.$(basename $f); done
  fi
  echo "ready $D $(date)"; du -sh $D | cut -f1
done
for rep in $REPS; do
  for n in $NS; do
    D=$T/$C-n$n; L=$D/log.r$rep; rm -rf $D/postProcessing
    echo "run $C n$n r$rep $(date)"
    if [ $n -eq 1 ]; then ( cd $D && timeout -k 60 3h taskset -c 0 solids4Foam > $L 2>&1 )
    else ( cd $D && timeout -k 60 3h mpirun -np $n --map-by core --bind-to core solids4Foam -parallel > $L 2>&1 ); fi
    echo "rc $? $(date) $(grep -c '^Time =' $L) steps, $(grep -c 'FOAM FATAL' $L) fatal, $(grep -c 'DIVERGED' $L) diverged"
    echo "node: load $(cut -d' ' -f1-3 /proc/loadavg), mem used/avail GB $(free -g | awk 'NR==2{print $3"/"$7}'), tmp $(du -sh $T | cut -f1), user procs $(ps -u $USER --no-headers | wc -l)"
    cp $L $OUT/$C-n$n-r$rep.log
  done
done
rm -rf $T
echo "done $(date)"
