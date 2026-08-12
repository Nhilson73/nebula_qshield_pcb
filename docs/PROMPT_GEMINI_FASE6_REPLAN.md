# Prompt para Gemini Spark — Fase 6: Re-planificación del placement analógico

## Contexto

Repositorio: `Nhilson73/nebula_qshield_pcb` (KiCad 10, PCB 4 capas).
Estado actual del PCB:

- `kicad-cli pcb drc --severity-error --refill-zones`: **0 violaciones**
- `kicad-cli sch erc --severity-all`: **0 violaciones**
- `kicad-cli pcb drc`: **40 items desconectados** (20 pares aprox).

El board mide **150 mm × 120 mm**. El factor de forma UNO Q (`J21`) y los conectores de borde (`J2/J3/J5/J15-J19`) deben considerarse inmutables.

## Problema con la propuesta de routing anterior

Se recibió una tabla de 37 rutas propuestas (ver `docs/RESPUESTA_SPARK_FASE6_ROUTING.md`) para cerrar los 40 nets desconectados. Al validarlas con un script Python contra obstáculos reales (pads, vías, pistas y zonas rellenas) se encontró que **muchas rutas chocan con componentes o pistas existentes** en el bloque analógico denso. El movimiento sugerido de `C20-C23` y `R30-R32` 1.5 mm hacia arriba **también colisiona** con `C14/C15/C19`.

Ejemplos concretos de bloqueo:

- `/HUM_ADC` (C23 pad1 → pista en F.Cu): cualquier trayectoria en F.Cu horizontal pasa por `R30/R31/R32` o por pistas GND/3V3 cercanas.
- `/ORP_ATT` (R32 → pista B.Cu): la vía propuesta en `(71.82, 35.14)` queda a menos de 0.35 mm de pistas `/3V3_RAIL`.
- `/12V_RAIL` islas en `In2.Cu`: los pares entre islas necesitan un puente en B.Cu o F.Cu que no atraviese zonas GND ni pads de borde.
- Muchos pares analógicos (`SN_D1_PH`, `SN_D2_PH`, `SN_D1_ORP`, `SN_D2_ORP`, `DO_SIG`, `PH_BUF`, etc.) están en F.Cu ↔ B.Cu y no hay espacio para vías de 0.5/0.2 mm sin violar clearance con pads o GND.

## Petición

Proponé un **re-acomodo mínimo del bloque analógico** que abra corredores de ruteo para cerrar los 40 nets. En lugar de dar coordenadas de pistas, dame:

1. **Nuevas posiciones (x, y, rotación)** solo para los componentes que haya que mover, priorizando:
   - Pasivos del bloque analógico: `C20, C21, C22, C23, C14, C15, C19, R30, R31, R32, R12, R13, R14, R15, R18`.
   - Si es necesario, `D19-D24` y los transformadores `T1, T2, T3`.
   - Como último recurso, re-ubicar ligeramente `U5-U13` (op-amps/aisladores) si eso desbloquea corredores.
2. **Corredores de ruteo** que se abren con esos movimientos: ejes Y o X libres de 0.6 mm de ancho para pistas de 0.25 mm + clearance 0.35 mm.
3. **Estrategia para `/12V_RAIL`**: indicar si el puente entre islas debe ir por F.Cu, B.Cu o ambos, y dónde ubicar las dos vías de 1.0/0.5 mm.
4. **Estrategia para GND**: vías de 0.5/0.2 mm cerca de `C11`, `U9`, `C21`, `C14`, `D5` que no entren en zonas `/3V3_RAIL` o pads vecinos.

## Restricciones

- No mover `J21`, conectores de borde, agujeros de montaje, relés `K1/K2`, drivers `U17/U20`.
- Mantener el board en 150 mm × 120 mm (a menos que justifiques que 160 mm × 130 mm es estrictamente necesario y no rompe el case futuro).
- Cualquier IC movido debe seguir conectado a sus resistencias/capacitores asociados sin pistas de más de 25 mm para señales analógicas.
- Los nets `RelayHV` (`/CHILLER_ISO`, `/CO2_SOL_OUT`, etc.) requieren 1.0 mm de track y 0.6 mm de clearance; no pasar por corredores analógicos.

## Archivos de soporte

- `docs/layout_fase6.png` — layout actual F.Cu + In1.Cu + In2.Cu + B.Cu.
- `docs/layout_bcu.png` — layout de B.Cu + Edge.Cuts (útil para ver espacio en B.Cu).
- `tools/unconnected_report.md` — tabla de los 40 pares desconectados con refs, capas y coordenadas.
- `docs/RESPUESTA_SPARK_FASE6_ROUTING.md` — tabla de rutas previas que resultaron en colisiones (para referencia, no aplicar tal cual).

Entregá la respuesta como una tabla markdown con: `Ref | x actual | y actual | x nuevo | y nuevo | rotación | nota`, seguida de la estrategia de ruteo por red.
