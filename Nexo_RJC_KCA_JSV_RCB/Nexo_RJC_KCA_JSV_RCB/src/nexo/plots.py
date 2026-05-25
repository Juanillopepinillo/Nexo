from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    }
)


PALETTE = {
    "canvas": "#ffffff",
    "axes": "#ffffff",
    "ink": "#102a43",
    "muted": "#486581",
    "grid": "#d9e2ec",
    "spine": "#bcccdc",
    "primary": "#1f4e79",
    "secondary": "#627d98",
    "highlight": "#0f766e",
    "warning": "#b45309",
    "danger": "#ba3a3a",
    "panel": "#edf3f8",
}


def _style_axes(fig, ax, *, grid_axis: str = "y") -> None:
    fig.patch.set_facecolor(PALETTE["canvas"])
    ax.set_facecolor(PALETTE["axes"])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["spine"])
        spine.set_linewidth(0.9)
    ax.tick_params(colors=PALETTE["ink"])
    ax.xaxis.label.set_color(PALETTE["ink"])
    ax.yaxis.label.set_color(PALETTE["ink"])
    ax.title.set_color(PALETTE["ink"])
    ax.grid(True, axis=grid_axis, color=PALETTE["grid"], linewidth=0.8)
    ax.set_axisbelow(True)


def _style_secondary_axis(ax) -> None:
    ax.set_facecolor("none")
    for spine in ax.spines.values():
        spine.set_color(PALETTE["spine"])
    ax.tick_params(colors=PALETTE["ink"])
    ax.xaxis.label.set_color(PALETTE["ink"])
    ax.yaxis.label.set_color(PALETTE["ink"])


def _save_figure(fig, output_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=240, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def figure_link_budget(coverage_df: pd.DataFrame, title: str):
    row = coverage_df.iloc[0]
    steps = [
        ("Ptx", 43.0, PALETTE["primary"]),
        ("Gtx", 18.0, PALETTE["secondary"]),
        ("Grx", 0.0, PALETTE["secondary"]),
        ("Perdidas adicionales", -12.0, PALETTE["warning"]),
        ("-Sensibilidad", -float(row["receiver_sensitivity_dbm"]), PALETTE["highlight"]),
    ]
    max_path_loss_db = float(row["max_path_loss_db"])
    labels = [label for label, _, _ in steps] + ["Lmax"]

    cumulative = 0.0
    starts = []
    ends = []
    for _, value, _ in steps:
        starts.append(cumulative)
        cumulative += value
        ends.append(cumulative)

    fig, ax = plt.subplots(figsize=(11.8, 6.2))
    _style_axes(fig, ax, grid_axis="y")

    for idx, ((_, value, color), start, end) in enumerate(zip(steps, starts, ends)):
        bottom = min(start, end)
        height = abs(end - start)
        ax.bar(idx, height, bottom=bottom, width=0.62, color=color, edgecolor="none")
        ax.text(
            idx,
            end + (2.5 if value >= 0 else -3.5),
            f"{value:+.1f} dB",
            ha="center",
            va="bottom" if value >= 0 else "top",
            color=PALETTE["ink"],
        )

    ax.bar(len(steps), max_path_loss_db, width=0.62, color=PALETTE["danger"], edgecolor="none")
    ax.text(len(steps), max_path_loss_db + 2.5, f"{max_path_loss_db:.1f} dB", ha="center", va="bottom", color=PALETTE["ink"])

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Contribucion acumulada (dB)")
    ax.set_title(title, loc="left")
    ax.yaxis.set_major_locator(MaxNLocator(7))
    ax.set_ylim(min(0.0, min(start for start in starts)) - 10.0, max_path_loss_db + 15.0)
    return fig


def figure_district_radii(capacity_df: pd.DataFrame, coverage_df: pd.DataFrame):
    coverage_radius = float(coverage_df.iloc[0]["coverage_radius_km"])
    labels = [f"N={int(value)}" for value in capacity_df["reuse_factor_n"]]
    values = capacity_df["capacity_radius_km"].to_numpy(dtype=float)
    recommended = capacity_df["recommended"].to_numpy(dtype=bool)
    colors = [PALETTE["highlight"] if flag else PALETTE["primary"] for flag in recommended]

    fig, ax = plt.subplots(figsize=(11.4, 6.2))
    _style_axes(fig, ax, grid_axis="y")
    bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.56)
    ax.axhline(coverage_radius, color=PALETTE["danger"], linestyle="--", linewidth=1.7, label="Radio por cobertura")

    for bar, value, is_recommended in zip(bars, values, recommended):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.008, f"{value:.3f} km", ha="center", va="bottom", color=PALETTE["ink"])
        if is_recommended:
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.035, "Opcion recomendada", ha="center", va="bottom", color=PALETTE["highlight"], fontsize=9.5, fontweight="bold")

    ax.set_ylabel("Radio de capacidad (km)")
    ax.set_title("Escenario A. Comparacion entre radio por cobertura y radio por capacidad", loc="left")
    ax.legend(frameon=False, loc="upper right")
    ax.yaxis.set_major_locator(MaxNLocator(6))
    return fig


