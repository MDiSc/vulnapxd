# Análisis de Impacto — CVSS v4.0

## VulnApp — Cuantificación de Vulnerabilidades

**OWASP Top 10 2025 | NIST SP 800-160 | Common Vulnerability Scoring System v4.0**

---

## Pertinencia de las CWE Seleccionadas (OWASP Top 10)

| Categoría OWASP | CWE Mapeada | Justificación Oficial / Directriz |
|-----------------|-------------|-----------------------------------|
| **A05:2025 Inyección** | **CWE-89** (SQLi) | Reconocida por MITRE/OWASP como la debilidad fundacional de inyección en bases de datos. |
| **A05:2025 Inyección** | **CWE-79** (XSS) | Mapeada clásicamente bajo Inyección debido a la inyección de código cliente. |
| **A04:2025 Fallas Criptográficas** | **CWE-327** (Algoritmo Roto) | Asociada al uso de MD5, el cual es considerado obsoleto y criptográficamente roto. |
| **A04:2025 Fallas Criptográficas** | **CWE-916** (Esfuerzo Insuficiente) | MD5 es excesivamente rápido para contraseñas, permitiendo ataques de fuerza bruta viables. |
| **A04:2025 Fallas Criptográficas** | **CWE-759** (Hash sin Salt) | Falta de un valor aleatorio (salt) hace que los hashes sean vulnerables a rainbow tables. |
| **A04:2025 Fallas Criptográficas** | **CWE-345/311** (Falta Autenticidad) | Falta de HMAC en las cookies permite manipulación de datos sensibles no encriptados. |

---

## Vulnerabilidad 1: SQL Injection (CWE-89)

**OWASP:** A05:2025 Inyección  
**Endpoint afectado:** POST /api/login, POST /api/search, GET /api/users/:id

### Vector CVSS v4.0

```
CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N
```

| Métrica Base              | Valor | Justificación |
|---------------------------|-------|---------------|
| Attack Vector (AV)        | N (Network) | El atacante accede via HTTP desde la red |
| Attack Complexity (AC)    | L (Low) | No requiere condiciones especiales |
| Attack Requirements (AT)  | N (None) | Sin prerrequisitos del entorno víctima |
| Privileges Required (PR)  | N (None) | /api/login no requiere autenticación |
| User Interaction (UI)     | N (None) | El ataque es completamente automatizable |
| Confidentiality (VC)      | H (High) | Extracción íntegra de la BD (usuarios, hashes) |
| Integrity (VI)            | H (High) | Posibilidad de modificar datos de BD |
| Availability (VA)         | H (High) | Posibilidad de borrar toda la BD |

**CVSS Score: 9.3 — CRÍTICO**

### Impacto Técnico

- **Confidencialidad:** Extracción completa de la tabla `users` incluyendo hashes de contraseñas MD5. Exfiltración del esquema completo vía `sqlite_master`.
- **Integridad:** Un atacante autenticado puede modificar o eliminar registros en la BD.
- **Disponibilidad:** Inyección de `DROP TABLE users` destruiría el sistema.

### Impacto de Negocio

- Exposición de PII (emails, usernames) → riesgo de cumplimiento GDPR/LOPD
- Credential stuffing: contraseñas MD5 descifradas se usan en otros servicios
- Pérdida total de confianza del usuario

---

## Vulnerabilidad 2: Stored XSS / Gusano Autorreplicante (CWE-79, CWE-116)

**OWASP:** A05:2025 Inyección  
**Endpoint afectado:** POST /api/message → GET /api/messages (renderizado)

### Vector CVSS v4.0

```
CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N
```

| Métrica Base              | Valor | Justificación |
|---------------------------|-------|---------------|
| Attack Vector (AV)        | N (Network) | Entrega via HTTP |
| Attack Complexity (AC)    | L (Low) | No requiere condiciones especiales |
| Privileges Required (PR)  | L (Low) | Requiere una cuenta de usuario |
| User Interaction (UI)     | P (Passive) | La víctima debe abrir su bandeja de entrada |
| Confidentiality (VC)      | H (High) | Exfiltración de cookies de sesión (secuestro) |
| Integrity (VI)            | H (High) | Acciones en nombre de la víctima |

**CVSS Score: 8.2 — ALTO**

### Impacto Técnico

