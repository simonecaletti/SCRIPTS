#!/bin/bash

# Usage: ./count_err_files.sh /path/to/directory [--print]

# Check arguments
if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/directory [--print]"
  exit 1
fi

DIR="$1"
PRINT=false

if [ "$2" == "--print" ]; then
  PRINT=true
fi

# Check that DIR is valid
if [ ! -d "$DIR" ]; then
  echo "Error: '$DIR' is not a valid directory."
  exit 1
fi

# Enable nullglob to avoid errors if no .err files
shopt -s nullglob

# Initialize counters
total_count=0
non_empty_count=0

# Loop through .err files
for file in "$DIR"/*.err; do
  ((total_count++))
  if [ -s "$file" ]; then
    ((non_empty_count++))
    if $PRINT; then
      echo "$file"
    fi
  fi
done

# Final summary
echo
echo "Total .err files checked in '$DIR': $total_count"
echo "Number of non-empty .err files: $non_empty_count"

