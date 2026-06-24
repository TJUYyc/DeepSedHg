import glob
import os
import re

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from matplotlib.lines import Line2D


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "font.size": 7,
    "axes.linewidth": 0.55,
})


DATA_FILE = "Figure5_data.xlsx"
OUTPUT_FILE = "Figure5.png"
MAP_DIR = "Maps"

PERIOD_AGE = {
    "Quaternary": 1,
    "Neogene": 10,
    "Paleogene": 50,
    "Cretaceous": 100,
    "Jurassic": 170,
    "Triassic": 230,
    "Permian": 280,
    "Carboniferous": 330,
    "Devonian": 380,
    "Silurian": 430,
    "Ordovician": 470,
    "Cambrian": 520,
}
PERIOD_ORDER = list(PERIOD_AGE.keys())
PERIOD_SHORT = {
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
ERA = {
    "Quaternary": "Cenozoic",
    "Neogene": "Cenozoic",
    "Paleogene": "Cenozoic",
    "Cretaceous": "Mesozoic",
    "Jurassic": "Mesozoic",
    "Triassic": "Mesozoic",
    "Permian": "Paleozoic",
    "Carboniferous": "Paleozoic",
    "Devonian": "Paleozoic",
    "Silurian": "Paleozoic",
    "Ordovician": "Paleozoic",
    "Cambrian": "Paleozoic",
}
ERA_COLOR = {
    "Cenozoic": "#f1c66d",
    "Mesozoic": "#80b8a8",
    "Paleozoic": "#7fa2ca",
}

CONCENTRATION_COLOR = "#4f9aa4"
ISOTOPE_COLOR = "#b6814c"
ISOTOPE_ONLY_COLOR = "#7c4d8b"
LAND_COLOR = "#e8ebe8"
LAND_EDGE = "#b7bdb9"
GRID_COLOR = "#d5d8d8"

MAPS = glob.glob(os.path.join(MAP_DIR, "**", "*.shp"), recursive=True)


def get_map(period):
    for path in MAPS:
        name = os.path.splitext(os.path.basename(path))[0].lower()
        if period.lower() in name:
            return path

    target = PERIOD_AGE[period]
    best = None
    diff = float("inf")
    for path in MAPS:
        name = os.path.splitext(os.path.basename(path))[0]
        match = re.search(r"(\d+)\s*Ma", name, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if abs(age - target) < diff:
                diff = abs(age - target)
                best = path
    return best


def add_land(ax, period):
    shp = get_map(period)
    if shp is None:
        return
    feature = ShapelyFeature(Reader(shp).geometries(), ccrs.PlateCarree())
    ax.add_feature(feature, facecolor=LAND_COLOR, edgecolor=LAND_EDGE, linewidth=0.18, zorder=1)


def draw_panel_label(ax, period):
    ax.text(
        0.018, 1.038, PERIOD_SHORT[period],
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=7.5,
        fontweight="bold",
        color="#222222",
        bbox=dict(
            boxstyle="square,pad=0.18",
            facecolor=ERA_COLOR[ERA[period]],
            edgecolor="none",
            alpha=0.95,
        ),
        clip_on=False,
        zorder=30,
    )


def draw_point_count(ax, n_points):
    ax.text(
        0.975, 0.035, f"n = {n_points:,}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.2,
        fontweight="normal",
        color="#303030",
        bbox=dict(
            boxstyle="square,pad=0.16",
            facecolor="white",
            edgecolor="none",
            alpha=0.78,
        ),
        clip_on=False,
        zorder=30,
    )


def add_figure_legends(fig):
    type_handles = [
        Line2D(
            [0], [0],
            marker="o",
            linestyle="none",
            markersize=4.7,
            markerfacecolor=CONCENTRATION_COLOR,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg concentration",
        ),
        Line2D(
            [0], [0],
            marker="o",
            linestyle="none",
            markersize=5.1,
            markerfacecolor=ISOTOPE_COLOR,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg concentration + Hg isotope",
        ),
        Line2D(
            [0], [0],
            marker="o",
            linestyle="none",
            markersize=5.4,
            markerfacecolor=ISOTOPE_ONLY_COLOR,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg isotope",
        ),
    ]
    fig.legend(
        handles=type_handles,
        loc="lower left",
        bbox_to_anchor=(0.045, 0.015),
        frameon=False,
        ncol=3,
        handletextpad=0.35,
        columnspacing=1.2,
        borderpad=0.1,
    )

    legend_x = 0.585
    legend_y = 0.040
    for era in ["Cenozoic", "Mesozoic", "Paleozoic"]:
        fig.text(
            legend_x,
            legend_y,
            era,
            fontsize=6.5,
            ha="left",
            va="center",
            bbox=dict(
                boxstyle="square,pad=0.20",
                facecolor=ERA_COLOR[era],
                edgecolor="none",
                alpha=0.95,
            ),
        )
        legend_x += 0.115


def main():
    plotted = pd.read_excel(DATA_FILE, sheet_name="Plotted_sites")
    plotted = plotted.dropna(subset=["Period", "Paleolongitude", "Paleolatitude", "Type_group"]).copy()
    plotted["Paleolongitude"] = pd.to_numeric(plotted["Paleolongitude"], errors="coerce")
    plotted["Paleolatitude"] = pd.to_numeric(plotted["Paleolatitude"], errors="coerce")
    plotted = plotted.dropna(subset=["Paleolongitude", "Paleolatitude"])


    fig = plt.figure(figsize=(183 / 25.4, 142 / 25.4), dpi=300)
    gs = fig.add_gridspec(
        nrows=4,
        ncols=3,
        left=0.045,
        right=0.975,
        top=0.958,
        bottom=0.110,
        wspace=0.060,
        hspace=0.185,
    )

    for i, period in enumerate(PERIOD_ORDER):
        row, col = divmod(i, 3)
        ax = fig.add_subplot(gs[row, col], projection=ccrs.EqualEarth())
        add_land(ax, period)

        sub = plotted[plotted["Period"] == period]
        conc = sub[sub["Type_group"] == "Hg concentration"]
        iso = sub[sub["Type_group"] == "Hg concentration + Hg isotope"]
        iso_only = sub[sub["Type_group"] == "Hg isotope"]

        ax.scatter(
            conc["Paleolongitude"],
            conc["Paleolatitude"],
            s=13,
            marker="o",
            color=CONCENTRATION_COLOR,
            edgecolors="white",
            linewidths=0.25,
            alpha=0.88,
            transform=ccrs.PlateCarree(),
            zorder=8,
        )
        ax.scatter(
            iso["Paleolongitude"],
            iso["Paleolatitude"],
            s=16,
            marker="o",
            color=ISOTOPE_COLOR,
            edgecolors="white",
            linewidths=0.28,
            alpha=0.95,
            transform=ccrs.PlateCarree(),
            zorder=10,
        )
        ax.scatter(
            iso_only["Paleolongitude"],
            iso_only["Paleolatitude"],
            s=22,
            marker="o",
            color=ISOTOPE_ONLY_COLOR,
            edgecolors="white",
            linewidths=0.32,
            alpha=0.98,
            transform=ccrs.PlateCarree(),
            zorder=12,
        )

        ax.set_global()
        if "geo" in ax.spines:
            ax.spines["geo"].set_edgecolor("#777777")
            ax.spines["geo"].set_linewidth(0.45)
        gridlines = ax.gridlines(
            crs=ccrs.PlateCarree(),
            draw_labels=False,
            linewidth=0.25,
            color=GRID_COLOR,
            alpha=0.70,
            linestyle="-",
            zorder=0,
        )
        gridlines.xlocator = mpl.ticker.FixedLocator([-120, -60, 0, 60, 120])
        gridlines.ylocator = mpl.ticker.FixedLocator([-60, -30, 0, 30, 60])
        draw_panel_label(ax, period)
        draw_point_count(ax, len(conc) + len(iso) + len(iso_only))

    add_figure_legends(fig)
    fig.savefig(OUTPUT_FILE, dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
