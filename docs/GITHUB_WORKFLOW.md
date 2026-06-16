# Guía de Distribución GitHub — VulnApp

## Distribución de Actividades, Ramas y Commits para 6 Integrantes

**Universidad Católica Andrés Bello · Ciberseguridad**

---

## 📋 Resumen Ejecutivo

Este documento define **paso a paso** cómo crear el repositorio desde cero, configurar las ramas, asignar colaboradores y distribuir los commits entre los 6 integrantes (3 Red Team + 3 Blue Team), garantizando trazabilidad de autoría individual tal como requiere el proyecto.

---

## 👥 Asignación de Equipos y Ramas

| Integrante       | C.I.       | Equipo     | Rama de trabajo principal     | Responsabilidad técnica |
|------------------|------------|------------|-------------------------------|-------------------------|
| Maurizio Brazón  | 30.514.308 | 🔴 Red Team | `feature/injection`          | SQLi exploit + reconocimiento |
| César Sánchez    | 28.310.444 | 🔴 Red Team | `feature/injection`          | XSS Worm + C2 listener  |
| Eduard Velasco   | 30.700.089 | 🔴 Red Team | `feature/crypto-failures`    | Cookie tampering + Hashcat |
| César Reyes      | 31.101.802 | 🔵 Blue Team| `feature/injection`          | Sentencias preparadas + escape HTML |
| Marco Cegarra    | 30.967.516 | 🔵 Blue Team| `feature/crypto-failures`    | scrypt KDF + verificación contraseñas |
| Sebastián Cova   | 30.142.979 | 🔵 Blue Team| `feature/crypto-failures`    | HMAC-SHA256 + validación de cierre |

---

## 🏗 Fase 1: Crear el Repositorio desde Cero

### ¿Quién lo hace?
**Maurizio Brazón** (Red Team Lead) crea el repositorio en GitHub.

### Pasos en GitHub.com

1. Ir a **github.com → New repository**
2. Configurar:
   - **Repository name:** `vulnapp-ucab`
   - **Description:** `VulnApp — Simulación de ataque informático y remediación | OWASP A05:2025 + A04:2025 | UCAB Ciberseguridad`
   - **Visibility:** `Private` (⚠ el código es deliberadamente inseguro)
   - **Initialize with:** marcar `Add a README file`
   - **Add .gitignore:** `Node`
3. Click **Create repository**

### Configurar .gitignore en el repositorio

Editar el `.gitignore` generado para incluir:

```gitignore
# Node
node_modules/
npm-debug.log*
*.log

# SQLite databases (no versionar la BD con datos)
*.db
*.db-shm
*.db-wal

# Archivos temporales de Hashcat
*.potfile
*.restore

# Variables de entorno
.env
.env.local
```

---

## 🔗 Fase 2: Agregar Colaboradores

### ¿Quién lo hace?
**Maurizio Brazón** (dueño del repo) va a **Settings → Collaborators → Add people**.

### Permisos

| Integrante       | Username GitHub | Rol en repo  |
|------------------|-----------------|--------------|
| Maurizio Brazón  | `maurizio-brazon` | Admin (dueño) |
| César Sánchez    | `cesar-sanchez-sec` | Write |
| Eduard Velasco   | `eduardvelasco`  | Write |
| César Reyes      | `cesarreyesuab`  | Write |
| Marco Cegarra    | `marcocegarra`   | Write |
| Sebastián Cova   | `sebastiancova`  | Write |

> **Nota:** Cada integrante debe aceptar la invitación por email antes de poder hacer push.

---

## 🌿 Fase 3: Crear las Ramas Base

### Estructura de ramas requerida por el anteproyecto

```
main                    ← rama de producción (código base inicial)
│
├── feature/injection          ← ID-1: Inyección (SQLi + XSS)
│   ├── commits Red Team   (exploit vulnerable)
│   └── commits Blue Team  (parches y remediación)
│
└── feature/crypto-failures    ← ID-2: Fallas Criptográficas
    ├── commits Red Team   (cookie tampering + Hashcat)
    └── commits Blue Team  (scrypt + HMAC)
```

### Comandos para crear las ramas (ejecutar por Maurizio)