- **C2 activo:** El Worm exfiltra cookies de todos los usuarios que abran mensajes
- **Persistencia:** El payload permanece en la BD hasta que se sanitice
- **Propagación viral:** El Worm se reenvía automáticamente a todos los usuarios

---

## Vulnerabilidad 3: MD5 sin Salt (CWE-327, CWE-759, CWE-916)

**OWASP:** A04:2025 Fallas Criptográficas  
**Endpoint afectado:** POST /api/register (almacenamiento), POST /api/login (verificación)

### Vector CVSS v4.0

```
CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N
```

| Métrica Base              | Valor | Justificación |
|---------------------------|-------|---------------|
| Attack Vector (AV)        | N (Network) | Los hashes se extraen via SQLi (encadenado) |
| Attack Complexity (AC)    | H (High) | Requiere acceso previo a los hashes (via SQLi) |
| Confidentiality (VC)      | H (High) | Contraseñas en texto claro tras cracking offline |

**CVSS Score: 7.4 — ALTO**

> **Nota:** La severidad aumenta a **CRÍTICO** cuando se combina con la SQLi (encadenamiento de vulnerabilidades). El vector combinado permite extracción + cracking en una sola sesión.

### Por qué MD5 es insuficiente (CWE-916)

| Métrica                  | MD5           | scrypt (N=16384)    |
|--------------------------|---------------|---------------------|
| Diseñado para            | Integridad    | Almacenamiento seguro |
| Velocidad (GPU RTX 4090) | ~10B hash/s   | ~500 hash/s         |
| Tiempo para crackear 'admin123' | < 0.001s | > 100 años       |
| Vulnerable a Rainbow Tables | Sí (sin salt) | No (salt único)   |
| Resistencia a ASIC/FPGA  | No           | Sí (memory-hard)    |

---

## Vulnerabilidad 4: Cookie Base64 sin HMAC (CWE-345, CWE-311)

**OWASP:** A04:2025 Fallas Criptográficas  
**Nota sobre observación de la profesora:** Esta vulnerabilidad fue identificada como Fallas Criptográficas (A04:2025) y NO como Ruptura de Control de Acceso (A01:2025). El fallo estructural radica en la **ausencia de primitiva criptográfica** (HMAC), no en una lógica deficiente de control de acceso per se. El ataque se enfoca en que la cookie contiene información sensible en texto plano codificado en Base64. El atacante la decodifica para leer datos confidenciales o secuestrar la sesión de otro usuario modificando el `userId` (CWE-345/CWE-311), sin involucrar una escalada de privilegios a administrador, para no solapar con A01.

### Vector CVSS v4.0

```
CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N
```

**CVSS Score: 8.7 — ALTO**

### Por qué Base64 NO es seguridad (CWE-311)

Base64 es un esquema de **codificación de transporte** (RFC 4648), no un algoritmo de cifrado:
- Cualquier cliente puede decodificar con `atob()` o `base64 -d`
- Sin firma HMAC, no hay manera de detectar si el payload fue modificado
- El servidor no puede distinguir entre una cookie legítima y una adulterada

### Contramedida implementada (HMAC-SHA256)

```
Cookie legítima:  eyJ1c2VySWQiOjJ9.a3f8c2b1e4d5...  (payload.firma)
Cookie adulterada: eyJ1c2VySWQiOjJ9.FIRMA_INCORRECTA
                   → crypto.timingSafeEqual() = false → HTTP 401
```

---

## Tabla Comparativa de Impacto CIA

| Vulnerabilidad        | Confidencialidad | Integridad | Disponibilidad | Acción del atacante |
|-----------------------|-----------------|------------|----------------|---------------------|
| SQLi /api/login       | 🔴 Alta          | 🔴 Alta     | 🔴 Alta         | Bypass auth + exfil BD |
| SQLi /api/search      | 🔴 Alta          | 🟡 Media    | 🟢 Baja         | Extracción de hashes  |
| Stored XSS Worm       | 🔴 Alta          | 🔴 Alta     | 🟢 Baja         | Secuestro de sesiones |
| MD5 sin salt          | 🔴 Alta          | 🟢 Baja     | 🟢 Baja         | Cracking offline      |
| Cookie Base64         | 🔴 Alta          | 🔴 Alta     | 🟢 Baja         | Secuestro de sesiones     |
