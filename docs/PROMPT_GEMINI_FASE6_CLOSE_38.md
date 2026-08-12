# Prompt para Gemini Spark — Nebula Q-Shield: cerrar los 38 nets desconectados restantes

## Contexto

Repositorio: `Nhilson73/nebula_qshield_pcb` (KiCad 10, PCB 4 capas). Spark tiene acceso al repo y puede leer `kicad/nebula_qshield.kicad_pcb`, los reportes DRC/ERC y los scripts de `tools/`.

**Estado actual del PCB (branch `main` / PR #59 mergeado):**

- `kicad-cli pcb drc --severity-error --refill-zones`: **0 violaciones**
- `kicad-cli sch erc --severity-all`: **0 violaciones**
- `kicad-cli pcb drc --severity-error`: **38 items desconectados** (ver `kicad/nebula_qshield-drc.rpt`)
- Board: **150 mm × 120 mm**, 4 capas (`F.Cu` señal, `In1.Cu` GND plane, `In2.Cu` split-plane `12V/5V/3V3`, `B.Cu` señal).

## Objetivo

Reducir los **38 nets desconectados a 0** manteniendo DRC/ERC limpios. Se permite re-ubicar componentes **solo si es estrictamente necesario para abrir corredores de ruteo**. No queremos trabajo extra sin retorno: si un movimiento no desbloquea varios nets, proponé otra cosa.

## No tocar / inmutable

- `J21` (UNO Q header) y sus 4 agujeros M3.
- Todos los conectores de borde: `J1`, `J2`, `J3`, `J5`, `J7`, `J8-J14`, `J15-J19`.
- Relés `K1`/`K2` y drivers `U17`/`U20`.
- Agujeros de montaje adicionales.
- El board no debe crecer (150 × 120 mm).
- **NO usar el área del acoplamiento UNO Q** para colocar componentes (quedó descartado en la conversación). Esa área solo puede usarse para tracks/vías de escape si no interfieren con `J21`.

## Clasificación de los 38 nets desconectados

Los pares están agrupados así (extraído de `kicad/nebula_qshield-drc.rpt`):

1. **Bloque analógico denso** (x ≈ 60–90 mm, y ≈ 18–35 mm):
   - `/Analog Acquisition/ORP_ATT`, `/HUM_ADC`, `/VDD_ISO_ORP` (×2), `/GND_ISO_PH`, `/ORP_SIG`, `/PH_BUF`, `/VDD_ISO_PH`, `/VDD_ISO_DO`, `/DO_FILT`, `/DO_BUF`, `/DO_SIG`, `/DO_SEC_B`, `/CO2_SIG`, `/PH_ATT`, `SN_D1_DO`, `SN_D2_DO`, `SN_D1_ORP`, `SN_D2_ORP`, `SN_D2_PH`.
2. **Rieles de potencia** (x < 15 mm, y ≈ 20–25 mm):
   - `/12V_RAIL` (4 pares), `/5V_RAIL` (4 pares), `/3V3_RAIL` (2 pares).
3. **GND** (5 pares):
   - `C11` pad 2, `U9` pad 5, `C21` pad 2, `C14` pad 2, `D5` pad 2.
4. **RS485 / digital**:
   - `/3V3_RAIL` en `U22` pin 14, `/I2C_SCL`.
5. **Actuadores**:
   - `/Actuator Drivers/MOTOR_HO` (`U17` pin 7 ↔ vía).
6. **Control**:
   - `/CO2_SOL_CTL` (`J21` pin 22 ↔ `R26` pad 1).

Los detalles exactos de cada par (coords, tipo de item, capa) están en `kicad/nebula_qshield-drc.rpt` y en el análisis `tools/uno_q_analysis.txt`.

## Netclasses relevantes

| Netclass | Track width | Vía (outer/drill) | Clearance |
|---|---|---|---|
| `Default` | 0.25 mm | 0.5 / 0.2 mm | 0.25 mm |
| `Analog` | 0.25 mm | 0.5 / 0.2 mm | 0.35 mm |
| `Power` | 0.50 mm | 0.8 / 0.4 mm | 0.30 mm |
| `HighCurrent` | 1.00 mm | 1.0 / 0.5 mm | 0.30–0.50 mm |
| `RelayHV` | 1.00 mm | 1.0 / 0.5 mm | 0.60 mm |

`Board_Edge` clearance: 0.25 mm. `RelayHV` clearance se redujo a 0.5 mm en layout; en DRC pasa.

## Problemas conocidos

- El bloque analógico está saturado: `C20-C23`, `R30-R32` y los op-amps/aisladores `U5-U13` comparten una zona pequeña. Cualquier vía de 0.5 mm o pista de 0.25 mm choca con pads vecinos o pistas GND/`/3V3_RAIL`.
- El `/12V_RAIL` en `In2.Cu` está fraccionado en islas. Un puente en `B.Cu` o `F.Cu` de 1.0 mm conectaría la isla izquierda (`R4`, `FB1`, `D2`) con la derecha (`K1`/`K2`/`U17`/`D12`/`D13`), pero debe evitar zonas GND y pads del bloque analógico.
- Los rails `/5V_RAIL` y `/3V3_RAIL` tienen pares desconectados en el mismo sector analógico/izquierdo.
- `CO2_SOL_CTL` (`J21` pin 22 en 41.66, 86.36) → `R26` pad 1 (105.0, 95.51). No puede ir en F.Cu horizontal por y=86.36 porque pasa por los pads de `J21`.
- `I2C_SCL` (`J21` pin 32 en 68.58, 86.36) → vía actual en 68.06, 96.0.

## Petición concreta

1. **Re-planificación mínima del bloque analógico**: si es necesario, proponé mover **solo pasivos** (`C20-C23`, `R30-R32`, `R12-R15`, `R18`) o re-ubicar ligeramente `U5-U13` (sin alejarlos más de 10 mm de sus conectores BNC/JST). Presentá la tabla:
   `Ref | x actual | y actual | x nuevo | y nuevo | rotación (°) | motivo (qué corredor abre)`.

2. **Estrategia de ruteo para los 38 pares**: para cada grupo (analógico, GND, potencia, RS485, actuadores, `CO2_SOL_CTL`/`I2C_SCL`), indicá:
   - Capa(s) a usar (`F.Cu`, `B.Cu`, `In1.Cu` solo para GND vías, `In2.Cu` solo para planes existentes).
   - Coordenadas aproximadas de vías y waypoints.
   - Ancho y tamaño de vía.
   - Cómo evitar obstáculos (pistas/zonas vecinas).

3. **Cierre de `/12V_RAIL`**: dónde colocar un puente de 1.0 mm en `B.Cu` y las dos vías `HighCurrent` (1.0 / 0.5 mm) para unir las islas izquierda y derecha sin violar GND/`/3V3_RAIL`.

4. **Vías GND**: ubicaciones concretas para insertar vías 0.5 / 0.2 mm cerca de `C11`, `U9`, `C21`, `C14`, `D5` que conecten a `In1.Cu` y no cortocircuiten con `/3V3_RAIL` ni pads vecinos.

5. **Alternativa de fabricación**: si considerás que llegar a 0 desconectados requiere un board más grande o un placement radical, decilo claramente y justificálo con cuántos nets se cerrarían.

## Formato de respuesta

- Empezá con un resumen ejecutivo: `¿merece mover componentes? Sí/No` y `¿qué se gana?`.
- Luego la tabla de movimientos (si aplica).
- Finalmente la estrategia de ruteo por grupo, con bullets y coordenadas.
- No generes código Python; Devin lo aplicará/validará con `kicad-cli pcb drc` y `kicad-cli sch erc`.