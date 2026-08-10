# Configurar KiCad 10 con GitHub por SSH (no-code / low-code)

Guía paso a paso para clonar el repositorio `Nhilson73/nebula_qshield_pcb` directamente desde KiCad 10 usando una llave SSH, sin necesidad de usar la terminal de Git.

---

## 1. Antes de empezar

- Tener instalado **KiCad 10.0.5** (o la versión 10.x que estés usando).
- Tener una cuenta en **GitHub** con acceso al repositorio.
- Para Windows: tener instalado **Git for Windows** o **OpenSSH para Windows** (viene en Windows 10/11 como componente opcional).

---

## 2. Generar la llave SSH

KiCad utiliza `libgit2`. Recomendamos generar una llave **Ed25519** (más segura y compacta). Si KiCad no la acepta, probar con **ECDSA** o, como última opción, **RSA 4096** en formato OpenSSH moderno (sin `-m PEM`).

### Windows

1. Abrir **Git Bash** (viene con Git for Windows) o **PowerShell**.
2. Ejecutar:
   ```bash
   ssh-keygen -t ed25519 -C "tucorreo@ejemplo.com"
   ```
3. Cuando pida la ubicación, dejar la predeterminada:
   ```
   C:\Users\<tu usuario>\.ssh\id_ed25519
   ```
4. Se recomienda poner una **passphrase** para proteger la llave privada. Si prefieres comodidad, puedes dejarla en blanco, pero ten en cuenta que cualquiera con acceso al archivo podría usarla.

### macOS

1. Abrir **Terminal**.
2. Ejecutar:
   ```bash
   ssh-keygen -t ed25519 -C "tucorreo@ejemplo.com"
   ```
3. Dejar la ubicación predeterminada:
   ```
   /Users/<tu usuario>/.ssh/id_ed25519
   ```

### Linux

1. Abrir una terminal.
2. Ejecutar:
   ```bash
   ssh-keygen -t ed25519 -C "tucorreo@ejemplo.com"
   ```
3. Dejar la ubicación predeterminada:
   ```
   ~/.ssh/id_ed25519
   ```

---

## 3. Agregar la llave pública a GitHub

