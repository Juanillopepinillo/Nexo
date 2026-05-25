from html import escape as html_escape
from pathlib import Path

import markdown
import pandas as pd


def _markdown_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, bool):
        return "Si" if value else "No"
    if isinstance(value, float):
        return format(value, "g")
    return str(value).replace("|", "\\|")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    columns = [str(column) for column in df.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in df.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")
    return "\n".join(lines)


def build_report_markdown(
    system_table: pd.DataFrame,
    scenario_goal_table: pd.DataFrame,
    assumptions_table: pd.DataFrame,
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]

    lines = [
        "# Operacion Nexo 5G/6G - Informe tecnico",
        "",
        "## Resumen",
        "",
        "Este informe dimensiona una red movil moderna para Nueva Pangea en dos escenarios de alta demanda: un distrito financiero urbano y un festival temporal masivo.",
        f"El escenario A queda limitado por capacidad y recomienda N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio.",
        f"El escenario B queda gobernado por densidad de trafico y exige cell splitting hasta la etapa S{int(festival_choice['split_stage'])}.",
        "",
        "## 1. Introduccion",
        "",
        "Una red movil moderna no se dimensiona solo por cobertura. En una ciudad inteligente importa separar alcance radio, carga de trafico e interferencia para tomar decisiones defendibles.",
        "",
        "## 2. Estado del arte",
        "",
        "LTE y 5G basan su eficiencia en OFDMA, planificacion dinamica y adaptacion MCS. Aun asi, el dimensionamiento inicial sigue dependiendo del balance de enlace, de los modelos de propagacion y de la teoria de trafico.",
        "",
        "## 3. Metodologia",
        "",
        "La cadena de calculo replica el enunciado: ruido termico, sensibilidad, perdida maxima admisible, radio por cobertura, trafico por usuario, densidad de trafico, capacidad Erlang B y radio por capacidad.",
        "",
        "### 3.1 Parametros base",
        "",
        dataframe_to_markdown(system_table),
        "",
        "### 3.2 Objetivos por escenario",
        "",
        dataframe_to_markdown(scenario_goal_table),
        "",
        "## 4. Resultados",
        "",
        "### 4.1 Cobertura",
        "",
        dataframe_to_markdown(pd.concat([district_coverage, festival_coverage], ignore_index=True)),
        "",
        "### 4.2 Capacidad en el distrito financiero",
        "",
        dataframe_to_markdown(district_capacity),
        "",
        "### 4.3 Capacidad y splitting en el festival",
        "",
        dataframe_to_markdown(festival_capacity),
        "",
        dataframe_to_markdown(festival_splitting),
        "",
        "## 5. Discusion",
        "",
        f"El radio por cobertura del distrito financiero es {float(district_coverage.iloc[0]['coverage_radius_km']):.3f} km, pero el radio de diseno recomendado cae a {float(district_choice['design_radius_km']):.3f} km por la carga de trafico.",
        f"En el festival la diferencia es todavia mayor: la cobertura teorica alcanza {float(festival_coverage.iloc[0]['coverage_radius_km']):.3f} km mientras que la capacidad sin splitting solo sostiene {float(festival_capacity.iloc[0]['capacity_radius_km']):.3f} km.",
        "",
        "## 6. Supuestos de trazabilidad",
        "",
        dataframe_to_markdown(assumptions_table),
        "",
        "## 7. Conclusiones",
        "",
        f"La solucion adoptada para el escenario A es N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio, porque es la primera opcion que cumple el umbral radio con la mayor capacidad posible.",
        f"La solucion adoptada para el escenario B es cell splitting hasta S{int(festival_choice['split_stage'])}, porque la densidad de usuarios domina claramente sobre la cobertura.",
        "",
        "### 7.1 Nueva Pangea 2030",
        "",
        "Si la densidad creciera, la evolucion natural del diseno pasaria por small cells, mas espectro, beamforming, slicing y edge computing.",
    ]
    return "\n".join(lines)


def build_annex_markdown(
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
) -> str:
    district_cov = district_coverage.iloc[0]
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_cov = festival_coverage.iloc[0]
    festival_cap = festival_capacity.iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]

    lines = [
        "# Operacion Nexo 5G/6G - Anexo de calculos",
        "",
        "## Escenario A - Distrito financiero",
        "",
        f"1. Ruido termico: `N = {district_cov['thermal_noise_dbm']:.3f} dBm`.",
        f"2. Sensibilidad: `Sens = {district_cov['receiver_sensitivity_dbm']:.3f} dBm`.",
        f"3. Perdida maxima admisible: `Lmax = {district_cov['max_path_loss_db']:.3f} dB`.",
        f"4. Radio por cobertura: `Rcov = {district_cov['coverage_radius_km']:.3f} km`.",
        f"5. Trafico por usuario: `Auser = {district_cov['traffic_per_user_erlang']:.3f} Erl`.",
        f"6. Densidad de trafico: `Akm2 = {district_cov['traffic_density_erlang_km2']:.3f} Erl/km2`.",
        f"7. Reuso recomendado: `N = {int(district_choice['reuse_factor_n'])}` con `Rdesign = {district_choice['design_radius_km']:.3f} km`.",
        "",
        "## Escenario B - Festival global",
        "",
        f"1. Ruido termico: `N = {festival_cov['thermal_noise_dbm']:.3f} dBm`.",
        f"2. Sensibilidad: `Sens = {festival_cov['receiver_sensitivity_dbm']:.3f} dBm`.",
        f"3. Perdida maxima admisible: `Lmax = {festival_cov['max_path_loss_db']:.3f} dB`.",
        f"4. Radio por cobertura: `Rcov = {festival_cov['coverage_radius_km']:.3f} km`.",
        f"5. Radio por capacidad sin splitting: `Rcap = {festival_cap['capacity_radius_km']:.3f} km`.",
        f"6. Split recomendado: `S{int(festival_choice['split_stage'])}` con `R = {festival_choice['radius_km']:.3f} km`.",
        f"7. Sitios en 1 km2 tras splitting: `{int(festival_choice['sites_for_target_area'])}`.",
    ]
    return "\n".join(lines)


