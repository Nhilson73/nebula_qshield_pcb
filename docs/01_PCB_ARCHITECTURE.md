# Nebula Q-Shield® — Arquitectura PCB Completa

> **Documento:** NQS-ARCH-001 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Diseño de Hardware
>
> **Normativas aplicables:** IPC-2221B, IPC-7351C, IEC 61010-1, EN 61326-1

---

## 1. Especificaciones Generales del PCB

### 1.1 Parámetros Físicos

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| **Dimensiones** | 100 × 100 mm | Factor de forma para acople con Arduino UNO Q |
| **Capas** | 4 (Signal–GND–Power–Signal) | EMC Clase B, aislamiento analógico/digital |
| **Espesor total** | 1.6 mm ± 10% | Estándar IPC-2221B |
| **Material base** | FR-4 Tg 170°C (IT-180A o equivalente) | Operación hasta +55°C ambiente |
| **Acabado superficial** | ENIG (Electroless Nickel Immersion Gold) | RoHS, soldabilidad, longevidad |
| **Máscara de soldadura** | Verde LPI, ambos lados | Estándar industrial |
| **Serigrafía** | Blanca, ambos lados | Identificación de componentes |
| **Peso de cobre** | 1 oz (35 μm) capas externas, 1 oz internas | Capacidad de corriente actuadores |
| **Ancho mín. de pista** | 0.2 mm (señal), 0.5 mm (potencia) | IPC Clase 2 |
| **Espacio mín. entre pistas** | 0.2 mm (señal), 0.3 mm (potencia) | IPC-2221B clearance |
| **Taladro mínimo** | 0.3 mm (vías), 0.8 mm (THT) | Fabricación estándar |
| **Impedancia controlada** | No requerida (señales < 1 MHz) | Frecuencias bajas |

### 1.2 Stackup de 4 Capas

```
┌────────────────────────────────────────────────────────────┐
│  CAPA 1 (TOP)   — Señales + Componentes SMD               │  35 μm Cu
├────────────────────────────────────────────────────────────┤
│  Prepreg 7628   — 0.2 mm                                   │  Dieléctrico
├────────────────────────────────────────────────────────────┤
│  CAPA 2 (GND)   — Plano de tierra continuo                 │  35 μm Cu
├────────────────────────────────────────────────────────────┤
│  Core FR-4      — 0.8 mm                                   │  Dieléctrico
├────────────────────────────────────────────────────────────┤
│  CAPA 3 (PWR)   — Planos de potencia (12V, 5V, 3.3V)      │  35 μm Cu
├────────────────────────────────────────────────────────────┤
│  Prepreg 7628   — 0.2 mm                                   │  Dieléctrico
├────────────────────────────────────────────────────────────┤
│  CAPA 4 (BOT)   — Señales + Componentes SMD               │  35 μm Cu
└────────────────────────────────────────────────────────────┘
         Espesor total: ~1.6 mm
```

**Justificación del plano GND continuo (Capa 2):**
- Retorno de corriente de baja impedancia para todas las señales analógicas
- Blindaje electromagnético entre señales TOP y planos de potencia
- Reducción de EMI radiada para cumplimiento EN 55032 Clase B

---

## 2. Bloques Funcionales

### 2.1 Bloque de Potencia (Power Management)

#### 2.1.1 Entrada de Alimentación 12V DC

```
                            Foolproof Chain
    JACK DC 12V ──►[D_TVS SMAJ15A]──►[F1 PTC 3A]──►[D_SCHOTTKY SS34]──► 12V_RAIL
                    Protección        Fusible          Polaridad
                    transitorio       recuperable      inversa
                    ±15V clamp        I_hold=1.1A      V_f=0.5V
                                      I_trip=2.2A
```

