#!/bin/bash -l
# B1: solid-block preconditioner check (campaign handoff, Section 3, B1).
#
#   B1_STAGE=spinup B1_KIND=cav|tube   serial spin-up to the developed state
#   B1_STAGE=windows B1_KIND=ring|cav|tube
#       every configuration and rank count of the case, one after another on
#       the allocated (exclusive) node; cav and tube restart from the spin-up
#
# Required environment: QM_ENV, QM_RUNS (stream directory, e.g. runs/b1),
# QM_SCRIPTS (campaign/scripts).

source "${QM_ENV:?}"
set -u
mkdir -p "${QM_RUNS:?}"
SETUP="${QM_SCRIPTS:?}/b1_setup.py"

# Rank placement used for every campaign run
export OMPI_MCA_rmaps_base_mapping_policy=core
export OMPI_MCA_hwloc_base_binding_policy=core
export OMPI_MCA_hwloc_base_report_bindings=1

now() { date +%s.%N; }
elapsed() { python3 -c "print(round($2 - $1, 3))"; }

# Peak resident memory per rank (kB) from /usr/bin/time, written as mem.<rank>
run_solver()
{
    local ranks="$1"
    if [ "$ranks" -gt 1 ]
    then
        mpirun -n "$ranks" bash -c \
            'exec /usr/bin/time -f %M -o mem.$OMPI_COMM_WORLD_RANK solids4Foam -parallel' \
            < /dev/null > log.solids4Foam 2>&1
    else
        /usr/bin/time -f %M -o mem.0 solids4Foam < /dev/null \
            > log.solids4Foam 2>&1
    fi
}

write_meta()
{
    local id="$1" kind="$2" config="$3" ranks="$4" rc="$5" wall="$6"
    python3 - "$id" "$kind" "$config" "$ranks" "$rc" "$wall" <<'EOF'
import glob, json, sys
run_id, kind, config, ranks, rc, wall = sys.argv[1:]
mem = []
for f in glob.glob("mem.*"):
    try:
        mem.append(int(open(f).read().split()[-1]))
    except (ValueError, IndexError):
        pass
json.dump({"run_id": run_id, "case": kind, "config": config,
           "ranks": int(ranks), "rc": int(rc), "wall_s": float(wall),
           "peak_rss_max_rank_gb": round(max(mem) / 2**20, 3) if mem else None,
           "peak_rss_sum_gb": round(sum(mem) / 2**20, 3) if mem else None,
           "binding": "mpirun map-by core bind-to core"},
          open("run_meta.json", "w"), indent=1)
EOF
}

spinup()
{
    local kind="$1" d="$QM_RUNS/spin-$1"
    python3 "$SETUP" spinup "$kind" "$d" || exit 1
    cd "$d" || exit 1
    local t0 rc
    t0=$(now)
    ./Allrun monolithic > log.Allrun 2>&1
    rc=$?
    python3 "$QM_SCRIPTS/provenance.py" "$d" --ranks 1 \
        --run-id "b1-spin-$kind" > /dev/null
    write_meta "b1-spin-$kind" "$kind" S0 1 "$rc" "$(elapsed "$t0" "$(now)")"
    echo "spin-$kind rc=$rc"
}

window()
{
    local kind="$1" config="$2" ranks="$3"
    local id="b1-$kind-$config-p$ranks" d="$QM_RUNS/b1-$kind-$config-p$ranks"
    if [ "$kind" = ring ]
    then
        python3 "$SETUP" ring "$d" --config "$config" --ranks "$ranks" \
            || return 1
    else
        python3 "$SETUP" window "$QM_RUNS/spin-$kind" "$d" \
            --config "$config" --ranks "$ranks" || return 1
    fi
    cd "$d" || return 1
    python3 "$QM_SCRIPTS/provenance.py" "$d" --ranks "$ranks" \
        --run-id "$id" > /dev/null

    local t0 rc
    if [ "$kind" = ring ]
    then
        # The tutorial Allrun builds the meshes and the initial velocity;
        # its decomposition is per region
        local args="monolithic standard"
        [ "$ranks" -gt 1 ] && args="$args parallel"
        t0=$(now)
        ./Allrun $args > log.Allrun 2>&1
        rc=$?
    else
        if [ "$ranks" -gt 1 ]
        then
            if [ "$kind" = tube ]
            then
                # One graph over both regions, as in the scaling stream
                decomposeParMonolithic -force > log.decompose 2>&1 || return 1
            else
                # Per-region decomposition, as the cavity tutorial Allrun
                { decomposePar -force -region fluid \
                  && decomposePar -force -region solid; } \
                    > log.decompose 2>&1 || return 1
            fi
        fi
        t0=$(now)
        run_solver "$ranks"
        rc=$?
    fi
    write_meta "$id" "$kind" "$config" "$ranks" "$rc" \
        "$(elapsed "$t0" "$(now)")"
    echo "$id rc=$rc"
}

case "${B1_STAGE:?}" in
    spinup)
        spinup "${B1_KIND:?}"
        ;;
    windows)
        case "${B1_KIND:?}" in
            ring) list="S0:1 S1:1 S0tight:1 S0:4 S1:4 S2:4 S0tight:4" ;;
            cav)  list="S0:1 S1:1 S0tight:1 S0:4 S1:4 S2:4 S0tight:4
                        S0:16 S1:16 S2:16 S0tight:16" ;;
            tube) list="S0:4 S1:4 S2:4 S0tight:4 S0:16 S1:16 S2:16
                        S0tight:16 S0:32 S1:32 S2:32 S0tight:32" ;;
        esac
        for item in $list
        do
            window "$B1_KIND" "${item%%:*}" "${item##*:}"
        done
        ;;
esac
