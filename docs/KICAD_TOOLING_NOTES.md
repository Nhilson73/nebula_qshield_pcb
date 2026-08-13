# Notas técnicas de tooling KiCad — cosas que cuestan horas si no las sabés

Esto es la destilación de lo aprendido armando `tools/route_fase6.py` y
`tools/replan_analog_block.py` (Fase 6). No es historia de qué se hizo —
para eso está `docs/CLAUDE_FASE6_REPORT.md` — es una referencia técnica para
la próxima vez que alguien (agente o humano) escriba o corra un script
`pcbnew`/`kicad-cli` sobre este repo.

## 1. `kicad-cli` necesita el `.kicad_pro` Y el `.kicad_dru` con el mismo basename

Si copiás `kicad/nebula_qshield.kicad_pcb` a otro nombre (por ejemplo para
probar un script sin tocar el archivo real) y corrés `kicad-cli pcb drc`
sobre esa copia, KiCad busca automáticamente `<basename>.kicad_pro` y
`<basename>.kicad_dru` **al lado**, con el mismo nombre base. Si no los
encuentra, corre con reglas de KiCad genéricas en vez de las reglas custom
del proyecto — y reporta violaciones que no existen en el board real.

Esto costó una sesión entera de confusión: una prueba temprana reportó
**217 violaciones** (vías de 0.5mm marcadas como ilegales, etc.) que
resultaron ser 100% falsos positivos por este motivo. Al copiar también
`.kicad_pro` y `.kicad_dru` con el mismo basename, bajó a las violaciones
reales (varias decenas, después 0).

**Regla:** cualquier script/test que copie el `.kicad_pcb` a otro lado tiene
que copiar también `.kicad_pro` y `.kicad_dru` con el mismo basename.

## 2. El ancho de netclass tiene DOS valores distintos — no confundirlos

- `kicad/nebula_qshield.kicad_pro` → `net_settings.classes[].track_width` es
  el ancho **preferido/default** — lo que el editor dibuja cuando arrancás
  un track nuevo a mano. No es un piso.
- `kicad/nebula_qshield.kicad_dru` tiene reglas custom (`Power_Rails`,
  `High_Current_12V`, `Analog_Signals`, `I2C_Bus`, `Relay_HV_Contacts`,
  `Signal_Default`) que definen el **mínimo real que el DRC exige**, y no
  coincide con el "preferido" de arriba:

  | Netclass | Ancho preferido (`.kicad_pro`) | Mínimo real (`.kicad_dru`) |
  |---|---|---|
  | Default | 0.25 mm | 0.20 mm |
  | Analog | 0.25 mm | 0.25 mm |
  | I2C | 0.25 mm | 0.25 mm |
  | Power | 0.50 mm | **0.50 mm** |
  | HighCurrent | 1.50 mm | **0.50 mm** |
  | RelayHV | 1.00 mm | 1.00 mm |

  (Vía y clearance: `.kicad_dru` también fija `via_diameter` mínimo 0.5mm
  para Signal_Default/Power/HighCurrent vs. los 0.6mm que sugiere
  `.kicad_pro` — el board admite vías más chicas de lo que el `.kicad_pro`
  hace parecer, PERO el piso real varía por netclass, no es un número único.)

  Un net puede matchear **varias** netclasses a la vez (ej. `/12V_RAIL` →
  `Power,HighCurrent,Default`); el valor efectivo es el `max()` de todas las
  que aplican, para cada parámetro por separado. Podés confirmar la
  combinación real de un net cargado en `pcbnew` con
  `net.GetNetClassName()` (devuelve el string separado por comas).

  **Si escribís un router que hace "neck-down" (ancho reducido) para
  entrar en un pad encajonado**, el piso legal para probar NO es un número
  de board genérico — es `max()` de los mínimos custom de las netclasses
  que matchea esa net especial. Route_fase6.py tiene esto en
  `MIN_WIDTH_BY_CLASS` / `min_track_width()`; ignorarlo generó 66
  violaciones `track_width` en una iteración temprana (tracks de 0.2mm en
  nets Power que exigían 0.5mm mínimo).

## 3. `PCB_VIA.GetWidth()` sin capa cuelga el proceso (no tira excepción)

```python
via.GetWidth()          # MAL: dispara un assert nativo -> dialogo modal
                         #      bloqueante en builds de Windows, el proceso
                         #      se queda colgado sin mensaje de error claro
via.GetWidth(pcbnew.F_Cu)  # BIEN: pedile el ancho en una capa especifica
```

El mensaje que sí llega a stderr antes de colgarse:
`PCB_VIA::GetWidth called without a layer argument`. Si un script Python
con `pcbnew` se cuelga sin avanzar y sin excepción visible, sospechá de
esto primero.

## 4. `kicad-cli pcb drc` puede reportar un par `Zone`↔`Zone` fantasma