```bash
# 1. Clonar el repositorio recién creado
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab

# 2. Configurar identidad Git
git config user.name  "Maurizio Brazón"
git config user.email "maurizio.brazon@ucab.edu.ve"

# 3. En main: subir el código vulnerable base + README
cp -r /ruta/al/proyecto/vulnapp/vulnerable ./vulnerable
cp -r /ruta/al/proyecto/vulnapp/docs       ./docs
cp    /ruta/al/proyecto/vulnapp/README.md  ./README.md

git add .
git commit -m "feat(base): estructura inicial de VulnApp - aplicación vulnerable por diseño

- Arquitectura monolítica Node.js v20 + SQLite (better-sqlite3)
- Frontend HTML5/CSS3/Vanilla JS sin frameworks de seguridad
- Superficie de ataque: endpoints /api/login, /api/search, /api/message, etc.
- Vulnerabilidades por diseño: CWE-89, CWE-79, CWE-116, CWE-327, CWE-759, CWE-916, CWE-345, CWE-311
- README.md con inventario de endpoints y stack tecnológico

Refs: OWASP A05:2025 + A04:2025 | Cyber Kill Chain"

git push origin main

# 4. Crear y publicar rama feature/injection
git checkout -b feature/injection
git push origin feature/injection

# 5. Crear y publicar rama feature/crypto-failures
git checkout main
git checkout -b feature/crypto-failures
git push origin feature/crypto-failures

# 6. Volver a main
git checkout main
```

---

## 📝 Fase 4: Commits del RED TEAM — Línea ID-1 (feature/injection)

### 4.1 — Maurizio Brazón: Reconocimiento + Exploit SQLi

```bash
# En su máquina local
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/injection

git config user.name  "Maurizio Brazón"
git config user.email "maurizio.brazon@ucab.edu.ve"

# Copiar sus archivos al repo
mkdir -p red-team
cp /ruta/red-team/01_reconocimiento.py      red-team/
cp /ruta/red-team/02_exploit_sqli.py        red-team/
cp /ruta/vulnerable/server.js               vulnerable/   # con comentarios vuln

# COMMIT 1: Reconocimiento
git add red-team/01_reconocimiento.py
git commit -m "red(recon): Fase I CKC - Reconocimiento manual de endpoints

- Script Python puro (sin herramientas de escaneo automatizado)
- Enumera: /api/login, /api/register, /api/search, /api/message, /api/profile
- Detecta cabeceras: X-Powered-By: Express, Set-Cookie: Base64 sin firma
- Análisis de la cookie de sesión: JSON en Base64 → CWE-345 confirmado
- Fases: I (Reconocimiento) de la Cyber Kill Chain

CWE: CWE-345, CWE-311 | OWASP: A04:2025 Fallas Criptográficas"

# COMMIT 2: Servidor vulnerable con comentarios de explotación
git add vulnerable/server.js
git commit -m "red(vuln): Backend vulnerable documentado con puntos de inyección SQLi

- POST /api/login: concatenación directa → CWE-89 explotable con OR bypass
- GET /api/users/:id: parámetro de ruta sin validación → UNION-Based SQLi
- POST /api/search: LIKE sin parametrización → exfiltración de sqlite_master
- MD5 sin salt en registro → CWE-327, CWE-759, CWE-916
- Cookie Base64 sin HMAC → CWE-345, CWE-311
- Cada vulnerabilidad documentada con comentarios en código fuente

Refs: Fases II+III+IV Cyber Kill Chain"

# COMMIT 3: Exploit SQLi
git add red-team/02_exploit_sqli.py
git commit -m "red(exploit): Fase III+IV CKC - Explotación manual SQL Injection (CWE-89)

- UNION-Based SQLi en /api/login, /api/search, /api/users/:id
- Entrega via POST con Content-Type: application/json (req.body directo)
- Sin SQLMap: control total sobre cada byte del payload
- Payload OR-bypass: ' OR '1'='1'-- → autentica sin credenciales válidas
- Payload UNION: extrae sqlite_master + tabla users + hashes MD5
- Documenta cómo el payload altera el AST de SQLite (better-sqlite3)
- Salida: hashes MD5 guardados en /tmp/vulnapp_hashes.txt para Hashcat

OWASP: A05:2025 | CWE: CWE-89"

git push origin feature/injection
```

### 4.2 — César Sánchez: XSS Worm + C2

