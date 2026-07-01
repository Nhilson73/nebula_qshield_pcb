# Nebula Q-Shield® — Netlist KiCad y Definiciones de Componentes

> **Documento:** NQS-NET-007 · **Rev:** 2.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Archivos de Diseño Electrónico
>
> **EDA Tool:** KiCad 9.x · Compatible Altium Designer / Eagle

---

## 1. Información del Proyecto KiCad

### 1.1 Estructura de Archivos

```
kicad/
├── nebula_qshield.kicad_pro          # Proyecto KiCad
├── nebula_qshield.kicad_sch          # Esquemático raíz (jerárquico)
│   ├── power_management.kicad_sch    # Sub-hoja: reguladores y protección
│   ├── analog_acquisition.kicad_sch  # Sub-hoja: 6 canales analógicos + aislamiento
│   ├── digital_i2c.kicad_sch        # Sub-hoja: bus I2C, HX711, RS485
│   ├── actuator_drivers.kicad_sch   # Sub-hoja: drivers de actuadores
│   └── hmi_connectors.kicad_sch     # Sub-hoja: HMI UART, shield header, conectores
├── nebula_qshield.kicad_pcb          # Layout PCB (pendiente)
├── nebula_qshield.kicad_dru          # Design rules (IPC-2221B Clase 2)
├── lib/
│   ├── nebula_symbols.kicad_sym      # 8 símbolos custom
│   └── nebula_footprints.pretty/     # Footprints custom
│       ├── BNC_Panel_Mount_Isolated.kicad_mod
│       └── Arduino_UNO_Shield_2x20.kicad_mod
├── gerber/                           # Archivos de fabricación
└── production/
    └── bom/
        └── nebula_qshield_bom.csv    # BOM completo con Digi-Key PNs
```

---

## 2. Netlist Completo — Tabla de Conexiones

### 2.1 Power Management Net

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| VIN_12V | J1:1 | D1:A, D2:A | Entrada 12V raw (barrel jack) |
| 12V_FUSED | D2:K | F1:1 | Post-Schottky |
| 12V_RAIL | F1:2 | U1:VIN, K1:coil+, K2:coil+, J17:1, J18:1, J19:1 | Rail 12V protegido |
| 5V_RAIL | U1:OUT | U2:VIN, J21:5V, U5:VCC, U8:VCC, U12:VCC | Rail 5V regulado |
| 3V3_RAIL | U2:OUT | R19:1, R20:1, U4:VDD, U14:VCC, C24:1 | Rail 3.3V |
| GND | J1:2 | Global ground | Tierra principal |
| PGND | K1:coil-, K2:coil-, Q1:S, Q2:S | Star GND point | Tierra de potencia |
| AGND | U4:VSS, R8:2, C12:2 | Star GND point | Tierra analógica |
| DGND | U14:GND, U21:GND1, R19:2(vía pull-down) | Star GND point | Tierra digital |

### 2.2 Analog Acquisition Nets

**Arquitectura B2: AMC1301 (aislamiento analógico) + SN6501 (supply aislado real con transformador)**

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| PH_RAW | J2:center | D3:A | Señal pH cruda del BNC |
| PH_FILT | D3:K, R7:1 | R7:2, C12:1 | Post-ESD, pre-filtro RC |
| PH_BUF | C12:1, R8:1, U4.1:IN+ | U4.1:OUT | Salida buffer pH (hot side) |
| PH_ADC | U6:VOUTP | J21:A0 | Post-AMC1301, al ADC del MCU |
| VDD_ISO_PH | T1:sec → D19,D20 rect → C28 | U4:VDD, U6:VDD1 | Supply aislado pH |
| GND_ISO_PH | T1:sec center-tap | U4:VSS, U6:GND1 | Tierra aislada pH |
| ORP_RAW | J3:center | D4:A | Señal ORP cruda del BNC |
| ORP_FILT | D4:K, R9:1 | R9:2, C15:1 | Post-ESD, pre-filtro RC |
| ORP_BUF | C15:1, R10:1, U7.1:IN+ | U7.1:OUT | Salida buffer ORP (hot side) |
| ORP_ADC | U9:VOUTP | J21:A1 | Post-AMC1301, al ADC del MCU |
| VDD_ISO_ORP | T2:sec → D21,D22 rect → C29 | U7:VDD, U9:VDD1 | Supply aislado ORP |
| GND_ISO_ORP | T2:sec center-tap | U7:VSS, U9:GND1 | Tierra aislada ORP |
| CO2_RAW | J4:OUT | D5:A | Señal presión CO₂ |
| CO2_ADC | U10.1:OUT | J21:A4 | Buffer → ADC (no aislado) |
| DO_RAW | J5:center | D6:A | Señal DO cruda del BNC |
| DO_BUF | C19:1, R14:1, U11.1:IN+ | U11.1:OUT | Salida buffer DO (hot side) |
| DO_ADC | U13:VOUTP | J21:A5 | Post-AMC1301, al ADC del MCU |
| VDD_ISO_DO | T3:sec → D23,D24 rect → C30 | U11:VDD, U13:VDD1 | Supply aislado DO |
| GND_ISO_DO | T3:sec center-tap | U11:VSS, U13:GND1 | Tierra aislada DO |
| TEMP_ADC | R15:2, C22:1, U10.2:OUT | J21:A2 | Divisor NTC → buffer → A2 |
| HUM_ADC | R17:2, C23:1 | J21:A3 | Señal humedad a A3 |

