#!/usr/bin/env python3
import os, glob, math, shutil
import argparse
import ast

# === PARSER ===
parser = argparse.ArgumentParser(description="Rebinning script for NNLOJET output distributions")
parser.add_argument('--input', required=True, help="Input filename")
parser.add_argument('--output', required=True, help="Output filename")
parser.add_argument('--rebinning', type=ast.literal_eval, required=True, help="Rebinning: sorted cutpoints; indices are 0-based data-line indices")
parser.add_argument('--pattern', required=True, help="File pattern for rebinning")
args = parser.parse_args()

#input_dir   = "hbb15nnlo/combined.temp/Final"
#output_dir  = "hbb15nnlo/combined/Final"
input_dir = args.input
output_dir = args.output

#file_pattern = "*costh_j12*"
#file_pattern = "*min_costh*"
file_pattern = args.pattern 

# Sorted cutpoints; indices are 0-based data-line indices

#rebinning for costh_j12
#step 1
#rebinning = list(range(0, 28, 4))
#rebinning += [27]
#step2
#rebinning = list(range(63, 179, 4))

#rebinning for min_costh
#rebinning = list(range(38, 90, 4))
rebinning = args.rebinning 

# Which value/error columns to aggregate (0-based)
# Each tuple is (value_idx, error_idx). If a column has no error, set error_idx=None.
VALUE_SCHEMA = [(3,4), (5,6), (7,8), (9,10)]  # e.g. tot_scale01,02,03,04 with their errors

# Formatting used for numeric outputs
def _fmt(x): return f"{x:.11E}"

os.makedirs(output_dir, exist_ok=True)

# ------------------------------------------------------------
#                MODULAR AGGREGATION STRATEGY
#   Tweak ONLY the functions in this section to change rules.
# ------------------------------------------------------------
def edge_lower(rows):
    """Lower edge of the aggregated bin."""
    return float(rows[0][0])

def edge_upper(rows):
    """Upper edge of the aggregated bin."""
    return float(rows[-1][2])

def edge_center(rows):
    """Center of the aggregated bin (default: width-weighted mean of centers)."""
    num, den = 0.0, 0.0
    for tok in rows:
        lo_i, ce_i, up_i = float(tok[0]), float(tok[1]), float(tok[2])
        w = max(up_i - lo_i, 0.0)
        num += ce_i * w
        den += w
    return (num / den) if den > 0 else float(rows[0][1])

def value_agg(rows, idx):
    """Weighted average of values with bin width as weight."""
    num, den = 0.0, 0.0
    for tok in rows:
        lo, up = float(tok[0]), float(tok[2])
        width = up - lo
        val = float(tok[idx])
        num += val * width
        den += width
    return num / den if den > 0 else 0.0

def error_agg(rows, val_idx, err_idx):
    """
    Weighted error aggregation.
    Formula:
        newerr = sqrt( sum_i (err_i * width_i)^2 ) / sum_i width_i
    """
    if err_idx is None:
        return 0.0

    num = 0.0   # accumulate (err_i * width_i)^2
    den = 0.0   # accumulate width_i

    for tok in rows:
        lo, up = float(tok[0]), float(tok[2])
        width = up - lo
        if err_idx < len(tok):
            err_i = float(tok[err_idx])
            num += (err_i * width) ** 2
        den += width

    return math.sqrt(num) / den if den > 0 else 0.0

# ------------------------------------------------------------


# ---------- Regular line (outside segments) ----------
def process_regular(tokens, idx):
    return " ".join(tokens) + "\n"

