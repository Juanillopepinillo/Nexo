# Operacion Nexo 5G/6G - Informe tecnico

## Resumen

Este informe desarrolla el reto Operacion Nexo 5G/6G para Nueva Pangea comparando dos escenarios de alta demanda: un distrito financiero urbano de alta densidad y un festival temporal con congestion extrema de usuarios.
El escenario A queda limitado por capacidad y recomienda N=4 con tres sectores por sitio.
El escenario B queda gobernado por densidad de trafico y exige cell splitting hasta la etapa S4.

## 1. Introduccion

Las redes moviles modernas deben resolver simultaneamente problemas de cobertura, capacidad e interferencia. En una ciudad inteligente, la conectividad de un distrito financiero no se comporta igual que la de un evento temporal con gran afluencia de usuarios. Por eso el dimensionamiento celular no puede apoyarse en un unico radio de cobertura, sino en una comparacion explicita entre el alcance del enlace y la carga de trafico soportable.

El objetivo del trabajo es justificar, con base fisica y matematica, la solucion de red mas adecuada en cada escenario y defender por que el radio final de diseno debe adoptarse siempre como el criterio mas restrictivo entre cobertura y capacidad.

## 2. Estado del arte

La evolucion hacia LTE y 5G consolida OFDMA, planificacion flexible de recursos y adaptacion dinamica de MCS. En ese contexto, la robustez y la eficiencia espectral dependen directamente de la calidad del canal y del margen radio disponible. Aun asi, el dimensionamiento preliminar sigue descansando sobre herramientas clasicas: balance de enlace, modelos logaritmicos de propagacion y teoria de trafico.

Los modelos de propagacion permiten traducir una perdida maxima admisible en un radio equivalente de cobertura. Por su parte, Erlang B sigue siendo una herramienta valida para estimar capacidad agregada y probabilidad de bloqueo cuando se desea comparar alternativas de diseno bajo un grado de servicio fijado.

## 3. Metodologia

La metodologia replica el orden propuesto en la guia docente: ruido termico, sensibilidad, perdida maxima admisible, radio por cobertura, trafico por usuario, densidad de trafico, capacidad Erlang B y radio por capacidad. El criterio final adopta siempre el menor radio entre cobertura y capacidad.

### 3.1 Expresiones de referencia

- `N = -174 + 10 log10(B) + NF` para el ruido termico.
- `Sens = N + SNRreq + Limpl` para la sensibilidad de receptor.
- `Pr = Ptx + Gtx + Grx - Lp - Lotros` para el balance de enlace.
- `Auser = lambda * h` para el trafico por usuario en Erlangs.
- Inversion de Erlang B para obtener la capacidad maxima al 2% de bloqueo.

### 3.2 Parametros base

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

### 3.3 Objetivos por escenario

| escenario | entorno | modelo | densidad | diseno_requerido |
| --- | --- | --- | --- | --- |
| Escenario A | Distrito financiero urbano denso | L_p = 135 + 35 log10(d) | 2500 usuarios activos/km2 | 3 sectores por sitio y comparacion N = 3, 4, 7 |
| Escenario B | Festival temporal en explanada abierta | L_p = 120 + 30 log10(d) | 8000 usuarios activos/km2 | Celdas omni y evaluacion de cell splitting |

### 3.4 Supuestos de trazabilidad

| supuesto | valor_aplicado | justificacion |
| --- | --- | --- |
| Area de referencia | 1 km2 en ambos escenarios | El enunciado pide cuantas celdas harian falta para un area objetivo, pero no fija una superficie concreta. Se normaliza a 1 km2 para comparar densidad celular. |
| Reparto de canales en A | floor(100 / N) por sitio y reparto uniforme entre 3 sectores | Es la interpretacion mas simple y reproducible cuando el enunciado no define scheduler ni redistribucion dinamica. |
| Interferencia co-canal | 2 interferentes dominantes en sectorizado | Aproximacion docente de primera corona para comparar N = 3, 4 y 7 sin introducir un simulador completo. |
| Geometria celular | Hexagono regular equivalente | Permite pasar de capacidad por area a radio celular y numero de sitios con una regla geometrica estandar. |
| Marco tecnologico | Lectura LTE/5G sobre formulas simplificadas | La memoria se redacta como red moderna aunque el dimensionamiento numerico se apoye en balance de enlace y Erlang B. |