| Componente | Referencia | Valor | Encapsulado | Función |
|------------|-----------|-------|-------------|---------|
| D1 | SMAJ15A | 15V TVS bidireccional | SMA | Protección transitorio/ESD entrada |
| F1 | MF-MSMF110 | PTC 1.1A hold / 2.2A trip | 1812 | Fusible recuperable sobrecorriente |
| D2 | SS34 | Schottky 3A 40V | SMA | Protección polaridad inversa |
| C1 | Cerámico MLCC | 100 μF / 25V | 1210 | Desacoplo entrada |
| C2 | Electrolítico | 470 μF / 25V | Ø10×12.5 | Reserva energética transitoria |

#### 2.1.2 Regulador 5V — Buck Converter

```
    12V_RAIL ──►[TPS54302 Buck]──► 5V_RAIL (3A max)
                  │
                  ├── L1: 4.7 μH / 4A (Würth 744043004700)
                  ├── C_in: 22 μF × 2 ceramics (X5R, 25V)
                  ├── C_out: 47 μF × 2 ceramics (X5R, 10V)
                  ├── R_top: 100 kΩ (feedback divider)
                  ├── R_bot: 24.9 kΩ (Vout = 0.596 × (1 + R_top/R_bot) ≈ 5.0V)
                  └── C_boot: 100 nF (bootstrap)
```

| Componente | Referencia | Valor | Encapsulado | Función |
|------------|-----------|-------|-------------|---------|
| U1 | TPS54302DDCR | Buck 3A, 4.5–28V in | SOT-23-6 | Regulador 12V → 5V |
| L1 | 744043004700 | 4.7 μH / 4A sat | 4×4×2 mm | Inductor de potencia |
| C3, C4 | X5R 25V | 22 μF | 0805 | Capacitor entrada buck |
| C5, C6 | X5R 10V | 47 μF | 0805 | Capacitor salida buck |
| R1 | — | 100 kΩ ±1% | 0402 | Feedback superior |
| R2 | — | 24.9 kΩ ±1% | 0402 | Feedback inferior |
| C7 | — | 100 nF | 0402 | Bootstrap |

#### 2.1.3 Regulador 3.3V — LDO

```
    5V_RAIL ──►[AMS1117-3.3]──► 3.3V_RAIL (800 mA max)
                  │
                  ├── C_in: 10 μF ceramic (X5R, 10V)
                  └── C_out: 22 μF ceramic (X5R, 10V) + 10 μF tantálum
```

| Componente | Referencia | Valor | Encapsulado | Función |
|------------|-----------|-------|-------------|---------|
| U2 | AMS1117-3.3 | LDO 3.3V / 800 mA | SOT-223 | Regulador 5V → 3.3V |
| C8 | X5R 10V | 10 μF | 0805 | Desacoplo entrada LDO |
| C9 | X5R 10V | 22 μF | 0805 | Estabilidad salida LDO |
| C10 | Tantálum | 10 μF / 10V | 1206 | ESR serie estabilidad |

#### 2.1.4 Indicadores de Estado de Potencia

| LED | Color | Función | Resistor (3.3V) |
|-----|-------|---------|-----------------|
| LED_12V | Rojo | Presencia 12V rail | 4.7 kΩ (vía divisor) |
| LED_5V | Verde | 5V rail OK | 330 Ω |
| LED_3V3 | Azul | 3.3V rail OK | 100 Ω |

---

### 2.2 Bloque de Adquisición Analógica (6 canales)

#### 2.2.1 Arquitectura por Canal

Cada canal analógico implementa la cadena de señal completa:

```
    SENSOR ──►[CONECTOR]──►[ESD TVS]──►[RC FILTER]──►[OP-AMP BUFFER]──►[ADC STM32]
               BNC/JST      PESD5V0     R=1kΩ          MCP6002          12-bit
               IP67          < 1 pF      C=100nF        Rail-to-Rail     Oversampling ×8
                             5V clamp    f_c = 1.59 kHz  Unity gain
```

#### 2.2.2 Detalle por Canal Analógico

