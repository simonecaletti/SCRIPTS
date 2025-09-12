#!/usr/bin/env python3

import os
import glob

# === USER SETTINGS ===
input_dir_1 = "hbb14nnlo/combined/Final/"
input_dir_2 = "hcc14nnlo/combined/Final/"
input_dir_3 = "hgg14nnlo/combined/Final/"
output_dir  = "tot14nnlo/combined/Final/"
file_pattern = "*.dat"  # Match common file extensions
tot_scale_indices = [3, 5, 7, 9]  # 0-based indices of tot_scale01..04

# === Ensure output directory exists ===
os.makedirs(output_dir, exist_ok=True)

def read_file_lines(path):
    with open(path, 'r') as f:
        return f.readlines()

def is_data_line(line):
    return line.strip() and not line.strip().startswith("#")

def parse_line_to_tokens(line):
    return line.strip().split()

def sum_scale_columns(tokens_list):
    result = tokens_list[0][:]  # start with a copy of first
    for i in tot_scale_indices:
        summed = sum(float(tokens[i]) for tokens in tokens_list)
        result[i] = f"{summed:.11E}"
    return result

def process_file(filename):
    file1 = os.path.join(input_dir_1, filename)
    file2 = os.path.join(input_dir_2, filename)
    file3 = os.path.join(input_dir_3, filename)

    if not all(os.path.isfile(f) for f in [file1, file2, file3]):
        print(f"❌ Skipping {filename} — missing in one of the folders")
        return

    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)
    lines3 = read_file_lines(file3)

    if len(lines1) != len(lines2) or len(lines1) != len(lines3):
        print(f"❌ Skipping {filename} — line count mismatch")
        return

    output_lines = []
    for l1, l2, l3 in zip(lines1, lines2, lines3):
        if not is_data_line(l1):
            output_lines.append(l1)
            continue

        tokens1 = parse_line_to_tokens(l1)
        tokens2 = parse_line_to_tokens(l2)
        tokens3 = parse_line_to_tokens(l3)

        if len(tokens1) != len(tokens2) or len(tokens1) != len(tokens3):
            print(f"❌ Skipping line in {filename} — token count mismatch")
            return

        summed_tokens = sum_scale_columns([tokens1, tokens2, tokens3])
        output_lines.append(" ".join(summed_tokens) + "\n")

    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as f:
        f.writelines(output_lines)
    print(f"[✓] Wrote: {output_path}")

# === MAIN LOOP ===
input_files = glob.glob(os.path.join(input_dir_1, file_pattern))
file_names = [os.path.basename(f) for f in input_files]

print(f"Found {len(file_names)} file(s) in {input_dir_1} to process")

for fname in file_names:
    process_file(fname)
