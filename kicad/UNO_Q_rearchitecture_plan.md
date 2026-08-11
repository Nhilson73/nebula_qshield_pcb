# UNO Q Shield Re-architecture Plan

> **Estado (2026-08-11):** plan histórico; el board actual es 125 × 120 mm con DRC/ERC 0 y 47 nets desconectadas en Fase 5. Fuente de verdad actual en `docs/INSIGHT_FABRICATION_ROADMAP.md`.
>
> Branch: `devin/uno-q-rearchitecture`  
> Status: proposal ready for review. Implementation will be applied after approval.

## 1. Electrical re-mapping

The corrected symbol `Arduino_UNO_Q_Shield_Header_Corrected` (32 pins) and footprint `Arduino_UNO_Q_Shield` are already in the library after PR #32. The migration below follows the user's instruction: **I2C moved to D20/D21, A4/A5 reserved for analog, physical pull-ups on the shield**.

### 1.1 J21 pin / net migration table

| Old pin | Old net (PCB) | New pin | New name | New net | Notes |
|---------|---------------|---------|----------|---------|-------|
| 1 | `/PH_ADC` | 9 | A0/D14 | `/PH_ADC` | analog input |
| 2 | `/ORP_ADC` | 10 | A1/D15 | `/ORP_ADC` | analog input |
| 3 | `/TEMP_ADC` | 11 | A2/D16 | `/TEMP_ADC` | analog input |
| 4 | `/HUM_ADC` | 12 | A3/D17 | `/HUM_ADC` | analog input |
| 5 | `/CO2_ADC` | 13 | A4/D18 | `/CO2_ADC` | **analog only** |
| 6 | `/DO_ADC` | 14 | A5/D19 | `/DO_ADC` | **analog only** |
| 7 | `/12V_RAIL` | 8 | VIN | `/12V_RAIL` | |
| 8 | `GND` | 6 | GND | `GND` | |
| 9 | `GND` | 7 | GND2 | `GND` | |
| 10 | `/5V_RAIL` | 5 | +5V | `/5V_RAIL` | |
| 11 | `/3V3_RAIL` | 4 | +3V3 | `/3V3_RAIL` | |
| 12 | `/MCU_NRST` | 3 | ~{RST} | `/MCU_NRST` | |
| 13 | unconnected | 2 | IOREF | unconnected | leave NC |
| 14 | `/I2C_SDA` | 31 | D20/SDA | `/I2C_SDA` | **moved from A4** |
| 15 | `/I2C_SCL` | 32 | D21/SCL | `/I2C_SDA` | **moved from A5** |
| 25 | `/HMI_RX` | 15 | D0 | `/HMI_RX` | |
| 26 | `/HMI_TX` | 16 | D1 | `/HMI_TX` | |
| 27 | `/HX711_DOUT` | 17 | D2 | `/HX711_DOUT` | |
| 28 | `/HX711_SCK` | 18 | ~D3 | `/HX711_SCK` | |
| 29 | `/PUMP_DIR` | 19 | D4 | `/PUMP_DIR` | |
| 30 | `/PUMP_PWM` | 20 | ~D5 | `/PUMP_PWM` | |
| 31 | `/CO2_PWM` | 21 | ~D6 | `/CO2_PWM` | |
| 32 | `/CO2_SOL_CTL` | 22 | D7 | `/CO2_SOL_CTL` | |
| 33 | `/MCU_WDI` | 23 | D8 | `/MCU_WDI` | |
| 34 | `/CHILLER_CTL` | 24 | ~D9 | `/CHILLER_CTL` | |
| 35 | unconnected | 25 | ~D10 | unconnected | leave NC |
| 36 | unconnected | 26 | ~D11 | unconnected | leave NC |
| 37 | unconnected | 27 | D12 | unconnected | leave NC |
| 38 | `/LED_STATUS` | 28 | D13 | `/LED_STATUS` | |
| 39 | `GND` | 29 | GND | `GND` | |
| 40 | `GND` | 30 | AREF | **unconnected** | old GND on pin 40 must be disconnected |

