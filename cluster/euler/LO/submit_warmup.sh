#!/bin/bash

# === CONFIGURATION ===
RUNCARD="epemZH2bb.warmup.run"
SEED=1
PARTITION="standard"
TIME="04:00:00"             # Short time for warmup
NODES=1
CPUS_PER_TASK=4             # Fewer cores if warmup is light
NAME="warmupLO"

mkdir -p logs

sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=${NAME}
#SBATCH --output=logs/${NAME}.out
#SBATCH --error=logs/${NAME}.err
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=${NODES}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --time=${TIME}

echo "Running warmup with seed ${SEED}"
NNLOJET -run ${RUNCARD} --iseed ${SEED}
EOF

echo "Submitted warmup job."

