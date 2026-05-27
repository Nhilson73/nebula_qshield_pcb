# Nebula Q-Shield® — Diseño 100% Foolproof

> **Documento:** NQS-FP-002 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Protección y Confiabilidad
>
> **Objetivo:** Garantizar que el Q-Shield® sobreviva a CUALQUIER error del usuario, condición ambiental adversa o fallo de componente sin daño permanente.

---

## 1. Filosofía Foolproof — Las 7 Capas de Protección

El diseño Q-Shield® implementa **7 capas de protección concéntricas** que aseguran que ningún error de usuario, transitorio eléctrico o fallo de componente pueda causar daño permanente al sistema.

```
    ┌───────────────────────────────────────────────────────────────┐
    │  CAPA 7: MONITOREO CONTINUO Y FAILSAFE POR FIRMWARE         │
    │  ┌───────────────────────────────────────────────────────┐   │
    │  │  CAPA 6: AISLAMIENTO GALVÁNICO                       │   │
    │  │  ┌───────────────────────────────────────────────┐   │   │
    │  │  │  CAPA 5: PROTECCIÓN TÉRMICA                   │   │   │
    │  │  │  ┌───────────────────────────────────────┐   │   │   │
    │  │  │  │  CAPA 4: LIMITACIÓN DE CORRIENTE      │   │   │   │
    │  │  │  │  ┌───────────────────────────────┐   │   │   │   │
    │  │  │  │  │  CAPA 3: SUPRESIÓN ESD/TVS    │   │   │   │   │
    │  │  │  │  │  ┌───────────────────────┐   │   │   │   │   │
    │  │  │  │  │  │  CAPA 2: POLARIDAD   │   │   │   │   │   │
    │  │  │  │  │  │  ┌───────────────┐   │   │   │   │   │   │
    │  │  │  │  │  │  │  CAPA 1:      │   │   │   │   │   │   │
    │  │  │  │  │  │  │  MECÁNICA     │   │   │   │   │   │   │
    │  │  │  │  │  │  └───────────────┘   │   │   │   │   │   │
    │  │  │  │  │  └───────────────────────┘   │   │   │   │   │
    │  │  │  │  └───────────────────────────────┘   │   │   │   │
    │  │  │  └───────────────────────────────────────┘   │   │   │
    │  │  └───────────────────────────────────────────────┘   │   │
    │  └───────────────────────────────────────────────────────┘   │
    └───────────────────────────────────────────────────────────────┘
```

---

## 2. CAPA 1 — Protección Mecánica

### 2.1 Conectores Keyed (Anti-Inserción Incorrecta)

Cada conector del Q-Shield® es **mecánicamente keyed** — es físicamente imposible conectarlo al revés o en el puerto equivocado.

| Conector | Tipo | Keying | Error que previene |
|----------|------|--------|-------------------|
| Sondas pH/ORP/DO | BNC hembra | Bayoneta con latch | Polaridad inversa imposible |
| Sensores analógicos | JST-XH (2.54 mm) | Polarizado con tab | Inversión de pines imposible |
| I2C (GPS, RTC, Cell) | JST-SH 4-pin (Qwiic) | 1.0 mm polarizado | Estándar Qwiic — universal |
| Celda de carga | Terminal block con tornillo | 4-pin etiquetado | Color-coded: E+/E-/S+/S- |
| HMI UART | JST-XH 4-pin (2.54 mm) | Polarizado con tab | Inversión de pines imposible |
| Alimentación 12V | DC barrel jack | 2.1×5.5mm, center-positive | Diámetro impide jacks incorrectos |

### 2.2 Etiquetado y Serigrafía

Cada conector tiene impreso en la PCB (serigrafía):

