#!/bin/bash -l
#SBATCH --account=p201136
#SBATCH --partition=cpu
#SBATCH --qos=default
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/project/home/p201136/philip-ma/slurm-%x-%j.out
#
# Measurement-only builds for the PR #618 cost benchmark, each a copy of an
# existing build tree (incremental) with the residual timing patch
# (foamPetscSnesSolver.C, not part of any commit):
#   head  : R0 tree, 85b0c1de6
#   pr    : fix tree at 8f36c7025 + revert aa77c2084 (code = PR before caching)
#   cache : pr + 32c553116 + 11a352315 (PR with caching)
set -u
B=/project/home/p201136/philip-ma/timing
P=/project/home/p201136/philip-ma/mxpatches
mkdir -p "$B"

mkcopy() {   # name source_root
    local name=$1 src=$2 d=$B/$1
    [ -d "$d/solids4foam" ] && return 0
    mkdir -p "$d"
    cp -a "$src/solids4foam" "$src/platforms" "$d/"
    sed "s|^export WM_PROJECT_USER_DIR=.*|export WM_PROJECT_USER_DIR=$d|" \
        "$src/env.sh" > "$d/env.sh"
}

am() {   # tree patch committer_date
    (cd "$1/solids4foam" && GIT_COMMITTER_NAME="Philip Cardiff" \
        GIT_COMMITTER_EMAIL=philip.cardiff@ucd.ie \
        GIT_COMMITTER_DATE="$3" git am -q "$2")
}

mkcopy head /project/home/p201287/philip/qm-head
mkcopy pr /project/home/p201136/philip-ma/qm-fix
am "$B/pr" "$P/0001-Revert-Tutorials-interpolate-U-linear-instead-of-ske.patch" "1792795757 +0100"
mkcopy cache "$B/pr"
am "$B/cache" "$P/0002-newtonIcoFluid-cache-the-viscous-fields-and-the-surf.patch" "1792797165 +0100"
am "$B/cache" "$P/0003-newtonIcoFluid-keep-the-surface-fit-arithmetic-in-it.patch" "1792798056 +0100"

for n in head pr cache; do
    (
        source "$B/$n/env.sh"
        cd "$B/$n/solids4foam" || exit 1
        git apply "$P/timing.patch" || exit 1
        echo "$n: $(git describe --always --dirty) ($(git log --oneline -1 | cut -c1-60))"
        cd src/solids4FoamModels && wmake -j 10 libso > "$B/$n/log.build.lib" 2>&1
        echo "$n lib rc=$? errors=$(grep -c ' error' $B/$n/log.build.lib)"
    ) &
done
wait
