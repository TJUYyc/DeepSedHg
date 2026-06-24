import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec


mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "font.size": 7,
    "axes.linewidth": 0.55,
    "xtick.direction": "out",
    "ytick.direction": "out",
})


DATA_FILE = "Figure4_data.xlsx"
OUTPUT_FILE = "Figure4.png"
ERA_LABELS = ["Cenozoic", "Mesozoic", "Paleozoic", "Precambrian"]


def lat_label(center):
    if center > 0:
        return f"{int(center)}°N"
    if center < 0:
        return f"{abs(int(center))}°S"
    return "0°"


def add_era_ticks(ax):
    ax.set_xticks(np.arange(len(ERA_LABELS)))
    ax.set_xticklabels(ERA_LABELS, rotation=25, ha="right", rotation_mode="anchor")
    ax.tick_params(axis="x", pad=1.5)


def main():
    df = pd.read_excel(DATA_FILE, sheet_name="Plotting_data")
    for col in ["Age2", "latitude", "longitude"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Age2", "latitude", "longitude"]).copy()

    era_bins = [0, 66, 251.902, 538.8, float("inf")]
    df["Era"] = pd.cut(df["Age2"], bins=era_bins, labels=ERA_LABELS, right=False)

    lat_edges = np.arange(-90, 100, 10)
    lat_centers = lat_edges[:-1] + 5
    df["LatBin"] = pd.cut(df["latitude"], bins=lat_edges, right=False, include_lowest=True)
    lat_index = pd.IntervalIndex.from_breaks(lat_edges, closed="left")

    points = df.groupby(["LatBin", "Era"], observed=False).size().unstack(fill_value=0)
    points = points.reindex(index=lat_index, columns=ERA_LABELS, fill_value=0)

    site_counts = np.zeros((len(lat_index), len(ERA_LABELS)), dtype=int)
    for i, latbin in enumerate(lat_index):
        for j, era in enumerate(ERA_LABELS):
            sub = df[(df["LatBin"] == latbin) & (df["Era"] == era)]
            site_counts[i, j] = sub[["latitude", "longitude"]].drop_duplicates().shape[0]
    sites = pd.DataFrame(site_counts, index=lat_index, columns=ERA_LABELS)

    site_cmap = LinearSegmentedColormap.from_list(
        "hg_sites",
        ["#f7f8f8", "#dcebe4", "#9fc9b8", "#4f9aa4", "#283c63"],
    )
    point_cmap = LinearSegmentedColormap.from_list(
        "hg_points",
        ["#f7f8f8", "#e8d9a2", "#dfc56c", "#c77855", "#8f2632"],
    )
    site_cmap.set_bad("#f7f8f8")
    point_cmap.set_bad("#f7f8f8")

    site_mat = np.ma.masked_where(sites.values == 0, sites.values)
    point_mat = np.ma.masked_where(points.values == 0, points.values)

    fig = plt.figure(figsize=(183 / 25.4, 118 / 25.4), dpi=300)
    gs = GridSpec(
        2,
        2,
        height_ratios=[18, 0.52],
        width_ratios=[1, 1],
        left=0.078,
        right=0.985,
        top=0.958,
        bottom=0.118,
        hspace=0.285,
        wspace=0.12,
    )
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    caxes = [fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]

    mats = [site_mat, point_mat]
    raw_mats = [sites.values, points.values]
    cmaps = [site_cmap, point_cmap]
    cb_labels = ["Individual sampling sites", "Compiled data points"]
    panel_labels = ["(a)", "(b)"]

    for idx, (ax, cax, mat, raw, cmap, cb_label, panel) in enumerate(
        zip(axes, caxes, mats, raw_mats, cmaps, cb_labels, panel_labels)
    ):
        im = ax.imshow(mat, origin="lower", aspect="auto", cmap=cmap)
        add_era_ticks(ax)

        yticks = np.arange(1, len(lat_centers), 2)
        ax.set_yticks(yticks)
        ax.set_yticklabels([lat_label(lat_centers[i]) for i in yticks])
        if idx == 0:
            ax.set_ylabel("Latitude")
        else:
            ax.tick_params(axis="y", labelleft=False)

        ax.set_xticks(np.arange(-0.5, len(ERA_LABELS), 1), minor=True)
        ax.set_yticks(np.arange(-0.5, len(lat_centers), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.75)
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.tick_params(axis="both", length=3, width=0.55)

        ax.text(
            0.980,
            0.965,
            panel,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            fontweight="bold",
            color="#111111",
        )

        vmax = raw.max()
        for i in range(raw.shape[0]):
            for j in range(raw.shape[1]):
                v = int(raw[i, j])
                if v > 0:
                    txt_color = "white" if v >= vmax * 0.58 else "#1a1a1a"
                    ax.text(
                        j,
                        i,
                        f"{v:,}" if idx == 1 else str(v),
                        ha="center",
                        va="center",
                        fontsize=6.0,
                        color=txt_color,
                    )

        for spine in ax.spines.values():
            spine.set_linewidth(0.55)
            spine.set_color("#777777")

        cb = fig.colorbar(im, cax=cax, orientation="horizontal")
        cb.set_label(cb_label, labelpad=1.5, fontsize=7)
        cb.ax.tick_params(labelsize=6, length=2.5, width=0.45)
        cb.outline.set_linewidth(0.45)

    fig.savefig(OUTPUT_FILE, bbox_inches="tight", dpi=600)
    plt.close(fig)


if __name__ == "__main__":
    main()
