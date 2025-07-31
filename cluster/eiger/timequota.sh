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
month=$((10#$(date +%m)))  # mese corrente come decimale
year=$(date +%Y)
quarter_start_month=$(( ((month - 1) / 3) * 3 + 1 ))
QUARTER_START=$(printf "%s-%02d-01" "$year" "$quarter_start_month")


# === EXTRACT FULL SREPORT ===
SREPORT_OUTPUT=$(sreport cluster AccountUtilizationByUser Start=$QUARTER_START End=now Accounts=$ACCOUNT 2>/dev/null)
#echo $SREPORT_OUTPUT

# === PRINT MEMBER USAGE (CPU Minutes) ===
echo -e "👥  Member Usage (CPU Minutes) for account '$ACCOUNT' since $QUARTER_START"
echo    "------------------------------------------------------------"
iflag=0
echo "$SREPORT_OUTPUT" | awk '
  /^[[:space:]]*alps-eig\+/ {
    if ($3 != "") {
      if (iflag != 0) {
      # User line: column 3 = login, 4 = name, 6 = CPU minutes
      printf " - %-15s %-20s %.2f Node/hours\n", $3, $4, $6/256/60
      }
     iflag ++;
    }
  }'
echo ""

# === EXTRACT TOTAL USAGE ===
CPU_MIN=$(echo "$SREPORT_OUTPUT" | awk 'NF == 4 && $3 ~ /^[0-9]+$/ { print $3 }')
#echo "cpu min: $CPU_MIN"

# === CONVERT TO NODE-HOURS ===
USED_NDHR=$(awk -v cmin=$CPU_MIN -v cores=$CPU_PER_NODE 'BEGIN { printf "%.2f", cmin / (cores * 60) }')
USED_MIN=$(awk "BEGIN {printf \"%.2f\", $USED_NDHR * 60}")
USED_DAY=$(awk "BEGIN {printf \"%.2f\", $USED_NDHR / 24}")

# === DISPLAY TOTAL USAGE ===
echo -e "🧮  Total Node-Hour Usage This Quarter from group $ACCOUNT (since $QUARTER_START)"
echo    "-------------------------------------------------------------"
echo "Used Wall Time (scaled by core usage):"
echo " - Node/minutes : $USED_MIN"
echo " - Node/hours   : $USED_NDHR"
echo " - Node/days    : $USED_DAY"
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

