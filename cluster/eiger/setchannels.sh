#!/usr/bin/env bash
set -euo pipefail

############################################
#         >>>> EDIT HERE <<<<
############################################

# Channels to create if none are specified on the CLI
DEFAULT_CHANNELS=(R V VV RV RR)

# Enable splitting RR into two runcards: <base>.a.run and <base>.b.run,
# and two submit scripts: submit_nnlojet_a.sh / submit_nnlojet_b.sh
SPLIT_RR=true

# NUM_NODES for each channel (used in submit_nnlojet.sh)
# Example: R,V -> 5 ; VV,RV,RR -> 8
# You can also specify RRa / RRb to override only in split RR mode
declare -A NUM_NODES_MAP=(
  [R]=2
  [V]=2
  [VV]=5
  [RV]=8
  #[RR]=8
  # Optional specific overrides when SPLIT_RR=true:
  [RRa]=8
  [RRb]=8
)

# WARMUP for each channel (in <base>.warmup.run)
# You can also specify RRa / RRb to override only in split RR mode (if needed)
declare -A WARMUP_MAP=(
  #[VV]="500000[20]"
  #[RR]="500000[20]"
  #[RR]="500000[10]"
  # Optional:
  #[RRa]="500000[10]"
  #[RRb]="500000[20]"
)

# PRODUCTION for each channel (in <base>.run)
# Only listed channels will be changed; others left as-is.
# You can also specify RRa / RRb to override only in split RR mode
declare -A PRODUCTION_MAP=(
  [V]="200000[20]"
  [R]="200000[20]"
  [VV]="500000[20]"
  [RV]="500000[20]"
  [RR]="500000[20]"
  # Optional (takes precedence over RR if present):
  [RRa]="80000[5]"
  [RRb]="200000[20]"
)

# Defaults to apply to LO templates BEFORE copying
LO_TEMPLATE_NUM_NODES_DEFAULT=1
LO_TEMPLATE_WARMUP_DEFAULT="100000[10]"
LO_TEMPLATE_PRODUCTION_DEFAULT="100000[20]"

############################################

usage() {
  cat <<EOF
Usage: $(basename "$0") <runcard_base> [channels...]

Arguments:
  runcard_base   Base name (e.g. 'myproc' -> myproc.run, myproc.warmup.run)
  channels...    Optional. Defaults to: ${DEFAULT_CHANNELS[*]}

This script:
  - Normalizes line endings to Unix (LF) to avoid ^M issues
  - Updates LO templates to chosen defaults (NUM_NODES, production, warmup)
  - Copies files from LO/ to each channel directory
  - Sets 'channel = <channel>' in runcards
  - Rewrites NAME=... in submit_nnlojet.sh to use the channel name
  - Applies per-channel NUM_NODES, production (run), and warmup (warmup.run) overrides
  - If SPLIT_RR=true and channel=RR:
      • creates <base>.a.run (region=a) and <base>.b.run (region=b)
      • creates submit_nnlojet_a.sh -> uses <base>.a.run, labeled RRa
      • creates submit_nnlojet_b.sh -> uses <base>.b.run, labeled RRb
    and allows overrides via keys RRa / RRb in the *_MAP settings
EOF
}