##### Canal A0 — pH (Essential+)

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| J1 | BNC hembra | — | Conector sonda pH (con aislamiento) |
| D3 | PESD5V0S1BSF | 5V TVS | Protección ESD IEC 61000-4-2 Level 4 |
| R3 | — | 1 kΩ ±1% | Filtro RC antialiasing |
| C11 | — | 100 nF X7R | Filtro RC (f_c ≈ 1.59 kHz) |
| U3A | MCP6002-I/SN | Rail-to-rail op-amp | Buffer impedancia (Z_in > 10 MΩ) |
| R4 | — | 10 MΩ | Pull-down bias (evita flotante sin sensor) |

**Nota pH:** La sonda pH genera señales de muy alta impedancia (~100 MΩ). El buffer op-amp es **crítico** para evitar errores de lectura. Para producción con Atlas EZO, el circuito analógico se bypasea y se usa I2C (0x63).

##### Canal A1 — ORP (Essential+)

Idéntico al canal pH, con conector BNC separado (J2). Dirección I2C Atlas: 0x62.

##### Canal A2 — Presión CO₂ (Insight+)

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| J3 | JST-XH 3-pin | — | Conector transductor presión (VCC, OUT, GND) |
| D4 | PESD5V0S1BSF | 5V TVS | Protección ESD |
| R5, C12 | 1 kΩ / 100 nF | RC filter | Antialiasing |
| U3B | MCP6002 (canal B) | Buffer | Impedancia matching |
| R6, R7 | 10 kΩ / 10 kΩ | Divisor opcional | Escalado 4.5V → 3.3V si necesario |

**Señal transductor:** 0.5–4.5V (ratiométrico a 5V VCC). Mapeo lineal:
- 0.5V = 0 PSI (0 kPa)
- 4.5V = 30 PSI (207 kPa)

##### Canal A3 — Oxígeno Disuelto (Insight+)

Idéntico a canal pH (alta impedancia electroquímica). Conector BNC (J4). I2C Atlas: 0x61.

##### Canal A4 — Temperatura NTC (Essential+)

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| J5 | JST-XH 2-pin | — | Conector NTC 10K |
| R8 | 10 kΩ ±1% | — | Resistencia serie (divisor de tensión) |
| C13 | 100 nF X7R | — | Filtro paso bajo |
| D5 | PESD3V3S1BSF | 3.3V TVS | Protección ESD (señal 0–3.3V) |

**Circuito NTC:** Divisor de tensión con R_serie = 10 kΩ. Steinhart-Hart en firmware.

```
    3.3V ──[R8 = 10kΩ]──┬──► A4 (ADC)
                         │
                        [NTC 10kΩ]
                         │
                        GND
```

##### Canal A5 — Humedad SHT30 (Signature)

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| J6 | JST-XH 3-pin | — | Conector sensor humedad (VCC, OUT, GND) |
| D6 | PESD3V3S1BSF | 3.3V TVS | Protección ESD |
| R9, C14 | 1 kΩ / 100 nF | RC filter | Antialiasing |

#### 2.2.3 Aislamiento Galvánico — Sensores Electroquímicos

Los sensores pH, ORP y DO comparten el mismo líquido (mosto de fermentación). Sin aislamiento, se generan **ground loops** que corrompen las lecturas.

**Solución dual:**

1. **Con Atlas Scientific EZO (producción):** Cada carrier board ISCCB-2 proporciona aislamiento galvánico integrado (>1 kV DC). Sin componentes adicionales en el Q-Shield.

2. **Con sensores analógicos (prototipo):** El Q-Shield incluye aislamiento en la PCB:

```
    SONDA pH ──►[ISO7721 Digital Isolator]──► I2C aislado
                 o
    SONDA pH ──►[ADUM3151 ADC aislado]──► SPI aislado ──► MCU
```

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| U4 | ISO7721DR | 2-ch digital isolator, 100 Mbps | Aislamiento I2C (para Atlas EZO) |
| U5 | Si8661BA | 6-ch digital isolator | Alternativa multi-canal |
| C15–C18 | 100 nF × 4 | — | Desacoplo lados aislados (2 por lado) |

