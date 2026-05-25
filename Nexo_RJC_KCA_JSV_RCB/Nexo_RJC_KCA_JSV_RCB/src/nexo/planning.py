import math

import pandas as pd

from .config import DistrictScenario, FestivalScenario, NetworkConfig


def thermal_noise_dbm(bandwidth_hz: float, noise_figure_db: float) -> float:
    if bandwidth_hz <= 0:
        raise ValueError("bandwidth_hz must be positive")
    return -174.0 + 10.0 * math.log10(bandwidth_hz) + noise_figure_db


def receiver_sensitivity_dbm(thermal_noise_value_dbm: float, snr_required_db: float, implementation_losses_db: float) -> float:
    return thermal_noise_value_dbm + snr_required_db + implementation_losses_db


def maximum_allowable_path_loss_db(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float,
    additional_losses_db: float,
    receiver_sensitivity_value_dbm: float,
) -> float:
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - additional_losses_db - receiver_sensitivity_value_dbm


def radius_from_log_path_loss_km(max_path_loss_db: float, intercept_db: float, slope_db: float) -> float:
    if slope_db <= 0:
        raise ValueError("slope_db must be positive")
    return 10.0 ** ((max_path_loss_db - intercept_db) / slope_db)


def traffic_per_user_erlang(calls_per_hour_per_user: float, holding_time_min: float) -> float:
    if calls_per_hour_per_user < 0 or holding_time_min < 0:
        raise ValueError("traffic inputs must be non-negative")
    return calls_per_hour_per_user * (holding_time_min / 60.0)


def traffic_density_erlang_km2(users_density_km2: float, traffic_per_user_value_erlang: float) -> float:
    if users_density_km2 < 0:
        raise ValueError("users_density_km2 must be non-negative")
    return users_density_km2 * traffic_per_user_value_erlang


def erlang_b_blocking(offered_traffic_erlang: float, channels: int) -> float:
    if offered_traffic_erlang < 0:
        raise ValueError("offered_traffic_erlang must be non-negative")
    if channels <= 0:
        raise ValueError("channels must be positive")

    blocking = 1.0
    for channel in range(1, channels + 1):
        blocking = (offered_traffic_erlang * blocking) / (channel + offered_traffic_erlang * blocking)
    return blocking


def inverse_erlang_b(channels: int, blocking_probability: float) -> float:
    if channels <= 0:
        raise ValueError("channels must be positive")
    if not 0.0 < blocking_probability < 1.0:
        raise ValueError("blocking_probability must be between 0 and 1")

    low = 0.0
    high = float(max(20, channels * 20))
    while erlang_b_blocking(high, channels) < blocking_probability:
        high *= 2.0

    for _ in range(80):
        mid = (low + high) / 2.0
        if erlang_b_blocking(mid, channels) > blocking_probability:
            high = mid
        else:
            low = mid
    return (low + high) / 2.0


def hexagon_area_km2(radius_km: float) -> float:
    if radius_km < 0:
        raise ValueError("radius_km must be non-negative")
    return 1.5 * math.sqrt(3.0) * radius_km**2


def hexagon_radius_from_area_km2(area_km2: float) -> float:
    if area_km2 < 0:
        raise ValueError("area_km2 must be non-negative")
    if area_km2 == 0:
        return 0.0
    return math.sqrt((2.0 * area_km2) / (3.0 * math.sqrt(3.0)))


def reuse_ratio(reuse_factor_n: int) -> float:
    if reuse_factor_n <= 0:
        raise ValueError("reuse_factor_n must be positive")
    return math.sqrt(3.0 * reuse_factor_n)


def reuse_distance_km(radius_km: float, reuse_factor_n: int) -> float:
    return radius_km * reuse_ratio(reuse_factor_n)


def estimated_sir_db(reuse_factor_n: int, path_loss_exponent: float, interferers: int) -> float:
    if path_loss_exponent <= 0:
        raise ValueError("path_loss_exponent must be positive")
    if interferers <= 0:
        raise ValueError("interferers must be positive")
    sir_linear = (reuse_ratio(reuse_factor_n) ** path_loss_exponent) / interferers
    return 10.0 * math.log10(sir_linear)


def site_count_for_area(target_area_km2: float, cell_area_km2: float) -> int:
    if cell_area_km2 <= 0:
        return 0
    return math.ceil(target_area_km2 / cell_area_km2)


