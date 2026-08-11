# Auditoría de Documentación — Archivos Markdown a Actualizar

**Fecha:** 2026-07-09 (actualizado 2026-08-11)  
**Contexto:** Re-arquitectura UNO Q para fabricación JLCPCB del tier **Insight**. Estado actual: board 125 × 120 mm, DRC/ERC 0, 47 nets desconectadas en Fase 5.  
**Documento de verdad:** `docs/INSIGHT_FABRICATION_ROADMAP.md`  
**Nueva referencia de factor de forma:** `docs/UNO_Q_FORM_FACTOR.md`

Esta auditoría lista los archivos `.md` del repo que contienen información desactualizada respecto al diseño actual (`main`) y al plan aprobado, con indicaciones de qué cambiar. El documento `docs/UNO_Q_FORM_FACTOR.md` ya captura las restricciones mecánicas inmutables del UNO Q y debe citarse en cualquier documento que hable de dimensiones, headers o recortes.

> **Actualización reciente:** `docs/04_BOM_PRODUCTION.md` sección 11 se actualizó con la convención DNP y los conteos finales Essential/Insight/Signature (88/137/146 de 163 placements). Se corrigió `tools/list_actual_components.py` y `tools/apply_tier_dnp4.py` para procesar también el formato s-expresión expandido de `kicad/hmi_connectors.kicad_sch`; ahora J20, J21, R36, R37 y D15-D18 tienen DNP. Todos los esquemáticos tienen las propiedades `DNP` y comentarios sincronizados con los tiers.

---

## Archivos con cambios obligatorios o altamente recomendados

### Referencia de factor de forma (nuevo documento)
- `docs/UNO_Q_FORM_FACTOR.md` — creado. Contiene las dimensiones del UNO Q, posición de headers/mounting holes, keepouts/cutouts y la regla inmutable: el patrón UNO Q no puede cambiar aunque el tamaño del Q-Shield sí.

### 1. `README.md`
- [Resuelto] **Dimensiones:** actualizado a `125 × 120 mm`.
- [Resuelto] **Header J21:** actualizado a `(32-pin shield header)` en README y `docs/01_PCB_ARCHITECTURE.md`.
- [Resuelto] **Mapeo analógico en la tabla "12 Componentes":** actualizado a `A0=pH`, `A1=ORP`, `A2=temp`, `A3=hum`, `A4=CO₂`, `A5=DO`.
- [Resuelto] **Mapeo de actuadores:** actualizado a `D5=PUMP_PWM`, `D6=PUMP_DIR`, `D7=CO2_SOL`, `D9=CO2_PWM`, `D8=CHILLER` (Insight+), `D4=MCU_WDI`.
- **I2C:** diagrama dice `I2C bus (7 devices)` sin ubicación; ahora el bus principal está en **D20/D21** con pull-ups `R36/R37`.
- **Recomendación:** actualizar el diagrama ASCII, la tabla de 12 componentes, la tabla de especificaciones y agregar un enlace a `docs/INSIGHT_FABRICATION_ROADMAP.md`.

### 2. `CONTRIBUTING.md`
- **Flujo de trabajo:** no menciona la bitácora ni la auditoría de docs.
- **Recomendación:** añadir un paso: "revisar y actualizar `docs/INSIGHT_FABRICATION_ROADMAP.md`, `README.md` y los documentos afectados (`01`, `04`, `06`, `07`, `08`) cuando un cambio toque pinout, esquemático o layout".

### 3. `docs/01_PCB_ARCHITECTURE.md`
- [Resuelto] **Dimensiones:** `125 × 120 mm`.
- [Resuelto] **Canales analógicos A2–A5:** actualizado a `A2=TEMP_ADC`, `A3=HUM_ADC` (Signature), `A4=CO2_ADC`, `A5=DO_ADC`.
- **Bloque I2C:** figura `STM32U585 I2C1` en SDA/SCL sin ubicación de pines; actualizar a `I2C2` en `D20/D21` (pines 31/32 de J21), con pull-ups `R36/R37`.
- [Resuelto] **Tabla de pines J21 (4.3):** actualizado según `docs/INSIGHT_FABRICATION_ROADMAP.md`.
- [Resuelto] **Mapa de zonas (5):** `125 × 120 mm`; header actualizado a 32 pines.

### 4. `docs/04_BOM_PRODUCTION.md`
- **J21:** descripción "Pin header, 2×20 stackable, 40" → actualizar a header Arduino UNO R3/Q de **32 pines** (1×8/1×6/1×10/1×8).
- **Pull-ups I2C:** faltan `R36` y `R37` (4.7 kΩ, 0402) en la BOM.
- **Bloque RS485 bridge:** faltan `U22` (SC16IS740), `U23` (SN74LVC1G04), `Y1` (1.8432 MHz), `C31/C32` (22 pF), `C33` (100 nF) y `R38` (10 kΩ) en la BOM. Verificar MPN/distribuidor.
- **Aislamiento analógico:** los diodos de rectificación aislados se numeran `D19–D24` y conectan con `T1–T3`; revisar si los MPN/cantidades coinciden con el esquemático actual.
- **Tier actual:** el documento dice "Tier: Signature (fully populated)"; para la fabricación Insight se recomienda crear variante/variante BOM o una sección de DNP para componentes Signature.

