/**
 * VulnApp - Versión ASEGURADA (Blue Team)
 * ============================================================
 * Contramedidas implementadas (OWASP Top 10 2025 / NIST SP 800-160):
 *
 *  ID-1 — Inyección (A05:2025):
 *    ✅ CWE-89:  Sentencias preparadas (parametrización posicional) en TODOS los endpoints
 *    ✅ CWE-79:  Función de escape HTML manual para salida contextual
 *    ✅ CWE-116: textContent en lugar de innerHTML en el frontend
 *
 *  ID-2 — Fallas Criptográficas (A04:2025):
 *    ✅ CWE-327/916/759: scrypt (KDF) con salt CSPRNG de 16 bytes por usuario
 *    ✅ CWE-345/311: Cookie firmada con HMAC-SHA256 (formato: payload.firma)
 *                   Comparación con crypto.timingSafeEqual() para evitar Timing Attacks
 *
 * Todas las contramedidas usan exclusivamente módulos nativos de Node.js v20.
 * No se utilizan librerías externas de seguridad (sin JWT, sin bcrypt, sin Helmet).
 * ============================================================
 */

'use strict';

const express  = require('express');
const crypto   = require('crypto');
const path     = require('path');

// ─── Base de datos ─────────────────────────────────────────────────────────
const Database = require('better-sqlite3');
const db = new Database('./vulnapp_secure.db');

// ─── Constante HMAC: clave secreta del servidor (en prod. usar variable de entorno) ───
const HMAC_SECRET = process.env.HMAC_SECRET || crypto.randomBytes(32).toString('hex');

// ─── Inicialización del esquema ────────────────────────────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL DEFAULT 'user',
    email    TEXT
  );

  CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id   INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content     TEXT    NOT NULL,
    created_at  TEXT    DEFAULT (datetime('now'))
  );
`);

// ─── Seed seguro con scrypt + salt ────────────────────────────────────────
// ✅ CONTRAMEDIDA CWE-327/759/916: scrypt como KDF, salt único por usuario
function hashPassword(plaintext) {
  const salt       = crypto.randomBytes(16).toString('hex');
  const derivedKey = crypto.scryptSync(plaintext, salt, 64).toString('hex');
  return `${salt}:${derivedKey}`;
}

function verifyPassword(plaintext, stored) {
  const [salt, storedKey] = stored.split(':');
  const derivedKey = crypto.scryptSync(plaintext, salt, 64).toString('hex');
  // ✅ timingSafeEqual evita Timing Attacks en la comparación
  const a = Buffer.from(derivedKey,  'hex');
  const b = Buffer.from(storedKey,   'hex');
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const seedUsers = [
  { username: 'admin',  password: 'admin123',   role: 'admin', email: 'admin@vulnapp.local' },
  { username: 'alice',  password: 'password1',  role: 'user',  email: 'alice@vulnapp.local' },
  { username: 'bob',    password: 'qwerty',     role: 'user',  email: 'bob@vulnapp.local'   },
  { username: 'carlos', password: 'carlos2024', role: 'user',  email: 'carlos@vulnapp.local'},
];

const insertUserStmt = db.prepare(`
  INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)
