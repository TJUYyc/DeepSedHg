import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from statsmodels.nonparametric.smoothers_lowess import lowess


warnings.filterwarnings("ignore", category=RuntimeWarning, module="statsmodels")

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.linewidth": 0.55,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.unicode_minus": False,
})


BASE_DIR = Path(__file__).resolve().parent

# Put these two Excel files in the same folder as this script.
DATA_FILE = "Figure6_data.xlsx"
GTS_FILE = "Geo_Time.xlsx"

# Output is saved to the same folder.
OUTPUT_FILE = "Figure6.png"

AGE_COL = "Age (Ma)"

PERIOD_LABELS = {
    "Quaternary": "Q",
    "Neogene": "N",
    "Paleogene": "Pg",
    "Cretaceous": "K",
    "Jurassic": "J",
    "Triassic": "T",
    "Permian": "P",
    "Carboniferous": "C",
    "Devonian": "D",
    "Silurian": "S",
    "Ordovician": "O",
    "Cambrian": "Cm",
}

ERA_LABELS = {
    "Neoproterozoic": "NPr",
    "Mesoproterozoic": "MPr",
    "Paleoproterozoic": "PPr",
    "Neoarchean": "NAr",
    "Mesoarchean": "MAr",
    "Paleoarchean": "PAr",
    "Eoarchean": "EAr",
}

PRECAMBRIAN_PERIOD_LABELS = {
    "Ediacaran": "Ed",
    "Cryogenian": "Cr",
    "Tonian": "To",
    "Stenian": "St",
    "Ectasian": "Ec",
    "Calymmian": "Ca",
    "Statherian": "St",
    "Orosirian": "Or",
    "Rhyacian": "Rh",
    "Siderian": "Si",
}

MASS_EXTINCTIONS = [
    ("LOME", 443.8),
    ("LDME", 358.9),
    ("EPME", 251.9),
    ("TJME", 201.4),
    ("KPgE", 66.0),
]

ENVIRONMENTAL_EVENTS = [
    ("T-OAE", 183.0),
    ("OAE1a", 120.0),
    ("OAE1b", 111.0),
    ("OAE2", 94.0),
    ("PETM", 56.0),
]

PRECAMBRIAN_EVENTS = [
    ("GOE", 2450.0),
    ("SG", 717.0),
    ("MG", 635.0),
    ("NOE", 580.0),
]

EVENT_COLOR = "#686868"
EVENT_LABEL_COLOR = "black"
EVENT_LABEL_BBOX = dict(
    boxstyle="square,pad=0.10",
    facecolor="white",
    edgecolor="none",
    alpha=0.82,
)

PRECAMBRIAN_EVENT_LABEL_AGE = {
    "SG": 770.0,
    "MG": 635.0,
    "NOE": 548.0,
}

PHANEROZOIC_EVENT_LABEL_AGE = {
    "KPgE": 72.0,
}


def load_data():
    df = pd.read_excel(DATA_FILE, sheet_name="Plotting_data")
    for col in [AGE_COL, "Hg concentration (ppb)", "d202Hg", "D199Hg", "D200Hg"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def full_ylim(values, pad=0.07):
    vals = pd.Series(values).replace([np.inf, -np.inf], np.nan).dropna()
    if vals.empty:
        return 0, 1
    lo = vals.min()
    hi = vals.max()
    span = hi - lo if hi > lo else 1
    return lo - span * pad, hi + span * pad


def lowess_line(x, y, frac, grid_n=360):
    valid = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[valid], dtype=float)
    y = np.asarray(y[valid], dtype=float)
    if len(x) < 25:
        return None

    xy = pd.DataFrame({"x": x, "y": y}).groupby("x", as_index=False)["y"].median()
    x = xy["x"].to_numpy(dtype=float)
    y = xy["y"].to_numpy(dtype=float)
    if len(x) < 12:
        return None

    order = np.argsort(x)
    x = x[order]
    y = y[order]
    fit = lowess(y, x, frac=frac, return_sorted=True)
    x_grid = np.linspace(np.nanmin(x), np.nanmax(x), grid_n)
    y_grid = np.interp(x_grid, fit[:, 0], fit[:, 1])
    return x_grid, y_grid


def draw_track(ax, x, y, x_span, color, frac, show_ylabel, ylabel, panel_label=None, zero_line=False):
    x_min, x_max = x_span
    mask = np.isfinite(x) & np.isfinite(y) & (x >= x_min) & (x <= x_max)
    xs = x[mask]
    ys = y[mask]

    ax.scatter(xs, ys, s=4.2, color=color, alpha=0.46, linewidth=0, rasterized=True)
    fit = lowess_line(xs, ys, frac=frac)
    if fit is not None:
        ax.plot(fit[0], fit[1], color="black", linewidth=1.05, alpha=0.92)

    ax.set_xlim(x_max, x_min)
    ax.grid(axis="y", color="#d7dada", linewidth=0.35, alpha=0.65)
    if zero_line:
        ax.axhline(0, color="#5d5d5d", linewidth=0.75, linestyle=(0, (3.0, 2.0)), zorder=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=6.4, length=3, width=0.5)

    if show_ylabel:
        ax.set_ylabel(ylabel, fontsize=7)
    else:
        ax.set_ylabel("")
        ax.tick_params(labelleft=False)
        ax.spines["left"].set_visible(False)

    if panel_label:
        ax.text(
            0.012,
            0.88,
            panel_label,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=6.7,
            fontweight="bold",
        )