```
    ┌──────────────────────────────────────┐
    │  J1 pH PROBE                         │
    │  ◄── BNC ──►   ⚠ LÍQUIDO AISLADO    │
    │                                       │
    │  J3 CO₂ PRESS          J5 NTC TEMP   │
    │  [VCC][OUT][GND]       [SIG][GND]    │
    │   +5V  AN   ⏚          AN   ⏚       │
    │                                       │
    │  J17 POWER 12V DC                    │
    │  [+12V][ ⏚ GND]                     │
    │  ⚠ MAX 15V              ⚡ FUSED 3A  │
    └──────────────────────────────────────┘
```

### 2.3 Protección Mecánica PCB

| Característica | Especificación |
|---------------|----------------|
| Agujeros de montaje | 4× M3, patrón Arduino UNO (spacing 53.34 × 50.8 mm) |
| Standoffs | 10 mm nylon (aislamiento eléctrico) |
| Conformal coating | Humiseal 1B73 o equivalente acrílico (opcional, recomendado para IP54) |
| Bordes PCB | Rounded 1 mm radius (previene microfisuras) |

---

## 3. CAPA 2 — Protección de Polaridad Inversa

### 3.1 Entrada de Alimentación 12V

**Error del usuario:** Conectar la fuente 12V con polaridad invertida.

**Protección:** Diodo Schottky serie (SS34) en línea de alimentación positiva.

```
    JACK 12V ──►[D2 SS34 Schottky]──► 12V_RAIL
                 │
                 ├── V_f = 0.5V @ 3A (pérdida mínima)
                 ├── V_RRM = 40V (soporta hasta 40V inverso)
                 └── I_F_max = 3A (suficiente para carga completa)

    Si usuario conecta al revés:
    ─12V ──►[D2 BLOQUEADO]──X── No llega corriente
                                 Corriente = 0 mA
                                 Sin daño
```

**Alternativa para producción (mayor eficiencia):** P-MOSFET en configuración ideal diode.

```
    JACK 12V ──►[Q_PMOS Si2301CDS]──► 12V_RAIL
                 │
                 Gate ← Tied to source vía R (auto-on con polaridad correcta)
                 │
                 ├── R_ds_on = 0.112Ω (pérdida: 0.112W @ 1A vs 0.5W del Schottky)
                 └── V_ds_max = -20V (protección bidireccional)
```

### 3.2 Protección en Conectores de Sensor

Cada conector JST incluye un diodo de clamp a GND que absorbe polaridad inversa:

| Conector | Diodo | V_clamp | Función |
|----------|-------|---------|---------|
| J3 (CO₂) | BAT54S dual | 0.3V | Clamp negativo + positivo |
| J5 (NTC) | BAT54S dual | 0.3V | Clamp negativo |
| J6 (Hum) | BAT54S dual | 0.3V | Clamp negativo + positivo |

### 3.3 Protección Salida Actuadores

Los MOSFETs de potencia (IRLZ44N) incluyen diodos body intrínsecos que protegen contra polaridad inversa en la carga del motor.

Los relays K1 y K2 tienen diodos flyback (1N4148W) que absorben la energía inductiva al abrir, evitando picos de tensión inversa.

---

## 4. CAPA 3 — Protección ESD y Supresión de Transitorios

### 4.1 Normativa de Referencia

| Ensayo | Norma | Nivel | Voltaje |
|--------|-------|-------|---------|
| ESD contacto | IEC 61000-4-2 | Level 4 | ±8 kV |
| ESD aire | IEC 61000-4-2 | Level 4 | ±15 kV |
| EFT (burst) | IEC 61000-4-4 | Level 3 | ±2 kV |
| Surge | IEC 61000-4-5 | Level 2 | ±1 kV |

### 4.2 Dispositivos TVS por Puerto

