# Nebula Q-Shield® — Bill of Materials (BOM) de Producción

> **Documento:** NQS-BOM-004 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Producción — Lista de Materiales
>
> **PCB:** Q-Shield v1.0 · **Tier:** Signature (fully populated)
>
> **Todos los componentes son RoHS 3 conformes (2011/65/EU + 2015/863)**

---

## 1. Resumen de Costos

| Categoría | Componentes | Costo unitario (100 uds) | Costo unitario (1000 uds) |
|-----------|-------------|--------------------------|---------------------------|
| Protección y potencia | 22 | $4.85 | $3.90 |
| Analógico (sensores) | 28 | $3.20 | $2.60 |
| Digital (I2C, RS485 bridge, HX711) | 18 | $4.50 | $3.60 |
| Actuadores (drivers) | 18 | $5.50 | $4.40 |
| Conectores | 21 | $6.30 | $5.10 |
| Pasivos (R, C) | 45 | $1.20 | $0.95 |
| PCB fabricación (4 capas, ENIG) | 1 | $8.00 | $4.50 |
| **TOTAL PCB Q-Shield®** | **153** | **$33.55** | **$25.05** |

> Los precios son estimados para componentes comprados en Digi-Key/Mouser con cantidades de 100 y 1000 unidades respectivamente. Los sensores y actuadores externos NO están incluidos (ver `HARDWARE_BUYING_GUIDE.md`).

---

## 2. BOM Completa — Componentes de Protección y Potencia

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|-------------|---------------|
| D1 | 1 | TVS diode, bidirectional | 15V, 400W | SMA | SMAJ15A | SMAJ15ALFCT-ND | $0.35 |
| D2 | 1 | Schottky diode | 40V, 3A | SMA | SS34 | SS34-E3/57TCT-ND | $0.28 |
| F1 | 1 | PTC resettable fuse | 1.1A hold / 2.2A trip | 1812 | MF-MSMF110/24X-2 | MF-MSMF110/24X-2CT-ND | $0.42 |
| F2 | 1 | PTC resettable fuse | 1.0A hold | 0805 | MF-PSMF110X-2 | MF-PSMF110X-2CT-ND | $0.18 |
| F3 | 1 | PTC resettable fuse | 0.5A hold | 0805 | MF-PSMF050X-2 | MF-PSMF050X-2CT-ND | $0.15 |
| F4 | 1 | PTC resettable fuse | 0.5A hold | 0805 | MF-PSMF050X-2 | MF-PSMF050X-2CT-ND | $0.15 |
| U1 | 1 | Buck converter | 4.5–28V in, 5V/3A out | SOT-23-6 | TPS54302DDCR | 296-50420-1-ND | $1.25 |
| L1 | 1 | Power inductor | 4.7 μH, 4A sat | 4×4×2mm | 744043004700 | 732-1260-1-ND | $0.48 |
| U2 | 1 | LDO regulator | 3.3V, 800mA | SOT-223 | AMS1117-3.3 | AMS1117-3.3CT-ND | $0.32 |
| FB1 | 1 | Ferrite bead | 600Ω @ 100MHz, 2A | 1206 | BLM31PG601SN1L | 490-5222-1-ND | $0.12 |

---

## 3. BOM Completa — Bloque Analógico

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|-------------|---------------|
| U3 | 2 | Dual op-amp, rail-to-rail | 1 MHz GBW | SOIC-8 | MCP6002-I/SN | MCP6002-I/SN-ND | $0.52 |
| D3 | 1 | TVS ESD, unidirectional | 5V clamp, 0.4pF | SOD-323F | PESD5V0S1BSF | 568-13204-1-ND | $0.15 |
| D4 | 1 | TVS ESD, unidirectional | 5V clamp | SOD-323F | PESD5V0S1BSF | 568-13204-1-ND | $0.15 |
| D5 | 1 | TVS ESD, unidirectional | 3.3V clamp | SOD-323F | PESD3V3S1BSF | 568-13206-1-ND | $0.15 |
| D6 | 1 | TVS ESD, unidirectional | 5V clamp | SOD-323F | PESD5V0S1BSF | 568-13204-1-ND | $0.15 |
| D7_1 | 1 | TVS ESD, unidirectional | 3.3V clamp | SOD-323F | PESD3V3S1BSF | 568-13206-1-ND | $0.15 |
| D8_1 | 1 | TVS ESD, unidirectional | 5V clamp | SOD-323F | PESD5V0S1BSF | 568-13204-1-ND | $0.15 |
| R3–R5, R9 | 4 | Resistor, thin film | 1 kΩ ±1% | 0402 | CRCW04021K00FKED | 541-1.00KLCT-ND | $0.02 |
| C11–C14 | 4 | Capacitor, MLCC | 100 nF X7R 50V | 0402 | CL05B104KO5NNNC | 1276-1001-1-ND | $0.01 |
| R4, R_PD | 6 | Resistor, pull-down | 10 MΩ ±5% | 0402 | CRCW040210M0JNED | 541-10.0MJCT-ND | $0.01 |
| R8 | 1 | Resistor, NTC series | 10 kΩ ±1% | 0402 | CRCW040210K0FKED | 541-10.0KLCT-ND | $0.02 |

