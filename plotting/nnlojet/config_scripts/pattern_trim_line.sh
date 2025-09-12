#!/bin/bash

# === CONFIGURABLE PARAMETERS ===
CONFIG_DIR="config/TOTmid"        # Directory with .config files
PATTERN="ycut ="           # Pattern to delete (can be changed to legend, color, etc.)

# === PROCESS FILES ===
for file in "$CONFIG_DIR"/*.config; do
    if [[ -f "$file" ]]; then
        sed "/^${PATTERN}[[:space:]]*=/d" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        echo "Removed line starting with '${PATTERN} =' from $file"
    fi
done
