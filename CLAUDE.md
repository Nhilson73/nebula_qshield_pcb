# Nebula Q-Shield — guía para agentes (Claude Code, Devin, etc.)

Este repo es el diseño de PCB de un shield UNO Q (KiCad 10) para control de
un sistema de acuario/cultivo (sensores analógicos, actuadores, RS485,
HX711). **El dueño del repo no programa** — todo el trabajo de diseño se
hace a través de agentes de IA (Claude Code, Devin, Gemini Spark) siguiendo
prompts guardados en `docs/PROMPT_*.md`. Ver `docs/CLAUDE_CODE_VS_CODE_SETUP_NO_CODE.md`
para el flujo que sigue el dueño.

## Archivos clave

- `kicad/nebula_qshield.kicad_pcb` — el layout. **170 × 120 mm** desde
  Fase 6 (era 150×120mm antes).
- `kicad/nebula_qshield.kicad_pro` — netclasses (ancho/vía/clearance
  *preferidos*) y otros ajustes de proyecto.
- `kicad/nebula_qshield.kicad_dru` — reglas de diseño custom. **Estas son
  las que el DRC realmente exige**, no las de `.kicad_pro` — ver nota 2 de
  `docs/KICAD_TOOLING_NOTES.md`.
- `kicad/nebula_qshield.kicad_sch` + los `.kicad_sch` de cada sheet
  (`analog_acquisition`, `power_management`, `actuator_drivers`,
  `hmi_connectors`, `digital_i2c`) — esquemático.
- `tools/` — scripts Python (`pcbnew`) de layout/ruteo. Muchos son
  descartables de iteraciones pasadas; los reutilizables de verdad son
  `tools/route_fase6.py` (cierre de desconectados) y
  `tools/replan_analog_block.py` (resize + reposicionar bloque analógico).
- `docs/CLAUDE_FASE6_REPORT.md` — qué se hizo en la Fase 6 y qué quedó
  pendiente, con causa raíz de cada desconectado restante.
- **`docs/KICAD_TOOLING_NOTES.md` — leé esto antes de escribir o correr
  cualquier script `pcbnew`/`kicad-cli` sobre este repo.** Documenta ~6
  gotchas que cuestan horas si no los sabés de antemano (abajo un resumen).

## Antes de tocar el board

- **Confirmá con el dueño antes de modificar `kicad/nebula_qshield.kicad_pcb`**
  (mover componentes, ripear tracks, cambiar tamaño de board) — no es
  programador, no puede revisar un diff de KiCad a ojo, así que la
  confirmación tiene que ser sobre el plan en palabras, no sobre el diff.
- Trabajá con una copia (`cp` a otro nombre) para probar scripts antes de
  aplicar al archivo real — pero copiá **también** el `.kicad_pro` y el
  `.kicad_dru` con el mismo basename (nota 1 de `docs/KICAD_TOOLING_NOTES.md`)
  o el DRC de la copia va a mentir.

## Validación (siempre correr después de tocar el board)

```bash
kicad-cli pcb drc --severity-error --refill-zones \
  -o kicad/nebula_qshield-drc.rpt kicad/nebula_qshield.kicad_pcb

kicad-cli sch erc --severity-all \
  -o kicad/nebula_qshield-erc.rpt kicad/nebula_qshield.kicad_sch
```

Objetivo: `Found 0 violations` en ambos, `unconnected_items` en 0 en el PCB.
En Windows local, `kicad-cli.exe` y el `python.exe` con `pcbnew` viven bajo
`C:\Program Files\KiCad\10.0\bin\` — no hace falta Docker para probar acá,
aunque la imagen `kicad/kicad:10.0.5` es la referencia para CI/Devin.

## Los 6 gotchas más caros (detalle completo en `docs/KICAD_TOOLING_NOTES.md`)

1. `kicad-cli` necesita `.kicad_pro`/`.kicad_dru` con el mismo basename que
   el `.kicad_pcb` al lado, si no aplica reglas genéricas y miente.
2. El ancho "preferido" de netclass (`.kicad_pro`) ≠ el mínimo real que
   exige el DRC (`.kicad_dru`) — no asumas que son el mismo número.
3. `via.GetWidth()` sin argumento de capa cuelga el proceso (assert nativo
   modal en Windows) — siempre `via.GetWidth(pcbnew.F_Cu)`.
4. `kicad-cli pcb drc` a veces reporta un par `Zone`↔`Zone` fantasma en
   islas de plano dividido — no es un punto de conexión real, filtralo.
5. `footprint.GetBoundingBox()` no es el courtyard real (puede ser mucho
   más grande) — para keepouts reales, filtrá `GraphicalItems()` por capa
   `F.Courtyard`.
6. Si escribís tu propio chequeo de clearance, usá tolerancia **positiva**
   (ej. `< 0.01`) nunca permisiva (`< -0.001`) — el redondeo a nanómetros
   de `pcbnew` puede colar violaciones de una fracción de micrón.
