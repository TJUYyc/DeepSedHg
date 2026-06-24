from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = "Figure8_data.xlsx"
OUTPUT_FILE = "Figure8.png"


AGE_ORDER = ["Precambrian", "Paleozoic", "Mesozoic", "Cenozoic"]
COLORS = {
    "Precambrian": "#355C7D",
    "Paleozoic": "#2A9D8F",
    "Mesozoic": "#E9A23B",
    "Cenozoic": "#B65C8A",
}


def setup_style():
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 7.5,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 8,
            "axes.linewidth": 0.75,
            "xtick.major.width": 0.65,
            "ytick.major.width": 0.65,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def scatter_by_group(ax, df, x, y, xlim=None, ylim=None):
    for group in AGE_ORDER:
        sub = df.loc[df["Age group"].eq(group) & df[x].notna() & df[y].notna()]
        if sub.empty:
            continue
        ax.scatter(
            sub[x],
            sub[y],
            s=12,
            c=COLORS[group],
            alpha=0.72,
            linewidths=0,
            label=group,
            rasterized=True,
        )

    ax.axhline(0, color="#9B9B9B", lw=0.65, zorder=0)
    ax.axvline(0, color="#9B9B9B", lw=0.65, zorder=0)
    ax.grid(True, color="#E8E8E8", lw=0.45, zorder=0)
    ax.set_axisbelow(True)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    for spine in ax.spines.values():
        spine.set_color("#575757")
        spine.set_linewidth(0.75)


def add_linear_fit(
    ax,
    df,
    x,
    y,
    reference_text_xy=(0.76, 0.83),
    fit_text_xy=(0.55, 0.12),
    reference_ha="left",
    fit_ha="left",
):
    sub = df.loc[df[x].notna() & df[y].notna(), [x, y]]
    if len(sub) < 2:
        return

    x0, x1 = ax.get_xlim()
    xx = np.linspace(x0, x1, 200)

    ax.plot(xx, xx, ls=":", lw=0.95, color="#8A8A8A", zorder=1.2)
    ax.text(
        *reference_text_xy,
        "1.00",
        transform=ax.transAxes,
        color="#6E6E6E",
        fontsize=7,
        weight="bold",
        ha=reference_ha,
    )

    slope, intercept = np.polyfit(sub[x], sub[y], 1)
    yy = slope * xx + intercept
    r = np.corrcoef(sub[x], sub[y])[0, 1]
    r_squared = r * r
    ax.plot(xx, yy, ls="--", lw=0.95, color="#4F4F4F", zorder=1.5)
    ax.text(
        *fit_text_xy,
        f"slope = {slope:.2f}\n$R^2$ = {r_squared:.2f}",
        transform=ax.transAxes,
        color="#4F4F4F",
        fontsize=7,
        weight="bold",
        linespacing=1.15,
        ha=fit_ha,
    )


def add_panel_label(ax, label):
    ax.text(
        0.03,
        0.96,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        weight="bold",
    )


def main():
    setup_style()
    df = pd.read_excel(DATA_FILE, sheet_name="Plotting_data")
    df["Age group"] = pd.Categorical(df["Age group"], categories=AGE_ORDER, ordered=True)
    for col in ["delta202Hg_permil", "Delta199Hg_permil", "Delta201Hg_permil", "Delta200Hg_permil"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.55), dpi=300)
    axes = axes.ravel()

    scatter_by_group(
        axes[0],
        df,
        "delta202Hg_permil",
        "Delta199Hg_permil",
        xlim=(-5.9, 5.5),
        ylim=(-0.82, 0.82),
    )
    axes[0].set_xlabel(r"$\delta^{202}$Hg (‰)")
    axes[0].set_ylabel(r"$\Delta^{199}$Hg (‰)")
    add_panel_label(axes[0], "(a)")

    scatter_by_group(
        axes[1],
        df,
        "Delta201Hg_permil",
        "Delta199Hg_permil",
        xlim=(-0.76, 0.76),
        ylim=(-0.82, 0.82),
    )
    add_linear_fit(axes[1], df, "Delta201Hg_permil", "Delta199Hg_permil")
    axes[1].set_xlabel(r"$\Delta^{201}$Hg (‰)")
    axes[1].set_ylabel(r"$\Delta^{199}$Hg (‰)")
    add_panel_label(axes[1], "(b)")

    scatter_by_group(
        axes[2],
        df,
        "Delta200Hg_permil",
        "Delta199Hg_permil",
        xlim=(-0.36, 0.31),
        ylim=(-0.82, 0.82),
    )
    add_linear_fit(
        axes[2],
        df,
        "Delta200Hg_permil",
        "Delta199Hg_permil",
        reference_text_xy=(0.985, 0.56),
        fit_text_xy=(0.96, 0.12),
        reference_ha="right",
        fit_ha="right",
    )
    axes[2].set_xlabel(r"$\Delta^{200}$Hg (‰)")
    axes[2].set_ylabel(r"$\Delta^{199}$Hg (‰)")
    add_panel_label(axes[2], "(c)")

    legend_ax = axes[3]
    legend_ax.axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    legend_ax.legend(
        handles,
        labels,
        loc="upper left",
        ncol=1,
        frameon=False,
        handletextpad=0.35,
        labelspacing=0.75,
        borderaxespad=0.0,
    )

    fig.subplots_adjust(left=0.085, right=0.985, top=0.970, bottom=0.085, wspace=0.28, hspace=0.32)
    fig.savefig(OUTPUT_FILE, dpi=600, bbox_inches="tight")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

