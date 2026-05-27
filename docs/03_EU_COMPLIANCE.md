# Nebula Q-Shield® — Cumplimiento Normativo Europeo

> **Documento:** NQS-EU-003 · **Rev:** 1.0 · **Fecha:** Mayo 2026
>
> **Clasificación:** Regulatorio — Certificación CE y Normativas EU
>
> **Aplicabilidad:** Mercado europeo (EEA + UK UKCA)

---

## 1. Resumen de Directivas Aplicables

El Nebula Q-Shield® debe cumplir las siguientes directivas y regulaciones europeas para obtener el **marcado CE** y poder comercializarse en el Espacio Económico Europeo:

| # | Directiva/Regulación | Referencia | Aplicabilidad |
|---|---------------------|------------|---------------|
| 1 | **Directiva EMC** | 2014/30/EU | Emisiones e inmunidad electromagnética |
| 2 | **Directiva LVD** | 2014/35/EU | Seguridad eléctrica (baja tensión) |
| 3 | **Directiva RoHS 3** | 2011/65/EU + 2015/863 | Restricción de sustancias peligrosas |
| 4 | **Regulación WEEE** | 2012/19/EU | Gestión de residuos electrónicos |
| 5 | **Directiva RED** | 2014/53/EU | Equipos de radio (WiFi/BT del UNO Q) |
| 6 | **Regulación REACH** | (EC) No 1907/2006 | Registro químico de sustancias |
| 7 | **Directiva Maquinaria** | 2006/42/EC | Si se integra en maquinaria agrícola |
| 8 | **Marcado CE** | Regulation (EC) 765/2008 | Declaración de conformidad |

---

## 2. Directiva EMC — 2014/30/EU

### 2.1 Normas Armonizadas Aplicables

| Ensayo | Norma | Título | Límite |
|--------|-------|--------|--------|
| **Emisiones conducidas** | EN 55032:2015+A1:2020 | Equipos multimedia — Emisiones | Clase B (residencial) |
| **Emisiones radiadas** | EN 55032:2015+A1:2020 | Equipos multimedia — Emisiones | Clase B, 30 MHz–6 GHz |
| **Inmunidad ESD** | EN 61000-4-2:2009 | Descarga electrostática | Level 4: ±8 kV contacto, ±15 kV aire |
| **Inmunidad radiada** | EN 61000-4-3:2020 | Campo electromagnético RF | 10 V/m, 80 MHz–6 GHz |
| **Inmunidad EFT** | EN 61000-4-4:2012 | Transitorios rápidos (burst) | Level 3: ±2 kV |
| **Inmunidad surge** | EN 61000-4-5:2014+A1:2017 | Sobretensiones transitorias | Level 2: ±1 kV (línea), ±0.5 kV (tierra) |
| **Inmunidad conducida** | EN 61000-4-6:2014 | Perturbaciones conducidas RF | 10 V, 0.15–80 MHz |
| **Inmunidad dips** | EN 61000-4-11:2020 | Variaciones de tensión, dips | Criterio B |
| **Flicker + harmónicos** | EN 61000-3-2:2019, EN 61000-3-3:2013 | Solo si > 75W de red AC | No aplica (DC input) |

### 2.2 Medidas de Diseño para Cumplimiento EMC

#### 2.2.1 Emisiones Conducidas (EN 55032 Clase B)

```
    Fuente externa ──►[Filtro LC Pi]──►[Ferrite bead]──► Entrada Q-Shield

    Filtro Pi en conector de entrada 12V:
    ┌─── C1 (100μF) ───┬─── L1 (FB 600Ω@100MHz) ───┬─── C2 (470μF) ───┐
    │                   │                             │                   │
    GND                GND                           GND                GND
```

| Componente | Valor | Función |
|-----------|-------|---------|
| FB1 | BLM31PG601SN1L (Murata) | Ferrite bead 600Ω @ 100 MHz, 2A | Supresión ruido conducido HF |
| C_Y1 | 2.2 nF / 250V Y2 (Safety) | Capacitor Y entre líneas ↔ tierra | Modo común |
| C_X1 | 100 nF / 50V X2 (Safety) | Capacitor X entre líneas | Modo diferencial |