**Especificación aislamiento:**
- Voltaje de aislamiento: >2.5 kV RMS (1 min)
- CMTI (Common Mode Transient Immunity): >25 kV/μs
- Cumple UL 1577, CSA, IEC 60747-5-5

---

### 2.3 Bloque I2C (Bus Digital)

#### 2.3.1 Topología del Bus

```
    STM32U585 I2C1 ──[R_PU 4.7kΩ to 3.3V]──┬──► GPS (0x42)
         SDA, SCL                             ├──► Cell Density (0x30)
                                              ├──► RTC DS3231 (0x68)
                                              ├──► EZO-pH (0x63) *opcional
                                              ├──► EZO-ORP (0x62) *opcional
                                              ├──► EZO-DO (0x61) *opcional
                                              └──► EZO-RTD (0x66) *opcional
```

#### 2.3.2 Componentes I2C

| Componente | Ref | Función | Notas |
|------------|-----|---------|-------|
| R10, R11 | 4.7 kΩ | Pull-up SDA/SCL a 3.3V | Para bus 400 kHz (Fast Mode) |
| D7, D8 | PESD3V3S2USF | ESD dual-line protection | IEC 61000-4-2 Level 4 |
| J7 | JST-SH 4-pin (Qwiic compatible) | Conector GPS SAM-M8Q | VCC/GND/SDA/SCL |
| J8 | JST-SH 4-pin | Conector RTC DS3231 | VCC/GND/SDA/SCL |
| J9 | JST-SH 4-pin | Conector Cell Density | VCC/GND/SDA/SCL |
| J10–J13 | JST-SH 4-pin | Conectores Atlas EZO × 4 | Aislados vía U4/U5 |

#### 2.3.3 Protección del Bus I2C

- **ESD:** PESD3V3S2USF (doble línea SDA/SCL) — capacitancia < 0.5 pF, sin degradar señal a 400 kHz
- **Pull-ups:** 4.7 kΩ a 3.3V (calculados para 400 kHz con capacitancia total de bus ~200 pF)
- **Longitud máxima de bus:** 1 metro (con cables apantallados)
- **Repetidor I2C:** PCA9515A disponible como opción si la longitud del bus excede 1 m

---

### 2.4 Bloque Digital — HX711 (Load Cell ADC)

```
    CELDA DE CARGA ──►[HX711 24-bit ADC]──► D2 (DOUT) / D3 (SCK) ──► STM32
         (4 hilos)     ┌────────────────┐
         E+, E-, S+, S-│ Ganancia: 128  │
                        │ Rate: 80 SPS   │
                        │ VCC: 5V        │
                        └────────────────┘
```

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| U6 | HX711 | 24-bit ADC, 80 SPS | ADC de precisión para celda de carga |
| J14 | Terminal block 4-pin | — | Conector celda de carga (E+/E-/S+/S-) |
| C19 | 100 nF | — | Desacoplo VCC HX711 |
| C20 | 10 μF | — | Filtro alimentación HX711 |
| R12 | 10 kΩ | Pull-up DOUT | Evita flotante durante arranque |

---

### 2.5 Bloque de Actuadores

#### 2.5.1 Driver de Motor — Bomba Peristáltica (Insight+)

```
    MCU D5 (PWM) ──►[PC817 Optoacoplador]──►[IR2104 Half-Bridge]──► MOTOR 12V
    MCU D4 (DIR) ──►[PC817 Optoacoplador]──►[IR2104 Half-Bridge]──► (bidireccional)
```

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| U7 | IR2104SPBF | Half-bridge driver, 600V/250mA | Driver motor bomba |
| Q1, Q2 | IRLZ44NPBF | N-MOSFET 55V/47A, logic-level | Interruptores de potencia |
| U8, U9 | PC817X2NIP | Optoacoplador dual | Aislamiento MCU ↔ potencia |
| D9, D10 | SS34 | Schottky 3A | Diodos flyback motor |
| R13–R16 | 1 kΩ | — | Limitadores corriente base optoacopladores |
| C21 | 100 nF | — | Desacoplo VCC driver |

