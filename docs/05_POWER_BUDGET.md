# Nebula Q-Shield® — Análisis de Presupuesto de Potencia

> **Documento:** NQS-PWR-005 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Ingeniería — Análisis Térmico y de Potencia

---

## 1. Arquitectura de Distribución de Energía

```
    ┌───────────────┐
    │ FUENTE 12V DC │
    │ 5A (60W max)  │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐     ┌──────────────────────────────────────┐
    │  TVS + PTC    │     │          12V RAIL (directo)          │
    │  + Schottky   │────►│                                      │
    │  (Foolproof)  │     │  ┌─────────┐  ┌─────────┐  ┌──────┐│
    └───────────────┘     │  │ Motor   │  │ CO₂     │  │Chiller│
                          │  │ Bomba   │  │Solenoide│  │Peltier│
                          │  │ 500 mA  │  │ 200 mA  │  │ 3.5A │
                          │  └─────────┘  └─────────┘  └──────┘│
                          └──────────────────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  TPS54302 Buck     │
                          │  12V → 5V / 3A     │
                          │  η ≈ 90%           │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼──────────────────────────────┐
                          │          5V RAIL                        │
                          │                                        │
                          │  ┌──────────┐  ┌──────────┐  ┌──────┐│
                          │  │ Arduino  │  │ HX711    │  │ GPS  ││
                          │  │ UNO Q    │  │ ADC      │  │SAM-M8│
                          │  │ (MCU+MPU)│  │ 1.5 mA   │  │50 mA ││
                          │  │ 1500 mA  │  └──────────┘  └──────┘│
                          │  └──────────┘  ┌──────────┐  ┌──────┐│
                          │                │ Display  │  │ Relay ││
                          │                │ Waveshare│  │ Coils ││
                          │                │ 400 mA   │  │120 mA ││
                          │                └──────────┘  └──────┘│
                          └────────────────────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  AMS1117-3.3 LDO   │
                          │  5V → 3.3V / 800mA │
                          │  η ≈ 66%           │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼──────────────────────────────┐
                          │          3.3V RAIL                      │
                          │                                        │
                          │  ┌──────────┐  ┌──────────┐  ┌──────┐│
                          │  │ Op-amps  │  │ I2C      │  │ ESD  ││
                          │  │ MCP6002  │  │ pull-ups │  │ TVS  ││
                          │  │ 1 mA     │  │ 0.7 mA   │  │< 1μA ││
                          │  └──────────┘  └──────────┘  └──────┘│
                          │  ┌──────────┐  ┌──────────┐          │
                          │  │ RTC      │  │ Isolator │          │
                          │  │ DS3231   │  │ ISO7721  │          │
                          │  │ 0.2 mA   │  │ 5 mA     │          │
                          │  └──────────┘  └──────────┘          │
                          └────────────────────────────────────────┘
```

---

## 2. Consumo Detallado por Componente

### 2.1 Rail de 12V (Directo — sin regulación)

| Componente | Estado activo | Estado standby | Pico | Notas |
|-----------|--------------|----------------|------|-------|
| Motor bomba peristáltica | 500 mA | 0 mA | 800 mA (arranque) | Duty cycle ~50% típico |
| Solenoide CO₂ (NC) | 200 mA | 0 mA | 250 mA (inrush) | Solo cuando inyecta CO₂ |
| Chiller Peltier TEC1-12706 | 3,500 mA | 0 mA | 5,000 mA (arranque frío) | Controlado por relay |
| Bobinas relay K1, K2 | 80 mA × 2 | 0 mA | 120 mA × 2 (inrush) | 12V coil, ~150Ω |
| CO₂ regulador PWM (válvula) | 100 mA | 0 mA | 200 mA | Duty cycle variable |
| **Subtotal 12V** | **4,460 mA** | **0 mA** | **6,490 mA** | |

> **Sin Chiller (Essential/Insight):** 880 mA activo, 1,490 mA pico.

### 2.2 Rail de 5V (Regulado por TPS54302)

