# Prompt para Claude — Nebula Q-Shield: cerrar 38 nets desconectados restantes

## Contexto

Repositorio: `Nhilson73/nebula_qshield_pcb`  
Herramienta: KiCad 10 (`kicad/nebula_qshield.kicad_pcb`, `.kicad_sch`).  
Objetivo: llevar el board a fabricación en JLCPCB, lo que requiere:
- `kicad-cli pcb drc --severity-error --refill-zones` → 0 violaciones, 0 items desconectados.
- `kicad-cli sch erc --severity-all` → 0 violaciones.

## Estado actual

- **DRC**: 0 violaciones de error.
- **Unconnected items**: 38.
- **ERC**: 0 violaciones.
- **Board**: 150 mm × 120 mm, 4 capas:
  - `F.Cu` señal
  - `In1.Cu` GND plane
  - `In2.Cu` split-plane (`/12V_RAIL`, `/5V_RAIL`, `/3V3_RAIL` con prioridades)
  - `B.Cu` señal
- **Netclasses clave**:
  - `Analog`: track 0.25 mm, vía 0.5/0.2 mm, clearance 0.35 mm
  - `Power`: track 0.5 mm, vía 0.8/0.4 mm, clearance 0.30 mm
  - `HighCurrent`: track 1.0 mm, vía 1.0/0.5 mm
  - `RelayHV`: track 1.0 mm, clearance 0.5–0.6 mm (regla actual del board)
- **Inmutable**: `J21` (header UNO Q), conectores de borde (`J1,J2,J3,J5,J7,J8-J14,J15-J19`), agujeros de montaje, relés `K1/K2` y drivers `U17/U20`. El área de acoplamiento del UNO Q **no debe usarse** para colocar componentes, solo tracks/vías de escape.

## Archivos relevantes

- `kicad/nebula_qshield.kicad_pcb` — board actual.
- `kicad/nebula_qshield-drc.rpt` — reporte con los 38 pares desconectados.
- `docs/PROMPT_GEMINI_FASE6_CLOSE_38.md` — prompt que enviamos a Gemini Spark.
- `RESPUESTA_SPARK_FASE6_CLOSE_38.md` — plan de Spark (movimiento de 6 pasivos + rutas).

## Por qué el plan de Spark falló al aplicarse

Spark propuso mover 6 pasivos (`C20,C21,C23,R30,R31,R32`) 2 mm hacia arriba para abrir un corredor horizontal en `y ≈ 30–31.5 mm` y así cerrar 19 de 22 stubs analógicos.

**Resultado de aplicar el movimiento directamente con `pcbnew`:**
- Baseline: 0 violaciones, 38 desconectados.
- Después del movimiento: **69 violaciones DRC**, 47 desconectados.

**Razón**: los nuevos sitios de los pasivos (`y ≈ 33.87–35.11 mm`) ya están ocupados por vías y pistas de otros nets (`/3V3_RAIL`, `GND`, `/CO2_FILT`, `/TEMP_ADC`, `/GND_ISO_DO`, etc.). El plan de Spark no consideró que había que **rippear primero** las pistas/vías existentes de esa zona. Algunos ejemplos reales del DRC:
- `C20` pad 1 en `(65.08, 35.11)` cortocircuita con vía `/3V3_RAIL` y pista `/CO2_FILT`.
- `C23` pad 1 en `(71.83, 35.11)` cortocircuita con vía `/3V3_RAIL` y pista `/HUM_ADC`.
- `R30` pad 1 en `(67.32, 33.87)` cortocircuita con pista `/3V3_RAIL`.
- `R31` en `(69.57, 33.87)` cortocircuita con pista `/TEMP_ADC` y vía `/GND_ISO_DO`.
- `R32` pad 2 en `(72.84, 33.87)` cortocircuita con vía `/3V3_RAIL` y vía `GND`.

Por eso el plan no es "aplicar y listo": requiere un rip-up-and-reroute previo del bloque analógico.

## Distribución de los 38 pares desconectados

Extraído de `kicad/nebula_qshield-drc.rpt`:

