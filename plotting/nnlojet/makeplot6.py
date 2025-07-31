#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import argparse
import os
import ast
import warnings

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser(description="Plot LO, NLO and NNLO differential cross sections from NNLOJET")
parser.add_argument('--path', default="combined/Final", help="Input common path (usually combined/Final)")
parser.add_argument('--input', nargs='+', required=True, help="List of input filenames (e.g. first LO, second NLO, third NNLO)")
parser.add_argument('--output', default="output.pdf", help="Output filename")
parser.add_argument('--enable-ratio', default=False, action='store_true', help="Enable second axes with ratio plot")
parser.add_argument('--denominator', help="Choose denominator for ratio plot among the input files (default is last file)")
parser.add_argument('--add-logo', action='store_true', help="Add 'NNLOJET' stylized logo on the top-right")
parser.add_argument('--logscale', action='store_true', help="Use logarithmic scale on the x-axis")
parser.add_argument('--histogram', action='store_true', help="Plot as histogram instead of function-style curve")
parser.add_argument('--rescale', type=float, help="Rescale the x axis by a factor")
parser.add_argument('--normalize', nargs='+', type=float, help="Normalization factor for the top plot (enter a factor per input file)")
parser.add_argument('--place-text', type=int, default=3, choices=[1, 2, 3, 4, 5, 6],
                    help="Position of the optional text box: 1=upper-left, 2=upper-central, 3=upper-right (default), 4=lower-left, 5=lower-central, 6=lower-right")
args = parser.parse_args()

filename_list = []
for input in args.input:
    filename_list.append(os.path.join(args.path, input))
outputname = args.output

# --- Extract observable name from input LO (e.g. "mH" from "LO.mH.dat") ---
observable = os.path.basename(filename_list[0]).split('.')[1]
config_file = os.path.join("config/", f"{observable}.config")

# --- Load labels from config file ---
config = {
    "xlabel": r"$m_H$ [GeV]",
    "ylabel_top": "cross section [pb]",
    "ylabel_bottom": "LO/NLO",
    "process": "$e^+e^-\rightarrow ZH(e^+e^-b\bar{b})$",
    "legend": ["LO", "NLO", "NNLO"],
    "color": ['green', 'blue', 'red'],
    "ycut" : 0.01,
    "xmin": None,
    "xmax": None,
    "ymin": None,
    "ymax": None,
    "ymin_ratio": 0.5,
    "ymax_ratio": 1.5
}

if os.path.isfile(config_file):
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if "=" in line:
                key, val = line.strip().split("=", 1)
                key = key.strip()
                val = val.strip()

                try:
                    config[key] = ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    config[key] = val
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
        "tot_scale03", "tot_scale03_Err",
        "tot_scale04", "tot_scale04_Err"
    ]
    return df

# --- Load data ---
df_list = []
for filename in filename_list:
    df_list.append(load_df(filename))

# Sanity check
for i_df in range(1,len(df_list)):
    if not df_list[0]["center"].equals(df_list[i_df]["center"]):
        raise ValueError("Central bin values do not match between (at least) two input files")

x = df_list[0]["center"]
if args.rescale: x = x / args.rescale
x_edges = df_list[0]["lower"].tolist()
x_edges.append(df_list[0]["upper"].iloc[-1])
x_edges = np.array(x_edges)
if args.rescale: x_edges = x_edges / args.rescale


# LO
val_central = []
val_low = []
val_up = []
for df in df_list:
    val_central.append(df["tot_scale01"])
    val_low.append(df[["tot_scale02", "tot_scale03"]].min(axis=1))
    val_up.append(df[["tot_scale02", "tot_scale03"]].max(axis=1))

# --- Normalization ---
norm = []
for i in range(len(val_central)):
    if args.normalize:
        if len(args.normalize) != len(val_central):
            raise ValueError("Normalization factors must match the number of input files (even if the same normalization factor)")
        norm.append(args.normalize[i])
    else:
        norm.append(1)

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
color = config['color']
for i in range(len(val_central)):
    if args.histogram:
        # Step-style histogram for central values
        ax1.stairs(val_central[i]/norm[i], x_edges, label=config['legend'][i], color=color[i], linewidth=2)

        # Shaded uncertainty band with step-like fill
        low = pd.concat([pd.Series(val_low[i]/norm[i]), pd.Series([0])], ignore_index=True)
        up = pd.concat([pd.Series(val_up[i]/norm[i]), pd.Series([0])], ignore_index=True)
        ax1.fill_between(
            x_edges, low, up,
            step='post', color=color[i], alpha=0.3, label=None
        )

    else:
        ax1.plot(x, val_central[i]/norm[i], color=color[i], linewidth=2, label=config['legend'][i])
        ax1.fill_between(x, val_low[i]/norm[i], val_up[i]/norm[i], color=color[i], alpha=0.3)

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

if args.logscale:
    ax1.set_xscale('log')

ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.5)

# Bottom plot: ratio
if args.enable_ratio and ax2:
    val_ratio= []
    val_ratio_low = []
    val_ratio_up = []
    for i in range(len(val_central)):
        if args.denominator and args.denominator not in args.input:
            raise ValueError("Denominator for ratio plot not among the input files")
        else:
            i_den = -1
            if args.denominator:
                i_den = args.input.index(args.denominator)

                # Prepare numerator and denominator arrays with normalization
                num_central = np.array(val_central[i]) / norm[i]
                den_central = np.array(val_central[i_den]) / norm[i_den]
                num_low = np.array(val_low[i]) / norm[i]
                num_up = np.array(val_up[i]) / norm[i]

                # Apply mask to avoid division by zero
                mask = den_central != 0

                ratio = np.full_like(num_central, np.nan)
                ratio[mask] = num_central[mask] / den_central[mask]
                val_ratio.append(ratio)

                ratio_low = np.full_like(num_low, np.nan)
                ratio_low[mask] = num_low[mask] / den_central[mask]
                val_ratio_low.append(ratio_low)

                ratio_up = np.full_like(num_up, np.nan)
                ratio_up[mask] = num_up[mask] / den_central[mask]
                val_ratio_up.append(ratio_up)

    for i in range(len(val_ratio)):
        if args.histogram:
            ax2.stairs(val_ratio[i], x_edges, label=config['legend'][i], color=color[i], linewidth=2)
            ratio_low = pd.concat([pd.Series(val_ratio_low[i]), pd.Series([0])], ignore_index=True)
            ratio_up = pd.concat([pd.Series(val_ratio_up[i]), pd.Series([0])], ignore_index=True)
            ax2.fill_between(
                x_edges, ratio_low, ratio_up,
                step='post', color=color[i], alpha=0.3, label=None
            )
        else:
            ax2.plot(x, val_ratio[i], color=color[i])
            ax2.fill_between(x, val_ratio_low[i], val_ratio_up[i], color=color[i], alpha=0.3)

    ax2.set_ylabel(config["ylabel_bottom"])
    ax2.set_xlabel(config["xlabel"])
    ax2.set_ylim(config["ymin_ratio"], config["ymax_ratio"])
    ax2.grid(True, alpha=0.5)
else:
    ax1.set_xlabel(config["xlabel"])

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
