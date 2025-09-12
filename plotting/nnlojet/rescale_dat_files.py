#!/usr/bin/env python3

import os
import glob

# === USER SETTINGS ===
input_dir = "hbb14nnlo/combined/Final"
output_dir = "hcc14nnlo/combined/Final"  # <-- Output directory
file_pattern = "*.dat"
# compute rescaling factor
mb = 4.20
mc = 1.29
rescale_factor = mc**2/mb**2                    # <-- Change only in the Yukawa factor

# === Ensure output directory exists ===
os.makedirs(output_dir, exist_ok=True)

# === FUNCTION TO PROCESS FILE ===
def rescale_file(input_path, output_path, factor):
    with open(input_path, 'r') as fin:
        lines = fin.readlines()

    output_lines = []
    for line in lines:
        if line.strip().startswith("#") or line.strip() == "":
            output_lines.append(line)
            continue

        tokens = line.strip().split()
        if len(tokens) < 11:
            output_lines.append(line)
            continue

        # Rescale only the tot_scale0X columns: positions 3,5,7,9 (0-based)
        for i in [3, 5, 7, 9]:
            tokens[i] = f"{float(tokens[i]) * factor:.11E}"

        output_lines.append(" ".join(tokens) + "\n")

    with open(output_path, 'w') as fout:
        fout.writelines(output_lines)
    print(f"[✓] Wrote: {output_path}")

# === MAIN ===
pattern = os.path.join(input_dir, file_pattern)
files = glob.glob(pattern)
print(f"Found {len(files)} file(s) matching '{file_pattern}' in {input_dir}")

for input_file in files:
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_dir, filename)
    rescale_file(input_file, output_file, rescale_factor)
