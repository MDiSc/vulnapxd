# Guía de Distribución GitHub — VulnApp

## Distribución de Actividades, Ramas y Commits para 6 Integrantes

**Universidad Católica Andrés Bello · Ciberseguridad**

---

## 📋 Resumen Ejecutivo

Este documento define **paso a paso** cómo configurar las ramas exigidas por el profesor, asignar colaboradores y distribuir los commits entre los 6 integrantes (3 Red Team + 3 Blue Team), garantizando trazabilidad de autoría individual tal como requiere el proyecto.

---

## 👥 Asignación de Equipos y Ramas

De acuerdo con las nuevas directrices de evaluación, el proyecto usará **exclusivamente dos ramas principales claramente diferenciadas**:

| Integrante       | C.I.       | Equipo     | Rama de trabajo obligatoria     | Responsabilidad técnica |
|------------------|------------|------------|---------------------------------|-------------------------|
| Maurizio Brazón  | 30.514.308 | 🔴 Red Team | `version-vulnerable`          | SQLi exploit + reconocimiento |
| César Sánchez    | 28.310.444 | 🔴 Red Team | `version-vulnerable`          | XSS Worm + C2 listener  |
| Eduard Velasco   | 30.700.089 | 🔴 Red Team | `version-vulnerable`          | Cookie tampering + Hashcat |
| César Reyes      | 31.101.802 | 🔵 Blue Team| `version-asegurada`           | Sentencias preparadas + escape HTML |
| Marco Cegarra    | 30.967.516 | 🔵 Blue Team| `version-asegurada`           | scrypt KDF + verificación contraseñas |
| Sebastián Cova   | 30.142.979 | 🔵 Blue Team| `version-asegurada`           | HMAC-SHA256 + validación de cierre |

---

## 🏗 Fase 1: Crear el Repositorio y las Dos Ramas Base

### ¿Quién lo hace?
**Maurizio Brazón** (Red Team Lead) crea el repositorio en GitHub y sube las bases iniciales para todos. *(Este paso ya ha sido completado y automatizado, las ramas ya existen en el repositorio).*

### Estructura de ramas requerida
```text
version-vulnerable      ← Código base inseguro + Comentarios Técnicos + Exploits del Red Team
│
└── version-asegurada   ← (Derivada de la vulnerable) Código remediado y asegurado por el Blue Team
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

> **Nota:** Cada integrante debe aceptar la invitación por email antes de poder hacer clone o push.

---

## 📝 Fase 3: Flujo de Trabajo del RED TEAM (Rama `version-vulnerable`)

Los miembros del Red Team deben clonar el repo y trabajar **SIEMPRE** sobre la rama `version-vulnerable`.

```bash
# 1. Clonar el repositorio
git clone https://github.com/MDiSc/vulnapp.git
cd vulnapp

# 2. Configurar identidad Git (¡Obligatorio para la nota individual!)
git config user.name "Tu Nombre"
git config user.email "tu.correo@ucab.edu.ve"

# 3. Asegurarse de estar en la rama vulnerable
git checkout version-vulnerable
git pull origin version-vulnerable
```

### 3.1 — Maurizio Brazón: Reconocimiento + Exploit SQLi
Debe agregar sus scripts en la carpeta `red-team/` y hacer commits documentados.
Ejemplo de commit:
```bash
git add red-team/01_reconocimiento.py red-team/02_exploit_sqli.py
git commit -m "red(exploit): Fases I-IV - Reconocimiento manual y SQLi (CWE-89)"
git push origin version-vulnerable
```

### 3.2 — César Sánchez: XSS Worm + C2
Debe agregar sus scripts de XSS en la carpeta del Red Team.
Ejemplo de commit:
```bash
git add red-team/04_xss_worm_payload.py
git commit -m "red(exploit): Fases V-VI - XSS Worm autorreplicante (CWE-79/116)"
git push origin version-vulnerable
```

### 3.3 — Eduard Velasco: Cookie Tampering + Hashcat
Debe documentar el abuso criptográfico y los scripts de cracking.
Ejemplo de commit:
```bash
git add red-team/03_exploit_cookie_tampering.py red-team/05_hashcat_demo.sh
git commit -m "red(exploit): Fase VII - Cookie Tampering y cracking MD5 (A04:2025)"
git push origin version-vulnerable
```

---

## 📝 Fase 4: Flujo de Trabajo del BLUE TEAM (Rama `version-asegurada`)

Los miembros del Blue Team deben trabajar **SIEMPRE** sobre la rama `version-asegurada`.

```bash
# 1. Clonar el repositorio
git clone https://github.com/MDiSc/vulnapp.git
cd vulnapp

# 2. Configurar identidad Git
git config user.name "Tu Nombre"
git config user.email "tu.correo@ucab.edu.ve"

# 3. Cambiar a la rama asegurada
git checkout version-asegurada
git pull origin version-asegurada
```

### 4.1 — César Reyes: Sentencias Preparadas + Escape HTML
Modificará `secure/server.js` y `secure/public/index.html` (o los de la carpeta principal, dependiendo de la convención que tome el equipo azul para el arreglo).
```bash
git add .
git commit -m "fix(injection): Remediación CWE-89, CWE-79 y CWE-116"
git push origin version-asegurada
```

### 4.2 — Marco Cegarra: scrypt KDF + Verificación
Añadirá el uso de funciones robustas de derivación de claves.
```bash
git add server.js
git commit -m "fix(crypto): Remediación CWE-327/759/916 con scrypt KDF nativo"
git push origin version-asegurada
```

### 4.3 — Sebastián Cova: HMAC-SHA256 + Validación de cierre
Añadirá validación HMAC para cookies y la verificación de CVSS.
```bash
git add server.js docs/IMPACTO_CVSS.md red-team/06_verificacion_contramedidas.py
git commit -m "fix(crypto): HMAC-SHA256 (CWE-345/311) y análisis CVSS"
git push origin version-asegurada
```

---

## ✅ Checklist Final para la Entrega

- [ ] Repositorio con dos ramas exclusivas: `version-vulnerable` y `version-asegurada`.
- [ ] La rama `version-vulnerable` contiene TODOS los comentarios de riesgos técnicos (CWE) exigidos.
- [ ] Commits del Red Team subidos a `version-vulnerable`.
- [ ] Commits del Blue Team subidos a `version-asegurada`.
- [ ] No existen ramas adicionales ni fusiones (merges) directas con "main".
- [ ] Cada commit tiene prefijo de equipo (`red(...)` o `fix(...)`) y trazabilidad de identidad del integrante.
- [ ] El repositorio no versiona archivos basura (`.db`, `node_modules`).