| Componente | Estado activo | Estado standby | Notas |
|-----------|--------------|----------------|-------|
| Arduino UNO Q (MCU + MPU) | 1,500 mA | 800 mA | Docker + MQTT + display driver |
| HMI Nextion/Stone 5" UART | 400 mA | 200 mA | Backlight + procesador integrado (alimentado vía J_HMI 5V) |
| GPS SAM-M8Q | 50 mA | 25 mA | Acquisition vs tracking |
| HX711 ADC | 1.5 mA | 0.001 mA | Power down < 1 μA |
| Relays coil driver (vía Q3/Q4) | 5 mA | 0 mA | Gate drive only |
| Optoacopladores LED side | 40 mA | 0 mA | 4× PC817 @ 10 mA |
| LEDs indicadores | 15 mA | 5 mA | 3 LEDs |
| **Subtotal 5V** | **2,012 mA** | **1,030 mA** | |

### 2.3 Rail de 3.3V (Regulado por AMS1117-3.3)

| Componente | Estado activo | Estado standby | Notas |
|-----------|--------------|----------------|-------|
| Op-amps MCP6002 × 2 | 1.0 mA | 1.0 mA | Quiescent 100 μA/amp |
| I2C pull-ups (4.7 kΩ × 2) | 0.7 mA | 0.7 mA | 3.3V / 4.7kΩ cada uno |
| ISO7721 digital isolator | 5.0 mA | 3.0 mA | Per-channel 2.5 mA |
| RTC DS3231 | 0.2 mA | 0.003 mA | Battery backup < 3 μA |
| Sensores analógicos (bias) | 2.0 mA | 0.5 mA | Corriente de bias circuitos |
| Cell density sensor (I2C) | 5.0 mA | 1.0 mA | Típico sensor turbidez |
| TVS ESD (leakage) | < 0.01 mA | < 0.01 mA | Negligible |
| Divisores resistivos | 0.33 mA | 0.33 mA | 10k/10k y similares |
| **Subtotal 3.3V** | **14.2 mA** | **6.5 mA** | |

---

## 3. Presupuesto de Potencia Total

### 3.1 Escenario: Signature Tier — Máxima Carga

| Rail | Corriente activa | Potencia | Corriente pico | Potencia pico |
|------|-----------------|----------|----------------|---------------|
| 12V directo | 4,460 mA | 53.5 W | 6,490 mA | 77.9 W |
| 5V (del buck) | 2,012 mA | 10.1 W | 2,500 mA | 12.5 W |
| 3.3V (del LDO) | 14.2 mA | 0.047 W | 20 mA | 0.066 W |
| **TOTAL desde fuente 12V** | — | **~65 W** | — | **~92 W** |

### 3.2 Escenario: Insight Tier — Sin Chiller

| Rail | Corriente activa | Potencia |
|------|-----------------|----------|
| 12V directo | 960 mA | 11.5 W |
| 5V (del buck) | 2,012 mA | 10.1 W |
| 3.3V (del LDO) | 12 mA | 0.040 W |
| **TOTAL desde fuente 12V** | — | **~23 W** |

### 3.3 Escenario: Essential Tier — Mínimo

| Rail | Corriente activa | Potencia |
|------|-----------------|----------|
| 12V directo | 0 mA | 0 W |
| 5V (del buck) | 1,970 mA | 9.85 W |
| 3.3V (del LDO) | 8 mA | 0.026 W |
| **TOTAL desde fuente 12V** | — | **~11 W** |

---

## 4. Análisis del Regulador Buck (TPS54302)

### 4.1 Condiciones de Operación

| Parámetro | Valor |
|-----------|-------|
| V_in | 12V (rango: 10.5–14V con derating) |
| V_out | 5.0V |
| I_out max | 2.5 A (con margen del 25% sobre 2.0 A nominal) |
| f_sw | 500 kHz (internal) |
| η (eficiencia estimada) | 89–92% @ 2A load |

### 4.2 Cálculos Térmicos

```
    P_in = V_out × I_out / η = 5.0 × 2.0 / 0.90 = 11.1 W
    P_loss = P_in - P_out = 11.1 - 10.0 = 1.1 W
    
    θ_JA (SOT-23-6 con plano GND) ≈ 60°C/W
    
    T_junction = T_ambient + P_loss × θ_JA
    T_junction = 55°C + 1.1W × 60°C/W = 55 + 66 = 121°C
    
    ⚠ 121°C está por debajo del thermal shutdown (165°C) pero
    por encima del margen recomendado (125°C max).
    
    SOLUCIÓN: Aumentar el plano de cobre bajo el IC y agregar
    vías térmicas (array 3×3, 0.3mm) al plano GND interno.
    
    Con vías térmicas: θ_JA ≈ 40°C/W
    T_junction = 55 + 1.1 × 40 = 99°C ✓ (margen de 66°C)
```