[[ ${1-} == "-h" || ${1-} == "--help" || $# -lt 1 ]] && { usage; exit 0; }

RUNCARD_BASE="$1"
shift || true

CHANNELS=("$@")
if [ ${#CHANNELS[@]} -eq 0 ]; then
  CHANNELS=("${DEFAULT_CHANNELS[@]}")
fi

LO_DIR="LO"
FILES=(
  "submit_nnlojet.sh"
  "${RUNCARD_BASE}.run"
  "${RUNCARD_BASE}.warmup.run"
)

# ---- helpers ----

sanitize_file() {
  # sanitize_file <file>  -> convert CRLF to LF (remove trailing \r)
  local f="$1"
  sed -i 's/\r$//' "$f" 2>/dev/null || true
}

set_kv_quoted() {
  # set_kv_quoted <file> <VAR> <value>
  local f="$1" var="$2" val="$3"
  sanitize_file "$f"
  if grep -qiE "^\s*${var}\s*=" "$f"; then
    sed -i -E "s|^\s*(${var}\s*=\s*).*|\1\"${val}\"|" "$f"
  else
    printf '%s="%s"\n' "$var" "$val" >> "$f"
  fi
  sanitize_file "$f"
}

ensure_line_kv() {
  # ensure_line_kv <file> <key> <value>
  local f="$1" key="$2" val="$3"
  sanitize_file "$f"
  if grep -qiE "^\s*${key}\s*=" "$f"; then
    sed -i -E "s|(^\s*${key}\s*=\s*).*$|\1${val}|" "$f"
  else
    printf "\n%s = %s\n" "$key" "$val" >> "$f"
  fi
  sanitize_file "$f"
}

set_num_nodes() {
  # set_num_nodes <file> <value>
  local f="$1" val="$2"
  sanitize_file "$f"
  if grep -qiE "^\s*NUM_NODES\s*=" "$f"; then
    sed -i -E "s|(^\s*NUM_NODES\s*=\s*).*$|\1${val}|" "$f"
  else
    sed -i "1i NUM_NODES=${val}" "$f"
  fi
  sanitize_file "$f"
}

apply_channel_to_submit() {
  # apply_channel_to_submit <file> <label> [runcard_filename] [base_name]
  local f="$1" label="$2"
  local runcard="${3-}" base="${4-}"
  sanitize_file "$f"

  # Replace LO -> <label> ONLY on the NAME= line (regardless of quotes)
  sed -i -E "/^\s*NAME\s*=/ s/LO/${label}/g" "$f"

  # Fallback: replace standalone 'LO' elsewhere if any still present
  if grep -q '\bLO\b' "$f"; then
    sed -i -E "s/\bLO\b/${label}/g" "$f"
  fi

  # >>> FIXED: write RUNCARD as a *quoted* assignment, robust to comments/trailing text
  if [[ -n "${runcard}" ]]; then
    set_kv_quoted "$f" "RUNCARD" "${runcard}"
    # Also replace any plain occurrences of base.run (if provided) with the new runcard name
    if [[ -n "${base}" ]]; then
      sed -i -E "s|\b${base}\.run\b|${runcard}|g" "$f"
    fi
  fi

  # NUM_NODES per label (prefer specific RRa/RRb over RR)
  local nodes=""
  if [[ -n "${NUM_NODES_MAP[$label]+x}" ]]; then
    nodes="${NUM_NODES_MAP[$label]}"
  else
    local base_label="${label%%[ab]}"
    if [[ -n "${NUM_NODES_MAP[$base_label]+x}" ]]; then
      nodes="${NUM_NODES_MAP[$base_label]}"
    fi
  fi
  if [[ -n "$nodes" ]]; then
    set_num_nodes "$f" "$nodes"
  fi

  chmod +x "$f"
  sanitize_file "$f"
}

apply_channel_to_run_basic() {
  # apply_channel_to_run_basic <file> <channel>
  local f="$1" ch="$2"
  sanitize_file "$f"

  # channel = <ch>  (if present), else fallback replace LO
  if grep -qiE "^\s*channel\s*=" "$f"; then
    sed -i -E "s|(^\s*channel\s*=\s*)\w+|\1${ch}|I" "$f"
  else
    sed -i -E "s/\bLO\b/${ch}/g" "$f"
  fi
}

apply_production_override() {
  # apply_production_override <file> <label>
  # label can be channel or subchannel (RRa/RRb). Prefer label; fallback to its base (RR).
  local f="$1" label="$2"
  local base="${label%%[ab]}"
  local val=""
  if [[ -n "${PRODUCTION_MAP[$label]+x}" ]]; then
    val="${PRODUCTION_MAP[$label]}"
  elif [[ -n "${PRODUCTION_MAP[$base]+x}" ]]; then
    val="${PRODUCTION_MAP[$base]}"
  fi
  if [[ -n "$val" ]]; then
    ensure_line_kv "$f" "production" "$val"
  fi
}

apply_warmup_override() {
  # apply_warmup_override <file> <label>
  local f="$1" label="$2"
  local base="${label%%[ab]}"
  local val=""
  if [[ -n "${WARMUP_MAP[$label]+x}" ]]; then
    val="${WARMUP_MAP[$label]}"
  elif [[ -n "${WARMUP_MAP[$base]+x}" ]]; then
    val="${WARMUP_MAP[$base]}"
  fi
  if [[ -n "$val" ]]; then
    ensure_line_kv "$f" "warmup" "$val"
  fi
}

set_region_on_channels_line() {
  # set_region_on_channels_line <file> <a|b>
  # Un-comments the 'region' in the CHANNELS line (removes '!') and sets region accordingly.
  local f="$1" region="$2"
  sanitize_file "$f"
  # Remove '!' before region only on lines starting with CHANNELS
  sed -i -E "/^\s*CHANNELS/ s/!\s*region/region/I" "$f"
  # Set the region value on CHANNELS line
  sed -i -E "/^\s*CHANNELS/ s/(region\s*=\s*)[[:alnum:]_]+/\1${region}/I" "$f"
  sanitize_file "$f"
}

apply_channel_to_run() {
  # apply_channel_to_run <dir> <base> <channel>
  local dir="$1" base="$2" ch="$3"

  local runfile="${dir}/${base}.run"
  local warmfile="${dir}/${base}.warmup.run"

  if [[ "$ch" == "RR" && "$SPLIT_RR" == "true" ]]; then
    # Create <base>.a.run and <base>.b.run
    local run_a="${dir}/${base}.a.run"
    local run_b="${dir}/${base}.b.run"

    cp -f "$runfile" "$run_a"
    cp -f "$runfile" "$run_b"
    rm -f "$runfile"

    # For each split runcard: set channel=RR, set region, and apply production overrides
    apply_channel_to_run_basic "$run_a" "RR"
    set_region_on_channels_line "$run_a" "a"
    apply_production_override "$run_a" "RRa"

    apply_channel_to_run_basic "$run_b" "RR"
    set_region_on_channels_line "$run_b" "b"
    apply_production_override "$run_b" "RRb"

    # Warmup remains a single file unless you also want split warmups.
    # Apply warmup overrides (prefer RRa/RRb keys if provided, else RR)
    if [[ -f "$warmfile" ]]; then
      apply_channel_to_run_basic "$warmfile" "RR"
      apply_warmup_override "$warmfile" "RR"
    fi

    # ---- Create split submit scripts ----
    local submit_base="${dir}/submit_nnlojet.sh"
    local submit_a="${dir}/submit_nnlojet_a.sh"
    local submit_b="${dir}/submit_nnlojet_b.sh"

    cp -f "$submit_base" "$submit_a"
    cp -f "$submit_base" "$submit_b"
    rm -f "$submit_base"  #<<< remove the default one if split

    # Point each to the correct runcard and label NAME as RRa / RRb
    apply_channel_to_submit "$submit_a" "RRa" "${base}.a.run" "${base}"
    apply_channel_to_submit "$submit_b" "RRb" "${base}.b.run" "${base}"

  else
    # Standard path for non-RR channels (or if SPLIT_RR=false)
    apply_channel_to_run_basic "$runfile" "$ch"
    apply_production_override "$runfile" "$ch"
    if [[ -f "$warmfile" ]]; then
      apply_channel_to_run_basic "$warmfile" "$ch"
      apply_warmup_override "$warmfile" "$ch"
    fi
  fi
}

# ---- sanity checks ----
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

# ---- Normalize LO templates and update to defaults ----
echo "==> Sanitizing and updating LO templates"
for f in "${FILES[@]}"; do
  sanitize_file "${LO_DIR}/${f}"
done
set_num_nodes       "${LO_DIR}/submit_nnlojet.sh"             "${LO_TEMPLATE_NUM_NODES_DEFAULT}"
ensure_line_kv      "${LO_DIR}/${RUNCARD_BASE}.run"           "production" "${LO_TEMPLATE_PRODUCTION_DEFAULT}"
ensure_line_kv      "${LO_DIR}/${RUNCARD_BASE}.warmup.run"    "warmup"     "${LO_TEMPLATE_WARMUP_DEFAULT}"

# ---- Per-channel creation ----
for ch in "${CHANNELS[@]}"; do
  echo "==> Creating channel '${ch}'"
  mkdir -p "${ch}"

  # Copy base files from LO/
  for f in "${FILES[@]}"; do
    cp -f "${LO_DIR}/${f}" "${ch}/${f}"
    sanitize_file "${ch}/${f}"
  done

  # Apply edits to runcards (handles RR split if enabled)
  apply_channel_to_run "${ch}" "${RUNCARD_BASE}" "${ch}"

  # Apply edits to submit script for non-split cases (RR split handled inside apply_channel_to_run)
  if ! { [[ "$ch" == "RR" && "$SPLIT_RR" == "true" ]]; }; then
    apply_channel_to_submit  "${ch}/submit_nnlojet.sh" "${ch}"
  fi
done

echo
echo "All channels created successfully."