#### 2.2.2 Emisiones Radiadas (EN 55032 Clase B)

Medidas de PCB layout para minimizar emisiones radiadas:

| Medida | Implementación | Efecto |
|--------|---------------|--------|
| Plano GND continuo (Capa 2) | Sin splits bajo señales de alta frecuencia | Reduce loop area EMI |
| Decoupling caps < 3 mm de IC | 100 nF MLCC X7R por cada IC | Minimiza corrientes de retorno HF |
| PWM con slew-rate limitado | R_gate 10Ω en MOSFETs IRLZ44N | Reduce dV/dt en conmutación |
| Cables apantallados para sensores | Apantallamiento conectado a GND en un extremo | Reduce radiación de cables |
| Ferrite beads en líneas PWM | 120Ω @ 100 MHz (0805) | Filtro HF en salidas actuadores |

#### 2.2.3 Inmunidad ESD (IEC 61000-4-2 Level 4)

Detallado en documento `02_FOOLPROOF_DESIGN.md`, Capa 3. Resumen:

- TVS en **todos** los puertos expuestos al usuario
- Guard ring GND alrededor de conectores
- PCB stackup 4 capas con plano GND continuo

#### 2.2.4 Inmunidad Surge (IEC 61000-4-5 Level 2)

```
    Entrada 12V DC:
    
    Surge ±1 kV ──►[SMAJ15A TVS]──►[PTC 3A]──► Regulador Buck
                    Clamp 24.4V     I_trip 2.2A
                    P_pk 400W       
                    t_response < 1 ns
```

El SMAJ15A soporta picos de 400W durante 10/1000 μs, suficiente para absorber surge de ±1 kV en línea DC.

### 2.3 Plan de Ensayos EMC

| Fase | Ensayo | Laboratorio | Costo estimado | Duración |
|------|--------|-------------|---------------|----------|
| Pre-compliance | Scan emisiones + inmunidad básica | Interno (SDR + LISN casero) | ~$0 | 1 semana |
| Compliance | EN 55032 + EN 61000-4-x completo | TÜV / SGS / Bureau Veritas | €3,000–€8,000 | 2–4 semanas |
| Re-test | Solo ensayos fallidos | Mismo laboratorio | €500–€2,000 | 1 semana |

---

## 3. Directiva LVD — 2014/35/EU

### 3.1 Aplicabilidad

La Directiva LVD aplica a equipos eléctricos con tensión nominal entre **50–1000V AC** o **75–1500V DC**.

El Q-Shield® opera a **12V DC** (entrada) y **5V/3.3V DC** (internos), por lo tanto **no aplica directamente la LVD**. Sin embargo, si el sistema se alimenta de un adaptador AC/DC de red (230V AC), el **adaptador** debe cumplir LVD y el conjunto debe cumplir:

| Norma | Título | Aplicabilidad |
|-------|--------|---------------|
| EN 62368-1:2020+A11:2020 | Audio/video, IT, y equipos de comunicación — Seguridad | Requerido si se vende con adaptador AC |
| EN 61010-1:2010+A1:2019 | Equipos de medida, control y laboratorio — Seguridad | Alternativa para equipos de instrumentación |

### 3.2 Requisitos de Seguridad Eléctrica

| Requisito | Implementación en Q-Shield |
|-----------|---------------------------|
| **Doble aislamiento** | Enclosure plástico IP54 (Clase II) |
| **Protección contra contacto** | Todos los terminales de potencia protegidos por enclosure |
| **Separación de circuitos** | Aislamiento galvánico MCU ↔ actuadores (optoacopladores) |
| **Puesta a tierra** | No requerida (Clase II — doble aislamiento) |
| **Marcado** | Símbolo Clase II (□ dentro de □) en etiqueta |
| **Fusible accesible** | PTC no necesita acceso (auto-reset) |

### 3.3 Adaptador de Red AC/DC (Requisitos para el adaptador externo)

El adaptador AC/DC que se venda con el Q-Shield® debe cumplir:

