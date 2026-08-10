# Nebula Q-Shield® PCB

**Precision Fermentation Monitor** — PCB shield de 4 capas para el Arduino UNO Q, con sensores de fermentación, control de actuadores, HMI UART y trazabilidad integrada al ecosistema Nebula.

Built by [Cafelium SRL](https://github.com/Nhilson73) · Dominican Republic

> **Parte del ecosistema [Nebula Q-Shield — Arduino App Lab](https://github.com/Nhilson73/Nebula_ArduinoAPPLab_UNOQ)**
>
> **Awards:** I+D Lab INDOTEL 2025 · CREE Banreservas 2026 · Pitch4FUN 2026
>
> **Firmware source of truth:** [`Nhilson73/Nebula_ArduinoAPPLab_UNOQ`](https://github.com/Nhilson73/Nebula_ArduinoAPPLab_UNOQ). No usar `Nebula_UNOQ_ArduinoIDE_Core` para validaciones de pinout/hardware.
>
> **Estado actual:** esquemático completo validado (ERC 0 violaciones), PCB migrado a KiCad 10.0.5, factor de forma UNO Q aplicado, dimensiones 100 mm × 120 mm, Fase 4 de ruteo de potencia pendiente de revisión en KiCad GUI.

---

## ¿Qué es el Q-Shield®?

El Q-Shield® es un **PCB shield de 4 capas** que se monta sobre el Arduino UNO Q (STM32U585 MCU + Qualcomm QRB2210 MPU), convirtiendo la placa en un sistema completo de monitoreo y control de fermentación para café y cacao de especialidad.

Se fabrica como **una sola PCB** para los tres tiers. La diferencia entre tiers se logra poblando o dejando en DNP ciertos componentes; el firmware selecciona el tier en tiempo de compilación.

```
┌──────────────────────────────────────────────────────────────────┐
│                    NEBULA Q-SHIELD® PCB v1.0                     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ POTENCIA     │  │  ANALÓGICO    │  │     DIGITAL          │   │
│  │              │  │              │  │                      │   │
│  │ 12 V input   │  │ pH  (A0)     │  │ I2C bus (D20/D21)    │   │
│  │ Buck 12→5 V  │  │ ORP (A1)     │  │ HX711 (D2/D3)        │   │
│  │ LDO 5→3.3 V  │  │ Temp (A2)    │  │ GPS + RTC (I2C)      │   │
│  │ TVS + PTC    │  │ CO2 (A4)     │  │ RS485 bridge (Sig.)  │   │
│  │ Schottky     │  │ DO  (A5)     │  │ HMI UART             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ACTUADORES (opto-aislados) — Insight+                  │   │
│  │  Recirculación · Solenoide gas · Chiller                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CONECTOR ARDUINO UNO Q / R3 (32-pin shield header)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Hardware Tier Model

Una sola PCB para los 3 tiers — los componentes no poblados (DNP) se seleccionan en fabricación:

| Tier | Sensores / Funciones | Actuadores | Placements poblados |
|------|----------------------|-----------|---------------------|
| **Essential®** | GPS (altitud), RTC/timestamp, temperatura, pH, ORP, HMI | — | 88 / 163 |
| **Insight®** | Essential + CO₂ (presión), DO, celdas de carga, I2C bus D20/D21 | Recirculación, solenoide gas, chiller | 137 / 163 |
| **Signature®** | Insight + densidad celular total (TCD) + activa (ACD) Hamilton vía RS485 | Igual que Insight | 146 / 163 |

- Convención DNP en el campo `DNP`: lista los tiers en los que el componente **no** se pobla.
- Canal de humedad y válvula PWM de gas quedan eliminados/DNP en todos los tiers.
- El pinout detallado de `J21` está en `docs/INSIGHT_FABRICATION_ROADMAP.md`.

---

## Componentes principales

| # | Componente | Interfaz | Tier |
|---|-----------|----------|------|
| 1 | Sensor pH | Analógico A0 / I2C EZO | Essential+ |
| 2 | Sensor ORP | Analógico A1 / I2C EZO | Essential+ |
| 3 | Sensor temperatura | Analógico A2 | Essential+ |
| 4 | GPS u-blox SAM-M8Q (altitud por GPS) | I2C 0x42 | Essential+ |
| 5 | RTC DS3231 | I2C 0x68 | Essential+ |
| 6 | HMI UART 5" (Nextion/Stone/DWIN) | UART TX/RX | Todos |
| 7 | Celdas de carga + HX711 | Digital D2/D3 | Insight+ |
| 8 | Transductor presión CO₂ | Analógico A4 | Insight+ |
| 9 | Sensor oxígeno disuelto (DO) | Analógico A5 | Insight+ |
| 10 | Driver recirculación (half-bridge) | PWM/DIR D5/D6 | Insight+ |
| 11 | Solenoide gas CO₂/H₂ | GPIO D7 | Insight+ |
| 12 | Chiller (relé opto-aislado) | GPIO D8 | Insight+ |
| 13 | Sensores Hamilton TCD + ACD | RS485/Modbus | Signature |

---

## Diseño 100% Foolproof — 7 Capas de Protección

```
┌─────────────────────────────────────────────────────────┐
│  7. Firmware failsafe (watchdog, store-forward)         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  6. Aislamiento galvánico (ISO7721, PC817)      │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │  5. Protección térmica (shutdown auto)  │   │   │
│  │  │  ┌─────────────────────────────────┐   │   │   │
│  │  │  │  4. Limitación corriente (PTC)  │   │   │   │
│  │  │  │  ┌─────────────────────────┐   │   │   │   │
│  │  │  │  │  3. ESD/TVS (±8kV)      │   │   │   │   │
│  │  │  │  │  ┌─────────────────┐   │   │   │   │   │
│  │  │  │  │  │  2. Polaridad   │   │   │   │   │   │
│  │  │  │  │  │  ┌─────────┐   │   │   │   │   │   │
│  │  │  │  │  │  │1. Mecán.│   │   │   │   │   │   │
│  │  │  │  │  │  └─────────┘   │   │   │   │   │   │
│  │  │  │  │  └─────────────────┘   │   │   │   │   │
│  │  │  │  └─────────────────────────┘   │   │   │   │
│  │  │  └─────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

- **Conectores keyed** — Físicamente imposible conectar al revés
- **Schottky SS34** — Protección polaridad inversa sin daño
- **TVS ESD IEC 61000-4-2 Level 4** — ±8 kV contacto, ±15 kV aire
- **PTC recuperable** — Auto-reset después de cortocircuito
- **Thermal shutdown** — Reguladores se apagan a 85°C y se recuperan
- **Opto-aislamiento** — MCU aislado de actuadores de potencia
- **Watchdog dual** — TPS3823 externo (1.6s) + IWDG interno (8s), poblado en TODOS los tiers
- **Aislamiento galvánico on-board** — SN6501 + AMC1301/ISO1541 por canal húmedo (pH, ORP, DO)

---

## Cumplimiento Normativo Europeo

| Directiva | Norma | Estado |
|-----------|-------|--------|
| **EMC** (2014/30/EU) | EN 55032 Clase B, EN 61000-4-2/3/4/5/6 | Diseñado |
| **RoHS 3** (2011/65/EU + 2015/863) | Soldadura SAC305, ENIG, sin Pb/Hg/Cd | Especificado |
| **WEEE** (2012/19/EU) | Categoría 6, registro por país | Pendiente registro |
| **RED** (2014/53/EU) | WiFi/BT via Arduino UNO Q cert. | Verificar con Arduino |
| **REACH** ((EC) 1907/2006) | Verificación SVHC proveedores | Pendiente |
| **Marcado CE** | Declaración de Conformidad | Post-ensayos |

---

## Estructura del Repositorio

```
nebula_qshield_pcb/
├── README.md                          # Este documento
├── .gitignore                         # Exclusiones KiCad/OS
│
├── docs/                              # Documentación de ingeniería
│   ├── 01_PCB_ARCHITECTURE.md         # Arquitectura completa del PCB
│   ├── 02_FOOLPROOF_DESIGN.md         # Diseño 100% Foolproof (7 capas)
│   ├── 03_EU_COMPLIANCE.md            # Cumplimiento normativo europeo
│   ├── 04_BOM_PRODUCTION.md           # BOM con part numbers Digi-Key/Mouser
│   ├── 05_POWER_BUDGET.md             # Análisis de presupuesto de potencia
│   ├── 06_PCB_LAYOUT_STACKUP.md       # Guías de layout y stackup 4 capas
│   ├── 07_KICAD_NETLIST.md            # Netlist KiCad y definiciones
│   ├── 08_MECHANICAL_ANALYSIS.md      # Análisis mecánico y compactación
│   ├── INSIGHT_FABRICATION_ROADMAP.md # Hoja de ruta JLCPCB para Insight
│   ├── UNO_Q_FORM_FACTOR.md           # Referencia inmutable del factor de forma UNO Q
│   ├── KICAD10_SSH_SETUP.md           # Guía SSH para clonar desde KiCad 10
│   └── DOCUMENTATION_UPDATE_AUDIT.md  # Auditoría de docs por actualizar
│
├── kicad/                             # Proyecto KiCad 10.0.5
│   ├── nebula_qshield.kicad_pro       # Proyecto principal
│   ├── nebula_qshield.kicad_sch       # Esquemático raíz (jerárquico)
│   ├── nebula_qshield.kicad_pcb       # Layout PCB (en progreso)
│   ├── power_management.kicad_sch     # Sub-hoja: reguladores y protección
│   ├── analog_acquisition.kicad_sch   # Sub-hoja: canales analógicos
│   ├── digital_i2c.kicad_sch          # Sub-hoja: bus I2C, HX711, RS485 bridge
│   ├── actuator_drivers.kicad_sch     # Sub-hoja: drivers de actuadores
│   ├── hmi_connectors.kicad_sch       # Sub-hoja: HMI UART y J21
│   ├── lib/                           # Librerías de símbolos y footprints
│   ├── production/                    # Salidas de fabricación
│   └── UNO_Q_rearchitecture_report.md # Reporte de re-arquitectura UNO Q
│
├── hardware/                          # Diseño mecánico
│   ├── enclosure/                     # Carcasa/enclosure IP54
│   └── cables/                        # Especificaciones de cables
│
├── test/                              # Testing y validación
│   ├── hil/                           # Hardware-in-the-Loop tests
│   └── validation/                    # Reportes de validación
│
└── tools/                             # Scripts Python de automatización
    ├── tier_counts.py                 # Conteos de componentes por tier
    ├── apply_tier_dnp4.py            # Aplicar propiedades DNP por tier
    ├── compare_pcb_to_netlist.py      # Verificar paridad PCB/netlist
    └── update_tier_comments.py       # Actualizar comentarios de tier
```

### Esquemáticos Jerárquicos

```
nebula_qshield.kicad_sch (raíz)
├── power_management.kicad_sch     → 12V protección, Buck 5V, LDO 3.3V, TPS3823 watchdog
├── analog_acquisition.kicad_sch   → pH/ORP/Temp/CO₂/DO + aislamiento galvánico
├── digital_i2c.kicad_sch          → I2C (D20/D21), HX711, RS485 Modbus bridge (Signature)
├── actuator_drivers.kicad_sch     → Recirculación, solenoide gas, chiller
└── hmi_connectors.kicad_sch       → HMI UART y shield header J21
```

---

## Especificaciones Técnicas

| Parámetro | Valor |
|-----------|-------|
| **Dimensiones** | 100 mm × 120 mm (factor de forma Arduino UNO Q inmutable; el tamaño exterior puede variar) |
| **Capas** | 4 (Signal–GND–Power–Signal) |
| **Material** | FR-4 Tg 170°C |
| **Acabado** | ENIG (RoHS) |
| **Cobre** | 1 oz (35 μm) todas las capas |
| **Temperatura operativa** | -10°C a +55°C |
| **Alimentación** | 12V DC (Essential: 2A, Insight: 3A, Signature: 8A) |
| **Placements totales** | 163 (88 Essential / 137 Insight / 146 Signature) |
| **KiCad** | 10.0.5 |
| **IPC Class** | Clase 2 |

---

## Presupuesto de Potencia

| Tier | Potencia continua | Fuente recomendada |
|------|-------------------|-------------------|
| Essential® | 11 W | 12V 2A (24W) |
| Insight® | 23 W | 12V 3A (36W) |
| Signature® | 65 W | 12V 8A (96W) |

---

## Getting Started

### Requisitos

- [KiCad 10.0.5](https://www.kicad.org/download/)
- [Python 3.11+](https://www.python.org/) (para scripts de BOM/CPL)
- Cuenta GitHub con acceso al repositorio

### Clonar el proyecto

Opción A — terminal:

```bash
git clone git@github.com:Nhilson73/nebula_qshield_pcb.git
cd nebula_qshield_pcb/kicad
# Abrir nebula_qshield.kicad_pro con KiCad 10
```

Opción B — desde KiCad 10:

Ver `docs/KICAD10_SSH_SETUP.md` para configurar SSH y clonar directamente desde `File → Clone Project from Git Repository`.

### Validación del diseño

```bash
# ERC
docker run --rm -v "$PWD:/workspace" kicad/kicad:10.0.5 \
  kicad-cli sch erc --severity-all \
  /workspace/kicad/nebula_qshield.kicad_sch

# DRC error-level
docker run --rm -v "$PWD:/workspace" kicad/kicad:10.0.5 \
  kicad-cli pcb drc --severity-error \
  /workspace/kicad/nebula_qshield.kicad_pcb

# Paridad PCB/netlist (exportar primero el netlist XML)
docker run --rm -v "$PWD:/workspace" kicad/kicad:10.0.5 \
  kicad-cli sch export netlist --format kicadxml \
  -o /workspace/kicad/uno_q.xml /workspace/kicad/nebula_qshield.kicad_sch

docker run --rm -v "$PWD:/workspace" kicad/kicad:10.0.5 \
  python3 /workspace/tools/compare_pcb_to_netlist.py
```

### Generar archivos de fabricación

Desde KiCad 10:

```
File → Plot → Gerber
File → Fabrication Outputs → Drill Files
File → Fabrication Outputs → BOM
File → Fabrication Outputs → Footprint Position File
```

Los parámetros de fabricación JLCPCB están en `docs/INSIGHT_FABRICATION_ROADMAP.md` y `docs/04_BOM_PRODUCTION.md`.

---

## Pinout J21 de referencia (Insight)

| Pin | Función | Net |
|-----|---------|-----|
| 1 | BOOT | NC |
| 2 | IOREF | NC |
| 3 | ~RESET | `/MCU_NRST` |
| 4 | +3V3 | `/3V3_RAIL` |
| 5 | +5V | `/5V_RAIL` |
| 6 | GND | `GND` |
| 7 | GND2 | `GND` |
| 8 | VIN | `/12V_RAIL` |
| 9 | A0/D14 | `/PH_ADC` |
| 10 | A1/D15 | `/ORP_ADC` |
| 11 | A2/D16 | `/TEMP_ADC` |
| 12 | A3/D17 | `/HUM_ADC` — DNP all tiers |
| 13 | A4/D18 | `/CO2_ADC` |
| 14 | A5/D19 | `/DO_ADC` |
| 15 | D0 | `/HMI_RX` |
| 16 | D1 | `/HMI_TX` |
| 17 | D2 | `/HX711_DOUT` |
| 18 | D3 | `/HX711_SCK` |
| 19 | D4 | `/MCU_WDI` |
| 20 | D5 | `/PUMP_PWM` |
| 21 | D6 | `/PUMP_DIR` |
| 22 | D7 | `/CO2_SOL_CTL` |
| 23 | D8 | `/CHILLER_CTL` |
| 24 | D9 | `/CO2_PWM` — DNP all tiers |
| 25 | D10 | `/RS485_IRQ` |
| 26 | D11 | NC |
| 27 | D12 | NC |
| 28 | D13 | `/LED_STATUS` |
| 29 | GND | `GND` |
| 30 | AREF | NC |
| 31 | D20/SDA | `/I2C_SDA` |
| 32 | D21/SCL | `/I2C_SCL` |

El pinout completo, mapa de tiers y hoja de ruta de fabricación están en `docs/INSIGHT_FABRICATION_ROADMAP.md`.

---

## Repositorios Relacionados

| Repositorio | Descripción |
|------------|-------------|
| [Nebula_ArduinoAPPLab_UNOQ](https://github.com/Nhilson73/Nebula_ArduinoAPPLab_UNOQ) | Firmware MCU + Software MPU + Servicios Docker + Contratos L2. **Source of truth** para el pinout y lógica del Q-Shield. |
| **nebula_qshield_pcb** (este repo) | PCB shield para Arduino UNO Q (esquemáticos KiCad, BOM, compliance) |

---

## Licencia

Proprietary — Cafelium SRL. All rights reserved.

---

## Team

- **Nhilson** — Lead Architect
- **Drancés** — Co-founder
- **Alfredo** — Co-founder

Powered by the **Nebula Ecosystem™**: Nebula Terra® · Nebula Fermentation® · Nebula Originblok® · Nebula Marketplace®
