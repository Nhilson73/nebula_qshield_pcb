# Contribuir al Nebula Q-Shield® PCB

## Flujo de trabajo

1. Crear branch desde `main`: `git checkout -b feature/descripcion`
2. Hacer cambios en KiCad o documentación
3. Ejecutar DRC/ERC en KiCad antes de commit
4. Commit con mensaje descriptivo: `feat: add thermal vias under TPS54302`
5. Push y crear Pull Request
6. Si el cambio toca pinout, esquemático, layout o BOM, actualizar `docs/INSIGHT_FABRICATION_ROADMAP.md` y revisar `docs/DOCUMENTATION_UPDATE_AUDIT.md` para mantener los demás `.md` sincronizados.

## Convenciones

### Commits

```
feat:     Nueva funcionalidad o componente
fix:      Corrección de error en diseño
docs:     Cambios en documentación
refactor: Reorganización sin cambio funcional
chore:    Mantenimiento (BOM updates, footprints)
```

### Esquemático KiCad

- Usar hojas jerárquicas (una por bloque funcional)
- Nomenclatura de nets: `BLOQUE_SEÑAL` (ej: `PH_RAW`, `I2C_SDA`, `12V_RAIL`)
- Cada componente debe tener campo `MPN` (Manufacturer Part Number)
- Cada componente debe tener campo `Distributor_PN` (Digi-Key o Mouser)

### Layout PCB

- Seguir las reglas de diseño en `docs/06_PCB_LAYOUT_STACKUP.md`
- No interrumpir el plano GND (Capa 2) bajo señales analógicas
- Capacitores de desacoplo < 3 mm del IC asociado
- Verificar DRC con 0 errores antes de commit

### BOM

- Actualizar `docs/04_BOM_PRODUCTION.md` cuando se cambien componentes
- Verificar disponibilidad en Digi-Key/Mouser antes de proponer alternativas
- Mantener compatibilidad con los 3 tiers (Essential/Insight/Signature)

## Revisión

Todo PR requiere revisión antes de merge. Los cambios en el esquemático o layout requieren:
- DRC/ERC con 0 errores
- BOM actualizado
- Documentación actualizada si afecta especificaciones
