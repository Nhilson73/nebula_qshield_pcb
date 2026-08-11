# Nebula Q-Shield® — Guías de Layout PCB y Stackup

> **Documento:** NQS-LAY-006 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Diseño Físico PCB
>
> **Normativas de referencia:** IPC-2221B, IPC-7351C, IPC-2152

---

## 1. Stackup de 4 Capas — Especificación Detallada

### 1.1 Estructura de Capas

```
    ═══════════════════════════════════════════════════════════════
    Capa 1 (TOP) — Señales + Componentes SMD          35 μm Cu
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    Prepreg 7628 (#2116 alternativo)                   0.20 mm
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    Capa 2 (GND) — Plano de tierra CONTINUO            35 μm Cu
    ═══════════════════════════════════════════════════════════════
    Core FR-4 (IT-180A, Tg 170°C)                     0.80 mm
    ═══════════════════════════════════════════════════════════════
    Capa 3 (PWR) — Planos de potencia                  35 μm Cu
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    Prepreg 7628 (#2116 alternativo)                   0.20 mm
    ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
    Capa 4 (BOT) — Señales + Componentes SMD          35 μm Cu
    ═══════════════════════════════════════════════════════════════
    
    Espesor total: 35+200+35+800+35+200+35 μm = 1,340 μm Cu + diel.
    Con máscaras: ~1.6 mm ± 10%
```

### 1.2 Asignación de Capas

| Capa | Nombre | Función | Contenido |
|------|--------|---------|-----------|
| L1 (TOP) | Signal_Top | Señales y componentes | Pistas de señal, componentes SMD/THT, pads |
| L2 | GND | Plano de tierra | **Continuo sin interrupciones** — retorno de corriente para todas las señales; polígono extendido al board 125 × 120 mm |
| L3 | PWR | Planos de potencia | Islas: 12V, 5V, 3.3V separadas por clearance |
| L4 (BOT) | Signal_Bot | Señales secundarias | Pistas secundarias, componentes SMD (cara inferior), test points; también flood `GND` para retorno |

### 1.3 Distribución del Plano de Potencia (Capa 3)

```
    ┌────────────────────────────────────────────────────────┐
    │                   CAPA 3 — PWR                         │
    │                                                        │
    │  ┌──────────────────┐  ┌───────────────────────────┐  │
    │  │                  │  │                           │  │
    │  │    12V RAIL      │  │       5V RAIL             │  │
    │  │                  │  │                           │  │
    │  │  (Actuadores,    │  │  (Arduino UNO Q,         │  │
    │  │   Relays,        │  │   Display, GPS,          │  │
    │  │   Motor driver)  │  │   HX711, Optos)          │  │
    │  │                  │  │                           │  │
    │  └──────────────────┘  │  ┌─────────────────────┐ │  │
    │                        │  │    3.3V RAIL         │ │  │
    │                        │  │  (Op-amps, I2C,     │ │  │
    │                        │  │   ISO, sensors)      │ │  │
    │                        │  └─────────────────────┘ │  │
    │                        └───────────────────────────┘  │
    │         ↑ clearance 0.5 mm entre islas ↑              │
    └────────────────────────────────────────────────────────┘
```

> **Nota de estado actual:** el board es **125 × 120 mm** (se amplió el ancho durante Fase 5 para que los conectores de borde no sobresalgan). La zona `/12V_RAIL` en `In2.Cu` (prioridad 1) ya cubre todo el board; las islas `/5V_RAIL` y `/3V3_RAIL` (prioridades 2-9) se recortan automáticamente formando un split-plane por prioridades. Durante Fase 5, `In1.Cu` se usó como capa de señal adicional durante el autoruteo para reducir desconectados; esto debe revisarse antes de fabricación. `kicad-cli pcb drc --severity-error` pasa sin violaciones (47 unconnected items). Ver `docs/INSIGHT_FABRICATION_ROADMAP.md` Fases 4-5.

---

## 2. Reglas de Diseño (Design Rules)

### 2.1 Reglas Generales

