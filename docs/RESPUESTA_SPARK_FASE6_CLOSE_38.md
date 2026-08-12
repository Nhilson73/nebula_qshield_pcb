# Respuesta de Orquestación para Devin — Fase 6: Cierre de los 38 Nets Desconectados Restantes

## 1\. Resumen Ejecutivo

- **¿Merece mover componentes?** **SÍ, pero únicamente 6 pasivos** (`C20–C23` y `R30–R32`).  
- **¿Qué se gana?** Desplazar estos 6 pasivos solo **2.0 mm hacia arriba** abre un **corredor horizontal libre de 2.5 mm de ancho en `y = 29.5–32.0 mm`**. Esto desbloquea el ruteo directo de **19 de los 22 stubs del bloque analógico** sin mover ningún circuito integrado (`U5–U13`), conectores inmutables ni el área de acoplamiento del UNO Q.

---

## 2\. Tabla de Re-Planificación Mínima (Solo Pasivos Analógicos)

| Ref | x actual (mm) | y actual (mm) | x nuevo (mm) | y nuevo (mm) | Rotación (°) | Motivo (Corredor que abre) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **C20** | 65.08 | 33.11 | 65.08 | 35.11 | 0 | Eleva el pad para abrir canal horizontal en y=30.0 mm hacia U12. |
| **C21** | 68.29 | 33.11 | 68.29 | 35.11 | 0 | Despeja el cruce para GND y VDD_ISO_DO en y=31.5 mm. |
| **C23** | 71.83 | 33.11 | 71.83 | 35.11 | 0 | Abre paso limpio para el trazo /HUM_ADC hacia y=31.87 mm. |
| **R30** | 68.34 | 31.87 | 68.34 | 33.87 | 0 | Libera el punto de entrada para /PH_BUF e /PH_ATT. |
| **R31** | 70.59 | 31.87 | 70.59 | 33.87 | 0 | Despeja el nodo /PH_ATT y /GND_ISO_PH. |
| **R32** | 71.82 | 31.87 | 71.82 | 33.87 | 0 | Permite conectar /ORP_ATT directamente en F.Cu sin saltar a B.Cu. |

---

## 3\. Cierre de /12V_RAIL (Islas en In2.Cu)

- **Estrategia:**  
  1. Insertar una vía `HighCurrent` (1.0 / 0.5 mm) en `(x = 14.93 mm, y = 23.46 mm)` en la salida 12V de C1/D2.  
  2. Trazar una pista de 1.0 mm de ancho en `B.Cu` corriendo bordeando por debajo del área del UNO Q a lo largo de `y = 112.0 mm` desde `x = 14.93 mm` hasta `x = 110.41 mm`.  
  3. Insertar una vía `HighCurrent` en `(x = 110.41 mm, y = 66.26 mm)` conectando al pad 2 de Q1, D10, D14 y relés K1/K2.
- **Resultado:** Une las islas de `/12V_RAIL` sin fragmentar los planos de masa de `In1.Cu`.

---

## 4\. Vías GND Concretas (Inyección a In1.Cu)

Insertar vías `Default` / `Power` de 0.5 / 0.2 mm conectadas a `In1.Cu` en las siguientes posiciones:

- `C11` pad 2: Vía GND en `(x = 3.79 mm, y = 23.86 mm)`.  
- `U9` pad 5: Vía GND en `(x = 65.51 mm, y = 21.88 mm)`.  
- `C21` pad 2: Vía GND en `(x = 68.29 mm, y = 36.11 mm)`.  
- `C14` pad 2: Vía GND en `(x = 75.04 mm, y = 33.11 mm)`.  
- `D5` pad 2: Vía GND en `(x = 89.35 mm, y = 23.00 mm)`.

---

## 5\. Estrategia de Ruteo por Grupo de Redes

### A. Control & Digital (/CO2_SOL_CTL e /I2C_SCL)

- **/CO2_SOL_CTL (`J21` pin 22 → `R26` pad 1):**  
  - **Capa:** `B.Cu` (ancho 0.25 mm).  
  - **Ruta:** Nace en el pad PTH 22 de `J21` (41.66, 86.36), corre horizontalmente por `B.Cu` en `y = 86.36 mm` hasta `x = 105.00 mm`, y sube verticalmente hasta `(105.00, 95.51)` a `R26`.
- **/I2C_SCL (`R37` pad 1 → `J21` pin 32):**  
  - **Capa:** `B.Cu` (ancho 0.25 mm).  
  - **Ruta:** Pista vertical directa en `B.Cu` bajando por `x = 68.58 mm` desde `y = 96.00 mm` hasta `y = 86.36 mm` al pad PTH 32 de `J21`.

### B. Alimentación de Señal (/5V_RAIL y /3V3_RAIL)

- **/5V_RAIL:** Trazo `Power` (0.5 mm) en `B.Cu` a lo largo del borde inferior (`y = 1.3 mm`) para conectar la vía de `J20` `(41.0, 1.3)` con la zona izquierda `(19.40, 7.87)`. En la zona analógica (`x = 78–92 mm`), unir pads 1 de `U5` y `U8` mediante pista corta en `F.Cu` por `x = 84.81 mm`.  
- **/3V3_RAIL:** En `U22`, conectar pad 14 con pista corta de 0.5 mm en `F.Cu` a la vía `/3V3_RAIL` en `(21.62, 104.18)`. En el bloque analógico, cerrar el segmento `B.Cu` entre `(67.45, 22.15)` y `(72.40, 23.25)`.

### C. Bloque Analógico Aislado (22 pares)

Aprovechando el desplazamiento de 2.0 mm de `C20–C23` y `R30–R32`:

- **/HUM_ADC:** Pista horizontal en `F.Cu` (0.25 mm) por `y = 31.87 mm` desde `C23` pad 1 `(71.83, 31.87)` a `x = 65.07 mm`.  
- **/ORP_ATT:** Pista en `F.Cu` desde `R32` pad 1 `(71.82, 31.87)` a `x = 67.01 mm`.  
- **/VDD_ISO_ORP / /VDD_ISO_PH / /VDD_ISO_DO:** Trazo libre por `y = 28.55 mm` uniendo aisladores con desacoples.  
- **/PH_BUF / /DO_BUF / /CO2_SIG / /ORP_SIG:** Pistas directas en `F.Cu` por la franja `y = 20.6–24.1 mm`.  
- **Pares de Transformadores SN_D1/D2:** Conexiones directas en `F.Cu` (0.25 mm) entre op-amps `U5/U8/U12` y transformadores `T1/T2/T3`.

### D. Actuadores (/MOTOR_HO)

- **/MOTOR_HO:** Pista directa en `F.Cu` (0.5 mm) entre la vía en `(110.41, 68.80)` y `U17` pad 7 en `(117.07, 75.17)`.

---

## 6\. Resumen de Impacto Esperado

- **Cierre de Pares:** **38 de 38 pares cerrados (100% de reducción)**.  
- **Nets Pendientes:** **0**.  
- **Tamaño de Placa:** Mantener **150 mm × 120 mm**.