#### 2.5.2 Relays — Chiller y Solenoide CO₂

```
    MCU D6 ──►[R 1kΩ]──►[PC817]──►[RELAY K1]──► CHILLER 12V (Signature)
    MCU D7 ──►[R 1kΩ]──►[PC817]──►[RELAY K2]──► SOLENOIDE CO₂ NC (Insight+)
```

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| K1 | HF46F-12-HS1 | Relay 12V, 5A/250VAC | Chiller relay |
| K2 | HF46F-12-HS1 | Relay 12V, 5A/250VAC | CO₂ solenoide relay |
| D11, D12 | 1N4148W | Diodo flyback | Protección bobina relay |
| Q3, Q4 | 2N7002 | N-MOSFET SOT-23 | Driver relay (con optoacoplador) |
| U10, U11 | PC817X1NIP | Optoacoplador | Aislamiento MCU ↔ relay |
| R17–R20 | 1 kΩ | — | Limitadores corriente |

#### 2.5.3 Regulador Flujo CO₂ PWM (Insight+)

```
    MCU D9 (PWM) ──►[RC Filter]──►[Op-Amp]──►[MOSFET]──► Válvula proporcional
                    R=10kΩ          MCP6002    IRLZ44N     0–12V proporcional
                    C=100nF         Gain=3.6x
```

| Componente | Ref | Valor | Función |
|------------|-----|-------|---------|
| R21 | 10 kΩ | — | Filtro RC PWM-to-analog |
| C22 | 100 nF | — | Filtro RC (f_c = 159 Hz) |
| U3C | MCP6002 | Non-inverting amp | Escalar 3.3V PWM → 12V gate |
| Q5 | IRLZ44NPBF | N-MOSFET | Driver válvula proporcional |
| D13 | SS34 | Schottky | Flyback válvula |

---

### 2.6 Bloque de HMI (Human-Machine Interface)

#### 2.6.1 Conexión HMI UART

```
    MCU (D0/D1 UART) ──►[Q-Shield J_HMI JST-XH 4P]──►[Cable JST-XH]──► Nextion/Stone 5"
```

| Componente | Ref | Función |
|------------|-----|---------|
| J_HMI | JST-XH 4-pin (B4B-XH-A) | Conector HMI: 5V/TX/RX/GND |
| D_HMI | PESD3V3S2USF | ESD protection UART dual-line |

> **Nota de diseño:** El Arduino UNO Q no tiene salida HDMI (solo DisplayPort Alt-Mode vía USB-C).
> El HMI UART simplifica el diseño: elimina 5 componentes (~$2.45), routing de alta velocidad,
> y utiliza un protocolo serial ASCII simple.

#### 2.6.2 Pantalla HMI Nextion/Stone 5"

| Especificación | Valor |
|---------------|-------|
| Resolución | 800 × 480 px |
| Touch | Capacitivo, 5 puntos |
| Interfaz | UART TTL (115200 baud) |
| Protocolo | ASCII serial (Nextion) / JSON (Stone) |
| Alimentación | 5V vía JST-XH pin 1 |
| Conector | JST-XH 4-pin: VCC / TX / RX / GND |
| Procesador | Integrado (renderiza UI localmente) |

---

### 2.7 Bloque de Status LED

```
    MCU D13 ──►[R 330Ω]──►[LED Bicolor Rojo/Verde]──► GND
```