```bash
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/injection
git pull origin feature/injection

git config user.name  "César Sánchez"
git config user.email "cesar.sanchez@ucab.edu.ve"

cp /ruta/red-team/04_xss_worm_payload.py red-team/

# COMMIT 1: Frontend vulnerable con innerHTML
git add vulnerable/public/index.html
git commit -m "red(vuln): Frontend vulnerable - innerHTML expuesto a Stored XSS (CWE-79/116)

- Mensajes renderizados con innerHTML sin sanitización de salida (CWE-116)
- Sin Content-Security-Policy (CSP) → ejecución irrestricta de scripts inline
- Panel de sesión expone cookie Base64 decodificada (CWE-311)
- Bandeja de entrada actúa como vector de propagación del Worm XSS

OWASP: A05:2025 | CWE: CWE-79, CWE-116"

# COMMIT 2: XSS Worm + C2
git add red-team/04_xss_worm_payload.py
git commit -m "red(exploit): Fases V+VI CKC - XSS Worm autorreplicante + C2 listener (CWE-79)

- Payload JavaScript asíncrono con fetch() nativo del navegador
- Fase Instalación: XSS persistente almacenado en BD SQLite → CWE-79
- Fase C2: servidor Python escucha beacons en puerto 8888
- Propagación Worm: se re-envía automáticamente a todos los usuarios
- Entrega: POST /api/message con Content-Type: application/json (req.body.content)
- Sin sanitización en servidor → innerHTML lo ejecuta en cada víctima

OWASP: A05:2025 | CWE: CWE-79, CWE-116 | Fases: V+VI CKC"

git push origin feature/injection
```

---

## 📝 Fase 5: Commits del RED TEAM — Línea ID-2 (feature/crypto-failures)

### 5.1 — Eduard Velasco: Cookie Tampering + Hashcat

```bash
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/crypto-failures
git pull origin feature/crypto-failures

git config user.name  "Eduard Velasco"
git config user.email "eduard.velasco@ucab.edu.ve"

cp /ruta/red-team/03_exploit_cookie_tampering.py red-team/
cp /ruta/red-team/05_hashcat_demo.sh              red-team/

# COMMIT 1: Cookie Tampering
git add red-team/03_exploit_cookie_tampering.py
git commit -m "red(exploit): Fases III+IV CKC - Cookie Base64 Tampering sin HMAC (CWE-345/311)

- 5 pasos documentados: login → decode B64 → manipular JSON → encode → inyectar
- Base64 es codificación de transporte (RFC 4648), NO cifrado (demostrado)
- Escalada de privilegios: role='user' → role='admin' en cookie
- Entrega: cabecera Cookie: session=<BASE64_ADULTERADO> en GET /api/profile
- Por qué funciona: ausencia de HMAC → servidor valida ciegamente (CWE-345)
- Impacto: acceso admin + exposición íntegra de BD con hashes

Nota corrección: Esta vuln es A04:2025 (Fallas Criptográficas), NO A01:2025.
La escalada de privilegios es consecuencia del fallo criptográfico (CWE-345).

OWASP: A04:2025 | CWE: CWE-345, CWE-311"

# COMMIT 2: Hashcat demo
git add red-team/05_hashcat_demo.sh
git commit -m "red(exploit): Fase VII CKC - Cracking offline MD5 sin salt con Hashcat (CWE-759/916)

- Hashes MD5 extraídos de la BD via SQLi en fase anterior
- hashcat -m 0 -a 0 hashes.txt rockyou.txt → descifra en < 0.001 segundos
- Tabla comparativa: MD5 (10B hash/s GPU) vs scrypt (500 hash/s GPU)
- Sin salt: usuarios con misma clave tienen mismo hash → Rainbow Tables
- Impacto: credenciales de todos los usuarios comprometidas para Credential Stuffing

OWASP: A04:2025 | CWE: CWE-327, CWE-759, CWE-916 | Fase: VII CKC"

git push origin feature/crypto-failures
```

---

## 📝 Fase 6: Commits del BLUE TEAM — Línea ID-1 (feature/injection)

### 6.1 — César Reyes: Sentencias Preparadas + Escape HTML