def system_parameter_table(config: NetworkConfig = NetworkConfig()) -> pd.DataFrame:
    rows = [
        ("Frecuencia de operacion", f"{config.frequency_mhz:g} MHz", "Comun a ambos escenarios"),
        ("Ancho de banda", f"{config.bandwidth_mhz:g} MHz", "Se usa en el ruido termico"),
        ("Potencia TX BS", f"{config.tx_power_dbm:g} dBm", "Equivale a 20 W"),
        ("Ganancia antena TX", f"{config.tx_gain_dbi:g} dBi", "Antena de estacion base"),
        ("Ganancia antena RX", f"{config.rx_gain_dbi:g} dBi", "Terminal movil"),
        ("Perdidas adicionales", f"{config.additional_losses_db:g} dB", "Cables, conectores y margen"),
        ("Figura de ruido", f"{config.noise_figure_db:g} dB", "NF del receptor"),
        ("Perdidas de implementacion", f"{config.implementation_losses_db:g} dB", "Termino L_impl"),
        ("Grado de servicio", f"{config.blocking_probability:.2%}", "Objetivo de bloqueo para Erlang B"),
        ("Canales fisicos totales", f"{config.total_channels:d}", "Pool simplificado tipo PRB"),
    ]
    return pd.DataFrame(rows, columns=["parametro", "valor", "papel_ingenieril"])


def scenario_goal_table(
    district: DistrictScenario = DistrictScenario(),
    festival: FestivalScenario = FestivalScenario(),
) -> pd.DataFrame:
    rows = [
        (
            "Escenario A",
            "Distrito financiero urbano denso",
            f"L_p = {district.propagation_intercept_db:.0f} + {district.propagation_slope_db:.0f} log10(d)",
            f"{district.users_density_km2:g} usuarios activos/km2",
            "3 sectores por sitio y comparacion N = 3, 4, 7",
        ),
        (
            "Escenario B",
            "Festival temporal en explanada abierta",
            f"L_p = {festival.propagation_intercept_db:.0f} + {festival.propagation_slope_db:.0f} log10(d)",
            f"{festival.users_density_km2:g} usuarios activos/km2",
            "Celdas omni y evaluacion de cell splitting",
        ),
    ]
    return pd.DataFrame(rows, columns=["escenario", "entorno", "modelo", "densidad", "diseno_requerido"])


def assumptions_table() -> pd.DataFrame:
    rows = [
        (
            "Area de referencia",
            "1 km2 en ambos escenarios",
            "El enunciado pide cuantas celdas harian falta para un area objetivo, pero no fija una superficie concreta. Se normaliza a 1 km2 para comparar densidad celular.",
        ),
        (
            "Reparto de canales en A",
            "floor(100 / N) por sitio y reparto uniforme entre 3 sectores",
            "Es la interpretacion mas simple y reproducible cuando el enunciado no define scheduler ni redistribucion dinamica.",
        ),
        (
            "Interferencia co-canal",
            "2 interferentes dominantes en sectorizado",
            "Aproximacion docente de primera corona para comparar N = 3, 4 y 7 sin introducir un simulador completo.",
        ),
        (
            "Geometria celular",
            "Hexagono regular equivalente",
            "Permite pasar de capacidad por area a radio celular y numero de sitios con una regla geometrica estandar.",
        ),
        (
            "Marco tecnologico",
            "Lectura LTE/5G sobre formulas simplificadas",
            "La memoria se redacta como red moderna aunque el dimensionamiento numerico se apoye en balance de enlace y Erlang B.",
        ),
    ]
    return pd.DataFrame(rows, columns=["supuesto", "valor_aplicado", "justificacion"])


