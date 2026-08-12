# Guía para usar Claude Code en VS Code — Nebula Q-Shield (no-code / low-code)

> Esta guía asume que no sos programador. Seguí los pasos de arriba a abajo y copiá los textos tal cual se indican.

## Qué vas a necesitar

1. **Visual Studio Code** instalado (gratis): https://code.visualstudio.com/
2. **Git** instalado (gratis): https://git-scm.com/downloads
3. **Docker Desktop** instalado (gratis): https://www.docker.com/products/docker-desktop
4. La extensión **Claude Code** en VS Code (ya la instalaste).

> **Consejo:** si Docker Desktop te da problemas en Windows, activá WSL2 durante la instalación. Si no sabés qué es, dejá que Docker lo active por vos.

## Paso 1 — Abrí el repositorio en VS Code

1. Abrite una terminal en tu computadora.
   - **Windows:** buscá "Git Bash" o "PowerShell" y abrilo.
   - **Mac/Linux:** abrí "Terminal".
2. Escribí (o copiá y pegá) esto y apretá Enter:

```bash
git clone https://github.com/Nhilson73/nebula_qshield_pcb.git
cd nebula_qshield_pcb
code .
```

Esto descarga el repo y abre VS Code en esa carpeta.

## Paso 2 — Abrí Claude Code

1. En VS Code, buscá el icono de **Claude Code** en la barra lateral izquierda.
2. Hacé clic. Se abre un panel de chat.
3. Iniciá sesión con tu cuenta de Anthropic (la misma que usaste para pagar).

## Paso 3 — Cargá el prompt de trabajo

Copiá este mensaje exacto y pegalo en el chat de Claude Code:

```
Leé el archivo docs/PROMPT_CLAUDE_CODE_FASE6.md del repo actual y seguí las instrucciones paso a paso. El objetivo es generar el script tools/route_fase6.py, ejecutarlo, y dejar el archivo kicad/nebula_qshield.kicad_pcb con 0 errores DRC y 0 items desconectados. Si necesitás mover componentes, mové solo pasivos del bloque analógico y nunca más de 2 mm. Antes de tocar el board, preguntame confirmación.
```

## Paso 4 — Dejá que Claude trabaje

Claude va a:

1. Leer el prompt y el DRC report.
2. Escribir un script de Python dentro de `tools/`.
3. Ejecutar Docker con KiCad para validar.

Si Claude te pregunta algo, respondé:

- **"Sí" / "Continuá"** si te pide permiso para modificar archivos.
- **"No"** si te propone cambiar componentes inmutables (`J21`, conectores de borde, relés, etc.).

## Paso 5 — Revisá el resultado

Claude debería mostrarte al final algo como esto:

```
Found 0 violations
Found 0 unconnected items
```

Si ves eso, el board está listo para fabricación.

Si no, Claude te va a decir cuántos errores quedaron. Copiá ese mensaje y pasáselo a Devin para que siga.

## Paso 6 — Guardá y subí los cambios

Copiá este bloque y pegalo en el chat de Claude para que suba todo:

```
Hacé commit y push de los cambios en una nueva rama llamada claude/fase6-routing-final. Mensaje de commit: "feat(pcb): Claude Code routing script closes 38 unconnected nets". Luego abrí un pull request contra main.
```

Claude va a ejecutar los comandos de Git. Cuando termine, te dará un link al pull request.

## Paso 7 — Pasale el PR a Devin

Copiá el link del PR y pegalo en la conversación con Devin. Devin revisará el board con `kicad-cli` y mergeará o seguirá iterando si falta algo.

## Si algo falla

- **"Docker no encontrado":** asegurate de que Docker Desktop esté abierto.
- **"No tengo permisos":** Claude te va a pedir permisos de terminal; aceptalos.
- **Claude queda trabajando mucho tiempo:** es normal, el ruteo es complejo. Si se corta, escribí `continuá` en el chat.
- **No entendés un mensaje de Claude:** copialo y pasaselo a Devin.

## Comandos de validación que Claude debe correr

Claude ya los conoce, pero por las dudas acá están:

```bash
docker run --rm -v "$(pwd):/workspace" -w /workspace kicad/kicad:10.0.5 \
  kicad-cli pcb drc --severity-error --refill-zones \
  -o /workspace/kicad/nebula_qshield-drc.rpt \
  /workspace/kicad/nebula_qshield.kicad_pcb

docker run --rm -v "$(pwd):/workspace" -w /workspace kicad/kicad:10.0.5 \
  kicad-cli sch erc --severity-all \
  -o /workspace/kicad/nebula_qshield-erc.rpt \
  /workspace/kicad/nebula_qshield.kicad_sch
```

Resultado esperado en ambos: `Found 0 violations`.

## Reglas de oro

- **No mover `J21` (el header del UNO Q).**
- **No mover conectores de borde (`J1`, `J2`, `J3`, `J5`, `J7`, `J8–J14`, `J15–J19`).**
- **No mover relés `K1`/`K2` ni drivers `U17`/`U20`.**
- **El board debe seguir midiendo 150 mm × 120 mm.**
- Si Claude quiere mover algo que no entendés, preguntale por qué antes de aceptar.