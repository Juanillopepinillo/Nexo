from __future__ import annotations

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


def _render_figure_card(image_path: str, title: str, subtitle: str) -> str:
    return f"""
    <article class=\"figure-card\">
      <div class=\"section-heading compact\">
        <h3>{html_escape(title)}</h3>
        <p>{html_escape(subtitle)}</p>
      </div>
      <img src=\"{html_escape(image_path)}\" alt=\"{html_escape(title)}\" loading=\"lazy\">
    </article>
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


def build_static_dashboard_html(
    system_table: pd.DataFrame,
    scenario_table: pd.DataFrame,
    assumptions_table: pd.DataFrame,
    district_coverage: pd.DataFrame,
    district_capacity: pd.DataFrame,
    festival_coverage: pd.DataFrame,
    festival_capacity: pd.DataFrame,
    festival_splitting: pd.DataFrame,
) -> str:
    district_choice = district_capacity.loc[district_capacity["recommended"]].iloc[0]
    festival_choice = festival_splitting.loc[festival_splitting["recommended"]].iloc[0]
    festival_cap = festival_capacity.iloc[0]
    build_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    hero_metrics = "\n".join(
        [
            _render_metric("Radio por cobertura A", f"{_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km", "Distrito financiero urbano"),
            _render_metric("Reuso recomendado", f"N={int(district_choice['reuse_factor_n'])}", "Primera opcion que supera el umbral radio"),
            _render_metric("Radio por cobertura B", f"{_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km", "Festival en explanada abierta"),
            _render_metric("Split recomendado", f"S{int(festival_choice['split_stage'])}", "Necesario para absorber la densidad"),
        ]
    )

    summary_bullets = _render_bullet_list(
        [
            f"Escenario A: el radio de cobertura es {_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km, pero la capacidad obliga a bajar hasta {_format_number(float(district_choice['design_radius_km']), 3)} km.",
            f"Escenario A: N={int(district_choice['reuse_factor_n'])} equilibra mejor capacidad e interferencia con SIR de {_format_number(float(district_choice['sectorized_sir_db']), 2)} dB.",
            f"Escenario B: la cobertura teorica llega a {_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km, mientras que la capacidad sin splitting solo sostiene {_format_number(float(festival_cap['capacity_radius_km']), 3)} km.",
            f"Escenario B: la primera etapa viable es S{int(festival_choice['split_stage'])}, con {int(festival_choice['sites_for_target_area'])} celdas equivalentes por km2.",
        ]
    )

    method_bullets = _render_bullet_list(
        [
            "Se calcula ruido termico, sensibilidad y perdida maxima admisible antes de despejar el radio por cobertura.",
            "La carga de trafico se modela con Erlang B a 2% de bloqueo, separando distrito sectorizado y festival omnidireccional.",
            "El radio final de diseno siempre adopta el criterio mas restrictivo entre cobertura y capacidad.",
        ]
    )

    methodology_table = _select_and_rename_columns(
        system_table,
        [("parametro", "Parametro"), ("valor", "Valor"), ("papel_ingenieril", "Lectura ingenieril")],
    )
    scenario_overview_table = _select_and_rename_columns(
        scenario_table,
        [("escenario", "Escenario"), ("entorno", "Entorno"), ("modelo", "Modelo"), ("densidad", "Densidad"), ("diseno_requerido", "Diseno requerido")],
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
            ("channels_per_site", "Canales/sitio"),
            ("channels_per_sector", "Canales/sector"),
            ("site_capacity_erlang", "Capacidad sitio (Erl)"),
            ("capacity_radius_km", "Radio capacidad (km)"),
            ("design_radius_km", "Radio diseno (km)"),
            ("sectorized_sir_db", "SIR sectorizada (dB)"),
            ("sir_margin_db", "Margen SIR (dB)"),
            ("sites_for_target_area", "Sitios por 1 km2"),
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
            ("channels_per_cell", "Canales/celda"),
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

    district_figures = "\n".join(
        [
            _render_figure_card("assets/figures/escenario_a_balance_enlace.png", "Balance de enlace del distrito", "Visualiza potencia, ganancias y perdida maxima admisible del escenario urbano."),
            _render_figure_card("assets/figures/escenario_a_radios.png", "Cobertura frente a capacidad", "Comparativa del radio teorico y del radio util bajo presion de trafico."),
            _render_figure_card("assets/figures/escenario_a_interferencia.png", "Trade-off de reuso N", "Muestra el equilibrio entre capacidad Erlang y SIR sectorizada para N = 3, 4 y 7."),
        ]
    )
    festival_figures = "\n".join(
        [
            _render_figure_card("assets/figures/escenario_b_balance_enlace.png", "Balance de enlace del festival", "El enlace es generoso en cobertura, pero eso no garantiza capacidad suficiente."),
            _render_figure_card("assets/figures/escenario_b_radios.png", "Radio por cobertura y capacidad", "La grafica deja clara la distancia entre la geometria radio y la demanda real."),
            _render_figure_card("assets/figures/escenario_b_cell_splitting.png", "Estrategia de cell splitting", "Se identifica la primera etapa que iguala o supera la densidad de usuarios exigida."),
        ]
    )

    download_cards = "\n".join(
        [
            _render_download_card("files/informe_resultados.html", "Informe tecnico web", "HTML", "Documento principal con desarrollo de metodologia, resultados y conclusiones."),
            _render_download_card("files/informe_resultados.md", "Informe tecnico editable", "MD", "Version ligera para revisar en GitHub o adaptar la memoria final."),
            _render_download_card("files/anexo_calculos.html", "Anexo de calculos", "HTML", "Secuencia numerica reproducible para defender cada formula."),
            _render_download_card("files/guion_defensa.html", "Guion de defensa", "HTML", "Resumen corto para exposicion oral del reto."),
            _render_download_card("files/escenario_a_capacidad.csv", "CSV escenario A", "CSV", "Tabla de reuso, capacidad, SIR y radio de diseno del distrito financiero."),
            _render_download_card("files/escenario_b_cell_splitting.csv", "CSV cell splitting", "CSV", "Tabla completa de etapas S0-S6 con capacidad por km2."),
            _render_download_card("src/nexo/main.py", "Codigo principal", "PY", "Punto de entrada para recalcular salidas y reconstruir la web."),
            _render_download_card("README.md", "README del paquete", "MD", "Instrucciones para abrir la pagina y regenerar todos los resultados."),
        ]
    )

    template = Template(
        """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Operacion Nexo 5G/6G | Dashboard tecnico</title>
  <meta name="description" content="Pagina web estatica del reto Operacion Nexo 5G/6G para Nueva Pangea.">
  <style>
    :root {
      color-scheme: dark;
      --bg: #0a0f1a;
      --bg-soft: #101726;
      --panel: rgba(15, 24, 40, 0.92);
      --panel-border: rgba(143, 92, 255, 0.22);
      --text: #edf2ff;
      --muted: #a6b1c7;
      --accent: #b794ff;
      --accent-strong: #8f5cff;
      --ok: #34d399;
      --shadow: 0 28px 60px rgba(0, 0, 0, 0.28);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background:
        radial-gradient(circle at top right, rgba(143, 92, 255, 0.25), transparent 32%),
        radial-gradient(circle at top left, rgba(52, 211, 153, 0.10), transparent 26%),
        linear-gradient(180deg, #060a12 0%, var(--bg) 48%, #091120 100%);
      color: var(--text);
      line-height: 1.6;
    }
    a { color: inherit; text-decoration: none; }
    img { width: 100%; display: block; border-radius: 18px; }
    .page { max-width: 1440px; margin: 0 auto; padding: 28px; }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 20;
      margin-bottom: 24px;
      backdrop-filter: blur(16px);
      background: rgba(6, 10, 18, 0.74);
      border: 1px solid rgba(183, 148, 255, 0.14);
      border-radius: 18px;
      padding: 16px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
      box-shadow: var(--shadow);
    }
    .brand strong { display: block; font-size: 1.02rem; letter-spacing: 0.08em; text-transform: uppercase; }
    .brand span { color: var(--muted); font-size: 0.92rem; }
    .topbar nav { display: flex; flex-wrap: wrap; gap: 10px; }
    .topbar nav a {
      color: var(--muted);
      border: 1px solid rgba(166, 177, 199, 0.18);
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.92rem;
    }
    .hero {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 24px;
      padding: 34px;
      border-radius: 28px;
      background: linear-gradient(135deg, rgba(15, 24, 40, 0.98), rgba(10, 15, 26, 0.95));
      border: 1px solid var(--panel-border);
      box-shadow: var(--shadow);
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-size: 0.78rem;
      color: var(--accent);
      margin-bottom: 14px;
    }
    .eyebrow::before {
      content: "";
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--ok);
      box-shadow: 0 0 18px rgba(52, 211, 153, 0.8);
    }
    h1 { margin: 0 0 14px; font-size: clamp(2.3rem, 4vw, 4.2rem); line-height: 1.02; }
    .hero p { margin: 0 0 16px; color: var(--muted); max-width: 74ch; }
    .hero-summary {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-top: 20px;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      align-content: start;
    }
    .metric-card, .panel, .figure-card, .table-card, .download-card {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 22px;
      box-shadow: var(--shadow);
    }
    .metric-card { padding: 20px; }
    .metric-label {
      display: block;
      margin-bottom: 10px;
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .metric-value { display: block; font-size: clamp(1.55rem, 2vw, 2.2rem); margin-bottom: 8px; }
    .metric-caption { margin: 0; color: var(--muted); font-size: 0.94rem; }
    .hero-summary .panel, .section-grid > .panel { padding: 22px; }
    .section-grid {
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      gap: 22px;
      margin-top: 26px;
    }
    .span-4 { grid-column: span 4; }
    .span-5 { grid-column: span 5; }
    .span-6 { grid-column: span 6; }
    .span-7 { grid-column: span 7; }
    .span-8 { grid-column: span 8; }
    .span-12 { grid-column: span 12; }
    .section-heading { margin-bottom: 16px; }
    .section-heading.compact { margin-bottom: 14px; }
    .section-heading h2, .section-heading h3 { margin: 0 0 8px; }
    .section-heading p { margin: 0; color: var(--muted); }
    .section-heading h2 { font-size: 1.55rem; }
    .section-heading h3 { font-size: 1.1rem; }
    .insight-list { margin: 0; padding-left: 18px; color: var(--text); }
    .insight-list li + li { margin-top: 10px; }
    .figure-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
    .figure-card { padding: 16px; }
    .table-card { padding: 22px; }
    .table-wrapper { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 720px; }
    th, td { padding: 12px 14px; border-bottom: 1px solid rgba(166, 177, 199, 0.12); text-align: left; vertical-align: top; }
    th { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); }
    td { color: #dfe8ff; font-size: 0.95rem; }
    tbody tr:hover { background: rgba(183, 148, 255, 0.05); }
    .download-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
    .download-card { padding: 22px; transition: transform 0.18s ease, border-color 0.18s ease; }
    .download-card:hover { transform: translateY(-3px); border-color: rgba(183, 148, 255, 0.35); }
    .download-type { display: inline-block; margin-bottom: 12px; padding: 6px 10px; border-radius: 999px; background: rgba(143, 92, 255, 0.16); color: var(--accent); font-size: 0.78rem; letter-spacing: 0.1em; text-transform: uppercase; }
    .download-card strong { display: block; margin-bottom: 8px; font-size: 1.04rem; }
    .download-card p { margin: 0 0 12px; color: var(--muted); }
    .download-link { color: var(--ok); font-weight: bold; }
    .footer-note { color: var(--muted); font-size: 0.92rem; text-align: center; margin-top: 28px; }
    .code-block {
      margin: 0;
      padding: 16px 18px;
      border-radius: 16px;
      background: rgba(5, 11, 22, 0.65);
      border: 1px solid rgba(183, 148, 255, 0.12);
      overflow-x: auto;
      color: #f5f7ff;
    }
    @media (max-width: 1180px) {
      .hero { grid-template-columns: 1fr; }
      .span-4, .span-5, .span-6, .span-7, .span-8 { grid-column: span 12; }
      .figure-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .download-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 760px) {
      .page { padding: 16px; }
      .topbar { position: static; flex-direction: column; align-items: flex-start; }
      .metric-grid, .hero-summary, .figure-grid, .download-grid { grid-template-columns: 1fr; }
      .hero { padding: 24px; }
      table { min-width: 640px; }
    }
  </style>
</head>
<body>
  <div class="page">
    <header class="topbar">
      <div class="brand">
        <strong>Operacion Nexo 5G/6G</strong>
        <span>Entrega estatica lista para GitHub, VS Code y apertura local</span>
      </div>
      <nav>
        <a href="#resumen">Resumen</a>
        <a href="#metodologia">Metodologia</a>
        <a href="#escenario-a">Escenario A</a>
        <a href="#escenario-b">Escenario B</a>
        <a href="#archivos">Archivos</a>
      </nav>
    </header>

    <section class="hero">
      <div>
        <div class="eyebrow">Nueva Pangea · red moderna comparativa</div>
        <h1>Diseno de red movil para un distrito financiero y un festival de alta densidad</h1>
        <p>
          Esta pagina adapta la estructura del proyecto de referencia a la casuistica de Operacion Nexo.
          La web resume el dimensionamiento por cobertura y por capacidad, el estudio de reutilizacion
          frecuencial y la evaluacion de cell splitting para una red orientada a contexto LTE/5G.
        </p>
        <p>
          Todo el contenido se puede abrir directamente desde el archivo <code>index.html</code>, sin backend,
          y queda acompasado con un paquete Python reproducible en <code>src/nexo/</code>.
        </p>
        <div class="hero-summary">
          <section class="panel">
            <div class="section-heading compact">
              <h3>Mensajes clave</h3>
              <p>Lo que debe sostener la memoria tecnica final.</p>
            </div>
            $summary_bullets
          </section>
          <section class="panel">
            <div class="section-heading compact">
              <h3>Metodo reproducible</h3>
              <p>Resumen de la cadena de calculo usada en el proyecto.</p>
            </div>
            $method_bullets
          </section>
        </div>
      </div>
      <div class="metric-grid">
        $hero_metrics
      </div>
    </section>

    <section class="section-grid" id="resumen">
      <article class="panel span-5">
        <div class="section-heading">
          <h2>Figura resumen</h2>
          <p>Decision consolidada de diseno para ambos escenarios del reto.</p>
        </div>
        <img src="assets/figures/resumen_operacion_nexo.png" alt="Resumen de la solucion Operacion Nexo" loading="lazy">
      </article>
      <div class="span-7">
        $scenario_table_html
      </div>
    </section>

    <section class="section-grid" id="metodologia">
      <div class="span-6">
        $methodology_table_html
      </div>
      <div class="span-6">
        $assumptions_table_html
      </div>
      <article class="panel span-12">
        <div class="section-heading">
          <h2>Como regenerar la entrega</h2>
          <p>El codigo esta preparado para ejecutarse en local y rehacer tablas, figuras y documentos.</p>
        </div>
        <pre class="code-block">set PYTHONPATH=src
python -m nexo.main</pre>
      </article>
    </section>

    <section class="section-grid" id="escenario-a">
      <article class="panel span-4">
        <div class="section-heading">
          <h2>Escenario A · Distrito financiero</h2>
          <p>Entorno urbano denso con tres sectores por sitio y comparacion N = 3, 4 y 7.</p>
        </div>
        $district_notes
      </article>
      <article class="panel span-8">
        <div class="section-heading">
          <h2>Galeria del escenario A</h2>
          <p>Balance de enlace, radios de diseno y compromiso entre capacidad e interferencia.</p>
        </div>
        <div class="figure-grid">
          $district_figures
        </div>
      </article>
      <div class="span-12">
        $district_coverage_table_html
      </div>
      <div class="span-12">
        $district_capacity_table_html
      </div>
    </section>

    <section class="section-grid" id="escenario-b">
      <article class="panel span-4">
        <div class="section-heading">
          <h2>Escenario B · Festival global</h2>
          <p>Explanada abierta con densidad extrema de usuarios y evaluacion explicita de cell splitting.</p>
        </div>
        $festival_notes
      </article>
      <article class="panel span-8">
        <div class="section-heading">
          <h2>Galeria del escenario B</h2>
          <p>Comparativa entre cobertura teorica, capacidad real y etapas sucesivas de splitting.</p>
        </div>
        <div class="figure-grid">
          $festival_figures
        </div>
      </article>
      <div class="span-12">
        $festival_coverage_table_html
      </div>
      <div class="span-5">
        $festival_capacity_table_html
      </div>
      <div class="span-7">
        $festival_splitting_table_html
      </div>
    </section>

    <section class="section-grid" id="archivos">
      <article class="panel span-12">
        <div class="section-heading">
          <h2>Archivos incluidos</h2>
          <p>La entrega queda lista para abrir, revisar en GitHub y seguir editando en Visual Studio Code.</p>
        </div>
        <div class="download-grid">
          $download_cards
        </div>
      </article>
    </section>

    <p class="footer-note">
      Build generado el $build_time. La pagina principal funciona en local y se puede publicar directamente como sitio estatico.
    </p>
  </div>
</body>
</html>
"""
    )

    return template.substitute(
        hero_metrics=hero_metrics,
        summary_bullets=summary_bullets,
        method_bullets=method_bullets,
        scenario_table_html=_render_table(scenario_overview_table, "Escenarios del reto", "Vision comparativa de entorno, modelo de propagacion y requisito de diseno."),
        methodology_table_html=_render_table(methodology_table, "Parametros base", "Datos comunes usados en todos los calculos de cobertura y capacidad."),
        assumptions_table_html=_render_table(assumptions_view, "Supuestos declarados", "Hipotesis que fijan la trazabilidad y la reproducibilidad del trabajo."),
        district_notes=_render_bullet_list(
            [
                f"Ruido termico estimado: {_format_number(float(district_coverage.iloc[0]['thermal_noise_dbm']), 2)} dBm; sensibilidad: {_format_number(float(district_coverage.iloc[0]['receiver_sensitivity_dbm']), 2)} dBm.",
                f"El radio de cobertura resulta {_format_number(float(district_coverage.iloc[0]['coverage_radius_km']), 3)} km, pero la carga obliga a radios mucho menores.",
                f"N={int(district_choice['reuse_factor_n'])} es la primera opcion con margen SIR positivo: {_format_number(float(district_choice['sir_margin_db']), 2)} dB.",
                f"Para 1 km2 se necesitan {int(district_choice['sites_for_target_area'])} sitios equivalentes bajo el criterio final de capacidad.",
            ]
        ),
        district_figures=district_figures,
        district_coverage_table_html=_render_table(district_coverage_view, "Cobertura del distrito", "Ruido, sensibilidad y radio teorico de cobertura para el entorno urbano denso."),
        district_capacity_table_html=_render_table(district_capacity_view, "Capacidad y reutilizacion en A", "Comparativa completa de N = 3, 4 y 7 con su impacto sobre Erlang y SIR."),
        festival_notes=_render_bullet_list(
            [
                f"El radio por cobertura del festival alcanza {_format_number(float(festival_coverage.iloc[0]['coverage_radius_km']), 3)} km gracias a una propagacion mas favorable.",
                f"La capacidad sin splitting solo permite {_format_number(float(festival_cap['capacity_radius_km']), 3)} km, asi que el limite real es el trafico.",
                f"La etapa recomendada es S{int(festival_choice['split_stage'])}, con {_format_number(float(festival_choice['radius_km']), 3)} km de radio por celda.",
                f"Tras el splitting se soportan {_format_number(float(festival_choice['supported_users_km2']), 0)} usuarios/km2 frente a una demanda de {int(festival_choice['demand_users_km2'])} usuarios/km2.",
            ]
        ),
        festival_figures=festival_figures,
        festival_coverage_table_html=_render_table(festival_coverage_view, "Cobertura del festival", "Valores de enlace y radio teorico para la explanada abierta del escenario B."),
        festival_capacity_table_html=_render_table(festival_capacity_view, "Capacidad base en B", "Sin splitting, la capacidad agregada sigue siendo insuficiente para la densidad exigida."),
        festival_splitting_table_html=_render_table(festival_splitting_view, "Tabla de cell splitting", "Evolucion de radio, celdas equivalentes y usuarios soportados desde S0 hasta S6."),
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
) -> None:
    _copy_output_assets(outputs_root, project_root)
    html = build_static_dashboard_html(
        system_table=system_table,
        scenario_table=scenario_table,
        assumptions_table=assumptions_table,
        district_coverage=district_coverage,
        district_capacity=district_capacity,
        festival_coverage=festival_coverage,
        festival_capacity=festival_capacity,
        festival_splitting=festival_splitting,
    )
    (project_root / "index.html").write_text(html, encoding="utf-8")