def district_coverage_table(
    scenario: DistrictScenario = DistrictScenario(),
    config: NetworkConfig = NetworkConfig(),
) -> pd.DataFrame:
    noise_dbm = thermal_noise_dbm(config.bandwidth_hz, config.noise_figure_db)
    sensitivity_dbm = receiver_sensitivity_dbm(noise_dbm, scenario.snr_required_db, config.implementation_losses_db)
    max_path_loss_db = maximum_allowable_path_loss_db(
        config.tx_power_dbm,
        config.tx_gain_dbi,
        config.rx_gain_dbi,
        config.additional_losses_db,
        sensitivity_dbm,
    )
    coverage_radius_km = radius_from_log_path_loss_km(
        max_path_loss_db,
        scenario.propagation_intercept_db,
        scenario.propagation_slope_db,
    )
    user_traffic_erlang = traffic_per_user_erlang(scenario.calls_per_hour_per_user, scenario.holding_time_min)
    density_traffic_erlang = traffic_density_erlang_km2(scenario.users_density_km2, user_traffic_erlang)

    return pd.DataFrame(
        [
            {
                "scenario": "A_distrito_financiero",
                "thermal_noise_dbm": noise_dbm,
                "receiver_sensitivity_dbm": sensitivity_dbm,
                "max_path_loss_db": max_path_loss_db,
                "coverage_radius_km": coverage_radius_km,
                "traffic_per_user_erlang": user_traffic_erlang,
                "traffic_density_erlang_km2": density_traffic_erlang,
                "target_area_km2": scenario.target_area_km2,
                "propagation_model": f"L_p = {scenario.propagation_intercept_db:.0f} + {scenario.propagation_slope_db:.0f} log10(d)",
                "snr_required_db": scenario.snr_required_db,
            }
        ]
    )