| Requisito | Norma |
|-----------|-------|
| Seguridad | EN 62368-1 o EN 60950-1 |
| Eficiencia energética | (EU) 2019/1782 (ErP Lote 6) — Nivel VI mín. |
| Marcado CE | Sí |
| Medical (si aplica) | EN 60601-1 (solo para uso clínico) |

**Recomendación:** Usar adaptadores de marca reconocida (Mean Well, TDK-Lambda, CUI) que ya tengan certificación CE/UL/TÜV.

---

## 4. Directiva RoHS 3 — 2011/65/EU + Delegada 2015/863

### 4.1 Sustancias Restringidas

| Sustancia | Límite máximo (% peso en material homogéneo) | Estado Q-Shield |
|-----------|----------------------------------------------|-----------------|
| Plomo (Pb) | 0.1% (1000 ppm) | ✓ Conforme — soldadura SAC305 (Sn96.5/Ag3.0/Cu0.5) |
| Mercurio (Hg) | 0.1% (1000 ppm) | ✓ Conforme — sin mercurio |
| Cadmio (Cd) | 0.01% (100 ppm) | ✓ Conforme — sin cadmio |
| Cromo hexavalente (Cr VI) | 0.1% (1000 ppm) | ✓ Conforme — acabado ENIG (sin Cr VI) |
| PBB (polibromobifenilos) | 0.1% (1000 ppm) | ✓ Conforme — FR-4 sin PBB |
| PBDE (éteres polibromados) | 0.1% (1000 ppm) | ✓ Conforme — FR-4 sin PBDE |
| DEHP (ftalato) | 0.1% (1000 ppm) | ✓ Conforme — sin PVC flexible |
| BBP (ftalato) | 0.1% (1000 ppm) | ✓ Conforme |
| DBP (ftalato) | 0.1% (1000 ppm) | ✓ Conforme |
| DIBP (ftalato) | 0.1% (1000 ppm) | ✓ Conforme |

### 4.2 Documentación Requerida

| Documento | Responsable | Estado |
|-----------|------------|--------|
| Declaración de conformidad RoHS | Cafelium SRL | Por generar |
| Certificados RoHS de cada componente | Proveedores (Digi-Key/Mouser) | Disponibles en datasheets |
| Test report ICP-OES (si requerido) | Laboratorio acreditado | Opcional (para auditoría) |
| Ficha técnica de soldadura SAC305 | Proveedor de pasta | Incluir en dossier |

### 4.3 Proceso de Soldadura RoHS

| Parámetro | Valor |
|-----------|-------|
| Aleación | SAC305 (Sn96.5 Ag3.0 Cu0.5) |
| Temperatura de refusión pico | 245°C ± 5°C |
| Tiempo sobre liquidus (217°C) | 60–90 segundos |
| Perfil | Rampa 1–2°C/s, soak 150–200°C 60–120s |
| Flux | No-clean ROL0 (IPC J-STD-004B) |

---

## 5. Regulación WEEE — 2012/19/EU

### 5.1 Clasificación del Producto

| Parámetro | Valor |
|-----------|-------|
| Categoría WEEE | Categoría 6: Equipos informáticos y de telecomunicaciones |
| Subcategoría | Equipos de monitorización y control |
| Código Open Scope | EEE para uso profesional (B2B) |
| Productor | Cafelium SRL (como importador/distribuidor EU) |

### 5.2 Obligaciones del Productor

| Obligación | Acción requerida | Estado |
|-----------|-----------------|--------|
| **Registro** | Registrarse en el sistema WEEE de cada Estado Miembro donde se venda | Pendiente |
| **Marcado** | Símbolo WEEE (contenedor tachado) en producto y embalaje | Por implementar |
| **Financiación** | Pagar eco-tasa a organismo colectivo (PRO) | Por contratar |
| **Información al usuario** | Instrucciones de disposición correcta en manual | Por incluir |
| **Reporting** | Informe anual de cantidades puestas en mercado | Anual |

### 5.3 Símbolo WEEE

```
         ┌────────────┐
         │     🗑️      │
         │    ──X──    │  ← Contenedor con ruedas tachado
         │   /    \    │     Mínimo 7 mm de altura
         └────────────┘     En etiqueta del producto
```

### 5.4 Registro por País (Mercados prioritarios)

