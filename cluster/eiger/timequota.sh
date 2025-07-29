#!/bin/bash

# === CONFIG ===
BAR_LEN=25
SCALE_NDHR=5000                 # Soft quota for visualization in node-hours
CPU_PER_NODE=256                # Eiger: 256 logical cores per node
ACCOUNT="eth5f"

# === COLORS ===
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
GREEN=$(tput setaf 2)
RESET=$(tput sgr0)

# === DETECT CURRENT QUARTER START ===
QUARTER_START=$(date +"%Y")-$(printf "%02d" $(( (($(date +%m)-1)/3*3)+1 )))-01

# === EXTRACT CPU MINUTES FROM SREPORT ===
CPU_MIN=$(sreport cluster AccountUtilizationByUser Start=$QUARTER_START End=now Accounts=$ACCOUNT 2>/dev/null | \
awk -v user="$USER" '$0 ~ user {print $6}')

# === IF NO DATA ===
if [[ -z "$CPU_MIN" ]]; then
    echo "No usage data available from sreport for account '$ACCOUNT' since $QUARTER_START."
    exit 1
fi

# === COMPUTE NODE-HOURS USED FROM COMPLETED JOBS ===
USED_HR=$(sreport cluster AccountUtilizationByUser Start=2025-07-01 End=now Accounts=eth5f | \
awk '/'"$USER"'/ {cpu_min = $6; node_hr = cpu_min / (256 * 60); printf "%.2f", node_hr}')

ù# === CONVERT TO NODE-HOURS ===
USED_NDHR=$(awk -v cmin=$CPU_MIN -v cores=$CPU_PER_NODE 'BEGIN { printf "%.2f", cmin / (cores * 60) }')
USED_MIN=$(awk "BEGIN {printf \"%.2f\", $USED_NDHR * 60}")
USED_DAY=$(awk "BEGIN {printf \"%.2f\", $USED_NDHR / 24}")

# === DISPLAY USAGE ===
echo -e "🧮  Node-Hour Usage This Quarter (since $QUARTER_START)"
echo    "------------------------------------------------------"
echo "Used Wall Time (scaled by core usage):"
echo " - Node-Minutes : $USED_MIN"
echo " - Node-Hours   : $USED_NDHR"
echo " - Node-Days    : $USED_DAY"
echo ""

# === PRINT BAR FUNCTION ===
print_bar() {
    local percent=$1
    local filled=$(awk -v p=$percent -v l=$BAR_LEN 'BEGIN {printf "%d", p * l / 100}')
    local empty=$((BAR_LEN - filled))

    # Choose color
    if (( $(awk "BEGIN {print ($percent < 50)}") )); then
        COLOR=$GREEN
    elif (( $(awk "BEGIN {print ($percent < 80)}") )); then
        COLOR=$YELLOW
    else
        COLOR=$RED
    fi

    echo -n " - ${COLOR}["
    printf "%0.s#" $(seq 1 $filled)
    printf "%0.s." $(seq 1 $empty)
    echo "]${RESET} ($percent%)"
}

# === PERCENTAGE + BAR ===
PCT=$(awk "BEGIN {printf \"%.2f\", ($USED_NDHR/$SCALE_NDHR)*100}")
echo "Used quota scaled to quarter availability ($SCALE_NDHR node/hours):"
print_bar "$PCT"