def district_capacity_table(
    coverage_table: pd.DataFrame,
    scenario: DistrictScenario = DistrictScenario(),
    config: NetworkConfig = NetworkConfig(),
) -> pd.DataFrame:
    coverage_radius_km = float(coverage_table.iloc[0]["coverage_radius_km"])
    traffic_density = float(coverage_table.iloc[0]["traffic_density_erlang_km2"])
    rows = []

    for reuse_factor in scenario.reuse_factors:
        channels_per_site = max(config.total_channels // reuse_factor, 1)
        channels_per_sector = max(channels_per_site // scenario.sectors_per_site, 1)
        sector_capacity = inverse_erlang_b(channels_per_sector, config.blocking_probability)
        site_capacity = sector_capacity * scenario.sectors_per_site
        capacity_area = site_capacity / traffic_density if traffic_density else math.inf
        capacity_radius = hexagon_radius_from_area_km2(capacity_area)
        design_radius = min(coverage_radius_km, capacity_radius)
        design_area = hexagon_area_km2(design_radius)
        sectorized_sir = estimated_sir_db(reuse_factor, scenario.path_loss_exponent, interferers=2)

        rows.append(
            {
                "reuse_factor_n": reuse_factor,
                "reuse_ratio_d_over_r": reuse_ratio(reuse_factor),
                "reuse_distance_km": reuse_distance_km(design_radius, reuse_factor),
                "channels_per_site": channels_per_site,
                "channels_per_sector": channels_per_sector,
                "sector_capacity_erlang": sector_capacity,
                "site_capacity_erlang": site_capacity,
                "capacity_area_km2": capacity_area,
                "capacity_radius_km": capacity_radius,
                "coverage_radius_km": coverage_radius_km,
                "design_radius_km": design_radius,
                "design_area_km2": design_area,
                "sectorized_sir_db": sectorized_sir,
                "sir_margin_db": sectorized_sir - scenario.snr_required_db,
                "limiting_factor": "capacity" if capacity_radius < coverage_radius_km else "coverage",
                "sites_for_target_area": site_count_for_area(scenario.target_area_km2, design_area),
            }
        )

    table = pd.DataFrame(rows).sort_values("reuse_factor_n").reset_index(drop=True)
    feasible = table[table["sectorized_sir_db"] >= scenario.snr_required_db]
    recommended_n = int(feasible.iloc[0]["reuse_factor_n"]) if not feasible.empty else int(table.iloc[0]["reuse_factor_n"])
    table["recommended"] = table["reuse_factor_n"].eq(recommended_n)
    return table


def festival_coverage_table(
    scenario: FestivalScenario = FestivalScenario(),
    config: NetworkConfig = NetworkConfig(),
) -> pd.DataFrame:
    noise_dbm = thermal_noise_dbm(config.bandwidth_hz, config.noise_figure_db)
    sensitivity_dbm = receiver_sensitivity_dbm(noise_dbm, scenario.snr_required_db, config.implementation_losses_db)
    max_path_loss_db = maximum_allowable_path_loss_db(
        config.tx_power_dbm,
        config.tx_gain_dbi,
        config.rx_gain_dbi,
        config.additional_losses_db,
        sensitivity_dbm,
    )
    coverage_radius_km = radius_from_log_path_loss_km(
        max_path_loss_db,
        scenario.propagation_intercept_db,
        scenario.propagation_slope_db,
    )
    user_traffic_erlang = traffic_per_user_erlang(scenario.calls_per_hour_per_user, scenario.holding_time_min)
    density_traffic_erlang = traffic_density_erlang_km2(scenario.users_density_km2, user_traffic_erlang)

    return pd.DataFrame(
        [
            {
                "scenario": "B_festival_global",
                "thermal_noise_dbm": noise_dbm,
                "receiver_sensitivity_dbm": sensitivity_dbm,
                "max_path_loss_db": max_path_loss_db,
                "coverage_radius_km": coverage_radius_km,
                "traffic_per_user_erlang": user_traffic_erlang,
                "traffic_density_erlang_km2": density_traffic_erlang,
                "target_area_km2": scenario.target_area_km2,
                "propagation_model": f"L_p = {scenario.propagation_intercept_db:.0f} + {scenario.propagation_slope_db:.0f} log10(d)",
                "snr_required_db": scenario.snr_required_db,
            }
        ]
    )


def festival_capacity_table(
    coverage_table: pd.DataFrame,
    scenario: FestivalScenario = FestivalScenario(),
    config: NetworkConfig = NetworkConfig(),
) -> pd.DataFrame:
    coverage_radius_km = float(coverage_table.iloc[0]["coverage_radius_km"])
    traffic_density = float(coverage_table.iloc[0]["traffic_density_erlang_km2"])
    cell_capacity = inverse_erlang_b(config.total_channels, config.blocking_probability)
    capacity_area = cell_capacity / traffic_density if traffic_density else math.inf
    capacity_radius = hexagon_radius_from_area_km2(capacity_area)
    design_radius = min(coverage_radius_km, capacity_radius)
    design_area = hexagon_area_km2(design_radius)

    return pd.DataFrame(
        [
            {
                "channels_per_cell": config.total_channels,
                "cell_capacity_erlang": cell_capacity,
                "capacity_area_km2": capacity_area,
                "capacity_radius_km": capacity_radius,
                "coverage_radius_km": coverage_radius_km,
                "design_radius_km": design_radius,
                "design_area_km2": design_area,
                "limiting_factor": "capacity" if capacity_radius < coverage_radius_km else "coverage",
                "sites_for_target_area": site_count_for_area(scenario.target_area_km2, design_area),
            }
        ]
    )


def festival_splitting_table(
    coverage_table: pd.DataFrame,
    scenario: FestivalScenario = FestivalScenario(),
    config: NetworkConfig = NetworkConfig(),
) -> pd.DataFrame:
    base_radius = float(coverage_table.iloc[0]["coverage_radius_km"])
    traffic_density = float(coverage_table.iloc[0]["traffic_density_erlang_km2"])
    user_traffic = float(coverage_table.iloc[0]["traffic_per_user_erlang"])
    cell_capacity = inverse_erlang_b(config.total_channels, config.blocking_probability)
    rows = []
    recommended_stage = None

    for stage in range(scenario.max_split_stage + 1):
        radius = base_radius / (2**stage)
        area = hexagon_area_km2(radius)
        capacity_density = cell_capacity / area if area else math.inf
        supported_users = capacity_density / user_traffic if user_traffic else math.inf
        meets_demand = capacity_density >= traffic_density
        if meets_demand and recommended_stage is None:
            recommended_stage = stage

        rows.append(
            {
                "split_stage": stage,
                "radius_km": radius,
                "area_km2": area,
                "cells_per_original_footprint": 4**stage,
                "capacity_density_erlang_km2": capacity_density,
                "supported_users_km2": supported_users,
                "demand_users_km2": scenario.users_density_km2,
                "meets_demand": meets_demand,
                "sites_for_target_area": site_count_for_area(scenario.target_area_km2, area),
            }
        )

    if recommended_stage is None:
        recommended_stage = scenario.max_split_stage

    table = pd.DataFrame(rows)
    table["recommended"] = table["split_stage"].eq(recommended_stage)
    return table
