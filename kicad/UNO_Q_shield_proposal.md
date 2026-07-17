# Arduino UNO Q shield footprint / header proposal

## 1. New footprint: `nebula_footprints:Arduino_UNO_Q_Shield`

The new footprint follows the official UNO Q CAD drill data (`48DMVQAD1_SGB-20250729a4-1-8.drl`) and the UNO Q datasheet (`ABX00162-datasheet.pdf`).

- Board origin (lower-left corner of the UNO Q board): `(0,0)`.
- UNO Q board size: `68.58 mm x 53.34 mm`.
- Mounting holes (NPTH, drill 3.2 mm):
  - `(13.97,  2.54)` lower-left
  - `(66.04,  7.62)` lower-right
  - `(66.04, 35.56)` upper-right
  - `(15.24, 50.80)` upper-left
- JANALOG row (bottom, y = 2.54 mm): 14 pins, left-to-right from pin 1 (BOOT) to pin 14 (A5/D19).
- JDIGITAL row (top, y = 50.80 mm): 18 pins, left-to-right from pin 15 (D0) to pin 32 (D21/SCL).
- Both rows reproduce the 2.54 mm pitch and the real gaps between connector sections.

### JANALOG pin assignment (left side of footprint)

| Pad | Name    | Typical function on UNO Q                         |
|-----|---------|---------------------------------------------------|
| 1   | BOOT    | MCU_BOOT0 boot strap                              |
| 2   | IOREF   | I/O voltage reference (3.3 V on UNO Q)          |
| 3   | ~RST    | MCU reset                                         |
| 4   | +3V3    | 3.3 V power out                                   |
| 5   | +5V     | 5 V power out                                     |
| 6   | GND     | Ground                                            |
| 7   | GND2    | Ground                                            |
| 8   | VIN     | 7-24 V input                                      |
| 9   | A0/D14  | PA4 / ADC0 / DAC0 / TIM2_CH1                      |
| 10  | A1/D15  | PA5 / ADC1 / DAC1 / TIM3_CH1                      |
| 11  | A2/D16  | PA6 / ADC2 / OPAMP2_INPUT+                        |
| 12  | A3/D17  | PA7 / ADC3 / OPAMP2_INPUT-                        |
| 13  | A4/D18  | PC1 / ADC4 / I2C3_SDA                             |
| 14  | A5/D19  | PC0 / ADC5 / I2C3_SCL                             |

### JDIGITAL pin assignment (right side of footprint)

| Pad | Name    | Typical function on UNO Q                         |
|-----|---------|---------------------------------------------------|
| 15  | D0      | PB7 / USART1_RX                                   |
| 16  | D1      | PB6 / USART1_TX                                   |
| 17  | D2      | PB3 / TIM2_CH2 / OPAMP2_OUTPUT                    |
| 18  | ~D3     | PB0 / TIM3_CH3                                    |
| 19  | D4      | PA12 / FDCAN1_TX                                  |
| 20  | ~D5     | PA11 / FDCAN1_RX                                  |
| 21  | ~D6     | PB1 / TIM3_CH4                                    |
| 22  | D7      | PB2 / TIM8_CH4N                                   |
| 23  | D8      | PB4 / TIM3_CH1                                    |
| 24  | ~D9     | PB8 / TIM4_CH3                                    |
| 25  | ~D10    | PB9 / SPI2_SS / TIM4_CH4                          |
| 26  | ~D11    | PB15 / SPI2_MOSI / TIM1_CH3N                      |
| 27  | D12     | PB14 / SPI2_MISO / TIM1_CH2N                      |
| 28  | D13     | PB13 / SPI2_SCK / TIM1_CH1N                       |
| 29  | GND     | Ground                                            |
| 30  | AREF    | Analog reference                                  |
| 31  | D20/SDA | PB11 / I2C2_SDA / TIM2_CH4                        |
| 32  | D21/SCL | PB10 / I2C2_SCL / TIM2_CH3                        |