| Puerto | Dispositivo TVS | V_clamp | C_junction | Norma cubierta |
|--------|----------------|---------|------------|----------------|
| Entrada 12V | SMAJ15A | 24.4V @ 1A | — | IEC 61000-4-5 Level 2 |
| Canales ADC (A0–A3) | PESD5V0S1BSF | 9.8V @ 1A | 0.4 pF | IEC 61000-4-2 Level 4 |
| Canal ADC (A4–A5) | PESD3V3S1BSF | 7.5V @ 1A | 0.4 pF | IEC 61000-4-2 Level 4 |
| I2C SDA/SCL | PESD3V3S2USF | 7.5V dual | 0.4 pF | IEC 61000-4-2 Level 4 |
| GPIO digitales | PESD5V0S1BSF | 9.8V | 0.3 pF | IEC 61000-4-2 Level 4 |
| HMI UART TX/RX | PESD3V3S2USF | 7.5V dual | 0.4 pF | IEC 61000-4-2 Level 4 |

### 4.3 Diseño de PCB para ESD

```
    Reglas de ruteo para protección ESD:
    
    1. TVS lo más cerca posible del conector (< 5 mm)
    2. Pista del conector al TVS: directa, sin vías
    3. Vía de tierra del TVS al plano GND: múltiples vías (≥ 2)
    4. Guard ring de GND alrededor de todos los conectores
    5. Sin pistas de señal bajo los conectores
```

---

## 5. CAPA 4 — Limitación de Corriente

### 5.1 Fusible Principal (Entrada 12V)

| Parámetro | Valor | Componente |
|-----------|-------|------------|
| Tipo | PTC recuperable (Polyfuse) | MF-MSMF110/24X-2 |
| I_hold | 1.1 A | Corriente continua sin disparo |
| I_trip | 2.2 A | Corriente de disparo |
| V_max | 24V | Voltaje máximo operativo |
| Tiempo de respuesta | < 5 s @ 2× I_hold | Respuesta rápida |
| Encapsulado | 1812 SMD | Compatible reflow |

**Escenario de fallo:** Si un usuario cortocircuita la salida 12V, el PTC se calienta y aumenta su resistencia de mΩ a kΩ en < 5 segundos, cortando la corriente. Al eliminar el cortocircuito, el PTC se enfría y el sistema se recupera automáticamente. **No necesita reemplazo.**

### 5.2 Limitación por Canal de Actuador

| Canal | Componente | Límite | Protección |
|-------|-----------|--------|------------|
| Motor bomba | Shunt 0.1Ω + comparador | 2A max | Shutdown driver IR2104 |
| Chiller relay | PTC 1A (0805) | 1A max | Auto-reset |
| CO₂ solenoide | PTC 0.5A (0805) | 0.5A max | Auto-reset |
| CO₂ regulador PWM | R_sense en MOSFET | 1A max | Firmware cutoff |

### 5.3 Protección de Entradas Analógicas

Cada entrada analógica incluye una resistencia serie de 1 kΩ que limita la corriente en caso de sobretensión a:

```
    I_max = (V_max - V_clamp_TVS) / R_serie
    I_max = (30V - 5V) / 1kΩ = 25 mA

    El TVS absorbe el exceso. El ADC del STM32 nunca ve más de V_clamp.
    Los diodos de protección internos del STM32 pueden manejar hasta 5 mA,
    pero nunca se activan porque el TVS externo clampea primero.
```

---

## 6. CAPA 5 — Protección Térmica

### 6.1 Monitoreo de Temperatura de la PCB

| Componente | Sensor | Ubicación | Umbral |
|-----------|--------|-----------|--------|
| NTC integrado | 10 kΩ NTC (en PCB) | Cerca del regulador buck | Shutdown @ 85°C |
| Thermal pad | Pad de cobre expuesto | Bajo U1 (TPS54302) | Disipación: 0.5W |

### 6.2 Protección Térmica del Regulador Buck

El TPS54302 incluye protección térmica interna:

| Parámetro | Valor |
|-----------|-------|
| Thermal shutdown | 165°C (junction) |
| Thermal hysteresis | 15°C |
| θ_JA (SOT-23-6 con plano GND) | 60°C/W |
| Potencia disipada máx. | (12V-5V) × 0.5A × (1-η) ≈ 0.35W @ η=90% |
| T_junction estimada | T_amb + 0.35W × 60°C/W = T_amb + 21°C |
| T_junction a 55°C ambiente | 76°C (muy debajo de 165°C shutdown) |