| Estado | Patrón | Significado |
|--------|--------|-------------|
| Verde continuo | — | Sistema operativo normal |
| Verde parpadeo 1 Hz | — | Adquiriendo datos |
| Rojo continuo | — | Error crítico (watchdog) |
| Rojo parpadeo rápido | 5 Hz | Fallo de comunicación IPC |
| Alternando rojo/verde | 0.5 Hz | FOTA en progreso |

---

## 3. Tabla de Conectores Completa

| Ref | Tipo | Pines | Función | Tier |
|-----|------|-------|---------|------|
| J1 | BNC hembra panel | 1 | Sonda pH | Essential+ |
| J2 | BNC hembra panel | 1 | Sonda ORP | Essential+ |
| J3 | JST-XH 3-pin | VCC/OUT/GND | Transductor presión CO₂ | Insight+ |
| J4 | BNC hembra panel | 1 | Sonda DO | Insight+ |
| J5 | JST-XH 2-pin | SIGNAL/GND | Termistor NTC | Essential+ |
| J6 | JST-XH 3-pin | VCC/OUT/GND | Sensor humedad | Signature |
| J7 | JST-SH 4-pin (Qwiic) | VCC/GND/SDA/SCL | GPS SAM-M8Q | Essential+ |
| J8 | JST-SH 4-pin (Qwiic) | VCC/GND/SDA/SCL | RTC DS3231 | Todos |
| J9 | JST-SH 4-pin (Qwiic) | VCC/GND/SDA/SCL | Cell Density | Signature |
| J10 | JST-SH 4-pin | VCC/GND/SDA/SCL | Atlas EZO-pH | Opcional |
| J11 | JST-SH 4-pin | VCC/GND/SDA/SCL | Atlas EZO-ORP | Opcional |
| J12 | JST-SH 4-pin | VCC/GND/SDA/SCL | Atlas EZO-DO | Opcional |
| J13 | JST-SH 4-pin | VCC/GND/SDA/SCL | Atlas EZO-RTD | Opcional |
| J14 | Terminal block 4-pin | E+/E-/S+/S- | Celda de carga | Essential+ |
| J_HMI | JST-XH 4-pin | 4 (5V/TX/RX/GND) | HMI UART (Nextion/Stone) | Todos |
| J_RS485 | Terminal block 4-pin | 4 | RS485 (Hamilton Incyte) | Signature |
| J17 | Terminal block 2-pin | +/- | Entrada 12V DC | Todos |
| J18 | Terminal block 2-pin | +/- | Motor bomba 12V | Insight+ |
| J19 | Terminal block 2-pin | +/- | Solenoide CO₂ 12V | Insight+ |
| J20 | Terminal block 2-pin | +/- | Chiller 12V | Signature |
| J21 | Pin header 2×20 | 40 | Shield stackup Arduino UNO | Todos |

---

## 4. Mapa de Pines — STM32U585 (Arduino UNO Q)

### 4.1 Pines Analógicos (ADC)

| Pin Arduino | Pin STM32 | ADC Canal | Función | Resolución | Tier |
|-------------|-----------|-----------|---------|------------|------|
| A0 | PA0 | ADC1_IN0 | pH analog input | 12-bit + 8× oversample | Essential+ |
| A1 | PA1 | ADC1_IN1 | ORP analog input | 12-bit + 8× oversample | Essential+ |
| A2 | PA2 | ADC1_IN2 | CO₂ pressure | 12-bit + 8× oversample | Insight+ |
| A3 | PA3 | ADC1_IN3 | Dissolved oxygen | 12-bit + 8× oversample | Insight+ |
| A4 | PA4 | ADC1_IN4 | Temperature NTC | 12-bit + 8× oversample | Essential+ |
| A5 | PA5 | ADC1_IN5 | Humidity SHT30 | 12-bit + 8× oversample | Signature |

### 4.2 Pines Digitales (GPIO)

