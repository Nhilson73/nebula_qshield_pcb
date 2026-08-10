# Configurar KiCad 10 con GitHub por SSH (no-code / low-code)

Guía paso a paso para clonar el repositorio `Nhilson73/nebula_qshield_pcb` directamente desde KiCad 10 usando una llave SSH, sin necesidad de usar la terminal de Git.

---

## 1. Antes de empezar

- Tener instalado **KiCad 10.0.5** (o la versión 10.x que estés usando).
- Tener una cuenta en **GitHub** con acceso al repositorio.
- Para Windows: tener instalado **Git for Windows** o **OpenSSH para Windows** (viene en Windows 10/11 como componente opcional).

---

## 2. Generar la llave SSH

KiCad utiliza `libgit2`, que entiende el formato clásico de llave OpenSSH. Para evitar problemas de compatibilidad, generamos una llave RSA en formato PEM.

### Windows

1. Abrir **Git Bash** (viene con Git for Windows) o **PowerShell**.
2. Ejecutar:
   ```bash
   ssh-keygen -t rsa -b 4096 -m PEM -C "tucorreo@ejemplo.com"
   ```
3. Cuando pida la ubicación, dejar la predeterminada:
   ```
   C:\Users\<tu usuario>\.ssh\id_rsa
   ```
4. Puedes poner una contraseña (passphrase) o dejarla en blanco. Si la pones, KiCad te la pedirá cada vez que clone/fetch/push.

### macOS

1. Abrir **Terminal**.
2. Ejecutar:
   ```bash
   ssh-keygen -t rsa -b 4096 -m PEM -C "tucorreo@ejemplo.com"
   ```
3. Dejar la ubicación predeterminada:
   ```
   /Users/<tu usuario>/.ssh/id_rsa
   ```

### Linux

1. Abrir una terminal.
2. Ejecutar:
   ```bash
   ssh-keygen -t rsa -b 4096 -m PEM -C "tucorreo@ejemplo.com"
   ```
3. Dejar la ubicación predeterminada:
   ```
   ~/.ssh/id_rsa
   ```

---

## 3. Agregar la llave pública a GitHub

1. Abrir el archivo de la llave pública:

   - **Windows**: abrir `C:\Users\<tu usuario>\.ssh\id_rsa.pub` con el Bloc de notas.
   - **macOS/Linux**: ejecutar en terminal:
     ```bash
     cat ~/.ssh/id_rsa.pub
     ```

2. Copiar todo el contenido (empieza con `ssh-rsa` y termina con tu correo).
3. Ir a GitHub → clic en tu foto de perfil → **Settings**.
4. En el menú lateral, seleccionar **SSH and GPG keys**.
5. Clic en **New SSH key**.
6. Poner un título, por ejemplo: `KiCad laptop`.
7. Pegar la llave pública en el campo **Key**.
8. Clic en **Add SSH key**.

---

## 4. Clonar el repositorio desde KiCad

1. Abrir **KiCad** (Project Manager).
2. Menú: **File → Clone Project from Git Repository...**.
3. En el campo **Location**, escribir la URL SSH del repositorio:
   ```
   git@github.com:Nhilson73/nebula_qshield_pcb.git
   ```
4. En **Connection**, seleccionar **SSH** (si aparece el tipo de conexión). En algunas versiones KiCad detecta SSH automáticamente al ver `git@github.com`.
5. En **SSH private key**, seleccionar (Browse) el archivo:
   ```
   C:\Users\<tu usuario>\.ssh\id_rsa     (Windows)
   /Users/<tu usuario>/.ssh/id_rsa        (macOS)
   ~/.ssh/id_rsa                          (Linux)
   ```
6. En **User name**, puedes escribir `git` (GitHub ignora el usuario real para SSH; la autenticación es por llave).
7. En **SSH key password**, escribir la passphrase si pusiste una. Si dejaste la llave sin passphrase, dejar en blanco.
8. Clic en **Test Connection** para verificar. Debería conectar sin error.
9. Clic en **OK** para clonar.

> **Importante:** Asegúrate de que el archivo seleccionado sea la llave **privada** (`id_rsa`), no la pública (`id_rsa.pub`). La llave privada no tiene extensión `.pub`.

---

## 5. Abrir el proyecto

1. Después de clonar, KiCad te pedirá dónde guardar la carpeta local.
2. Elegir una carpeta, por ejemplo:
   ```
   C:\Users\<tu usuario>\Documents\KiCad\nebula_qshield_pcb
   ```
3. Una vez clonado, abrir el archivo `kicad/nebula_qshield.kicad_pro` desde el Project Manager.

---

## 6. Actualizar el proyecto (fetch / pull)

KiCad 10 incluye menús básicos de control de versiones:

1. En el Project Manager, hacer clic derecho sobre el proyecto.
2. Seleccionar **Version Control**.
3. Usar **Pull** o **Fetch** según necesites.

Si el menú de KiCad no hace pull correctamente (algunas versiones solo hacen fetch), puedes usar cualquier cliente Git (GitHub Desktop, TortoiseGit, la terminal) para hacer `git pull` en la carpeta clonada, y luego recargar el proyecto en KiCad.

---

## 7. Solución de problemas

### KiCad no acepta la llave o da error de autenticación

- Verificar que la URL sea `git@github.com:Nhilson73/nebula_qshield_pcb.git` y no `https://github.com/...`.
- Verificar que la llave privada sea `id_rsa` (sin `.pub`).
- Si la llave fue generada con `ssh-keygen` sin `-m PEM`, probar regenerarla con `-m PEM`.
- Si usas Windows y tu llave fue creada por PuTTY/TortoiseGit (archivo `.ppk`), KiCad no la entiende. Genera una nueva llave con `ssh-keygen` o `Git Bash`.

### Error "Unable to negotiate ... no matching host key type"

Esto ocurre en algunas versiones de `libgit2` si GitHub deshabilita algoritmos antiguos. Prueba agregar esto al archivo `~/.ssh/config` (crearlo si no existe):

```
Host github.com
    HostkeyAlgorithms +ssh-rsa
    PubkeyAcceptedAlgorithms +ssh-rsa
```

En Windows la ruta es `C:\Users\<tu usuario>\.ssh\config`.

### KiCad pide la passphrase cada vez

- Si no quieres escribir la passphrase, generar una nueva llave sin passphrase (presionar Enter cuando `ssh-keygen` pregunte).
- Alternativa en Windows: ejecutar `ssh-add C:\Users\<tu usuario>\.ssh\id_rsa` en Git Bash antes de abrir KiCad. Esto carga la llave en memoria.

### La conexión SSH funciona en terminal pero no en KiCad

- KiCad busca por defecto `id_rsa`, `id_dsa` o `id_ecdsa` en la carpeta `.ssh`. Si usas una llave Ed25519 (`id_ed25519`), usa el cuadro de diálogo de KiCad para seleccionarla manualmente.
- KiCad puede no detectar `id_ed25519` automáticamente. Se recomienda usar `id_rsa` para mayor compatibilidad.

---

## 8. Enlaces útiles

- Generar llaves SSH en GitHub: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
- Foro de KiCad sobre Git: https://forum.kicad.info/t/tutorial-how-to-enable-git-in-kicad-8/49235
- Documentación de KiCad sobre control de versiones: https://docs.kicad.org/
