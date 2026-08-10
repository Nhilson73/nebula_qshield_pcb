# Nebula Q-Shield® — Análisis Mecánico y Compactación

> **Documento:** NQS-MECH-008 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Diseño Mecánico PCB
>
> **Normativas de referencia:** IPC-2221B, IPC-7351C
>
> **Nota (2026-08-10):** el factor de forma y los recortes del Arduino UNO Q para el Q-Shield están documentados en `docs/UNO_Q_FORM_FACTOR.md`. Ese documento es la referencia inmutable; este archivo sigue siendo útil como análisis histórico pero contiene datos que requieren actualización (dimensiones, header J21, recortes).

---

## 1. Dimensiones del PCB

### 1.1 Factor de Forma

| Parámetro | Valor | Notas |
|-----------|-------|-------|
| **Dimensiones PCB** | 100 × 120 mm (puede variar) | El factor de forma UNO Q es inmutable; el board puede ser 100×100, 100×120 u otro tamaño |
| **Factor de forma UNO Q** | 68.58 × 53.34 mm | Patrón de headers y agujeros de montaje según `docs/UNO_Q_FORM_FACTOR.md` |
| **Área total** | 12,000 mm² | |
| **Espesor** | 1.6 mm ± 10% | Estándar IPC-2221B |
| **Capas** | 4 (Signal–GND–PWR–Signal) | |
| **Bordes** | Rounded 1 mm radius | Previene microfisuras |
| **Agujeros de montaje** | 4× M3 (3.2 mm drill) | Patrón UNO R3/Q; ver `docs/UNO_Q_FORM_FACTOR.md` |

### 1.2 Restricciones Geométricas Clave

| Restricción | Valor | Impacto |
|------------|-------|---------|
| J21 shield header UNO R3/Q | 32 pines (14+18), 50.8 mm entre filas | Patrón inmutable; el Q-Shield puede crecer pero este header no cambia |
| Clearance lateral J21 | ≥ 0.5 mm por lado | Respetar `copper_edge_clearance` de JLCPCB |
| Zona de ventilación / keepouts | USB-C, power button, JCTL, SPI2, Qwiic | Dejar recortes Eco1.User/Edge.Cuts según `docs/UNO_Q_FORM_FACTOR.md` |

---

## 2. Análisis de Compactación

### 2.1 Resumen por Zona Funcional

| Zona | Componentes | Área footprints | Max altura | % del PCB |
|------|-------------|-----------------|------------|-----------|
| **A — Potencia** | 30 | 389 mm² | 12.5 mm (C2) | 3.9% |
| **B — Analógica** | 71 | 949 mm² | 25.0 mm (BNC) | 9.5% |
| **C — Digital** | 21 | 465 mm² | 8.5 mm (terminal) | 4.6% |
| **D — Actuadores** | 30 | 1,186 mm² | 10.0 mm (TO-220) | 11.9% |
| **E — HMI** | 6 | 553 mm² | 8.5 mm (J21) | 5.5% |
| **TOTAL** | **158** | **3,541 mm²** | **25.0 mm** | **35.4%** |

### 2.2 Densidad de Ocupación

| Métrica | Valor | Evaluación |
|---------|-------|------------|
| Densidad TOP (footprints/área total) | 35.4% | Cómoda (< 50%) |
| Densidad TOP+BOT (dual-side) | ~17.7% | Muy holgada |
| Densidad zona media (sin J21 ni BNCs) | 31.0% | Cómoda |
| Componentes por cm² | 1.58 | Baja densidad |

**Referencia industrial:**
- < 50% = Densidad cómoda (routing fácil, producción estándar)
- 50–70% = Densidad ajustada (routing cuidadoso, pick-and-place preciso)
- \> 70% = Densidad alta (BGA, µBGA, interposer — no aplica aquí)

### 2.3 Veredicto de Compactación

**El board aprobado actualmente es 100 × 120 mm.** El factor de forma UNO Q no cambia; las dimensiones del Q-Shield pueden ajustarse. La densidad sigue siendo cómoda para un PCB de 4 capas con componentes THT y SMD mixtos, con margen para routing, guard rings, via fences y clearance de aislamiento galvánico.

