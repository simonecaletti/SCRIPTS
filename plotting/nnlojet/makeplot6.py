#!/usr/bin/env python3

from matplotlib.transforms import Bbox
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
parser.add_argument('--add-ratios', type=int, default=0, help="Add arbitrary number of ratio plots as extra axes (default is 0)")
parser.add_argument('--set-ratios', type=ast.literal_eval, help="Enter list (or list of lists for multiple ratios) of files for ratio plots (first one is always the denominator)")
parser.add_argument('--add-logo', action='store_true', help="Add 'NNLOJET' stylized logo on the top-right")
parser.add_argument('--x-logscale', action='store_true', help="Use logarithmic scale on the x-axis")
parser.add_argument('--y-logscale', action='store_true', help="Use logarithmic scale on the y-axis")
parser.add_argument('--legend-ncol', type=int, default=1, help="Number of columns for the legend")
parser.add_argument('--histogram', action='store_true', help="Plot as histogram instead of function-style curve")
parser.add_argument('--rescale', type=float, help="Rescale the x axis by a factor")
parser.add_argument('--normalize', nargs='+', type=float, help="Normalization factor for the top plot (enter a factor per input file)")
parser.add_argument('--config-path', default="config/", type=str, help="Path to the config files")
parser.add_argument('--place-text', type=int, default=3, choices=[1, 2, 3, 4, 5, 6],
                    help="Position of the optional text box: 1=upper-left, 2=upper-central, 3=upper-right (default), 4=lower-left, 5=lower-central, 6=lower-right")
args = parser.parse_args()

filename_list = []
for input in args.input:
    filename_list.append(os.path.join(args.path, input))
outputname = args.output

# --- Extract observable name from input LO (e.g. "mH" from "LO.mH.dat") ---
observable = os.path.basename(filename_list[0]).split('.')[1]
config_file = os.path.join(args.config_path, f"{observable}.config")

