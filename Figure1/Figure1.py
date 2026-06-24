from pathlib import Path
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_BASE = "Figure1"


FIELD_GROUPS = {
    "Reference fields": [
        "Sample ID",
        "First Author",
        "Publication Time",
        "Reference",
        "DOI",
        "Data Type",
    ],
    "Sampling location fields": [
        "Longitude",
        "Latitude",
        "Location1",
        "Location2",
        "Section",
        "Paleolongitude",
        "Paleolatitude",
    ],
    "Chronostratigraphic fields": [
        "Age",
        "Unit",
        "Era",
        "Period",
        "Epoch",
        "Stage",
        "Formation",
    ],
    "Lithological and depositional fields": [
        "Lithology",
        "Setting",
        "Relative Depth",
    ],
    "Geochemical data fields": [
        "Hg Concentration",
        "Host Phase Proxies",
        "Hg Isotope Compositions",
        "Isotope 2σ Uncertainties",
        "Other Isotopes",
        "Fe-speciation Parameters",
        "Elemental Concentrations",
    ],
}


def setup_style():
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 8.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def wrapped_lines(items, width=28):
    lines = []
    for item in items:
        wrapped = textwrap.wrap(item, width=width)
        if not wrapped:
            continue
        lines.append("- " + wrapped[0])
        for continuation in wrapped[1:]:
            lines.append("  " + continuation)
    return lines


def main():
    setup_style()
    fig, ax = plt.subplots(figsize=(9.0, 3.55), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.23, 1)
    ax.axis("off")

    groups = list(FIELD_GROUPS.items())
    x_positions = [0.10, 0.285, 0.47, 0.655, 0.81]
    root_x, root_y = x_positions[2], 0.88
    trunk_y = 0.76
    header_y = 0.70
    items_y = 0.595

    ax.text(
        root_x,
        root_y,
        "DeepSedHg",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="square,pad=0.28", fc="white", ec="black", lw=0.8),
    )

    ax.plot([root_x, root_x], [root_y - 0.035, trunk_y], color="black", lw=0.8)
    ax.plot([x_positions[0], x_positions[-1]], [trunk_y, trunk_y], color="black", lw=0.8)

    ax.text(0.025, header_y, "Field\ncategory", ha="left", va="top", fontsize=8.2)
    ax.text(0.025, items_y, "Field\nitems", ha="left", va="top", fontsize=8.2)

    for x, (group_name, items) in zip(x_positions, groups):
        ax.plot([x, x], [trunk_y, header_y + 0.028], color="black", lw=0.8)
        header_text = "\n".join(textwrap.wrap(group_name, width=22))
        ax.text(x, header_y, header_text, ha="left", va="top", fontsize=8.8, fontweight="bold")

        line_y = items_y
        for line in wrapped_lines(items, width=25):
            ax.text(x, line_y, line, ha="left", va="top", fontsize=8.2)
            line_y -= 0.048

    fig.subplots_adjust(left=0.025, right=0.995, top=0.965, bottom=0.02)
    fig.savefig(f"{OUTPUT_BASE}.png", dpi=600, bbox_inches="tight")
    print(f"Saved: {OUTPUT_BASE}.png")


if __name__ == "__main__":
    main()
