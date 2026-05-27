# Nebula Q-Shield® — Netlist KiCad y Definiciones de Componentes

> **Documento:** NQS-NET-007 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Archivos de Diseño Electrónico
>
> **EDA Tool:** KiCad 8.x (recomendado) · Compatible Altium Designer / Eagle

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
| VIN_12V | J17:1 | D1:A, D2:A | Entrada 12V raw |
| 12V_FUSED | D2:K | F1:1 | Post-Schottky |
| 12V_RAIL | F1:2 | U1:VIN, K1:coil+, K2:coil+, J18:1, J19:1, J20:1 | Rail 12V protegido |
| 5V_RAIL | U1:OUT | U2:VIN, J21:5V, U6:VCC, U8:VCC2, U9:VCC2 | Rail 5V regulado |
| 3V3_RAIL | U2:OUT | R10:1, R11:1, U3:VDD, U4:VCC1, C15:1 | Rail 3.3V |
| GND | J17:2 | Global ground | Tierra principal |
| PGND | K1:coil-, K2:coil-, Q1:S, Q2:S | Star GND point | Tierra de potencia |
| AGND | U3:VSS, R4:2, C11:2 | Star GND point | Tierra analógica |
| DGND | U6:GND, U4:GND1, R10:2(vía pull-down) | Star GND point | Tierra digital |

### 2.2 Analog Acquisition Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| PH_RAW | J1:center | D3:A | Señal pH cruda del BNC |
| PH_FILT | D3:K, R3:1 | R3:2, C11:1 | Post-ESD, pre-filtro |
| PH_BUFF | C11:1, U3A:IN+ | U3A:OUT | Salida buffer pH |
| PH_ADC | U3A:OUT | J21:A0 | Al pin A0 del Arduino |
| ORP_RAW | J2:center | D4:A | Señal ORP cruda |
| ORP_FILT | D4:K | R_ORP:1, C_ORP:1 | Filtrado |
| ORP_BUFF | U3A_2:OUT | J21:A1 | Al pin A1 |
| CO2_RAW | J3:OUT | D6_CO2:A | Señal presión CO₂ |
| CO2_ADC | U3B:OUT | J21:A2 | Al pin A2 |
| DO_RAW | J4:center | D_DO:A | Señal DO cruda |
| DO_ADC | U3B_2:OUT | J21:A3 | Al pin A3 |
| TEMP_DIV | R8:2, NTC:1 | J21:A4 | Divisor NTC a A4 |
| HUM_ADC | J6:OUT | J21:A5 | Señal humedad a A5 |

### 2.3 I2C Bus Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| I2C_SDA | J21:SDA | R10:2, D7:1, J7:SDA, J8:SDA, J9:SDA, J10:SDA | Bus I2C data |
| I2C_SCL | J21:SCL | R11:2, D8:1, J7:SCL, J8:SCL, J9:SCL, J10:SCL | Bus I2C clock |
| SDA_ISO | U4:SDA_OUT | J11:SDA, J12:SDA, J13:SDA | I2C aislado (Atlas) |
| SCL_ISO | U4:SCL_OUT | J11:SCL, J12:SCL, J13:SCL | I2C aislado (Atlas) |

### 2.4 Digital & HX711 Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| HX711_DOUT | U6:DOUT | R12:1, J21:D2 | Load cell data |
| HX711_SCK | J21:D3 | U6:PD_SCK | Load cell clock |
| HX711_E+ | J14:1 | U6:INA+ | Excitación + |
| HX711_E- | J14:2 | U6:INA- | Excitación - |
| HX711_S+ | J14:3 | U6:INB+ | Señal + |
| HX711_S- | J14:4 | U6:INB- | Señal - |