---

## 4. BOM Completa — Bloque I2C y Digital

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|-------------|---------------|
| R10, R11 | 2 | Resistor, pull-up I2C | 4.7 kΩ ±1% | 0402 | CRCW04024K70FKED | 541-4.70KLCT-ND | $0.02 |
| D7, D8 | 1 | TVS ESD, dual-line I2C | 3.3V clamp, 0.5pF | SOT-23-3 | PESD3V3S2USF | 568-13207-1-ND | $0.22 |
| U4 | 1 | Digital isolator, 2-ch | 100 Mbps, 2.5kV | SOIC-8 | ISO7721DR | 296-46893-1-ND | $1.85 |
| U6 | 1 | 24-bit ADC, load cell | 80 SPS, gain 128 | SOP-16 | HX711 | — (LCSC: C124335) | $0.65 |
| R12 | 1 | Resistor, pull-up | 10 kΩ ±5% | 0402 | CRCW040210K0JNED | 541-10.0KJCT-ND | $0.01 |
| C19, C20 | 2 | Capacitor, desacoplo HX711 | 100 nF + 10 μF | 0402 + 0805 | — | — | $0.03 |
| U22 | 1 | I2C-to-UART bridge | SC16IS740, 64-byte FIFO | TSSOP-16 | SC16IS740IPW/Q900 | 568-13068-1-ND | $1.85 |
| U23 | 1 | Single inverter | SN74LVC1G04 | SOT-353/SC-70-5 | SN74LVC1G04DCKR | 296-11602-1-ND | $0.35 |
| Y1 | 1 | Crystal | 1.8432 MHz | HC-49-SD SMD | ABLS-1.8432MHZ-B4-T | 535-9930-1-ND | $0.45 |
| C31, C32 | 2 | Capacitor, carga cristal | 22 pF C0G 50V | 0402 | CL05C220JB5NNNC | 1276-1013-1-ND | $0.01 |
| C33 | 1 | Capacitor, desacoplo U22 | 100 nF X7R 50V | 0402 | CL05B104KO5NNNC | 1276-1001-1-ND | $0.01 |
| R38 | 1 | Resistor, pull-up IRQ | 10 kΩ ±1% | 0402 | CRCW040210K0FKED | 541-10.0KLCT-ND | $0.02 |

---

## 5. BOM Completa — Bloque Actuadores

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|-------------|---------------|
| U7 | 1 | Half-bridge gate driver | 600V, bootstrap | SOIC-8 | IR2104SPBF | IR2104SPBF-ND | $1.45 |
| Q1, Q2 | 2 | N-MOSFET, logic-level | 55V, 47A, 22mΩ | TO-220AB | IRLZ44NPBF | IRLZ44NPBF-ND | $1.10 |
| Q3, Q4 | 2 | N-MOSFET, small signal | 60V, 300mA | SOT-23 | 2N7002 | 2N7002-FDICT-ND | $0.08 |
| Q5 | 1 | N-MOSFET, logic-level | 55V, 47A | TO-220AB | IRLZ44NPBF | IRLZ44NPBF-ND | $1.10 |
| K1, K2 | 2 | Relay, SPST-NO | 12V coil, 5A/250VAC | THT | HF46F-12-HS1 | 255-5799-ND | $1.20 |
| U8, U9 | 2 | Optocoupler, dual | CTR 50–600% | DIP-8 | PC817X2NIP | — (Mouser: 852-PC817X2NIP0F) | $0.35 |
| U10, U11 | 2 | Optocoupler, single | CTR 50–600% | DIP-4 | PC817X1NIP | — (Mouser: 852-PC817X1NIP0F) | $0.18 |
| D9–D13 | 5 | Schottky diode, flyback | 40V, 3A | SMA | SS34 | SS34-E3/57TCT-ND | $0.28 |
| D11_2, D12_2 | 2 | Signal diode, flyback relay | 100V, 200mA | SOD-323 | 1N4148W | 1N4148WX-TPMSCT-ND | $0.03 |
| R13–R20 | 8 | Resistor, current limit | 1 kΩ ±5% | 0402 | CRCW04021K00JNED | 541-1.00KJCT-ND | $0.01 |
| C21, C28, C29 | 3 | Capacitor, desacoplo driver | 100 nF X7R | 0402 | CL05B104KO5NNNC | 1276-1001-1-ND | $0.01 |