`);

for (const u of seedUsers) {
  insertUserStmt.run(u.username, hashPassword(u.password), u.role, u.email);
}

// ═══════════════════════════════════════════════════════════════════════════
// CONTRAMEDIDAS HMAC — Módulo de sesión segura
// CWE-345 / CWE-311: Firma criptográfica de las cookies de sesión
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Firma un payload JSON con HMAC-SHA256.
 * Formato de cookie resultante: BASE64(payload).FIRMA_HEX
 */
function signSession(payload) {
  const payloadB64 = Buffer.from(JSON.stringify(payload)).toString('base64');
  const signature  = crypto
    .createHmac('sha256', HMAC_SECRET)
    .update(payloadB64)
    .digest('hex');
  return `${payloadB64}.${signature}`;
}

/**
 * Verifica y decodifica una cookie de sesión firmada.
 * Rechaza cualquier cookie cuya firma no coincida (previene tampering).
 * Usa timingSafeEqual para prevenir Timing Attacks.
 */
function verifySession(cookieValue) {
  try {
    const dotIndex   = cookieValue.lastIndexOf('.');
    if (dotIndex === -1) return null;

    const payloadB64 = cookieValue.slice(0, dotIndex);
    const signature  = cookieValue.slice(dotIndex + 1);

    // Re-calcular la firma esperada con la clave secreta del servidor
    const expectedSig = crypto
      .createHmac('sha256', HMAC_SECRET)
      .update(payloadB64)
      .digest('hex');

    // ✅ Comparación en tiempo constante: previene Oracle de timing
    const sigBuf      = Buffer.from(signature,   'hex');
    const expectedBuf = Buffer.from(expectedSig, 'hex');

    if (sigBuf.length !== expectedBuf.length || !crypto.timingSafeEqual(sigBuf, expectedBuf)) {
      return null; // Firma inválida → rechazado
    }

    return JSON.parse(Buffer.from(payloadB64, 'base64').toString('utf8'));
  } catch {
    return null;
  }
}

function getSession(req) {
  const cookieHeader = req.headers['cookie'] || '';
  const match = cookieHeader.match(/session=([^;]+)/);
  if (!match) return null;
  return verifySession(decodeURIComponent(match[1]));
}

// ─── Middleware de autenticación ───────────────────────────────────────────
function requireAuth(req, res, next) {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: 'No autenticado o sesión inválida' });
  req.session = session;
  next();
}

function requireAdmin(req, res, next) {
  // ✅ Se verifica el rol consultando la BD, NO confiando en la cookie
  const userInDb = db.prepare('SELECT role FROM users WHERE id = ?').get(req.session.userId);
  if (!userInDb || userInDb.role !== 'admin') {
    return res.status(403).json({ error: 'Acceso restringido a administradores' });
  }
  next();
}

// ═══════════════════════════════════════════════════════════════════════════
// CONTRAMEDIDA XSS — Función de escape HTML contextual
// CWE-79 / CWE-116: Codificación de salida manual (sin frameworks)
// ═══════════════════════════════════════════════════════════════════════════
function escapeHtml(str) {
  if (typeof str !== 'string') return String(str);
  return str
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#x27;')
    .replace(/\//g, '&#x2F;');
}

// ─── Aplicación Express ────────────────────────────────────────────────────
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// ─── ENDPOINT: POST /api/register ─────────────────────────────────────────
// ✅ Sentencia preparada para verificar existencia
// ✅ scrypt + CSPRNG salt para almacenamiento seguro de contraseña
app.post('/api/register', (req, res) => {
  const { username, password, email } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Usuario y contraseña son obligatorios' });
  }

  // Validación de longitud básica
  if (username.length > 50 || password.length > 128) {
    return res.status(400).json({ error: 'Campos demasiado largos' });
  }

  // ✅ SENTENCIA PREPARADA — elimina CWE-89
  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) {
    return res.status(409).json({ error: 'El usuario ya existe' });
  }

  // ✅ KDF scrypt — elimina CWE-327, CWE-759, CWE-916
  const hashedPassword = hashPassword(password);

  db.prepare('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)').run(
    username, hashedPassword, email || '', 'user'
  );

  res.json({ message: 'Usuario registrado correctamente' });
});

// ─── ENDPOINT: POST /api/login ────────────────────────────────────────────
// ✅ Sentencia preparada (solo busca por username, verifica contraseña en Node.js)
// ✅ Cookie firmada con HMAC-SHA256 — elimina CWE-345, CWE-311
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Faltan credenciales' });
  }

  // ✅ SENTENCIA PREPARADA — CWE-89 eliminado
  const user = db.prepare(
    'SELECT id, username, role, email, password FROM users WHERE username = ?'
  ).get(username);

  // ✅ Verificación de contraseña scrypt con timingSafeEqual — CWE-327 eliminado
  if (!user || !verifyPassword(password, user.password)) {
    // Mensaje genérico: no revelamos si el usuario existe
    return res.status(401).json({ error: 'Credenciales inválidas' });
  }

  // ✅ Cookie firmada HMAC-SHA256 — CWE-345 eliminado
  const sessionCookie = signSession({ userId: user.id, username: user.username, role: user.role });

  res.setHeader('Set-Cookie', `session=${sessionCookie}; Path=/; HttpOnly; SameSite=Strict`);
  res.json({ message: 'Autenticado correctamente', role: user.role });
});

// ─── ENDPOINT: GET /api/profile ───────────────────────────────────────────
// ✅ Rol verificado contra la BD, no contra la cookie
app.get('/api/profile', requireAuth, (req, res) => {
  // ✅ Se consulta el rol en la BD para no confiar en el cookie
  const userInDb = db.prepare(
    'SELECT id, username, role, email FROM users WHERE id = ?'
  ).get(req.session.userId);

  if (!userInDb) return res.status(404).json({ error: 'Usuario no encontrado' });

  if (userInDb.role === 'admin') {
    // Admin ve lista de usuarios pero SIN los hashes de contraseñas
    const allUsers = db.prepare('SELECT id, username, role, email FROM users').all();
    return res.json({ admin: true, users: allUsers });
  }

  res.json({ user: userInDb });
});

// ─── ENDPOINT: GET /api/users/:id ─────────────────────────────────────────
// ✅ Sentencia preparada — CWE-89 eliminado
app.get('/api/users/:id', requireAuth, (req, res) => {
  const { id } = req.params;

  // Validar que sea un entero
  if (!/^\d+$/.test(id)) {
    return res.status(400).json({ error: 'ID inválido' });
  }

  // ✅ SENTENCIA PREPARADA — parámetro no puede inyectar código
  const user = db.prepare(
    'SELECT id, username, role, email FROM users WHERE id = ?'
  ).get(Number(id));

  if (!user) return res.status(404).json({ error: 'Usuario no encontrado' });
  res.json({ user });
});

// ─── ENDPOINT: POST /api/search ───────────────────────────────────────────
// ✅ Sentencia preparada con LIKE seguro — CWE-89 eliminado
app.post('/api/search', requireAuth, (req, res) => {
  const { query: searchTerm } = req.body;
  if (!searchTerm || typeof searchTerm !== 'string') {
    return res.status(400).json({ error: 'Término de búsqueda inválido' });
  }

  // ✅ SENTENCIA PREPARADA: el % se agrega en Node.js, no en la query
  const results = db.prepare(
    'SELECT id, username, email FROM users WHERE username LIKE ?'
  ).all(`%${searchTerm}%`);

  res.json({ results });
});

// ─── ENDPOINT: POST /api/message ──────────────────────────────────────────
// ✅ Contenido almacenado tal cual pero el frontend lo renderiza con textContent
app.post('/api/message', requireAuth, (req, res) => {
  const { receiverId, content } = req.body;

  if (!content || !receiverId) {
    return res.status(400).json({ error: 'Faltan campos' });
  }

  if (!/^\d+$/.test(String(receiverId))) {
    return res.status(400).json({ error: 'receiverId inválido' });
  }

  if (content.length > 2000) {
    return res.status(400).json({ error: 'Mensaje demasiado largo' });
  }

  // ✅ SENTENCIA PREPARADA
  db.prepare(
    'INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)'
  ).run(req.session.userId, Number(receiverId), content);

  res.json({ message: 'Mensaje enviado' });
});

// ─── ENDPOINT: GET /api/messages ──────────────────────────────────────────
// ✅ Sentencia preparada; el frontend aplicará escapeHtml o textContent
app.get('/api/messages', requireAuth, (req, res) => {
  const msgs = db.prepare(`
    SELECT m.id, m.content, m.created_at, u.username AS sender
    FROM messages m
    JOIN users u ON u.id = m.sender_id
    WHERE m.receiver_id = ?
    ORDER BY m.created_at DESC
  `).all(req.session.userId);

  // ✅ Sanitización de salida en el servidor también (defensa en profundidad)
  const safeMsgs = msgs.map(m => ({
    ...m,
    content: escapeHtml(m.content),
    sender:  escapeHtml(m.sender),
  }));

  res.json({ messages: safeMsgs });
});

// ─── Inicio del servidor ───────────────────────────────────────────────────
const PORT = process.env.PORT || 4000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[VulnApp SEGURA] Backend corriendo en http://0.0.0.0:${PORT}`);
  console.log('Contramedidas activas: scrypt KDF + HMAC-SHA256 + Sentencias Preparadas + Escape HTML');
});