### 6.3 Protección Térmica de Actuadores

| Componente | Protección | Método |
|-----------|-----------|--------|
| MOSFETs IRLZ44N | θ_JA = 62°C/W, P_max = 1.6W @ 55°C | Pad de cobre 10×10 mm |
| Relays | Rated 5A, uso a < 1A | Derating > 80% |
| Optoacopladores | I_LED < 10 mA (rated 50 mA) | Derating > 80% |

### 6.4 Diseño Térmico PCB

```
    Reglas de layout térmico:

    1. Vías térmicas bajo reguladores (array 3×3, 0.3 mm)
    2. Plano de cobre expuesto (thermal pad) en cara inferior bajo U1
    3. Componentes de potencia (MOSFETs, relays) en borde de PCB
       para convección natural
    4. Espacio mínimo 5 mm entre componentes térmicos
    5. No colocar sensores analógicos cerca de fuentes de calor
```

---

## 7. CAPA 6 — Aislamiento Galvánico

### 7.1 Aislamiento Sensores Electroquímicos

| Barrera | Componente | Voltaje | Función |
|---------|-----------|---------|---------|
| pH ↔ MCU | Atlas ISCCB-2 (externo) | 1 kV DC | Elimina ground loops |
| ORP ↔ MCU | Atlas ISCCB-2 (externo) | 1 kV DC | Elimina ground loops |
| DO ↔ MCU | Atlas ISCCB-2 (externo) | 1 kV DC | Elimina ground loops |
| I2C aislado (on-board) | ISO7721DR | 2.5 kV RMS | Backup si no hay Atlas |

### 7.2 Aislamiento Actuadores ↔ MCU

| Barrera | Componente | Voltaje | Función |
|---------|-----------|---------|---------|
| GPIO ↔ Motor driver | PC817X2NIP | 5 kV pk | Protege MCU de EMI motor |
| GPIO ↔ Relay chiller | PC817X1NIP | 5 kV pk | Aislamiento inductivo |
| GPIO ↔ Relay CO₂ | PC817X1NIP | 5 kV pk | Aislamiento inductivo |

### 7.3 Separación de Planos de Tierra

```
    ┌──────────────────────────────────────────────────────┐
    │                  PLANO GND (Capa 2)                  │
    │                                                      │
    │  ┌────────────┐        ┌────────────┐               │
    │  │ AGND       │        │ DGND       │               │
    │  │ (analógico)│        │ (digital)  │               │
    │  │            │        │            │               │
    │  │ Sensores   │  SLOT  │ I2C, GPIO  │  SLOT         │
    │  │ ADC        │◄─────►│ UART       │◄─────►        │
    │  │ Op-amps    │ bridge │            │ bridge        │
    │  └────────────┘  0Ω   └────────────┘  0Ω           │
    │                   │                    │             │
    │                   └──── STAR GND ──────┘             │
    │                         (punto único)                │
    │                                                      │
    │                        ┌────────────┐               │
    │                        │ PGND       │               │
    │                        │ (potencia) │               │
    │                        │            │               │
    │                        │ MOSFETs    │               │
    │                SLOT    │ Relays     │               │
    │               ◄─────►│ 12V rail   │               │
    │                bridge │            │               │
    │                 0Ω    └────────────┘               │
    │                  │                                   │
    │                  └──── STAR GND ─────────────────    │
    │                         (punto único)                │
    └──────────────────────────────────────────────────────┘
```

**Star grounding:** Los tres planos (AGND, DGND, PGND) se conectan en un único punto cercano al conector de entrada de alimentación. Esto evita que corrientes de retorno de los actuadores contaminen las señales analógicas.

---

## 8. CAPA 7 — Monitoreo y Failsafe por Firmware