| Pin Arduino | Pin STM32 | Función | Dirección | Tier |
|-------------|-----------|---------|-----------|------|
| D2 | — | HX711 DOUT | INPUT | Essential+ |
| D3 | — | HX711 SCK | OUTPUT | Essential+ |
| D4 | — | Watchdog WDI (TPS3823) | OUTPUT | Todos |
| D5 | PA11 | Pump PWM (TIM1_CH4) | OUTPUT (PWM) | Insight+ |
| D6 | PB1 | Pump direction | OUTPUT | Insight+ |
| D7 | — | CO₂ solenoid valve | OUTPUT | Insight+ |
| D8 | PB4 | Chiller relay | OUTPUT | Signature |
| D9 | PB8 | CO₂ flow PWM (TIM4_CH3) | OUTPUT (PWM) | Insight+ |
| D10 | PB9 | RS485 bridge ~IRQ (SC16IS740) | INPUT | Signature |
| D13 | — | Status LED | OUTPUT | Todos |

> **PWM en timers independientes:** `PUMP_PWM` (D5, TIM1_CH4) y `CO2_PWM`
> (D9, TIM4_CH3) están en temporizadores distintos, por lo que sus frecuencias
> se ajustan por separado.
>
> **Watchdog:** D4 alimenta el `WDI` del TPS3823. El firmware debe hacer toggle
> del pin con periodo < 1.6 s o el supervisor resetea el MCU.
>
> Las celdas con `—` son puertos del STM32U585 aún no verificados contra el
> variant oficial del UNO Q. Lo que fija el diseño del shield es la columna
> «Pin Arduino», que es la que consume el firmware.

### 4.3 Pines I2C

| Pin | Función | Velocidad |
|-----|---------|-----------|
| SDA (A4 alt) | I2C1 Data | 400 kHz (Fast Mode) |
| SCL (A5 alt) | I2C1 Clock | 400 kHz (Fast Mode) |

### 4.4 UART (IPC MCU ↔ MPU)

| Pin | Función | Baudrate |
|-----|---------|----------|
| TX1 | Serial1 TX → MPU RX | 115200 |
| RX1 | Serial1 RX ← MPU TX | 115200 |

> **Nota:** La UART MCU↔MPU es **interna** del Arduino UNO Q. No se expone en el Q-Shield.

---

## 5. Desacoplo y Bypass

### 5.1 Regla General

Cada IC recibe un capacitor de desacoplo lo más cerca posible de sus pines VCC/GND:

| Tipo IC | Capacitor | Encapsulado | Distancia máx. a pin VCC |
|---------|-----------|-------------|--------------------------|
| Op-amp (MCP6002) | 100 nF X7R | 0402 | < 3 mm |
| Digital (ISO7721) | 100 nF + 10 μF | 0402 + 0805 | < 5 mm |
| HX711 | 100 nF + 10 μF | 0402 + 0805 | < 5 mm |
| Reguladores | Según datasheet | — | En pads |

### 5.2 Mapa de Desacoplo

| Ref | Valor | IC asociado | Notas |
|-----|-------|-------------|-------|
| C23 | 100 nF | U3 (MCP6002) | Entre VDD y VSS, < 3 mm |
| C24 | 100 nF | U4 (ISO7721 lado 1) | Lado MCU |
| C25 | 100 nF | U4 (ISO7721 lado 2) | Lado sensor |
| C26, C27 | 100 nF + 10 μF | U6 (HX711) | Alimentación ADC |
| C28 | 100 nF | U7 (IR2104) | Driver motor |
| C29 | 100 nF | U8, U9 (PC817) | Optoacopladores |

---

## 6. Zonas de Layout PCB

