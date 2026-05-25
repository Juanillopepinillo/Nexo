from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PALETTE = {
    "bg": "#f5efe7",
    "panel": "#fffdfa",
    "ink": "#1f2430",
    "muted": "#667085",
    "grid": "#d8d1c6",
    "accent": "#8f5cff",
    "accent_soft": "#d9ccff",
    "teal": "#0f766e",
    "amber": "#d97706",
    "rose": "#b91c1c",
}


def _style_axes(fig, ax) -> None:
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["panel"])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid"])
    ax.tick_params(colors=PALETTE["ink"])
    ax.xaxis.label.set_color(PALETTE["ink"])
    ax.yaxis.label.set_color(PALETTE["ink"])
    ax.title.set_color(PALETTE["ink"])
    ax.grid(True, color=PALETTE["grid"], alpha=0.55, linewidth=0.8)


def _save_figure(fig, output_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)


def figure_link_budget(coverage_df: pd.DataFrame, title: str):
    row = coverage_df.iloc[0]
    labels = ["Ptx", "Gtx", "Grx", "Perdidas", "Sens"]
    increments = [
        43.0,
        18.0,
        0.0,
        -float(row["max_path_loss_db"] - row["receiver_sensitivity_dbm"]),
        -float(row["receiver_sensitivity_dbm"]),
    ]
    starts = [0.0]
    for value in increments[:-1]:
        starts.append(starts[-1] + value)
    ends = [start + value for start, value in zip(starts, increments)]
    colors = [PALETTE["teal"], PALETTE["accent"], PALETTE["accent_soft"], PALETTE["amber"], PALETTE["rose"]]

    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    _style_axes(fig, ax)

    for index, (label, start, end, color) in enumerate(zip(labels, starts, ends, colors)):
        left = min(start, end)
        width = abs(end - start)
        ax.barh(index, width, left=left, color=color, edgecolor="none", height=0.64)
        ax.text(end + 1.2, index, f"{end:.1f} dB", va="center", ha="left", fontsize=9, color=PALETTE["ink"])

    ax.axvline(float(row["max_path_loss_db"]), color=PALETTE["accent"], linestyle="--", linewidth=1.6)
    ax.text(
        float(row["max_path_loss_db"]) + 1.0,
        len(labels) - 0.3,
        f"Lmax = {float(row['max_path_loss_db']):.1f} dB",
        fontsize=9.5,
        fontweight="bold",
        color=PALETTE["accent"],
    )
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Presupuesto acumulado (dB)")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.grid(True, axis="x", color=PALETTE["grid"], alpha=0.6)
    return fig


def figure_district_radii(capacity_df: pd.DataFrame, coverage_df: pd.DataFrame):
    coverage_radius = float(coverage_df.iloc[0]["coverage_radius_km"])
    labels = [f"N={int(value)}" for value in capacity_df["reuse_factor_n"]]
    values = capacity_df["capacity_radius_km"].to_numpy(dtype=float)
    recommended = capacity_df["recommended"].to_numpy(dtype=bool)
    colors = [PALETTE["accent"] if flag else PALETTE["teal"] for flag in recommended]

    fig, ax = plt.subplots(figsize=(7.5, 4.7))
    _style_axes(fig, ax)
    bars = ax.bar(labels, values, color=colors, edgecolor="none")
    ax.axhline(coverage_radius, color=PALETTE["amber"], linestyle="--", linewidth=1.8, label="Radio por cobertura")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.008, f"{value:.3f} km", ha="center", fontsize=9, color=PALETTE["ink"])
    ax.set_ylabel("Radio (km)")
    ax.set_title("Escenario A: cobertura frente a capacidad", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    return fig


def figure_district_tradeoff(capacity_df: pd.DataFrame, snr_required_db: float):
    labels = [f"N={int(value)}" for value in capacity_df["reuse_factor_n"]]
    capacity = capacity_df["site_capacity_erlang"].to_numpy(dtype=float)
    sir = capacity_df["sectorized_sir_db"].to_numpy(dtype=float)
    recommended = capacity_df["recommended"].to_numpy(dtype=bool)
    colors = [PALETTE["accent"] if flag else PALETTE["amber"] for flag in recommended]

    fig, ax1 = plt.subplots(figsize=(8.3, 4.9))
    _style_axes(fig, ax1)
    ax1.bar(labels, capacity, color=colors, edgecolor="none", label="Capacidad por sitio")
    ax1.set_ylabel("Capacidad (Erlang)")
    ax1.set_title("Escenario A: compromiso entre capacidad e interferencia", loc="left", fontweight="bold")

    ax2 = ax1.twinx()
    ax2.set_facecolor("none")
    ax2.plot(labels, sir, color=PALETTE["teal"], marker="o", linewidth=2.2, label="SIR sectorizada")
    ax2.axhline(snr_required_db, color=PALETTE["rose"], linestyle=":", linewidth=1.6, label="SNR requerida")
    ax2.set_ylabel("SIR / SNR (dB)", color=PALETTE["ink"])
    ax2.tick_params(colors=PALETTE["ink"])

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, frameon=False, loc="upper left")
    return fig