```bash
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/injection
git pull origin feature/injection

git config user.name  "César Reyes"
git config user.email "cesar.reyes@ucab.edu.ve"

cp /ruta/secure/server.js        secure/
cp /ruta/secure/public/index.html secure/public/
mkdir -p secure/public secure

# COMMIT 1: Backend seguro — sentencias preparadas
git add secure/server.js
git commit -m "fix(injection): Blue Team - Remediación CWE-89 con sentencias preparadas nativas

- TODOS los endpoints migrados a db.prepare('... WHERE col = ?') con better-sqlite3
- Parámetros posicionales (?): el driver precompila la query antes de insertar datos
- El input del usuario nunca altera el AST de SQLite → CWE-89 eliminado
- /api/login: SELECT ... WHERE username = ? (payload OR no ejecutable)
- /api/search: SELECT ... WHERE username LIKE ? (UNION SELECT inoperante)
- /api/users/:id: validación de tipo (/^\d+$/) + SELECT WHERE id = ?
- Validación de longitud y tipos en todos los endpoints

Prueba de concepto: ' OR '1'='1'-- retorna HTTP 401 (0 resultados)
Prueba de concepto: UNION SELECT FROM users → 0 filas / error de columnas

OWASP: A05:2025 | CWE: CWE-89 | Contramedida: Parametrización (NIST SP 800-160)"

# COMMIT 2: Frontend seguro — textContent
git add secure/public/index.html
git commit -m "fix(xss): Blue Team - Remediación CWE-79/116 con textContent y escapeHtml()

- innerHTML reemplazado por textContent en renderizado de mensajes
- textContent trata cualquier string como texto literal (no HTML/JS)
- El servidor aplica escapeHtml() antes del envío (defensa en profundidad):
  < → &lt;  | > → &gt;  | & → &amp;  | ' → &#x27;  | \" → &quot;
- XSS Worm se muestra como texto inofensivo: <script>...</script> literal

Prueba de concepto: <script>alert('XSS')</script> → mostrado como texto
Prueba de concepto: fetch() del Worm → NO se ejecuta en el navegador

OWASP: A05:2025 | CWE: CWE-79, CWE-116 | Contramedida: Output Encoding + textContent"

git push origin feature/injection
```

---

## 📝 Fase 7: Commits del BLUE TEAM — Línea ID-2 (feature/crypto-failures)

### 7.1 — Marco Cegarra: scrypt KDF + Verificación segura

```bash
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/crypto-failures
git pull origin feature/crypto-failures

git config user.name  "Marco Cegarra"
git config user.email "marco.cegarra@ucab.edu.ve"

# COMMIT: scrypt KDF
git add secure/server.js
git commit -m "fix(crypto): Blue Team - Remediación CWE-327/759/916 con scrypt KDF nativo

- MD5 eliminado completamente del flujo de almacenamiento de contraseñas
- Implementación con crypto.scryptSync() — módulo nativo Node.js v20
- Salt CSPRNG: crypto.randomBytes(16).toString('hex') — único por usuario
- Formato almacenado: 'salt_hex:derived_key_hex' (64 bytes derivados)
- Verificación con timingSafeEqual() — previene Timing Attacks (canal lateral)
- MD5 (10B hash/seg GPU) vs scrypt (500 hash/seg GPU) → rainbow tables inviables

hashPassword(pwd): genera salt aleatorio + scrypt → 'salt:key'
verifyPassword(pwd, stored): re-deriva + timingSafeEqual → boolean

Sin librerías externas: solo crypto nativo (NIST SP 800-160 — Seguridad por Diseño)

OWASP: A04:2025 | CWE: CWE-327, CWE-759, CWE-916 | Contramedida: KDF scrypt + CSPRNG"

git push origin feature/crypto-failures
```

### 7.2 — Sebastián Cova: HMAC-SHA256 + Validación de cierre