| País | Organismo | Registro | Eco-tasa estimada |
|------|----------|----------|-------------------|
| España | RAEE / Ecotic / Ecolec | Obligatorio | ~€0.05–€0.30/unidad |
| Alemania | Stiftung EAR | Obligatorio (elektroG) | ~€0.10–€0.50/unidad |
| Francia | Eco-organismes (ESR) | Obligatorio | ~€0.10–€0.40/unidad |
| Italia | CDC RAEE | Obligatorio | ~€0.05–€0.30/unidad |
| Países Bajos | Wecycle / Stichting Open | Obligatorio | ~€0.05–€0.25/unidad |

> **Recomendación:** Contratar un **Representante Autorizado EU** (EU AR) que gestione el registro WEEE en múltiples países. Coste típico: €2,000–€5,000/año para < 10 países.

---

## 6. Directiva RED — 2014/53/EU (Radio Equipment Directive)

### 6.1 Aplicabilidad

El Arduino UNO Q integra **WiFi 802.11b/g/n/ac** y **Bluetooth 5.1** vía el Qualcomm QRB2210. La Directiva RED aplica a cualquier equipo que transmita/reciba radio intencionalmente.

> **Nota importante:** El módulo de radio está **integrado en el Arduino UNO Q** (fabricado por Arduino). Si Arduino ya tiene certificación RED/FCC para el UNO Q, el Q-Shield® como shield pasivo no necesita certificación RED separada, siempre que no modifique la antena ni la cadena de RF.

### 6.2 Normas Armonizadas RED

| Requisito | Norma | Aplicabilidad |
|-----------|-------|---------------|
| EMC (Art. 3.1b) | EN 301 489-1 V2.2.3 + EN 301 489-17 V3.2.4 | WiFi + Bluetooth EMC |
| Espectro RF (Art. 3.2) | EN 300 328 V2.2.2 (2.4 GHz) | WiFi 2.4 GHz |
| Espectro RF (Art. 3.2) | EN 301 893 V2.1.1 (5 GHz) | WiFi 5 GHz |
| Espectro RF (Art. 3.2) | EN 300 328 V2.2.2 | Bluetooth |
| Seguridad (Art. 3.1a) | EN 62368-1:2020 | Seguridad eléctrica |
| SAR (si aplica) | EN 62209-2:2010 | Solo si dispositivo portátil < 20 cm del cuerpo |

### 6.3 Estrategia de Certificación

| Escenario | Estrategia | Costo |
|-----------|-----------|-------|
| Arduino UNO Q ya tiene RED cert. | Declarar Q-Shield como "accesorio pasivo" — No requiere RED propia | €0 |
| Arduino UNO Q NO tiene RED cert. | Certificar el conjunto (Q-Shield + UNO Q) como equipo de radio | €5,000–€15,000 |
| Usar módulo RF pre-certificado | Si el módulo Qualcomm tiene cert. modular | Verificar con Arduino |

**Recomendación:** Solicitar a Arduino la **Declaración de Conformidad RED** del UNO Q y verificar que cubra el uso como parte del Q-Shield®.

---

## 7. Regulación REACH — (EC) No 1907/2006

### 7.1 Obligaciones

| Obligación | Descripción | Acción |
|-----------|------------|--------|
| SVHC (Substances of Very High Concern) | Informar si producto contiene SVHC > 0.1% w/w | Verificar con proveedores |
| Candidate List check | Revisar lista de candidatos ECHA (actualizada 2×/año) | Cada 6 meses |
| SCIP Database | Notificar artículos con SVHC a la base de datos SCIP de ECHA | Si aplica |
| Declaración de proveedor | Solicitar declaración REACH a cada proveedor de componentes | Al inicio |

### 7.2 Componentes con Potencial SVHC

| Componente | Material de riesgo | Estado |
|-----------|-------------------|--------|
| Soldadura | Sin plomo (SAC305) — OK | ✓ Conforme |
| PCB FR-4 | Verificar retardante de llama (no debe ser HBCDD) | Verificar con fabricante |
| Capacitores MLCC | Verificar bario (BaTiO3) — actualmente no listado | ✓ OK |
| Conectores | Verificar niquelado | Solicitar declaración |

