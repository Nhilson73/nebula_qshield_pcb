# Prompt para Gemini Spark — Fase 6: cierre de 40 nets desconectadas en Nebula Q-Shield

## Contexto

- **Proyecto:** KiCad 10 PCB `nebula_qshield` para Arduino UNO Q.
- **Board actual:** 150 mm × 120 mm (J1 barrel jack movido a la derecha, conectores de borde dentro del outline).
- **Stackup:** 4 capas — `F.Cu` (señal), `In1.Cu` (GND), `In2.Cu` (PWR split `/12V_RAIL`), `B.Cu` (señal).
- **Estado de fabricación:** DRC 0 violaciones, ERC 0 violaciones, **40 pares de pads/tracks/vías aún desconectados**.
- **Herramientas disponibles:** `kicad-cli`, `pcbnew` Python, `place_power_vias_v3.py`, `close_pairs_v7.py`.
- **Imagen de apoyo:** `docs/layout_fase6.png` (render de F.Cu + In1.Cu + In2.Cu + B.Cu + Edge.Cuts + F.SilkS).

## Netclasses relevantes

| Netclass | track_width | via_diameter | clearance |
| --- | --- | --- | --- |
| Analog | 0.25 mm | 0.6 / 0.3 mm | 0.3 mm |
| Power | 0.5 mm | 0.8 / 0.4 mm (vías 0.6/0.3 también aceptadas) | 0.3 mm con otros |
| HighCurrent | 0.5–1.5 mm | 1.0 / 0.5 mm | 0.3 mm |
| RelayHV | 1.0 mm | 1.0 / 0.5 mm | 0.5 mm (no aplica a estas nets) |
| Default/I2C | 0.25 mm | 0.6 / 0.3 mm | 0.25–0.3 mm |

## Descripción del problema

Queda un conjunto de **40 pares desconectados** concentrados en:

1. **GND (5 pares):** vías/planes vs pads de capacitores/resistencias, principalmente alrededor de `C11`, `U9`, `C21`, `C14`, `D5` y `Q2`.
2. **Riles de potencia (11 pares):** `/12V_RAIL` tiene islas separadas en `In2.Cu`; `/5V_RAIL` y `/3V3_RAIL` tienen pads/tracks alejados del plano interno.
3. **Señales analógicas aisladas (~24 pares):** `VDD_ISO_*`, `*_ATT`, `*_SIG`, `SN_D*`, `PH_BUF`, `DO_BUF/DO_SIG/DO_SEC_B`, `CO2_SIG`, `ORP_SIG`, `HUM_ADC`, etc. La mayoría son cortos entre pads SMD y tracks/vías, algunos atraviesan zonas densas de `U5/U6/U8/U9/U12/U13` y sus resistencias/capacitores asociados.

## Tabla completa de pares desconectados

Ver archivo adjunto `tools/unconnected_report.md` o la tabla abajo.

