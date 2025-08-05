#!/bin/bash

# === Configuration ===
RUNCARD="epemZH2bb.run"  # Your NNLOJET runcard
NAME="bbLO"              # Job label
ACCOUNT="eth5f"          # CSCS group account
EMAIL="scaletti@ethz.ch" # Replace with your ETH email
TIME="1-00:00:00"        # Walltime
NUM_NODES=2              # Number of sbatch jobs to launch (each is NUM_THREADS jobs)
NUM_THREADS=256          # Eiger: 256 logical core per node
PARTITION="normal"       # Partition to submit
CONSTRAINT="mc"          # Ensure multicore node
START_SEED=1             # First seed: can be different than 1
MEMORY=1G                # Memory requirement per job
#DEPEND=5398786             # Dependence job id, if used add
# "#SBATCH --dependency=afeterok:${DEPEND}" below

mkdir -p logs

CURRENT_SEED=$START_SEED

# === Submit a different sbatch job per node ===
for NODE_ID in $(seq 0 $((NUM_NODES - 1))); do

  SEED_THIS_JOB=$CURRENT_SEED

  # === Single job start here ===
  sbatch <<EOF
#!/bin/bash -l
#SBATCH --job-name=${NAME}${NODE_ID}
#SBATCH --account=${ACCOUNT}
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${EMAIL}
#SBATCH --time=${TIME}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=${NUM_THREADS}
#SBATCH --cpus-per-task=1
#SBATCH --partition=${PARTITION}
#SBATCH --constraint=${CONSTRAINT}
#SBATCH --output=logs/${NAME}_${NODE_ID}.out
#SBATCH --error=logs/${NAME}_${NODE_ID}.err
#SBATCH --mem-per-cpu=${MEMORY}
#SBATCH --exclusive

export OMP_STACKSIZE=1G
export OMP_NUM_THREADS=1

SEED=${SEED_THIS_JOB}
for ((i=0; i<${NUM_THREADS}; i++)); do
    echo "Launching seed \$SEED"
    NNLOJET -run ${RUNCARD} -iseed \$SEED > logs/${NAME}_nod${NODE_ID}_s\${SEED}.out 2> logs/${NAME}_nod${NODE_ID}_s\${SEED}.err &
    SEED=\$((SEED + 1))
done

wait

EOF

  echo "Submitted on the ${NODE_ID} node ${NUM_THREADS} NNLOJET runs (seeds ${CURRENT_SEED}–$((CURRENT_SEED + NUM_THREADS - 1)))."
  CURRENT_SEED=$((CURRENT_SEED + NUM_THREADS))

done
