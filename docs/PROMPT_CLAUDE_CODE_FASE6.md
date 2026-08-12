# Prompt para Claude Code — Cerrar 38 nets desconectados en Nebula Q-Shield

## Contexto del proyecto

Repositorio: `https://github.com/Nhilson73/nebula_qshield_pcb`  
Herramienta: KiCad 10 (`kicad/nebula_qshield.kicad_pcb`, `kicad/nebula_qshield.kicad_sch`).  
Entorno de validación: Docker `kicad/kicad:10.0.5` con el repo montado en `/workspace`.

Objetivo final: board fabricable en JLCPCB.
- `kicad-cli pcb drc --severity-error --refill-zones kicad/nebula_qshield.kicad_pcb` → 0 violaciones, 0 unconnected items.
- `kicad-cli sch erc --severity-all kicad/nebula_qshield.kicad_sch` → 0 violaciones.

## Estado actual (branch `main`, post-PR #60)

- DRC: 0 violaciones.
- Unconnected items: 38.
- ERC: 0 violaciones.
- Board: 150 mm × 120 mm, 4 capas:
  - `F.Cu` — señal
  - `In1.Cu` — GND plane
  - `In2.Cu` — split-plane (`/12V_RAIL` prioridad 1, `/5V_RAIL` y `/3V3_RAIL` mayor prioridad)
  - `B.Cu` — señal

## Netclasses relevantes

| Netclass | Ancho pista | Vía (drill/pad) | Clearance mínimo |
|---|---|---|---|
| Default | 0.25 mm | 0.5 / 0.2 mm | 0.20–0.25 mm |
| Analog | 0.25 mm | 0.5 / 0.2 mm | 0.35 mm |
| Power | 0.50 mm | 0.8 / 0.4 mm | 0.30 mm |
| HighCurrent | 1.00 mm | 1.0 / 0.5 mm | 0.30–0.50 mm |
| RelayHV | 1.00 mm | 1.0 / 0.5 mm | 0.50–0.60 mm |

`Board_Edge` clearance: 0.25 mm.

## Archivos que ya están en el repo

- `docs/PROMPT_GEMINI_FASE6_CLOSE_38.md` — prompt enviado a Gemini Spark.
- `docs/RESPUESTA_SPARK_FASE6_CLOSE_38.md` — plan de Spark.
- `docs/PROMPT_CLAUDE_FASE6_CLOSE_38.md` — prompt anterior para Claude.
- `kicad/nebula_qshield-drc.rpt` — reporte DRC actual con los 38 pares desconectados.
- `tools/uno_q_analysis.txt` — análisis de cada par: coordenadas, capas, refs.
- `tools/move_analog_passives.py` — script de prueba que movió 6 pasivos y demostró que el plan de Spark colisiona.
- `tools/analyze_uno_q_usefulness*.py` — scripts para verificar proximidad al área del UNO Q.

## Resumen del problema

El board tiene 38 pares de items físicamente no conectados. FreeRouting se estanca en ~38. Gemini Spark propuso mover 6 pasivos (`C20`, `C21`, `C23`, `R30`, `R31`, `R32`) 2 mm hacia arriba para abrir un corredor en `y ≈ 30–31.5 mm`. Al aplicarlo con `pcbnew`, se generaron **69 violaciones DRC** (cortocircuitos y clearances) porque los nuevos sitios caen sobre vías y pistas existentes (`/3V3_RAIL`, `GND`, `/CO2_FILT`, `/TEMP_ADC`, etc.).

La raíz del problema es **congestión en el bloque analógico** (`x ≈ 60–90 mm`, `y ≈ 18–35 mm`) y **islas en los planes de potencia** de `In2.Cu`.

## Inmutables (NO mover, NO modificar)

- `J21` (header UNO Q) y sus 4 agujeros M3.
- Conectores de borde: `J1`, `J2`, `J3`, `J5`, `J7`, `J8–J14`, `J15–J19`.
- Agujeros de montaje adicionales.
- Relés `K1`/`K2` y drivers `U17`/`U20`.
- Tamaño del board: 150 mm × 120 mm.
- Área de acoplamiento del UNO Q: no colocar componentes allí (tracks/vías de escape sí, si no pisan `J21`).

## Trabajo que ya intentamos

- FreeRouting completo: se estanca con ~38 desconectados.
- Scripts `close_pairs_v7/v8`: reducen algunos pares pero dejan vías aisladas.
- Vías GND manuales: ayudan parcialmente pero el plano `In1.Cu` tiene islas o clearance con pistas de potencia.
- Puente `/12V_RAIL` en `B.Cu` por `y = 112 mm`: colisiona con pistas existentes en F.Cu/B.Cu.
- Spark move-2mm: 69 violaciones al aplicar.

## Qué necesitamos que hagas

1. **Cloná o abrí el repo** (`Nhilson73/nebula_qshield_pcb`) en tu entorno de Claude Code.
2. **Leé el DRC report** `kicad/nebula_qshield-drc.rpt` para ver los 38 pares exactos.
3. **Escribí un script Python** (`tools/route_fase6.py`) que use `pcbnew` para cerrar los 38 pares con DRC 0.

### Requisitos del script