### 2.5 Actuator Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| PUMP_DIR | J21:D4 | R13:1 | Dirección bomba |
| PUMP_DIR_ISO | U8:OUT_A | U7:IN_A | Post-optoacoplador |
| PUMP_PWM | J21:D5 | R14:1 | PWM bomba |
| PUMP_PWM_ISO | U8:OUT_B | U7:IN_B | Post-optoacoplador |
| MOTOR+ | U7:OUT_A | J18:1 | Motor terminal + |
| MOTOR- | U7:OUT_B | J18:2 | Motor terminal - |
| CHILLER_CTL | J21:D6 | R15:1 | Control chiller |
| CHILLER_ISO | U10:OUT | Q3:G | Post-optoacoplador |
| CHILLER_RELAY | Q3:D | K1:coil- | Activa relay chiller |
| CO2_SOL_CTL | J21:D7 | R16:1 | Control solenoide |
| CO2_SOL_ISO | U11:OUT | Q4:G | Post-optoacoplador |
| CO2_SOL_RELAY | Q4:D | K2:coil- | Activa relay solenoide |
| CO2_PWM | J21:D9 | R21:1 | PWM regulador CO₂ |
| CO2_PWM_FILT | R21:2, C22:1 | U3C:IN+ | Filtrado RC |
| CO2_PWM_AMP | U3C:OUT | Q5:G | Amplificado |
| CO2_VALVE | Q5:D | J_CO2_VALVE:1 | Válvula proporcional |

### 2.6 Display & Indicator Nets

| Net Name | From (Ref:Pin) | To (Ref:Pin) | Notes |
|----------|---------------|-------------|-------|
| HMI_TX | J21:D1 (TX) | J_HMI:TX | UART TX al HMI (Nextion/Stone) |
| HMI_RX | J21:D0 (RX) | J_HMI:RX | UART RX del HMI (touch events) |
| HMI_5V | 5V_RAIL | J_HMI:VCC | Alimentación 5V al HMI |
| LED_STATUS | J21:D13 | R_LED:1 | LED de estado |

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

### 4.2 BNC Panel Mount (J1, J2, J4)

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
    │   ├── Buck converter 12V→5V (U1, L1, C3-C7)
    │   ├── LDO 5V→3.3V (U2, C8-C10)
    │   └── Power LEDs (LED1-3, R_LED1-3)
    │
    ├── Sheet 2: analog_acquisition
    │   ├── pH channel (J1, D3, R3, C11, U3A, R4)
    │   ├── ORP channel (J2, D4, R_ORP, C_ORP, U3A_2)
    │   ├── CO₂ pressure channel (J3, D6_CO2, R5, C12, U3B)
    │   ├── DO channel (J4, D_DO, R_DO, C_DO, U3B_2)
    │   ├── Temperature channel (J5, R8, C13, D5)
    │   ├── Humidity channel (J6, D6, R9, C14)
    │   └── Galvanic isolation (U4, U5, C15-C18)
    │
    ├── Sheet 3: digital_i2c
    │   ├── I2C bus (R10, R11, D7, D8)
    │   ├── I2C connectors (J7-J13)
    │   ├── HX711 load cell ADC (U6, J14, C19, C20, R12)
    │   └── Status LED (R_LED, LED_STATUS)
    │
    ├── Sheet 4: actuator_drivers
    │   ├── Motor driver (U7, Q1, Q2, U8, U9, D9, D10)
    │   ├── Chiller relay (K1, U10, Q3, D11)
    │   ├── CO₂ solenoid relay (K2, U11, Q4, D12)
    │   ├── CO₂ PWM regulator (R21, C22, U3C, Q5, D13)
    │   └── PTC fuses (F2-F4)
    │
    └── Sheet 5: hmi_connectors
        ├── HMI UART connector (J_HMI, D_HMI)
        ├── Arduino shield header (J21)
        └── Sensor clamp diodes (D_CL1–D_CL3 BAT54S)
```

---

## 7. Exportación para Fabricación

### 7.1 Generación de Gerber (KiCad 8)

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

*Documento NQS-NET-007 Rev 1.0 — Nebula Ecosystem® — Netlist KiCad*
