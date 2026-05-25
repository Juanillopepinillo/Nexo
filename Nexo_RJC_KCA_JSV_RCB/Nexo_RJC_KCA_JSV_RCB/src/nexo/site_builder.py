from __future__ import annotations

import base64
import shutil
from datetime import datetime
from html import escape as html_escape
from pathlib import Path
from string import Template

import pandas as pd


def _format_number(value: float, digits: int = 2) -> str:
    if digits == 0:
        return str(int(round(value)))
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def _format_cell(value: object) -> str:
    if pd.isna(value):
        return "-"
    if isinstance(value, bool):
        return "Si" if value else "No"
    if isinstance(value, float):
        return _format_number(value, 3)
    return str(value).replace("_", " ")


def _select_and_rename_columns(df: pd.DataFrame, columns: list[tuple[str, str]]) -> pd.DataFrame:
    selected = [(source, target) for source, target in columns if source in df.columns]
    if not selected:
        return df.copy()
    return df[[source for source, _ in selected]].rename(columns={source: target for source, target in selected})


def _render_metric(label: str, value: str, caption: str) -> str:
    return f"""
    <article class=\"metric-card\">
      <span class=\"metric-label\">{html_escape(label)}</span>
      <strong class=\"metric-value\">{html_escape(value)}</strong>
      <p class=\"metric-caption\">{html_escape(caption)}</p>
    </article>
    """


def _render_bullet_list(items: list[str]) -> str:
    bullets = "".join(f"<li>{html_escape(item)}</li>" for item in items if item)
    return f'<ul class="insight-list">{bullets}</ul>'


def _render_reference_list(items: list[str]) -> str:
    rows = "".join(f"<li>{html_escape(item)}</li>" for item in items if item)
    return f'<ol class="reference-list">{rows}</ol>'


def _render_ordered_list(items: list[str]) -> str:
    rows = "".join(f"<li>{html_escape(item)}</li>" for item in items if item)
    return f'<ol class="process-list">{rows}</ol>'


def _render_table(df: pd.DataFrame, title: str, subtitle: str) -> str:
    headers = "".join(f"<th>{html_escape(str(column))}</th>" for column in df.columns)
    rows = []
    for row in df.itertuples(index=False, name=None):
        cells = "".join(f"<td>{html_escape(_format_cell(value))}</td>" for value in row)
        rows.append(f"<tr>{cells}</tr>")
    return f"""
    <article class=\"table-card\">
      <div class=\"section-heading\">
        <h3>{html_escape(title)}</h3>
        <p>{html_escape(subtitle)}</p>
      </div>
      <div class=\"table-wrapper\">
        <table>
          <thead><tr>{headers}</tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </article>
    """


def _render_figure_card(image_src: str, title: str, caption: str) -> str:
    return f"""
    <figure class=\"figure-card\">
      <img src=\"{html_escape(image_src)}\" alt=\"{html_escape(title)}\" loading=\"lazy\">
      <figcaption>
        <strong>{html_escape(title)}</strong>
        <span>{html_escape(caption)}</span>
      </figcaption>
    </figure>
    """


def _render_download_card(href: str, label: str, file_type: str, description: str) -> str:
    return f"""
    <a class=\"download-card\" href=\"{html_escape(href)}\">
      <span class=\"download-type\">{html_escape(file_type)}</span>
      <strong>{html_escape(label)}</strong>
      <p>{html_escape(description)}</p>
      <span class=\"download-link\">Abrir archivo</span>
    </a>
    """


def _copy_output_assets(outputs_root: Path, project_root: Path) -> None:
    figures_src = outputs_root / "figures"
    figures_dst = project_root / "assets" / "figures"
    files_dst = project_root / "files"
    figures_dst.mkdir(parents=True, exist_ok=True)
    files_dst.mkdir(parents=True, exist_ok=True)

    if figures_src.exists():
        for figure_path in figures_src.glob("*.png"):
            shutil.copy2(figure_path, figures_dst / figure_path.name)

    for pattern in ("*.html", "*.md", "*.csv"):
        for file_path in outputs_root.glob(pattern):
            shutil.copy2(file_path, files_dst / file_path.name)


def _inline_png(image_path: Path) -> str:
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _build_inline_figure_map(outputs_root: Path) -> dict[str, str]:
    figures_dir = outputs_root / "figures"
    if not figures_dir.exists():
        return {}
    return {figure_path.name: _inline_png(figure_path) for figure_path in figures_dir.glob("*.png")}


def _figure_src(name: str, inline_figures: dict[str, str]) -> str:
    return inline_figures.get(name, f"assets/figures/{name}")