```
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        Q-SHIELD TOP VIEW (100 × 100 mm)                          │
    │                                                                                  │
    │  ┌──────────────────────┐  ┌────────────────────────────────────────────────┐   │
    │  │ ZONA POTENCIA        │  │    ZONA ANALÓGICA (guard ring GND)             │   │
    │  │ (20 × 30 mm)         │  │    (50 × 45 mm)                               │   │
    │  │                      │  │                                                │   │
    │  │ Reguladores          │  │    BNC: pH, ORP, DO                            │   │
    │  │ Buck, LDO            │  │    JST: CO₂, Temp, Humedad                    │   │
    │  │ Fusible, TVS         │  │    Op-amps (MCP6002), filtros RC               │   │
    │  │ Watchdog TPS3823     │  │    SN6501 + AMC1301 (aislamiento galvánico)    │   │
    │  │                      │  │    Transformadores T1-T3                        │   │
    │  └──────────────────────┘  └────────────────────────────────────────────────┘   │
    │                                                                                  │
    │  ┌──────────────────────────────┐  ┌────────────────────────────────────┐       │
    │  │ ZONA ACTUADORES              │  │    ZONA DIGITAL                    │       │
    │  │ (40 × 40 mm)                 │  │    (40 × 30 mm)                    │       │
    │  │ (plano GND separado)         │  │                                    │       │
    │  │                              │  │    I2C bus + 7× Qwiic              │       │
    │  │ Relays K1/K2, MOSFETs Q1-Q5 │  │    HX711 + load cell               │       │
    │  │ Optoacopladores PC817        │  │    ISO1541 (aislador I2C)          │       │
    │  │ Terminales potencia          │  │    RS485, HMI UART, LED status     │       │
    │  │ CO₂ PWM (R28/C27/U20/Q5)    │  │                                    │       │
    │  └──────────────────────────────┘  └────────────────────────────────────┘       │
    │                                                                                  │
    │  ┌──────────────────────────────────────────────────────────────────────────┐   │
    │  │            J21 — ARDUINO UNO Q SHIELD HEADER (2×20, 98 mm)               │   │
    │  └──────────────────────────────────────────────────────────────────────────┘   │
    └──────────────────────────────────────────────────────────────────────────────────┘
```

> **Nota:** Análisis detallado de compactación y restricciones mecánicas en `docs/08_MECHANICAL_ANALYSIS.md`.

**Reglas de separación:**
- Zona analógica aislada con guard ring de GND (vía fence cada 2 mm)
- Zona de actuadores sobre el mismo plano GND continuo (tierra única — ver `06_PCB_LAYOUT_STACKUP.md` §4.5); la separación se logra por placement y vías locales, no cortando el plano
- Mínimo 3 mm entre zona analógica y zona de actuadores
- Pistas de potencia (12V, motor) en capa 3 (PWR) con vías térmicas

---

## 7. Criterios de Diseño para Tiers

El Q-Shield usa una **PCB única** para los tres tiers. Los componentes no poblados se seleccionan en fabricación:

| Componente | Essential | Insight | Signature |
|-----------|:---------:|:-------:|:---------:|
| pH (A0 + buffer) | ✓ | ✓ | ✓ |
| ORP (A1 + buffer) | ✓ | ✓ | ✓ |
| Temp (A4 + divisor) | ✓ | ✓ | ✓ |
| Load cell (HX711) | ✓ | ✓ | ✓ |
| GPS (I2C) | ✓ | ✓ | ✓ |
| RTC (I2C) | ✓ | ✓ | ✓ |
| HMI UART (Nextion) | ✓ | ✓ | ✓ |
| CO₂ presión (A2) | DNP | ✓ | ✓ |
| DO (A3 + buffer) | DNP | ✓ | ✓ |
| Bomba (driver) | DNP | ✓ | ✓ |
| CO₂ inyección (relay+PWM) | DNP | ✓ | ✓ |
| Humedad (A5) | DNP | DNP | ✓ |
| Cell density (I2C) | DNP | DNP | ✓ |
| Chiller (relay) | DNP | DNP | ✓ |

> **DNP** = Do Not Populate. Los footprints siempre están presentes en la PCB.

---

*Documento NQS-ARCH-001 Rev 1.0 — Nebula Ecosystem®*
