# Operacion Nexo 5G/6G - Anexo de calculos

## Formulas base

- `N = -174 + 10 log10(B) + NF`
- `Sens = N + SNRreq + Limpl`
- `Lmax = Ptx + Gtx + Grx - Lotros - Sens`
- `Auser = llamadas_por_hora * duracion_media_horas`

## Escenario A - Distrito financiero

1. Ruido termico: `N = -93.990 dBm`.
2. Sensibilidad: `Sens = -76.990 dBm`.
3. Perdida maxima admisible: `Lmax = 125.990 dB`.
4. Radio por cobertura: `Rcov = 0.553 km`.
5. Trafico por usuario: `Auser = 0.100 Erl`.
6. Densidad de trafico: `Akm2 = 250.000 Erl/km2`.
7. Reuso recomendado: `N = 4` con `Rdesign = 0.129 km`.

## Escenario B - Festival global

1. Ruido termico: `N = -93.990 dBm`.
2. Sensibilidad: `Sens = -86.990 dBm`.
3. Perdida maxima admisible: `Lmax = 135.990 dB`.
4. Radio por cobertura: `Rcov = 3.412 km`.
5. Radio por capacidad sin splitting: `Rcap = 0.225 km`.
6. Split recomendado: `S4` con `R = 0.213 km`.
7. Sitios en 1 km2 tras splitting: `9`.

## Validacion numerica de consistencia

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