# Hoja de Ruta — Fabricación JLCPCB Nebula Fermentation® Insight

**Meta:** Liberar el PCB `Nebula Q-Shield` para fabricación en [JLCPCB](https://jlcpcb.com/) con el tier **Insight** (GPS, RTC, pH, ORP, temperatura, CO₂, DO, bomba, celda de carga, chiller, gas solenoide). El tier **Signature** añade sensores de densidad celular Hamilton (TCD + ACD) vía RS485; el canal de humedad queda eliminado/DNP y la válvula PWM de gas queda DNP en todos los tiers.

**Repo válido de firmware:** `Nhilson73/Nebula_ArduinoAPPLab_UNOQ` (`nebula_qshield/sketch/sketch.ino`).  
**Repo en standby:** `Nhilson73/Nebula_UNOQ_ArduinoIDE_Core` (no usar para esta bitácora).

---

## Checklist Maestra

### Fase 0 — Congelar pinout J21 (Insight)
- [x] Validar `J21` contra `sketch.ino` de `Nebula_ArduinoAPPLab_UNOQ`.
- [x] Decidir destino de `D4`: se asigna a `/MCU_WDI`; el firmware `Nebula_ArduinoAPPLab_UNOQ` no usa `D4`, por lo que el `loop()` debe togglear este pin para alimentar el watchdog TPS3823 (o usarse soft-WD).
- [x] Confirmar mapeo final A0-A5 y D0-D13 en `hmi_connectors.kicad_sch` y `nebula_qshield.kicad_pcb`.
- [x] Documentar pinout aprobado en esta bitácora.

### Fase 1 — KiCad 10 y sincronización esquemático ↔ PCB
- [x] Convertir `kicad/nebula_qshield.kicad_pcb` a formato KiCad 10 (ya estaba en 10.0.5).
- [x] Sincronizar esquemático ↔ PCB con forward-annotation headless (`tools/apply_phase1_minimal.py` + `tools/sexpr.py`).
- [x] Traer los 7 footprints faltantes:
  - `U22` SC16IS740
  - `U23` SN74LVC1G04
  - `Y1` 1.8432 MHz
  - `C31`, `C32` 22 pF
  - `C33` 100 nF
  - `R38` 10 kΩ
- [x] Verificar paridad con `compare_pcb_to_netlist.py`: 0 missing footprints, 0 net mismatches.
- [x] Validación: `kicad-cli sch erc --severity-all` = 0 violaciones; `kicad-cli pcb drc --severity-error` = 0 violaciones.

### Fase 2 — Mecánica y Edge.Cuts
- [x] Revisar/recolocar `Edge.Cuts`: los recortes interiores para USB-C/power jack y los keepouts `Eco1.User` para USB-C/PMIC, JCTL, SPI2/Qwiic se mantienen según el plan aprobado en `kicad/UNO_Q_rearchitecture_plan.md`.
- [x] Corregir conflicto entre `F.SilkS` de `J21` y los `Edge.Cuts`: se eliminó el rectángulo de silkscreen del footprint `Arduino_UNO_Q_Shield` (tanto en el PCB como en la librería) porque se solapaba con los recortes del board; el courtyard `F.CrtYd` y el outline `F.Fab` se conservan.
- [x] Revisar holguras mecánicas para USB-C, botón de power, JCTL, SPI2/Qwiic (ver `docs/UNO_Q_FORM_FACTOR.md` y keepouts `Eco1.User`).
- [x] Validar que todos los pads de `J21` y agujeros de montaje queden dentro del board 100 mm × 120 mm.
- [x] Confirmar dimensiones finales del board (100 mm × 120 mm) y posición `J21` (5.08, 35.56).
- [ ] Pendiente posterior: ajustar `copper edge clearance` y slots de conectores grandes (BNC, terminal blocks, DC barrel, HMI) en Fases 4–5 cuando se ruteen esas zonas.

### Fase 3 — Reparar nets críticas
- [x] `U15` pin 8 (`VCC`) → red `/3V3_RAIL` (no `/5V_RAIL`).
- [x] `U15` pines `RO`, `DI`, `DE`, `~RE` → conectar a nets `RS485_RO`, `RS485_DI`, `RS485_DE` hacia `U22`/`U23`.
- [x] `J21` pin 25 (`D10`) → `/RS485_IRQ`.
- [x] `J21` pines 19, 21, 23, 24 → corregir a `/MCU_WDI`, `/PUMP_DIR`, `/CHILLER_CTL`, `/CO2_PWM` según pinout aprobado.
- [x] Unificar `AGND` y `PGND` a `GND` en el PCB (no quedan nets `AGND`/`PGND` en el layout).
- [x] `R36`/`R37`: corregir asignación de pines en esquemático para evitar warnings de paridad.
- [x] `T1`/`T2`/`T3`: el símbolo `Transformer_SP_2S` tiene 7 pines, pero el footprint Wuerth 750315371 tiene 6 pads. Se movió `*_SEC_B` del pin 7 al pin 6 (pad físico existente) y se no-conectó el pin 7 sobrante; `*_SEC_A` permanece en pin 4, `GND_ISO_*` en pin 5. Paridad esquemático/PCB corregida.

### Fase 4 — Ruteo Fase A (Potencia)
- [x] Definir/rellenar plano `GND` en L2 (`In1.Cu`) y cobertura `GND` en `B.Cu`: polígonos extendidos a toda el área del board (100 × 120 mm) y zonas rellenadas con `kicad-cli pcb drc --refill-zones`.
- [ ] Definir/rellenar planos `3V3_RAIL`, `5V_RAIL`, `12V_RAIL` en `In2.Cu`/`B.Cu` según zonas de potencia. **Bloqueo identificado:** la zona `/12V_RAIL` actualmente tiene un polígono de 100 × 100 mm con prioridad 1 que solapa con las islas `/5V_RAIL` y `/3V3_RAIL` en `In2.Cu`; requiere rediseño como split-planes o islas con prioridades y net-ties antes de rellenar.
- [ ] Rutear `VIN_12V`, `12V_FUSED`, `5V_RAIL`, `3V3_RAIL`, `EN_UVLO`, `FB` cumpliendo netclasses (`Power`, `HighCurrent`).
- [ ] Verificar anchos mínimos: señales 0.2 mm, power 0.5 mm, `RelayHV` 1.0 mm / 2.5 mm clearance.

### Fase 5 — Ruteo Fase B (Señales Insight)
- [ ] Rutear señales analógicas `PH_ADC`, `ORP_ADC`, `TEMP_ADC`, `CO2_ADC`, `DO_ADC` en F.Cu, cortas y alejadas del buck.
- [ ] Crear islas galvánicas independientes en B.Cu/In2.Cu para `GND_ISO_PH`, `GND_ISO_ORP`, `GND_ISO_DO` y `VDD_ISO_*`.
- [ ] Rutear `HX711_DOUT`/`HX711_SCK` (D2/D3).
- [ ] Rutear `I2C_SDA`/`I2C_SCL` (D20/D21) con pull-ups `R36`/`R37`.
- [ ] Rutear puente RS485 (`U22-U23-U15-J16`): cristal, capacitores, `~IRQ`, `~RTS`/inversor, `RS485_A`/`RS485_B`.

### Fase 6 — Ruteo Fase C (Actuadores, limpieza, DRC)
- [ ] Rutear actuadores Insight:
  - `PUMP_PWM` (D5) y `PUMP_DIR` (D6)
  - `CO2_SOL_CTL` (D7) → solenoide único de gas (CO₂/H₂) en J18
  - `CHILLER_CTL` (D8) → relé K2/J19
  - `CO2_PWM` (D9) → DNP all tiers (válvula proporcional no poblada)
- [ ] Canal `/HUM_ADC` (A3) eliminado; no rutear a conector.
- [ ] Aplicar pase FreeRouting controlado o manual para nets restantes.
- [ ] Limpieza de silkscreen, revisión de `silk_overlap` y `silk_edge_clearance`.
- [ ] `kicad-cli sch erc --severity-all` = 0 violaciones.
- [ ] `kicad-cli pcb drc --severity-error` = 0 violaciones (unconnected items aceptables previo a envío si son intencionales, pero idealmente < 50).

### Fase 7 — Salidas JLCPCB y PR final
- [ ] Validar design rules de JLCPCB:
  - mínimo track/space: 0.1 mm (4 mil)
  - mínimo drill: 0.2 mm
  - edge clearance: ≥ 0.2 mm
- [ ] Generar Gerbers: `kicad-cli pcb export gerbers --output production/gerber/ ...`
- [ ] Generar drill: `kicad-cli pcb export drill --output production/drill/ ...`
- [ ] Generar position file: `kicad-cli pcb export pos ...`
- [ ] Generar BOM (Insight): `kicad-cli sch export bom ...` marcando componentes Signature como DNP en variante.
- [ ] Verificar visualmente capas en Gerber Viewer o KiCad Gerber Viewer.
- [ ] Crear PR final, validar CI verde, mergear.
- [ ] Subir archivos a JLCPCB y elegir capas/terminación (ENIG, FR-4 Tg170, 4 capas, 1.6 mm).

---

## Pinout J21 de referencia (Insight)

| Pin | Función | Net |
|-----|---------|-----|
| 1 | `BOOT` | NC |
| 2 | `IOREF` | NC |
| 3 | `~RST` | `/MCU_NRST` |
| 4 | `+3V3` | `/3V3_RAIL` |
| 5 | `+5V` | `/5V_RAIL` |
| 6 | `GND` | `GND` |
| 7 | `GND2` | `GND` |
| 8 | `VIN` | `/12V_RAIL` |
| 9 | `A0/D14` | `/PH_ADC` |
| 10 | `A1/D15` | `/ORP_ADC` |
| 11 | `A2/D16` | `/TEMP_ADC` |
| 12 | `A3/D17` | `/HUM_ADC` — canal humedad eliminado; DNP all tiers |
| 13 | `A4/D18` | `/CO2_ADC` |
| 14 | `A5/D19` | `/DO_ADC` |
| 15 | `D0` | `/HMI_RX` |
| 16 | `D1` | `/HMI_TX` |
| 17 | `D2` | `/HX711_DOUT` |
| 18 | `D3` | `/HX711_SCK` |
| 19 | `D4` | `/MCU_WDI` — el firmware debe togglear `D4` para alimentar WDI |
| 20 | `D5` | `/PUMP_PWM` |
| 21 | `D6` | `/PUMP_DIR` |
| 22 | `D7` | `/CO2_SOL_CTL` |
| 23 | `D8` | `/CHILLER_CTL` — Insight+ |
| 24 | `D9` | `/CO2_PWM` — DNP all tiers (gas único por solenoide D7/K1/J18) |
| 25 | `D10` | `/RS485_IRQ` |
| 26 | `~D11` | NC |
| 27 | `D12` | NC |
| 28 | `D13` | `/LED_STATUS` |
| 29 | `GND` | `GND` |
| 30 | `AREF` | NC |
| 31 | `D20/SDA` | `/I2C_SDA` |
| 32 | `D21/SCL` | `/I2C_SCL` |

---

## Anotaciones / Bitácora

- `2026-08-10`: Forense inicial. PCB en `main` desfasado respecto al esquemático. Ver `kicad/FORENSIC_REPORT.md`.
- `2026-07-09`: Fase 0 completada. Netlist generado con `kicad-cli sch export netlist` (KiCad 10.0.5) confirma que `J21` pines 9–32 coinciden con `sketch.ino` de `Nebula_ArduinoAPPLab_UNOQ`. ERC `--severity-all` = 0 violaciones. Se corrigieron comentarios desactualizados en `analog_acquisition.kicad_sch` y `hmi_connectors.kicad_sch`.
- `2026-07-09`: Se creó `docs/UNO_Q_FORM_FACTOR.md` como referencia permanente del factor de forma UNO Q y se corrigió el footprint `Arduino_UNO_Q_Shield` (`kicad/lib/nebula_footprints.pretty/Arduino_UNO_Q_Shield.kicad_mod`) para que la fila digital vaya de `D21/SCL` (pin 32) a `D0` (pin 15), coincidiendo con el CAD oficial del UNO Q. Se añadió nota: el Q-Shield puede cambiar de tamaño, pero el patrón de headers/orificios UNO Q no.
- `2026-07-09`: Fase 2 — mecánica y Edge.Cuts. Se eliminó el rectángulo `F.SilkS` del footprint `Arduino_UNO_Q_Shield` (PCB y librería) para resolver los warnings de ese footprint contra los recortes interiores del board; se limpió un paréntesis de cierre huérfano en `Edge.Cuts`. Validación: `kicad-cli pcb drc --severity-error` = 0 violaciones; `kicad-cli sch erc --severity-all` = 0 violaciones. El DRC `--severity-warning` reporta **447 warnings** (199 `silk_overlap`, 199 `silk_over_copper`, 43 `silk_edge_clearance`, 5 `isolated_copper`, 1 `lib_footprint_mismatch`), producto del placement denso y de que el board aún no está ruteado; se abordarán en Fases 4–5. Se ajustó `docs/INSIGHT_FABRICATION_ROADMAP.md`, `docs/08_MECHANICAL_ANALYSIS.md` y `04_BOM_PRODUCTION.md`; se corrigieron los 5 findings de Devin Review de PR #40 (`sexpr.py`, `compare_pcb_to_netlist.py`, `apply_phase1_minimal.py`, posición de `C31/C32/C33`, y BOM de los 7 componentes RS485 bridge).
- `2026-07-09`: Redefinición de tiers. Se fijó: **Essential** (GPS, RTC, temp, pH, ORP), **Insight** (Essential + CO₂, DO, HX711, chiller, recirculación, solenoide gas), **Signature** (Insight + TCD + ACD Hamilton por RS485). Humedad y válvula PWM quedan DNP en todos los tiers. Se corrigió `tools/list_actual_components.py` y `tools/apply_tier_dnp4.py` para manejar el formato s-expresión expandido de `kicad/hmi_connectors.kicad_sch` (anteriormente se ignoraban J20, J21, R36, R37 y D15-D18). Conteos finales: Essential 88 / Insight 137 / Signature 146 de 163 placements únicos. Validación: `kicad-cli sch erc --severity-all` = 0 violaciones; `kicad-cli pcb drc --severity-error` = 0 violaciones (332 desconectados baseline).
