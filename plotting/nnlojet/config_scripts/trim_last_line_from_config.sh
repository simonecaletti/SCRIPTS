#!/bin/bash

CONFIG_DIR="config/BB"

for file in "$CONFIG_DIR"/*.config; do
    if [[ -f "$file" ]]; then
        # Remove the last line and overwrite the file
        head -n -1 "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        echo "Trimmed last line from $file"
    fi
done
