#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") <runcard_base> [channels...]

Arguments:
  runcard_base   Base name of the runcards (e.g. 'myproc' for myproc.run and myproc.warmup.run)
  channels...    (optional) list of channels to create. Default: R V VV RV RR

This script:
  - Copies files from the LO/ folder
  - Creates folders named after each channel
  - Replaces 'channel = LO' with 'channel = <channel>' in runcards
  - Replaces NAME="...LO" with NAME="...<channel>" in both submit scripts
  - Replaces other standalone 'LO' tokens as fallback
EOF
}

if [[ ${1-} == "-h" || ${1-} == "--help" || $# -lt 1 ]]; then
  usage
  exit 0
fi

RUNCARD_BASE="$1"
shift || true
CHANNELS=("$@")
if [ ${#CHANNELS[@]} -eq 0 ]; then
  CHANNELS=(R V VV RV RR)
fi

LO_DIR="LO"
FILES=(
  "submit_warmup.sh"
  "submit_nnlojet.sh"
  "${RUNCARD_BASE}.run"
  "${RUNCARD_BASE}.warmup.run"
)

# Sanity checks
for f in "${FILES[@]}"; do
  if [ ! -f "${LO_DIR}/${f}" ]; then
    echo "ERROR: Missing ${LO_DIR}/${f}" >&2
    exit 1
  fi
done

echo "Using LO dir     : ${LO_DIR}"
echo "Runcard base     : ${RUNCARD_BASE}"
echo "Channels         : ${CHANNELS[*]}"
echo

for ch in "${CHANNELS[@]}"; do
  echo "==> Creating channel '${ch}'"
  mkdir -p "${ch}"

  # Copy files
  for f in "${FILES[@]}"; do
    cp -f "${LO_DIR}/${f}" "${ch}/${f}"
  done

  # Edit runcards
  for rc in "${ch}/${RUNCARD_BASE}.run" "${ch}/${RUNCARD_BASE}.warmup.run"; do
    if grep -qiE "^\s*channel\s*=" "$rc"; then
      sed -i.bak -E "s|(^\s*channel\s*=\s*)\w+|\1${ch}|I" "$rc"
    else
      sed -i.bak -E "s/\bLO\b/${ch}/g" "$rc"
    fi
    rm -f "${rc}.bak"
  done

  # Edit submit scripts
  for shf in "${ch}/submit_warmup.sh" "${ch}/submit_nnlojet.sh"; do
    # Replace NAME="...LO" with NAME="...<ch>"
    sed -i.bak -E "s|^(NAME\s*=\s*\"?.*?)LO(\"?)$|\1${ch}\2|" "$shf"

    # Fallback: replace standalone 'LO'
    if grep -q '\bLO\b' "$shf"; then
      sed -i -E "s/\bLO\b/${ch}/g" "$shf"
    fi

    rm -f "${shf}.bak"
    chmod +x "$shf"
  done
done

echo
echo "All channels created successfully."

