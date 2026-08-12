# Prompt para Gemini Spark — Fase 6: cerrar nets desconectadas del Q-Shield

## Contexto del proyecto
- **Repo:** `Nhilson73/nebula_qshield_pcb`
- **PCB:** Nebula Q-Shield, 4 capas, factor de forma Arduino UNO Q.
- **Dimensiones actuales:** 150 mm × 120 mm.
- **Stackup:** F.Cu señal, In1.Cu GND (también usada como señal en autoruteo), In2.Cu split power (12V/5V/3V3), B.Cu señal/GND.
- **Herramientas:** KiCad 10.0.5 en Docker, FreeRouting v1.9.0, scripts Python con `pcbnew`.
- **Estado actual (DRC/ERC):** 0 violaciones de error, 72 nets desconectadas (aproximadamente).
- **Reglas activas:**
  - `Signal_Default`: vía 0.5/0.2 mm, track 0.2 mm, clearance 0.2 mm.
  - `Power_Rails`: vía 0.5/0.2 mm, track 0.5 mm, clearance 0.25 mm.
  - `High_Current_12V`: vía 0.5/0.2 mm, track 0.5 mm, clearance 0.3 mm.
  - `Analog_Signals`: clearance 0.3 mm a cualquier otro net.
  - `Board_Edge`: 0.25 mm.

## Restricciones inmutables (NO modificar)
- `J21` (header UNO Q) en `(5.08, 35.56)`, patrón de 4 agujeros M3 del UNO Q intacto.
- `I2C_SDA`/`I2C_SCL` en pines 31/32 de J21.
- Pull-ups físicos de 4.7 kΩ (R36/R37) y `I2C_SDA`/`I2C_SCL` en J21.
- `A4`/`A5` reservados para `CO2_ADC`/`DO_ADC`.
- Zonas de recorte interno para USB-C, botón, JCTL, SPI2 y Qwiic.
- Stackup de 4 capas.
- No cambiar el netlist ni el pinout.

## Objetivo de este prompt
Proponer un **plan de vías y pistas cortas** para cerrar las nets desconectadas, priorizando:

1. Rieles de potencia: `/12V_RAIL`, `/5V_RAIL`, `/3V3_RAIL`.
2. Islas de GND.
3. Señales analógicas y del bus I2C/SPI/RS485 que queden sueltas.

## Archivos adjuntos (incluirlos en la conversación)
- `nebula_qshield-drc.rpt`: reporte DRC de KiCad que lista todas las parejas de items desconectados.
- `kicad/nebula_qshield.kicad_pcb`: archivo del PCB (opcional, pesado; puedes usar solo el reporte).

## Formato de respuesta esperado
Para cada pareja desconectada que propongas cerrar, entrega un bloque con:

```
Net: <nombre>
Item A: <tipo> <ref> <pad> (<x>, <y>) <capa>
Item B: <tipo> <ref> <pad> (<x>, <y>) <capa>
Estrategia: [via_en_pad_A + track_B | via_en_A + via_en_B + track_en_B.Cu | track_F.Cu recto | track_F.Cu en L | ...]
Pasos propuestos (coordenadas en mm, ancho en mm, capa):
1. Via en (<x>, <y>) capa par F-B, diámetro 0.5 mm, drill 0.2 mm.
2. Track de (<x1>,<y1>) a (<x2>,<y2>) en <capa>, ancho <w>.
...
Justificación: <por qué este camino no viola clearance 0.3 mm con pads de señales/analógicas ni el edge/cutout>
```

Si crees que un par requiere **re-ubicar un componente**, indica el ref, posición actual y nueva posición, y justifica por qué mejora la ruteabilidad sin romper las restricciones inmutables.

## Reglas de clearance a verificar
- **Vías 0.5 mm (radio 0.25 mm)** + margen netclass mínimo 0.25 mm ⇒ centro de vía debe estar a ≥ 0.5 mm de cualquier cobre de otro net.
- **Tracks 0.5 mm** (ancho) ⇒ edge del track a ≥ 0.25 mm de otro net (0.3 mm si el otro net es analógico).
- **Edge.Cuts y cutouts internos** ⇒ mantener ≥ 0.25 mm.
- **RelayHV** ⇒ mínimo 0.5 mm en la regla actual (aunque el conocimiento del usuario pide 2.5 mm; este conflicto aún está pendiente; proponer separación conservadora ≥ 1.0 mm si cruzas nets de relé).

## Criterios de prioridad
1. Cierra primero los pares más cortos (< 5 mm) y los que sean dentro de un mismo componente.
2. Usa la capa In2.Cu de split power para rieles de potencia conectando vías en pads; si el plano está cortado, propón un puente corto en B.Cu o F.Cu.
3. Para GND, coloca vías 0.5/0.2 en pads GND SMD y en tracks GND que parezcan islas.
4. Evita cruzar pistas de señal por encima de pads de señal vecinos; rodea por el lado libre.
5. Si la densidad impide cerrar un par, proponé re-ubicar un componente no crítico en vez de forzar una pista.

## Entrega final
Devolvé una lista priorizada de acciones (máximo 30 propuestas principales) numeradas, con coordenadas exactas y justificación de clearance. No generes código Python; Devin aplicará las propuestas manualmente con `pcbnew` y validará DRC/ERC.