---

## 8. Marcado CE — Procedimiento

### 8.1 Pasos para Obtener Marcado CE

```
    ┌───────────────────┐
    │ 1. Identificar     │
    │    directivas      │
    │    aplicables      │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 2. Identificar     │
    │    normas          │
    │    armonizadas     │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 3. Diseñar         │
    │    conforme a      │
    │    normas          │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 4. Ensayos de      │
    │    conformidad     │
    │    (laboratorio)   │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 5. Compilar        │
    │    Technical File  │
    │    (Dossier)       │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 6. Declaration of  │
    │    Conformity      │
    │    (DoC) firmada   │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 7. Marcar CE en    │
    │    producto y      │
    │    embalaje        │
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │ 8. Comercializar   │
    │    en el EEA       │
    └───────────────────┘
```

### 8.2 Technical File (Dossier Técnico)

El dossier técnico debe contener:

| Sección | Contenido | Documento Q-Shield |
|---------|-----------|-------------------|
| Descripción general | Uso previsto, especificaciones | `README.md` + `01_PCB_ARCHITECTURE.md` |
| Dibujos de diseño | Esquemáticos, layout PCB, mecánico | Archivos KiCad |
| Esquemas eléctricos | Diagrama de circuito completo | KiCad schematic |
| Lista de componentes | BOM con referencias | `04_BOM_PRODUCTION.md` |
| Normas aplicadas | Lista de normas armonizadas | Este documento |
| Informes de ensayo | Resultados de laboratorio EMC/Safety | Post-ensayo |
| Análisis de riesgos | FMEA o análisis de riesgos | `02_FOOLPROOF_DESIGN.md` |
| Manual de usuario | Instrucciones de instalación y uso | Por crear |
| Declaración de Conformidad | DoC firmada | Plantilla abajo |

### 8.3 Plantilla — Declaración de Conformidad EU

```
═══════════════════════════════════════════════════════════
              EU DECLARATION OF CONFORMITY
═══════════════════════════════════════════════════════════

Manufacturer:
    Cafelium SRL
    [Dirección completa]
    República Dominicana

EU Authorized Representative:
    [Nombre del representante autorizado EU]
    [Dirección en la EU]

Product:
    Nebula Q-Shield® — Precision Fermentation Monitor PCB
    Model: NQS-SIG-001 (Signature) / NQS-INS-001 (Insight) /
           NQS-ESS-001 (Essential)

This declaration of conformity is issued under the sole
responsibility of the manufacturer.

The object of the declaration described above is in conformity
with the relevant Union harmonisation legislation:

    ☐ EMC Directive 2014/30/EU
    ☐ RoHS Directive 2011/65/EU as amended by 2015/863
    ☐ RED Directive 2014/53/EU (if applicable)

Standards applied:
    EN 55032:2015+A1:2020 (Class B)
    EN 61000-4-2:2009 (Level 4)
    EN 61000-4-3:2020 (10 V/m)
    EN 61000-4-4:2012 (Level 3)
    EN 61000-4-5:2014+A1:2017 (Level 2)
    EN 61000-4-6:2014 (10 V)
    EN 50581:2012 (RoHS technical documentation)

Test reports:
    [Número de informe de laboratorio]
    [Nombre del laboratorio acreditado]

Signed for and on behalf of:
    Cafelium SRL

    ________________________
    [Nombre]
    [Cargo]
    [Lugar, Fecha]
═══════════════════════════════════════════════════════════
```

### 8.4 Símbolo CE

```
    Proporciones oficiales del marcado CE:

         ┌──────────────────┐
         │                  │
         │    ████  ██████  │
         │   ██  ██ ██      │  Altura mínima: 5 mm
         │   ██     █████   │
         │   ██  ██ ██      │  Las dos letras deben tener
         │    ████  ██████  │  la MISMA altura
         │                  │
         └──────────────────┘

    Ubicación: Etiqueta del producto, embalaje, y manual.
    Si el producto es muy pequeño: solo en embalaje y manual.
```

---

## 9. UK UKCA (Post-Brexit)

Para vender en el Reino Unido, se requiere el marcado **UKCA** además del CE:

