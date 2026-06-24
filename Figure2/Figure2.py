import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.linewidth": 0.55,
    "xtick.direction": "out",
    "ytick.direction": "out",
})


DATA_FILE = "Figure2_data.xlsx"
OUTPUT_FILE = "Figure2.png"


def comma_fmt(x, _):
    return f"{int(x):,}"


def main():
    df = pd.read_excel(DATA_FILE, sheet_name="Annual_summary")
    df = df.sort_values("Year").copy()

    year = df["Year"]
    paper_annual = df["Annual_publications"]
    paper_cumu = df["Cumulative_publications"]
    data_annual = df["Annual_data_points"]
    data_cumu = df["Cumulative_data_points"]

    annual_pub_color = "#8a6f4d"
    cumu_pub_color = "#e0bf78"
    annual_data_color = "#4f9aa4"
    cumu_data_color = "#80b8a8"
    grid_color = "#d5d8d8"

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(183 / 25.4, 118 / 25.4),
        sharex=True,
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.20},
        dpi=300,
    )

    panels = [
        (
            axes[0],
            paper_annual,
            paper_cumu,
            annual_pub_color,
            cumu_pub_color,
            "Annual publications",
            "Cumulative publications",
            "(a)",
        ),
        (
            axes[1],
            data_annual,
            data_cumu,
            annual_data_color,
            cumu_data_color,
            "Annual data points",
            "Cumulative data points",
            "(b)",
        ),
    ]

    for ax, annual, cumulative, annual_color, cumu_color, ylabel, ylabel2, label in panels:
        ax2 = ax.twinx()
        ax2.fill_between(year, cumulative, color=cumu_color, alpha=0.24, linewidth=0, zorder=1)
        ax2.plot(year, cumulative, color=cumu_color, linewidth=1.3, zorder=2)

        ax.vlines(year, 0, annual, color=annual_color, alpha=0.82, linewidth=1.4, zorder=3)
        ax.scatter(
            year,
            annual,
            s=22,
            color=annual_color,
            edgecolor="white",
            linewidth=0.45,
            zorder=4,
        )

        ax.set_ylabel(ylabel)
        ax2.set_ylabel(ylabel2)
        ax.text(0.012, 0.925, label, transform=ax.transAxes, fontsize=8, fontweight="bold")

        ax.grid(axis="y", color=grid_color, linestyle="-", linewidth=0.35, alpha=0.70)
        ax.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)
        ax.yaxis.set_major_formatter(FuncFormatter(comma_fmt))
        ax2.yaxis.set_major_formatter(FuncFormatter(comma_fmt))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
        ax2.yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        ax.tick_params(axis="both", length=3, width=0.55)
        ax2.tick_params(axis="y", length=3, width=0.55)

    axes[1].set_xlabel("Publication year")
    axes[1].set_xlim(int(year.min()) - 0.7, int(year.max()) + 0.7)
    axes[1].set_xticks(list(range(int(year.min()), int(year.max()) + 1)))
    axes[1].tick_params(axis="x", rotation=45)

    fig.savefig(OUTPUT_FILE, bbox_inches="tight", dpi=600)
    plt.close(fig)


if __name__ == "__main__":
    main()