### 1.2 I2C pull-ups

- Add two `R_0603_1608Metric` resistors on the Q-Shield.
- Reference designators: `R36` (SDA) and `R37` (SCL).
- Value: `4.7 kΩ` (1 %, 1/10 W).
- Connections:
  - `R36` pin 1 → `/3V3_RAIL`
  - `R36` pin 2 → `/I2C_SDA` (J21 pin 31)
  - `R37` pin 1 → `/3V3_RAIL`
  - `R37` pin 2 → `/I2C_SCL` (J21 pin 32)
- Proposed placement (resistor centers, top side, near J21 JDIGITAL row):
  - `R36`: `(66.04 mm, 88.90 mm)`
  - `R37`: `(68.58 mm, 88.90 mm)`

## 2. Mechanical placement

### 2.1 Recommended J21 origin

After checking a 2.54 mm grid over the 125 mm × 120 mm board, the best compromise between collision count and top-side mechanical clearance is:

```text
J21 footprint origin -> (5.08 mm, 35.56 mm)
UNO board on Q-Shield -> x =  5.08 mm .. 73.66 mm
                         y = 35.56 mm .. 88.90 mm
UNO footprint courtyard -> x =  3.81 mm .. 74.93 mm
                         y = 34.29 mm .. 90.17 mm
```

Why this origin:
- Keeps all UNO Q connectors and tall parts within the 125 mm × 120 mm board.
- Leaves a `5.08 mm` left margin for the USB-C connector body.
- Leaves a `25.44 mm` margin to the top board edge for the power jack / JCTL / JMedia cutouts (max y = `94.56 mm`).
- Only **10 components** must be relocated (see next section). Lower origins or centered origins create 30+ collisions.

### 2.2 Components that must be moved

The following 10 footprints overlap the `Arduino_UNO_Q_Shield` courtyard when J21 is at `(5.08, 35.56)`. Suggested new centers were found with a 1.27 mm packing search, avoiding the UNO area and other components.

| Ref | Footprint | Current center (mm) | Suggested new center (mm) | Rotation |
|-----|-----------|---------------------|---------------------------|----------|
| `D10` | `D_SMA` | (64.65, 51.92) | (78.74, 49.53) | 0° |
| `D11` | `D_SMA` | (72.15, 51.92) | (74.93, 82.55) | 0° |
| `F4` | `Fuse_0805_2012Metric` | (66.58, 55.12) | (74.93, 54.61) | 0° |
| `K1` | `Relay_SPDT_Omron_G5V-1` | (56.50, 42.62) | (74.93, 76.20) | 90° |
| `K2` | `Relay_SPDT_Omron_G5V-1` | (69.75, 42.62) | (74.93, 66.04) | 90° |
| `Q4` | `SOT-23` | (62.85, 56.10) | (74.93, 57.15) | 90° |
| `U16` | `DIP-8_W7.62mm` | (34.00, 45.00) | (74.93, 86.36) | 0° |
| `U17` | `SOIC-8_3.9x4.9mm_P1.27mm` | (64.85, 47.12) | (85.09, 82.55) | 0° |
| `U19` | `DIP-4_W7.62mm` | (56.67, 53.09) | (74.93, 34.29) | 90° |
| `U20` | `SOIC-8_3.9x4.9mm_P1.27mm` | (72.60, 47.12) | (67.31, 90.17) | 0° |

These moves are **placement-only suggestions**. After moving, the affected tracks (relays, diodes, opto/isolators, etc.) must be reviewed and re-routed in KiCad.

## 3. Edge.Cuts / keepout zones

All coordinates are **Q-Shield board-local**, computed by adding the J21 origin `(5.08, 35.56)` to the UNO-relative keepout table from `UNO_Q_shield_proposal.md`.

