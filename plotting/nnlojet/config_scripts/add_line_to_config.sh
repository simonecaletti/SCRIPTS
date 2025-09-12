#!/bin/bash

# Directory containing the .config files
CONFIG_DIR="config/TOTmid"

# Line to add
#LINE_TO_ADD='process = $e^+e^-\rightarrow ZH @ NNLO$'
#LINE_TO_ADD='line_style = ["-", "-", "-", "-", "dotted", "dotted", "dotted", "dotted"]'
#LINE_TO_ADD='legend = [r"$H\rightarrow b\bar{b}$", r"$H\rightarrow c\bar{c}$", r"$H\rightarrow gg$", "Total"]'
#LINE_TO_ADD='color = ["orange", "lightblue", "purple", "seagreen", "orange", "lightblue", "purple", "seagreen"]'
#LINE_TO_ADD='scale = m_H'
#LINE_TO_ADD='ylabel_bottom_list = [r"Ratio to $H\rightarrow b\bar{b}$", r"Ratio to $H\rightarrow b\bar{b}$"]'
LINE_TO_ADD='ycut = 0.03'
#  Loop through all .config files
for file in "$CONFIG_DIR"/*.config; do
    echo "$LINE_TO_ADD" >> "$file"
    echo "Updated $file"
done
