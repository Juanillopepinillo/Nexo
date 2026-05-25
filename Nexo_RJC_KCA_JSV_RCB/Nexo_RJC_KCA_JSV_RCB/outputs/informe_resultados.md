# Operacion Nexo 5G/6G - Informe tecnico

## Resumen

Este informe dimensiona una red movil moderna para Nueva Pangea en dos escenarios de alta demanda: un distrito financiero urbano y un festival temporal masivo.
El escenario A queda limitado por capacidad y recomienda N=4 con tres sectores por sitio.
El escenario B queda gobernado por densidad de trafico y exige cell splitting hasta la etapa S4.

## 1. Introduccion

Una red movil moderna no se dimensiona solo por cobertura. En una ciudad inteligente importa separar alcance radio, carga de trafico e interferencia para tomar decisiones defendibles.

## 2. Estado del arte

LTE y 5G basan su eficiencia en OFDMA, planificacion dinamica y adaptacion MCS. Aun asi, el dimensionamiento inicial sigue dependiendo del balance de enlace, de los modelos de propagacion y de la teoria de trafico.

## 3. Metodologia

La cadena de calculo replica el enunciado: ruido termico, sensibilidad, perdida maxima admisible, radio por cobertura, trafico por usuario, densidad de trafico, capacidad Erlang B y radio por capacidad.

### 3.1 Parametros base

| parametro | valor | papel_ingenieril |
| --- | --- | --- |
| Frecuencia de operacion | 1800 MHz | Comun a ambos escenarios |
| Ancho de banda | 20 MHz | Se usa en el ruido termico |
| Potencia TX BS | 43 dBm | Equivale a 20 W |
| Ganancia antena TX | 18 dBi | Antena de estacion base |
| Ganancia antena RX | 0 dBi | Terminal movil |
| Perdidas adicionales | 12 dB | Cables, conectores y margen |
| Figura de ruido | 7 dB | NF del receptor |
| Perdidas de implementacion | 2 dB | Termino L_impl |
| Grado de servicio | 2.00% | Objetivo de bloqueo para Erlang B |
| Canales fisicos totales | 100 | Pool simplificado tipo PRB |

### 3.2 Objetivos por escenario

| escenario | entorno | modelo | densidad | diseno_requerido |
| --- | --- | --- | --- | --- |
| Escenario A | Distrito financiero urbano denso | L_p = 135 + 35 log10(d) | 2500 usuarios activos/km2 | 3 sectores por sitio y comparacion N = 3, 4, 7 |
| Escenario B | Festival temporal en explanada abierta | L_p = 120 + 30 log10(d) | 8000 usuarios activos/km2 | Celdas omni y evaluacion de cell splitting |

## 4. Resultados

### 4.1 Cobertura

| scenario | thermal_noise_dbm | receiver_sensitivity_dbm | max_path_loss_db | coverage_radius_km | traffic_per_user_erlang | traffic_density_erlang_km2 | target_area_km2 | propagation_model | snr_required_db |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_distrito_financiero | -93.9897 | -76.9897 | 125.99 | 0.552793 | 0.1 | 250 | 1 | L_p = 135 + 35 log10(d) | 15 |
| B_festival_global | -93.9897 | -86.9897 | 135.99 | 3.41185 | 0.0833333 | 666.667 | 1 | L_p = 120 + 30 log10(d) | 5 |

### 4.2 Capacidad en el distrito financiero