```bash
git clone https://github.com/maurizio-brazon/vulnapp-ucab.git
cd vulnapp-ucab
git checkout feature/crypto-failures
git pull origin feature/crypto-failures

git config user.name  "Sebastián Cova"
git config user.email "sebastian.cova@ucab.edu.ve"

cp /ruta/red-team/06_verificacion_contramedidas.py red-team/
cp /ruta/docs/IMPACTO_CVSS.md                      docs/

# COMMIT 1: HMAC
git add secure/server.js
git commit -m "fix(crypto): Blue Team - Remediación CWE-345/311 con cookie firmada HMAC-SHA256

- Cookie en Base64 plano reemplazada por formato: BASE64(payload).FIRMA_HMAC
- Firma generada: crypto.createHmac('sha256', SECRET).update(payloadB64).digest('hex')
- Verificación en cada request: re-genera HMAC y compara con timingSafeEqual()
- Cualquier manipulación del payload invalida la firma → HTTP 401/403
- Cookie con HttpOnly=true + SameSite=Strict (previene CSRF y acceso JS)
- Rol verificado en BD (requireAdmin) — no se confía en el rol de la cookie
- Sin JWT ni librerías externas: solo módulo crypto nativo (NIST SP 800-160)

Prueba de concepto: Cookie Base64 adulterada → HTTP 401 (timingSafeEqual falla)
Prueba de concepto: role=admin en cookie sin HMAC válido → acceso denegado

OWASP: A04:2025 | CWE: CWE-345, CWE-311 | Contramedida: HMAC-SHA256 + timingSafeEqual"

# COMMIT 2: Validación de cierre + CVSS
git add red-team/06_verificacion_contramedidas.py docs/IMPACTO_CVSS.md
git commit -m "docs(validation): Blue Team - Validación de cierre + análisis de impacto CVSS v4.0

- Script de verificación: ejecuta los 4 exploits del Red Team contra versión segura
- Test 1: SQLi bypass → HTTP 401 (sentencias preparadas)
- Test 2: UNION SELECT → 0 filas sin hashes expuestos
- Test 3: Cookie Base64 adulterada → HTTP 401 (HMAC inválido)
- Test 4: XSS Worm → contenido escapado como texto literal
- Test 5: scrypt login correcto → HTTP 200
- Análisis CVSS v4.0: vectores, scores y comparativas para cada vulnerabilidad
- Tabla CIA: Confidencialidad/Integridad/Disponibilidad por vulnerabilidad

Validación: 100% de exploits neutralizados en versión asegurada"

git push origin feature/crypto-failures
```

---

## 🔀 Fase 8: Merge de Ramas a Main

### ¿Quién lo hace?
**Maurizio Brazón** (Admin) realiza los merges finales via Pull Request en GitHub.

### Paso a paso

#### Pull Request 1: feature/injection → main

1. En GitHub: **Pull requests → New pull request**
   - base: `main` ← compare: `feature/injection`
   - Title: `[ID-1] Inyección: Exploit SQLi/XSS + Remediación (sentencias preparadas + textContent)`
   - Description:
     ```
     ## Línea de Trabajo ID-1: Inyección (A05:2025)

     ### Red Team (Maurizio Brazón, César Sánchez)
     - Reconocimiento: enumeración manual de endpoints
     - Exploit SQLi UNION-Based en /api/login, /api/search, /api/users/:id
     - XSS Worm autorreplicante + C2 listener en puerto 8888

     ### Blue Team (César Reyes)
     - Sentencias preparadas en todos los endpoints (CWE-89 neutralizado)
     - escapeHtml() + textContent (CWE-79/116 neutralizados)
     - Verificación: exploit original ineficaz en versión segura

     CWE: 89, 79, 116 | OWASP: A05:2025
     ```
   - Reviewers: César Reyes, César Sánchez
   - **Merge strategy:** Squash and merge (para commits limpios) o **Merge commit** (para trazabilidad individual)

2. Aprobar el PR y hacer merge.

#### Pull Request 2: feature/crypto-failures → main

1. **Pull requests → New pull request**
   - base: `main` ← compare: `feature/crypto-failures`
   - Title: `[ID-2] Fallas Criptográficas: Cookie Tampering/Hashcat + Remediación (scrypt + HMAC)`
   - Description:
     ```
     ## Línea de Trabajo ID-2: Fallas Criptográficas (A04:2025)

     ### Red Team (Eduard Velasco)
     - Cookie Base64 Tampering: 5 pasos de explotación documentados
     - Hashcat: cracking offline de hashes MD5 sin salt

     ### Blue Team (Marco Cegarra, Sebastián Cova)
     - scrypt KDF: crypto.scryptSync() + CSPRNG salt (CWE-327/759/916)
     - HMAC-SHA256: cookie firmada + timingSafeEqual (CWE-345/311)
     - Validación de cierre: 100% exploits neutralizados
     - Análisis CVSS v4.0 completo

     CWE: 327, 759, 916, 345, 311 | OWASP: A04:2025
     ```

2. Aprobar y hacer merge.

---

## 🏷 Fase 9: Tag de Release Final