---

## 6. BOM Completa — Conectores

| Ref | Qty | Descripción | Pines | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-----|-------------|---------------|
| J1 | 1 | BNC receptacle, panel mount | 1 | 31-221-RFX | ARF1065-ND | $1.85 |
| J2 | 1 | BNC receptacle, panel mount | 1 | 31-221-RFX | ARF1065-ND | $1.85 |
| J3 | 1 | JST-XH header, right angle | 3 | B3B-XH-A(LF)(SN) | 455-2248-ND | $0.15 |
| J4 | 1 | BNC receptacle, panel mount | 1 | 31-221-RFX | ARF1065-ND | $1.85 |
| J5 | 1 | JST-XH header, right angle | 2 | B2B-XH-A(LF)(SN) | 455-2247-ND | $0.12 |
| J6 | 1 | JST-XH header, right angle | 3 | B3B-XH-A(LF)(SN) | 455-2248-ND | $0.15 |
| J7–J13 | 7 | JST-SH header (Qwiic compat.) | 4 | SM04B-SRSS-TB(LF)(SN) | 455-1804-1-ND | $0.32 |
| J14 | 1 | Terminal block, rising clamp | 4 | 1757242 (Phoenix Contact) | 277-1274-ND | $0.85 |
| J_HMI | 1 | JST-XH header, HMI UART | 4 (5V/TX/RX/GND) | B4B-XH-A(LF)(SN) | 455-2249-ND | $0.15 |
| J17 | 1 | DC barrel jack, 2.1×5.5mm | 3 | PJ-002AH | CP-002AH-ND | $0.75 |
| J18–J20 | 3 | Terminal block, 2-pin | 2 | 1757229 (Phoenix Contact) | 277-1273-ND | $0.52 |
| J21 | 1 | Arduino UNO Q shield header | 32 | — (Arduino UNO R3/Q shield header set) | — | $1.50 |

---

## 7. BOM Completa — Pasivos (Reguladores)

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|---------------|
| C1 | 1 | MLCC, input filter | 100 μF 25V X5R | 1210 | GRM32ER61E107ME20L | $0.85 |
| C2 | 1 | Electrolytic, bulk | 470 μF 25V | Ø10×12.5 | UCD1E471MNL1GS | $0.45 |
| C3, C4 | 2 | MLCC, buck input | 22 μF 25V X5R | 0805 | GRM21BR61E226ME44L | $0.28 |
| C5, C6 | 2 | MLCC, buck output | 47 μF 10V X5R | 0805 | GRM21BR61A476ME15L | $0.35 |
| C7 | 1 | MLCC, bootstrap | 100 nF 50V X7R | 0402 | CL05B104KO5NNNC | $0.01 |
| C8 | 1 | MLCC, LDO input | 10 μF 10V X5R | 0805 | GRM21BR61A106KE19L | $0.08 |
| C9 | 1 | MLCC, LDO output | 22 μF 10V X5R | 0805 | GRM21BR61A226ME44L | $0.12 |
| C10 | 1 | Tantalum, LDO stab. | 10 μF 10V | 1206 | T491A106M010AT | $0.18 |
| C23–C29 | 7 | MLCC, IC decoupling | 100 nF 50V X7R | 0402 | CL05B104KO5NNNC | $0.01 |
| R1 | 1 | Resistor, feedback top | 100 kΩ ±1% | 0402 | CRCW0402100KFKED | $0.02 |
| R2 | 1 | Resistor, feedback bot | 24.9 kΩ ±1% | 0402 | CRCW040224K9FKED | $0.02 |

---

## 8. BOM Completa — LEDs Indicadores

| Ref | Qty | Descripción | Color | Encapsulado | MPN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|---------------|
| LED1 | 1 | LED indicator | Rojo | 0603 | 150060RS75000 | $0.05 |
| LED2 | 1 | LED indicator | Verde | 0603 | 150060GS75000 | $0.05 |
| LED3 | 1 | LED indicator | Azul | 0603 | 150060BS75000 | $0.08 |
| R_LED1 | 1 | Resistor, LED current | 4.7 kΩ ±5% | 0402 | CRCW04024K70JNED | $0.01 |
| R_LED2 | 1 | Resistor, LED current | 330 Ω ±5% | 0402 | CRCW0402330RJNED | $0.01 |
| R_LED3 | 1 | Resistor, LED current | 100 Ω ±5% | 0402 | CRCW0402100RJNED | $0.01 |

