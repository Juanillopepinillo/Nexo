from pathlib import Path
import sys

if __name__ == "__main__" and __package__ is None:
    script_path = Path(__file__).resolve()
    sys.path.insert(0, str(script_path.parent.parent))
    __package__ = script_path.parent.name

from .config import DistrictScenario, FestivalScenario, NetworkConfig
from .planning import (
    assumptions_table,
    compliance_table,
    district_capacity_table,
    district_coverage_table,
    festival_capacity_table,
    festival_coverage_table,
    festival_splitting_table,
    numerical_validation_table,
    scenario_goal_table,
    system_parameter_table,
)
from .plots import (
    save_district_radii_plot,
    save_district_tradeoff_plot,
    save_festival_radii_plot,
    save_festival_splitting_plot,
    save_link_budget_plot,
    save_solution_summary_plot,
)
from .reporting import (
    build_annex_markdown,
    build_defense_brief_markdown,
    build_report_markdown,
    write_html_document,
)
from .site_builder import write_static_site


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    outputs_root = project_root / "outputs"
    figures_root = outputs_root / "figures"
    outputs_root.mkdir(parents=True, exist_ok=True)
    figures_root.mkdir(parents=True, exist_ok=True)

    config = NetworkConfig()
    district = DistrictScenario()
    festival = FestivalScenario()

    system_table = system_parameter_table(config)
    scenario_table = scenario_goal_table(district, festival)
    assumptions = assumptions_table()
    district_coverage = district_coverage_table(district, config)
    district_capacity = district_capacity_table(district_coverage, district, config)
    festival_coverage = festival_coverage_table(festival, config)
    festival_capacity = festival_capacity_table(festival_coverage, festival, config)
    festival_splitting = festival_splitting_table(festival_coverage, festival, config)
    compliance = compliance_table(district_capacity, festival_capacity, festival_splitting)
    validation = numerical_validation_table(
        district_coverage,
        district_capacity,
        festival_coverage,
        festival_capacity,
        festival_splitting,
    )

    system_table.to_csv(outputs_root / "parametros_sistema.csv", index=False)
    scenario_table.to_csv(outputs_root / "objetivos_escenario.csv", index=False)
    assumptions.to_csv(outputs_root / "supuestos.csv", index=False)
    district_coverage.to_csv(outputs_root / "escenario_a_cobertura.csv", index=False)
    district_capacity.to_csv(outputs_root / "escenario_a_capacidad.csv", index=False)
    festival_coverage.to_csv(outputs_root / "escenario_b_cobertura.csv", index=False)
    festival_capacity.to_csv(outputs_root / "escenario_b_capacidad.csv", index=False)
    festival_splitting.to_csv(outputs_root / "escenario_b_cell_splitting.csv", index=False)
    compliance.to_csv(outputs_root / "cumplimiento_enunciado.csv", index=False)
    validation.to_csv(outputs_root / "validacion_numerica.csv", index=False)

    save_link_budget_plot(district_coverage, figures_root / "escenario_a_balance_enlace.png", "Escenario A: balance de enlace y perdida admisible")
    save_district_radii_plot(district_capacity, district_coverage, figures_root / "escenario_a_radios.png")
    save_district_tradeoff_plot(district_capacity, district.snr_required_db, figures_root / "escenario_a_interferencia.png")
    save_link_budget_plot(festival_coverage, figures_root / "escenario_b_balance_enlace.png", "Escenario B: balance de enlace y perdida admisible")
    save_festival_radii_plot(festival_capacity, figures_root / "escenario_b_radios.png")
    save_festival_splitting_plot(festival_splitting, figures_root / "escenario_b_cell_splitting.png")
    save_solution_summary_plot(district_capacity, festival_capacity, festival_splitting, figures_root / "resumen_operacion_nexo.png")

    report_markdown = build_report_markdown(
        system_table,
        scenario_table,
        assumptions,
        district_coverage,
        district_capacity,
        festival_coverage,
        festival_capacity,
        festival_splitting,
        compliance,
        validation,
    )
    annex_markdown = build_annex_markdown(
        district_coverage,
        district_capacity,
        festival_coverage,
        festival_capacity,
        festival_splitting,
        validation,
    )
    defense_markdown = build_defense_brief_markdown(district_capacity, festival_splitting)

    (outputs_root / "informe_resultados.md").write_text(report_markdown, encoding="utf-8")
    (outputs_root / "anexo_calculos.md").write_text(annex_markdown, encoding="utf-8")
    (outputs_root / "guion_defensa.md").write_text(defense_markdown, encoding="utf-8")

    write_html_document(outputs_root / "informe_resultados.html", "Operacion Nexo 5G/6G - Informe tecnico", report_markdown)
    write_html_document(outputs_root / "anexo_calculos.html", "Operacion Nexo 5G/6G - Anexo de calculos", annex_markdown)
    write_html_document(outputs_root / "guion_defensa.html", "Operacion Nexo 5G/6G - Guion de defensa", defense_markdown)

    write_static_site(
        project_root=project_root,
        outputs_root=outputs_root,
        system_table=system_table,
        scenario_table=scenario_table,
        assumptions_table=assumptions,
        district_coverage=district_coverage,
        district_capacity=district_capacity,
        festival_coverage=festival_coverage,
        festival_capacity=festival_capacity,
        festival_splitting=festival_splitting,
        compliance_table=compliance,
        validation_table=validation,
    )

    print(f"Proyecto generado en: {project_root}")
    print(f"Pagina web lista en: {project_root / 'index.html'}")


if __name__ == "__main__":
    main()