1. Abrir el archivo de la llave pública:

   - **Windows**: abrir `C:\Users\<tu usuario>\.ssh\id_ed25519.pub` con el Bloc de notas.
   - **macOS/Linux**: ejecutar en terminal:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```

2. Copiar todo el contenido (empieza con `ssh-ed25519` y termina con tu correo).
3. Ir a GitHub → clic en tu foto de perfil → **Settings**.
4. En el menú lateral, seleccionar **SSH and GPG keys**.
5. Clic en **New SSH key**.
6. Poner un título, por ejemplo: `KiCad laptop`.
7. Pegar la llave pública en el campo **Key**.
8. Clic en **Add SSH key**.

---

## 4. Agregar la clave del host de GitHub

La primera vez, KiCad/libgit2 necesita conocer la clave pública del host `github.com`. Si no está registrada, el test de conexión dará `invalid or unknown remote ssh hostkey`.

1. Abrir **Git Bash** (Windows), **Terminal** (macOS) o una terminal (Linux).
2. Ejecutar:
   ```bash
   ssh-keyscan github.com >> ~/.ssh/known_hosts
   ```
   O, si prefieres hacerlo manualmente:
   ```bash
   ssh -T git@github.com
   ```
   y escribir `yes` cuando pregunte si confías en el host.
3. Verificar que el archivo `known_hosts` se creó en:
   - Windows: `C:\Users\<tu usuario>\.ssh\known_hosts`
   - macOS: `/Users/<tu usuario>/.ssh/known_hosts`
   - Linux: `~/.ssh/known_hosts`

## 5. Clonar el repositorio desde KiCad

1. Abrir **KiCad** (Project Manager).
2. Menú: **File → Clone Project from Git Repository...**.
3. En el campo **Location**, escribir la URL SSH del repositorio **con el usuario `git@`**:
   ```
   git@github.com:Nhilson73/nebula_qshield_pcb.git
   ```
   > Si escribes solo `github.com:Nhilson73/nebula_qshield_pcb.git` (sin `git@`), KiCad puede no reconocer el usuario SSH y fallar.
4. En **Connection**, seleccionar **SSH** (si aparece el tipo de conexión). En algunas versiones KiCad detecta SSH automáticamente al ver `git@github.com`.
5. En **SSH private key**, seleccionar (Browse) el archivo:
   ```
   C:\Users\<tu usuario>\.ssh\id_ed25519     (Windows)
   /Users/<tu usuario>/.ssh/id_ed25519        (macOS)
   ~/.ssh/id_ed25519                          (Linux)
   ```
6. En **User name**, escribir `git` (GitHub ignora el usuario real para SSH; la autenticación es por llave).
7. En **SSH key password**, escribir la passphrase si pusiste una. Si dejaste la llave sin passphrase, dejar en blanco.
8. Clic en **Test Connection** para verificar. Debería conectar sin error.
9. Clic en **OK** para clonar.

> **Importante:** Asegúrate de que el archivo seleccionado sea la llave **privada** (`id_ed25519`), no la pública (`id_ed25519.pub`). La llave privada no tiene extensión `.pub`.

> **Nota:** Algunas versiones de KiCad solo detectan automáticamente `id_rsa`, `id_dsa` o `id_ecdsa` en la carpeta `.ssh`. Si el campo no se rellena solo, usa el botón **Browse** para seleccionar `id_ed25519` manualmente.

---

## 6. Abrir el proyecto

1. Después de clonar, KiCad te pedirá dónde guardar la carpeta local.
2. Elegir una carpeta, por ejemplo:
   ```
   C:\Users\<tu usuario>\Documents\KiCad\nebula_qshield_pcb
   ```
3. Una vez clonado, abrir el archivo `kicad/nebula_qshield.kicad_pro` desde el Project Manager.

---

## 7. Actualizar el proyecto (fetch / pull)

KiCad 10 incluye menús básicos de control de versiones:

1. En el Project Manager, hacer clic derecho sobre el proyecto.
2. Seleccionar **Version Control**.
3. Usar **Pull** o **Fetch** según necesites.

Si el menú de KiCad no hace pull correctamente (algunas versiones solo hacen fetch), puedes usar cualquier cliente Git (GitHub Desktop, TortoiseGit, la terminal) para hacer `git pull` en la carpeta clonada, y luego recargar el proyecto en KiCad.

---

## 8. Solución de problemas

### KiCad no acepta la llave o da error de autenticación

- Verificar que la URL sea `git@github.com:Nhilson73/nebula_qshield_pcb.git` y no `https://github.com/...`.
- Verificar que la llave privada sea `id_ed25519` (sin `.pub`).
- Si usas Windows y tu llave fue creada por PuTTY/TortoiseGit (archivo `.ppk`), KiCad no la entiende. Genera una nueva llave con `ssh-keygen` o **Git Bash** en formato OpenSSH.
- Si Ed25519 no funciona, probar con ECDSA:
  ```bash
  ssh-keygen -t ecdsa -b 521 -C "tucorreo@ejemplo.com"
  ```
  y usar el archivo `id_ecdsa` en KiCad.
- Si ECDSA tampoco funciona, como última opción usar RSA 4096:
  ```bash
  ssh-keygen -t rsa -b 4096 -C "tucorreo@ejemplo.com"
  ```
  y usar `id_rsa`.

### KiCad pide la passphrase cada vez

- Se recomienda usar una passphrase y cargar la llave en el agente SSH antes de abrir KiCad.
- En Windows (Git Bash / PowerShell):
  ```bash
  ssh-add C:\Users\<tu usuario>\.ssh\id_ed25519
  ```
- En macOS/Linux:
  ```bash
  ssh-add ~/.ssh/id_ed25519
  ```
- Si prefieres no escribir la passphrase, puedes dejar la llave sin passphrase al generarla, pero es menos seguro.

### Error "Unable to negotiate ... no matching host key type"

- Este error suele deberse a una llave o algoritmo no soportado por la versión de `libgit2` de KiCad. La solución más sencilla es usar **Ed25519** o **ECDSA** en lugar de RSA.
- Si estás usando una llave RSA muy antigua (formato PEM o firma SHA-1), regenera la llave con el comando moderno de RSA o, preferiblemente, con Ed25519.
- **No se recomienda** agregar configuraciones globales en `~/.ssh/config` para reactivar algoritmos obsoletos (`ssh-rsa` SHA-1), ya que reduce la seguridad de todas las conexiones SSH.

### La conexión SSH funciona en terminal pero no en KiCad

- KiCad puede no detectar automáticamente `id_ed25519`. Selecciónala manualmente con el botón **Browse**.
- Verifica que la llave privada sea el archivo sin extensión `.pub`.
- Asegúrate de que el archivo de la llave esté en formato OpenSSH. Si fue generado por PuTTY, conviértelo o genera una nueva con `ssh-keygen`.

---

## 9. Enlaces útiles

- Generar llaves SSH en GitHub: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
- Foro de KiCad sobre Git: https://forum.kicad.info/t/tutorial-how-to-enable-git-in-kicad-8/49235
- Documentación de KiCad sobre control de versiones: https://docs.kicad.org/
