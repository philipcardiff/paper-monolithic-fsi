#!/bin/bash -l
#SBATCH --job-name=tsr-prep
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --exclusive
#SBATCH --time=03:00:00
#SBATCH --output=/project/home/p201136/philip-tube-scaling/prep.%j.out
# 3dTube strong-scaling rerun: t = 5 ms restart states on the exact-arc
# (solids4foam#625) meshes for both couplings, build qm-a421 (a421f063d).
#  qmL2: r5-tube-mono-L2-t6 case rerun 0 -> 5 ms (16 ranks)
#  qmL3: r5-tube-mono-L3-t6 saved 5 ms state (reconstructed)
#  rnL2: rn-exact/rn-L2 restarted 4 -> 5 ms (16 ranks)
#  rnL3: rn-exact/rn-L3 case rerun 0 -> 5 ms (96 ranks, slabs)
# Each is reconstructed at 0.005 and stripped of processor dirs.
W=/project/home/p201136/philip-tube-scaling
A=/project/home/p201287/philip/qm-a421/runs
source /project/home/p201287/philip/qm-a421/env.sh > /dev/null 2>&1
export OMPI_MCA_hwloc_base_binding_policy=none PRTE_MCA_hwloc_default_binding_policy=none
echo "prep $SLURM_JOB_ID $(hostname) $(date)"
df -h /tmp /dev/shm; stat -f -c %T /tmp /dev/shm; free -g | head -2; which mpirun solids4Foam decomposeParMonolithic; mpirun --version | head -1
mkdir -p $W/work && cd $W/work
setctl() { # dir startFrom end writeInterval
  sed -i -e "s/^startFrom .*/startFrom       $2;/" -e "s/^endTime .*/endTime         $3;/" \
         -e "s/^writeInterval .*/writeInterval   $4;/" $1/system/controlDict; }
slabs() { # dir N
  for f in $1/system/decomposeParDict $1/system/fluid/decomposeParDict $1/system/solid/decomposeParDict; do
    [ -f $f ] && sed -i -e "s/^numberOfSubdomains .*/numberOfSubdomains $2;/" \
      -e "s/^method .*/method simple;\nsimpleCoeffs { n (1 1 $2); delta 0.001; }/" $f
  done; }
recon() { # dir; keeps the processor dirs if either region fails
  # (as run on 17 Nov the failure only printed RECON FAIL; none occurred)
  ( cd $1 && for r in fluid solid; do reconstructPar -region $r -time 0.005 > log.reconstructPar.$r 2>&1 \
      || { echo "RECON FAIL $1 $r"; exit 1; }; done
    rm -rf processor* postProcessing 0.004 0.008 0.012 0.016 0.02 0.01 0.015
    echo "$1 reconstructed at 0.005" ); }
tar xf $A/r5.tar --exclude='*/processor*' r5/r5-tube-mono-L2-t6 && mv r5/r5-tube-mono-L2-t6 qmL2
tar xf $A/r5.tar --exclude='*/processor*/0.01' --exclude='*/processor*/0.015' --exclude='*/processor*/0.02' r5/r5-tube-mono-L3-t6 && mv r5/r5-tube-mono-L3-t6 qmL3
tar xf $A/rn-exact.tar --exclude='*/processor*/0.008' --exclude='*/processor*/0.012' --exclude='*/processor*/0.016' --exclude='*/processor*/0.02' rn-exact/rn-L2 && mv rn-exact/rn-L2 rnL2
tar xf $A/rn-exact.tar --exclude='*/processor*' rn-exact/rn-L3 && mv rn-exact/rn-L3 rnL3
rmdir r5 rn-exact; rm -rf qmL2/0.02 rnL3/0.02 qmL2/postProcessing rnL3/postProcessing rnL2/postProcessing
echo "extracted $(date)"; du -sh qmL2 qmL3 rnL2 rnL3
# QM L2: 0 -> 5 ms on 16 ranks (original scotch decomposition)
( cd qmL2 && setctl . startTime 0.005 0.005 && decomposeParMonolithic -force > log.decompose.prefix 2>&1 \
  && mpirun -np 16 solids4Foam -parallel > log.prefix 2>&1; echo "qmL2 prefix rc $? $(date)"; tail -3 log.prefix ) &
# RN L2: 4 -> 5 ms on 16 ranks (its own decomposition)
( cd rnL2 && setctl . latestTime 0.005 0.001 && mpirun -np 16 solids4Foam -parallel > log.prefix 2>&1; echo "rnL2 prefix rc $? $(date)"; tail -3 log.prefix ) &
# RN L3: 0 -> 5 ms on 96 ranks (slabs)
( cd rnL3 && setctl . startTime 0.005 0.005 && slabs . 96 && for r in fluid solid; do decomposePar -force -region $r > log.decompose.prefix.$r 2>&1; done \
  && mpirun -np 96 solids4Foam -parallel > log.prefix 2>&1; echo "rnL3 prefix rc $? $(date)"; tail -3 log.prefix ) &
recon qmL3
wait
recon qmL2; recon rnL2; recon rnL3
for c in qmL2 qmL3 rnL2 rnL3; do echo "== $c $(cat $c/0.005/uniform/time 2>/dev/null | grep -E '^(value|index)')"; ls $c $c/0.005/fluid $c/0.005/solid | tr '\n' ' '; echo; done
du -sh qmL2 qmL3 rnL2 rnL3; find . | wc -l
echo "prep done $(date)"
