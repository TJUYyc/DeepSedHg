import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.linewidth": 0.55,
    "xtick.direction": "out",
    "ytick.direction": "out",
})


DATA_FILE = "Figure3_data.xlsx"
OUTPUT_FILE = "Figure3.png"


def main():
    site_df = pd.read_excel(DATA_FILE, sheet_name="Plotted_sites")
    lat_df = pd.read_excel(DATA_FILE, sheet_name="Latitude_distribution")

    site_df["Longitude"] = pd.to_numeric(site_df["Longitude"], errors="coerce")
    site_df["Latitude"] = pd.to_numeric(site_df["Latitude"], errors="coerce")
    site_df = site_df.dropna(subset=["Longitude", "Latitude", "Type_group"])

    concentration_color = "#4f9aa4"
    combined_color = "#b6814c"
    isotope_color = "#7c4d8b"
    bar_fill = "#80b8a8"
    land_color = "#e8ebe8"
    land_edge = "#b7bdb9"
    grid_color = "#d5d8d8"

    fig = plt.figure(figsize=(183 / 25.4, 92 / 25.4), dpi=300)
    gs = GridSpec(
        1, 2,
        width_ratios=[5.25, 1.30],
        left=0.035,
        right=0.985,
        top=0.960,
        bottom=0.205,
        wspace=0.18,
    )

    ax_map = fig.add_subplot(gs[0, 0], projection=ccrs.EqualEarth())
    ax_map.set_global()
    ax_map.add_feature(cfeature.OCEAN, facecolor="white", edgecolor="none", zorder=0)
    ax_map.add_feature(
        cfeature.LAND,
        facecolor=land_color,
        edgecolor=land_edge,
        linewidth=0.22,
        zorder=1,
    )
    ax_map.coastlines(linewidth=0.22, color=land_edge, zorder=2)
    if "geo" in ax_map.spines:
        ax_map.spines["geo"].set_edgecolor("#777777")
        ax_map.spines["geo"].set_linewidth(0.45)

    gridlines = ax_map.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=False,
        linewidth=0.25,
        color=grid_color,
        alpha=0.70,
        linestyle="-",
        zorder=0,
    )
    gridlines.xlocator = mpl.ticker.FixedLocator([-120, -60, 0, 60, 120])
    gridlines.ylocator = mpl.ticker.FixedLocator([-60, -30, 0, 30, 60])

    conc_df = site_df[site_df["Type_group"] == "Hg concentration"]
    combined_df = site_df[site_df["Type_group"] == "Hg concentration + Hg isotope"]
    isotope_df = site_df[site_df["Type_group"] == "Hg isotope"]

    # Draw from most abundant to rarest so rare isotope-only sites remain visible.
    ax_map.scatter(
        conc_df["Longitude"],
        conc_df["Latitude"],
        s=14,
        color=concentration_color,
        edgecolor="white",
        linewidth=0.25,
        alpha=0.86,
        transform=ccrs.PlateCarree(),
        zorder=3,
    )
    ax_map.scatter(
        combined_df["Longitude"],
        combined_df["Latitude"],
        s=18,
        color=combined_color,
        edgecolor="white",
        linewidth=0.30,
        alpha=0.94,
        transform=ccrs.PlateCarree(),
        zorder=4,
    )
    ax_map.scatter(
        isotope_df["Longitude"],
        isotope_df["Latitude"],
        s=24,
        color=isotope_color,
        edgecolor="white",
        linewidth=0.35,
        alpha=0.98,
        transform=ccrs.PlateCarree(),
        zorder=5,
    )
    ax_map.text(
        0.018,
        0.965,
        "(a)",
        transform=ax_map.transAxes,
        fontsize=8,
        fontweight="bold",
        va="top",
    )

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markersize=4.6,
            markerfacecolor=concentration_color,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg concentration",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markersize=5.0,
            markerfacecolor=combined_color,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg concentration + Hg isotope",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="none",
            markersize=5.4,
            markerfacecolor=isotope_color,
            markeredgecolor="white",
            markeredgewidth=0.30,
            label="Hg isotope",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(0.047, 0.192),
        frameon=False,
        handletextpad=0.35,
        borderpad=0.1,
        labelspacing=0.34,
    )

    ax_hist = fig.add_subplot(gs[0, 1])
    ax_hist.barh(
        lat_df["Latitude_bin_center"],
        lat_df["Sampling_sites"],
        height=8.2,
        color=bar_fill,
        edgecolor=concentration_color,
        linewidth=0.55,
    )
    ax_hist.set_ylim(-90, 90)
    ax_hist.set_yticks(range(-80, 81, 20))
    ax_hist.set_ylabel("Latitude (°)", labelpad=3)
    ax_hist.set_xlabel("Sampling sites")
    ax_hist.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
    ax_hist.grid(axis="x", color=grid_color, linestyle="-", linewidth=0.35, alpha=0.70)
    ax_hist.spines["top"].set_visible(False)
    ax_hist.spines["right"].set_visible(False)
    ax_hist.tick_params(axis="both", length=3, width=0.55)
    ax_hist.text(
        0.965,
        0.965,
        "(b)",
        transform=ax_hist.transAxes,
        fontsize=8,
        fontweight="bold",
        ha="right",
        va="top",
    )

    fig.savefig(OUTPUT_FILE, bbox_inches="tight", dpi=600)
    plt.close(fig)


if __name__ == "__main__":
    main()
