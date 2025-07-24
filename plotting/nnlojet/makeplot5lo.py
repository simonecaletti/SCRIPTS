#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import warnings

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser(description="Plot LO differential cross section from NNLOJET")
parser.add_argument('--path', default="combined/Final", help="Input common path (usually combined/Final)")
parser.add_argument('--input', required=True, help="Input filename (LO only)")
parser.add_argument('--output', default="output_lo.pdf", help="Output filename")
parser.add_argument('--add-logo', action='store_true', help="Add 'NNLOJET' stylized logo on the top-right")
args = parser.parse_args()

filename_lo = os.path.join(args.path, args.input)
outputname = "plots/" + args.output

# --- Extract observable name from input LO (e.g. "mH" from "LO.mH.dat") ---
observable = os.path.basename(filename_lo).split('.')[1]
config_file = os.path.join("config/", f"{observable}.config")

# --- Load labels from config file ---
config = {
    "xlabel": r"$m_H$ [GeV]",
    "ylabel_top": "cross section [pb]",
    "process": "$e^+e^-\rightarrow ZH(e^+e^-b\bar{b})$",
    "xmin": None,
    "xmax": None,
    "ymin": None,
    "ymax": None
}

if os.path.isfile(config_file):
    with open(config_file, 'r') as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("=", 1)
                config[key.strip()] = val.strip()
else:
    warnings.warn(f"Config file {config_file} not found. Using default labels.")

# --- Plot settings ---
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 14
})

def load_df(filename):
    df = pd.read_csv(filename, sep=r"\s+", comment="#", header=None)
    df.columns = [
        "lower", "center", "upper",
        "tot_scale01", "tot_scale01_Err",
        "tot_scale02", "tot_scale02_Err",
        "tot_scale03", "tot_scale03_Err"
    ]
    return df

# --- Load LO data ---
df_lo = load_df(filename_lo)
x = df_lo["center"]
lo_central = df_lo["tot_scale01"]
lo_low = df_lo[["tot_scale02", "tot_scale03"]].min(axis=1)
lo_up = df_lo[["tot_scale02", "tot_scale03"]].max(axis=1)

# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

ax.plot(x, lo_central, 'g-', linewidth=2, label='LO')
ax.fill_between(x, lo_low, lo_up, color='green', alpha=0.3)

ax.set_ylabel(config["ylabel_top"])
xmin = float(config["xmin"]) if config["xmin"] not in [None, "None"] else x.min()
xmax = float(config["xmax"]) if config["xmax"] not in [None, "None"] else x.max()
ymin = float(config["ymin"]) if config["ymin"] not in [None, "None"] else None
ymax = float(config["ymax"]) if config["ymax"] not in [None, "None"] else None

ax.set_xlim(xmin, xmax)
if ymin is not None and ymax is not None:
    ax.set_ylim(ymin, ymax)
ax.set_ylim(bottom=0)
ax.set_xlabel(config["xlabel"])
ax.legend(loc='upper left')
ax.grid(True, alpha=0.5)

# Optional text box
ax.text(0.85, 0.92, config["process"] + "\n" + r"$\sqrt{s}=240$ GeV" + "\n" + r"$\alpha_S(m_Z) = 0.118$",
        transform=ax.transAxes, ha='center', va='top')

# Optional logo
if args.add_logo:
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial"],
        "font.size": 14
    })
    ax.text(
        0.98, 1.08, "NNLOJET", transform=ax.transAxes,
        fontsize=16, fontweight='bold', fontstyle='italic', ha='right', va='top'
    )

# Save figure
plt.savefig(outputname)