### 8.1 Watchdog de Hardware

| Parámetro | Valor |
|-----------|-------|
| Tipo | Hardware IWDG (STM32U585) |
| Timeout | 8 segundos |
| Feed interval | 4 segundos |
| Acción al expirar | Hard reset MCU |
| Detección post-reset | Flag `RCC_CSR.IWDGRSTF` — reporta vía IPC |

### 8.2 Monitoreo de Voltajes por ADC

El firmware lee periódicamente los voltajes de los rails de potencia:

| Rail | Canal ADC | Divisor | Umbral bajo | Umbral alto | Acción |
|------|-----------|---------|-------------|-------------|--------|
| 12V | ADC interno | 10k/3.3k | < 10.5V | > 14V | Alerta MQTT + LED rojo |
| 5V | ADC interno | 10k/10k | < 4.5V | > 5.5V | Alerta MQTT |
| 3.3V | VREFINT | — | < 3.0V | > 3.6V | Error crítico |

### 8.3 Failsafe de Actuadores

| Actuador | Condición de fallo | Acción automática |
|----------|-------------------|-------------------|
| CO₂ solenoide | Presión > 180 kPa | **CIERRE INMEDIATO** (latching fault) |
| CO₂ solenoide | Pérdida de comunicación IPC > 10s | Cierre (normalmente cerrado — fail-safe) |
| CO₂ solenoide | Watchdog reset | Cierre (GPIO baja al reset) |
| Chiller relay | Ciclo on < 60s | Bloqueo (protección compresor) |
| Chiller relay | Ciclo off < 120s | Bloqueo (protección compresor) |
| Bomba motor | Corriente > 2A | Shutdown driver (hardware) |
| Bomba motor | Pérdida de comunicación | Motor detenido (PWM = 0 al reset) |
| Todos | Temperatura PCB > 85°C | Shutdown todos los actuadores |

### 8.4 Store-and-Forward (Resiliencia de Datos)

| Nivel | Capacidad | Trigger | Acción |
|-------|-----------|---------|--------|
| MCU buffer | 64 entradas | IPC NACK o timeout | Almacena en circular buffer SRAM |
| MPU SQLite | 10,000 entradas | immudb inaccesible | WAL mode, replay cada 30s |

> **Garantía:** No se pierde ningún dato de sensor, incluso con cortes de energía, reinicios del sistema o fallos de comunicación.

---

## 9. Matriz de Escenarios de Error

### 9.1 Errores de Usuario

| # | Escenario | Capa | Protección | Resultado |
|---|-----------|------|-----------|-----------|
| 1 | Conecta fuente 12V al revés | 2 | Schottky SS34 bloquea | Sin daño, sin función |
| 2 | Conecta fuente 24V en vez de 12V | 3+4 | TVS SMAJ15A clampea + PTC dispara | PTC se recupera solo |
| 3 | Cortocircuita terminal de sensor | 4 | R serie 1kΩ + TVS | Sin daño al ADC |
| 4 | Toca conector con descarga estática | 3 | TVS < 0.4 pF | Sin daño, sin error de lectura |
| 5 | Conecta sensor en puerto incorrecto | 1 | Conectores keyed JST | Físicamente imposible |
| 6 | Alimenta 12V sin sensor conectado | 4 | Pull-down 10MΩ en cada canal | Lee 0V (sin flotante) |
| 7 | Desconecta HMI en caliente | 3 | ESD protection UART (PESD3V3S2USF) | Sin daño |
| 8 | Sumerge cable sensor en agua | 6 | Aislamiento galvánico | Sin ground loop |
| 9 | Cortocircuita motor bomba | 4 | PTC + driver overcurrent | Auto-shutdown, auto-reset |
| 10 | Olvida desconectar CO₂ | 7 | Presión max 180 kPa → cierre automático | Seguro (latching) |

### 9.2 Fallos Ambientales

