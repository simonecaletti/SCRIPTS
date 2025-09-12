#!/bin/bash

# Usage:
# ./replace_line.sh "old line content" "new line content"

OLD_LINE="$1"
NEW_LINE="$2"
CONFIG_DIR="config/TOT"

if [[ -z "$OLD_LINE" || -z "$NEW_LINE" ]]; then
  echo "Usage: $0 \"old line\" \"new line\""
  exit 1
fi

for file in "$CONFIG_DIR"/*.config; do
    if grep -Fxq "$OLD_LINE" "$file"; then
        sed -i "s|^$OLD_LINE$|$NEW_LINE|" "$file"
        echo "Replaced in $file"
    fi
done
