#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Field-image data for ringAddedMass: the R-fix run rf-ram-qm-strong-m2-n100
# repeated for its first period (100 steps) with every step written, so that
# the image can show a state with both ring deformation and fluid motion (the
# run itself writes only its end, four periods on, near zero displacement).
F=/project/home/p201136/philip-ma/rfix
SRC=/project/home/p201136/philip-ma/runs-rfix/rf-ram-qm-strong-m2-n100
D=/project/home/p201136/philip-ma/runs-render/rf-ram-qm-strong-m2-n100-T1
source "$F/env.sh"
(cd "$F/solids4foam" && git describe --always --dirty --tags)
rm -rf "$D"; mkdir -p "$D"
cp -r "$SRC/0" "$SRC/constant" "$SRC/system" "$D/"
cd "$D" || exit 1
sed -i -E 's/^(endTime\s+).*;/\18.17426474563;/; s/^(writeInterval\s+).*;/\11;/' \
    system/controlDict
grep -E "^(endTime|deltaT|writeInterval)" system/controlDict
solids4Foam > log.solids4Foam 2>&1
echo "rc=$? steps=$(grep -c '^Time =' log.solids4Foam) $(grep ExecutionTime log.solids4Foam | tail -1)"
