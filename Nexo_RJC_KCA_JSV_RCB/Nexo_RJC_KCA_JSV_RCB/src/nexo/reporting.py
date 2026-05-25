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
    compliance_table: pd.DataFrame,
    validation_table: pd.DataFrame,
) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]

    lines = [
        "# Operacion Nexo 5G/6G - Informe tecnico",
        "",
        "## Resumen",
        "",
        "Este informe desarrolla el reto Operacion Nexo 5G/6G para Nueva Pangea comparando dos escenarios de alta demanda: un distrito financiero urbano de alta densidad y un festival temporal con congestion extrema de usuarios.",
        f"El escenario A queda limitado por capacidad y recomienda N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio.",
        f"El escenario B queda gobernado por densidad de trafico y exige cell splitting hasta la etapa S{int(festival_choice['split_stage'])}.",
        "",
        "## 1. Introduccion",
        "",
        "Las redes moviles modernas deben resolver simultaneamente problemas de cobertura, capacidad e interferencia. En una ciudad inteligente, la conectividad de un distrito financiero no se comporta igual que la de un evento temporal con gran afluencia de usuarios. Por eso el dimensionamiento celular no puede apoyarse en un unico radio de cobertura, sino en una comparacion explicita entre el alcance del enlace y la carga de trafico soportable.",
        "",
        "El objetivo del trabajo es justificar, con base fisica y matematica, la solucion de red mas adecuada en cada escenario y defender por que el radio final de diseno debe adoptarse siempre como el criterio mas restrictivo entre cobertura y capacidad.",
        "",
        "## 2. Estado del arte",
        "",
        "La evolucion hacia LTE y 5G consolida OFDMA, planificacion flexible de recursos y adaptacion dinamica de MCS. En ese contexto, la robustez y la eficiencia espectral dependen directamente de la calidad del canal y del margen radio disponible. Aun asi, el dimensionamiento preliminar sigue descansando sobre herramientas clasicas: balance de enlace, modelos logaritmicos de propagacion y teoria de trafico.",
        "",
        "Los modelos de propagacion permiten traducir una perdida maxima admisible en un radio equivalente de cobertura. Por su parte, Erlang B sigue siendo una herramienta valida para estimar capacidad agregada y probabilidad de bloqueo cuando se desea comparar alternativas de diseno bajo un grado de servicio fijado.",
        "",
        "## 3. Metodologia",
        "",
        "La metodologia replica el orden propuesto en la guia docente: ruido termico, sensibilidad, perdida maxima admisible, radio por cobertura, trafico por usuario, densidad de trafico, capacidad Erlang B y radio por capacidad. El criterio final adopta siempre el menor radio entre cobertura y capacidad.",
        "",
        "### 3.1 Expresiones de referencia",
        "",
        "- `N = -174 + 10 log10(B) + NF` para el ruido termico.",
        "- `Sens = N + SNRreq + Limpl` para la sensibilidad de receptor.",
        "- `Pr = Ptx + Gtx + Grx - Lp - Lotros` para el balance de enlace.",
        "- `Auser = lambda * h` para el trafico por usuario en Erlangs.",
        "- Inversion de Erlang B para obtener la capacidad maxima al 2% de bloqueo.",
        "",
        "### 3.2 Parametros base",
        "",
        dataframe_to_markdown(system_table),
        "",
        "### 3.3 Objetivos por escenario",
        "",
        dataframe_to_markdown(scenario_goal_table),
        "",
        "### 3.4 Supuestos de trazabilidad",
        "",
        dataframe_to_markdown(assumptions_table),
        "",
        "## 4. Escenarios",
        "",
        "### 4.1 Escenario A - Distrito financiero",
        "",
        f"El distrito financiero representa un entorno urbano denso con {float(district_coverage.iloc[0]['traffic_density_erlang_km2']):.1f} Erl/km2, una SNR requerida de 15 dB y una arquitectura de tres sectores por sitio. El reto exige comparar N = 3, 4 y 7 para evaluar el equilibrio entre capacidad e interferencia.",
        "",
        "### 4.2 Escenario B - Festival global de innovacion",
        "",
        f"El festival representa una explanada abierta con {float(festival_coverage.iloc[0]['traffic_density_erlang_km2']):.1f} Erl/km2, una SNR requerida de 5 dB, celdas omnidireccionales y necesidad de evaluar cell splitting para absorber la demanda.",
        "",
        "## 5. Pruebas, calculos y simulaciones",
        "",
        "### 5.1 Cobertura",
        "",
        dataframe_to_markdown(pd.concat([district_coverage, festival_coverage], ignore_index=True)),
        "",
        "### 5.2 Escenario A - Capacidad e interferencia",
        "",
        dataframe_to_markdown(district_capacity),
        "",
        f"La ganancia de sectorizacion para la opcion recomendada es {float(district_choice['sectorization_gain_db']):.3f} dB respecto a una referencia omnidireccional de primera corona.",
        "",
        "### 5.3 Escenario B - Capacidad y cell splitting",
        "",
        dataframe_to_markdown(festival_capacity),
        "",
        dataframe_to_markdown(festival_splitting),
        "",
        "### 5.4 Validacion numerica de consistencia",
        "",
        dataframe_to_markdown(validation_table),
        "",
        "## 6. Resultados",
        "",
        f"En el distrito financiero, el radio por cobertura es {float(district_coverage.iloc[0]['coverage_radius_km']):.3f} km, pero el radio recomendado cae a {float(district_choice['design_radius_km']):.3f} km por limitacion de capacidad.",
        f"En el festival, la cobertura teorica alcanza {float(festival_coverage.iloc[0]['coverage_radius_km']):.3f} km mientras que la capacidad sin splitting solo sostiene {float(festival_capacity.iloc[0]['capacity_radius_km']):.3f} km.",
        f"El escenario A recomienda N={int(district_choice['reuse_factor_n'])} y el escenario B recomienda cell splitting hasta S{int(festival_choice['split_stage'])}.",
        "",
        "## 7. Discusion",
        "",
        "La comparacion entre escenarios confirma que el diseno celular no puede justificarse solo por cobertura. En el distrito financiero la sectorizacion y la reutilizacion permiten controlar la interferencia, pero el parametro dominante sigue siendo la capacidad agregada por sitio. Un N muy bajo deja poco margen radio, mientras que un N muy alto penaliza severamente la capacidad. Por eso N=4 es la primera opcion tecnicamente equilibrada.",
        "",
        f"Ademas, la comparacion entre SIR sectorizada y SIR omnidireccional muestra una mejora de {float(district_choice['sectorization_gain_db']):.3f} dB para la opcion recomendada, lo que refuerza la necesidad de sectorizar el sitio en el escenario urbano denso.",
        "",
        "En el festival la situacion cambia por completo. La propagacion abierta y la menor SNR requerida dan un radio de cobertura muy amplio, pero eso no aporta una solucion real porque la limitacion dominante es la densidad de trafico. La unica estrategia coherente dentro del marco del enunciado es el cell splitting, que incrementa la densidad de celdas hasta superar la demanda objetivo.",
        "",
        "## 8. Conclusiones",
        "",
        f"La solucion adoptada para el escenario A es N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio, porque es la primera alternativa que supera el umbral radio y mantiene una capacidad razonable por sitio.",
        f"La solucion adoptada para el escenario B es cell splitting hasta S{int(festival_choice['split_stage'])}, porque la densidad de usuarios domina claramente sobre la cobertura y obliga a reducir el area de servicio por celda.",
        "",
        "### 8.1 Nueva Pangea 2030",
        "",
        "Si la densidad de usuarios creciera o se demandaran nuevos servicios como IoT masivo, movilidad conectada o 5G SA, la evolucion natural del diseno pasaria por small cells, mas espectro, beamforming, slicing y edge computing.",
        "",
        "## 9. Cumplimiento del enunciado",
        "",
        dataframe_to_markdown(compliance_table),
        "",
        "## 10. Referencias bibliograficas",
        "",
        "1. T. S. Rappaport, Wireless Communications: Principles and Practice, 2nd ed., Prentice Hall.",
        "2. A. Goldsmith, Wireless Communications, Cambridge University Press.",
        "3. S. Sesia, I. Toufik y M. Baker, LTE - The UMTS Long Term Evolution, Wiley.",
        "4. E. Dahlman, S. Parkvall y J. Skold, 5G NR: The Next Generation Wireless Access Technology, Academic Press.",
    ]
    return "\n".join(lines)