---

## 3. Componentes Críticos — Perfil de Altura

### 3.1 Mapa de Alturas (Vista de Perfil Z)

```
    Altura (mm)
    25 │ ████                             ← BNC J2, J3, J5 (25mm)
       │ ████
    20 │ ████
       │ ████
    15 │ ████
       │ ████  ▓▓▓▓                       ← C2 electrolítico (12.5mm)
    12 │ ████  ▓▓▓▓  ░░░░                 ← J1 barrel jack (11mm)
    10 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒          ← Q1/Q2/Q5 TO-220 (10mm)
       │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████
     8 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████    ← J21 header, terminals (8.5mm)
       │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒
     7 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ← K1/K2 relays, JST-XH (7mm)
       │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒
     5 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ████  ← PC817 DIP (5mm)
       │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ████
     3 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ████  ████  ← Transformers (3mm)
     2 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ████  ████  ████  ← SMD ICs
     1 │ ████  ▓▓▓▓  ░░░░  ▒▒▒▒  ████  ▒▒▒▒  ████  ████  ████  ████ ← 0402/0805
    ───┼──────────────────────────────────────────────────────────────
       │  BNC   C2    J1    TO220  J21   K1/K2  PC817  Xfmr  SMD  Passives
```

### 3.2 Tabla de Componentes por Altura

| Categoría | Componentes | Altura (mm) | Ubicación recomendada |
|-----------|-------------|-------------|----------------------|
| **Muy alto (>10mm)** | J2, J3, J5 (BNC) | 25.0 | Borde superior, panel mount |
| | C2 (electrolítico) | 12.5 | Zona potencia, cerca de J1 |
| | J1 (barrel jack) | 11.0 | Borde izquierdo superior |
| **Alto (7–10mm)** | Q1, Q2, Q5 (TO-220) | 10.0 | Borde de zona actuadores |
| | J15, J16 (terminal 4P) | 8.5 | Borde zona digital |
| | J17–J19, J22 (terminal 2P) | 8.5 | Borde zona actuadores |
| | J21 (shield header) | 8.5 | Borde inferior completo |
| | K1, K2 (relays) | 7.0 | Centro zona actuadores |
| | J4, J6, J7, J20 (JST-XH) | 7.0 | Bordes |
| **Medio (3–7mm)** | U16, U18, U19 (PC817) | 5.0 | Zona actuadores |
| | J8–J14 (Qwiic) | 3.5 | Zona digital |
| | T1–T3 (transformers) | 3.0 | Zona analógica |
| **Bajo (<3mm)** | ICs SOIC-8, SOT-23 | 1.0–1.8 | Cualquier zona |
| | Pasivos 0402/0805 | 0.5–1.0 | Cualquier zona |

---

## 4. Cuellos de Botella Identificados

### 4.1 Cuello #1 — Conectores BNC (Crítico: Altura)

| Aspecto | Detalle |
|---------|---------|
| **Componentes** | J2 (pH), J3 (ORP), J5 (DO) |
| **Dimensión** | 15.0 × 12.0 mm footprint, **25.0 mm altura** |
| **Problema** | Protruyen 25mm sobre el PCB — el enclosure debe acomodar esta altura |
| **Espacio lineal** | 3× BNC = 45 mm mínimo de borde → cabe en 100 mm |

**Recomendación:** Montar BNCs en el **borde superior** del PCB con orientación vertical (panel mount). El enclosure debe tener aberturas en el panel frontal para los BNCs. Alternativamente, considerar BNC right-angle (90°) para reducir altura a ~12mm a costa de más profundidad.

```
    OPCIÓN A: Vertical (actual)          OPCIÓN B: 90° Right-angle
    
    ┌─────┐                               ═══════╗
    │ BNC │ 25mm                                  ║ 12mm
    │     │                               ────────╝
    └──┤├─┘                               │ BNC │
    ───────                               └─────┘
     PCB                                   PCB
```