### 4.3 Selección del Inductor

```
    L = (V_in - V_out) × V_out / (V_in × f_sw × ΔI_L)
    
    ΔI_L = 30% × I_out = 0.30 × 2.0 = 0.6 A (ripple target)
    
    L = (12 - 5) × 5 / (12 × 500000 × 0.6)
    L = 35 / 3,600,000 = 9.7 μH
    
    Seleccionado: 4.7 μH (valor estándar inferior)
    → ΔI_L real = 35 / (12 × 500k × 4.7μ) = 1.24 A (62% ripple)
    
    ⚠ Ripple alto pero aceptable con capacitores de salida grandes.
    I_peak = I_out + ΔI_L/2 = 2.0 + 0.62 = 2.62 A
    
    Inductor seleccionado: 4.7 μH, I_sat = 4A → margen 53% ✓
```

---

## 5. Análisis del LDO (AMS1117-3.3)

### 5.1 Condiciones de Operación

| Parámetro | Valor |
|-----------|-------|
| V_in | 5.0V |
| V_out | 3.3V |
| V_dropout | 1.0V @ 800 mA (max) |
| I_out | 14.2 mA (típico), 20 mA (pico) |
| Headroom | 5.0 - 3.3 = 1.7V >> 1.0V dropout ✓ |

### 5.2 Cálculos Térmicos

```
    P_loss = (V_in - V_out) × I_out = (5.0 - 3.3) × 0.0142 = 0.024 W
    
    θ_JA (SOT-223) ≈ 90°C/W
    
    T_junction = 55°C + 0.024W × 90°C/W = 55 + 2.2 = 57.2°C ✓
    
    Margen térmico: 150°C - 57.2°C = 92.8°C ✓ (excelente)
```

> El LDO opera muy por debajo de su capacidad térmica. No hay riesgo térmico.

---

## 6. Análisis de Fuente de Alimentación Externa

### 6.1 Requisitos por Tier

| Tier | Potencia continua | Potencia pico | Fuente recomendada |
|------|-------------------|---------------|-------------------|
| **Essential** | 11 W | 15 W | 12V 2A (24W) — suficiente |
| **Insight** | 23 W | 35 W | 12V 3A (36W) — recomendado |
| **Signature** | 65 W | 92 W | 12V 8A (96W) — obligatorio |

> **Nota sobre Chiller:** El Peltier TEC1-12706 consume hasta 5A @ 12V (60W). Para producción, se recomienda un chiller de recirculación con su propia alimentación separada, reduciendo la fuente del Q-Shield a 12V 3A.

### 6.2 Fuentes de Alimentación Recomendadas

| Tier | Modelo | Potencia | Precio | Certificaciones |
|------|--------|----------|--------|----------------|
| Essential/Insight | Mean Well GST36E12-P1J | 36W (12V/3A) | $18 | CE, UL, FCC, TÜV |
| Signature | Mean Well GST90A12-P1M | 90W (12V/7.5A) | $32 | CE, UL, FCC, TÜV |
| Producción (sin Peltier) | Mean Well GST36E12-P1J | 36W (12V/3A) | $18 | CE, UL, FCC, TÜV |

---

## 7. Protección de Potencia — Escenarios de Fallo

### 7.1 Cortocircuito en Rail 5V

```
    Escenario: Componente en 5V_RAIL cortocircuita a GND
    
    1. TPS54302 entra en current limit (3.5A, 1 ms)
    2. Si persiste > hiccup period → regulador se apaga
    3. Reinicia automáticamente con soft-start
    4. Si fallo permanente → cicla en hiccup mode (protege fuente)
    
    Resultado: Sin daño. Regulador se protege.
```

### 7.2 Sobretensión en Entrada 12V

```
    Escenario: Usuario conecta fuente 24V por error
    
    1. TVS SMAJ15A clampea a 24.4V (conduce pico de corriente)
    2. PTC F1 se calienta con la corriente extra
    3. Si corriente > 2.2A → PTC abre circuito en < 5s
    4. Sistema se apaga de forma segura
    5. Al desconectar 24V y reconectar 12V → PTC se enfría → sistema arranca
    
    Resultado: Sin daño. Auto-recuperación.
```

### 7.3 Pérdida de Alimentación (Power Fail)

