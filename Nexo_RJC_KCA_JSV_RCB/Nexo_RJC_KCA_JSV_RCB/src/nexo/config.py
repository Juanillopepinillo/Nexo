from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class NetworkConfig:
    frequency_mhz: float = 1800.0
    bandwidth_mhz: float = 20.0
    tx_power_dbm: float = 43.0
    tx_gain_dbi: float = 18.0
    rx_gain_dbi: float = 0.0
    additional_losses_db: float = 12.0
    noise_figure_db: float = 7.0
    implementation_losses_db: float = 2.0
    blocking_probability: float = 0.02
    total_channels: int = 100

    @property
    def bandwidth_hz(self) -> float:
        return self.bandwidth_mhz * 1e6


@dataclass(frozen=True)
class DistrictScenario:
    users_density_km2: float = 2500.0
    calls_per_hour_per_user: float = 3.0
    holding_time_min: float = 2.0
    snr_required_db: float = 15.0
    propagation_intercept_db: float = 135.0
    propagation_slope_db: float = 35.0
    path_loss_exponent: float = 3.5
    sectors_per_site: int = 3
    reuse_factors: Sequence[int] = (3, 4, 7)
    target_area_km2: float = 1.0


@dataclass(frozen=True)
class FestivalScenario:
    users_density_km2: float = 8000.0
    calls_per_hour_per_user: float = 5.0
    holding_time_min: float = 1.0
    snr_required_db: float = 5.0
    propagation_intercept_db: float = 120.0
    propagation_slope_db: float = 30.0
    path_loss_exponent: float = 3.0
    target_area_km2: float = 1.0
    max_split_stage: int = 6
