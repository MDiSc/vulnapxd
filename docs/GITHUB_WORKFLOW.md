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
✅ **Estado en Repositorio Oficial:** Commit parcial ya realizado (`red(exploit): Reconocimiento manual y SQLi`).

⚠️ **ACCIÓN REQUERIDA (Correcciones v8):**
Dado que el commit anterior se hizo con la versión antigua, Maurizio debe hacer un nuevo commit para:
1. Subir los archivos base de la aplicación vulnerable (frontend y backend) con los mecanismos de monitoreo nativo (Corrección #5).
2. Actualizar `01_reconocimiento.py` con la nueva terminología de CWE-311 (Corrección #1).

*(Nota: Los archivos de documentación finales como el `README.md` técnico y `PAYLOADS_REFERENCIA.txt` son entregables de la **Etapa 2**, por lo que no es necesario subirlos en esta fase).*

Ejemplo del commit de corrección que debe realizar:
```bash
git add vulnerable/ red-team/01_reconocimiento.py
git commit -m "red(correcciones-v8): Ajuste CWE-311 en reconocimiento y base vulnerable con monitoreo nativo"
git push origin version-vulnerable
```

### 3.2 — César Sánchez: XSS Worm + C2
✅ **Estado en Repositorio Oficial:** Commit ya realizado (`red(exploit): XSS Worm autorreplicante`).
**Nota:** El payload XSS no fue afectado por las correcciones v8. No necesita hacer commits de arreglo.

### 3.3 — Eduard Velasco: Cookie Tampering + Hashcat
⏳ **Estado:** Pendiente.
Debe agregar sus scripts asegurándose de tomar la **versión ya corregida (v8)** de `03_exploit_cookie_tampering.py` desde el repositorio borrador (`vulnapxd`), la cual prioriza la extracción de datos sobre la manipulación (Corrección #1).

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
