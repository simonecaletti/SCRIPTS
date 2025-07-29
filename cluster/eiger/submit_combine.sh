#!/bin/bash

# ------------------- Configuration -------------------
SBATCH_TIME="02:00:00"
SBATCH_CPUS=24
SBATCH_MEM="1G"
JOB_NAME="combine"
LOGFILE="combine.log"
# -----------------------------------------------------

# Submit the SLURM job directly (no temp files)
sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=$JOB_NAME
#SBATCH --output=$LOGFILE
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=$SBATCH_CPUS
#SBATCH --time=$SBATCH_TIME
#SBATCH --mem=$SBATCH_MEM

echo "Running on: \$(hostname)"
echo "Checking for combine.ini..."

if [ ! -f combine.ini ]; then
  echo "[ERROR] combine.ini not found in current directory: \$(pwd)"
  exit 1
fi

echo "Starting nnlojet-combine.py at: \$(date)"
nnlojet-combine.py
echo "Finished at: \$(date)"
EOF