def figure_district_tradeoff(capacity_df: pd.DataFrame, snr_required_db: float):
    labels = [f"N={int(value)}" for value in capacity_df["reuse_factor_n"]]
    capacity = capacity_df["site_capacity_erlang"].to_numpy(dtype=float)
    sir = capacity_df["sectorized_sir_db"].to_numpy(dtype=float)
    omni_sir = capacity_df["omnidirectional_sir_db"].to_numpy(dtype=float)
    recommended = capacity_df["recommended"].to_numpy(dtype=bool)
    colors = [PALETTE["highlight"] if flag else PALETTE["secondary"] for flag in recommended]

    fig, ax1 = plt.subplots(figsize=(11.8, 6.4))
    _style_axes(fig, ax1, grid_axis="y")
    bars = ax1.bar(labels, capacity, color=colors, edgecolor="none", width=0.56, label="Capacidad por sitio")
    ax1.set_ylabel("Capacidad (Erlang)")
    ax1.set_title("Escenario A. Compromiso entre capacidad agregada y margen radio", loc="left")
    ax1.yaxis.set_major_locator(MaxNLocator(6))

    ax2 = ax1.twinx()
    _style_secondary_axis(ax2)
    ax2.plot(labels, sir, color=PALETTE["primary"], marker="o", linewidth=2.4, markersize=7, label="SIR sectorizada")
    ax2.plot(labels, omni_sir, color=PALETTE["warning"], marker="s", linewidth=2.0, markersize=6, label="SIR omni de referencia")
    ax2.axhline(snr_required_db, color=PALETTE["danger"], linestyle="--", linewidth=1.7, label="SNR requerida")
    ax2.set_ylabel("SIR (dB)")
    ax2.yaxis.set_major_locator(MaxNLocator(6))

    for bar, value in zip(bars, capacity):
        ax1.text(bar.get_x() + bar.get_width() / 2, value + 0.4, f"{value:.1f}", ha="center", va="bottom", color=PALETTE["ink"], fontsize=9.5)

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper right")
    return fig


def figure_festival_radii(capacity_df: pd.DataFrame):
    row = capacity_df.iloc[0]
    labels = ["Radio por cobertura", "Radio por capacidad"]
    values = [float(row["coverage_radius_km"]), float(row["capacity_radius_km"])]
    colors = [PALETTE["primary"], PALETTE["danger"]]

    fig, ax = plt.subplots(figsize=(11.6, 5.4))
    _style_axes(fig, ax, grid_axis="x")
    bars = ax.barh(labels, values, color=colors, edgecolor="none", height=0.52)

    for bar, value in zip(bars, values):
        ax.text(value + 0.06, bar.get_y() + bar.get_height() / 2, f"{value:.3f} km", va="center", ha="left", color=PALETTE["ink"])

    ax.set_xlabel("Radio equivalente (km)")
    ax.set_title("Escenario B. Comparativa entre radio teorico de cobertura y radio util por capacidad", loc="left")
    ax.xaxis.set_major_locator(MaxNLocator(7))
    ax.invert_yaxis()
    return fig


def figure_festival_splitting(splitting_df: pd.DataFrame):
    stage_values = splitting_df["split_stage"].to_numpy(dtype=int)
    labels = [f"S{stage}" for stage in stage_values]
    supported = splitting_df["supported_users_km2"].to_numpy(dtype=float)
    demand = float(splitting_df["demand_users_km2"].iloc[0])
    radius = splitting_df["radius_km"].to_numpy(dtype=float)
    recommended_stage = int(splitting_df.loc[splitting_df["recommended"], "split_stage"].iloc[0])

    fig, ax1 = plt.subplots(figsize=(11.8, 6.4))
    _style_axes(fig, ax1, grid_axis="y")
    ax1.plot(stage_values, supported, color=PALETTE["primary"], marker="o", linewidth=2.4, markersize=7, label="Usuarios soportados")
    ax1.axhline(demand, color=PALETTE["danger"], linestyle="--", linewidth=1.7, label="Demanda objetivo")
    ax1.axvline(recommended_stage, color=PALETTE["highlight"], linestyle=":", linewidth=1.8)
    ax1.set_yscale("log")
    ax1.set_ylabel("Usuarios soportados por km2")
    ax1.set_xticks(stage_values)
    ax1.set_xticklabels(labels)
    ax1.set_title("Escenario B. Efecto del cell splitting sobre la densidad de usuarios soportada", loc="left")

    ax2 = ax1.twinx()
    _style_secondary_axis(ax2)
    ax2.plot(stage_values, radius, color=PALETTE["secondary"], marker="s", linewidth=2.0, markersize=6.5, label="Radio resultante")
    ax2.set_ylabel("Radio por celda (km)")
    ax2.yaxis.set_major_locator(MaxNLocator(6))

    ax1.annotate(
        "Primera etapa viable",
        xy=(recommended_stage, supported[recommended_stage]),
        xytext=(recommended_stage + 0.35, supported[recommended_stage] * 1.8),
        arrowprops={"arrowstyle": "->", "color": PALETTE["highlight"], "lw": 1.2},
        color=PALETTE["highlight"],
        fontsize=10,
        fontweight="bold",
    )

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper left")
    return fig


