#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
# R-fix build: feature-petsc-snes-quasi-monolithic at 4ae081609 (#618 merged),
# in a copy of the qm-fix tree (incremental), with the tutorial changes of the
# open PR #617 applied uncommitted (schemes in the run copies).
F=/project/home/p201136/philip-ma/rfix
SRC=/project/home/p201136/philip-ma/qm-fix
if [ ! -d "$F/solids4foam" ]; then
    mkdir -p "$F"
    cp -r "$SRC/solids4foam" "$SRC/platforms" "$F/"
    sed "s|^export WM_PROJECT_USER_DIR=.*|export WM_PROJECT_USER_DIR=$F|" "$SRC/env.sh" > "$F/env.sh"
fi
source "$F/env.sh"
cd "$F/solids4foam" || exit 1
git fetch -q origin feature-petsc-snes-quasi-monolithic || exit 1
git checkout -q --detach 4ae081609 || exit 1
git apply --include='tutorials/*' /project/home/p201136/philip-ma/mxpatches/pr617.diff || exit 1
echo "describe: $(git describe --always --dirty) ($(git log --oneline -1 | cut -c1-70))"
git status --short | sed 's/^/  /'
cd src/solids4FoamModels && wmake -j 32 libso > "$F/log.build.lib" 2>&1; echo "lib rc=$? errors=$(grep -c ' error' $F/log.build.lib)"
cd ../../applications/solvers/solids4Foam && wmake > "$F/log.build.app" 2>&1; echo "app rc=$?"
