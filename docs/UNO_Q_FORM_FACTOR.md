# UNO Q Form-Factor Reference for Nebula Q-Shield

> **Immutable design rule:** the Arduino UNO Q header/mounting pattern must be preserved inside the Nebula Q-Shield so the shield can be stacked on the UNO Q without mechanical or electrical conflicts. The outer dimensions of the Q-Shield (100 mm × 120 mm for the current design) can change, but the UNO Q pattern and keepouts cannot.

## 1. Source documents

All dimensions below come from the official Arduino UNO Q documentation:

- User manual / pinout: `https://docs.arduino.cc/hardware/uno-q/`
- CAD files / STEP / drill: `https://github.com/arduino/docs-content/tree/main/content/hardware/02.uno/boards/uno-q/downloads`
- SKU: `ABX00162` / `ABX00173`
- Last reviewed: 2026-08-10

## 2. UNO Q board envelope

| Parameter | Value |
|-----------|-------|
| PCB size | **68.58 mm × 53.34 mm** |
| Thickness | 1.6 mm (standard) |
| Corner radius | 4 × R1.6 mm |
| Bottom-side keepout | Components below 2 mm from the bottom surface so the board can stack on carrier bases |

The Q-Shield must leave the following UNO Q features physically accessible (use `Edge.Cuts` slots + `Eco1.User` keepouts):

- **USB-C (JUSB1)** on the board edge
- **Power button** near the top-left corner (when USB is at the top)
- **JCTL** 1.8 V 2×5 header near the top edge
- **JSPI** 6-pin SPI2 header on the right edge
- **QWIIC** 4-pin I2C connector on the right edge
- **JMEDIA** and **JMISC** on the left edge (if the shield is large enough to cover them, the Q-Shield should be cut out or raised to avoid interference)

## 3. Arduino-compatible headers (J21) — physical pinout

The UNO Q exposes the same 32-pin Arduino UNO R3/Q header pattern as a shield. The two headers are on the 68.58 mm edges, 2.54 mm pitch, 48.26 mm center-to-center distance.

### 3.1 Analog + power header — 14 pins

Bottom header, left-to-right (standard board orientation, USB on the left):

| # | Name | Notes |
|---|------|-------|
| 1 | `BOOT` | Special boot pin, normally not used by a shield |
| 2 | `IOREF` | Voltage reference |
| 3 | `~RESET` | Active-low reset |
| 4 | `+3V3` | 3.3 V rail |
| 5 | `+5V` | 5 V rail |
| 6 | `GND` | Ground |
| 7 | `GND2` | Ground |
| 8 | `VIN` | 7-24 VDC input |
| 9 | `A0 / D14` | Analog input (not 5 V tolerant) |
| 10 | `A1 / D15` | Analog input (not 5 V tolerant) |
| 11 | `A2 / D16` | Analog input |
| 12 | `A3 / D17` | Analog input |
| 13 | `A4 / D18` | Analog input / I2C3_SDA (shared) |
| 14 | `A5 / D19` | Analog input / I2C3_SCL (shared) |

### 3.2 Digital header — 18 pins

Top header, left-to-right. It is physically two connectors with a small gap between `D8` and `D7`:

Left connector (10 pins):

| # | Name | Notes |
|---|------|-------|
| 32 | `D21 / SCL` | I2C2_SCL |
| 31 | `D20 / SDA` | I2C2_SDA |
| 30 | `AREF` | Analog reference |
| 29 | `GND` | Ground |
| 28 | `D13 / SCK` | SPI2_SCK |
| 27 | `D12 / MISO` | SPI2_MISO |
| 26 | `D11 / MOSI` | SPI2_MOSI (PWM) |
| 25 | `D10 / SS` | SPI2_SS (PWM) |
| 24 | `D9` | PWM |
| 23 | `D8` | |

Right connector (8 pins):

| # | Name | Notes |
|---|------|-------|
| 22 | `D7` | |
| 21 | `D6` | PWM |
| 20 | `D5` | PWM |
| 19 | `D4` | |
| 18 | `D3` | PWM |
| 17 | `D2` | |
| 16 | `D1` | USART1_TX |
| 15 | `D0` | USART1_RX |

### 3.3 I2C pin conflict note

The UNO Q has two I2C peripherals exposed on the same physical pins:

- `Wire` (I2C3) is on `A4`/`A5` (pins 13/14).
- `Wire1` / `Wire2` (I2C2) is on `D20`/`D21` (pins 31/32).

For the **Nebula Insight** tier, the I2C bus used by the shield sensors is moved to `D20`/`D21` (pins 31/32) with 4.7 kΩ pull-ups on the shield. Pins `A4`/`A5` are reserved for `CO2_ADC` and `DO_ADC` only.

## 4. Recommended Q-Shield footprint coordinates

The following coordinates use an origin at the lower-left corner of the **UNO Q board outline**. The Q-Shield's `J21` footprint can be translated/rotated as long as these relative positions are preserved.

### 4.1 Mounting holes (M3, non-plated 3.2 mm)

| Hole | X (mm) | Y (mm) |
|------|--------|--------|
| H1 | 13.97 | 2.54 |
| H2 | 66.04 | 7.62 |
| H3 | 66.04 | 35.56 |
| H4 | 15.24 | 50.80 |

### 4.2 Header rows (pad centers, 1.05 mm drills)

Analog + power header (row 1, y = 2.54 mm), pin 1 at **X = 27.94 mm**, increasing 2.54 mm up to pin 14 at **X = 63.5 mm**.

Digital header (row 2, y = 50.8 mm). It is split into a 10-pin left connector and an 8-pin right connector:

- Left connector (pins 32 → 23, left-to-right):
  - Start **X = 18.8 mm**, pitch 2.54 mm, end **X = 41.66 mm**
- Gap of 4.06 mm
- Right connector (pins 22 → 15, left-to-right):
  - Start **X = 45.72 mm**, pitch 2.54 mm, end **X = 63.5 mm**

This means the leftmost pin of the digital header is `D21/SCL` (pin 32) and the rightmost pin is `D0` (pin 15).

### 4.3 Q-Shield outline example

If the Q-Shield is **100 mm × 120 mm** and `J21` is placed with the UNO Q lower-left at `(5.08, 35.56)` of the Q-Shield, the resulting absolute coordinates are the ones listed in the table above plus the offset. The shield must still leave clearance for the UNO Q connectors listed in section 2.

## 5. Design checklist for every Q-Shield revision

- [ ] `J21` footprint uses the exact 32-pad UNO R3/Q pattern.
- [ ] Digital header pad numbering goes **SCL/32 → D0/15** left-to-right on the top row (or equivalent after rotation), not the reverse.
- [ ] Mounting holes line up with the four UNO Q M3 holes.
- [ ] `Edge.Cuts` and `Eco1.User` keepouts provide clearance for USB-C, power button, JCTL, JSPI and QWIIC.
- [ ] Q-Shield size can be changed, but the UNO Q header/mounting pattern inside it must not be altered.
- [ ] For Insight, `A4`/`A5` are analog only; `D20`/`D21` carry the I2C bus with on-shield 4.7 kΩ pull-ups.

## 6. Validation command

```bash
docker run --rm -v $(pwd):/workspace kicad/kicad:10.0.5 \
  kicad-cli sch export netlist --format kicadxml \
  -o /workspace/kicad/uno_q.net \
  /workspace/kicad/nebula_qshield.kicad_sch
```

Verify that `J21` maps to the physical pinout above and that `kicad-cli sch erc --severity-all` returns 0 violations.