def add_event_markers(axes_ph, timescale_ax=None):
    line_axes = list(axes_ph)
    if timescale_ax is not None:
        line_axes.append(timescale_ax)

    for ax in line_axes:
        for _, age in MASS_EXTINCTIONS:
            ax.axvline(age, color=EVENT_COLOR, linewidth=0.65, linestyle=(0, (2.2, 2.0)), alpha=0.78, zorder=3)
        for _, age in ENVIRONMENTAL_EVENTS:
            ax.axvline(age, color=EVENT_COLOR, linewidth=0.55, linestyle=(0, (1.2, 2.0)), alpha=0.68, zorder=2.8)

    top_ax = axes_ph[0]
    for label, age in MASS_EXTINCTIONS:
        label_age = PHANEROZOIC_EVENT_LABEL_AGE.get(label, max(age - 6.0, 0))
        top_ax.text(
            label_age,
            0.985,
            label,
            transform=top_ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=6.2,
            fontweight="semibold",
            color=EVENT_LABEL_COLOR,
            rotation=90,
            bbox=EVENT_LABEL_BBOX,
            clip_on=False,
        )
    for i, (label, age) in enumerate(ENVIRONMENTAL_EVENTS):
        label_age = max(age - 5.0, 0)
        top_ax.text(
            label_age,
            0.985,
            label,
            transform=top_ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=6.0,
            fontweight="semibold",
            color=EVENT_LABEL_COLOR,
            rotation=90,
            bbox=EVENT_LABEL_BBOX,
            clip_on=False,
        )


def add_precambrian_event_markers(axes_pr, timescale_ax=None):
    line_axes = list(axes_pr)
    if timescale_ax is not None:
        line_axes.append(timescale_ax)

    for ax in line_axes:
        for _, age in PRECAMBRIAN_EVENTS:
            ax.axvline(age, color=EVENT_COLOR, linewidth=0.60, linestyle=(0, (1.5, 2.0)), alpha=0.72, zorder=3)

    top_ax = axes_pr[0]
    for label, age in PRECAMBRIAN_EVENTS:
        label_age = PRECAMBRIAN_EVENT_LABEL_AGE.get(label, max(age - 35.0, 542.0))
        top_ax.text(
            label_age,
            0.985,
            label,
            transform=top_ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=6.2,
            fontweight="semibold",
            color=EVENT_LABEL_COLOR,
            rotation=90,
            bbox=EVENT_LABEL_BBOX,
            clip_on=False,
        )


def plot_precambrian_timescale(ax):
    periods = pd.read_excel(GTS_FILE, sheet_name="Epoch")
    eras = pd.read_excel(GTS_FILE, sheet_name="Era")
    periods = periods[(periods["ELowerBoundary"] >= 538.8) & (periods["EUpperBoundary"] <= 3000)].copy()
    eras = eras[(eras["PLowerBoundary"] >= 538.8) & (eras["PUpperBoundary"] <= 3000)].copy()

    for _, row in periods.iterrows():
        left = row["EUpperBoundary"]
        width = row["ELowerBoundary"] - row["EUpperBoundary"]
        ax.add_patch(
            patches.Rectangle(
                (left, 0.23),
                width,
                0.23,
                linewidth=0.18,
                edgecolor="white",
                facecolor=row["Color"],
            )
        )
        label = PRECAMBRIAN_PERIOD_LABELS.get(str(row["Epoch"]), "")
        if label and width > 70:
            ax.text(left + width / 2, 0.345, label, ha="center", va="center", fontsize=4.7)

    for _, row in eras.iterrows():
        left = row["PUpperBoundary"]
        width = row["PLowerBoundary"] - row["PUpperBoundary"]
        ax.add_patch(
            patches.Rectangle(
                (left, 0.00),
                width,
                0.23,
                linewidth=0.28,
                edgecolor="white",
                facecolor=row["Color"],
            )
        )
        label = ERA_LABELS.get(str(row["Period"]), "")
        if label:
            ax.text(left + width / 2, 0.115, label, ha="center", va="center", fontsize=5.1)

    ax.set_xlim(3000, 538.8)
    ax.set_ylim(0, 0.46)
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelsize=6.3, length=2.5, width=0.45, pad=1)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.45)


