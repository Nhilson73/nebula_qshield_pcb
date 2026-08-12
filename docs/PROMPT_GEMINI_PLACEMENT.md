# Prompt for Gemini Spark / ChatGPT: Q-Shield component re-placement

## Context
You are assisting with a 4-layer KiCad 10 PCB named Nebula Q-Shield for the Arduino UNO Q form factor. The board is currently 125 mm × 120 mm and has 47 remaining unconnected nets after a FreeRouting pass. All ERC/DRC error-level violations are 0, but fabrication is blocked until unconnected nets reach 0.

## Files (for reference, do not edit)
- `kicad/nebula_qshield.kicad_pcb` — current layout
- `kicad/cluster_analysis.json` — generated footprint positions/bboxes/nets
- `docs/INSIGHT_FABRICATION_ROADMAP.md` — status and constraints

## Immutable constraints
1. `J21` (Arduino UNO Q header, 32 pins) must keep its exact footprint and mounting hole pattern at `(5.08, 35.56)`.
2. `I2C_SDA`/`I2C_SCL` must terminate on J21 pins 31/32 (D20/D21).
3. `A4`/`A5` (J21 pins 13/14) are reserved for `CO2_ADC`/`DO_ADC`; do not reassign.
4. 4.7 kΩ physical I2C pull-ups must remain.
5. Keepouts/cutouts for USB-C, power button, JCTL/SPI2 and Qwiic must remain.
6. 4-layer stackup is fixed: F.Cu signal, In1.Cu GND (used as extra signal during autorouting), In2.Cu split power, B.Cu signal/GND.
7. Board may be enlarged to 150 mm × 120 mm if it helps (enclosure not yet designed), but the UNO Q header stays at the same `(5.08, 35.56)` location.

## Problem to solve
The 47 unconnected nets are concentrated in:
- `12V_RAIL` stubs around `U17` (motor driver), `K1`/`K2` (relays), `Q1`/`Q2`/`Q5` (power MOSFETs).
- `3V3_RAIL` and `5V_RAIL` stubs around `U22` (RS485/I2C bridge), `U15` (MAX485), `U21` (I2C isolator), `U5`/`U8`/`U12` (analog front-end).
- Digital/analog stubs around `Q3`/`Q4` (relay coil drivers), `U18`/`U19` (optocouplers), `U20` (CO2 PWM).
- The top-right quadrant of the board (x ≈ 75–117 mm, y ≈ 90–118 mm) is 95 % empty.
- The right edge from y ≈ 38–90 mm is fully occupied by connectors `J15`/`J16`/`J17`/`J18`/`J19` and the analog BNCs `J2`/`J3`/`J5`.

## What you should output
Provide a **component placement proposal** in the following format:

```
Component | Current pos (mm) | Proposed pos (mm) | Justification
```

For every moved component include:
- Reference designator.
- New `(x, y)` coordinates (rotation unchanged; only translation).
- A one-sentence reason tied to net length, connector proximity or congestion reduction.

Propose moves for at least these groups:
1. **Actuator driver cluster** (`U16`, `U17`, `U18`, `U19`, `U20`, `K1`, `K2`, `Q1`, `Q2`, `Q3`, `Q4`, `Q5`, `D10`–`D14`, `F2`/`F3`/`F4`, `R24`–`R28`, `C27`) to the **top-right** near `J17`/`J18`/`J19`.
2. **RS485/I2C bridge cluster** (`U15`, `U22`, `U23`, `Y1`, `C31`/`C32`/`C33`, `R38`) to the **top-left** above `J21` and close to the `I2C_SDA`/`I2C_SCL` pull-ups.
3. Any other small passives that must move to avoid overlaps.

## Rules
- All proposed bounding boxes must stay inside the board outline (125 × 120 mm or enlarged 150 × 120 mm, clearly state which size you are using).
- Proposed positions must not overlap existing fixed components (see `cluster_analysis.json` for others) by at least 0.5 mm.
- Do not move `J21`, mounting holes `H1`/`H2`, the BNCs `J2`/`J3`/`J5`, terminal blocks `J15`–`J19`, Qwiic/EZO connectors `J8`–`J14`, the barrel jack `J1`, or the USB-C/power-button keepouts.
- Prefer short, direct routing between connectors and their driver/relay/valve.
- If you recommend enlarging the board to 150 mm × 120 mm, explicitly say so and explain which nets/components benefit.

## Deliverable
Return only the table of moves plus a short summary of expected impact on the 47 unconnected nets. Devin will then apply the coordinates in KiCad, re-export the DSN, run FreeRouting, validate DRC/ERC, and open a PR.
