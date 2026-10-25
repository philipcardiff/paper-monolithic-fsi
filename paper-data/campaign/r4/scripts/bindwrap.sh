#!/bin/bash
# Pin this MPI rank to core number OMPI_COMM_WORLD_LOCAL_RANK of FARM_CORES
# (comma-separated list), then exec the command.
IFS=, read -ra C <<< "${FARM_CORES:?}"
r=${OMPI_COMM_WORLD_LOCAL_RANK:-0}
exec taskset -c "${C[$r]}" "$@"