def figure_festival_radii(capacity_df: pd.DataFrame):
    row = capacity_df.iloc[0]
    labels = ["Cobertura", "Capacidad"]
    values = [float(row["coverage_radius_km"]), float(row["capacity_radius_km"])]
    colors = [PALETTE["teal"], PALETTE["accent"]]

    fig, ax = plt.subplots(figsize=(7.1, 4.7))
    _style_axes(fig, ax)
    bars = ax.bar(labels, values, color=colors, edgecolor="none")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.05, f"{value:.3f} km", ha="center", fontsize=10, color=PALETTE["ink"])
    ax.set_ylabel("Radio (km)")
    ax.set_title("Escenario B: la cobertura no resuelve la congestion", loc="left", fontweight="bold")
    return fig


def figure_festival_splitting(splitting_df: pd.DataFrame):
    labels = [f"S{int(stage)}" for stage in splitting_df["split_stage"]]
    supported = splitting_df["supported_users_km2"].to_numpy(dtype=float)
    demand = float(splitting_df["demand_users_km2"].iloc[0])
    radius = splitting_df["radius_km"].to_numpy(dtype=float)
    recommended = splitting_df["recommended"].to_numpy(dtype=bool)
    colors = [PALETTE["accent"] if flag else PALETTE["amber"] for flag in recommended]

    fig, ax1 = plt.subplots(figsize=(8.5, 4.9))
    _style_axes(fig, ax1)
    ax1.bar(labels, supported, color=colors, edgecolor="none", label="Usuarios soportados/km2")
    ax1.axhline(demand, color=PALETTE["rose"], linestyle="--", linewidth=1.6, label="Demanda")
    ax1.set_ylabel("Usuarios soportados por km2")
    ax1.set_title("Escenario B: cell splitting para alcanzar la demanda", loc="left", fontweight="bold")

    ax2 = ax1.twinx()
    ax2.set_facecolor("none")
    ax2.plot(labels, radius, color=PALETTE["teal"], marker="o", linewidth=2.0, label="Radio resultante")
    ax2.set_ylabel("Radio (km)", color=PALETTE["ink"])
    ax2.tick_params(colors=PALETTE["ink"])

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

    fig, ax = plt.subplots(figsize=(9.7, 5.4))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["panel"])
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid"])

    ax.text(0.04, 0.92, "Operacion Nexo 5G/6G", transform=ax.transAxes, fontsize=22, fontweight="bold", color=PALETTE["ink"])
    ax.text(0.04, 0.84, "Figura resumen de decisiones de diseno para Nueva Pangea", transform=ax.transAxes, fontsize=11, color=PALETTE["muted"])

    boxes = [
        (
            0.05,
            0.16,
            0.4,
            0.54,
            "Escenario A · Distrito financiero",
            [
                f"Reuso recomendado: N = {int(district['reuse_factor_n'])}",
                f"Radio por cobertura: {float(district['coverage_radius_km']):.3f} km",
                f"Radio por capacidad: {float(district['capacity_radius_km']):.3f} km",
                f"SIR sectorizada: {float(district['sectorized_sir_db']):.2f} dB",
                f"Sitios en 1 km2: {int(district['sites_for_target_area'])}",
            ],
            PALETTE["accent"],
        ),
        (
            0.54,
            0.16,
            0.4,
            0.54,
            "Escenario B · Festival global",
            [
                f"Radio por cobertura: {float(festival['coverage_radius_km']):.3f} km",
                f"Radio por capacidad: {float(festival['capacity_radius_km']):.3f} km",
                f"Split recomendado: S{int(split['split_stage'])}",
                f"Usuarios soportados: {float(split['supported_users_km2']):.0f} usuarios/km2",
                f"Celdas en 1 km2: {int(split['sites_for_target_area'])}",
            ],
            PALETTE["teal"],
        ),
    ]

    for left, bottom, width, height, title, bullets, color in boxes:
        rect = plt.Rectangle((left, bottom), width, height, transform=ax.transAxes, facecolor="white", edgecolor=color, linewidth=2.0)
        ax.add_patch(rect)
        ax.text(left + 0.02, bottom + height - 0.08, title, transform=ax.transAxes, fontsize=13.5, fontweight="bold", color=color)
        y = bottom + height - 0.16
        for bullet in bullets:
            ax.text(left + 0.03, y, f"- {bullet}", transform=ax.transAxes, fontsize=10.8, color=PALETTE["ink"])
            y -= 0.09

    ax.text(
        0.04,
        0.05,
        "Conclusion: el distrito se limita por capacidad pero se resuelve con sectorizacion y N=4; el festival queda gobernado por densidad y exige cell splitting.",
        transform=ax.transAxes,
        fontsize=9.8,
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
