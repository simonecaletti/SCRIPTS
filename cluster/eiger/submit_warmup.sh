#!/bin/bash

# === USER CONFIGURATION ===
RUNCARD="epemZH2bb.warmup.run"   		# Replace with your runcard
NAME="warmupLO"				# Job label
SEED=1                           	# Starting seed
PARTITION="standard"                  	# SLURM partition name
TIME="04:00:00"                       	# Walltime for each job
CPUS_PER_TASK=4                      	# Cores per task, adjust as needed
NAME="bbLO"

export OMP_STACKSIZE=1G
export OMP_NUM_THREADS=1

mkdir -p logs

# === WARMUP ===
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=${NAME}
#SBATCH --output=logs/${NAME}.out
#SBATCH --error=logs/${NAME}.err
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --time=${TIME}

echo "Running warmup with seed ${SEED}"
NNLOJET -run ${RUNCARD} --iseed ${SEED}
EOF

echo "Submitted warmup job."