| reuse_factor_n | reuse_ratio_d_over_r | reuse_distance_km | channels_per_site | channels_per_sector | sector_capacity_erlang | site_capacity_erlang | capacity_area_km2 | capacity_radius_km | coverage_radius_km | design_radius_km | design_area_km2 | sectorized_sir_db | sir_margin_db | limiting_factor | sites_for_target_area | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 3 | 0.492776 | 33 | 11 | 5.84153 | 17.5246 | 0.0700984 | 0.164259 | 0.552793 | 0.164259 | 0.0700984 | 13.6889 | -1.31106 | capacity | 15 | No |
| 4 | 3.4641 | 0.448365 | 25 | 8 | 3.62705 | 10.8812 | 0.0435246 | 0.129432 | 0.552793 | 0.129432 | 0.0435246 | 15.8754 | 0.875372 | capacity | 23 | Si |
| 7 | 4.58258 | 0.32549 | 14 | 4 | 1.09226 | 3.27678 | 0.0131071 | 0.0710277 | 0.552793 | 0.0710277 | 0.0131071 | 20.1285 | 5.12854 | capacity | 77 | No |

### 4.3 Capacidad y splitting en el festival

| channels_per_cell | cell_capacity_erlang | capacity_area_km2 | capacity_radius_km | coverage_radius_km | design_radius_km | design_area_km2 | limiting_factor | sites_for_target_area |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100 | 87.972 | 0.131958 | 0.225368 | 3.41185 | 0.225368 | 0.131958 | capacity | 8 |

| split_stage | radius_km | area_km2 | cells_per_original_footprint | capacity_density_erlang_km2 | supported_users_km2 | demand_users_km2 | meets_demand | sites_for_target_area | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 3.41185 | 30.2435 | 1 | 2.90879 | 34.9055 | 8000 | No | 1 | No |
| 1 | 1.70593 | 7.56087 | 4 | 11.6352 | 139.622 | 8000 | No | 1 | No |
| 2 | 0.852963 | 1.89022 | 16 | 46.5407 | 558.488 | 8000 | No | 1 | No |
| 3 | 0.426481 | 0.472555 | 64 | 186.163 | 2233.95 | 8000 | No | 3 | No |
| 4 | 0.213241 | 0.118139 | 256 | 744.65 | 8935.81 | 8000 | Si | 9 | Si |
| 5 | 0.10662 | 0.0295347 | 1024 | 2978.6 | 35743.2 | 8000 | Si | 34 | No |
| 6 | 0.0533102 | 0.00738366 | 4096 | 11914.4 | 142973 | 8000 | Si | 136 | No |

## 5. Discusion

El radio por cobertura del distrito financiero es 0.553 km, pero el radio de diseno recomendado cae a 0.129 km por la carga de trafico.
En el festival la diferencia es todavia mayor: la cobertura teorica alcanza 3.412 km mientras que la capacidad sin splitting solo sostiene 0.225 km.

## 6. Supuestos de trazabilidad

| supuesto | valor_aplicado | justificacion |
| --- | --- | --- |
| Area de referencia | 1 km2 en ambos escenarios | El enunciado pide cuantas celdas harian falta para un area objetivo, pero no fija una superficie concreta. Se normaliza a 1 km2 para comparar densidad celular. |
| Reparto de canales en A | floor(100 / N) por sitio y reparto uniforme entre 3 sectores | Es la interpretacion mas simple y reproducible cuando el enunciado no define scheduler ni redistribucion dinamica. |
| Interferencia co-canal | 2 interferentes dominantes en sectorizado | Aproximacion docente de primera corona para comparar N = 3, 4 y 7 sin introducir un simulador completo. |
| Geometria celular | Hexagono regular equivalente | Permite pasar de capacidad por area a radio celular y numero de sitios con una regla geometrica estandar. |
| Marco tecnologico | Lectura LTE/5G sobre formulas simplificadas | La memoria se redacta como red moderna aunque el dimensionamiento numerico se apoye en balance de enlace y Erlang B. |

## 7. Conclusiones

La solucion adoptada para el escenario A es N=4 con tres sectores por sitio, porque es la primera opcion que cumple el umbral radio con la mayor capacidad posible.
La solucion adoptada para el escenario B es cell splitting hasta S4, porque la densidad de usuarios domina claramente sobre la cobertura.

### 7.1 Nueva Pangea 2030

Si la densidad creciera, la evolucion natural del diseno pasaria por small cells, mas espectro, beamforming, slicing y edge computing.