> **Nota ADC mapping (fuente de verdad = firmware):**
> A0=PH_ADC, A1=ORP_ADC, A2=TEMP_ADC, A3=HUM_ADC, A4=CO2_ADC, A5=DO_ADC

### 2.3 I2C Bus Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| I2C_SDA | J21:SDA | R19:2, D9:1, J8:SDA, J9:SDA, J10:SDA | Bus I2C data |
| I2C_SCL | J21:SCL | R20:2, D9:2, J8:SCL, J9:SCL, J10:SCL | Bus I2C clock |
| SDA_ISO | U21:SDA2 | J11:SDA, J12:SDA, J13:SDA, J14:SDA | I2C aislado (Atlas EZO) |
| SCL_ISO | U21:SCL2 | J11:SCL, J12:SCL, J13:SCL, J14:SCL | I2C aislado (Atlas EZO) |

### 2.4 Digital & HX711 Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| HX711_DOUT | U14:DOUT | R21:1, J21:D2 | Load cell data (3.3V logic) |
| HX711_SCK | J21:D3 | U14:PD_SCK | Load cell clock |
| HX711_E+ | J15:1 | U14:INA+ | Excitación + |
| HX711_E- | J15:2 | U14:INA- | Excitación - |
| HX711_S+ | J15:3 | U14:INB+ | Señal + |
| HX711_S- | J15:4 | U14:INB- | Señal - |
| HX711_VCC | 3V3_RAIL | U14:VCC, U14:VSUP | Alimentación 3.3V (sin level-shift) |

### 2.5 Actuator Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| PUMP_DIR | J21:D4 | R24:1 | Dirección bomba |
| PUMP_DIR_ISO | U16:OUT_A | U17:IN_A | Post-optoacoplador (PC817X2) |
| PUMP_PWM | J21:D5 | R25:1 | PWM bomba |
| PUMP_PWM_ISO | U16:OUT_B | U17:IN_B | Post-optoacoplador (PC817X2) |
| MOTOR+ | U17:OUT_A | J17:1 | Motor terminal + |
| MOTOR- | U17:OUT_B | J17:2 | Motor terminal - |
| CHILLER_CTL | J21:D6 | R26:1 | Control chiller |
| CHILLER_ISO | U18:OUT | Q3:G | Post-optoacoplador (PC817X1) |
| CHILLER_RELAY | Q3:D | K1:coil- | Activa relay chiller |
| CO2_SOL_CTL | J21:D7 | R27:1 | Control solenoide CO₂ |
| CO2_SOL_ISO | U19:OUT | Q4:G | Post-optoacoplador (PC817X1) |
| CO2_SOL_RELAY | Q4:D | K2:coil- | Activa relay solenoide |
| CO2_PWM | J21:D9 | R28:1 | PWM regulador CO₂ |
| CO2_PWM_FILT | R28:2, C27:1 | U20.2:IN+ | Filtrado RC |
| CO2_PWM_AMP | U20.2:OUT | Q5:G | Amplificado |
| CO2_VALVE | Q5:D | J22:1 | Válvula proporcional CO₂ |

### 2.6 Display & Indicator Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| HMI_TX | J21:D1 (TX) | J20:TX | UART TX al HMI (Nextion/Stone) |
| HMI_RX | J21:D0 (RX) | J20:RX | UART RX del HMI (touch events) |
| HMI_5V | 5V_RAIL | J20:VCC | Alimentación 5V al HMI |
| LED_STATUS | J21:D13 | R23:1 | LED de estado bicolor |

---

## 3. Símbolos Esquemáticos Custom

### 3.1 Nebula Q-Shield Shield Header (J21)