# --- Load labels from config file ---
config = {
    "xlabel": r"$m_H$ [GeV]",
    "ylabel_top": "cross section [pb]",
    "ylabel_bottom_list": ["LO/NLO"],
    "process": "$e^+e^-\rightarrow ZH(e^+e^-b\\bar{b})$",
    "legend": ["LO", "NLO", "NNLO"],
    "color": ['green', 'blue', 'red'],
    "line_style": ['-', '--', '-.'],
    "ycut" : None,
    "xmin": None,
    "xmax": None,
    "ymin": None,
    "ymax": None,
    "ymin_ratio": 0.5,
    "ymax_ratio": 1.5,
    "scale": 1.0
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

# --- Helper: enforce first/last ticks while keeping Matplotlib's formatter ---
def add_first_last_xticks(ax, xmin, xmax, is_log=False):
    # Get current ticks
    ticks = list(ax.get_xticks())

    # For log, keep valid positive ticks within range
    if is_log:
        ticks = [t for t in ticks if t > 0 and xmin <= t <= xmax]

    # Ensure first and last are included
    if len(ticks) == 0 or not np.isclose(ticks[0], xmin):
        ticks = [xmin] + ticks
    if not np.isclose(ticks[-1], xmax):
        ticks = ticks + [xmax]

    ax.set_xticks(ticks)
    # Keep the existing formatter (so style matches other ticks)
    ax.xaxis.set_major_formatter(ax.xaxis.get_major_formatter())

# --- Load data ---
df_list = []
for filename in filename_list:
    df_list.append(load_df(filename))

# Sanity check
for i_df in range(1, len(df_list)):
    if not df_list[0]["center"].equals(df_list[i_df]["center"]):
        raise ValueError("Central bin values do not match between (at least) two input files")

x = df_list[0]["center"]
if args.rescale:
    x = x / args.rescale
x_edges = df_list[0]["lower"].tolist()
x_edges.append(df_list[0]["upper"].iloc[-1])
x_edges = np.array(x_edges)
if args.rescale:
    x_edges = x_edges / args.rescale

# Values
val_central = []
val_low = []
val_up = []
for df in df_list:
    # Use user's chosen central/low/up mapping
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
if args.add_ratios > 0:
    height = 4.5
    height_ratios = [5]
    nrows = 1
    ncols = 1
    for iratio in range(args.add_ratios):
        height += 1.5
        height_ratios.append(1.5)
        nrows += 1
    fig = plt.figure(figsize=(7, height), constrained_layout=True)
    gs = fig.add_gridspec(nrows, ncols, height_ratios=height_ratios, hspace=0.02)
    ax1 = fig.add_subplot(gs[0])
    ax2 = [fig.add_subplot(gs[iratio+1], sharex=ax1) for iratio in range(args.add_ratios)]
else:
    fig, ax1 = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    ax2 = None

# Top plot: total cross section
color = config['color']
style = config['line_style']  # fixed key name
while len(config['legend']) < len(val_central):
    config['legend'].append(None)

for i in range(len(val_central)):
    if args.histogram:
        ax1.stairs(val_central[i]/norm[i], x_edges, label=config['legend'][i], color=color[i], linestyle=style[i], linewidth=1)
        low = pd.concat([pd.Series(val_low[i]/norm[i]), pd.Series([0])], ignore_index=True)
        up = pd.concat([pd.Series(val_up[i]/norm[i]), pd.Series([0])], ignore_index=True)
        ax1.fill_between(x_edges, low, up, step='post', color=color[i], alpha=0.15, label=None)
    else:
        ax1.plot(x, val_central[i]/norm[i], color=color[i], linewidth=1, linestyle=style[i], label=config['legend'][i])
        ax1.fill_between(x, val_low[i]/norm[i], val_up[i]/norm[i], color=color[i], alpha=0.15)

ax1.set_ylabel(config["ylabel_top"])
xmin = float(config["xmin"]) if config["xmin"] not in [None, "None"] else x.min()
xmax = float(config["xmax"]) if config["xmax"] not in [None, "None"] else x.max()
ymin = float(config["ymin"]) if config["ymin"] not in [None, "None"] else None
ymax = float(config["ymax"]) if config["ymax"] not in [None, "None"] else None

ax1.set_xlim(xmin, xmax)
if (ymin not in [None, "None"] and ymax not in [None, "None"]):
    ax1.set_ylim(ymin, ymax)
else:
    ax1.set_ylim(bottom=0)

if args.add_ratios > 0 and ax2:
    ax1.tick_params(labelbottom=False)

if args.x_logscale:
    ax1.set_xscale('log')
if args.y_logscale:
    ax1.set_yscale('log')

ax1.legend(loc='upper left', ncol=args.legend_ncol, frameon=False)
ax1.grid(True, alpha=0.5)

# Bottom plot: ratios
if args.add_ratios > 0 and ax2:

    if not args.set_ratios:
        default_ratios = range(1, len(args.input)+1)
        set_ratios = [default_ratios for _ in range(args.add_ratios)]
    else:
        if len(args.set_ratios) != args.add_ratios:
            raise ValueError("set_ratios does not match with the requested number of ratio plots")
        set_ratios = args.set_ratios

    for iratio in range(args.add_ratios):
        val_ratio = []
        val_ratio_low = []
        val_ratio_up = []
        for i in set_ratios[iratio]:
            i_den = set_ratios[iratio][0]

            num_central = np.array(val_central[i-1]) / norm[i-1]
            den_central = np.array(val_central[i_den-1]) / norm[i_den-1]
            num_low = np.array(val_low[i-1]) / norm[i-1]
            num_up = np.array(val_up[i-1]) / norm[i-1]

            mask = den_central != 0

            ratio = np.full_like(num_central, np.nan)
            ratio[mask] = num_central[mask] / den_central[mask]
            val_ratio.append(ratio)

            rlow = np.full_like(num_low, np.nan)
            rlow[mask] = num_low[mask] / den_central[mask]
            val_ratio_low.append(rlow)

            rup = np.full_like(num_up, np.nan)
            rup[mask] = num_up[mask] / den_central[mask]
            val_ratio_up.append(rup)

        for i in range(len(val_ratio)):
            ci = set_ratios[iratio][i] - 1  # color/style index aligned with input
            if args.histogram:
                ax2[iratio].stairs(val_ratio[i], x_edges, label=config['legend'][i], color=color[ci], linestyle=style[ci], linewidth=1)
                ratio_low = pd.concat([pd.Series(val_ratio_low[i]), pd.Series([0])], ignore_index=True)
                ratio_up = pd.concat([pd.Series(val_ratio_up[i]), pd.Series([0])], ignore_index=True)
                ax2[iratio].fill_between(x_edges, ratio_low, ratio_up, step='post', color=color[ci], alpha=0.15, label=None)
            else:
                ax2[iratio].plot(x, val_ratio[i], color=color[ci], linestyle=style[ci])
                ax2[iratio].fill_between(x, val_ratio_low[i], val_ratio_up[i], color=color[ci], alpha=0.15)

        ax2[iratio].set_ylabel(config["ylabel_bottom_list"][iratio])
        if iratio != len(ax2) - 1:
            ax2[iratio].tick_params(labelbottom=False)
            ax2[iratio].set_xlabel("")
            ax1.set_xlabel("")
        if iratio == len(ax2) - 1:
            ax2[iratio].set_xlabel(config["xlabel"])
        ax2[iratio].set_ylim(config["ymin_ratio"], config["ymax_ratio"])
        ax2[iratio].grid(True, alpha=0.5)

    # Ensure first/last ticks appear on the shared x-axis (apply to bottom ratio axis)
    add_first_last_xticks(ax2[-1], xmin, xmax, is_log=args.x_logscale)

else:
    ax1.set_xlabel(config["xlabel"])
    # Ensure first/last ticks appear on x-axis
    add_first_last_xticks(ax1, xmin, xmax, is_log=args.x_logscale)

# Optional text box
textbox = r"$\sqrt{s}=240$ GeV" + "\n" + r"$\mu_R = {}$".format(config["scale"])
if "ycut" in config and config["ycut"] not in [None, "None", ""]:
    textbox += "\n" + r"$y_{{cut}} = {}$".format(config["ycut"])

pos = {
    1: (0.05, 0.95, 'left',  'top'),    # upper-left
    2: (0.5, 0.95, 'center',  'top'),   # upper-central
    3: (0.88, 0.95, 'center', 'top'),   # upper-right
    4: (0.05, 0.05, 'left',  'bottom'), # lower-left
    5: (0.5, 0.05, 'center',  'bottom'),# lower-central
    6: (0.88, 0.05, 'center', 'bottom') # lower-right
}[args.place_text]

ax1.text(pos[0], pos[1], textbox, transform=ax1.transAxes, ha=pos[2], va=pos[3],
         bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
ax1.text(
    0.02, 1.06, config["process"], transform=ax1.transAxes,
    fontsize=14, fontweight='bold', fontstyle='italic', ha='left', va='top',
)

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