# ---------- Collapse one segment into ONE line ----------
def aggregate_segment_to_line(rows, schema):
    """
    rows   : list[list[str]] tokens of data lines in the segment
    schema : list[(val_idx, err_idx)]
    returns: a SINGLE aggregated line string
    """
    # Start from the first row structure to preserve number/order of tokens
    out = rows[0][:]

    # Edges & center
    try:
        out[0] = _fmt(edge_lower(rows))
        out[1] = _fmt(edge_center(rows))
        out[2] = _fmt(edge_upper(rows))
    except Exception:
        # keep original if parsing fails, but try to proceed for values
        pass

    # Values & errors
    for (v_idx, e_idx) in schema:
        if v_idx < len(out):
            try:
                out[v_idx] = _fmt(value_agg(rows, v_idx))
            except Exception:
                pass
        if e_idx is not None and e_idx < len(out):
            try:
                out[e_idx] = _fmt(error_agg(rows, v_idx, e_idx))
            except Exception:
                pass

    return " ".join(out) + "\n"

# ---------- Segment helpers ----------
def build_segments(cuts):
    """Return list of (lo, hi, inclusive_hi) for segments:
       [c0,c1), [c1,c2), ..., last is [c_{n-2}, c_{n-1}] (right-closed)."""
    if len(cuts) < 2: return []
    segs = []
    for i in range(len(cuts) - 2):
        segs.append((cuts[i], cuts[i+1], False))  # right-open
    segs.append((cuts[-2], cuts[-1], True))       # last right-closed
    return segs

def rebinning_file(input_path, output_path, cuts):
    segments = build_segments(cuts)

    with open(input_path, "r") as fin:
        lines = fin.readlines()

    output_lines = []
    data_index = 0  # counts only non-comment, non-empty data lines

    seg_iter = iter(segments)
    try:
        current_seg = next(seg_iter)
    except StopIteration:
        current_seg = None

    def in_current_segment(idx, seg):
        if seg is None: return False
        lo, hi, closed = seg
        return (lo <= idx <= hi) if closed else (lo <= idx < hi)

    seg_buffer = []
    i_line = 0
    seg_id_counter = 0  # stable segment id without O(n) index lookups

    while i_line < len(lines):
        line = lines[i_line]
        stripped = line.strip()

        # Pass-through for comments/blanks
        if stripped.startswith("#") or stripped == "":
            output_lines.append(line)
            i_line += 1
            continue

        tokens = stripped.split()

        if current_seg is not None and in_current_segment(data_index, current_seg):
            # collect tokens for this segment
            seg_buffer.append(tokens)

            # is this the last data line of the current segment?
            lo, hi, closed = current_seg
            end_here = (data_index == hi) if closed else (data_index + 1 == hi)

            data_index += 1
            i_line += 1

            if end_here:
                # collapse and flush a single line
                agg_line = aggregate_segment_to_line(seg_buffer, VALUE_SCHEMA)
                output_lines.append(agg_line)
                seg_buffer = []
                # advance segment
                try:
                    current_seg = next(seg_iter)
                    seg_id_counter += 1
                except StopIteration:
                    current_seg = None
            continue
        else:
            # Outside any segment: one-to-one
            output_lines.append(process_regular(tokens, data_index))
            data_index += 1
            i_line += 1

    # If file ended mid-segment, flush what we have
    if seg_buffer:
        agg_line = aggregate_segment_to_line(seg_buffer, VALUE_SCHEMA)
        output_lines.append(agg_line)

    with open(output_path, "w") as fout:
        fout.writelines(output_lines)

    print(f"[✓] Wrote: {output_path} | data lines processed: {data_index} | segments: {segments}")

# === MAIN ===
pattern = os.path.join(input_dir, file_pattern)
files = glob.glob(pattern)
print(f"Found {len(files)} file(s) matching '{file_pattern}' in {input_dir}")

for input_file in files:
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_dir, filename)
    rebinning_file(input_file, output_file, rebinning)

# Copy untouched files to the new folder
pattern = os.path.join(input_dir, file_pattern)
files = glob.glob(pattern)
# Copy untouched files to the new folder (only if not already there)
all_files = glob.glob(os.path.join(input_dir, "*"))
for f in all_files:
    if f not in files:  # not processed by rebinning
        target = os.path.join(output_dir, os.path.basename(f))
        if not os.path.exists(target):
            shutil.copy(f, target)
            print(f"[→] Copied unchanged: {os.path.basename(f)}")
        else:
            print(f"[skip] Already exists in output: {os.path.basename(f)}")
