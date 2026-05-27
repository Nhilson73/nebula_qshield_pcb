# Nebula Q-Shield® PCB

**Precision Fermentation Monitor** — PCB shield industrial para el Arduino UNO Q, con 12 componentes de adquisición de datos, control de actuadores, HMI UART 5" (Nextion/Stone), y cumplimiento normativo europeo completo.

Built by [Cafelium SRL](https://github.com/Nhilson73) · 🇩🇴 Dominican Republic

> **Parte del ecosistema [Nebula Agtech® Core](https://github.com/Nhilson73/Nebula_Agtech_Core)**
>
> **Awards:** I+D Lab INDOTEL 2025 · CREE Banreservas 2026 · Pitch4FUN 2026

---

## ¿Qué es el Q-Shield®?

El Q-Shield® es un **PCB shield de 4 capas** que se monta sobre el Arduino UNO Q (STM32U585 MCU + Qualcomm QRB2210 MPU), convirtiendo la placa en un sistema completo de monitoreo y control de fermentación para café y cacao de especialidad.

```
┌──────────────────────────────────────────────────────────────────┐
│                    NEBULA Q-SHIELD® PCB v1.0                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ POTENCIA     │  │  ANALÓGICO   │  │     DIGITAL          │   │
│  │              │  │              │  │                      │   │
│  │ Buck 12→5V   │  │ 6× ADC      │  │ I2C bus (7 devices)  │   │
│  │ LDO 5→3.3V   │  │ Op-amp buf. │  │ HX711 24-bit ADC     │   │
│  │ TVS + PTC    │  │ RC filters  │  │ HMI UART (Nextion)   │   │
│  │ Schottky     │  │ ESD protect │  │ ESD protection       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ACTUADORES (opto-aislados)                              │   │
│  │  Motor driver (half-bridge) · Relay ×2 · PWM regulator   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CONECTOR ARDUINO UNO Q (2×20 shield header)             │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Los 12 Componentes

| # | Componente | Interfaz | Tier |
|---|-----------|----------|------|
| 1 | Sensor pH (Nernst + comp. térmica) | Analógico A0 / I2C EZO | Essential+ |
| 2 | Sensor ORP (potencial redox) | Analógico A1 / I2C EZO | Essential+ |
| 3 | Sensor temperatura (NTC/PT-1000) | Analógico A4 / I2C EZO-RTD | Essential+ |
| 4 | Celda de carga + HX711 (peso) | Digital D2/D3 | Essential+ |
| 5 | Transductor presión CO₂ (30 PSI) | Analógico A2 | Insight+ |
| 6 | Sensor oxígeno disuelto (DO) | Analógico A3 / I2C EZO | Insight+ |
| 7 | Sensor humedad (SHT30) | Analógico A5 | Signature |
| 8 | GPS u-blox SAM-M8Q | I2C 0x42 | Essential+ |
| 9 | Sensor densidad celular (turbidez) | I2C 0x30 | Signature |
| 10 | RTC DS3231 (reloj tiempo real) | I2C 0x68 | Todos |
| 11 | Módulo relay 4 canales (actuadores) | GPIO D4–D7, D9 | Insight+ |
| 12 | HMI UART 5" (Nextion/Stone) | UART TX/RX (JST-XH 4P) | Todos |

---

## Hardware Tier Model

Una sola PCB para los 3 tiers — los componentes no poblados (DNP) se seleccionan en fabricación:

| Tier | Sensores | Actuadores | Costo PCB | Costo total estimado |
|------|----------|-----------|-----------|---------------------|
| **Essential®** | pH, ORP, Temp, Peso, GPS, RTC | — | ~$23 | ~$350–$440 |
| **Insight®** | Essential + CO₂, DO | Bomba, CO₂ inyección | ~$27 | ~$750–$950 |
| **Signature®** | Insight + Humedad, Cell density | + Chiller | ~$31 | ~$810–$1,010 |

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
- **Aislamiento galvánico on-board** — SN6501 + ADuM1250 por sensor húmedo (pH, ORP, DO)

---

## Cumplimiento Normativo Europeo

| Directiva | Norma | Estado |
|-----------|-------|--------|
| **EMC** (2014/30/EU) | EN 55032 Clase B, EN 61000-4-2/3/4/5/6 | ✓ Diseñado |
| **RoHS 3** (2011/65/EU + 2015/863) | Soldadura SAC305, ENIG, sin Pb/Hg/Cd | ✓ Especificado |
| **WEEE** (2012/19/EU) | Categoría 6, registro por país | ☐ Pendiente registro |
| **RED** (2014/53/EU) | WiFi/BT via Arduino UNO Q cert. | ☐ Verificar con Arduino |
| **REACH** ((EC) 1907/2006) | Verificación SVHC proveedores | ☐ Pendiente |
| **Marcado CE** | Declaración de Conformidad | ☐ Post-ensayos |

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
│   └── 07_KICAD_NETLIST.md            # Netlist KiCad y definiciones
│
├── kicad/                             # Proyecto KiCad 8.x
│   ├── nebula_qshield.kicad_pro       # Proyecto principal
│   ├── nebula_qshield.kicad_sch       # Esquemático raíz (jerárquico)
│   ├── power_management.kicad_sch     # Sub-hoja: reguladores y protección
│   ├── analog_acquisition.kicad_sch   # Sub-hoja: 6 canales analógicos
│   ├── digital_i2c.kicad_sch         # Sub-hoja: bus I2C y HX711
│   ├── actuator_drivers.kicad_sch    # Sub-hoja: drivers de actuadores
│   ├── hmi_connectors.kicad_sch      # Sub-hoja: HMI UART y conectores
│   ├── nebula_qshield.kicad_dru       # Reglas de diseño (IPC-2221B)
│   ├── nebula_qshield.kicad_pcb       # Layout PCB (pendiente)
│   ├── lib/
│   │   ├── nebula_symbols.kicad_sym   # 8 símbolos custom
│   │   └── nebula_footprints.pretty/  # Footprints custom (BNC, shield)
│   ├── 3d_models/                     # Modelos 3D (STEP/WRL)
│   ├── gerber/                        # Archivos de fabricación
│   └── production/
│       └── bom/                       # BOM exportado (CSV con Digi-Key PNs)
│
├── hardware/                          # Diseño mecánico
│   ├── enclosure/                     # Carcasa/enclosure IP54
│   └── cables/                        # Especificaciones de cables
│
├── test/                              # Testing y validación
│   ├── hil/                           # Hardware-in-the-Loop tests
│   └── validation/                    # Reportes de validación
│
└── tools/                             # Scripts y utilidades
```

### Esquemáticos Jerárquicos Completados

```
nebula_qshield.kicad_sch (raíz)
├── power_management.kicad_sch     → 12V protección, Buck 5V, LDO 3.3V, TPS3823 watchdog
├── analog_acquisition.kicad_sch   → 6 canales: pH/ORP/CO₂/DO/Temp/Hum + aislamiento galvánico
├── digital_i2c.kicad_sch          → I2C bus, 7× Qwiic, HX711, RS485 (DNP), LED estado
├── actuator_drivers.kicad_sch     → Motor IR2104, 2× relays opto-aislados, PWM CO₂
└── hmi_connectors.kicad_sch       → HMI UART (JST-XH 4P), shield header J21, sensor clamps
```

---

## Especificaciones Técnicas

| Parámetro | Valor |
|-----------|-------|
| **Dimensiones** | 68.6 × 53.3 mm (factor forma Arduino UNO) |
| **Capas** | 4 (Signal–GND–Power–Signal) |
| **Material** | FR-4 Tg 170°C |
| **Acabado** | ENIG (RoHS) |
| **Cobre** | 1 oz (35 μm) todas las capas |
| **Temperatura operativa** | -10°C a +55°C |
| **Alimentación** | 12V DC (Essential: 2A, Insight: 3A, Signature: 8A) |
| **Componentes totales** | 147 (Signature, fully populated) |
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

- [KiCad 8.x](https://www.kicad.org/download/) (EDA tool open source)
- [Python 3.11+](https://www.python.org/) (para scripts de BOM/CPL)

### Abrir el Proyecto

```bash
git clone https://github.com/Nhilson73/nebula_qshield_pcb.git
cd nebula_qshield_pcb/kicad
# Abrir nebula_qshield.kicad_pro con KiCad 8.x
```

### Generar Archivos de Fabricación

```bash
# Desde KiCad:
# File → Plot → Gerber (configuración en docs/07_KICAD_NETLIST.md)
# File → Fabrication Outputs → Drill Files
# File → Fabrication Outputs → BOM
# File → Fabrication Outputs → Footprint Position File
```

---

## Repositorios Relacionados

| Repositorio | Descripción |
|------------|-------------|
| [Nebula_Agtech_Core](https://github.com/Nhilson73/Nebula_Agtech_Core) | Firmware MCU (C++17) + Software MPU (Python) + Contratos L2 |
| [gateway_nebula_fermentation](https://github.com/Nhilson73/gateway_nebula_fermentation) | Gateway ESP32-P4 WiFi + Touch 7" + Sensores |
| **nebula_qshield_pcb** (este repo) | PCB shield para Arduino UNO Q |

---

## Licencia

Proprietary — Cafelium SRL. All rights reserved.

---

## Team

- **Nhilson** — Lead Architect
- **Drancés** — Co-founder
- **Alfredo** — Co-founder

Powered by the **Nebula Ecosystem™**: Nebula Terra® · Nebula Fermentation® · Nebula Originblok® · Nebula Marketplace®