def figure_solution_summary(
    district_capacity_df: pd.DataFrame,
    festival_capacity_df: pd.DataFrame,
    festival_splitting_df: pd.DataFrame,
):
    district = district_capacity_df.loc[district_capacity_df["recommended"]].iloc[0]
    festival = festival_capacity_df.iloc[0]
    split = festival_splitting_df.loc[festival_splitting_df["recommended"]].iloc[0]

    fig, ax = plt.subplots(figsize=(13.2, 6.6))
    fig.patch.set_facecolor(PALETTE["canvas"])
    ax.set_facecolor(PALETTE["axes"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["spine"])
        spine.set_linewidth(0.9)

    ax.text(0.04, 0.92, "Operacion Nexo 5G/6G", transform=ax.transAxes, fontsize=21, fontweight="bold", color=PALETTE["ink"])
    ax.text(0.04, 0.85, "Resumen de decisiones de dimensionamiento radio para Nueva Pangea", transform=ax.transAxes, fontsize=11, color=PALETTE["muted"])

    panels = [
        (
            0.05,
            "Escenario A · Distrito financiero",
            [
                f"Reuso recomendado: N = {int(district['reuse_factor_n'])}",
                f"Radio por cobertura: {float(district['coverage_radius_km']):.3f} km",
                f"Radio de diseno: {float(district['design_radius_km']):.3f} km",
                f"SIR sectorizada: {float(district['sectorized_sir_db']):.2f} dB",
                f"Sitios por 1 km2: {int(district['sites_for_target_area'])}",
            ],
            PALETTE["primary"],
        ),
        (
            0.53,
            "Escenario B · Festival global",
            [
                f"Radio por cobertura: {float(festival['coverage_radius_km']):.3f} km",
                f"Radio sin splitting: {float(festival['capacity_radius_km']):.3f} km",
                f"Etapa recomendada: S{int(split['split_stage'])}",
                f"Radio final por celda: {float(split['radius_km']):.3f} km",
                f"Celdas por 1 km2: {int(split['sites_for_target_area'])}",
            ],
            PALETTE["highlight"],
        ),
    ]

    for left, title, items, color in panels:
        rect = Rectangle((left, 0.18), 0.42, 0.56, transform=ax.transAxes, facecolor=PALETTE["panel"], edgecolor=PALETTE["spine"], linewidth=1.0)
        ax.add_patch(rect)
        ax.text(left + 0.02, 0.68, title, transform=ax.transAxes, fontsize=13, fontweight="bold", color=color)
        y = 0.60
        for item in items:
            ax.text(left + 0.03, y, f"- {item}", transform=ax.transAxes, fontsize=10.5, color=PALETTE["ink"])
            y -= 0.095

    ax.text(
        0.04,
        0.07,
        "Conclusion tecnica: el escenario A se limita por capacidad pero se resuelve con sectorizacion y N=4; el escenario B queda dominado por la densidad y requiere cell splitting hasta S4.",
        transform=ax.transAxes,
        fontsize=9.5,
        color=PALETTE["muted"],
    )
    return fig


def save_link_budget_plot(coverage_df: pd.DataFrame, output_path: Path, title: str) -> None:
    _save_figure(figure_link_budget(coverage_df, title), output_path)


def save_district_radii_plot(capacity_df: pd.DataFrame, coverage_df: pd.DataFrame, output_path: Path) -> None:
    _save_figure(figure_district_radii(capacity_df, coverage_df), output_path)


def save_district_tradeoff_plot(capacity_df: pd.DataFrame, snr_required_db: float, output_path: Path) -> None:
    _save_figure(figure_district_tradeoff(capacity_df, snr_required_db), output_path)


def save_festival_radii_plot(capacity_df: pd.DataFrame, output_path: Path) -> None:
    _save_figure(figure_festival_radii(capacity_df), output_path)


def save_festival_splitting_plot(splitting_df: pd.DataFrame, output_path: Path) -> None:
    _save_figure(figure_festival_splitting(splitting_df), output_path)


def save_solution_summary_plot(
    district_capacity_df: pd.DataFrame,
    festival_capacity_df: pd.DataFrame,
    festival_splitting_df: pd.DataFrame,
    output_path: Path,
) -> None:
    _save_figure(figure_solution_summary(district_capacity_df, festival_capacity_df, festival_splitting_df), output_path)