| Parámetro | Clase Señal | Clase Potencia | Clase Alta Corriente |
|-----------|-------------|----------------|---------------------|
| Ancho mínimo de pista | 0.20 mm (8 mil) | 0.50 mm (20 mil) | 1.00 mm (40 mil) |
| Espacio mínimo pista-pista | 0.20 mm | 0.30 mm | 0.50 mm |
| Espacio pista-plano | 0.20 mm | 0.30 mm | 0.50 mm |
| Espacio pista-borde PCB | 0.25 mm | 0.50 mm | 0.50 mm |
| Via drill | 0.30 mm | 0.40 mm | 0.50 mm |
| Via pad | 0.60 mm | 0.80 mm | 1.00 mm |
| Via annular ring | ≥ 0.15 mm | ≥ 0.20 mm | ≥ 0.25 mm |

### 2.2 Ancho de Pista por Corriente (IPC-2152, 1 oz Cu, ΔT 20°C)

| Corriente | Ancho pista ext. | Ancho pista int. | Aplicación |
|-----------|-----------------|-----------------|------------|
| 100 mA | 0.20 mm (8 mil) | 0.25 mm | Señales analógicas |
| 500 mA | 0.50 mm (20 mil) | 0.75 mm | 5V distribución |
| 1 A | 0.80 mm (32 mil) | 1.20 mm | 5V principal |
| 2 A | 1.50 mm (60 mil) | 2.20 mm | 12V actuadores |
| 3 A | 2.20 mm (87 mil) | 3.20 mm | 12V entrada / Chiller |
| 5 A | 3.50 mm (138 mil) | 5.00 mm | Chiller Peltier |

### 2.3 Clearance de Voltaje (IPC-2221B, Tabla 6.1)

| Voltaje entre conductores | Clearance interno (coated) | Clearance externo (uncoated) |
|--------------------------|---------------------------|------------------------------|
| ≤ 15V DC | 0.1 mm (4 mil) | 0.1 mm |
| ≤ 50V DC | 0.6 mm (24 mil) | 0.6 mm |
| ≤ 100V DC | 0.6 mm | 1.5 mm |
| ≤ 300V AC (relay contacts) | 2.0 mm | 2.5 mm |

> **Nota:** Los relays K1/K2 manejan hasta 250V AC en sus contactos. Las pistas de potencia de los contactos relay deben tener **clearance ≥ 2.5 mm** respecto a señales de baja tensión.

---

## 3. Zonas de Layout y Placement

### 3.1 Mapa de Zonas (Vista Superior)

```
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │  125 mm                                                                          │
    │  ┌──────────────────────────────────────────────────────────────────────────┐    │
    │  │                                                                          │    │
    │  │  ZONA A: POTENCIA (20×30mm)     │  ZONA B: ANALÓGICA (50×45mm)         │    │
    │  │  ┌─────────────────────┐        │  ┌──────────────────────────────────┐ │    │
    │  │  │ J1 (12V barrel jack)│        │  │ J2 (pH BNC)  J3 (ORP BNC)       │ │    │
    │  │  │ D1 TVS, F1 PTC     │        │  │ J5 (DO BNC)                      │ │    │
    │  │  │ D2 SS34            │        │  │ J4 (CO₂ JST) J6 (NTC) J7 (Hum) │ │    │
    │  │  │ U1 TPS54302 + L1   │        │  │ U4/U7/U10/U11 MCP6002 buffers   │ │    │
    │  │  │ U2 AMS1117         │        │  │ U5/U8/U12 SN6501 + T1-T3       │ │  125
    │  │  │ C1, C2 (bulk caps) │        │  │ U6/U9/U13 AMC1301 (isolation)   │ │  mm
    │  │  │ U3 TPS3823 + SW1   │        │  │ RC filters, ESD TVS              │ │    │
    │  │  │ LED1-3, R4-R6      │        │  │ Guard ring GND                   │ │    │
    │  │  └─────────────────────┘        │  └──────────────────────────────────┘ │    │
    │  │                                  │                                      │    │
    │  │  ZONA D: ACTUADORES (40×40mm)   │  ZONA C: DIGITAL (40×30mm)          │    │
    │  │  ┌─────────────────────────┐    │  ┌──────────────────────────────┐    │    │
    │  │  │ U16 PC817X2 (motor)    │    │  │ J8-J14 Qwiic connectors (7×)│    │    │
    │  │  │ U17 IR2104             │    │  │ U14 HX711 + J15 load cell   │    │    │
    │  │  │ Q1, Q2 IRLZ44N        │    │  │ R19-R20 I2C pull-ups        │    │    │
    │  │  │ D10, D11 flyback       │    │  │ D9 TVS I2C                  │    │    │
    │  │  │ J17 motor terminal     │    │  │ U15 MAX485 + J16 RS485     │    │    │
    │  │  │ K1, K2 relays          │    │  │ U21 ISO1541                 │    │    │
    │  │  │ U18, U19 PC817 (relay) │    │  │ LED4 status + R23          │    │    │
    │  │  │ Q3-Q5, D12-D14        │    │  │ J20 HMI UART (JST-XH 4P)  │    │    │
    │  │  │ J18, J19, J22 terms   │    │  └──────────────────────────────┘    │    │
    │  │  │ R28, C27, U20 (CO2)    │    │                                      │    │
    │  │  │ F2-F4 PTC fuses        │    │                                      │    │
    │  │  └─────────────────────────┘    │                                      │    │
    │  │                                                                        │    │
    │  │  ┌──────────────────────────────────────────────────────────────────┐  │    │
    │  │  │          J21 — ARDUINO UNO Q SHIELD HEADER (32 pines, ~50.8mm) │  │    │
    │  │  └──────────────────────────────────────────────────────────────────┘  │    │
    │  └──────────────────────────────────────────────────────────────────────────┘    │
    └──────────────────────────────────────────────────────────────────────────────────┘
```