def build_defense_brief_markdown(district_capacity: pd.DataFrame, festival_splitting: pd.DataFrame) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]
    lines = [
        "# Operacion Nexo 5G/6G - Guion de defensa",
        "",
        "- El reto separa explicitamente cobertura y capacidad.",
        f"- En el distrito financiero la recomendacion final es N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio.",
        f"- En el festival la cobertura no es el problema; la solucion es cell splitting hasta S{int(festival_choice['split_stage'])}.",
        "- El radio final siempre adopta el criterio mas restrictivo.",
        "- Las decisiones quedan trazadas en tablas, CSV y figuras dentro de la web estatica.",
    ]
    return "\n".join(lines)


def build_html_document(document_title: str, markdown_text: str) -> str:
    html_body = markdown.markdown(markdown_text, extensions=["tables"])
    return f"""<!doctype html>
<html lang=\"es\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{html_escape(document_title)}</title>
  <style>
    body {{ font-family: Arial, Helvetica, sans-serif; margin: 0; background: #f7f2ea; color: #20242f; }}
    main {{ max-width: 1100px; margin: 32px auto; background: white; padding: 36px 42px; border-radius: 18px; box-shadow: 0 18px 40px rgba(0,0,0,0.08); }}
    h1, h2, h3 {{ color: #181c24; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 1.4rem 0; font-size: 0.94rem; }}
    th, td {{ border: 1px solid #ddd5ca; padding: 0.55rem 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f3ebe0; color: #8f5cff; text-transform: uppercase; font-size: 0.78rem; }}
    code {{ background: #f3ece3; padding: 0.12rem 0.28rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <main>{html_body}</main>
</body>
</html>
"""


def write_html_document(output_path: Path, document_title: str, markdown_text: str) -> None:
    output_path.write_text(build_html_document(document_title, markdown_text), encoding="utf-8")