| Feature | Board-local x (mm) | Board-local y (mm) | Treatment |
|---------|--------------------|--------------------|-----------|
| USB-C connector | 2.08 .. 23.08 | 81.56 .. 94.56 | `Edge.Cuts` slot + all-layer keepout |
| Power button | 13.08 .. 19.08 | 86.06 .. 94.56 | `Edge.Cuts` slot + all-layer keepout |
| JCTL header | 17.08 .. 40.08 | 87.06 .. 94.56 | keepout (slot if header is tall) |
| Power jack / JMEDIA | 60.08 .. 77.08 | 85.56 .. 94.56 | `Edge.Cuts` slot + all-layer keepout |
| SPI2 / JSPI | 67.08 .. 77.08 | 68.56 .. 88.56 | keepout / partial cutout |
| QWIIC | 67.08 .. 77.08 | 50.56 .. 65.56 | keepout |
| USB-C / PMIC tall parts (left edge) | 2.08 .. 11.08 | 65.56 .. 94.56 | keepout |

Recommended clearance from any `Edge.Cuts` slot or keepout to Q-Shield copper/placement: **2.0 mm** preferred, **1.5 mm** absolute minimum.

## 4. Schematic update plan

1. Replace `J21` `lib_id` with `nebula_symbols:Arduino_UNO_Q_Shield_Header_Corrected`.
2. Update `J21` footprint property to `nebula_footprints:Arduino_UNO_Q_Shield`.
3. Expand the `(pin ...)` list from 31 to 32 entries, numbered `1` .. `32`.
4. Re-wire using the migration table in section 1.1. Keep `/I2C_SDA` and `/I2C_SCL` labels but route them to pins 31/32 instead of pins 13/14.
5. Add `R36` and `R37` pull-up resistors to the schematic, connected to `/3V3_RAIL`, `/I2C_SDA`, and `/I2C_SCL`.
6. Verify ERC.

> Note: `hmi_connectors.kicad_sch` currently contains duplicate local-label/wire blocks around the old `J21`. These should be cleaned during the re-wire to avoid duplicate net labels.

## 5. PCB update plan

1. Replace `J21` footprint with `nebula_footprints:Arduino_UNO_Q_Shield`.
2. Place `J21` at `(5.08, 35.56)`.
3. Remap every J21 pad net using section 1.1.
4. Move the 10 components in section 2.2 to their suggested coordinates.
5. Add `R36` and `R37` footprints and route them to `/3V3_RAIL` and pins 31/32.
6. Add the `Edge.Cuts` slots and keepout zones from section 3.
7. Re-route the broken analog tracks for `/CO2_ADC` and `/DO_ADC` (pins 13/14) as short, shielded tracks. Keep them away from I2C and power switching noise, with a 0.5 mm margin around existing tracks near `U20`/`Q1` per the design knowledge note.
8. Run `kicad-cli pcb drc` and `kicad-cli sch erc`.

## 6. Validation command

```bash
cd /home/ubuntu/repos/nebula_qshield_pcb
kicad-cli sch erc -o kicad/erc_rearch.json kicad/nebula_qshield.kicad_sch
kicad-cli pcb drc -o kicad/drc_rearch.json kicad/nebula_qshield.kicad_pcb
```

Target: **0 ERC violations** and **0 DRC errors**. Unconnected items are expected until re-routing is completed.

## 7. Expected outcome after approval

- `J21` uses the standard UNO R3/Q-compatible 32-pin footprint at a mechanically safe location.
- I2C is on `D20/D21` with physical `4.7 kΩ` pull-ups.
- `A4`/`A5` are dedicated to `CO2_ADC`/`DO_ADC` with clean analog return paths.
- Perimeter cutouts give access to USB-C, power button, JCTL, and SPI2/Qwiic.
- Schematic/PCB are ready for final cleanup and re-routing.