> **Nota:** Ver `docs/08_MECHANICAL_ANALYSIS.md` para análisis detallado de compactación,
> restricciones de altura por componente, y recomendaciones de enclosure.

### 3.2 Reglas de Placement

| Regla | Descripción | Impacto |
|-------|-------------|---------|
| P1 | Conectores de entrada (12V, BNC) en borde superior | Acceso usuario |
| P2 | Componentes de protección (TVS, PTC) < 5 mm del conector asociado | ESD performance |
| P3 | Reguladores (U1, U2) junto a entrada 12V | Distribución limpia |
| P4 | Capacitores de desacoplo < 3 mm del IC asociado | Desacoplo efectivo |
| P5 | Zona analógica separada ≥ 3 mm de zona actuadores | Anti-crosstalk |
| P6 | MOSFETs y relays en borde de PCB | Disipación térmica convección |
| P7 | No colocar componentes bajo el Arduino (zona de ventilación) | Térmico |
| P8 | Cristal/osciladores lejos de conectores I/O | EMC |
| P9 | Test points accesibles desde cara inferior | Debug/ICT |

---

## 4. Routing Guidelines

### 4.1 Señales Analógicas (Zona B)

```
    REGLAS PARA SEÑALES ANALÓGICAS:
    
    ✓ Rutear en Capa 1 (TOP) exclusivamente
    ✓ Plano GND continuo debajo (Capa 2) — SIN INTERRUPCIONES
    ✓ Guard ring de GND alrededor de la zona analógica completa
    ✓ Pistas de señal analógica NO cruzan pistas digitales
    ✓ Separación ≥ 1 mm entre pistas analógicas adyacentes
    ✓ Vías de GND fence cada 2 mm alrededor del perímetro
    ✓ Resistencias de filtro RC lo más cerca posible del pad ADC
    ✓ NO pasar pistas de potencia por debajo de la zona analógica
    
    ✗ NO usar vías en señales analógicas (cambio de capa)
    ✗ NO rutear señales analógicas paralelas a pistas de reloj
    ✗ NO compartir vía de retorno GND con señales de potencia
```

### 4.2 Bus I2C (Zona C)

```
    REGLAS PARA BUS I2C:
    
    ✓ Pull-ups (R10, R11) lo más cerca posible del MCU
    ✓ SDA y SCL rutados en paralelo con separación ≥ 0.5 mm
    ✓ Longitud máxima total del bus: 20 cm en PCB
    ✓ TVS ESD (D7/D8) lo más cerca del primer conector I2C
    ✓ Capacitancia total del bus < 400 pF (para 400 kHz)
    
    Cálculo de capacitancia:
    - PCB traces (20 cm × ~1 pF/cm): 20 pF
    - 7 conectores × ~10 pF cada uno: 70 pF
    - TVS ESD (0.5 pF × 2): 1 pF
    - Pull-up parasitic: ~2 pF
    - Total: ~93 pF ✓ (muy debajo de 400 pF)
```

### 4.3 Líneas de Potencia (Zonas A y D)