def build_annex_markdown(
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
    validation_table: pd.DataFrame,
) -> str:
    district_cov = district_coverage.iloc[0]
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_cov = festival_coverage.iloc[0]
    festival_cap = festival_capacity.iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]

    lines = [
        "# Operacion Nexo 5G/6G - Anexo de calculos",
        "",
        "## Formulas base",
        "",
        "- `N = -174 + 10 log10(B) + NF`",
        "- `Sens = N + SNRreq + Limpl`",
        "- `Lmax = Ptx + Gtx + Grx - Lotros - Sens`",
        "- `Auser = llamadas_por_hora * duracion_media_horas`",
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
        "",
        "## Validacion numerica de consistencia",
        "",
        dataframe_to_markdown(validation_table),
    ]
    return "\n".join(lines)


def build_defense_brief_markdown(district_capacity: pd.DataFrame, festival_splitting: pd.DataFrame) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]
    lines = [
        "# Operacion Nexo 5G/6G - Guion de defensa",
        "",
        "- El reto separa explicitamente los problemas de cobertura y capacidad.",
        f"- En el distrito financiero la recomendacion final es N={int(district_choice['reuse_factor_n'])} con tres sectores por sitio.",
        f"- En el festival la cobertura no es el problema dominante; la solucion es cell splitting hasta S{int(festival_choice['split_stage'])}.",
        "- El radio final siempre adopta el criterio mas restrictivo entre cobertura y capacidad.",
        "- Las decisiones quedan respaldadas por tablas, CSV, anexos y figuras dentro de la web estatica.",
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
    body {{ font-family: "Segoe UI", Arial, Helvetica, sans-serif; margin: 0; background: #eef2f6; color: #102a43; line-height: 1.65; overflow-wrap: anywhere; }}
    main {{ max-width: 1120px; margin: 32px auto; background: white; padding: 36px 42px; border: 1px solid #d9e2ec; border-radius: 12px; box-shadow: 0 8px 20px rgba(15,23,42,0.06); }}
    h1, h2, h3 {{ color: #102a43; }}
    p, li {{ color: #243b53; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0 1.4rem 0; font-size: 0.94rem; }}
    th, td {{ border: 1px solid #d9e2ec; padding: 0.55rem 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #edf3f8; color: #1f4e79; text-transform: uppercase; font-size: 0.78rem; letter-spacing: 0.04em; }}
    code {{ background: #f4f7fa; border: 1px solid #d9e2ec; padding: 0.12rem 0.28rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <main>{html_body}</main>
</body>
</html>
"""


def write_html_document(output_path: Path, document_title: str, markdown_text: str) -> None:
    output_path.write_text(build_html_document(document_title, markdown_text), encoding="utf-8")