En islas de plano dividido (`/12V_RAIL`, `/5V_RAIL`, `/3V3_RAIL` en
`In2.Cu`), a veces (no siempre — parece ligado al orden/threading del
relleno de zonas en esa corrida puntual) `kicad-cli` reporta un par
`[unconnected_items]` con dos entradas `Zone` en la **misma coordenada**,
que además cae justo en la esquina del board (ej. `(-8.00, -2.00)`). No es
un punto de conexión real — es un artefacto del detector de islas.
`route_fase6.py` lo filtra explícitamente (`parse_pairs` + chequeo de
`type == 'Zone'` en `main()`) en vez de intentar "rutear" ese par.

## 5. `footprint.GetBoundingBox()` NO es el courtyard real

Para `J21` (header UNO Q), `GetBoundingBox()` devuelve
`(3.785, 29.63) – (74.955, 94.83)` — un rectángulo enorme que probablemente
incluye gráficos de fab-layer u otra cosa ajena al courtyard real. El
courtyard real (capa `F.Courtyard`, que es lo que efectivamente exige
0.25mm de clearance contra otros footprints) es:

```
J21:  (3.785, 34.265) – (74.955, 90.195)
```

sensiblemente más chico y con otro origen en Y. Para calcular zonas de
exclusión reales (por ejemplo antes de reubicar componentes), consultá
`fp.GraphicalItems()` filtrando por `'Courtyard' in board.GetLayerName(item.GetLayer())`
y tomá el bounding box de esos ítems específicos — nunca el del footprint
completo.

### Mapa de courtyards relevantes (post Fase 6, board 170×120mm)

Útil para cualquier reubicación futura cerca del bloque analógico o del
header UNO Q:

| Ref | Courtyard (x0,y0)–(x1,y1) mm | Qué es |
|---|---|---|
| J21 | (3.785, 34.265)–(74.955, 90.195) | Área de acoplamiento UNO Q — inmutable |
| J2 | (92.375, -0.025)–(104.425, 12.025) | Terminal de campo |
| J3 | (92.375, 12.525)–(104.425, 24.575) | Terminal de campo |
| J5 | (92.375, 25.125)–(104.425, 37.175) | Terminal de campo |
| J15 | (95.375, 38.175)–(116.425, 48.225) | Terminal de campo |
| J16 | (95.375, 48.725)–(116.425, 58.775) | Terminal de campo |
| J17 | (95.375, 59.275)–(106.425, 69.325) | Terminal de campo |
| D10 | (86.475, 68.225)–(93.525, 71.775) | Diodo, sector actuadores |

La columna J2/J3/J5/J15–J19 arranca su courtyard en **x≈92.4–95.4**, no en
x=98.4 (que es solo la posición nominal del pad) — cualquier layout que
asuma "hay espacio hasta 98.4" se va a chocar con esto.

## 6. Margen de tolerancia en clearance: siempre positivo, nunca permisivo

Si escribís tu propio chequeo de clearance (no usando el DRC de KiCad
directamente) vas a redondear coordenadas a enteros de nanómetro
(`int(round(x * 1e6))`). Eso introduce error de sub-micrón. Un chequeo con
tolerancia permisiva tipo:

```python
if distancia - requerido < -0.001:   # MAL: permite pasar hasta 1 micron corto
```

deja pasar casos que en la práctica violan el DRC real por una fracción de
micrón — pasó en una iteración temprana (11 violaciones `clearance` con
"actual" a 0.0006–0.001mm del límite). La forma correcta es un margen de
seguridad **positivo** por encima del requerido:

```python
if distancia - requerido < 0.01:     # BIEN: exige 0.01mm de margen real
```

## 7. Herramientas reutilizables de este repo

- **`tools/route_fase6.py`** — router Dijkstra sobre grilla local (F.Cu/B.Cu
  + vía) con verificación geométrica exacta antes de comprometer nada al
  board. Lee `kicad-cli pcb drc` (`unconnected_items`) y cierra pares uno
  por uno. Reutilizable tal cual para cualquier ronda futura de cierre de
  desconectados — correrlo varias veces seguidas sobre el mismo board sigue
  sumando cierres (cada pasada cambia la congestión para la siguiente).
  Acepta un path de board opcional como primer argumento posicional
  (default: `kicad/nebula_qshield.kicad_pcb`).
- **`tools/replan_analog_block.py`** — extiende el board y reempaqueta el
  bloque analógico en un corredor en L. Los rectángulos `REGION_1`/`REGION_2`
  están calibrados al milímetro contra los courtyards de la tabla de arriba;
  si el layout cambia, hay que recalibrarlos (varias iteraciones dieron
  falsos `courtyards_overlap` hasta que calzaron).

## 8. Validación de referencia

```bash
kicad-cli pcb drc --severity-error --refill-zones \
  -o kicad/nebula_qshield-drc.rpt kicad/nebula_qshield.kicad_pcb

kicad-cli sch erc --severity-all \
  -o kicad/nebula_qshield-erc.rpt kicad/nebula_qshield.kicad_sch
```

En Windows local, `kicad-cli.exe` vive en
`C:\Program Files\KiCad\10.0\bin\kicad-cli.exe` y el intérprete de Python
con `pcbnew` importable en
`C:\Program Files\KiCad\10.0\bin\python.exe` (trae `numpy` — no `scipy`).
No hace falta Docker para correr estos scripts localmente; la imagen
`kicad/kicad:10.0.5` es equivalente para CI/Devin.