```
    KiCad Symbol: Nebula_QShield_Header
    
    ┌───────────────────────────────────────────┐
    │              J21                           │
    │  ARDUINO UNO SHIELD HEADER                │
    │                                            │
    │  Left side:          Right side:           │
    │  ┌────────┐          ┌────────┐           │
    │  │ A0  ├──1          25──┤ D0   │           │
    │  │ A1  ├──2          26──┤ D1   │           │
    │  │ A2  ├──3          27──┤ D2   │           │
    │  │ A3  ├──4          28──┤ D3   │           │
    │  │ A4  ├──5          29──┤ D4   │           │
    │  │ A5  ├──6          30──┤ D5   │           │
    │  │     │             31──┤ D6   │           │
    │  │ VIN ├──7          32──┤ D7   │           │
    │  │ GND ├──8          33──┤ D8   │           │
    │  │ GND ├──9          34──┤ D9   │           │
    │  │ 5V  ├──10         35──┤ D10  │           │
    │  │ 3V3 ├──11         36──┤ D11  │           │
    │  │ RST ├──12         37──┤ D12  │           │
    │  │ IOREF├──13        38──┤ D13  │           │
    │  │ SDA ├──14         39──┤ GND  │           │
    │  │ SCL ├──15         40──┤ AREF │           │
    │  └────────┘          └────────┘           │
    └───────────────────────────────────────────┘
```

---

## 4. Footprints Custom

### 4.1 Arduino UNO Shield Mounting (J21)

```
    Footprint: Arduino_UNO_Shield_Header
    
    Mounting holes: 4 × M3 (3.2 mm drill, no plate)
    
    Pin headers:
    - Left: 1×15 female header, 2.54 mm pitch
    - Right: 1×15 female header, 2.54 mm pitch
    
    Total: 40 pins (2 × 20, pero solo 30 señales usadas)
    
    Coordenadas de montaje (origen = esquina inferior izquierda):
    Hole 1: (14.0, 2.54) mm
    Hole 2: (66.04, 7.62) mm
    Hole 3: (66.04, 35.56) mm
    Hole 4: (15.24, 50.80) mm
```

### 4.2 BNC Panel Mount (J2, J3, J5)

```
    Footprint: BNC_Panel_Mount_Isolated
    
    Tipo: BNC hembra, montaje panel, aislado
    Pad center: 1 × 1.5 mm drill (señal)
    Pad shell: 4 × 1.0 mm drill (shield/GND)
    Shell-to-center isolation: 3.0 mm (para floating shield)
    
    Courtyard: 12.0 × 12.0 mm
```

---

## 5. Design Rules (KiCad DRC)

### 5.1 Archivo de Reglas (.kicad_dru)

```
    (version 1)
    (rule "Signal"
      (constraint track_width (min 0.2mm))
      (constraint clearance (min 0.2mm))
    )
    (rule "Power"
      (constraint track_width (min 0.5mm))
      (constraint clearance (min 0.3mm))
      (condition "A.NetClass == 'Power'")
    )
    (rule "High_Current"
      (constraint track_width (min 1.0mm))
      (constraint clearance (min 0.5mm))
      (condition "A.NetClass == 'HighCurrent'")
    )
    (rule "Analog"
      (constraint clearance (min 0.3mm))
      (condition "A.NetClass == 'Analog'")
    )
    (rule "Relay_HV"
      (constraint clearance (min 2.5mm))
      (condition "A.NetClass == 'RelayHV'")
    )
```

### 5.2 Net Classes

| Net Class | Track Width | Clearance | Via Drill | Via Pad | Nets |
|-----------|-------------|-----------|-----------|---------|------|
| Default | 0.25 mm | 0.20 mm | 0.30 mm | 0.60 mm | All signals |
| Power | 0.50 mm | 0.30 mm | 0.40 mm | 0.80 mm | 5V, 3.3V rails |
| HighCurrent | 1.50 mm | 0.50 mm | 0.50 mm | 1.00 mm | 12V, motor, chiller |
| Analog | 0.25 mm | 0.30 mm | 0.30 mm | 0.60 mm | PH_*, ORP_*, TEMP_* |
| I2C | 0.25 mm | 0.25 mm | 0.30 mm | 0.60 mm | I2C_SDA, I2C_SCL |
| RelayHV | 1.00 mm | 2.50 mm | 0.50 mm | 1.00 mm | Relay contact traces |

---

## 6. Esquemático Jerárquico — Estructura

