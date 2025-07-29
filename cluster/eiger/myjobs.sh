#!/bin/bash

# Get current username
USER=$(whoami)

# Display jobs owned by this user
squeue --me \
  --format="%.18i %.9P %.20j %.8u %.2t %.10M %.6D %R" \
  --sort=-t