def build_static_dashboard_html(
    system_table: pd.DataFrame,
    scenario_table: pd.DataFrame,
    assumptions_table: pd.DataFrame,
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
    compliance_table: pd.DataFrame,
    validation_table: pd.DataFrame,
    inline_figures: dict[str, str],
) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]
    festival_cap = festival_capacity.iloc[0]
    build_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    hero_metrics = "\n".join(
        [
            _render_metric("Cobertura A", f"{_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km", "Radio teorico del distrito financiero"),
            _render_metric("Decision A", f"N={int(district_choice['reuse_factor_n'])}", "Reuso recomendado con 3 sectores"),
            _render_metric("Cobertura B", f"{_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km", "Radio teorico del festival global"),
            _render_metric("Decision B", f"S{int(festival_choice['split_stage'])}", "Primera etapa de splitting que satisface la demanda"),
        ]
    )

    intro_points = _render_bullet_list(
        [
            "Una red movil moderna debe equilibrar cobertura, capacidad e interferencia, especialmente en entornos urbanos densos y eventos temporales de alta concentracion de usuarios.",
            "El espectro radio es limitado, por lo que el territorio se divide en celulas y se reutilizan frecuencias con distancias de proteccion e hipotesis de interferencia controladas.",
            "El objetivo del trabajo es demostrar, con base fisica y matematica, que el radio final de diseno depende del criterio mas restrictivo y no solo del alcance del enlace.",
        ]
    )
    state_of_art_points = _render_bullet_list(
        [
            "LTE y 5G heredan de OFDMA la asignacion flexible de recursos y la adaptacion MCS, donde la robustez y la eficiencia espectral cambian segun la calidad del canal.",
            "Los modelos logaritmicos de propagacion siguen siendo la base del dimensionamiento preliminar, aunque en redes reales deban calibrarse con medidas y datos del entorno.",
            "La teoria de trafico de Erlang B sigue siendo una herramienta valida para estimar capacidad agregada y probabilidad de bloqueo en ejercicios de planificacion celular.",
        ]
    )
    summary_points = _render_bullet_list(
        [
            f"Escenario A: el radio por cobertura es {_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km, pero la capacidad obliga a bajar a {_format_number(float(district_choice['design_radius_km']), 3)} km.",
            f"Escenario A: N={int(district_choice['reuse_factor_n'])} es la primera opcion con margen radio positivo y mejor equilibrio capacidad-SIR.",
            f"Escenario B: la cobertura teorica es {_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km, mientras que la capacidad sin splitting solo admite {_format_number(float(festival_cap['capacity_radius_km']), 3)} km.",
            f"Escenario B: la primera etapa viable es S{int(festival_choice['split_stage'])}, con {int(festival_choice['sites_for_target_area'])} celdas equivalentes por km2.",
        ]
    )
    method_steps = _render_ordered_list(
        [
            "Calculo del ruido termico con N = -174 + 10 log10(B) + NF.",
            "Estimacion de sensibilidad con Sens = N + SNR requerida + perdidas de implementacion.",
            "Obtencion de la perdida maxima admisible a partir del balance de enlace.",
            "Despeje del radio por cobertura usando el modelo logaritmico de propagacion del escenario.",
            "Calculo de trafico por usuario, densidad de trafico y capacidad maxima con Erlang B al 2% de bloqueo.",
            "Comparacion final entre radio por cobertura y radio por capacidad para adoptar el criterio mas restrictivo.",
        ]
    )
    discussion_points = _render_bullet_list(
        [
            "En el distrito financiero domina la capacidad, no la cobertura. La sectorizacion mejora la reutilizacion, pero un N demasiado alto penaliza la capacidad agregada por sitio.",
            "El paso de N=3 a N=4 corrige el margen radio sin degradar tanto la capacidad como N=7, por eso es la primera opcion tecnicamente razonable.",
            f"La ganancia de sectorizacion para la opcion recomendada es de {_format_number(float(district_choice['sectorization_gain_db']), 2)} dB frente a una referencia omnidireccional, lo que refuerza la decision de sectorizar el despliegue urbano.",
            "En el festival, la propagacion favorable no resuelve la carga. El cuello de botella es la densidad de usuarios, de modo que la solucion pasa por cell splitting.",
            "El contraste entre ambos escenarios confirma la idea central del enunciado: cobertura y capacidad son problemas distintos y deben analizarse por separado.",
        ]
    )
    conclusion_points = _render_bullet_list(
        [
            f"Solucion adoptada para el escenario A: N={int(district_choice['reuse_factor_n'])}, tres sectores por sitio y radio de diseno {_format_number(float(district_choice['design_radius_km']), 3)} km.",
            f"Solucion adoptada para el escenario B: cell splitting hasta S{int(festival_choice['split_stage'])}, con radio final {_format_number(float(festival_choice['radius_km']), 3)} km por celda.",
            "La evolucion futura del sistema pasaria por small cells, mas espectro, beamforming, slicing y edge computing si la densidad de usuarios siguiera creciendo.",
        ]
    )
    compliance_points = _render_bullet_list(
        [
            "La pagina incluye introduccion, estado del arte, metodologia, descripcion de escenarios, calculos, resultados, discusion y conclusiones.",
            "Se muestran tablas comparativas de radios por cobertura y capacidad, criterio limitante y numero de celdas equivalentes por km2.",
            "Se adjuntan anexo de calculos, informe web, guion de defensa, figuras y codigo reproducible para Visual Studio Code y GitHub.",
        ]
    )
    references_html = _render_reference_list(
        [
            "T. S. Rappaport, Wireless Communications: Principles and Practice, 2nd ed., Prentice Hall.",
            "A. Goldsmith, Wireless Communications, Cambridge University Press.",
            "S. Sesia, I. Toufik y M. Baker, LTE - The UMTS Long Term Evolution, Wiley.",
            "E. Dahlman, S. Parkvall y J. Skold, 5G NR: The Next Generation Wireless Access Technology, Academic Press.",
        ]
    )

    system_view = _select_and_rename_columns(
        system_table,
        [("parametro", "Parametro"), ("valor", "Valor"), ("papel_ingenieril", "Interpretacion")],
    )
    scenario_view = _select_and_rename_columns(
        scenario_table,
        [("escenario", "Escenario"), ("entorno", "Entorno"), ("modelo", "Modelo de propagacion"), ("densidad", "Densidad"), ("diseno_requerido", "Analisis requerido")],
    )
    assumptions_view = _select_and_rename_columns(
        assumptions_table,
        [("supuesto", "Supuesto"), ("valor_aplicado", "Valor aplicado"), ("justificacion", "Justificacion")],
    )
    district_coverage_view = _select_and_rename_columns(
        district_coverage,
        [
            ("scenario", "Escenario"),
            ("thermal_noise_dbm", "Ruido termico (dBm)"),
            ("receiver_sensitivity_dbm", "Sensibilidad (dBm)"),
            ("max_path_loss_db", "Lmax (dB)"),
            ("coverage_radius_km", "Radio cobertura (km)"),
            ("traffic_per_user_erlang", "Trafico usuario (Erl)"),
            ("traffic_density_erlang_km2", "Densidad trafico (Erl/km2)"),
        ],
    )
    district_capacity_view = _select_and_rename_columns(
        district_capacity,
        [
            ("reuse_factor_n", "N"),
            ("reuse_ratio_d_over_r", "D/R"),
            ("reuse_distance_km", "Distancia reuso (km)"),
            ("sectors_per_site", "Sectores por sitio"),
            ("channels_per_site", "Canales por sitio"),
            ("channels_per_sector", "Canales por sector"),
            ("site_capacity_erlang", "Capacidad sitio (Erl)"),
            ("capacity_radius_km", "Radio capacidad (km)"),
            ("design_radius_km", "Radio diseno (km)"),
            ("sectorized_sir_db", "SIR sectorizada (dB)"),
            ("omnidirectional_sir_db", "SIR omni (dB)"),
            ("sectorization_gain_db", "Ganancia sectorizacion (dB)"),
            ("sir_margin_db", "Margen SIR (dB)"),
            ("sites_for_target_area", "Sitios por 1 km2"),
            ("sectors_for_target_area", "Sectores por 1 km2"),
            ("recommended", "Recomendado"),
        ],
    )
    festival_coverage_view = _select_and_rename_columns(
        festival_coverage,
        [
            ("scenario", "Escenario"),
            ("thermal_noise_dbm", "Ruido termico (dBm)"),
            ("receiver_sensitivity_dbm", "Sensibilidad (dBm)"),
            ("max_path_loss_db", "Lmax (dB)"),
            ("coverage_radius_km", "Radio cobertura (km)"),
            ("traffic_per_user_erlang", "Trafico usuario (Erl)"),
            ("traffic_density_erlang_km2", "Densidad trafico (Erl/km2)"),
        ],
    )
    festival_capacity_view = _select_and_rename_columns(
        festival_capacity,
        [
            ("channels_per_cell", "Canales por celda"),
            ("cell_capacity_erlang", "Capacidad celda (Erl)"),
            ("capacity_radius_km", "Radio capacidad (km)"),
            ("coverage_radius_km", "Radio cobertura (km)"),
            ("design_radius_km", "Radio diseno (km)"),
            ("sites_for_target_area", "Celdas por 1 km2"),
            ("limiting_factor", "Factor limitante"),
        ],
    )
    festival_splitting_view = _select_and_rename_columns(
        festival_splitting,
        [
            ("split_stage", "Etapa"),
            ("radius_km", "Radio (km)"),
            ("area_km2", "Area (km2)"),
            ("cells_per_original_footprint", "Celdas equivalentes"),
            ("supported_users_km2", "Usuarios soportados/km2"),
            ("demand_users_km2", "Demanda usuarios/km2"),
            ("meets_demand", "Cumple demanda"),
            ("sites_for_target_area", "Celdas por 1 km2"),
            ("recommended", "Recomendado"),
        ],
    )
    compliance_view = _select_and_rename_columns(
        compliance_table,
        [
            ("bloque_enunciado", "Bloque del enunciado"),
            ("evidencia", "Evidencia"),
            ("cumple", "Cumple"),
            ("comentario", "Comentario"),
        ],
    )
    validation_view = _select_and_rename_columns(
        validation_table,
        [
            ("control", "Control"),
            ("resultado", "Resultado"),
            ("criterio", "Criterio"),
            ("valido", "Valido"),
        ],
    )

    summary_figure = _render_figure_card(
        _figure_src("resumen_operacion_nexo.png", inline_figures),
        "Figura resumen de decisiones de diseno",
        "Sintesis de las decisiones adoptadas en ambos escenarios, con reuso recomendado para el distrito financiero y etapa de cell splitting para el festival global.",
    )
    district_figures = "\n".join(
        [
            _render_figure_card(_figure_src("escenario_a_balance_enlace.png", inline_figures), "Escenario A. Balance de enlace", "Diagrama waterfall del presupuesto radio del distrito financiero y de la perdida maxima admisible del enlace."),
            _render_figure_card(_figure_src("escenario_a_radios.png", inline_figures), "Escenario A. Cobertura frente a capacidad", "Comparativa entre el radio teorico de cobertura y el radio util por capacidad para N = 3, 4 y 7."),
            _render_figure_card(_figure_src("escenario_a_interferencia.png", inline_figures), "Escenario A. Compromiso capacidad-SIR", "Relacion entre capacidad agregada por sitio y margen radio para justificar la seleccion del reuso final."),
        ]
    )
    festival_figures = "\n".join(
        [
            _render_figure_card(_figure_src("escenario_b_balance_enlace.png", inline_figures), "Escenario B. Balance de enlace", "Desglose del enlace radio en la explanada abierta antes de introducir la restriccion de capacidad."),
            _render_figure_card(_figure_src("escenario_b_radios.png", inline_figures), "Escenario B. Cobertura frente a capacidad", "Comparacion directa entre radio por cobertura y radio por capacidad sin aplicar todavia cell splitting."),
            _render_figure_card(_figure_src("escenario_b_cell_splitting.png", inline_figures), "Escenario B. Evolucion del cell splitting", "La primera etapa que satisface la densidad de usuarios del festival es S4, tal como exige el analisis comparativo."),
        ]
    )

    download_cards = "\n".join(
        [
            _render_download_card("files/informe_resultados.html", "Informe tecnico web", "HTML", "Documento principal con la estructura academica y los resultados del trabajo."),
            _render_download_card("files/informe_resultados.md", "Informe tecnico editable", "MD", "Version ligera para GitHub o para incorporar a una memoria final."),
            _render_download_card("files/anexo_calculos.html", "Anexo de calculos", "HTML", "Trazabilidad numerica paso a paso de ambos escenarios."),
            _render_download_card("files/guion_defensa.html", "Guion de defensa", "HTML", "Resumen corto para exposicion oral del reto."),
            _render_download_card("files/escenario_a_capacidad.csv", "CSV escenario A", "CSV", "Tabla completa de reuso, capacidad, SIR y radio de diseno del distrito financiero."),
            _render_download_card("files/escenario_b_cell_splitting.csv", "CSV escenario B", "CSV", "Secuencia S0-S6 con usuarios soportados, radios y celdas equivalentes."),
            _render_download_card("files/cumplimiento_enunciado.csv", "Cumplimiento del enunciado", "CSV", "Matriz explicita de evidencias para verificar que la entrega cubre lo pedido por la guia docente."),
            _render_download_card("files/validacion_numerica.csv", "Validacion numerica", "CSV", "Controles de consistencia para comprobar que los resultados cumplen las condiciones del modelo."),
            _render_download_card("src/nexo/main.py", "Codigo principal", "PY", "Punto de entrada para regenerar la web, las tablas y las figuras del proyecto."),
            _render_download_card("README.md", "README del proyecto", "MD", "Instrucciones de apertura local y recalculo desde Visual Studio Code."),
        ]
    )

    template = Template(
        """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Operacion Nexo 5G/6G | Informe web tecnico</title>
  <meta name="description" content="Informe web tecnico del reto Operacion Nexo 5G/6G para Nueva Pangea.">
  <style>
    :root {
      --page: #edf2f7;
      --paper: #ffffff;
      --ink: #102a43;
      --muted: #52606d;
      --line: #d9e2ec;
      --accent: #1f4e79;
      --accent-soft: #edf3f8;
      --ok: #0f766e;
      --shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: "Segoe UI", Arial, Helvetica, sans-serif;
      background: var(--page);
      color: var(--ink);
      line-height: 1.65;
      overflow-wrap: anywhere;
    }
    a { color: inherit; text-decoration: none; }
    img { max-width: 100%; height: auto; display: block; }
    code {
      background: #f4f7fa;
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 0.08rem 0.28rem;
      font-family: Consolas, "Courier New", monospace;
      font-size: 0.95em;
    }
    .page {
      max-width: 1480px;
      margin: 0 auto;
      padding: 24px;
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
      margin-bottom: 24px;
      padding: 14px 18px;
      background: rgba(255, 255, 255, 0.96);
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }
    .brand strong {
      display: block;
      font-size: 1rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .brand span { color: var(--muted); font-size: 0.92rem; }
    .topbar nav {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .topbar nav a {
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      font-size: 0.9rem;
      color: var(--muted);
      background: #fff;
      white-space: nowrap;
    }
    .hero,
    .section-block,
    .metric-card,
    .panel,
    .table-card,
    .figure-card,
    .download-card {
      min-width: 0;
    }
    .hero,
    .section-block {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
    }
    .hero {
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 24px;
      padding: 30px;
    }
    .eyebrow {
      display: inline-block;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.76rem;
      font-weight: 700;
      margin-bottom: 12px;
    }
    h1 {
      margin: 0 0 14px;
      font-size: clamp(2.1rem, 3.8vw, 3.4rem);
      line-height: 1.08;
    }
    h2, h3 { margin: 0 0 8px; }
    p { margin: 0 0 14px; color: var(--muted); }
    .hero-summary {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      align-content: start;
    }
    .metric-card {
      padding: 18px;
      background: #fff;
      border: 1px solid var(--line);
      border-left: 4px solid var(--accent);
      border-radius: 10px;
      box-shadow: var(--shadow);
    }
    .metric-label {
      display: block;
      margin-bottom: 8px;
      font-size: 0.76rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-weight: 700;
    }
    .metric-value {
      display: block;
      margin-bottom: 8px;
      font-size: 1.9rem;
      color: var(--ink);
    }
    .metric-caption { margin: 0; font-size: 0.94rem; }
    .panel-grid {
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 20px;
    }
    .col-4 { grid-column: span 4; }
    .col-5 { grid-column: span 5; }
    .col-6 { grid-column: span 6; }
    .col-7 { grid-column: span 7; }
    .col-8 { grid-column: span 8; }
    .col-12 { grid-column: span 12; }
    .section-block {
      margin-top: 24px;
      padding: 24px;
    }
    .panel,
    .table-card,
    .figure-card,
    .download-card {
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 10px;
      box-shadow: var(--shadow);
    }
    .panel,
    .table-card { padding: 20px; }
    .section-heading { margin-bottom: 14px; }
    .section-heading p { margin: 0; }
    .section-title {
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line);
    }
    .section-title h2 { font-size: 1.55rem; }
    .insight-list,
    .reference-list,
    .process-list {
      margin: 0;
      padding-left: 20px;
      color: var(--ink);
    }
    .insight-list li + li,
    .reference-list li + li,
    .process-list li + li { margin-top: 10px; }
    .process-list li,
    .reference-list li,
    .insight-list li { color: var(--ink); }
    .table-wrapper { overflow: auto; }
    table {
      width: 100%;
      min-width: 820px;
      border-collapse: collapse;
    }
    th, td {
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    td {
      color: var(--ink);
      font-size: 0.95rem;
    }
    tbody tr:hover { background: #fafcff; }
    .figure-stack {
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
    }
    .figure-card {
      margin: 0;
      padding: 18px;
    }
    .figure-card img {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }
    .figure-card figcaption {
      margin-top: 12px;
      display: grid;
      gap: 6px;
    }
    .figure-card strong {
      color: var(--ink);
      font-size: 1rem;
    }
    .figure-card span {
      color: var(--muted);
      font-size: 0.94rem;
    }
    .two-column-text {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }
    .formula-block {
      padding: 16px 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fbfd;
      color: var(--ink);
      font-family: Consolas, "Courier New", monospace;
      white-space: pre-wrap;
    }
    .download-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }
    .download-card {
      padding: 20px;
    }
    .download-type {
      display: inline-block;
      margin-bottom: 10px;
      padding: 5px 9px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 0.76rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-weight: 700;
    }
    .download-card strong {
      display: block;
      margin-bottom: 8px;
      font-size: 1rem;
      color: var(--ink);
    }
    .download-card p { margin: 0 0 12px; }
    .download-link {
      color: var(--ok);
      font-weight: 700;
    }
    .code-block {
      margin: 0;
      padding: 15px 16px;
      border-radius: 8px;
      background: #f7fafc;
      border: 1px solid var(--line);
      color: var(--ink);
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: Consolas, "Courier New", monospace;
    }
    .footer-note {
      color: var(--muted);
      font-size: 0.9rem;
      text-align: center;
      margin-top: 26px;
    }
    @media (max-width: 1180px) {
      .hero,
      .hero-summary,
      .two-column-text,
      .metric-grid,
      .download-grid {
        grid-template-columns: 1fr;
      }
      .col-4, .col-5, .col-6, .col-7, .col-8 { grid-column: span 12; }
    }
    @media (max-width: 760px) {
      .page { padding: 16px; }
      .topbar {
        position: static;
        flex-direction: column;
        align-items: flex-start;
      }
      .hero,
      .section-block { padding: 20px; }
      table { min-width: 680px; }
    }
  </style>
</head>
<body>
  <div class="page">
    <header class="topbar">
      <div class="brand">
        <strong>Operacion Nexo 5G/6G</strong>
        <span>Informe web tecnico para Nueva Pangea</span>
      </div>
      <nav>
        <a href="#introduccion">Introduccion</a>
        <a href="#metodologia">Metodologia</a>
        <a href="#escenarios">Escenarios</a>
        <a href="#escenario-a">Escenario A</a>
        <a href="#escenario-b">Escenario B</a>
        <a href="#conclusiones">Conclusiones</a>
        <a href="#cumplimiento">Cumplimiento</a>
        <a href="#entregables">Entregables</a>
      </nav>
    </header>

    <section class="hero">
      <div>
        <div class="eyebrow">Redes y Comunicaciones Moviles · Nueva Pangea</div>
        <h1>Dimensionamiento comparativo de una red movil moderna</h1>
        <p>
          Esta pagina presenta una solucion completa del reto <code>Operacion Nexo 5G/6G</code>, adaptada a una
          estructura de informe tecnico-profesional. El trabajo compara el comportamiento radio de un distrito financiero
          urbano de alta densidad y de un festival temporal con concentracion extrema de usuarios.
        </p>
        <p>
          Se separan explicitamente los problemas de cobertura, capacidad e interferencia, se justifica el criterio
          limitante en cada escenario y se deja trazabilidad numerica mediante tablas, anexos y figuras reproducibles.
        </p>
        <div class="hero-summary">
          <section class="panel">
            <div class="section-heading">
              <h3>Resumen ejecutivo</h3>
              <p>Lectura rapida de las decisiones de diseno mas importantes.</p>
            </div>
            $summary_points
          </section>
          <section class="panel">
            <div class="section-heading">
              <h3>Que entrega este proyecto</h3>
              <p>Salida estatica lista para Visual Studio Code y GitHub.</p>
            </div>
            $compliance_points
          </section>
        </div>
      </div>
      <div class="metric-grid">
        $hero_metrics
      </div>
    </section>

    <section class="section-block" id="introduccion">
      <div class="section-title">
        <h2>1. Introduccion y estado del arte</h2>
        <p>Contexto tecnico del problema y fundamentos teoricos que justifican el enfoque adoptado.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-6">
          <div class="section-heading">
            <h3>1.1 Introduccion</h3>
            <p>Planteamiento del reto y separacion entre cobertura y capacidad.</p>
          </div>
          $intro_points
        </section>
        <section class="panel col-6">
          <div class="section-heading">
            <h3>1.2 Estado del arte</h3>
            <p>OFDMA, adaptacion MCS, modelos de propagacion y capacidad de trafico.</p>
          </div>
          $state_of_art_points
        </section>
      </div>
    </section>

    <section class="section-block" id="metodologia">
      <div class="section-title">
        <h2>2. Metodologia</h2>
        <p>Secuencia reproducible de calculo, parametros base y supuestos declarados del trabajo.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-6">
          <div class="section-heading">
            <h3>2.1 Secuencia de calculo</h3>
            <p>Orden exacto seguido para reproducir los resultados del enunciado.</p>
          </div>
          $method_steps
          <div class="formula-block">N = -174 + 10 log10(B) + NF
Sens = N + SNRreq + Limpl
Pr = Ptx + Gtx + Grx - Lp - Lotros</div>
        </section>
        <div class="col-6">
          $system_table_html
        </div>
        <div class="col-12">
          $assumptions_table_html
        </div>
        <section class="panel col-12">
          <div class="section-heading">
            <h3>2.2 Ejecucion local</h3>
            <p>El paquete puede regenerarse en local para recalcular las tablas, las figuras y esta propia pagina.</p>
          </div>
          <pre class="code-block">set PYTHONPATH=src
python -m nexo.main</pre>
        </section>
      </div>
    </section>

    <section class="section-block" id="escenarios">
      <div class="section-title">
        <h2>3. Escenarios del reto</h2>
        <p>Comparativa de entorno, modelo de propagacion, densidad de usuarios y requisito de diseno.</p>
      </div>
      <div class="panel-grid">
        <div class="col-12">
          $scenario_table_html
        </div>
        <div class="col-12 figure-stack">
          $summary_figure
        </div>
      </div>
    </section>

    <section class="section-block" id="escenario-a">
      <div class="section-title">
        <h2>4. Escenario A. Distrito financiero</h2>
        <p>Dimensionamiento de un entorno urbano denso con tres sectores por sitio y comparacion de N = 3, 4 y 7.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-12">
          <div class="section-heading">
            <h3>4.1 Lectura tecnica</h3>
            <p>Interpretacion de cobertura, capacidad e interferencia en el escenario urbano.</p>
          </div>
          $district_notes
        </section>
        <section class="panel col-12">
          <div class="section-heading">
            <h3>4.2 Pruebas, calculos y simulaciones</h3>
            <p>Figuras a gran tamano para justificar el balance de enlace, el radio util y la eleccion del reuso final.</p>
          </div>
          <div class="figure-stack">
            $district_figures
          </div>
        </section>
        <div class="col-12">
          $district_coverage_table_html
        </div>
        <div class="col-12">
          $district_capacity_table_html
        </div>
      </div>
    </section>

    <section class="section-block" id="escenario-b">
      <div class="section-title">
        <h2>5. Escenario B. Festival global de innovacion</h2>
        <p>Analisis de una explanada abierta con altisima densidad de usuarios y evaluacion explicita de cell splitting.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-12">
          <div class="section-heading">
            <h3>5.1 Lectura tecnica</h3>
            <p>Interpretacion de la restriccion dominante y justificacion del cell splitting.</p>
          </div>
          $festival_notes
        </section>
        <section class="panel col-12">
          <div class="section-heading">
            <h3>5.2 Pruebas, calculos y simulaciones</h3>
            <p>Figuras a gran tamano para comparar cobertura, capacidad y evolucion de la subdivision celular.</p>
          </div>
          <div class="figure-stack">
            $festival_figures
          </div>
        </section>
        <div class="col-12">
          $festival_coverage_table_html
        </div>
        <div class="col-12">
          $festival_capacity_table_html
        </div>
        <div class="col-12">
          $festival_splitting_table_html
        </div>
      </div>
    </section>

    <section class="section-block" id="conclusiones">
      <div class="section-title">
        <h2>6. Resultados, discusion y conclusiones</h2>
        <p>Interpretacion comparativa de la casuistica, validacion de consistencia y respuesta final a la pregunta de diseno del enunciado.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-6">
          <div class="section-heading">
            <h3>6.1 Discusion</h3>
            <p>Comparacion razonada de los factores limitantes de ambos escenarios.</p>
          </div>
          $discussion_points
        </section>
        <section class="panel col-6">
          <div class="section-heading">
            <h3>6.2 Conclusiones</h3>
            <p>Decisiones finales de despliegue y proyeccion futura de la red.</p>
          </div>
          $conclusion_points
        </section>
        <div class="col-12">
          $validation_table_html
        </div>
      </div>
    </section>

    <section class="section-block" id="cumplimiento">
      <div class="section-title">
        <h2>7. Cumplimiento del enunciado</h2>
        <p>Matriz de evidencias para verificar que la entrega cubre los apartados y comprobaciones exigidos por la guia docente.</p>
      </div>
      <div class="panel-grid">
        <div class="col-12">
          $compliance_table_html
        </div>
      </div>
    </section>

    <section class="section-block" id="entregables">
      <div class="section-title">
        <h2>8. Referencias y entregables</h2>
        <p>Bibliografia minima de apoyo y archivos incluidos en la entrega final.</p>
      </div>
      <div class="panel-grid">
        <section class="panel col-5">
          <div class="section-heading">
            <h3>7.1 Referencias bibliograficas</h3>
            <p>Fuentes tecnicas adecuadas para fundamentar el marco teorico del trabajo.</p>
          </div>
          $references_html
        </section>
        <section class="panel col-7">
          <div class="section-heading">
            <h3>7.2 Archivos incluidos</h3>
            <p>Recursos listos para abrir en local, revisar en GitHub y continuar en Visual Studio Code.</p>
          </div>
          <div class="download-grid">
            $download_cards
          </div>
        </section>
      </div>
    </section>

    <p class="footer-note">Version generada el $build_time. Este <code>index.html</code> es autocontenido y mantiene las figuras embebidas para que sigan viendose al descargarlo desde GitHub.</p>
  </div>
</body>
</html>
"""
    )

    return template.substitute(
        hero_metrics=hero_metrics,
        intro_points=intro_points,
        state_of_art_points=state_of_art_points,
        summary_points=summary_points,
        method_steps=method_steps,
        discussion_points=discussion_points,
        conclusion_points=conclusion_points,
        compliance_points=compliance_points,
        references_html=references_html,
        system_table_html=_render_table(system_view, "Parametros base del sistema", "Magnitudes comunes utilizadas en todos los calculos de cobertura, capacidad e interferencia."),
        assumptions_table_html=_render_table(assumptions_view, "Supuestos declarados", "Hipotesis necesarias para mantener trazabilidad, reproducibilidad y coherencia entre tablas y figuras."),
        scenario_table_html=_render_table(scenario_view, "Comparativa de escenarios", "Entorno, propagacion, densidad de usuarios y requisito de diseno de los dos casos del reto."),
        summary_figure=summary_figure,
        district_notes=_render_bullet_list(
            [
                f"Ruido termico estimado: {_format_number(float(district_coverage.iloc[0]['thermal_noise_dbm']), 2)} dBm; sensibilidad del receptor: {_format_number(float(district_coverage.iloc[0]['receiver_sensitivity_dbm']), 2)} dBm.",
                f"El radio por cobertura es {_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km, pero el radio util de capacidad recomendado cae a {_format_number(float(district_choice['design_radius_km']), 3)} km.",
                f"La opcion final es N={int(district_choice['reuse_factor_n'])}, con SIR sectorizada de {_format_number(float(district_choice['sectorized_sir_db']), 2)} dB y margen de {_format_number(float(district_choice['sir_margin_db']), 2)} dB respecto al umbral requerido.",
                f"La sectorizacion aporta una mejora de {_format_number(float(district_choice['sectorization_gain_db']), 2)} dB frente a la referencia omnidireccional del mismo reuso.",
                f"Con este criterio, el area normalizada de 1 km2 exige {int(district_choice['sites_for_target_area'])} sitios equivalentes y {int(district_choice['sectors_for_target_area'])} sectores.",
            ]
        ),
        district_figures=district_figures,
        district_coverage_table_html=_render_table(district_coverage_view, "Cobertura en el escenario A", "Resultado del balance de enlace y radio teorico de cobertura en el distrito financiero."),
        district_capacity_table_html=_render_table(district_capacity_view, "Capacidad y reutilizacion en el escenario A", "Comparativa de N = 3, 4 y 7 bajo carga urbana densa y grado de servicio del 2%."),
        festival_notes=_render_bullet_list(
            [
                f"El radio por cobertura del festival alcanza {_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km gracias a una propagacion mas favorable y a una SNR requerida menor.",
                f"La capacidad sin splitting solo soporta {_format_number(float(festival_cap['capacity_radius_km']), 3)} km, por lo que la restriccion dominante es el trafico agregado y no la cobertura del enlace.",
                f"La primera etapa viable es S{int(festival_choice['split_stage'])}, con radio {_format_number(float(festival_choice['radius_km']), 3)} km por celda y {int(festival_choice['sites_for_target_area'])} celdas equivalentes por 1 km2.",
                f"En la etapa adoptada se soportan {_format_number(float(festival_choice['supported_users_km2']), 0)} usuarios/km2 frente a una demanda de {int(festival_choice['demand_users_km2'])} usuarios/km2.",
            ]
        ),
        festival_figures=festival_figures,
        festival_coverage_table_html=_render_table(festival_coverage_view, "Cobertura en el escenario B", "Magnitudes del enlace y radio teorico de cobertura para el festival global de innovacion."),
        festival_capacity_table_html=_render_table(festival_capacity_view, "Capacidad base del escenario B", "Sin subdivision celular, la capacidad agregada no satisface la densidad exigida en el festival."),
        festival_splitting_table_html=_render_table(festival_splitting_view, "Tabla de cell splitting", "Secuencia completa de subdivision celular desde S0 hasta S6 y criterio de seleccion final."),
        validation_table_html=_render_table(validation_view, "Validacion numerica de consistencia", "Controles que verifican que las decisiones recomendadas respetan las restricciones del modelo y del enunciado."),
        compliance_table_html=_render_table(compliance_view, "Matriz de cumplimiento", "Evidencias concretas que enlazan la entrega final con cada bloque exigido por la guia docente."),
        download_cards=download_cards,
        build_time=html_escape(build_time),
    )


def write_static_site(
    project_root: Path,
    outputs_root: Path,
    system_table: pd.DataFrame,
    scenario_table: pd.DataFrame,
    assumptions_table: pd.DataFrame,
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
    compliance_table: pd.DataFrame,
    validation_table: pd.DataFrame,
) -> None:
    _copy_output_assets(outputs_root, project_root)
    inline_figures = _build_inline_figure_map(outputs_root)
    html = build_static_dashboard_html(
        system_table=system_table,
        scenario_table=scenario_table,
        assumptions_table=assumptions_table,
        district_coverage=district_coverage,
        district_capacity=district_capacity,
        festival_coverage=festival_coverage,
        festival_capacity=festival_capacity,
        festival_splitting=festival_splitting,
        compliance_table=compliance_table,
        validation_table=validation_table,
        inline_figures=inline_figures,
    )
    (project_root / "index.html").write_text(html, encoding="utf-8")
