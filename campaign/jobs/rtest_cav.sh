#!/bin/bash -l
# Restart test on the B1 campaign mesh (cavity factor 4, backward), fix build:
# continuous 0 -> 15 s writing at 10 s, then a restart 10 -> 15 s
source /home/philipc/OpenFOAM/philipc-v2512-qmfix/env.sh
set -u
R=/home/philipc/OpenFOAM/philipc-v2512-qmfix/runs/rtest
cd $R/cav || exit 1
sed '/^# Run solver/,$d' Allrun > Allrun.prepare
bash Allrun.prepare monolithic > log.prepare 2>&1 || exit 1
foamDictionary -entry endTime -set 15 system/controlDict > /dev/null
foamDictionary -entry writeInterval -set 10 system/controlDict > /dev/null
foamDictionary -entry writePrecision -set 12 system/controlDict > /dev/null
cp -a $R/cav $R/cav-restart
solids4Foam > log.solids4Foam 2>&1 || exit 1
cd $R/cav-restart
cp -a $R/cav/10 .
foamDictionary -entry startFrom -set latestTime system/controlDict > /dev/null
solids4Foam > log.solids4Foam 2>&1
echo "restart rc=$?"