| # | Escenario | Capa | Protección | Resultado |
|---|-----------|------|-----------|-----------|
| 11 | Rayo cercano (surge en línea 12V) | 3 | SMAJ15A + PTC | TVS absorbe, PTC protege |
| 12 | Corte de energía durante escritura | 7 | Store-forward + WAL SQLite | Datos recuperados al reiniciar |
| 13 | Temperatura ambiente > 55°C | 5 | Derating + thermal shutdown | Regulador se apaga, reinicia al enfriar |
| 14 | Condensación por lluvia | 1 | Conformal coating + IP54 enclosure | Funcionalidad mantenida |
| 15 | Vibración por maquinaria | 1 | Montaje M3 + terminal blocks con tornillo | Conexiones seguras |

### 9.3 Fallos de Componente

| # | Escenario | Capa | Protección | Resultado |
|---|-----------|------|-----------|-----------|
| 16 | Sensor pH falla (circuito abierto) | 7 | Pull-down 10MΩ → lectura 0V detectada | Alerta MQTT, dato marcado FAULT |
| 17 | Op-amp falla | 7 | Lectura fuera de rango detectada por firmware | Alerta, sensor deshabilitado |
| 18 | MOSFET falla en corto | 4 | PTC en línea de motor | Motor limitado, PTC dispara |
| 19 | Relay falla pegado | 7 | Watchdog → todos los GPIO a LOW | Chiller/CO₂ limitados por protección |
| 20 | Regulador 5V falla | — | Regulador tiene OVP/UVP internos | MCU se reinicia, datos en flash |

---

## 10. Resumen de Componentes de Protección

| Ref | Componente | Cantidad | Función |
|-----|-----------|----------|---------|
| D1 | SMAJ15A (TVS) | 1 | Protección surge entrada 12V |
| D2 | SS34 (Schottky) | 1 | Polaridad inversa entrada |
| D3–D6 | PESD5V0S1BSF / PESD3V3S1BSF | 6 | ESD por canal analógico |
| D7–D8 | PESD3V3S2USF | 1 | ESD bus I2C (dual) |
| D9–D13 | SS34 | 5 | Flyback actuadores |
| D_HMI | PESD3V3S2USF | 1 | ESD HMI UART dual-line |
| F1 | MF-MSMF110 (PTC) | 1 | Fusible recuperable principal |
| F2–F4 | PTC 0805 | 3 | Fusibles por actuador |
| U8–U11 | PC817 | 4 | Optoacoplamiento actuadores |
| U4 | ISO7721DR | 1 | Aislamiento I2C galvánico |
| R_pull-down | 10 MΩ × 6 | 6 | Anti-flotante canales ADC |
| R_serie | 1 kΩ × 6 | 6 | Limitación corriente canales ADC |
| BAT54S | Dual Schottky clamp × 3 | 3 | Clamp polaridad conectores |

**Total componentes de protección:** ~40 piezas dedicadas exclusivamente a protección.

---

## 11. Certificaciones de Protección Aplicables

| Ensayo | Norma | Nivel Requerido | Nivel Alcanzado |
|--------|-------|----------------|-----------------|
| ESD contacto | IEC 61000-4-2 | Level 3 (±6 kV) | **Level 4 (±8 kV)** |
| ESD aire | IEC 61000-4-2 | Level 3 (±8 kV) | **Level 4 (±15 kV)** |
| EFT/Burst | IEC 61000-4-4 | Level 2 (±1 kV) | **Level 3 (±2 kV)** |
| Surge | IEC 61000-4-5 | Level 1 (±0.5 kV) | **Level 2 (±1 kV)** |
| Polaridad inversa | — | No destructivo | **No destructivo, auto-recovery** |
| Sobrecorriente | — | Auto-recovery | **PTC auto-reset** |
| Térmica | — | Shutdown seguro | **Auto-shutdown, auto-recovery** |

---

*Documento NQS-FP-002 Rev 1.0 — Nebula Ecosystem® — 100% Foolproof by Design*
