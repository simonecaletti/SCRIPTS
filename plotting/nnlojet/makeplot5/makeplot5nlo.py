#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import warnings

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser(description="Plot LO and NLO differential cross sections and their ratio (LO/NLO)")
parser.add_argument('--path', default="combined/Final", help="Input common path (usually combined/Final)")
parser.add_argument('--input', nargs=2, required=True, help="Input filenames: first LO, second NLO")
parser.add_argument('--output', default="output_lo_nlo_ratio.pdf", help="Output filename")
parser.add_argument('--add-logo', action='store_true', help="Add 'NNLOJET' stylized logo on the top-right")
parser.add_argument('--logscale', action='store_true', help="Use logarithmic scale on the x-axis")
parser.add_argument('--histogram', action='store_true', help="Plot as histogram instead of function-style curve")
parser.add_argument('--place-text', type=int, default=3, choices=[1, 2, 3, 4, 5, 6],
                    help="Position of the optional text box: 1=upper-left, 2=upper-central, 3=upper-right (default), 4=lower-left, 5=lower-central, 6=lower-right")
args = parser.parse_args()

filename_lo = os.path.join(args.path, args.input[0])
filename_nlo = os.path.join(args.path, args.input[1])
outputname = "plots/" + args.output

# --- Extract observable name from input LO ---
observable = os.path.basename(filename_lo).split('.')[1]
config_file = os.path.join("config/", f"{observable}.config")

# --- Load config ---
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

if not df_lo["center"].equals(df_nlo["center"]):
    raise ValueError("Bin centers do not match between LO and NLO files")

x = df_lo["center"]

# LO
x_edges = df_lo["lower"].tolist()
x_edges.append(df_lo["upper"].iloc[-1])
x_edges = np.array(x_edges)
lo_central = df_lo["tot_scale01"]
lo_low = df_lo[["tot_scale02", "tot_scale03"]].min(axis=1)
lo_up = df_lo[["tot_scale02", "tot_scale03"]].max(axis=1)

# NLO
nlo_central = df_nlo["tot_scale01"]
nlo_low = df_nlo[["tot_scale02", "tot_scale03"]].min(axis=1)
nlo_up = df_nlo[["tot_scale02", "tot_scale03"]].max(axis=1)

# --- Set up figure with ratio subplot ---
fig = plt.figure(figsize=(8, 6), constrained_layout=True)
gs = fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.05)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1], sharex=ax1)

# --- Top plot: cross sections ---
if args.histogram:
    # Step-style histogram for central values
    ax1.stairs(lo_central, x_edges, label="LO", color='green', linewidth=2)
    ax1.stairs(nlo_central, x_edges, label="NLO", color='blue', linewidth=2)

    # Shaded uncertainty band with step-like fill
    lo_low = pd.concat([lo_low, pd.Series([0])], ignore_index=True)
    lo_up = pd.concat([lo_up, pd.Series([0])], ignore_index=True)
    ax1.fill_between(
        x_edges, lo_low, lo_up,
        step='post', color='green', alpha=0.3, label=None
    )
    nlo_low = pd.concat([nlo_low, pd.Series([0])], ignore_index=True)
    nlo_up = pd.concat([nlo_up, pd.Series([0])], ignore_index=True)
    ax1.fill_between(
        x_edges, nlo_low, nlo_up,
        step='post', color='blue', alpha=0.3, label=None
    )
else:
    ax1.plot(x, lo_central, 'g-', linewidth=2, label='LO')
    ax1.fill_between(x, lo_low, lo_up, color='green', alpha=0.3)

    ax1.plot(x, nlo_central, 'b-', linewidth=2, label='NLO')
    ax1.fill_between(x, nlo_low, nlo_up, color='blue', alpha=0.3)

ax1.set_ylabel(config["ylabel_top"])
xmin = float(config["xmin"]) if config["xmin"] not in [None, "None"] else x.min()
xmax = float(config["xmax"]) if config["xmax"] not in [None, "None"] else x.max()
ymin = float(config["ymin"]) if config["ymin"] not in [None, "None"] else None
ymax = float(config["ymax"]) if config["ymax"] not in [None, "None"] else None

ax1.set_xlim(xmin, xmax)
if ymin is not None and ymax is not None:
    ax1.set_ylim(ymin, ymax)
ax1.set_ylim(bottom=0)

if args.logscale:
    ax1.set_xscale("log")

ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.5)

# --- Bottom plot: ratio LO / NLO ---
ratio = lo_central / nlo_central
ax2.plot(x, ratio, 'g-')
ax2.axhline(1.0, color='blue', linestyle='-', linewidth=1.5, alpha=0.5)

ax2.set_ylabel(config["ylabel_bottom"])
ax2.set_xlabel(config["xlabel"])
ax2.set_ylim(0.7, 1.3)
ax2.grid(True, alpha=0.5)

# Optional text box
textbox = (
    config["process"] + "\n"
    + r"$\sqrt{s}=240$ GeV" + "\n"
    + r"$\alpha_S(m_Z) = 0.118$" + "\n"
    + r"Durham $y_{{cut}}={}$".format(config["ycut"])
)
pos = {
    1: (0.05, 0.95, 'left',  'top'),    # upper-left
    2: (0.5, 0.95, 'center',  'top'),  # upper-central
    3: (0.95, 0.95, 'right', 'top'),    # upper-right
    4: (0.05, 0.05, 'left',  'bottom'), # lower-left
    5: (0.5, 0.05, 'center',  'bottom'), # lower-central
    6: (0.95, 0.05, 'right', 'bottom')  # lower-right
}[args.place_text]
ax1.text(pos[0], pos[1], textbox, transform=ax1.transAxes, ha=pos[2], va=pos[3])

# --- Optional logo ---
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

# --- Save plot ---
plt.savefig(outputname)