```
    nebula_qshield.kicad_sch (ROOT)
    │
    ├── Sheet 1: power_management
    │   ├── 12V input protection (D1, D2, F1)
    │   ├── Buck converter 12V→5V (U1, L1, C3-C7, R1, R2)
    │   ├── LDO 5V→3.3V (U2, C8-C10)
    │   ├── Watchdog supervisor (U3, SW1, R3, C11)
    │   └── Power LEDs (LED1-3, R4-R6)
    │
    ├── Sheet 2: analog_acquisition
    │   ├── pH channel — isolated (J2, D3, R7, C12, R8, U4, U5, U6, T1, D19-D20, C28, C13-C14)
    │   ├── ORP channel — isolated (J3, D4, R9, C15, R10, U7, U8, U9, T2, D21-D22, C29, C16-C17)
    │   ├── CO₂ pressure channel (J4, D5, R11, C18, R12, U10.1)
    │   ├── DO channel — isolated (J5, D6, R13, C19, R14, U11, U12, U13, T3, D23-D24, C30, C20-C21)
    │   ├── Temperature channel (J6, D7, R15, C22, R16, U10.2)
    │   ├── Humidity channel (J7, D8, R17, C23, R18)
    │   └── Op-amp decoupling (C24)
    │
    ├── Sheet 3: digital_i2c
    │   ├── I2C bus (R19, R20, D9)
    │   ├── I2C connectors (J8-J14)
    │   ├── I2C isolation — Atlas EZO (U21 ISO1541)
    │   ├── HX711 load cell ADC (U14, J15, R21, C25, C26)
    │   ├── RS485 transceiver (U15, J16, R22)
    │   └── Status LED (LED4, R23)
    │
    ├── Sheet 4: actuator_drivers
    │   ├── Motor H-bridge driver (U16, U17, Q1, Q2, D10, D11, R24, R25, F2, J17)
    │   ├── CO₂ solenoid relay (U19, Q4, K2, D13, R27, F3, J18)
    │   ├── Chiller relay (U18, Q3, K1, D12, R26, F4, J19)
    │   ├── CO₂ PWM regulator (R28, C27, U20, Q5, D14, J22)
    │   └── PTC fuses (F2-F4)
    │
    └── Sheet 5: hmi_connectors
        ├── HMI UART connector (J20, D15)
        ├── Arduino shield header (J21)
        └── Sensor clamp diodes (D16, D17, D18 BAT54S)
```

---

## 7. Exportación para Fabricación

### 7.1 Generación de Gerber (KiCad 9)

```
    File → Plot → Gerber
    
    Configuración:
    ├── Format: Gerber X2 (preferred) o RS-274X
    ├── Coordinate format: 4.6 (metric)
    ├── Drill format: Excellon (2:4, metric)
    ├── Layers: F.Cu, In1.Cu, In2.Cu, B.Cu, F.Mask, B.Mask,
    │           F.SilkS, B.SilkS, Edge.Cuts, F.Paste, B.Paste
    ├── Use extended X2 attributes: Yes
    ├── Subtract soldermask from silk: Yes
    └── Generate drill file separately: Yes
```

### 7.2 Generación de BOM

```
    Tools → Edit Symbol Fields → Export CSV
    
    Campos requeridos:
    - Reference
    - Value
    - Footprint
    - MPN (Manufacturer Part Number)
    - Distributor PN (Digi-Key / Mouser)
    - Description
    - DNP (Do Not Populate flag for tier variants)
```

### 7.3 Generación de CPL (Component Placement List)

```
    File → Fabrication Outputs → Footprint Position File
    
    Format: CSV
    Columns: Ref, Val, Package, PosX, PosY, Rot, Side
    Units: Millimeters
    Coordinate origin: Auxiliary axis origin (PCB corner)
```

---

## 8. Validación Pre-Fabricación

### 8.1 DRC (Design Rule Check) — KiCad

| Check | Severity | Expected |
|-------|----------|----------|
| Clearance violations | Error | 0 |
| Unconnected nets | Error | 0 |
| Track width violations | Error | 0 |
| Via drill violations | Error | 0 |
| Courtyard overlap | Warning | Review needed |
| Silk over pad | Warning | 0 |
| Missing footprints | Error | 0 |
| Missing net connections | Error | 0 |

### 8.2 ERC (Electrical Rule Check) — KiCad

| Check | Severity | Expected |
|-------|----------|----------|
| Unconnected pins | Error | 0 (all pins must be connected or marked no-connect) |
| Power pin conflicts | Error | 0 |
| Driver conflicts | Warning | Review |
| Missing power flags | Error | 0 |

### 8.3 Manufacturing Review

| Check | Method |
|-------|--------|
| Gerber vs. schematic | Import Gerber in viewer, visual compare |
| BOM vs. schematic | Cross-reference all references |
| Drill file verification | Load in drill viewer, check all holes |
| Panelization | Verify V-score or tab placement |
| Stencil | Verify paste layer matches pads |

---

*Documento NQS-NET-007 Rev 2.0 — Nebula Ecosystem® — Netlist KiCad*