- Cargar `kicad/nebula_qshield.kicad_pcb`.
- Extraer los pares desconectados con `BOARD.GetConnectivity()` y `CONNECTIVITY_DATA`.
- Para cada par, intentar conectar los items con **una o dos vías + tracks rectos o en L** en `F.Cu` o `B.Cu`.
- Verificar clearance contra:
  - Todos los pads y vías del board.
  - Todos los tracks de `F.Cu` y `B.Cu`.
  - Zonas rellenas de `In1.Cu` y `In2.Cu` (usar `zone.HitTestFilledArea` o similar).
- Respetar netclasses (ancho, vía, clearance).
- Si no entra una ruta, **intentar un movimiento mínimo** (≤ 2 mm) de pasivos del bloque analógico (`C20–C23`, `R30–R32`) o re-ubicar una vía, siempre validando que no genere colisiones.
- Si es necesario, **ripar tracks/vías pequeñas** de un área delimitada (`x ≈ 64–74 mm, y ≈ 31–37 mm`) y reconectalas, pero nunca nada inmutable.
- Refill zones con `pcbnew.ZONE_FILLER`.
- Guardar `kicad/nebula_qshield.kicad_pcb`.
- Imprimir estadísticas: pares intentados, cerrados, fallidos.

### Validación que debe pasar

Después de correr tu script, ejecutar desde la raíz del repo:

```bash
docker run --rm -v "$(pwd):/workspace" -w /workspace kicad/kicad:10.0.5 \
  kicad-cli pcb drc --severity-error --refill-zones \
  -o /workspace/kicad/nebula_qshield-drc.rpt \
  /workspace/kicad/nebula_qshield.kicad_pcb

docker run --rm -v "$(pwd):/workspace" -w /workspace kicad/kicad:10.0.5 \
  kicad-cli sch erc --severity-all \
  -o /workspace/kicad/nebula_qshield-erc.rpt \
  /workspace/kicad/nebula_qshield.kicad_sch
```

Resultado esperado:
- DRC: `Found 0 violations`, `unconnected_items` = 0.
- ERC: `Found 0 violations`.

## Estrategia sugerida (puedés cambiarla si justificás)

1. **GND**: insertar vías 0.5/0.2 mm en los pads `C11.2`, `U9.5`, `C21.2`, `C14.2`, `D5.2` que conecten a `In1.Cu`. Verificar que no cortocircuiten con `/3V3_RAIL` cercano.
2. **Potencia**:
   - `/12V_RAIL`: unir islas con un puente de 1.0 mm en `B.Cu` desde `(14.93, 23.46)` hasta `(110.41, 66.26)` (o el camino que encuentres libre), con vías `HighCurrent` en los extremos.
   - `/5V_RAIL` y `/3V3_RAIL`: cerrar pares en el borde inferior/analógico con tracks `Power` 0.5 mm y vías 0.8/0.4 mm.
3. **Control**:
   - `/CO2_SOL_CTL`: `J21` pin 22 `(41.66, 86.36)` → `R26` pad 1 `(105.0, 95.51)`, preferentemente por `B.Cu`.
   - `/I2C_SCL`: vía cerca de `R37` `(68.06, 96.0)` → `J21` pin 32 `(68.58, 86.36)`, por `B.Cu`.
4. **Bloque analógico**: con pares de pads en `F.Cu` y su opuesto en `B.Cu`, usar vías cerca de los pads y tracks cortos. Si no entran, mover `C20–C23`/`R30–R32` ≤ 2 mm y reintentar.
5. **Actuadores**:
   - `/MOTOR_HO`: `U17` pin 7 `(117.07, 75.17)` → vía `(110.41, 68.80)`, `F.Cu` o `B.Cu`, ancho 0.5 mm.

## Entregables

1. Script `tools/route_fase6.py` (o nombre similar) autocontenido y ejecutable en `kicad/kicad:10.0.5`.
2. `kicad/nebula_qshield.kicad_pcb` modificado con DRC 0 y 0 desconectados.
3. Breve `docs/CLAUDE_FASE6_REPORT.md` explicando qué cerró el script, qué movimientos hizo y qué quedó pendiente (si algo).
4. Ejecutá los comandos de validación y pegá las últimas líneas de salida en el reporte.

## Notas para evitar errores conocidos

- En `pcbnew`, las constantes de capa interna son `pcbnew.In1_Cu` y `pcbnew.In2_Cu` (no `IN2_Cu`).
- `ZONE_FILLER` se instancia como `f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones())`.
- `ZONE.GetFilledPolysList(pcbnew.In2_Cu)` necesita el argumento de capa.
- Para ver si una vía queda aislada, usá `conn = b.GetConnectivity(); conn.Build(b); len(conn.GetConnectedItems(via))`.
- No asumas que una zona rellena está conectada visualmente: usá `HitTestFilledArea` para confirmar que un punto cae dentro del cobre real.

## Si no llegás a 0

Si el script no puede cerrar todos los pares, explicá en el reporte:
- Cuántos cerró y cuántos no.
- Qué pares no entraron y por qué (obstáculo, clearance, no hay capa disponible).
- Si recomendás agrandar el board, re-ubicar componentes grandes o cambiar la netclass de algún net.

Devin se encargará de revisar tu script, ejecutarlo en su entorno Docker y abrir un PR con el board final.