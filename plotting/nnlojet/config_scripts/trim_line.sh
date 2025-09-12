#!/bin/bash

CONFIG_DIR="config/INEX"
LINE_TO_DELETE=3  # <-- CHANGE this to the line number you want to delete

for file in "$CONFIG_DIR"/*.config; do
    if [[ -f "$file" ]]; then
        # Delete the specific line and overwrite the file
        sed "${LINE_TO_DELETE}d" "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        echo "Removed line $LINE_TO_DELETE from $file"
    fi
done