```
    REGLAS PARA POTENCIA:
    
    ✓ Rutear preferentemente en Capa 3 (PWR) como planos
    ✓ Cuando necesario en L1/L4: pistas anchas (ver tabla §2.2)
    ✓ Vías de potencia: múltiples en paralelo para reducir resistencia
    ✓ Tierra unificada: un único net GND sobre el plano continuo de Capa 2
      (no existen nets AGND/DGND/PGND separados — ver §4.5)
    ✓ Bypass caps en pads de potencia de cada IC
    
    Vías de potencia — tabla de corriente:
    | Corriente | Vías 0.3mm | Vías 0.4mm | Vías 0.5mm |
    |-----------|-----------|-----------|-----------|
    | 0.5 A     | 1         | 1         | 1         |
    | 1.0 A     | 2         | 1         | 1         |
    | 2.0 A     | 4         | 3         | 2         |
    | 3.0 A     | 6         | 4         | 3         |
```

### 4.4 Líneas PWM de Actuadores

```
    REGLAS PARA PWM (D5, D9):
    
    ✓ Ferrite bead (120Ω @ 100MHz) en serie, lo más cerca del pin MCU
    ✓ Resistor de gate (10Ω) en serie hacia gate MOSFET
    ✓ Pista directa MCU → Optoacoplador → Driver/MOSFET
    ✓ Plano GND debajo para retorno limpio
    ✓ NO rutear junto a señales analógicas
```

### 4.5 Arquitectura de Tierra — GND Unificado

Decisión de diseño: **un único net `GND`** sobre el plano continuo de Capa 2.
No existen nets `AGND`, `DGND` ni `PGND` separados en el esquemático.

```
    TODOS los retornos (analógico, digital, potencia)
        ↓
    Plano GND continuo en Capa 2
        ↓
    Retorno al conector de entrada de alimentación
```

Fundamento:

- El "star grounding" se resuelve **a nivel de componente**, no partiendo el
  plano: cada bloque tiene su cap de desacoplo local y sus vías al plano a
  menos de 2 mm del pad, así que ve un retorno local de baja impedancia.
- Partir el plano crea discontinuidades en el camino de retorno, que a 4 capas
  empeoran la EMI en lugar de mejorarla.
- Cumple IPC-A-610 Clase 3, que pide continuidad de plano >95 % en circuitos
  analógicos.

**Lo que sí permanece aislado.** El aislamiento galvánico NO se hace con planos
de tierra separados, sino con la barrera de los AMC1301 y sus fuentes flotantes
(SN6501 + transformador). Estos nets son genuinamente flotantes y **no deben
unirse a `GND` bajo ninguna circunstancia**:

| Net aislado | Barrera | Alcance |
|-------------|---------|---------|
| `GND_ISO_PH` | U6 (AMC1301) + T1 | Sonda pH |
| `GND_ISO_ORP` | U9 (AMC1301) + T2 | Sonda ORP |
| `GND_ISO_DO` | U13 (AMC1301) + T3 | Sonda DO |
| `GND_ISO` | U21 (ISO1541) | Bus I2C aislado |

En el layout, cada uno de estos nets requiere su propio pour local separado del
plano principal por el clearance de la barrera de aislamiento — el plano
continuo de Capa 2 se refiere únicamente al dominio `GND`.

---

## 5. Guard Ring y Via Fence

### 5.1 Guard Ring Analógico

```
    ┌─────────────────────────────────────┐
    │  ●  ●  ●  ●  ●  ●  ●  ●  ●  ●    │ ← Vías GND cada 2 mm
    │  ●                              ●   │
    │  ●   ZONA ANALÓGICA             ●   │
    │  ●   (pH, ORP, DO, Temp,        ●   │ ← Pista GND 0.5 mm
    │  ●    CO₂, Humidity)            ●   │    en L1 (TOP)
    │  ●                              ●   │
    │  ●   Op-amps + Filtros RC       ●   │
    │  ●                              ●   │
    │  ●  ●  ●  ●  ●  ●  ●  ●  ●  ●    │
    └─────────────────────────────────────┘
    
    Especificación guard ring:
    - Pista de cobre: 0.5 mm ancho, conectada a GND
    - Vías al plano GND (L2): cada 2 mm, drill 0.3 mm
    - Cierra completamente el perímetro de la zona analógica
```