### 4.2 Cuello #2 — J21 Shield Header (Crítico: Ancho)

| Aspecto | Detalle |
|---------|---------|
| **Componente** | J21 — Header Arduino UNO R3/Q, 32 pines (14+18) |
| **Dimensión** | ~68.6 mm de ancho × 53.3 mm de profundidad (patrón UNO Q) |
| **Problema** | El patrón es inmutable; el Q-Shield debe dejar holgura para USB-C, botón power, JCTL, SPI2/Qwiic |
| **Impacto** | El routing del shield header debe usar vías a L2/L3 inmediatamente y respetar los keepouts de `docs/UNO_Q_FORM_FACTOR.md` |

**Recomendación:** Es una restricción inherente al factor de forma. Routing de señales del shield header debe usar vías hacia L2/L3 inmediatamente después de los pads. Pistas de potencia del header deben usar la capa PWR (L3).

### 4.3 Cuello #3 — MOSFETs TO-220 (Altura + Térmico)

| Aspecto | Detalle |
|---------|---------|
| **Componentes** | Q1, Q2 (H-bridge), Q5 (CO2 valve) |
| **Dimensión** | 10.0 × 15.0 mm, **10.0 mm altura** |
| **Problema** | Altura + disipación térmica + tab=Drain aislado |
| **Área total** | 3 × 150 = 450 mm² |

**Recomendaciones:**
1. **Alternativa SMD:** Reemplazar IRLZ44N TO-220 por **IRLZ44NS** (D²PAK/TO-263), mismo die, 2.5mm altura, soldable por reflujo. Ahorra 7.5mm de altura por MOSFET.
2. Si se mantiene TO-220: montar verticalmente con heatsink clip. Pad de cobre aislado en PCB (tab=Drain).
3. Thermal vias bajo los pads: array 2×3, drill 0.3mm, conectados a copper pour en L4.

### 4.4 Cuello #4 — Electrolítico C2 (Altura)

| Aspecto | Detalle |
|---------|---------|
| **Componente** | C2 — 470µF/25V electrolítico radial |
| **Dimensión** | Ø10 × 12.5 mm |
| **Problema** | Componente más alto de la zona de potencia |

**Recomendación:** Reemplazar por capacitor **electrolítico SMD** o **polymer cap**:
- Opción A: Panasonic EEVFK1E471P (470µF/25V, SMD D10, 10.2mm altura) — reduce 2mm
- Opción B: 2× MLCC 100µF/25V 1210 (GRM32ER61E107ME20L) + C1 existente = 300µF total — reduce a 2mm altura, suficiente para bulk filtering con el buck converter TPS54302

### 4.5 Cuello #5 — Relays K1/K2 (Área)

| Aspecto | Detalle |
|---------|---------|
| **Componentes** | K1 (chiller), K2 (CO2 solenoid) |
| **Dimensión** | 12.0 × 12.0 × 7.0 mm cada uno |
| **Área total** | 2 × 144 = 288 mm² |

**Recomendación:** Mantener como están. Los relays HF46F son la opción más compacta para 5A/250VAC. Alternativas solid-state (SSR) serían más pequeñas pero más costosas y requieren heatsink para cargas inductivas.

---

## 5. Layout de Zonas Propuesto (100 × 120 mm — dimensiones ajustables)

### 5.1 Mapa de Zonas Actualizado