def plot_phanerozoic_timescale(ax):
    periods = pd.read_excel(GTS_FILE, sheet_name="Period")
    epochs = pd.read_excel(GTS_FILE, sheet_name="Epoch")
    periods = periods[periods["Period"].isin(PERIOD_LABELS)].copy()
    epochs = epochs[(epochs["EUpperBoundary"] >= 0) & (epochs["ELowerBoundary"] <= 538.8)].copy()

    for _, row in epochs.iterrows():
        left = row["EUpperBoundary"]
        width = row["ELowerBoundary"] - row["EUpperBoundary"]
        ax.add_patch(
            patches.Rectangle(
                (left, 0.23),
                width,
                0.23,
                linewidth=0.18,
                edgecolor="white",
                facecolor=row["Color"],
            )
        )

    for _, row in periods.iterrows():
        left = row["PUpperBoundary"]
        width = row["PLowerBoundary"] - row["PUpperBoundary"]
        ax.add_patch(
            patches.Rectangle(
                (left, 0.00),
                width,
                0.23,
                linewidth=0.28,
                edgecolor="white",
                facecolor=row["Color"],
            )
        )
        ax.text(left + width / 2, 0.115, PERIOD_LABELS[str(row["Period"])], ha="center", va="center", fontsize=5.1)

    ax.set_xlim(545, 0)
    ax.set_ylim(0, 0.46)
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelsize=6.3, length=2.5, width=0.45, pad=1)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.45)


def main():
    df = load_data()
    variables = [
        ("Hg", "Hg concentration (ppb)", r"$\log_{10}$ Hg concentration (ppb)", "#4f9aa4", True, 0.11, 0.012),
        ("d202", "d202Hg", r"$\delta^{202}$Hg (‰)", "#c77855", False, 0.12, 0.021),
        ("D199", "D199Hg", r"$\Delta^{199}$Hg (‰)", "#8f2632", False, 0.12, 0.021),
        ("D200", "D200Hg", r"$\Delta^{200}$Hg (‰)", "#3f6f9f", False, 0.12, 0.021),
    ]

    prepared = []
    for _, col, ylabel, color, log_y, frac_pr, frac_ph in variables:
        data = df[[AGE_COL, col]].dropna().copy()
        if log_y:
            data = data[data[col] > 0]
            data[col] = np.log10(data[col])
        x = data[AGE_COL].to_numpy(dtype=float)
        y = data[col].to_numpy(dtype=float)
        prepared.append((x, y, ylabel, color, frac_pr, frac_ph))

    fig = plt.figure(figsize=(183 / 25.4, 142 / 25.4), dpi=300)
    gs = GridSpec(
        5,
        2,
        height_ratios=[1, 1, 1, 1, 0.22],
        width_ratios=[0.72, 1.38],
        left=0.082,
        right=0.988,
        top=0.945,
        bottom=0.075,
        hspace=0.045,
        wspace=0.035,
    )

    axes = []
    for r, (x, y, ylabel, color, frac_pr, frac_ph) in enumerate(prepared):
        ax_pr = fig.add_subplot(gs[r, 0])
        ax_ph = fig.add_subplot(gs[r, 1], sharey=ax_pr)
        ylim = full_ylim(y)

        draw_track(
            ax_pr,
            x,
            y,
            (538.8, 3000),
            color,
            frac_pr,
            show_ylabel=True,
            ylabel=ylabel,
            panel_label=f"({chr(97 + r)})",
            zero_line=r > 0,
        )
        draw_track(
            ax_ph,
            x,
            y,
            (0, 545),
            color,
            frac_ph,
            show_ylabel=False,
            ylabel="",
            zero_line=r > 0,
        )
        ax_pr.set_ylim(*ylim)
        ax_ph.set_ylim(*ylim)
        ax_pr.tick_params(labelbottom=False, bottom=False)
        ax_ph.tick_params(labelbottom=False, bottom=False)
        axes.append((ax_pr, ax_ph))

    axes[0][0].set_title("Precambrian", fontsize=8, fontweight="bold", pad=3)
    axes[0][1].set_title("Phanerozoic", fontsize=8, fontweight="bold", pad=3)

    ax_pr_ts = fig.add_subplot(gs[4, 0], sharex=axes[-1][0])
    ax_ph_ts = fig.add_subplot(gs[4, 1], sharex=axes[-1][1])
    plot_precambrian_timescale(ax_pr_ts)
    plot_phanerozoic_timescale(ax_ph_ts)
    add_precambrian_event_markers([ax_pr for ax_pr, _ in axes], timescale_ax=ax_pr_ts)
    add_event_markers([ax_ph for _, ax_ph in axes], timescale_ax=ax_ph_ts)

    fig.text(0.535, 0.034, "Age (Ma)", ha="center", va="center", fontsize=7)
    fig.savefig(OUTPUT_FILE, dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
