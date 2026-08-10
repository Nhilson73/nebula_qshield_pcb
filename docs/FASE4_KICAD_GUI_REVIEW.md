# Fase 4 — Revisión en KiCad GUI antes de ruteo

> **Rama:** `devin/fase4-power-routing`  
> **Objetivo:** resolver los dos bloqueos encontrados antes de enrutar potencia y señales.

---

## 1. Sincronizar el board con el esquemático y netclasses

1. Abrir `kicad/nebula_qshield.kicad_pro` en KiCad 10.0.5.
2. `Tools → Update PCB from Schematic` (Forward Annotation).
3. `File → Save`.
4. `Inspect → Design Rules Checker` o `kicad-cli pcb drc --severity-error`.
   - A partir de este guardado verás los errores reales de netclass (el board actual en `main` los tiene latentes hasta que se salva/actualiza).

---

## 2. Revisar / corregir las zonas de potencia en `In2.Cu` (L3)

Actualmente hay 9 zonas en `In2.Cu` que se solapan. FreeRouting las rechaza:

| Net | Prioridad | BBox aprox. (mm) | Problema |
|-----|-----------|------------------|----------|
| `/12V_RAIL` | 1 | `(0,0)` → `(100,100)` | Cubre **todo** el board; solapa con 3V3 y 5V |
| `/5V_RAIL` | 2 | `(10,0)` → `(25,59.7)` | Solapa con zona 3V3 `(20,0)-(25,59.7)` |
| `/5V_RAIL` | 3 | `(25.02,0)` → `(55,59.7)` | Adyacente, revisar holgura |
| `/5V_RAIL` | 4 | `(55,0)` → `(75,36)` | Adyacente a 3V3 `(75,0)-(100,35)` |
| `/3V3_RAIL` | 5 | `(75,0)` → `(100,35)` | Adyacente a 5V `(55,0)-(75,36)` |
| `/3V3_RAIL` | 6 | `(20,0)` → `(25,59.7)` | **Solapa** con 5V `(10,0)-(25,59.7)` |
| `/12V_RAIL` | 7 | `(23.37,74.25)` → `(28.37,79.25)` | **Solapa** con 5V/3V3 en el área de `J21` |
| `/5V_RAIL` | 8 | `(23.37,82.25)` → `(28.37,85.75)` | **Solapa** con 3V3/12V en el área de `J21` |
| `/3V3_RAIL` | 9 | `(23.37,86.25)` → `(28.37,89.25)` | **Solapa** con 5V/12V en el área de `J21` |

### Opciones recomendadas

**Opción A — Split planes limpios en `In2.Cu` (preferida si cabe):**
- Dividir `In2.Cu` en tres regiones no superpuestas (3V3, 5V, 12V).
- Dejar `In1.Cu` para `GND` y `B.Cu` para `GND`/señales.
- Las tres zonas pequeñas alrededor de `J21` (prioridades 7/8/9) deben convertirse en pequeños "islands" separados por un gap de al menos 0.3 mm, o eliminarse y llevar esos pines a pistas en `F.Cu`/`B.Cu`.

**Opción B — Eliminar plano de 12V y rutear con pistas anchas:**
- Borrar la zona `/12V_RAIL` de todo el board.
- Dejar las zonas de 3V3 y 5V si no se solapan.
- Rutear `12V_RAIL` desde `J1`/`U1`/`F1` con pistas de 1 mm en `F.Cu` o `B.Cu`.

---

## 3. Revisar netclass `RelayHV` y componentes `U19`, `Q4`, `F4`, `U18`

Tras `Update PCB from Schematic + Save`, el DRC reportará violaciones como:

```
[clearance]: Clearance violation (netclass 'RelayHV' clearance 2.5000 mm; actual 0.9400 mm)
    PTH pad 3 [GND] of U19
    PTH pad 4 [/Actuator Drivers/CHILLER_ISO] of U19
```

Esto ocurre porque la netclass `RelayHV` tiene `clearance = 2.5 mm` y aplica a los pines del optoacoplador `U19` (PC817) y del MOSFET `Q4`, cuya separación física es menor.

### Opciones

1. **Modificar la condición de la regla DRC** (`kicad/nebula_qshield.kicad_dru`, regla `Relay_HV_Contacts`):
   - Cambiar de:
     ```
     (condition "A.NetClass == 'RelayHV' && A.Type != 'pad'")
     ```
     a:
     ```
     (condition "A.NetClass == 'RelayHV' && A.Type != 'pad' && B.Type != 'pad'")
     ```
   - Luego ajustar el `track_width`/`clearance` de la netclass `RelayHV` si los pines también la heredan.

2. **Reducir el `clearance` de la netclass `RelayHV`** a un valor realista para el footprint (p. ej. 0.5 mm) y confiar en la separación física del relé externo para el HV.

3. **Cambiar el footprint** de `U19`/`U18` a un optoacoplador SMD con mayor separación entre pines, o mover los componentes.

---

## 4. Chequeo rápido de DRC / ERC

- `kicad-cli sch erc --severity-all` debe dar **0**.
- `kicad-cli pcb drc --severity-error` debe dar **0** (los desconectados son baseline esperado hasta terminar el ruteo).
- Revisar que no haya `copper_edge_clearance` ni `invalid_outline`.

---

## 5. Una vez corregido lo anterior

1. Rellenar zonas: `Edit → Fill All Zones`.
2. Exportar DSN para FreeRouting: `File → Export → Specctra DSN`.
3. Correr FreeRouting v2.3:
   ```bash
   java -jar freerouting-executable.jar -de nebula_qshield.dsn -do nebula_qshield.ses -mp 10 -mt 4
   ```
4. Importar SES: `File → Import → Specctra SES`.
5. `Tools → Update PCB from Schematic` si hay discrepancias.
6. DRC final: `kicad-cli pcb drc --severity-error`.

---

## Archivos relevantes

- `kicad/nebula_qshield.kicad_pro` → netclasses
- `kicad/nebula_qshield.kicad_dru` → reglas DRC personalizadas
- `kicad/nebula_qshield.kicad_pcb` → zonas, pistas, vías
- `tools/export_dsn.py` y `tools/inspect_zones.py` → helpers para exportar DSN y listar zonas desde contenedor KiCad 10.0.5