### 5.2 Via Fence de Borde de PCB

```
    Para cumplimiento EMC (EN 55032 Clase B):
    
    - Vías de GND fence a lo largo del borde de la PCB
    - Separación: cada 3 mm
    - Drill: 0.3 mm
    - Pad: 0.6 mm
    - Distancia al borde: 0.5 mm (clearance de fabricación)
    
    Esto crea un "muro" de GND que reduce la radiación
    electromagnética por los bordes de la PCB.
```

---

## 6. Thermal Management Layout

### 6.1 Thermal Vias bajo Regulador Buck (U1)

```
    ┌─────────────────────────┐
    │   U1 TPS54302 (SOT-23-6)│
    │   ┌───────────────────┐ │
    │   │   ○ ○ ○           │ │  ○ = Via térmica 0.3 mm
    │   │   ○ ○ ○           │ │  Array 3×3 bajo exposed pad
    │   │   ○ ○ ○           │ │  Conectadas al plano GND (L2)
    │   └───────────────────┘ │
    │                         │
    │   Plano de cobre expuesto│
    │   (cara inferior L4)     │  10 × 10 mm copper pour
    │   para disipación        │  conectado a GND vía vías
    └─────────────────────────┘
```

### 6.2 Heatsink Pads para MOSFETs (TO-220)

```
    Q1, Q2, Q5 (IRLZ44N TO-220):
    
    ┌─────────────┐
    │  ┌─────────┐│
    │  │ MOSFET  ││  Pad de cobre bajo tab: 10 × 15 mm
    │  │ TO-220  ││  Vías térmicas al plano GND: 2×3 array
    │  │         ││  NO conectar tab a GND si tab = Drain
    │  └─┤ ├─┤ ├┘│  (Verificar pinout — IRLZ44N tab = Drain)
    │    G  D  S  │
    └─────────────┘
    
    Para IRLZ44N: Tab = Drain
    → Pad de cobre aislado (NOT connected to GND)
    → Usar aislante térmico (silicone pad) si heatsink compartido
```

---

## 7. Solder Mask y Silkscreen

### 7.1 Solder Mask

| Regla | Valor |
|-------|-------|
| Solder mask expansion | 0.05 mm (2 mil) por lado |
| Solder mask minimum web | 0.10 mm (4 mil) |
| Solder mask clearance en vías tented | 0 (vías cubiertas por máscara) |
| Solder mask color | Verde (estándar) |

### 7.2 Silkscreen

| Elemento | Requisito |
|---------|-----------|
| Tamaño mínimo texto | 0.8 mm alto, 0.15 mm trazo |
| Referencia de componente | Junto a cada componente (ref. designator) |
| Polaridad | Marcas de pin 1 (punto/triángulo) en ICs y diodos |
| Valor | Solo en componentes críticos (resistores feedback, calibración) |
| Conectores | Nombre + función + pinout en cada conector |
| Versión PCB | "Q-SHIELD v1.0" + fecha + logo Nebula |
| Marcas CE/WEEE | En cara inferior (BOT silkscreen) |
| Advertencias | "⚠ 12V MAX" junto a J17, "⚠ HIGH VOLTAGE" junto a K1/K2 |

---

## 8. Test Points

| Test Point | Señal | Ubicación | Tipo |
|-----------|-------|-----------|------|
| TP1 | 12V_RAIL | Cerca de D2 salida | Pad 1.5 mm (BOT) |
| TP2 | 5V_RAIL | Salida U1 | Pad 1.5 mm (BOT) |
| TP3 | 3.3V_RAIL | Salida U2 | Pad 1.5 mm (BOT) |
| TP4 | GND | Centro zona analógica | Pad 1.5 mm (BOT) |
| TP5 | GND | Centro zona digital | Pad 1.5 mm (BOT) |
| TP6 | GND | Centro zona potencia | Pad 1.5 mm (BOT) |
| TP7 | pH_RAW | Salida buffer U3A | Pad 1.0 mm (BOT) |
| TP8 | ORP_RAW | Salida buffer U3B | Pad 1.0 mm (BOT) |
| TP9 | SDA | Bus I2C dato | Pad 1.0 mm (BOT) |
| TP10 | SCL | Bus I2C reloj | Pad 1.0 mm (BOT) |
| TP11 | PWM_PUMP | D5 salida | Pad 1.0 mm (BOT) |
| TP12 | PWM_CO2 | D9 salida | Pad 1.0 mm (BOT) |

