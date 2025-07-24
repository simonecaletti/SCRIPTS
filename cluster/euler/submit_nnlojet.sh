#!/bin/bash

# === USER CONFIGURATION ===
RUNCARD="epemZH2bb.run"   # Replace with your actual runcard path
START_SEED=1                        # Starting seed
END_SEED=50		      # Ending seed (inclusive)
PARTITION="standard"                  # SLURM partition name
TIME="04:00:00"                       # Walltime for each job
NODES=1                               # Number of nodes per job
CPUS_PER_TASK=1                      # Cores per task, adjust as needed
NAME="bbLO"


# === SCRIPT STARTS HERE ===
for SEED in $(seq $START_SEED $END_SEED); do
  JOBNAME="${NAME}${SEED}"
  sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=${JOBNAME}
#SBATCH --output=logs/${JOBNAME}.out
#SBATCH --error=logs/${JOBNAME}.err
#SBATCH --partition=${PARTITION}
#SBATCH --nodes=${NODES}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=${CPUS_PER_TASK}
#SBATCH --time=${TIME}

# Load any required modules or environment
# module load nnlojet  # Uncomment and modify if needed

echo "Running with seed ${SEED}"
NNLOJET -run ${RUNCARD} -iseed ${SEED}
EOF
echo "Submitted job with seed ${SEED}."
done

