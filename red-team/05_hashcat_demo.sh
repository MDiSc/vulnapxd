#!/usr/bin/env bash
# =============================================================================
# VulnApp Red Team — Fase VII: ACCIONES SOBRE OBJETIVOS — Hashcat MD5 Demo
# =============================================================================
# Objetivo    : Cracking offline de hashes MD5 sin salt extraídos de la BD
# OWASP       : A04:2025 Fallas Criptográficas
# CWE         : CWE-327 (Broken Cryptographic Algorithm)
#               CWE-759 (Use of One-Way Hash without Salt)
#               CWE-916 (Use of Password Hash with Insufficient Computational Effort)
# Fase CKC    : VII — Acciones sobre los Objetivos
# Herramienta : Hashcat (descifrado offline en Kali Linux)
# =============================================================================
# AVISO LEGAL: Solo para uso en laboratorio controlado.
# =============================================================================

set -e

BANNER="
╔══════════════════════════════════════════════════════════════╗
║   VulnApp Red Team — FASE VII: HASHCAT MD5 CRACKING         ║
║   CWE-327/759/916 | A04:2025 Fallas Criptográficas          ║
╚══════════════════════════════════════════════════════════════╝
"
echo "$BANNER"

# ── Hashes MD5 extraídos de la BD mediante SQLi (sin salt) ──────────────────
# Formato: un hash por línea (sin usuario — hashcat -m 0 solo necesita el hash)
HASHES_FILE="/tmp/vulnapp_hashes.txt"

cat > "$HASHES_FILE" << 'EOF'
0192023a7bbd73250516f069df18b500
7c6a180b36896a0a8c02787eeafb0e4c
d8578edf8458ce06fbc5bb76a58c5ca4
b0be8b15a4d3b7f94dc3dca5d7c9e46f
EOF

echo "[*] Hashes MD5 extraídos de la BD (sin salt):"
echo "    - 0192023a7bbd73250516f069df18b500  (admin123)"
echo "    - 7c6a180b36896a0a8c02787eeafb0e4c  (password1)"
echo "    - d8578edf8458ce06fbc5bb76a58c5ca4  (qwerty)"
echo "    - b0be8b15a4d3b7f94dc3dca5d7c9e46f  (carlos2024)"
echo ""

WORDLIST="/usr/share/wordlists/rockyou.txt"
OUTPUT_FILE="/tmp/vulnapp_cracked.txt"

# ── Verificar que Hashcat y rockyou están disponibles ───────────────────────
if ! command -v hashcat &>/dev/null; then
    echo "[!] Hashcat no encontrado. Instalar con: sudo apt install hashcat"
    echo "[*] Simulando resultado del ataque para fines demostrativos..."
    SIMULATE=1
else
    SIMULATE=0
fi

if [ "$SIMULATE" -eq 0 ] && [ ! -f "$WORDLIST" ]; then
    echo "[!] rockyou.txt no encontrado en $WORDLIST"
    echo "    Intentando descomprimir: sudo gunzip /usr/share/wordlists/rockyou.txt.gz"
    if [ -f "${WORDLIST}.gz" ]; then
        sudo gunzip "${WORDLIST}.gz" || true
    else
        SIMULATE=1
        echo "[*] Simulando resultado del ataque..."
    fi
fi

echo "═══════════════════════════════════════════════════════════════"
echo "[FASE VII] Ejecutando ataque de diccionario offline con Hashcat"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Modo    : -m 0 (MD5 puro)"
echo "  Ataque  : -a 0 (diccionario - rockyou.txt)"
echo "  Razón   : Sin salt → hashes deterministas → vulnerables a precomputación"
echo "  Con salt scrypt: este ataque sería computacionalmente inviable"
echo ""

if [ "$SIMULATE" -eq 0 ]; then
    echo "[*] Ejecutando: hashcat -m 0 -a 0 $HASHES_FILE $WORDLIST --show"
    echo ""
    
    # Ejecutar hashcat
    hashcat -m 0 -a 0 "$HASHES_FILE" "$WORDLIST" \
        --outfile "$OUTPUT_FILE" \
        --outfile-format 2 \
        --quiet \
        --status \
        2>/dev/null || true

    echo ""
    echo "[+] Resultados del cracking:"
    if [ -f "$OUTPUT_FILE" ]; then
        hashcat -m 0 "$HASHES_FILE" --show 2>/dev/null || cat "$OUTPUT_FILE"
    fi
else
    # ── Simulación para la demo (cuando Hashcat no está disponible) ──────────
    echo "[SIMULACIÓN] Resultados que produciría Hashcat con rockyou.txt:"
    echo ""
    echo "  0192023a7bbd73250516f069df18b500:admin123"
    echo "  7c6a180b36896a0a8c02787eeafb0e4c:password1"
    echo "  d8578edf8458ce06fbc5bb76a58c5ca4:qwerty"
    echo "  b0be8b15a4d3b7f94dc3dca5d7c9e46f:carlos2024"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "[ANÁLISIS DE IMPACTO — CWE-759, CWE-916]"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  POR QUÉ FUNCIONA (Fallas Criptográficas — A04:2025):"
echo ""
echo "  1. MD5 es una función de HASH de integridad, NO de almacenamiento"
echo "     de contraseñas. Fue diseñada para ser RÁPIDA (CWE-916)."
echo ""
echo "  2. Sin salt: usuarios con la misma contraseña tienen el MISMO hash."
echo "     Permite ataques con Rainbow Tables precomputadas (CWE-759)."
echo ""
echo "  3. MD5 está oficialmente roto (colisiones conocidas, CWE-327)."
echo "     Hardware moderno: ~10 BILLION hashes/seg con GPU."
echo ""
echo "  COMPARACIÓN — scrypt vs MD5 para cracking:"
echo "  ┌──────────────┬────────────────────────┬─────────────────────┐"
echo "  │ Algoritmo    │ Hashes/segundo (GPU)   │ Tiempo p/'password1'│"
echo "  ├──────────────┼────────────────────────┼─────────────────────┤"
echo "  │ MD5          │ ~10,000,000,000        │ < 0.001 segundos    │"
echo "  │ scrypt(N=16k)│ ~500                   │ > años              │"
echo "  └──────────────┴────────────────────────┴─────────────────────┘"
echo ""
echo "  IMPACTO (CID):"
echo "  → Confidencialidad: Credenciales de TODOS los usuarios comprometidas"
echo "  → Credential Stuffing: Si reutilizan contraseñas en otros servicios"
echo "  → Acceso admin: Contraseña 'admin123' descifrada en < 0.001 segundos"
echo ""
echo "[→] Acciones sobre Objetivos completadas. Ver: INFORME_IMPACTO.md"
echo ""
