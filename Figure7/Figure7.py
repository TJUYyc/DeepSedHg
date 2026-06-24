from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = "Figure7_data.xlsx"
OUT_PNG = "Figure7.png"

GROUPS = [
    ("Precambrian", "#2F6DB3"),
    ("Paleozoic", "#4B9B5E"),
    ("Mesozoic", "#E4943A"),
    ("Cenozoic", "#C84E4E"),
]

BIN_WIDTHS = {
    "lg Hg concentration": 0.25,
    "delta202Hg_permil": 0.25,
    "Delta199Hg_permil": 0.05,
    "Delta200Hg_permil": 0.01,
}

X_LIMITS = {
    "lg Hg concentration": (-2.2, 5.1),
    "delta202Hg_permil": (-4.0, 3.0),
    "Delta199Hg_permil": (-0.78, 0.78),
    "Delta200Hg_permil": (-0.20, 0.25),
}


def find_nth_column(columns, token, occurrence):
    matches = [col for col in columns if token in str(col)]
    if len(matches) < occurrence:
        raise ValueError(f"Could not find occurrence {occurrence} for token {token!r}")
    return matches[occurrence - 1]


def age_group(age):
    if pd.isna(age):
        return np.nan
    if age >= 545:
        return "Precambrian"
    if age >= 251.9:
        return "Paleozoic"
    if age >= 66:
        return "Mesozoic"
    if age >= 0:
        return "Cenozoic"
    return np.nan


def kde_1d(values, grid):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return np.full_like(grid, np.nan, dtype=float)

    std = np.std(values, ddof=1)
    q25, q75 = np.percentile(values, [25, 75])
    iqr = q75 - q25
    sigma = min(std, iqr / 1.349) if iqr > 0 else std
    if not np.isfinite(sigma) or sigma <= 0:
        sigma = std if std > 0 else 1.0

    bandwidth = 0.9 * sigma * values.size ** (-1 / 5)
    if not np.isfinite(bandwidth) or bandwidth <= 0:
        bandwidth = max(std, 1.0) * 0.2

    z = (grid[:, None] - values[None, :]) / bandwidth
    density = np.exp(-0.5 * z * z).sum(axis=1)
    density /= values.size * bandwidth * np.sqrt(2 * np.pi)
    return density


def clean_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def load_plotting_data():
    plot_df = pd.read_excel(DATA_FILE, sheet_name="plotting_data")
    required_columns = [
        "Age group",
        "lg Hg concentration",
        "delta202Hg_permil",
        "Delta199Hg_permil",
        "Delta200Hg_permil",
    ]
    missing = [col for col in required_columns if col not in plot_df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {DATA_FILE.name}: {missing}")

    numeric_columns = [
        "Age (Ma)",
        "Hg concentration (ppb)",
        "lg Hg concentration",
        "delta202Hg_permil",
        "Delta199Hg_permil",
        "Delta200Hg_permil",
    ]
    for col in numeric_columns:
        if col in plot_df.columns:
            plot_df[col] = clean_numeric(plot_df[col])

    return plot_df


def make_summary(plot_df, variables):
    rows = []
    for var_key, label, _ in variables:
        for group, _color in GROUPS:
            values = plot_df.loc[plot_df["Age group"].eq(group), var_key].dropna()
            if values.empty:
                rows.append(
                    {
                        "Variable": label,
                        "Age group": group,
                        "n": 0,
                        "median": np.nan,
                        "IQR_low": np.nan,
                        "IQR_high": np.nan,
                        "min": np.nan,
                        "max": np.nan,
                    }
                )
                continue
            q25, med, q75 = np.percentile(values, [25, 50, 75])
            rows.append(
                {
                    "Variable": label,
                    "Age group": group,
                    "n": int(values.size),
                    "median": med,
                    "IQR_low": q25,
                    "IQR_high": q75,
                    "min": values.min(),
                    "max": values.max(),
                }
            )
    return pd.DataFrame(rows)


def plot_frequency_panel(ax, plot_df, var_key, label, panel_label):
    all_values = plot_df[var_key].dropna().to_numpy(dtype=float)
    if var_key in X_LIMITS:
        x_min, x_max = X_LIMITS[var_key]
    else:
        lo, hi = np.percentile(all_values, [0.1, 99.9])
        padding = (hi - lo) * 0.12 if hi > lo else 1.0
        x_min, x_max = lo - padding, hi + padding
    grid = np.linspace(x_min, x_max, 500)
    bin_width = BIN_WIDTHS[var_key]

    max_frequency = 0
    for group, color in GROUPS:
        values = plot_df.loc[plot_df["Age group"].eq(group), var_key].dropna()
        if values.size < 2:
            continue
        density = kde_1d(values, grid)
        if np.all(np.isnan(density)):
            continue
        frequency = density * bin_width * 100
        max_frequency = max(max_frequency, float(np.nanmax(frequency)))
        ax.plot(grid, frequency, color=color, lw=1.9, label=group)
        ax.fill_between(grid, frequency, 0, color=color, alpha=0.20, linewidth=0)

        median = float(np.median(values))
        if x_min <= median <= x_max:
            ax.axvline(median, color=color, lw=1.0, ls="--", alpha=0.80)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(bottom=0, top=max_frequency * 1.18 if max_frequency > 0 else None)
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel("Frequency (%)", fontsize=10)
    ax.text(
        0.02,
        0.94,
        panel_label,
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )
    ax.tick_params(axis="both", labelsize=9, direction="out", length=3.5, width=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="0.88", lw=0.6)


def main():
    plot_df = load_plotting_data()

    per_mil = "\u2030"
    variables = [
        ("lg Hg concentration", "lg Hg concentration (ppb)", "(a)"),
        ("delta202Hg_permil", rf"$\delta^{{202}}$Hg ({per_mil})", "(b)"),
        ("Delta199Hg_permil", rf"$\Delta^{{199}}$Hg ({per_mil})", "(c)"),
        ("Delta200Hg_permil", rf"$\Delta^{{200}}$Hg ({per_mil})", "(d)"),
    ]

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(8.6, 6.5), constrained_layout=False)
    for ax, (var_key, label, panel_label) in zip(axes.ravel(), variables):
        plot_frequency_panel(ax, plot_df, var_key, label, panel_label)

    handles = [
        Line2D([0], [0], color=color, lw=2.2, label=group) for group, color in GROUPS
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=4,
        frameon=False,
        fontsize=10,
        bbox_to_anchor=(0.5, 0.995),
        handlelength=2.2,
        columnspacing=1.6,
    )

    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.085, top=0.915, wspace=0.28, hspace=0.32)
    fig.savefig(OUT_PNG, dpi=600, bbox_inches="tight")

    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()