```
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │  100 mm                                                                          │
    │  ┌──────────────────────────────────────────────────────────────────────────┐    │
    │  │  ZONA A: POTENCIA (20×30mm)     │  ZONA B: ANALÓGICA (50×45mm)         │    │
    │  │  ┌─────────────────────┐        │  ┌──────────────────────────────────┐ │    │
    │  │  │ J1 (12V barrel jack)│        │  │ J2 (pH BNC)  J3 (ORP BNC)       │ │    │
    │  │  │ D1 TVS, F1 PTC     │        │  │ J5 (DO BNC)                      │ │    │
    │  │  │ D2 SS34            │        │  │ J4 (CO₂ JST) J6 (NTC) J7 (Hum) │ │    │
    │  │  │ U1 TPS54302 + L1   │        │  │                                  │ │    │
    │  │  │ U2 AMS1117         │        │  │ U4/U7/U10/U11 MCP6002 buffers   │ │    │
    │  │  │ C1, C2 (bulk caps) │        │  │ U5/U8/U12 SN6501 + T1-T3       │ │    │
    │  │  │ U3 TPS3823 + SW1   │        │  │ U6/U9/U13 AMC1301 (isolation)   │ │  100
    │  │  │ LED1-3, R4-R6      │        │  │ RC filters, ESD TVS              │ │  mm
    │  │  └─────────────────────┘        │  │ Guard ring GND                   │ │    │
    │  │                                  │  └──────────────────────────────────┘ │    │
    │  │  ZONA D: ACTUADORES (40×40mm)   │  ZONA C: DIGITAL (40×30mm)           │    │
    │  │  ┌─────────────────────────┐    │  ┌──────────────────────────────┐    │    │
    │  │  │ U16 PC817X2 (motor)    │    │  │ J8-J14 Qwiic connectors (7×)│    │    │
    │  │  │ U17 IR2104             │    │  │ U14 HX711 + J15 load cell   │    │    │
    │  │  │ Q1, Q2 IRLZ44N        │    │  │ R19-R20 I2C pull-ups        │    │    │
    │  │  │ D10, D11 flyback       │    │  │ D9 TVS I2C                  │    │    │
    │  │  │ J17 motor terminal     │    │  │ U15 MAX485 + J16 RS485     │    │    │
    │  │  │ K1, K2 relays          │    │  │ U21 ISO1541                 │    │    │
    │  │  │ U18, U19 PC817 (relay) │    │  │ LED4 status + R23          │    │    │
    │  │  │ Q3, Q4 2N7002          │    │  │ J20 HMI UART (JST-XH 4P)  │    │    │
    │  │  │ D12, D13 flyback       │    │  └──────────────────────────────┘    │    │
    │  │  │ J18, J19, J22 terminals│    │                                      │    │
    │  │  │ Q5 + D14 (CO2 valve)   │    │                                      │    │
    │  │  │ R28, C27, U20 (CO2 PWM)│    │                                      │    │
    │  │  │ F2-F4 PTC fuses        │    │                                      │    │
    │  │  └─────────────────────────┘    │                                      │    │
    │  │                                                                        │    │
    │  │  ┌──────────────────────────────────────────────────────────────────┐  │    │
    │  │  │            J21 — ARDUINO UNO Q SHIELD HEADER (2×20)              │  │    │
    │  │  │                        98 mm                                      │  │    │
    │  │  └──────────────────────────────────────────────────────────────────┘  │    │
    │  └──────────────────────────────────────────────────────────────────────────┘    │
    └──────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Dimensiones por Zona

| Zona | Dimensión estimada | Área | Componentes | Ocupación |
|------|-------------------|------|-------------|-----------|
| A — Potencia | 20 × 30 mm | 600 mm² | 389 mm² fp | 65% |
| B — Analógica | 50 × 45 mm | 2,250 mm² | 949 mm² fp | 42% |
| C — Digital | 40 × 30 mm | 1,200 mm² | 465 mm² fp | 39% |
| D — Actuadores | 40 × 40 mm | 1,600 mm² | 1,186 mm² fp | 74% |
| E — J21 strip | 100 × 8 mm | 800 mm² | 553 mm² fp | 69% |
| **Margen/routing** | — | ~3,550 mm² | — | **35% libre** |

### 5.3 Reglas de Separación entre Zonas

| Frontera | Clearance | Método |
|----------|-----------|--------|
| Analógica ↔ Actuadores | ≥ 5 mm | Guard ring GND + via fence |
| Analógica ↔ Digital | ≥ 3 mm | Guard ring GND |
| Potencia ↔ Analógica | ≥ 3 mm | Plano GND continuo debajo |
| Aislamiento galvánico (pH/ORP/DO) | ≥ 2.5 mm | Slot PCB + creepage |
| Relay contactos (K1/K2) ↔ baja tensión | ≥ 2.5 mm | IPC-2221B 300V AC |

---

## 6. Restricciones para Enclosure

### 6.1 Perfil de Altura del Enclosure

| Zona del enclosure | Altura mín. interna | Componente limitante |
|--------------------|---------------------|---------------------|
| Panel frontal (BNC) | 25 mm + 5 mm clearance = 30 mm | J2, J3, J5 |
| Zona potencia | 12.5 mm + 3 mm = 15.5 mm | C2 electrolítico |
| Zona actuadores | 10 mm + 3 mm = 13 mm | Q1, Q2, Q5 TO-220 |
| Zona digital | 8.5 mm + 3 mm = 11.5 mm | J15, J16 terminals |
| Bajo PCB (standoffs) | 10 mm | Nylon standoffs |

**Altura total mínima del enclosure:** 30 mm (tapa) + 1.6 mm (PCB) + 10 mm (standoffs) = **41.6 mm**

### 6.2 Accesos de Panel

| Panel | Aberturas | Componentes |
|-------|-----------|-------------|
| Frontal (superior) | 3× BNC, 3× JST-XH (J4, J6, J7) | Sensores |
| Lateral izquierdo | J1 (12V DC), J17-J19, J22 (terminals) | Potencia/actuadores |
| Lateral derecho | J8-J14 (Qwiic ×7), J15 (load cell) | I2C/digital |
| Trasero | J20 (HMI UART), J16 (RS485) | Comunicación |
| Inferior | J21 (shield header) → conecta al Arduino UNO Q | Host board |

---

## 7. Recomendaciones de Optimización (Opcionales)

### 7.1 Sustituciones de Componentes para Reducir Altura

| Componente actual | Alternativa | Ahorro altura | Costo delta | Prioridad |
|-------------------|-------------|---------------|-------------|-----------|
| Q1/Q2/Q5 IRLZ44N TO-220 | IRLZ44NS D²PAK | -7.5 mm/each | +$0.20/each | Alta |
| C2 470µF/25V radial | 2× MLCC 100µF 1210 | -10.5 mm | +$0.85 total | Media |
| K1/K2 HF46F relay | G5V-1-DC12 (Omron) | -2 mm | +$0.50/each | Baja |
| BNC vertical | BNC 90° right-angle | -13 mm | +$0.50/each | Enclosure-dependent |

### 7.2 Componentes Candidatos para Cara Inferior (BOT)

Mover a BOT para reducir congestión TOP:

| Componente | Footprint | Motivo |
|-----------|-----------|--------|
| Pasivos 0402 (R, C) | ~50 piezas | Bajo perfil, soldable por reflujo |
| D3-D8 TVS SOD-323F | 6 piezas | Bajo perfil |
| D19-D24 BAT54 SOD-323 | 6 piezas | Bajo perfil |
| Test points TP1-TP12 | 12 pads | Debug access desde abajo |

---

## 8. Resumen Ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| **¿Cabe todo en 100×100mm?** | **✅ Sí** — densidad de 35.4% es cómoda |
| **¿Se requiere PCB más grande?** | **No** — 100×100mm tiene 35% de margen libre |
| **Cuello de botella principal** | Zona de actuadores (74% ocupación local) |
| **Componente más crítico (altura)** | BNC connectors (25mm) → define enclosure |
| **Componente más crítico (área)** | J21 shield header (490 mm², 98% del ancho) |
| **Recomendación #1** | Sustituir TO-220 por D²PAK (reduce 7.5mm altura) |
| **Recomendación #2** | Sustituir C2 electrolítico por 2× MLCC 1210 |
| **Recomendación #3** | Mover pasivos 0402/SOD-323 a cara BOT |

---

*Documento NQS-MECH-008 Rev 1.0 — Nebula Ecosystem® — Análisis Mecánico PCB*
