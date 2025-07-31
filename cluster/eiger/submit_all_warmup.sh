#!/bin/bash

# === USER CONFIGURATION ===
RUNCARD="epemZH2gg.warmup.run" 		# Replace with your warmup runcard (common name)
NAME="warmup"				# Job label
PARTITION="normal"
TIME="12:00:00"
CPUS_PER_TASK=8				# 32 logical core used = 8 x 6 stages
SEED=1

export OMP_STACKSIZE=1G
export OMP_NUM_THREADS=${CPUS_PER_TASK}

# === STAGES TO RUN ===
STAGES=("LO" "R" "V" "VV" "RV" "RR")

sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=${NAME}
#SBATCH --output=${NAME}.out
#SBATCH --error=${NAME}.err
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=1
#SBATCH --ntasks=6
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --time=${TIME}

echo "Running warmup stages: ${STAGES[*]}"
echo "Using seed: ${SEED}"

for stage in ${STAGES[@]}; do
    (
        export OMP_NUM_THREADS=${CPUS_PER_TASK}
        cd \${stage}
	mkdir -p logs/
        echo "Starting warmup for \${stage}"
        NNLOJET -run ${RUNCARD} --iseed ${SEED} > ../logs/${NAME}${stage}.out 2>&1
    ) &
done

wait
echo "All warmup jobs completed."
EOF

echo "Submitted combined warmup job."

