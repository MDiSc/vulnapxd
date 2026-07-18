#!/usr/bin/env bash
# =============================================================================
# VulnApp Blue Team — Monitoreo Pasivo y Análisis Post-Explotación
# =============================================================================
# Objetivo    : Demostrar Identificación Técnica Post-Explotación interactuando
#               nativamente con la base de datos (sqlite3) para evidenciar el
#               compromiso, según la Corrección #5 de las instrucciones.
# Fase CKC    : Monitoreo Defensivo
# Herramienta : sqlite3 CLI nativa
# =============================================================================

BANNER="
╔══════════════════════════════════════════════════════════════╗
║   VulnApp Blue Team — MONITOREO POST-EXPLOTACIÓN            ║
║   Evidencia de Compromiso en Base de Datos (SQLite3)         ║
╚══════════════════════════════════════════════════════════════╝
"
echo "$BANNER"

# Definir la ruta a la BD dependiendo desde dónde se ejecuta
if [ -f "../vulnerable/vulnapp.db" ]; then
    DB_PATH="../vulnerable/vulnapp.db"
elif [ -f "./vulnapp.db" ]; then
    DB_PATH="./vulnapp.db"
else
    echo "[!] No se encontró la base de datos vulnapp.db en el directorio actual ni en ../vulnerable"
    echo "[!] Ejecuta este script desde la carpeta del proyecto o asegúrate de que el servidor vulnerable fue arrancado."
    exit 1
fi

echo "[*] Base de datos objetivo encontrada en: $DB_PATH"
echo "[*] Ejecutando análisis forense sobre la base de datos..."
echo "─────────────────────────────────────────────────────────────────"

# Verificar si sqlite3 CLI está instalada
if ! command -v sqlite3 &> /dev/null; then
    echo "[!] La herramienta 'sqlite3' no está instalada en el sistema."
    echo "[!] Instálala usando: sudo apt-get install sqlite3"
    exit 1
fi

echo "[1] Buscando artefactos maliciosos en la tabla 'messages' (Evidencia XSS)"
echo "    Comando ejecutado: SELECT id, sender_id, receiver_id, content FROM messages WHERE content LIKE '%<script>%';"
echo ""

sqlite3 "$DB_PATH" -header -column "SELECT id, sender_id, receiver_id, content FROM messages WHERE content LIKE '%<script>%';" | sed 's/^/    /'

echo ""
echo "[2] Auditando los roles de usuario (Evidencia de manipulación o inyección)"
echo "    Comando ejecutado: SELECT id, username, role FROM users;"
echo ""

sqlite3 "$DB_PATH" -header -column "SELECT id, username, role FROM users;" | sed 's/^/    /'

echo ""
echo "─────────────────────────────────────────────────────────────────"
echo "CONCLUSIÓN DEL ANÁLISIS FORENSE:"
echo "Si los resultados de la consulta #1 devuelven registros con '<script>',"
echo "se confirma una intrusión exitosa mediante Stored XSS (CWE-79)."
echo "El Blue Team debe proceder a neutralizar la amenaza implementando"
echo "escape de caracteres HTML en la salida (textContent)."
echo "================================================================="
