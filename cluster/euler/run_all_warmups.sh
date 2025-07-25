#!/usr/bin/env bash
set -euo pipefail

# Folders to scan
dirs=(LO R RR RV V VV)

for d in "${dirs[@]}"; do
    script="$d/submit_warmup.sh"
    if [[ -f "$script" ]]; then
        echo "[$(date '+%F %T')] -> $script"
        ( cd "$d" && bash submit_warmup.sh )
    else
        echo "WARN: $script not found" >&2
    fi
done

echo "All done."