### 5. `docs/06_PCB_LAYOUT_STACKUP.md`
- [Resuelto] **Dimensiones del board:** no se encontró referencia incorrecta en el archivo; verificar mapa ASCII/header.
- [Resuelto] **Header J21:** actualizado a `(32 pines, ~50.8mm)`.
- **Faltan keepouts/cutouts:** no documenta los recortes perimetrales para USB-C, botón de power, `JCTL`, `SPI2`/`Qwiic` aprobados en la re-arquitectura.
- [Resuelto] **Plano GND L2:** actualizado para indicar polígono `GND` en `In1.Cu` y `B.Cu` extendido al board 125 × 120 mm.
- [Resuelto] **Plano de potencia `In2.Cu`:** actualizado para indicar que el split-plane `/12V_RAIL`/`/5V_RAIL`/`/3V3_RAIL` funciona por prioridades y el polígono `/12V_RAIL` ya cubre el board 125 × 120 mm; pendiente aclarar islas `GND_ISO_*`.
- **Reglas de diseño vs. JLCPCB:** añadir validación de JLCPCB (4/4 mil, 0.2 mm drill, 0.2 mm track, etc.).

### 6. `docs/07_KICAD_NETLIST.md`
- **Versión EDA:** dice `KiCad 9.x`; el proyecto se migró a **KiCad 10.0.5**.
- **I2C nets:**
  - `I2C_SDA`/`I2C_SCL` apuntan a `J21:SDA`/`J21:SCL`; deben apuntar a `J21:31` (`D20/SDA`) y `J21:32` (`D21/SCL`).
- **Pull-ups:** menciona `R10/R11` (4.7 kΩ) en `I2C_SDA`/`SCL`; ahora los pull-ups del bus principal son `R36`/`R37`. `R10`/`R11` pueden ser del bus aislado o estar obsoletos — verificar esquemático.
- **ADC mapping (nota 2.2):** `A0=PH_ADC, A1=ORP_ADC, A2=TEMP_ADC, A3=HUM_ADC, A4=CO2_ADC, A5=DO_ADC` es correcto; pero el resto de tablas de pines del documento deben alinearse.
- **Tierra unificada:** dice "No existen nets `AGND`, `DGND` ni `PGND`". El PCB todavía tiene `AGND`/`PGND` separados en algunas zonas; actualizar según el resultado de la Fase 3.
- **Estructura de archivos:** no lista `hmi_connectors.kicad_sch` como sub-hoja jerárquica.
- **Generación de Gerber:** sección 7.1 refiere a `KiCad 9`; actualizar a comandos `kicad-cli` de KiCad 10 y salidas `production/`.

### 7. `docs/08_MECHANICAL_ANALYSIS.md`
- [Resuelto] **Dimensiones:** actualizado a `125 × 120 mm` y `15,000 mm²`.
- [Resuelto] **Header J21:** actualizado a 32 pines; el ancho entre columnas es ~50.8 mm según patrón UNO Q.
- **Cuello #2:** basado en ancho 98 mm; en 125×120 mm ya no es cuello de ancho.
- **Recortes y keepouts:** agregar sección con los slots Edge.Cuts y keepouts Eco1.User para USB-C, botón power, JCTL, SPI2/Qwiic.
- [Resuelto] **Veredicto compactación:** actualizado a "125×120 aprobado".
- [Resuelto] **Mapa de zonas propuesto:** ASCII actualizado a 125×120 y posición J21 `(5.08, 35.56)`.

### 8. `kicad/UNO_Q_rearchitecture_report.md`
- [Resuelto] **Estado y nota histórica:** se añadió nota de reporte histórico; el pinout definitivo y el estado actual están en `docs/INSIGHT_FABRICATION_ROADMAP.md`.

---

## Archivos que parecen correctos o no requieren cambio inmediato

- `docs/02_FOOLPROOF_DESIGN.md` — protecciones generales siguen válidas; solo revisar si cambian conectores o mapeo de pins de protección ESD.
- `docs/03_EU_COMPLIANCE.md` — normativas generales; sin impacto directo del pinout o dimensiones.
- `docs/05_POWER_BUDGET.md` — verificar si tier Insight cambia consumo (sin humedad/cell density) pero números generales siguen aplicables.
- `kicad/UNO_Q_shield_proposal.md` — propuesta pre-aprobada; referir a `docs/INSIGHT_FABRICATION_ROADMAP.md`.
- `kicad/UNO_Q_rearchitecture_plan.md` — plan previo; se recomienda mantenerlo como histórico y redirigir al roadmap.

---

## Propuesta de orden de actualización

1. `README.md` y `CONTRIBUTING.md` — actualizar con dimensiones, header 32 pines, mapeo Insight, y enlace al roadmap.
2. `docs/07_KICAD_NETLIST.md` — corregir I2C, versión KiCad, ADC mapping, estructura de archivos.
3. `docs/01_PCB_ARCHITECTURE.md` — dimensiones, mapeo analógico, I2C D20/D21, mapa de zonas.
4. `docs/04_BOM_PRODUCTION.md` — J21 32 pines, añadir R36/R37 y bloque RS485 bridge, variante Insight/Signature.
5. `docs/06_PCB_LAYOUT_STACKUP.md` y `docs/08_MECHANICAL_ANALYSIS.md` — dimensiones 125×120, header, keepouts, recortes.
6. `kicad/UNO_Q_rearchitecture_report.md` — nota de histórico y enlace al roadmap.