## 2. New symbol: `nebula_symbols:Arduino_UNO_Q_Shield_Header_Corrected`

- 32 pins arranged 14+18 with the names above.
- Footprint property points to `nebula_footprints:Arduino_UNO_Q_Shield`.
- Pin 1 (BOOT, JANALOG) is marked with the square pad in the footprint.
- The old `Arduino_UNO_Q_Shield_Header` and `Arduino_UNO_Shield_2x20` remain in place so the current `J21` instance keeps the existing DRC/ERC baseline. Swapping `J21` to the corrected entries is a manual migration step.

## 3. J21 placement proposal

To keep the UNO Q board centered on the 100 x 100 mm Q-Shield:

```text
J21 footprint origin  ->  (15.71 mm, 23.33 mm)
UNO board on Q-Shield ->  x = 15.71 .. 84.29 mm
                         y = 23.33 .. 76.67 mm
```

This is a safe starting point. If it overlaps with already-placed components, move the origin in 2.54 mm steps (header pitch) so that the four mounting holes and the header rows stay on the existing 100 x 100 mm `Edge.Cuts`.

## 4. Keepout / cutout proposal

Add these zones on the Q-Shield **relative to the UNO Q board origin** (add the J21 `(x,y)` offset to convert to Q-Shield coordinates). Use `Dwgs.User` / `Cmts.User` for keepouts and `Edge.Cuts` for actual board slots where a connector or button must pass through the shield.

| Feature          | Board-local rectangle (x) | Board-local rectangle (y) | Treatment |
|------------------|---------------------------|---------------------------|-----------|
| USB-C connector  | -3.0 .. 18.0 mm           | 46.0 .. 59.0 mm           | Edge.Cuts slot + all-layer keepout |
| Power button     | 8.0 .. 14.0 mm            | 50.5 .. 59.0 mm           | Edge.Cuts slot + all-layer keepout |
| JCTL header      | 12.0 .. 35.0 mm           | 51.5 .. 59.0 mm           | Keepout (cutout only if the header is tall enough to require a slot) |
| Power jack / JMEDIA | 55.0 .. 72.0 mm        | 50.0 .. 59.0 mm           | Edge.Cuts slot + all-layer keepout |
| SPI2 / JSPI      | 62.0 .. 72.0 mm           | 33.0 .. 53.0 mm           | Keepout / partial cutout |
| QWIIC            | 62.0 .. 72.0 mm           | 15.0 .. 30.0 mm           | Keepout |
| USB-C/PMIC tall parts (left edge) | -3.0 .. 6.0 mm | 30.0 .. 59.0 mm | Keepout |

Recommended clearance between the Q-Shield copper/placement and these zones: **2.0 mm** minimum, **1.5 mm** absolute minimum.

## 5. Important design note: I2C / A4-A5 conflict

On the UNO Q, `A4/D18` and `A5/D19` are **the same physical pins** as `I2C3_SDA` and `I2C3_SCL`. The old symbol treated SDA/SCL as separate pins, which cannot be routed independently on this connector. The corrected symbol reflects the hardware:

- I2C3 bus: pins 13 (A4/D18) and 14 (A5/D19).
- Alternative I2C2 bus: pins 31 (D20/SDA) and 32 (D21/SCL).

If the design requires both analog A4/A5 and an independent I2C, either use the **Qwiic** connector or the **I2C2** digital pins (31/32) and do not connect anything to pins 13/14 for analog.

## 6. Migration checklist

1. In **Schematic**, change `J21` symbol to `nebula_symbols:Arduino_UNO_Q_Shield_Header_Corrected`.
2. Reassign the existing Q-Shield nets to the new pin numbers using the table above.
3. In **PCB**, change `J21` footprint to `nebula_footprints:Arduino_UNO_Q_Shield`.
4. Move `J21` to the proposed `(15.71, 23.33)` origin (or adjusted location).
5. Add the keepout / cutout polygons from section 4.
6. Re-run DRC/ERC and re-route any broken tracks.