---

## 9. BOM Completa — ESD Protection (HMI UART)

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Digi-Key PN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|-------------|---------------|
| D_HMI | 1 | ESD protection, HMI UART dual-line | 3.3V dual, 0.4pF | SOT-23-3 | PESD3V3S2USF | 568-13207-1-ND | $0.22 |

---

## 10. BOM Completa — Sensor Clamp Diodes

| Ref | Qty | Descripción | Valor | Encapsulado | MPN | Precio (100+) |
|-----|-----|------------|-------|-------------|-----|---------------|
| D_CL1–D_CL3 | 3 | Dual Schottky, sensor clamp | 30V, 200mA | SOT-23-3 | BAT54S | $0.06 |

---

## 11. Componentes por Tier (DNP en tiers inferiores)

### Essential (Componentes a poblar: 98 de 153)

No poblar: CO₂ presión (A2), DO (A3), Humedad (A5), Motor driver (U7, Q1-Q2, U8-U9), CO₂ relay (K2, U10), CO₂ regulador (Q5), Chiller relay (K1, U11), RS485 bridge (U22, U23, Y1, C31-C33, R38), Cell density connector (J9), y sus pasivos asociados.

### Insight (Componentes a poblar: 134 de 153)

Poblar adicionalmente el bloque RS485/I2C bridge: U22, U23, Y1, C31, C32, C33, R38.
No poblar: Humedad (A5), Cell density connector (J9), Chiller relay (K1, U11, D6, R9, C14), y pasivos del canal de humedad.

### Signature (Fully populated: 153 de 153)

Todos los componentes poblados.

---

## 12. Información de Fabricación PCB

| Parámetro | Especificación |
|-----------|---------------|
| Capas | 4 |
| Material | FR-4 Tg170 (IT-180A) |
| Espesor | 1.6 mm ±10% |
| Cobre externo | 1 oz (35 μm) |
| Cobre interno | 1 oz (35 μm) |
| Acabado | ENIG (2–5 μin Au / 120–240 μin Ni) |
| Máscara soldadura | Verde LPI, ambos lados |
| Serigrafía | Blanca, ambos lados |
| Ancho mín. pista | 0.2 mm |
| Espacio mín. | 0.2 mm |
| Taladro mín. | 0.3 mm |
| Impedancia controlada | No |
| Via tenting | Sí (vías ≤ 0.4 mm) |
| Panelización | V-score, 2×3 panel |
| IPC Class | Clase 2 (productos electrónicos dedicados) |
| UL | UL 94V-0 flamabilidad |

### Fabricantes PCB Recomendados

| Fabricante | Ubicación | Lead time | Precio (100 uds, 4L ENIG) | Calidad |
|-----------|-----------|-----------|---------------------------|---------|
| **JLCPCB** | Shenzhen, China | 5–7 días | ~$4–$6/pcb | Buena (IPC-2) |
| **PCBWay** | Shenzhen, China | 5–7 días | ~$5–$8/pcb | Buena (IPC-2) |
| **Eurocircuits** | Bélgica, EU | 5–10 días | ~$15–$25/pcb | Excelente (IPC-2/3) |
| **OSH Park** | Portland, USA | 10–14 días | ~$10–$15/pcb | Excelente |
| **Würth Elektronik** | Alemania, EU | 7–14 días | ~$20–$35/pcb | Certificada (automotive) |

> **Para certificación EU:** Recomendamos Eurocircuits o Würth Elektronik (fabricación EU, trazabilidad completa, certificados de conformidad).

---

## 13. Notas de Ensamblaje

| Aspecto | Especificación |
|---------|---------------|
| Perfil de reflow | SAC305: pico 245°C, liquidus 217°C, 60–90s |
| Pasta de soldadura | SAC305 T4 (20–38 μm), no-clean flux ROL0 |
| Componentes THT | K1, K2 (relays), J14 (terminal block), Q1-Q2, Q5 (TO-220) — wave o manual |
| Inspección | AOI (Automated Optical Inspection) post-reflow |
| Prueba eléctrica | ICT (In-Circuit Test) o Flying Probe |
| Limpieza | No-clean: sin limpieza post-soldadura |
| Conformal coating | Opcional: Humiseal 1B73 (spray, curado UV) |

---

*Documento NQS-BOM-004 Rev 1.0 — Nebula Ecosystem® — BOM de Producción*