| Net | A | Ref A | Capa A | xA | yA | B | Ref B | Capa B | xB | yB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| /Analog Acquisition/ORP_ATT | Pad 1 | R32 | F.Cu | 71.82 | 31.87 | Track | None | B.Cu | 67.0102 | 35.1403 |
| /HUM_ADC | Pad 1 | C23 | F.Cu | 71.83 | 33.11 | Track | None | F.Cu | 65.07 | 31.87 |
| GND | Via | None | F.Cu - B.Cu | 4.4598 | 25.9154 | Pad 2 | C11 | F.Cu | 3.79 | 24.86 |
| GND | Via | None | F.Cu - B.Cu | 63.6826 | 19.1636 | Pad 5 | U9 | F.Cu | 65.505 | 20.875 |
| GND | Pad 2 | C21 | F.Cu | 68.29 | 33.11 | Track | None | F.Cu | 71.2772 | 33.8472 |
| GND | Track | None | F.Cu | 72.79 | 33.11 | Pad 2 | C14 | F.Cu | 75.04 | 32.11 |
| GND | Pad 2 | D5 | F.Cu | 89.35 | 21.9 | Track | None | F.Cu | 88.185 | 26.0062 |
| /3V3_RAIL | Pad 14 | U22 | F.Cu | 22.8625 | 104.025 | Via | None | F.Cu - B.Cu | 21.6224 | 104.1817 |
| /3V3_RAIL | Track | None | F.Cu | 67.445 | 22.1518 | Via | None | F.Cu - B.Cu | 72.3983 | 23.2477 |
| /Analog Acquisition/VDD_ISO_ORP | Via | None | F.Cu - B.Cu | 70.35 | 28.55 | Pad 1 | U9 | F.Cu | 61.695 | 25.825 |
| /Analog Acquisition/VDD_ISO_ORP | Via | None | F.Cu - B.Cu | 70.35 | 28.55 | Via | None | F.Cu - B.Cu | 84.3898 | 28.5614 |
| /CO2_SOL_CTL | PTH pad 22 | J21 | F.Cu - B.Cu | 41.66 | 86.36 | Via | None | F.Cu - B.Cu | 105.0 | 95.51 |
| /Analog Acquisition/GND_ISO_PH | Track | None | F.Cu | 85.54 | 31.86 | Via | None | F.Cu - B.Cu | 69.57 | 31.87 |
| /Analog Acquisition/ORP_SIG | Via | None | F.Cu - B.Cu | 78.57 | 20.12 | Track | None | F.Cu | 89.6 | 20.6 |
| /I2C_SCL | Pad 1 | R37 | F.Cu | 68.055 | 96.0 | Track | None | B.Cu | 68.58 | 86.36 |
| /Analog Acquisition/PH_BUF | Via | None | F.Cu - B.Cu | 68.34 | 31.87 | Track | None | F.Cu | 83.1227 | 11.825 |
| /Analog Acquisition/VDD_ISO_PH | Track | None | F.Cu | 83.695 | 20.0977 | Track | None | F.Cu | 64.2719 | 27.4719 |
| /5V_RAIL | Via | None | F.Cu - B.Cu | 41.0 | 1.3 | Track | None | F.Cu | 19.4 | 7.87 |
| /5V_RAIL | Track | None | F.Cu | 84.8125 | 21.9 | Track | None | F.Cu | 78.05 | 18.05 |
| /5V_RAIL | Via | None | F.Cu - B.Cu | 85.1261 | 24.8836 | Track | None | F.Cu | 84.8125 | 21.9 |
| /5V_RAIL | Via | None | F.Cu - B.Cu | 91.7685 | 26.4338 | Track | None | F.Cu | 85.1261 | 24.8836 |
| /Analog Acquisition/VDD_ISO_DO | Track | None | F.Cu | 75.35 | 30.05 | Track | None | F.Cu | 64.9261 | 33.2639 |
| /Analog Acquisition/DO_FILT | Track | None | F.Cu | 78.58 | 32.86 | Track | None | F.Cu | 69.57 | 30.62 |
| /Actuator Drivers/MOTOR_HO | Via | None | F.Cu - B.Cu | 110.4135 | 68.7984 | Pad 7 | U17 | F.Cu | 117.0714 | 75.1659 |
| /12V_RAIL | Zone | None | In2.Cu | -8.0 | -2.0 | Via | None | F.Cu - B.Cu | -8.0 | -2.0 |
| /12V_RAIL | Pad 1 | R4 | F.Cu | 2.82 | 22.37 | Track | None | F.Cu | 7.3441 | 24.4989 |
| /12V_RAIL | Via | None | F.Cu - B.Cu | 10.225 | 24.0 | Track | None | F.Cu | 14.925 | 23.4563 |
| /12V_RAIL | Track | None | F.Cu | 14.925 | 23.4563 | Via | None | F.Cu - B.Cu | 14.4 | 20.15 |
| /12V_RAIL | Zone | None | In2.Cu | -8.0 | -2.0 | Zone | None | In2.Cu | -8.0 | -2.0 |
| /Analog Acquisition/DO_SEC_B | Pad 6 | T3 | F.Cu | 75.51 | 6.81 | Via | None | F.Cu - B.Cu | 63.65 | 31.1 |
| /Analog Acquisition/CO2_SIG | Via | None | F.Cu - B.Cu | 89.0 | 24.1 | Via | None | F.Cu - B.Cu | 75.07 | 27.87 |
| /Analog Acquisition/PH_ATT | Pad 2 | R31 | F.Cu | 70.59 | 31.87 | Track | None | B.Cu | 68.955 | 29.87 |
| /Analog Acquisition/PH_ATT | Pad 2 | R31 | F.Cu | 70.59 | 31.87 | Pad 2 | U6 | F.Cu | 84.965 | 19.575 |
| /Analog Acquisition/DO_BUF | Pad 2 | U13 | F.Cu | 80.215 | 27.325 | Track | None | F.Cu | 74.465 | 20.875 |
| /Analog Acquisition/DO_SIG | Track | None | F.Cu | 89.35 | 27.6 | Pad 1 | R13 | F.Cu | 67.32 | 30.62 |
| /Analog Acquisition/SN_D1_DO | Via | None | F.Cu - B.Cu | 56.2625 | 30.05 | Via | None | F.Cu - B.Cu | 75.71 | 18.55 |
| /Analog Acquisition/SN_D2_DO | Via | None | F.Cu - B.Cu | 80.39 | 18.05 | Pad 5 | U12 | F.Cu | 58.3375 | 28.15 |
| /Analog Acquisition/SN_D1_ORP | Via | None | F.Cu - B.Cu | 66.26 | 18.05 | Pad 3 | U8 | F.Cu | 84.8125 | 27.55 |
| /Analog Acquisition/SN_D2_ORP | Pad 5 | U8 | F.Cu | 87.0875 | 25.65 | Track | None | F.Cu | 71.34 | 18.05 |
| /Analog Acquisition/SN_D2_PH | Pad 5 | U5 | F.Cu | 87.0875 | 21.9 | Pad 3 | T1 | F.Cu | 62.09 | 18.05 |