## 4. Escenarios

### 4.1 Escenario A - Distrito financiero

El distrito financiero representa un entorno urbano denso con 250.0 Erl/km2, una SNR requerida de 15 dB y una arquitectura de tres sectores por sitio. El reto exige comparar N = 3, 4 y 7 para evaluar el equilibrio entre capacidad e interferencia.

### 4.2 Escenario B - Festival global de innovacion

El festival representa una explanada abierta con 666.7 Erl/km2, una SNR requerida de 5 dB, celdas omnidireccionales y necesidad de evaluar cell splitting para absorber la demanda.

## 5. Pruebas, calculos y simulaciones

### 5.1 Cobertura

| scenario | thermal_noise_dbm | receiver_sensitivity_dbm | max_path_loss_db | coverage_radius_km | traffic_per_user_erlang | traffic_density_erlang_km2 | target_area_km2 | propagation_model | snr_required_db |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_distrito_financiero | -93.9897 | -76.9897 | 125.99 | 0.552793 | 0.1 | 250 | 1 | L_p = 135 + 35 log10(d) | 15 |
| B_festival_global | -93.9897 | -86.9897 | 135.99 | 3.41185 | 0.0833333 | 666.667 | 1 | L_p = 120 + 30 log10(d) | 5 |

### 5.2 Escenario A - Capacidad e interferencia

| reuse_factor_n | reuse_ratio_d_over_r | reuse_distance_km | sectors_per_site | channels_per_site | channels_per_sector | sector_capacity_erlang | site_capacity_erlang | capacity_area_km2 | capacity_radius_km | coverage_radius_km | design_radius_km | design_area_km2 | sectorized_sir_db | omnidirectional_sir_db | sectorization_gain_db | sir_margin_db | limiting_factor | sites_for_target_area | sectors_for_target_area | recommended |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 3 | 0.492776 | 3 | 33 | 11 | 5.84153 | 17.5246 | 0.0700984 | 0.164259 | 0.552793 | 0.164259 | 0.0700984 | 13.6889 | 8.91773 | 4.77121 | -1.31106 | capacity | 15 | 45 | No |
| 4 | 3.4641 | 0.448365 | 3 | 25 | 8 | 3.62705 | 10.8812 | 0.0435246 | 0.129432 | 0.552793 | 0.129432 | 0.0435246 | 15.8754 | 11.1042 | 4.77121 | 0.875372 | capacity | 23 | 69 | Si |
| 7 | 4.58258 | 0.32549 | 3 | 14 | 4 | 1.09226 | 3.27678 | 0.0131071 | 0.0710277 | 0.552793 | 0.0710277 | 0.0131071 | 20.1285 | 15.3573 | 4.77121 | 5.12854 | capacity | 77 | 231 | No |

La ganancia de sectorizacion para la opcion recomendada es 4.771 dB respecto a una referencia omnidireccional de primera corona.

### 5.3 Escenario B - Capacidad y cell splitting

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

### 5.4 Validacion numerica de consistencia

| control | resultado | criterio | valido |
| --- | --- | --- | --- |
| Ruido termico comun | -93.990 dBm | -93.990 dBm aproximados para 20 MHz y NF=7 dB | Si |
| Sensibilidad escenario A | -76.990 dBm | N + 15 dB + 2 dB | Si |
| Sensibilidad escenario B | -86.990 dBm | N + 5 dB + 2 dB | Si |
| Factibilidad radio N=3 | Margen SIR = -1.311 dB | Debe ser negativo para descartar N=3 | Si |
| Factibilidad radio N=4 | Margen SIR = 0.875 dB | Debe ser positivo para aceptar N=4 | Si |
| Factor limitante en A | capacity | Debe dominar capacidad | Si |
| Factor limitante en B | capacity | Debe dominar capacidad | Si |
| Split S3 | Cumple demanda = False | Debe ser insuficiente | Si |
| Split S4 | Cumple demanda = True | Debe ser la primera etapa viable | Si |

