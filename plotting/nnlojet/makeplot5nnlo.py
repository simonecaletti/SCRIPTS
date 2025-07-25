#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import argparse
import os
import warnings

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser(description="Plot LO, NLO and NNLO differential cross sections from NNLOJET")
parser.add_argument('--path', default="combined/Final", help="Input common path (usually combined/Final)")
parser.add_argument('--input', nargs=3, required=True, help="Input filenames: first LO, second NLO, third NNLO")
parser.add_argument('--output', default="output.pdf", help="Output filename")
parser.add_argument('--enable-ratio', default=False, action='store_true', help="Enable second axes with ratio plot")
parser.add_argument('--denominator', choices=["LO", "NLO", "NNLO"], default="NNLO",
                    help="Choose denominator for ratio plot (default: NNLO)")
parser.add_argument('--add-logo', action='store_true', help="Add 'NNLOJET' stylized logo on the top-right")
args = parser.parse_args()

filename_lo = os.path.join(args.path, args.input[0])
filename_nlo = os.path.join(args.path, args.input[1])
filename_nnlo = os.path.join(args.path, args.input[2])
outputname = "plots/" + args.output

# --- Extract observable name from input LO (e.g. "mH" from "LO.mH.dat") ---
observable = os.path.basename(filename_lo).split('.')[1]
config_file = os.path.join("config/", f"{observable}.config")

# --- Load labels from config file ---
config = {
    "xlabel": r"$m_H$ [GeV]",
    "ylabel_top": "cross section [pb]",
    "ylabel_bottom": "LO/NLO",
    "process": "$e^+e^-\rightarrow ZH(e^+e^-b\bar{b})$",
    "ycut" : 0.01,
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

# --- Load data ---
df_lo = load_df(filename_lo)
df_nlo = load_df(filename_nlo)
df_nnlo = load_df(filename_nnlo)

# Sanity check
if not df_lo["center"].equals(df_nlo["center"]):
    raise ValueError("Central bin values do not match between LO and NLO files")
# Sanity check
if not df_lo["center"].equals(df_nnlo["center"]):
    raise ValueError("Central bin values do not match between LO and NNLO files")

x = df_lo["center"]

# LO
lo_central = df_lo["tot_scale01"]
lo_low = df_lo[["tot_scale02", "tot_scale03"]].min(axis=1)
lo_up = df_lo[["tot_scale02", "tot_scale03"]].max(axis=1)

# NLO
nlo_central = df_nlo["tot_scale01"]
nlo_low = df_nlo[["tot_scale02", "tot_scale03"]].min(axis=1)
nlo_up = df_nlo[["tot_scale02", "tot_scale03"]].max(axis=1)

# NNLO
nnlo_central = df_nnlo["tot_scale01"]
nnlo_low = df_nnlo[["tot_scale02", "tot_scale03"]].min(axis=1)
nnlo_up = df_nnlo[["tot_scale02", "tot_scale03"]].max(axis=1)

# --- Plotting ---
if args.enable_ratio:
    fig = plt.figure(figsize=(8, 6), constrained_layout=True)
    gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.05)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
else:
    fig, ax1 = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    ax2 = None

# Top plot: total cross section
ax1.plot(x, lo_central, 'g-', linewidth=2, label='LO')
ax1.fill_between(x, lo_low, lo_up, color='green', alpha=0.3)

ax1.plot(x, nlo_central, 'b-', linewidth=2, label='NLO')
ax1.fill_between(x, nlo_low, nlo_up, color='blue', alpha=0.3)

ax1.plot(x, nnlo_central, 'r-', linewidth=2, label='NNLO')
ax1.fill_between(x, nnlo_low, nnlo_up, color='red', alpha=0.3)

ax1.set_ylabel(config["ylabel_top"])
xmin = float(config["xmin"]) if config["xmin"] not in [None, "None"] else x.min()
xmax = float(config["xmax"]) if config["xmax"] not in [None, "None"] else x.max()
ymin = float(config["ymin"]) if config["ymin"] not in [None, "None"] else None
ymax = float(config["ymax"]) if config["ymax"] not in [None, "None"] else None
#print(xmin, xmax)
ax1.set_xlim(xmin, xmax)
if (ymin not in [None, "None"] and ymax not in [None, "None"]):
    ax1.set_ylim(ymin, ymax)
ax1.set_ylim(bottom=0)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.5)

# Bottom plot: ratio
if args.enable_ratio and ax2:
    if args.denominator == "NNLO":
        ratio1 = lo_central / nnlo_central
        ratio2 = nlo_central / nnlo_central
        #label = "LO / NLO"
    else:
        ratio1 = nlo_central / lo_central
        ratio2 = nnlo_central / lo_central
        #label = "NLO / LO"
    ax2.plot(x, ratio1, 'g-')
    ax2.plot(x, ratio2, 'b-')
    ax2.axhline(1.0, color='red', linestyle='-', linewidth=1.5, alpha=0.5)
    ax2.set_ylabel(config["ylabel_bottom"])
    ax2.set_xlabel(config["xlabel"])
    ax2.set_ylim(0.7, 1.1)
    ax2.grid(True, alpha=0.5)
else:
    ax1.set_xlabel(config["xlabel"])

# Optional text box
ax1.text(0.85, 0.92, config["process"] + "\n" + r"$\sqrt{s}=240$ GeV" + "\n" + r"$\alpha_S(m_Z) = 0.118$"+ "\n" + r"Durham $y_{cut}={}$".format(config["ycut"]),
             transform=ax1.transAxes, ha='center', va='top')

if args.add_logo:
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial"],
        "font.size": 14
    })
    ax1.text(
        0.98, 1.08, "NNLOJET", transform=ax1.transAxes,
        fontsize=16, fontweight='bold', fontstyle='italic', ha='right', va='top'
    )

# Save figure
plt.savefig(outputname)