1. **Bloque analógico denso** (`x ≈ 60–90 mm, y ≈ 18–35 mm`) — 22 pares:
   - `/Analog Acquisition/ORP_ATT`, `/HUM_ADC`, `/VDD_ISO_ORP` (×2), `/GND_ISO_PH`, `/ORP_SIG`, `/PH_BUF`, `/VDD_ISO_PH`, `/VDD_ISO_DO`, `/DO_FILT`, `/DO_BUF`, `/DO_SIG`, `/DO_SEC_B`, `/CO2_SIG`, `/PH_ATT`, `SN_D1_DO`, `SN_D2_DO`, `SN_D1_ORP`, `SN_D2_ORP`, `SN_D2_PH`.
2. **Rieles de potencia** (`x < 15 mm, y ≈ 20–25 mm`) — 12 pares:
   - `/12V_RAIL` (4 pares), `/5V_RAIL` (4 pares), `/3V3_RAIL` (2 pares).
3. **GND** (5 pares):
   - Vías/pads de `C11`, `U9`, `C21`, `C14`, `D5`.
4. **RS485 / digital** (2 pares):
   - `/3V3_RAIL` en `U22` pin 14, `/I2C_SCL`.
5. **Actuadores** (1 par):
   - `/Actuator Drivers/MOTOR_HO` (`U17` pin 7 ↔ vía).
6. **Control** (1 par):
   - `/CO2_SOL_CTL` (`J21` pin 22 ↔ `R26`).

(Nota: hay más de 38 líneas porque algunos pares pertenecen al mismo net; los detalles exactos están en el DRC report adjunto.)

## Petición

Dado que Devin ya intentó `FreeRouting` (se estanca en ~38 desconectados), scripts `close_pairs` y movimientos manuales parciales, y ahora el plan de Spark colapsa al aplicarse, **necesitamos una estrategia concreta que pueda ejecutar Devin con `pcbnew` y que llegue a 0 desconectados**.

Por favor, respondé con **una de estas dos cosas** (preferiblemente la opción 2):

### Opción 1 — Plan de rip-up + reroute del bloque analógico
- Indicá exactamente qué tracks y vías hay que eliminar en el rectángulo `x ≈ 64–74 mm, y ≈ 31–37 mm` (o el área que consideres necesaria).
- Confirmá si el movimiento de `C20–C23/R30–R32` 2 mm hacia arriba es correcto o necesita otra distancia/ángulo.
- Proporcioná una secuencia de pasos: qué nets rippear, qué componentes mover, y cómo reconectar cada grupo de nets.
- Incluí vías de escape, capas a usar y ancho de pista.

### Opción 2 — Script de ruteo Python completo
- Escribí un script en Python usando `pcbnew` que cierre los 38 pares desconectados.
- El script debe:
  - Leer `kicad/nebula_qshield.kicad_pcb`.
  - Usar un buscador de caminos A* o grid con clearance real contra pads, tracks y zonas rellenas (`In1.Cu`, `In2.Cu`, `F.Cu`, `B.Cu`).
  - Respetar netclasses (ancho, vía, clearance).
  - Permitir movimientos mínimos de pasivos si es estrictamente necesario, siempre chequeando que no genere nuevas colisiones.
  - Ejecutar `b.BuildConnectivity()` y guardar el board.
  - Imprimir cuántos pares cerró y cuáles quedaron sin ruta.
- No hace falta que sea perfecto en el primer intento; podemos iterar.

### Incluí en la respuesta
1. **Resumen ejecutivo al inicio**: `¿es viable llegar a 0 desconectados con la colocación actual o hace falta un placement más grande?`
2. **Si proponés movimientos de componentes**: tabla `Ref | x | y | rotación | justificación`.
3. **Si proponés rutas**: para cada net o grupo, indicá capa, waypoints, vías y por qué no choca.
4. **Si das código**: que el script sea autocontenido y runnable en `kicad/kicad:10.0.5` (Python 3 + `pcbnew`).

## Restricciones duras

- No mover `J21`, conectores de borde, agujeros, relés ni drivers.
- No usar el área del acoplamiento UNO Q para componentes (tracks/vías de escape sí, si no pisan `J21`).
- No aumentar el board más allá de 150 × 120 mm.
- `RelayHV` clearance 0.5 mm (regla actual del board).
- `Board_Edge` clearance 0.25 mm.
- Vías de señal 0.5/0.2 mm (JLCPCB estándar).

## Entrega esperada

Markdown con análisis + código (si optás por la opción 2). Devin se encargará de ejecutar, validar con `kicad-cli pcb drc` y `kicad-cli sch erc`, y abrir el PR correspondiente.