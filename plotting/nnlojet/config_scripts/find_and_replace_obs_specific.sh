#!/usr/bin/env bash
set -euo pipefail

# =========================
# CONFIG — EDIT THESE
# =========================
# Folders to scan (space-separated)
FOLDERS=( "config/BB" "config/GG" "config/BBmid" "config/GGmid" "config/BBsmall" "config/GGsmall" )

# Exact filename to target in each folder (same name across folders)
TARGET_NAME="costh_j12"

# Lines that start with this string will be removed.
# (Default behavior: fixed-string, anchored at start-of-line)
REMOVE_PATTERN='xmax'

# Set to "startswith" (fixed string) or "regex"
PATTERN_MODE="startswith"

# Line to append at the end of each matching file
LINE_TO_ADD='xmax = 0.75'
# Optional: create a backup alongside each file (e.g., ".bak"), or leave empty to disable
BACKUP_EXT=".bak"

# Optional: avoid adding LINE_TO_ADD if it already exists exactly as a line
AVOID_DUPLICATES=false
# =========================


update_one_file () {
  local file="$1"
  local tmp
  tmp="$(mktemp)"

  # Backup if requested
  if [[ -n "${BACKUP_EXT}" ]]; then
    cp -p -- "$file" "$file${BACKUP_EXT}"
  fi

  # Remove lines according to pattern/mode
  if ! awk -v p="$REMOVE_PATTERN" -v mode="$PATTERN_MODE" '
    function startswith(s, pat) { return index(s, pat) == 1 }
    {
      if (mode == "regex") {
        if ($0 ~ ("^" p)) next;    # remove lines that match regex at start
      } else {
        if (startswith($0, p)) next;# remove lines that start with fixed string
      }
      print
    }
  ' "$file" > "$tmp"; then
    echo "awk failed while processing: $file" >&2
    rm -f "$tmp"
    return 1
  fi

  # Append the new line (optionally skip duplicates)
  if $AVOID_DUPLICATES; then
    if ! grep -qxF -- "$LINE_TO_ADD" "$tmp"; then
      printf '%s\n' "$LINE_TO_ADD" >> "$tmp"
    fi
  else
    printf '%s\n' "$LINE_TO_ADD" >> "$tmp"
  fi

  mv -- "$tmp" "$file"
  echo "Updated $file"
}

# Walk all folders and process files named TARGET_NAME
for dir in "${FOLDERS[@]}"; do
  [[ -d "$dir" ]] || { echo "Skip: $dir (not a directory)"; continue; }
  # Find only files with the exact name
  while IFS= read -r -d '' f; do
    update_one_file "$f"
  done < <(find "$dir" -type f -name "$TARGET_NAME" -print0)
done