---

## 9. Panelización

### 9.1 Configuración de Panel

```
    ┌─────────────────────────────────────────────────────┐
    │  Panel: 2 × 3 = 6 PCBs por panel                   │
    │                                                      │
    │  ┌──────┐  ┌──────┐  ┌──────┐                      │
    │  │ PCB1 │  │ PCB2 │  │ PCB3 │   ← V-score          │
    │  │      │  │      │  │      │      entre PCBs       │
    │  └──────┘  └──────┘  └──────┘                      │
    │  ┌──────┐  ┌──────┐  ┌──────┐                      │
    │  │ PCB4 │  │ PCB5 │  │ PCB6 │                      │
    │  │      │  │      │  │      │                      │
    │  └──────┘  └──────┘  └──────┘                      │
    │                                                      │
    │  Tooling holes: 3 × 3.2 mm (esquinas del panel)     │
    │  Fiducials: 3 × 1.0 mm (para pick-and-place)        │
    │  Rails: 5 mm top/bottom, 5 mm left/right            │
    └─────────────────────────────────────────────────────┘
```

### 9.2 Fiducials para Ensamblaje Automático

| Tipo | Cantidad | Tamaño | Ubicación |
|------|----------|--------|-----------|
| Panel global | 3 | 1.0 mm pad, 2.0 mm clearance | Esquinas panel (L-pattern) |
| PCB local | 2 | 1.0 mm pad, 2.0 mm clearance | Esquinas opuestas del PCB |

---

## 10. DFM (Design for Manufacturing) Checklist

| # | Check | Resultado |
|---|-------|-----------|
| 1 | Ancho mín. de pista ≥ 0.15 mm (fabricante estándar) | ✓ 0.20 mm |
| 2 | Espacio mín. ≥ 0.15 mm | ✓ 0.20 mm |
| 3 | Drill mín. ≥ 0.20 mm (laser) / 0.30 mm (mecánico) | ✓ 0.30 mm |
| 4 | Annular ring ≥ 0.10 mm | ✓ 0.15 mm |
| 5 | Solder mask web ≥ 0.10 mm | ✓ 0.10 mm |
| 6 | Copper-to-edge ≥ 0.25 mm | ✓ 0.25 mm |
| 7 | Pad-to-pad ≥ 0.20 mm | ✓ 0.20 mm |
| 8 | Via tenting en ambos lados (vías ≤ 0.4 mm) | ✓ Especificado |
| 9 | Fiducials para pick-and-place | ✓ 2 local + 3 panel |
| 10 | Tooling holes para jig | ✓ 3 × 3.2 mm |
| 11 | V-score o tab-route para panelización | ✓ V-score |
| 12 | Componentes ≥ 0.5 mm del borde V-score | ✓ Layout rule |
| 13 | Marcas de polaridad en todos los componentes polarizados | ✓ Silkscreen |
| 14 | BOM matches PCB footprints | ✓ Verificar post-layout |
| 15 | IPC Class 2 compliance | ✓ Especificado |

---

## 11. Archivos de Fabricación (Gerber Output)

| Archivo | Contenido | Extensión |
|---------|-----------|-----------|
| F.Cu | Capa 1 — Cobre TOP | .gtl |
| In1.Cu | Capa 2 — GND | .g2 |
| In2.Cu | Capa 3 — PWR | .g3 |
| B.Cu | Capa 4 — Cobre BOT | .gbl |
| F.Mask | Máscara soldadura TOP | .gts |
| B.Mask | Máscara soldadura BOT | .gbs |
| F.Silkscreen | Serigrafía TOP | .gto |
| B.Silkscreen | Serigrafía BOT | .gbo |
| Edge.Cuts | Contorno PCB | .gm1 |
| F.Paste | Stencil de pasta TOP | .gtp |
| B.Paste | Stencil de pasta BOT | .gbp |
| Drill | Taladrado PTH | .drl (Excellon) |
| NPTH | Taladrado no-plated | .drl (Excellon) |
| BOM | Bill of Materials | .csv |
| CPL | Component Placement List | .csv (X,Y,rotation,side) |

---

*Documento NQS-LAY-006 Rev 1.0 — Nebula Ecosystem® — Layout PCB y Stackup*