| Aspecto | CE (EU) | UKCA (UK) |
|---------|---------|-----------|
| Territorio | EEA (27 estados + EEA) | Gran Bretaña (no N. Irlanda) |
| Normas | EN (armonizadas EU) | BS EN (designadas UK) |
| Declaración | EU DoC | UK DoC |
| Representante | EU Authorized Representative | UK Responsible Person |
| Aceptación mutua | No acepta UKCA | Acepta CE hasta 2028 (pendiente extensión) |

> **Recomendación:** Certificar CE primero. El UKCA usa las mismas normas técnicas (BS EN = EN). Preparar UK DoC en paralelo es trivial.

---

## 10. Cronograma de Certificación Recomendado

| Fase | Actividad | Duración | Costo estimado |
|------|----------|----------|---------------|
| 1 | Diseño conforme a normas (este documento) | Completado | — |
| 2 | Pre-compliance testing interno | 2 semanas | ~€500 (equipo) |
| 3 | Correcciones de diseño (si necesario) | 1–2 semanas | — |
| 4 | Ensayos EMC en laboratorio acreditado | 2–4 semanas | €3,000–€8,000 |
| 5 | Ensayos RoHS (ICP-OES si requerido) | 1 semana | €500–€1,500 |
| 6 | Compilar Technical File | 1 semana | — |
| 7 | Firmar DoC + marcar producto | 1 día | — |
| 8 | Registro WEEE (por país) | 2–4 semanas | €500–€2,000/país |
| | **Total estimado** | **8–12 semanas** | **€5,000–€15,000** |

---

## 11. Laboratorios de Ensayo Recomendados

| Laboratorio | Ubicación | Acreditación | Servicios | Contacto |
|------------|-----------|-------------|-----------|----------|
| **TÜV SÜD** | Múnich, Alemania | DAkkS (ISO 17025) | EMC + Safety + RED | tuvsud.com |
| **SGS** | Múltiples (España, Alemania) | ENAC / DAkkS | EMC + RoHS + WEEE | sgs.com |
| **Bureau Veritas** | París, Francia + global | COFRAC | EMC + Safety | bureauveritas.com |
| **Intertek** | UK + EU | UKAS / DAkkS | EMC + RED + RoHS | intertek.com |
| **CETECOM** | Saarbrücken, Alemania | DAkkS | RED (radio) + EMC | cetecom.com |
| **Element** | UK + EU | UKAS | EMC + Environmental | element.com |

---

## 12. Checklist de Conformidad

| # | Requisito | Estado | Responsable |
|---|-----------|--------|------------|
| 1 | Diseño PCB con plano GND continuo (EMC) | ✓ Diseñado | Ingeniería HW |
| 2 | TVS ESD en todos los puertos (IEC 61000-4-2) | ✓ Diseñado | Ingeniería HW |
| 3 | Filtro EMI entrada (ferrite + caps) | ✓ Diseñado | Ingeniería HW |
| 4 | Componentes RoHS (soldadura SAC305, ENIG) | ✓ Especificado | Compras |
| 5 | Símbolo WEEE en producto y embalaje | ☐ Pendiente | Marketing |
| 6 | Registro WEEE en países target | ☐ Pendiente | Legal/Regulatorio |
| 7 | Technical File compilado | ☐ Pendiente | Ingeniería |
| 8 | Pre-compliance EMC testing | ☐ Pendiente | Ingeniería HW |
| 9 | Ensayos EMC laboratorio acreditado | ☐ Pendiente | Ingeniería HW |
| 10 | Ensayo RoHS (si requerido) | ☐ Pendiente | Calidad |
| 11 | Declaración de conformidad CE firmada | ☐ Pendiente | Dirección |
| 12 | Marcado CE en producto | ☐ Pendiente | Producción |
| 13 | RED — verificar certificación Arduino UNO Q | ☐ Pendiente | Ingeniería |
| 14 | REACH — solicitar declaraciones proveedores | ☐ Pendiente | Compras |
| 15 | UK UKCA DoC (si aplica) | ☐ Pendiente | Regulatorio |

---

*Documento NQS-EU-003 Rev 1.0 — Nebula Ecosystem® — Conformidad Europea Completa*