## Preguntas para Spark

1. **¿Qué componentes densos conviene reubicar levemente** para abrir corredores de ruteo sin romper el factor de forma del UNO Q? Tené en cuenta que `J21` (header UNO Q) y los conectores de borde (`J2`, `J3`, `J5`, `J15-J19`) son inmutables; el resto puede moverse.
2. **Para cada net en la tabla**, proponé una ruta concreta: capa(s), vía(s), puntos de inicio/fin y esquina intermedia si es necesaria. Considerá `In1.Cu` y `In2.Cu` como caminos alternativos (aunque hoy rompen planes, se pueden rellenar después si justificás el tramo corto).
3. **Para `/12V_RAIL`**: ¿cómo identificás las islas reales del split-plane en `In2.Cu` y qué vías/puentes necesitás para unirlas? Los pares `Zone` tienen coordenadas de origen (-8,-2) que no representan la isla real.
4. **Para GND**: ¿hay espacio para vías adicionales cerca de `C11`, `C21`, `C14`, `D5`, `U9`, `Q2` que conecten a `In1.Cu` sin romper otras nets?

## Formato de respuesta deseado

Devolvé:
- Una **lista numerada de movimientos de componentes** (ref, nueva x, nueva y, rotación, justificación en 1 línea).
- Una **tabla de ruteo propuesto** (net, capa, x_inicio, y_inicio, x_esquina, y_esquina, x_fin, y_fin, vía en x,y, nota).
- Un **resumen de impacto**: cuántos pares se cierran, cuáles quedan pendientes y si recomendás aumentar el board (actualmente 150×120 mm, enclosure aún no diseñado).
