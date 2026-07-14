#!/usr/bin/env python3
"""
=============================================================================
VulnApp Red Team — Fase I: RECONOCIMIENTO
=============================================================================
Objetivo    : Enumerar endpoints de la API en el servidor víctima Ubuntu
              (192.168.56.20) usando peticiones HTTP manuales sin herramientas
              automáticas de escaneo.
OWASP       : A05:2025 Inyección / A04:2025 Fallas Criptográficas
Herramienta : Python 3 (urllib estándar) + análisis manual de cabeceras HTTP
Fase CKC    : I — Reconocimiento
Equipo      : Red Team (Maurizio Brazón, César Sánchez, Eduard Velasco)
=============================================================================
AVISO LEGAL: Solo para uso en laboratorio controlado. Prohibido en sistemas
             sin autorización explícita por escrito.
=============================================================================
"""

import urllib.request
import urllib.error
import json
import base64
import sys
import time

TARGET = "http://192.168.56.20:4000"

# Endpoints candidatos a probar (sin herramientas automáticas)
ENDPOINTS = [
    ("GET",  "/"),
    ("GET",  "/api/profile"),
    ("GET",  "/api/messages"),
    ("POST", "/api/login"),
    ("POST", "/api/register"),
    ("POST", "/api/search"),
    ("POST", "/api/message"),
    ("GET",  "/api/users/1"),
    ("GET",  "/api/users/2"),
    ("GET",  "/api/users/admin"),
]

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         VulnApp Red Team — FASE I: RECONOCIMIENTO            ║
║         Kill Chain Step 1 / 7                                ║
╚══════════════════════════════════════════════════════════════╝
"""

def probe_endpoint(method, path, body=None, headers=None, cookie=None):
    """Prueba un endpoint y devuelve código HTTP + cabeceras relevantes."""
    url = TARGET + path
    req_headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    if cookie:
        req_headers["Cookie"] = f"session={cookie}"
    if headers:
        req_headers.update(headers)

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw_body = resp.read(512).decode(errors='replace')
            return {
                "status": resp.status,
                "server": resp.getheader("Server", "—"),
                "x-powered-by": resp.getheader("X-Powered-By", "—"),
                "set-cookie": resp.getheader("Set-Cookie", "—"),
                "content-type": resp.getheader("Content-Type", "—"),
                "body_snippet": raw_body[:200],
            }
    except urllib.error.HTTPError as e:
        raw_body = e.read(256).decode(errors='replace')
        return {"status": e.code, "body_snippet": raw_body[:200]}
    except Exception as ex:
        return {"status": "ERROR", "body_snippet": str(ex)}


def analyze_cookie(set_cookie_header):
    """Decodifica y analiza la cookie de sesión devuelta por el servidor."""
    if not set_cookie_header or set_cookie_header == "—":
        return
    print("\n  [+] Cookie de sesión detectada:")
    print(f"      Raw: {set_cookie_header}")

    try:
        val = set_cookie_header.split("session=")[1].split(";")[0]
        decoded = base64.b64decode(val + "==").decode()
        print(f"      [FALLA DETECTADA] Base64 decodificado: {decoded}")
        print("      → Cookie en texto plano SIN firma HMAC (CWE-345, CWE-311)")
        try:
            obj = json.loads(decoded)
            print(f"      → Campos: {obj}")
            if "role" in obj:
                print(f"      → CAMPO 'role'={obj['role']} expuesto en texto plano — dato sensible legible sin criptografía (CWE-311)")
        except Exception:
            pass
    except Exception:
        print("      → No parece ser Base64 simple (podría tener firma HMAC — versión segura)")


def main():
    print(BANNER)
    print(f"[*] Target: {TARGET}")
    print(f"[*] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("[*] Iniciando reconocimiento manual de endpoints...\n")
    print(f"{'MÉTODO':<6}  {'ENDPOINT':<25}  {'STATUS':<7}  {'OBSERVACIONES'}")
    print("-" * 80)

    login_cookie = None

    for method, path in ENDPOINTS:
        # Payload mínimo para POST
        body = None
        if path == "/api/login":
            body = {"username": "alice", "password": "password1"}
        elif path == "/api/register":
            body = {"username": "testprobe", "password": "test123"}
        elif path == "/api/search":
            body = {"query": "alice"}
        elif path == "/api/message":
            body = {"receiverId": 1, "content": "probe"}

        result = probe_endpoint(method, path, body=body,
                                cookie=login_cookie)
        status = result["status"]

        obs = []
        if result.get("x-powered-by") and result["x-powered-by"] != "—":
            obs.append(f"X-Powered-By: {result['x-powered-by']}")
        if result.get("set-cookie") and result["set-cookie"] != "—":
            obs.append("Cookie emitida")
            if not login_cookie and path == "/api/login":
                try:
                    raw_val = result["set-cookie"].split("session=")[1].split(";")[0]
                    login_cookie = raw_val
                except Exception:
                    pass

        print(f"{method:<6}  {path:<25}  {str(status):<7}  {', '.join(obs) or '—'}")
        time.sleep(0.15)  # Delay manual — sin flood

        # Analizar cookie de login
        if path == "/api/login" and result.get("set-cookie"):
            analyze_cookie(result["set-cookie"])

    print("\n[*] Reconocimiento completado.")
    print("\n[HALLAZGOS]")
    print("  → Endpoints descubiertos: /api/login, /api/register, /api/search,")
    print("    /api/message, /api/messages, /api/profile, /api/users/:id")
    print("  → Tecnología backend: Node.js / Express (X-Powered-By: Express)")
    print("  → Gestión de sesión: Cookie Base64 sin firma HMAC → CWE-345, CWE-311")
    print("  → Posible superficie SQLi en: /api/login, /api/search, /api/users/:id")
    print("  → Posible Stored XSS en: /api/message (texto libre sin sanitizar)")
    print("\n→ Próxima fase: II Armamento (weaponize_payloads.py)\n")


if __name__ == "__main__":
    main()