```
    Escenario: Corte de energía abrupto
    
    1. C2 (470 μF) mantiene 12V_RAIL durante ~5 ms
    2. C5/C6 (94 μF total) mantiene 5V durante ~2 ms
    3. MCU watchdog no se alimenta → reset limpio
    4. Store-forward buffer en SRAM se pierde (64 entradas)
    5. MPU SQLite WAL mode → datos hasta último checkpoint preservados
    6. RTC DS3231 mantiene hora con batería CR1220
    
    Resultado: Pérdida de hasta 64 lecturas de sensor (< 1 minuto).
              Datos en immudb/SQLite preservados.
```

---

## 8. Eficiencia Energética y Recomendaciones

### 8.1 Eficiencia del Sistema

| Conversión | Eficiencia | Pérdida |
|-----------|-----------|---------|
| 12V → 5V (TPS54302) | 90% | 1.1W @ 2A load |
| 5V → 3.3V (AMS1117) | 66% | 0.024W @ 14 mA |
| 12V → Actuadores (directo) | ~100% | Resistiva (relays ~1W) |
| **Sistema global** | **~85%** | **~2.5W en regulación** |

### 8.2 Recomendaciones para Optimización

| # | Recomendación | Ahorro estimado | Complejidad |
|---|--------------|----------------|-------------|
| 1 | Reemplazar AMS1117 por buck 3.3V (TPS62203) | 0.01W (negligible a 14 mA) | Baja |
| 2 | Alimentar Chiller con fuente dedicada separada | Reduce fuente principal a 3A | Media |
| 3 | Sleep mode MCU entre lecturas de sensor | ~30% CPU power | Media (firmware) |
| 4 | Desactivar GPS después de fix inicial | 25 mA ahorro | Baja (firmware) |
| 5 | Modo sleep de pantalla después de 5 min inactividad | 200 mA ahorro | Baja (software) |

---

## 9. Tabla Resumen — Presupuesto de Potencia

```
    ┌────────────────────────────────────────────────────────────────────┐
    │                POWER BUDGET SUMMARY — Q-SHIELD v1.0               │
    ├────────────────────────────────────────────────────────────────────┤
    │                                                                    │
    │  FUENTE: 12V DC external                                          │
    │  ├── PTC F1: 1.1A hold / 2.2A trip                               │
    │  ├── TVS D1: SMAJ15A (clamp 24.4V)                               │
    │  │                                                                 │
    │  ├── 12V_RAIL (directo) ── 4,460 mA active / 6,490 mA peak      │
    │  │   ├── Motor bomba ──────── 500 mA (Insight+)                  │
    │  │   ├── Solenoide CO₂ ────── 200 mA (Insight+)                  │
    │  │   ├── Chiller Peltier ──── 3,500 mA (Signature)               │
    │  │   ├── Relay coils ──────── 160 mA                             │
    │  │   └── CO₂ regulador ────── 100 mA (Insight+)                  │
    │  │                                                                 │
    │  ├── TPS54302 Buck (η=90%) ── 5V / 2,012 mA / 10.1W             │
    │  │   ├── Arduino UNO Q ────── 1,500 mA                           │
    │  │   ├── Pantalla 5" ──────── 400 mA                             │
    │  │   ├── GPS SAM-M8Q ──────── 50 mA                              │
    │  │   ├── HX711 ───────────── 1.5 mA                              │
    │  │   ├── Optoacopladores ──── 40 mA                              │
    │  │   └── LEDs ─────────────── 15 mA                              │
    │  │                                                                 │
    │  └── AMS1117-3.3 LDO (η=66%) ── 3.3V / 14.2 mA / 0.047W        │
    │      ├── Op-amps MCP6002 ──── 1.0 mA                             │
    │      ├── ISO7721 isolator ─── 5.0 mA                             │
    │      ├── I2C pull-ups ──────── 0.7 mA                            │
    │      ├── Cell density ──────── 5.0 mA                             │
    │      ├── DS3231 RTC ────────── 0.2 mA                            │
    │      └── Bias/misc ────────── 2.3 mA                             │
    │                                                                    │
    ├────────────────────────────────────────────────────────────────────┤
    │  TOTAL:  Essential = 11W   Insight = 23W   Signature = 65W       │
    │  FUENTE: Essential = 2A    Insight = 3A    Signature = 8A        │
    └────────────────────────────────────────────────────────────────────┘
```

---

*Documento NQS-PWR-005 Rev 1.0 — Nebula Ecosystem® — Análisis de Potencia*