```bash
git checkout main
git pull origin main

# Tag de versión vulnerable
git tag -a v1.0-vulnerable -m "VulnApp v1.0 - Versión vulnerable (pre-remediación)
Vulnerabilidades activas: CWE-89, CWE-79, CWE-116, CWE-327, CWE-759, CWE-916, CWE-345, CWE-311
OWASP: A05:2025 + A04:2025
Para fines de demostración ofensiva únicamente."

# Tag de versión asegurada
git tag -a v2.0-secure -m "VulnApp v2.0 - Versión asegurada (post-remediación Blue Team)
Contramedidas: Sentencias preparadas, scrypt KDF, HMAC-SHA256, textContent
OWASP: A05:2025 + A04:2025 neutralizados
NIST SP 800-160: Seguridad por Diseño."

git push origin --tags
```

---

## 📊 Resumen Visual de Commits por Integrante

```
main
│
│  commit: "feat(base): estructura inicial de VulnApp"  ← Maurizio Brazón
│
├─────────────────────────────────────────────────────────────────────────
│              feature/injection
│              │
│              │  Red Team ──────────────────────────────────────────────
│              │  commit: "red(recon): Fase I CKC - Reconocimiento"     ← Maurizio Brazón
│              │  commit: "red(vuln): Backend vulnerable documentado"   ← Maurizio Brazón
│              │  commit: "red(exploit): Fases III+IV - SQLi CWE-89"   ← Maurizio Brazón
│              │  commit: "red(vuln): Frontend vulnerable innerHTML"    ← César Sánchez
│              │  commit: "red(exploit): Fases V+VI - XSS Worm + C2"  ← César Sánchez
│              │
│              │  Blue Team ─────────────────────────────────────────────
│              │  commit: "fix(injection): CWE-89 sentencias preparadas" ← César Reyes
│              │  commit: "fix(xss): CWE-79/116 textContent+escapeHtml" ← César Reyes
│              │
├─────────────────────────────────────────────────────────────────────────
│              feature/crypto-failures
│              │
│              │  Red Team ──────────────────────────────────────────────
│              │  commit: "red(exploit): Cookie Base64 Tampering CWE-345" ← Eduard Velasco
│              │  commit: "red(exploit): Hashcat MD5 cracking CWE-759"   ← Eduard Velasco
│              │
│              │  Blue Team ─────────────────────────────────────────────
│              │  commit: "fix(crypto): scrypt KDF CWE-327/759/916"      ← Marco Cegarra
│              │  commit: "fix(crypto): HMAC-SHA256 CWE-345/311"         ← Sebastián Cova
│              │  commit: "docs(validation): Validación cierre CVSS"     ← Sebastián Cova
│
│  [PR Merge] feature/injection → main
│  [PR Merge] feature/crypto-failures → main
│
│  tag: v1.0-vulnerable
│  tag: v2.0-secure
```

---

## ✅ Checklist Final para la Entrega

### Verificar antes de la presentación

- [ ] Repositorio privado con los 6 integrantes como colaboradores
- [ ] Rama `feature/injection` con commits de Maurizio, César Sánchez y César Reyes
- [ ] Rama `feature/crypto-failures` con commits de Eduard, Marco y Sebastián
- [ ] 2 Pull Requests mergeados a `main` (uno por línea de trabajo)
- [ ] Tags `v1.0-vulnerable` y `v2.0-secure` publicados
- [ ] README.md con inventario de endpoints visible en la raíz del repo
- [ ] Carpeta `docs/` con PAYLOADS_REFERENCIA.txt e IMPACTO_CVSS.md
- [ ] Carpeta `red-team/` con todos los scripts Python y shell
- [ ] `.gitignore` excluye archivos `.db`, `.env` y `node_modules/`
- [ ] Cada commit tiene prefijo de equipo (`red(...)` o `fix(...)`)
- [ ] La autoría de cada commit refleja el nombre real del integrante

---

## ⚠ Reglas Importantes

1. **No pushear directamente a `main`** — solo via Pull Request
2. **No hacer merge de sus propias Pull Requests** — debe aprobarlas otro integrante
3. **Cada integrante configura** `git config user.name` y `git config user.email` con su nombre real antes de hacer commits
4. **No versionar** archivos `.db` ni `.env` (el `.gitignore` lo previene)
5. **No subir contraseñas reales** — solo el seed de datos de laboratorio
6. **El repositorio debe ser PRIVADO** hasta concluir el curso