## 6. Resultados

En el distrito financiero, el radio por cobertura es 0.553 km, pero el radio recomendado cae a 0.129 km por limitacion de capacidad.
En el festival, la cobertura teorica alcanza 3.412 km mientras que la capacidad sin splitting solo sostiene 0.225 km.
El escenario A recomienda N=4 y el escenario B recomienda cell splitting hasta S4.

## 7. Discusion

La comparacion entre escenarios confirma que el diseno celular no puede justificarse solo por cobertura. En el distrito financiero la sectorizacion y la reutilizacion permiten controlar la interferencia, pero el parametro dominante sigue siendo la capacidad agregada por sitio. Un N muy bajo deja poco margen radio, mientras que un N muy alto penaliza severamente la capacidad. Por eso N=4 es la primera opcion tecnicamente equilibrada.

Ademas, la comparacion entre SIR sectorizada y SIR omnidireccional muestra una mejora de 4.771 dB para la opcion recomendada, lo que refuerza la necesidad de sectorizar el sitio en el escenario urbano denso.

En el festival la situacion cambia por completo. La propagacion abierta y la menor SNR requerida dan un radio de cobertura muy amplio, pero eso no aporta una solucion real porque la limitacion dominante es la densidad de trafico. La unica estrategia coherente dentro del marco del enunciado es el cell splitting, que incrementa la densidad de celdas hasta superar la demanda objetivo.

## 8. Conclusiones

La solucion adoptada para el escenario A es N=4 con tres sectores por sitio, porque es la primera alternativa que supera el umbral radio y mantiene una capacidad razonable por sitio.
La solucion adoptada para el escenario B es cell splitting hasta S4, porque la densidad de usuarios domina claramente sobre la cobertura y obliga a reducir el area de servicio por celda.

### 8.1 Nueva Pangea 2030

Si la densidad de usuarios creciera o se demandaran nuevos servicios como IoT masivo, movilidad conectada o 5G SA, la evolucion natural del diseno pasaria por small cells, mas espectro, beamforming, slicing y edge computing.

## 9. Cumplimiento del enunciado

| bloque_enunciado | evidencia | cumple | comentario |
| --- | --- | --- | --- |
| Introduccion y estado del arte | Incluido en la web y en el informe tecnico | Si | Se incorporan contexto LTE/5G, OFDMA, MCS, propagacion y capacidad. |
| Metodologia reproducible | Ruido, sensibilidad, Lmax, cobertura, trafico, Erlang B y radio final | Si | La secuencia de calculo sigue el orden exacto marcado en el enunciado. |
| Escenario A con reutilizacion y sectorizacion | N=4, 3 sectores y comparacion frente a omni | Si | Se cuantifican SIR sectorizada, SIR omni y ganancia por sectorizacion. |
| Escenario B con cell splitting | Primera etapa viable: S4 | Si | Se evalua la secuencia completa de splitting hasta satisfacer la demanda. |
| Comparacion cobertura frente a capacidad | A: 0.129 km; B: 0.225 km | Si | Ambos escenarios muestran el criterio limitante y el radio final de diseno. |
| Numero de celdas o sitios en area objetivo | A: 23 sitios/1 km2; B: 9 celdas/1 km2 | Si | El area objetivo se normaliza a 1 km2 por no venir fijada en la guia docente. |
| Figura resumen final | Incluida en la web y en assets/figures | Si | Sintetiza las decisiones de diseno para ambos escenarios. |

## 10. Referencias bibliograficas

1. T. S. Rappaport, Wireless Communications: Principles and Practice, 2nd ed., Prentice Hall.
2. A. Goldsmith, Wireless Communications, Cambridge University Press.
3. S. Sesia, I. Toufik y M. Baker, LTE - The UMTS Long Term Evolution, Wiley.
4. E. Dahlman, S. Parkvall y J. Skold, 5G NR: The Next Generation Wireless Access Technology, Academic Press.