#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════╗
║   POS Abarrotes v3  —  Punto de Venta e Inventario  ║
║   Tecnologías: Python · PySide6 · SQLite             ║
╚══════════════════════════════════════════════════════╝
Ejecutar:  python pos_abarrotes.py
Requiere:  pip install PySide6
"""

import sys
import sqlite3
import hashlib
import json
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QSpinBox, QDoubleSpinBox, QHeaderView,
    QComboBox, QGroupBox, QDialog, QFormLayout,
    QStatusBar, QDateEdit, QGridLayout, QDialogButtonBox,
    QPlainTextEdit,
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QMovie, QPixmap, QTransform

# ──────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────

DB_NAME = "abarrotes_pos.db"
BACKUP_DB_NAME = "abarrotes_pos_respaldo.db"
CODIGO_MANUAL_PREFIX = "MANUAL-"
APP_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
BUNDLED_APP_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR)).resolve()
PERRITO_ASSETS_DIR = APP_DIR / "assets"
if not PERRITO_ASSETS_DIR.exists():
    PERRITO_ASSETS_DIR = BUNDLED_APP_DIR / "assets"
PERRITO_FRAMES_DIR = PERRITO_ASSETS_DIR / "perrito_frames"
PERRITO_CONFIG_PATH = PERRITO_ASSETS_DIR / "perrito_config.json"
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# ── Mascota: frases por evento (agrega o edita libremente; también puedes
#    sobreescribirlas sin tocar el código en assets/perrito_config.json) ──
FRASES_PERRITO = {
    "login": [
        "¡Buen día, {nombre}!",
        "¡Hola {nombre}! A darle con todo",
        "¡Guau! Qué gusto verte, {nombre}",
        "Caja lista, ¡vamos {nombre}!",
    ],
    "venta": [
        "¡Venta guardada! 🎉",
        "¡Otra venta más, {nombre}!",
        "¡Ka-ching! Buen trabajo",
        "¡Eso! La caja va creciendo",
        "¡Vendido! Sigamos así",
    ],
    "apartado": [
        "¡Apartado registrado!",
        "Producto apartado con éxito",
        "El cliente ya tiene su apartado",
        "Apartado guardado, ¡bien hecho!",
    ],
    "abono": [
        "¡Abono recibido!",
        "El cliente va avanzando",
        "¡Cada abono cuenta!",
        "Abono guardado correctamente",
    ],
    "prestamo": [
        "¡Préstamo registrado!",
        "Anoté lo que se llevó el cliente",
        "Préstamo guardado, yo lo vigilo 👀",
        "¡Listo! Préstamo bajo control",
    ],
    "devolucion": [
        "¡Producto de vuelta al inventario!",
        "Devolución registrada",
        "¡Regresó la mercancía!",
        "Inventario actualizado",
    ],
    "corte": [
        "¡Corte de caja listo!",
        "Buen cierre, {nombre}",
        "Cuentas claras, ¡a descansar!",
        "¡Día completado! 🐾",
    ],
    "inactividad": [
        "¿Sigues ahí, {nombre}?",
        "Aquí espero, sin prisa",
        "Zzz... avísame si me necesitas",
        "Estiro las patitas mientras tanto",
    ],
    "casual": [
        "Vamos con todo, {nombre}",
        "Gran dia para vender",
        "Listo para escanear",
        "Cada ticket cuenta",
        "Buen trabajo, {nombre}",
        "Periquita va fuerte",
        "Escanea y seguimos",
        "Datos a salvo",
    ],
}

# ── Mascota: mapeo estado/evento → nombre del GIF (sin extensión) que se
#    busca dentro de assets/. Si el GIF no existe se usa la animación base
#    (caminando) y, en último caso, los frames PNG originales. Para integrar
#    GIFs nuevos basta copiarlos a assets/ y mapearlos aquí o en el JSON. ──
ANIMACIONES_PERRITO = {
    "caminando":   "caminando",
    "idle":        "idle_parado",
    "login":       "saludando",
    "venta":       "saltando",
    "apartado":    "saludando",
    "abono":       "saltando",
    "prestamo":    "saludando",
    "devolucion":  "girando_360",
    "corte":       "girando_360",
    "inactividad": "idle_parado",
    "festejo":     "saltando",
    "espera":      "idle_parado",
}

USUARIOS_INICIALES = [
    ("admin", "Administrador", "admin", "admin123"),
    ("vendedor", "Perfil de ventas", "vendedor", "venta123"),
    ("vendedor1", "Vendedor 1", "vendedor", "venta123"),
    ("vendedor2", "Vendedor 2", "vendedor", "venta456"),
    ("vendedor3", "Vendedor 3", "vendedor", "venta789"),
]

ESTILO = """
QMainWindow, QWidget, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background: #1e1e2e;
    border-radius: 0 4px 4px 4px;
}
QTabBar::tab {
    background: #313244;
    color: #cdd6f4;
    padding: 9px 22px;
    border: 1px solid #45475a;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    min-width: 150px;
}
QTabBar::tab:selected  { background: #89b4fa; color: #1e1e2e; font-weight: bold; }
QTabBar::tab:hover:!selected { background: #45475a; }
QTableWidget {
    background-color: #181825;
    alternate-background-color: #1e1e2e;
    gridline-color: #45475a;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 4px;
}
QTableWidget::item { padding: 4px 8px; }
QHeaderView::section {
    background-color: #313244;
    color: #89b4fa;
    padding: 6px 8px;
    border: none;
    border-right: 1px solid #45475a;
    font-weight: bold;
}
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    min-height: 28px;
}
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus,
QComboBox:focus, QDateEdit:focus { border: 1px solid #89b4fa; }
QLineEdit:disabled, QSpinBox:disabled { color: #6c7086; background-color: #252535; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button {
    background: #45475a; border: none; width: 18px;
}
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: none;
    border-radius: 4px;
    padding: 7px 16px;
    font-size: 13px;
    min-height: 32px;
}
QPushButton:hover    { background-color: #585b70; }
QPushButton:pressed  { background-color: #313244; }
QPushButton:disabled { background-color: #313244; color: #6c7086; }
QPushButton#btn_cobrar {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-size: 19px;
    font-weight: bold;
    min-height: 58px;
    border-radius: 8px;
}
QPushButton#btn_cobrar:hover { background-color: #94e2d5; }
QPushButton#btn_verde  { background-color: #89b4fa; color: #1e1e2e; font-weight: bold; }
QPushButton#btn_verde:hover  { background-color: #74c7ec; }
QPushButton#btn_rojo   { background-color: #f38ba8; color: #1e1e2e; }
QPushButton#btn_rojo:hover   { background-color: #eba0ac; }
QPushButton#btn_naranja { background-color: #fab387; color: #1e1e2e; }
QPushButton#btn_naranja:hover { background-color: #f9c284; }
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 6px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLabel#lbl_titulo {
    font-size: 22px;
    font-weight: bold;
    color: #89b4fa;
    padding-bottom: 4px;
}
QLabel#lbl_total {
    font-size: 38px;
    font-weight: bold;
    color: #a6e3a1;
}
QStatusBar {
    background-color: #313244;
    color: #a6adc8;
    font-size: 12px;
}
QScrollBar:vertical  { background: #1e1e2e; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #45475a; min-height: 20px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

# ──────────────────────────────────────────────────────────
# BASE DE DATOS
# ──────────────────────────────────────────────────────────

def conectar():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    return conn


def agregar_columna_si_falta(conn, tabla, columna, definicion):
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({tabla})")
    columnas = [fila[1] for fila in c.fetchall()]
    if columna not in columnas:
        c.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def hash_password(contrasena):
    return hashlib.sha256(contrasena.encode("utf-8")).hexdigest()


def crear_usuarios_iniciales(conn):
    c = conn.cursor()
    for usuario, nombre, rol, contrasena in USUARIOS_INICIALES:
        c.execute("""
            INSERT OR IGNORE INTO usuarios
                (usuario, nombre, rol, password_hash, activo, fecha_alta)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (
            usuario, nombre, rol, hash_password(contrasena),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))


def validar_login(usuario, contrasena):
    with conectar() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, usuario, nombre, rol, password_hash
            FROM usuarios
            WHERE usuario = ? AND activo = 1
        """, (usuario.strip(),))
        row = c.fetchone()

    if not row:
        return None

    uid, user, nombre, rol, password_hash = row
    if hash_password(contrasena) != password_hash:
        return None

    return {
        "id": uid,
        "usuario": user,
        "nombre": nombre,
        "rol": rol,
    }


def nombre_visible_usuario(usuario):
    if not usuario:
        return ""
    return (usuario.get("nombre_turno") or usuario.get("nombre") or usuario.get("usuario") or "").strip()


def iniciar_registro_sesion(usuario_id, fondo_inicial=0, vendedor_nombre=""):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO sesiones_usuario
                (usuario_id, inicio, fondo_inicial, vendedor_nombre, estado)
            VALUES (?, ?, ?, ?, 'ABIERTA')
        """, (usuario_id, fecha, fondo_inicial, vendedor_nombre))
        return c.lastrowid


def resumen_caja_sesion(sesion_id, cierre=None):
    cierre = cierre or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT s.usuario_id, s.inicio, COALESCE(s.fondo_inicial, 0),
                   COALESCE(NULLIF(s.vendedor_nombre, ''), u.nombre)
            FROM sesiones_usuario s
            JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.id = ?
        """, (sesion_id,))
        row = c.fetchone()

        if not row:
            return None

        usuario_id, inicio, fondo, nombre = row
        c.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN metodo_pago = 'Efectivo' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN metodo_pago = 'Tarjeta' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN metodo_pago = 'Transferencia' THEN total ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN metodo_pago = 'Otro' THEN total ELSE 0 END), 0),
                COUNT(*)
            FROM ventas
            WHERE sesion_id = ?
               OR (sesion_id IS NULL AND usuario_id = ? AND fecha >= ? AND fecha <= ?)
        """, (sesion_id, usuario_id, inicio, cierre))
        efectivo, tarjeta, transferencia, otro, num_ventas = c.fetchone()

        # Movimientos de dinero de apartados (anticipos y devoluciones)
        c.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'ABONO' AND metodo_pago = 'Efectivo'
                                  THEN monto ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN tipo = 'ABONO' AND metodo_pago <> 'Efectivo'
                                  THEN monto ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN tipo = 'DEVOLUCION' THEN monto ELSE 0 END), 0)
            FROM abonos_apartado
            WHERE sesion_id = ?
        """, (sesion_id,))
        anticipos_efectivo, anticipos_otros, devoluciones = c.fetchone()

    esperado = fondo + efectivo + anticipos_efectivo - devoluciones
    return {
        "usuario_id": usuario_id,
        "vendedor": nombre,
        "inicio": inicio,
        "cierre": cierre,
        "fondo": fondo,
        "efectivo": efectivo,
        "tarjeta": tarjeta,
        "transferencia": transferencia,
        "otro": otro,
        "anticipos_efectivo": anticipos_efectivo,
        "anticipos_otros": anticipos_otros,
        "devoluciones_anticipo": devoluciones,
        "num_ventas": num_ventas,
        "esperado": esperado,
    }


def cerrar_registro_sesion(sesion_id, efectivo_contado=None, diferencia=None, observaciones=""):
    if not sesion_id:
        return
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conn:
        conn.execute("""
            UPDATE sesiones_usuario
            SET fin = ?,
                efectivo_contado = ?,
                diferencia_efectivo = ?,
                observaciones = ?,
                corte_cerrado = 1,
                estado = 'CERRADA'
            WHERE id = ? AND estado = 'ABIERTA'
        """, (fecha, efectivo_contado, diferencia, observaciones, sesion_id))


def asegurar_base_guardada():
    with conectar() as conn:
        conn.commit()
        try:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
        except sqlite3.DatabaseError:
            pass
    try:
        with sqlite3.connect(DB_NAME) as origen:
            with sqlite3.connect(BACKUP_DB_NAME) as respaldo:
                origen.backup(respaldo)
    except sqlite3.DatabaseError:
        pass


def crear_tablas():
    with conectar() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario       TEXT UNIQUE NOT NULL,
                nombre        TEXT NOT NULL,
                rol           TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                activo        INTEGER DEFAULT 1,
                fecha_alta    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sesiones_usuario (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                inicio     TEXT NOT NULL,
                fin        TEXT,
                vendedor_nombre TEXT DEFAULT '',
                fondo_inicial REAL DEFAULT 0,
                efectivo_contado REAL,
                diferencia_efectivo REAL,
                observaciones TEXT DEFAULT '',
                corte_cerrado INTEGER DEFAULT 0,
                estado     TEXT DEFAULT 'ABIERTA',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS productos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras   TEXT    UNIQUE NOT NULL,
                nombre          TEXT    NOT NULL,
                categoria       TEXT    DEFAULT '',
                precio_compra   REAL    DEFAULT 0,
                precio_venta    REAL    NOT NULL,
                stock           INTEGER DEFAULT 0,
                stock_minimo    INTEGER DEFAULT 5,
                activo          INTEGER DEFAULT 1,
                fecha_alta      TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha             TEXT NOT NULL,
                total             REAL NOT NULL,
                metodo_pago       TEXT NOT NULL,
                efectivo_recibido REAL DEFAULT 0,
                usuario_id        INTEGER,
                sesion_id         INTEGER,
                vendedor_nombre   TEXT DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id        INTEGER NOT NULL,
                producto_id     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL,
                precio_unitario REAL    NOT NULL,
                costo_unitario  REAL    DEFAULT 0,
                subtotal        REAL    NOT NULL,
                costo_total     REAL    DEFAULT 0,
                FOREIGN KEY (venta_id)    REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id     INTEGER NOT NULL,
                tipo_movimiento TEXT    NOT NULL,
                cantidad        INTEGER NOT NULL,
                motivo          TEXT    DEFAULT '',
                fecha           TEXT    NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS historial_precios (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id             INTEGER NOT NULL,
                usuario_id              INTEGER,
                precio_compra_anterior  REAL DEFAULT 0,
                precio_compra_nuevo     REAL DEFAULT 0,
                precio_venta_anterior   REAL DEFAULT 0,
                precio_venta_nuevo      REAL DEFAULT 0,
                motivo                  TEXT DEFAULT '',
                fecha                   TEXT NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS proveedores (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT UNIQUE NOT NULL,
                telefono    TEXT DEFAULT '',
                notas       TEXT DEFAULT '',
                activo      INTEGER DEFAULT 1,
                fecha_alta  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS compras (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                proveedor_id INTEGER NOT NULL,
                usuario_id   INTEGER,
                fecha        TEXT NOT NULL,
                total        REAL DEFAULT 0,
                notas        TEXT DEFAULT '',
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalle_compras (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id       INTEGER NOT NULL,
                producto_id     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL,
                costo_unitario  REAL DEFAULT 0,
                precio_venta    REAL DEFAULT 0,
                subtotal        REAL DEFAULT 0,
                FOREIGN KEY (compra_id) REFERENCES compras(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS ticket_pendiente (
                usuario_id   INTEGER PRIMARY KEY,
                actualizado  TEXT NOT NULL,
                vendedor_nombre TEXT DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalle_ticket_pendiente (
                usuario_id      INTEGER NOT NULL,
                producto_id     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                costo_unitario  REAL DEFAULT 0,
                subtotal        REAL NOT NULL,
                PRIMARY KEY (usuario_id, producto_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS clientes (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre     TEXT NOT NULL,
                telefono   TEXT DEFAULT '',
                correo     TEXT DEFAULT '',
                activo     INTEGER DEFAULT 1,
                fecha_alta TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS apartados (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id      INTEGER NOT NULL,
                descripcion     TEXT DEFAULT '',
                monto_total     REAL NOT NULL,
                estado          TEXT DEFAULT 'ACTIVO',
                fecha_creacion  TEXT NOT NULL,
                fecha_cierre    TEXT,
                venta_id        INTEGER,
                usuario_id      INTEGER,
                sesion_id       INTEGER,
                vendedor_nombre TEXT DEFAULT '',
                notas           TEXT DEFAULT '',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS abonos_apartado (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                apartado_id     INTEGER NOT NULL,
                tipo            TEXT DEFAULT 'ABONO',
                monto           REAL NOT NULL,
                metodo_pago     TEXT DEFAULT 'Efectivo',
                fecha           TEXT NOT NULL,
                usuario_id      INTEGER,
                sesion_id       INTEGER,
                vendedor_nombre TEXT DEFAULT '',
                FOREIGN KEY (apartado_id) REFERENCES apartados(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS prestamos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id      INTEGER NOT NULL,
                fecha           TEXT NOT NULL,
                estado          TEXT DEFAULT 'ACTIVO',
                usuario_id      INTEGER,
                sesion_id       INTEGER,
                vendedor_nombre TEXT DEFAULT '',
                notas           TEXT DEFAULT '',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalle_prestamos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                prestamo_id     INTEGER NOT NULL,
                producto_id     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                costo_unitario  REAL DEFAULT 0,
                estado          TEXT DEFAULT 'PRESTADO',
                fecha_estado    TEXT,
                venta_id        INTEGER,
                FOREIGN KEY (prestamo_id) REFERENCES prestamos(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );
        """)
        agregar_columna_si_falta(conn, "detalle_ventas", "costo_unitario", "REAL DEFAULT 0")
        agregar_columna_si_falta(conn, "detalle_ventas", "costo_total", "REAL DEFAULT 0")
        agregar_columna_si_falta(conn, "ventas", "usuario_id", "INTEGER")
        agregar_columna_si_falta(conn, "ventas", "sesion_id", "INTEGER")
        agregar_columna_si_falta(conn, "ventas", "vendedor_nombre", "TEXT DEFAULT ''")
        agregar_columna_si_falta(conn, "sesiones_usuario", "vendedor_nombre", "TEXT DEFAULT ''")
        agregar_columna_si_falta(conn, "sesiones_usuario", "fondo_inicial", "REAL DEFAULT 0")
        agregar_columna_si_falta(conn, "sesiones_usuario", "efectivo_contado", "REAL")
        agregar_columna_si_falta(conn, "sesiones_usuario", "diferencia_efectivo", "REAL")
        agregar_columna_si_falta(conn, "sesiones_usuario", "observaciones", "TEXT DEFAULT ''")
        agregar_columna_si_falta(conn, "sesiones_usuario", "corte_cerrado", "INTEGER DEFAULT 0")
        agregar_columna_si_falta(conn, "ticket_pendiente", "vendedor_nombre", "TEXT DEFAULT ''")
        crear_usuarios_iniciales(conn)


def es_codigo_manual(codigo):
    return bool(codigo) and codigo.startswith(CODIGO_MANUAL_PREFIX)


def codigo_visible(codigo):
    return "Sin código" if es_codigo_manual(codigo) else codigo


def generar_codigo_manual():
    return CODIGO_MANUAL_PREFIX + datetime.now().strftime("%Y%m%d%H%M%S%f")


RE_TELEFONO = re.compile(r"^[0-9+()\-\s]{7,20}$")
RE_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def telefono_valido(telefono):
    """Teléfono opcional: vacío es válido; si se captura debe tener formato."""
    telefono = (telefono or "").strip()
    if not telefono:
        return True
    digitos = re.sub(r"\D", "", telefono)
    return bool(RE_TELEFONO.match(telefono)) and 7 <= len(digitos) <= 15


def correo_valido(correo):
    """Correo opcional: vacío es válido; si se captura debe tener formato."""
    correo = (correo or "").strip()
    if not correo:
        return True
    return bool(RE_CORREO.match(correo))


def obtener_o_crear_cliente(cursor, nombre, telefono="", correo="", fecha=None):
    """Reutiliza un cliente existente (mismo nombre y teléfono) o lo crea."""
    nombre = " ".join((nombre or "").split())
    telefono = (telefono or "").strip()
    correo = (correo or "").strip()
    fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT id, COALESCE(telefono, ''), COALESCE(correo, '')
        FROM clientes
        WHERE LOWER(nombre) = LOWER(?) AND activo = 1
        ORDER BY id DESC
    """, (nombre,))
    candidatos = cursor.fetchall()

    elegido = None
    if telefono:
        for fila in candidatos:
            if fila[1].strip() == telefono:
                elegido = fila
                break
    elif candidatos:
        elegido = candidatos[0]

    if elegido:
        cid, tel_actual, correo_actual = elegido
        if telefono and not tel_actual.strip():
            cursor.execute("UPDATE clientes SET telefono = ? WHERE id = ?",
                           (telefono, cid))
        if correo and not correo_actual.strip():
            cursor.execute("UPDATE clientes SET correo = ? WHERE id = ?",
                           (correo, cid))
        return cid

    cursor.execute("""
        INSERT INTO clientes (nombre, telefono, correo, fecha_alta)
        VALUES (?, ?, ?, ?)
    """, (nombre, telefono, correo, fecha))
    return cursor.lastrowid


def separar_fecha_hora(fecha_hora):
    try:
        dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M:%S")
    except (TypeError, ValueError):
        partes = (fecha_hora or "").split()
        fecha = partes[0] if partes else ""
        hora = partes[1] if len(partes) > 1 else ""
        return fecha, hora


class _CasillaSeleccionMixin:
    def _seleccionar_texto(self):
        QTimer.singleShot(0, self.lineEdit().selectAll)

    def _actualizar_texto_cero(self):
        self.setSpecialValueText(" " if self.minimum() == 0 else "")

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._seleccionar_texto()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._seleccionar_texto()

    def setRange(self, minimo, maximo):
        super().setRange(minimo, maximo)
        self._actualizar_texto_cero()

    def setMinimum(self, minimo):
        super().setMinimum(minimo)
        self._actualizar_texto_cero()


class CasillaEntero(_CasillaSeleccionMixin, QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._actualizar_texto_cero()


class CasillaMonto(_CasillaSeleccionMixin, QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._actualizar_texto_cero()


# ──────────────────────────────────────────────────────────
# DIÁLOGO — AJUSTE DE STOCK
# ──────────────────────────────────────────────────────────

class DialogoAjusteStock(QDialog):
    def __init__(self, nombre, stock_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ajustar stock — {nombre}")
        self.setMinimumWidth(380)
        lay = QFormLayout(self)
        lay.setSpacing(10)

        lay.addRow("Stock actual:", QLabel(f"<b>{stock_actual}</b> unidades"))

        self._combo = QComboBox()
        self._combo.addItems([
            "ENTRADA  (agregar unidades)",
            "SALIDA   (retirar unidades)",
            "AJUSTE   (establecer valor exacto)",
        ])
        lay.addRow("Tipo de movimiento:", self._combo)

        self._spin = CasillaEntero()
        self._spin.setRange(1, 999_999)
        lay.addRow("Cantidad:", self._spin)

        self._motivo = QLineEdit()
        self._motivo.setPlaceholderText("Ej: Compra proveedor, merma, conteo físico...")
        lay.addRow("Motivo:", self._motivo)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def resultado(self):
        txt = self._combo.currentText()
        if "ENTRADA" in txt:
            tipo = "ENTRADA"
        elif "SALIDA" in txt:
            tipo = "SALIDA"
        else:
            tipo = "AJUSTE"
        return {
            "tipo": tipo,
            "cantidad": self._spin.value(),
            "motivo": self._motivo.text().strip() or "Ajuste manual",
        }


# ──────────────────────────────────────────────────────────
# DIÁLOGO — CAMBIO DE PRECIOS
# ──────────────────────────────────────────────────────────

class DialogoCambioPrecio(QDialog):
    def __init__(self, nombre, compra_actual, venta_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Cambiar precios — {nombre}")
        self.setMinimumWidth(430)
        lay = QFormLayout(self)
        lay.setSpacing(10)

        lay.addRow("Producto:", QLabel(f"<b>{nombre}</b>"))
        lay.addRow("Compra actual:", QLabel(f"<b>${compra_actual:.2f}</b>"))
        lay.addRow("Venta actual:", QLabel(f"<b>${venta_actual:.2f}</b>"))

        self._spin_compra = CasillaMonto()
        self._spin_compra.setRange(0, 999_999)
        self._spin_compra.setPrefix("$")
        self._spin_compra.setDecimals(2)
        self._spin_compra.setValue(compra_actual)
        lay.addRow("Nuevo precio compra:", self._spin_compra)

        self._spin_venta = CasillaMonto()
        self._spin_venta.setRange(0, 999_999)
        self._spin_venta.setPrefix("$")
        self._spin_venta.setDecimals(2)
        self._spin_venta.setValue(venta_actual)
        lay.addRow("Nuevo precio venta:", self._spin_venta)

        self._motivo = QLineEdit()
        self._motivo.setPlaceholderText("Ej: Subió proveedor, promoción, ajuste de margen...")
        lay.addRow("Motivo:", self._motivo)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def resultado(self):
        return {
            "compra": self._spin_compra.value(),
            "venta": self._spin_venta.value(),
            "motivo": self._motivo.text().strip() or "Cambio manual de precio",
        }


class DialogoEntradaInventario(QDialog):
    def __init__(self, nombre, stock_actual, compra_actual, venta_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Añadir stock — {nombre}")
        self.setMinimumWidth(430)
        lay = QFormLayout(self)
        lay.setSpacing(10)

        lay.addRow("Producto:", QLabel(f"<b>{nombre}</b>"))
        lay.addRow("Stock actual:", QLabel(f"<b>{stock_actual}</b> unidades"))
        lay.addRow("Compra actual:", QLabel(f"<b>${compra_actual:.2f}</b>"))
        lay.addRow("Venta actual:", QLabel(f"<b>${venta_actual:.2f}</b>"))

        self._spin_cantidad = CasillaEntero()
        self._spin_cantidad.setRange(1, 999_999)
        lay.addRow("Cantidad a añadir:", self._spin_cantidad)

        self._spin_compra = CasillaMonto()
        self._spin_compra.setRange(0, 999_999)
        self._spin_compra.setPrefix("$")
        self._spin_compra.setDecimals(2)
        self._spin_compra.setValue(compra_actual)
        lay.addRow("Precio compra:", self._spin_compra)

        self._spin_venta = CasillaMonto()
        self._spin_venta.setRange(0, 999_999)
        self._spin_venta.setPrefix("$")
        self._spin_venta.setDecimals(2)
        self._spin_venta.setValue(venta_actual)
        lay.addRow("Precio venta:", self._spin_venta)

        self._motivo = QLineEdit()
        self._motivo.setPlaceholderText("Ej: Compra proveedor, surtido, reposición...")
        lay.addRow("Motivo:", self._motivo)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def resultado(self):
        return {
            "cantidad": self._spin_cantidad.value(),
            "compra": self._spin_compra.value(),
            "venta": self._spin_venta.value(),
            "motivo": self._motivo.text().strip() or "Entrada de inventario",
        }


class DialogoHistorialPrecios(QDialog):
    def __init__(self, producto_id, nombre, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historial de precios — {nombre}")
        self.resize(900, 430)
        lay = QVBoxLayout(self)

        info = QLabel(f"<b>{nombre}</b>")
        lay.addWidget(info)

        tabla = QTableWidget()
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "Fecha", "Usuario", "Compra antes", "Compra nueva",
            "Venta antes", "Venta nueva", "Margen nuevo", "Motivo",
        ])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT h.fecha, COALESCE(u.nombre, 'Sin usuario'),
                       h.precio_compra_anterior, h.precio_compra_nuevo,
                       h.precio_venta_anterior, h.precio_venta_nuevo,
                       h.motivo
                FROM historial_precios h
                LEFT JOIN usuarios u ON u.id = h.usuario_id
                WHERE h.producto_id = ?
                ORDER BY h.fecha DESC, h.id DESC
            """, (producto_id,))
            filas = c.fetchall()

        tabla.setRowCount(len(filas))
        for fila, (fecha, usuario, compra_ant, compra_nueva, venta_ant, venta_nueva, motivo) in enumerate(filas):
            margen = venta_nueva - compra_nueva
            valores = [
                fecha, usuario, f"${compra_ant:.2f}", f"${compra_nueva:.2f}",
                f"${venta_ant:.2f}", f"${venta_nueva:.2f}", f"${margen:.2f}", motivo,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(fila, col, cell)

        lay.addWidget(tabla)

        if not filas:
            lay.addWidget(QLabel("Este producto todavía no tiene cambios de precio registrados."))

        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignRight)


# ──────────────────────────────────────────────────────────
# DIÁLOGO — DETALLE DE VENTA
# ──────────────────────────────────────────────────────────

class DialogoDetalleVenta(QDialog):
    def __init__(self, venta_id, fecha, total, metodo, parent=None, vendedor=""):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Venta #{venta_id}")
        self.resize(780, 430)
        lay = QVBoxLayout(self)

        texto_vendedor = f"&nbsp;&nbsp;|&nbsp;&nbsp;Vendedor: <b>{vendedor}</b>" if vendedor else ""
        info = QLabel(
            f"<b>Venta #{venta_id}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"{fecha}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Método: <b>{metodo}</b>{texto_vendedor}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Total: <b>${total:.2f}</b>"
        )
        info.setWordWrap(True)
        lay.addWidget(info)

        tabla = QTableWidget()
        tabla.setColumnCount(7)
        tabla.setHorizontalHeaderLabels(
            ["Producto", "Código", "Cant.", "Precio Unit.", "Subtotal", "Costo", "Ganancia"]
        )
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT p.nombre, p.codigo_barras,
                       d.cantidad, d.precio_unitario, d.subtotal,
                       COALESCE(NULLIF(d.costo_unitario, 0), p.precio_compra, 0),
                       COALESCE(NULLIF(d.costo_total, 0), d.cantidad * COALESCE(p.precio_compra, 0), 0)
                FROM detalle_ventas d
                JOIN productos p ON d.producto_id = p.id
                WHERE d.venta_id = ?
                ORDER BY p.nombre
            """, (venta_id,))
            filas = c.fetchall()

        costo_venta = sum(fila[6] for fila in filas)
        ganancia_venta = total - costo_venta
        info.setText(
            f"<b>Venta #{venta_id}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"{fecha}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Método: <b>{metodo}</b>{texto_vendedor}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Venta: <b>${total:.2f}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Ganancia: <b>${ganancia_venta:.2f}</b>"
        )

        tabla.setRowCount(len(filas))
        for i, (nom, cod, cant, precio, sub, costo_unit, costo_total) in enumerate(filas):
            ganancia = sub - costo_total
            valores = [
                nom, codigo_visible(cod), str(cant), f"${precio:.2f}",
                f"${sub:.2f}", f"${costo_total:.2f}", f"${ganancia:.2f}",
            ]
            for j, v in enumerate(valores):
                cell = QTableWidgetItem(v)
                cell.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(i, j, cell)

        lay.addWidget(tabla)
        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignRight)


# ──────────────────────────────────────────────────────────
# DIÁLOGO — INICIO DE SESIÓN
# ──────────────────────────────────────────────────────────

class DialogoLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inicio de sesión — Tienda Periquita")
        self.setMinimumWidth(390)
        self.usuario_actual = None

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        titulo = QLabel("Tienda Periquita")
        titulo.setObjectName("lbl_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(titulo)

        subtitulo = QLabel("Ingresa con tu usuario y contraseña")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("color: #a6adc8;")
        lay.addWidget(subtitulo)

        form = QFormLayout()
        form.setSpacing(10)

        self._inp_usuario = QLineEdit()
        self._inp_usuario.setPlaceholderText("Ej: admin o vendedor")
        form.addRow("Usuario:", self._inp_usuario)

        self._inp_contrasena = QLineEdit()
        self._inp_contrasena.setEchoMode(QLineEdit.Password)
        self._inp_contrasena.setPlaceholderText("Contraseña")
        self._inp_contrasena.returnPressed.connect(self._intentar_login)
        form.addRow("Contraseña:", self._inp_contrasena)

        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("Entrar")
        btns.button(QDialogButtonBox.Cancel).setText("Salir")
        btns.accepted.connect(self._intentar_login)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        ayuda = QLabel(
            "Usuarios iniciales: admin/admin123 y vendedor/venta123. "
            "El nombre real del vendedor se pide al abrir caja."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #6c7086; font-size: 11px;")
        lay.addWidget(ayuda)

        self._inp_usuario.setFocus()

    def _intentar_login(self):
        usuario = self._inp_usuario.text().strip()
        contrasena = self._inp_contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Datos incompletos",
                                "Escribe usuario y contraseña.")
            return

        usuario_actual = validar_login(usuario, contrasena)
        if not usuario_actual:
            QMessageBox.warning(self, "Acceso denegado",
                                "Usuario o contraseña incorrectos.")
            self._inp_contrasena.clear()
            self._inp_contrasena.setFocus()
            return

        self.usuario_actual = usuario_actual
        self.accept()


class DialogoNombreVendedor(QDialog):
    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nombre del vendedor")
        self.setMinimumWidth(390)
        self._nombre = ""

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        titulo = QLabel("Vendedor en turno")
        titulo.setObjectName("lbl_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(titulo)

        ayuda = QLabel(
            "Escribe el nombre de quien atendera esta caja. "
            "Asi el administrador vera las ventas, cortes y KPIs por persona."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #a6adc8;")
        lay.addWidget(ayuda)

        form = QFormLayout()
        self._inp_nombre = QLineEdit()
        self._inp_nombre.setPlaceholderText("Ej: Ana, Luis, Mariana...")
        self._inp_nombre.returnPressed.connect(self._aceptar)
        form.addRow("Nombre:", self._inp_nombre)
        lay.addLayout(form)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Continuar")
        bts.button(QDialogButtonBox.Cancel).setText("Cancelar")
        bts.accepted.connect(self._aceptar)
        bts.rejected.connect(self.reject)
        lay.addWidget(bts)

        self._inp_nombre.setFocus()

    def _aceptar(self):
        nombre = self._inp_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Falta nombre",
                                "Escribe el nombre del vendedor en turno.")
            self._inp_nombre.setFocus()
            return
        self._nombre = " ".join(nombre.split())
        self.accept()

    def nombre(self):
        return self._nombre


class DialogoFondoInicial(QDialog):
    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fondo inicial de caja")
        self.setMinimumWidth(380)

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        titulo = QLabel(f"Apertura de caja — {nombre_visible_usuario(usuario_actual)}")
        titulo.setObjectName("lbl_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(titulo)

        form = QFormLayout()
        self._spin_fondo = CasillaMonto()
        self._spin_fondo.setRange(0, 999_999)
        self._spin_fondo.setPrefix("$")
        self._spin_fondo.setDecimals(2)
        self._spin_fondo.setSingleStep(50)
        form.addRow("Fondo inicial en efectivo:", self._spin_fondo)
        lay.addLayout(form)

        ayuda = QLabel(
            "Este monto se usará para calcular el efectivo esperado al cerrar caja."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #a6adc8; font-size: 12px;")
        lay.addWidget(ayuda)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Abrir caja")
        bts.button(QDialogButtonBox.Cancel).setText("Cancelar")
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addWidget(bts)

    def fondo(self):
        return self._spin_fondo.value()


class DialogoCierreCaja(QDialog):
    def __init__(self, resumen, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cierre de caja")
        self.setMinimumWidth(520)
        self._resumen = resumen

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        titulo = QLabel(f"Cierre de caja — {resumen['vendedor']}")
        titulo.setObjectName("lbl_titulo")
        titulo.setAlignment(Qt.AlignCenter)
        lay.addWidget(titulo)

        form = QFormLayout()
        form.addRow("Inicio:", QLabel(resumen["inicio"]))
        form.addRow("Cierre:", QLabel(resumen["cierre"]))
        form.addRow("Ventas realizadas:", QLabel(str(resumen["num_ventas"])))
        form.addRow("Fondo inicial:", QLabel(f"${resumen['fondo']:.2f}"))
        form.addRow("Vendido en efectivo:", QLabel(f"${resumen['efectivo']:.2f}"))
        form.addRow("Vendido con tarjeta:", QLabel(f"${resumen['tarjeta']:.2f}"))
        form.addRow("Vendido por transferencia:", QLabel(f"${resumen['transferencia']:.2f}"))
        form.addRow("Vendido otro método:", QLabel(f"${resumen['otro']:.2f}"))
        form.addRow("Anticipo de apartado (efectivo):",
                    QLabel(f"${resumen.get('anticipos_efectivo', 0):.2f}"))
        form.addRow("Anticipo de apartado (otros métodos):",
                    QLabel(f"${resumen.get('anticipos_otros', 0):.2f}"))
        form.addRow("Devoluciones de anticipo (efectivo):",
                    QLabel(f"-${resumen.get('devoluciones_anticipo', 0):.2f}"))
        form.addRow("Efectivo esperado:", QLabel(f"<b>${resumen['esperado']:.2f}</b>"))

        self._spin_contado = CasillaMonto()
        self._spin_contado.setRange(0, 9_999_999)
        self._spin_contado.setPrefix("$")
        self._spin_contado.setDecimals(2)
        self._spin_contado.setSingleStep(50)
        self._spin_contado.setValue(resumen["esperado"])
        self._spin_contado.valueChanged.connect(self._actualizar_diferencia)
        form.addRow("Efectivo contado:", self._spin_contado)

        self._lbl_diferencia = QLabel()
        form.addRow("Diferencia:", self._lbl_diferencia)
        lay.addLayout(form)

        lay.addWidget(QLabel("Observaciones del vendedor:"))
        self._observaciones = QPlainTextEdit()
        self._observaciones.setPlaceholderText(
            "Ej: faltante por cambio, pago pendiente, retiro de efectivo..."
        )
        self._observaciones.setMaximumHeight(90)
        lay.addWidget(self._observaciones)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Cerrar caja")
        bts.button(QDialogButtonBox.Cancel).setText("Regresar")
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addWidget(bts)

        self._actualizar_diferencia()

    def _actualizar_diferencia(self):
        diferencia = self._spin_contado.value() - self._resumen["esperado"]
        self._lbl_diferencia.setText(f"${diferencia:.2f}")
        color = "#a6e3a1" if diferencia == 0 else "#f38ba8"
        self._lbl_diferencia.setStyleSheet(
            f"font-size: 17px; font-weight: bold; color: {color};"
        )

    def resultado(self):
        contado = self._spin_contado.value()
        diferencia = contado - self._resumen["esperado"]
        return {
            "efectivo_contado": contado,
            "diferencia": diferencia,
            "observaciones": self._observaciones.toPlainText().strip(),
        }


class AsistentePerrito(QWidget):
    def __init__(self, parent=None, nombre_usuario=""):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._nombre_usuario = nombre_usuario.strip() or "equipo"

        self._frames = [
            QPixmap(str(p))
            for p in sorted(PERRITO_FRAMES_DIR.glob("frame_*.png"))
        ]
        self._frames = [p for p in self._frames if not p.isNull()]
        self._gifs = self._cargar_gifs()
        self._frases = {k: list(v) for k, v in FRASES_PERRITO.items()}
        self._animaciones = dict(ANIMACIONES_PERRITO)
        self._modo_animaciones = "aleatorio"
        self._animaciones_aleatorias = []
        self._ultimo_gif = ""
        self._aplicar_config_externa()

        self._tam = 82
        self._frame_idx = 0
        self._dx = 2
        self._x = 24
        self._y = 200
        self._bubble_ticks = 0
        self._ultima_frase = ""
        self._movie = None
        self._estado = ""
        self._ultima_actividad = datetime.now()
        self._aviso_inactividad = False

        self._img = QLabel(self)
        self._img.setFixedSize(self._tam, self._tam)
        self._img.setScaledContents(False)

        self._bubble = QLabel(self)
        self._bubble.setStyleSheet(
            "background: rgba(49, 50, 68, 230); color: #cdd6f4; "
            "border: 1px solid #89b4fa; border-radius: 6px; padding: 4px 8px;"
        )
        self._bubble.hide()

        self.setFixedSize(230, 112)

        self._timer_anim = QTimer(self)
        self._timer_anim.timeout.connect(self._siguiente_frame)
        self._timer_anim.start(230)

        self._timer_mov = QTimer(self)
        self._timer_mov.timeout.connect(self._mover)
        self._timer_mov.start(45)

        self._timer_mensaje = QTimer(self)
        self._timer_mensaje.timeout.connect(self._mensaje_casual)
        self._timer_mensaje.start(15000)

        self._timer_estado = QTimer(self)
        self._timer_estado.setSingleShot(True)
        self._timer_estado.timeout.connect(lambda: self._set_estado("caminando"))

        self._timer_inactividad = QTimer(self)
        self._timer_inactividad.timeout.connect(self._checar_inactividad)
        self._timer_inactividad.start(30000)

        self._set_estado("caminando")
        if self._movie is None:
            self._actualizar_frame()

    # ── carga de recursos y configuración ──────────────────

    def _cargar_gifs(self):
        """Detecta todos los GIFs dentro de assets/ (subcarpetas incluidas)."""
        gifs = {}
        try:
            if PERRITO_ASSETS_DIR.exists():
                for ruta in sorted(PERRITO_ASSETS_DIR.rglob("*.gif")):
                    gifs.setdefault(ruta.stem.lower(), ruta)
        except OSError:
            pass
        return gifs

    def _aplicar_config_externa(self):
        """Permite editar frases y mapeo de animaciones sin tocar el código."""
        try:
            if not PERRITO_CONFIG_PATH.exists():
                return
            datos = json.loads(PERRITO_CONFIG_PATH.read_text(encoding="utf-8"))
            modo = str(datos.get("modo_animaciones", self._modo_animaciones)).strip().lower()
            if modo in ("aleatorio", "random"):
                self._modo_animaciones = "aleatorio"
            elif modo in ("por_evento", "evento"):
                self._modo_animaciones = "por_evento"

            animaciones_aleatorias = datos.get("animaciones_aleatorias")
            if isinstance(animaciones_aleatorias, list):
                self._animaciones_aleatorias = [
                    Path(str(gif)).stem.lower()
                    for gif in animaciones_aleatorias
                    if str(gif).strip()
                ]

            for evento, frases in (datos.get("frases") or {}).items():
                if isinstance(frases, list) and frases:
                    self._frases[evento] = [str(f) for f in frases]
            for estado, gif in (datos.get("animaciones") or {}).items():
                if gif:
                    self._animaciones[estado] = Path(str(gif)).stem.lower()
        except (OSError, ValueError):
            pass

    # ── animaciones ────────────────────────────────────────

    def _nombres_animacion_aleatoria(self):
        candidatos = [
            nombre for nombre in self._animaciones_aleatorias
            if nombre in self._gifs
        ]
        if not candidatos:
            candidatos = sorted(self._gifs.keys())
        return candidatos

    def _ruta_animacion_aleatoria(self):
        candidatos = self._nombres_animacion_aleatoria()
        if not candidatos:
            return None
        opciones = [nombre for nombre in candidatos if nombre != self._ultimo_gif]
        elegido = random.choice(opciones or candidatos)
        self._ultimo_gif = elegido
        return self._gifs.get(elegido)

    def _ruta_animacion_por_evento(self, estado):
        nombre_gif = (self._animaciones.get(estado) or "").lower()
        ruta = self._gifs.get(nombre_gif)
        if ruta is None and estado != "caminando":
            ruta = self._gifs.get((self._animaciones.get("caminando") or "").lower())
        if ruta is not None:
            self._ultimo_gif = ruta.stem.lower()
        return ruta

    def _set_estado(self, estado, duracion_ms=0):
        if self._modo_animaciones == "aleatorio":
            ruta = self._ruta_animacion_aleatoria()
        else:
            ruta = self._ruta_animacion_por_evento(estado)

        if self._movie is not None:
            self._movie.stop()
            self._movie.deleteLater()
            self._movie = None

        if ruta is not None:
            movie = QMovie(str(ruta))
            if movie.isValid():
                movie.setCacheMode(QMovie.CacheAll)
                movie.frameChanged.connect(self._frame_gif)
                self._movie = movie
                movie.start()
            else:
                movie.deleteLater()

        self._estado = estado
        if self._movie is None:
            self._actualizar_frame()
        if duracion_ms > 0:
            self._timer_estado.start(duracion_ms)
        else:
            self._timer_estado.stop()

    def _frame_gif(self, *_args):
        if self._movie is None:
            return
        pix = self._movie.currentPixmap()
        if not pix.isNull():
            self._mostrar_pixmap(pix)

    def _mostrar_pixmap(self, pix):
        if self._dx < 0:
            pix = pix.transformed(QTransform().scale(-1, 1))
        pix = pix.scaled(
            self._tam, self._tam,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._img.setPixmap(pix)
        self._img.move(0, 28)

    def _actualizar_frame(self):
        if not self._frames:
            if self._movie is None and not self._gifs:
                self.hide()
            return
        self._mostrar_pixmap(self._frames[self._frame_idx % len(self._frames)])

    def _siguiente_frame(self):
        if self._movie is not None or not self._frames:
            return
        self._frame_idx = (self._frame_idx + 1) % len(self._frames)
        self._actualizar_frame()

    def _mover(self):
        parent = self.parent()
        if not parent:
            return
        max_x = max(0, parent.width() - self.width() - 20)
        target_y = max(80, parent.height() - self.height() - 58)
        self._y = int(self._y + (target_y - self._y) * 0.18)
        self._x += self._dx
        if self._x <= 10 or self._x >= max_x:
            self._dx *= -1
            self._x = max(10, min(self._x, max_x))
        self.move(int(self._x), int(self._y))
        self.raise_()

        if self._bubble_ticks > 0:
            self._bubble_ticks -= 1
            if self._bubble_ticks == 0:
                self._bubble.hide()

    # ── frases y eventos ───────────────────────────────────

    def _frase(self, evento):
        frases = self._frases.get(evento) or self._frases.get("casual") or []
        if not frases:
            return ""
        opciones = [f for f in frases if f != self._ultima_frase] or list(frases)
        frase = random.choice(opciones)
        self._ultima_frase = frase
        return frase

    def _mensaje_casual(self):
        frase = self._frase("casual")
        if frase:
            self.mostrar_mensaje(frase)
        self._set_estado("casual", 4500)

    def evento(self, nombre):
        """Reacciona a un evento del sistema: frase contextual + animación."""
        frase = self._frase(nombre)
        if frase:
            self.mostrar_mensaje(frase)
        self._set_estado(nombre, 4500)
        if nombre != "inactividad":
            self._ultima_actividad = datetime.now()
            self._aviso_inactividad = False

    def _checar_inactividad(self):
        if self._aviso_inactividad:
            return
        segundos = (datetime.now() - self._ultima_actividad).total_seconds()
        if segundos >= 240:
            self._aviso_inactividad = True
            self.evento("inactividad")

    def mostrar_mensaje(self, texto):
        self._bubble.setText(texto.replace("{nombre}", self._nombre_usuario))
        self._bubble.adjustSize()
        self._bubble.move(72, 8)
        self._bubble.show()
        self._bubble_ticks = 90


# ──────────────────────────────────────────────────────────
# DIÁLOGOS — APARTADOS
# ──────────────────────────────────────────────────────────

class DialogoAbonoApartado(QDialog):
    def __init__(self, cliente, saldo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Abonar al apartado — {cliente}")
        self.setMinimumWidth(420)
        self._saldo = saldo

        lay = QFormLayout(self)
        lay.setSpacing(10)
        lay.addRow("Cliente:", QLabel(f"<b>{cliente}</b>"))
        lay.addRow("Saldo restante:", QLabel(f"<b>${saldo:.2f}</b>"))

        self._spin_monto = CasillaMonto()
        self._spin_monto.setRange(0, saldo)
        self._spin_monto.setPrefix("$")
        self._spin_monto.setDecimals(2)
        self._spin_monto.setSingleStep(10)
        lay.addRow("Monto del abono:", self._spin_monto)

        self._combo_metodo = QComboBox()
        self._combo_metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])
        lay.addRow("Método de pago:", self._combo_metodo)

        ayuda = QLabel("El abono no puede ser mayor al saldo restante.")
        ayuda.setStyleSheet("color: #a6adc8; font-size: 11px;")
        lay.addRow(ayuda)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Registrar abono")
        bts.accepted.connect(self._validar)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def _validar(self):
        if self._spin_monto.value() <= 0:
            QMessageBox.warning(self, "Monto inválido",
                                "El abono debe ser mayor a $0.00.")
            return
        self.accept()

    def resultado(self):
        return {
            "monto": self._spin_monto.value(),
            "metodo": self._combo_metodo.currentText(),
        }


class DialogoLiquidarApartado(QDialog):
    def __init__(self, cliente, monto_total, saldo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Liquidar apartado — {cliente}")
        self.setMinimumWidth(460)
        self._saldo = saldo

        lay = QFormLayout(self)
        lay.setSpacing(10)
        lay.addRow("Cliente:", QLabel(f"<b>{cliente}</b>"))
        lay.addRow("Monto del apartado:", QLabel(f"<b>${monto_total:.2f}</b>"))
        lay.addRow("Saldo restante:", QLabel(f"<b>${saldo:.2f}</b>"))

        self._combo_metodo = QComboBox()
        self._combo_metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])
        if saldo > 0:
            aviso = QLabel(
                f"Se cobrará el saldo restante de <b>${saldo:.2f}</b> como último "
                f"abono y el apartado se registrará como venta liquidada."
            )
            aviso.setWordWrap(True)
            lay.addRow(aviso)
            lay.addRow("Método del último pago:", self._combo_metodo)
        else:
            aviso = QLabel(
                "El apartado ya está pagado por completo. "
                "Se registrará como venta liquidada."
            )
            aviso.setWordWrap(True)
            lay.addRow(aviso)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Liquidar y convertir en venta")
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def metodo(self):
        return self._combo_metodo.currentText()


class DialogoCancelarApartado(QDialog):
    def __init__(self, cliente, abonado, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Cancelar apartado — {cliente}")
        self.setMinimumWidth(480)
        self._abonado = abonado

        lay = QFormLayout(self)
        lay.setSpacing(10)
        lay.addRow("Cliente:", QLabel(f"<b>{cliente}</b>"))
        lay.addRow("Anticipos recibidos:", QLabel(f"<b>${abonado:.2f}</b>"))

        self._combo_devolver = QComboBox()
        if abonado > 0:
            self._combo_devolver.addItem(
                f"Devolver ${abonado:.2f} en efectivo al cliente", True)
            self._combo_devolver.addItem(
                "No devolver (la tienda conserva el anticipo)", False)
            lay.addRow("Anticipo:", self._combo_devolver)
        else:
            lay.addRow(QLabel("Este apartado no tiene anticipos registrados."))

        self._inp_motivo = QLineEdit()
        self._inp_motivo.setPlaceholderText("Ej: el cliente ya no quiso el producto...")
        lay.addRow("Motivo:", self._inp_motivo)

        ayuda = QLabel(
            "La devolución en efectivo se descuenta del corte de caja "
            "de la sesión actual."
        )
        ayuda.setWordWrap(True)
        ayuda.setStyleSheet("color: #a6adc8; font-size: 11px;")
        lay.addRow(ayuda)

        bts = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bts.button(QDialogButtonBox.Ok).setText("Cancelar apartado")
        bts.button(QDialogButtonBox.Cancel).setText("Regresar")
        bts.accepted.connect(self.accept)
        bts.rejected.connect(self.reject)
        lay.addRow(bts)

    def resultado(self):
        devolver = bool(self._combo_devolver.currentData()) if self._abonado > 0 else False
        return {
            "devolver": devolver,
            "motivo": self._inp_motivo.text().strip() or "Cancelación de apartado",
        }


class DialogoAbonosApartado(QDialog):
    def __init__(self, apartado_id, cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Abonos del apartado #{apartado_id} — {cliente}")
        self.resize(720, 400)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"<b>{cliente}</b> — Apartado #{apartado_id}"))

        tabla = QTableWidget()
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderLabels(
            ["Fecha", "Tipo", "Monto", "Método", "Vendedor"]
        )
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT fecha, tipo, monto, metodo_pago,
                       COALESCE(NULLIF(vendedor_nombre, ''), 'Sin registro')
                FROM abonos_apartado
                WHERE apartado_id = ?
                ORDER BY fecha ASC, id ASC
            """, (apartado_id,))
            filas = c.fetchall()

        tabla.setRowCount(len(filas))
        for fila, (fecha, tipo, monto, metodo, vendedor) in enumerate(filas):
            tipo_txt = "Anticipo de apartado" if tipo == "ABONO" else "Devolución de anticipo"
            monto_txt = f"${monto:.2f}" if tipo == "ABONO" else f"-${monto:.2f}"
            for col, val in enumerate([fecha, tipo_txt, monto_txt, metodo, vendedor]):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if tipo != "ABONO":
                    cell.setForeground(QColor("#f38ba8"))
                tabla.setItem(fila, col, cell)
        lay.addWidget(tabla)

        if not filas:
            lay.addWidget(QLabel("Este apartado todavía no tiene abonos registrados."))

        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignRight)


# ──────────────────────────────────────────────────────────
# DIÁLOGO — DETALLE DE PRÉSTAMO
# ──────────────────────────────────────────────────────────

class DialogoDetallePrestamo(QDialog):
    """Detalle de un préstamo: devolver artículos o cobrarlos como venta."""

    def __init__(self, prestamo_id, contexto, parent=None):
        super().__init__(parent)
        self._prestamo_id = prestamo_id
        self._ctx = contexto       # usuario_id, sesion_id, vendedor
        self.cambios = False
        self.hubo_devolucion = False
        self.hubo_cobro = False

        self.setWindowTitle(f"Detalle de préstamo #{prestamo_id}")
        self.resize(860, 480)
        lay = QVBoxLayout(self)

        self._lbl_info = QLabel()
        self._lbl_info.setWordWrap(True)
        lay.addWidget(self._lbl_info)

        self._tabla = QTableWidget()
        self._tabla.setColumnCount(8)
        self._tabla.setHorizontalHeaderLabels([
            "ID", "Producto", "Código", "Cant.", "Precio Unit.",
            "Subtotal", "Estado", "Fecha estado",
        ])
        self._tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla.setAlternatingRowColors(True)
        self._tabla.hideColumn(0)
        lay.addWidget(self._tabla)

        hl = QHBoxLayout()
        btn_devolver = QPushButton("📦  Devolver seleccionado")
        btn_devolver.setObjectName("btn_naranja")
        btn_devolver.clicked.connect(self._devolver_seleccionado)

        btn_cobrar = QPushButton("💰  Cobrar seleccionado")
        btn_cobrar.setObjectName("btn_verde")
        btn_cobrar.clicked.connect(lambda: self._cobrar(todos=False))

        btn_cobrar_todo = QPushButton("💰  Cobrar todo lo prestado")
        btn_cobrar_todo.setObjectName("btn_verde")
        btn_cobrar_todo.clicked.connect(lambda: self._cobrar(todos=True))

        self._combo_metodo = QComboBox()
        self._combo_metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)

        hl.addWidget(btn_devolver)
        hl.addWidget(btn_cobrar)
        hl.addWidget(btn_cobrar_todo)
        hl.addWidget(QLabel("Método de cobro:"))
        hl.addWidget(self._combo_metodo)
        hl.addStretch()
        hl.addWidget(btn_cerrar)
        lay.addLayout(hl)

        hint = QLabel(
            "💡  Devolver reintegra el producto al inventario. "
            "Cobrar convierte los artículos en una venta normal."
        )
        hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        lay.addWidget(hint)

        self._cargar()

    def _cargar(self):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT cl.nombre, COALESCE(cl.telefono, ''), p.fecha, p.estado,
                       COALESCE(NULLIF(p.vendedor_nombre, ''), 'Sin registro')
                FROM prestamos p
                JOIN clientes cl ON cl.id = p.cliente_id
                WHERE p.id = ?
            """, (self._prestamo_id,))
            cab = c.fetchone()

            c.execute("""
                SELECT d.id, pr.nombre, pr.codigo_barras, d.cantidad,
                       d.precio_unitario, d.estado, COALESCE(d.fecha_estado, '')
                FROM detalle_prestamos d
                JOIN productos pr ON pr.id = d.producto_id
                WHERE d.prestamo_id = ?
                ORDER BY d.id
            """, (self._prestamo_id,))
            filas = c.fetchall()

        if cab:
            nombre, telefono, fecha, estado, vendedor = cab
            tel_txt = f"&nbsp;&nbsp;|&nbsp;&nbsp;Tel: <b>{telefono}</b>" if telefono else ""
            pendiente = sum(
                cant * precio for _d, _n, _c, cant, precio, est, _f in filas
                if est == "PRESTADO"
            )
            self._lbl_info.setText(
                f"<b>Préstamo #{self._prestamo_id}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"Cliente: <b>{nombre}</b>{tel_txt}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"Fecha: {fecha}&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"Estado: <b>{estado}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"Vendedor: <b>{vendedor}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
                f"Pendiente: <b>${pendiente:.2f}</b>"
            )

        colores = {
            "PRESTADO": QColor("#f9e2af"),
            "DEVUELTO": QColor("#a6e3a1"),
            "COBRADO": QColor("#89b4fa"),
        }
        self._tabla.setRowCount(len(filas))
        for fila, (did, nombre, codigo, cant, precio, estado, fecha_e) in enumerate(filas):
            valores = [
                str(did), nombre, codigo_visible(codigo), str(cant),
                f"${precio:.2f}", f"${cant * precio:.2f}", estado, fecha_e,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if col == 6 and estado in colores:
                    cell.setForeground(QColor("#1e1e2e"))
                    cell.setBackground(colores[estado])
                self._tabla.setItem(fila, col, cell)

    def _detalle_seleccionado(self):
        fila = self._tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un artículo del préstamo.")
            return None
        return int(self._tabla.item(fila, 0).text())

    def _items_prestados(self, solo_detalle_id=None):
        with conectar() as conn:
            c = conn.cursor()
            sql = """
                SELECT id, producto_id, cantidad, precio_unitario, costo_unitario
                FROM detalle_prestamos
                WHERE prestamo_id = ? AND estado = 'PRESTADO'
            """
            params = [self._prestamo_id]
            if solo_detalle_id is not None:
                sql += " AND id = ?"
                params.append(solo_detalle_id)
            c.execute(sql, params)
            return c.fetchall()

    def _actualizar_estado_prestamo(self, cursor):
        cursor.execute("""
            SELECT COUNT(*) FROM detalle_prestamos
            WHERE prestamo_id = ? AND estado = 'PRESTADO'
        """, (self._prestamo_id,))
        pendientes = cursor.fetchone()[0]
        cursor.execute(
            "UPDATE prestamos SET estado = ? WHERE id = ?",
            ("ACTIVO" if pendientes else "CERRADO", self._prestamo_id),
        )

    def _devolver_seleccionado(self):
        did = self._detalle_seleccionado()
        if did is None:
            return
        items = self._items_prestados(solo_detalle_id=did)
        if not items:
            QMessageBox.warning(self, "No disponible",
                                "Ese artículo ya fue devuelto o cobrado.")
            return

        _did, producto_id, cantidad, _precio, _costo = items[0]
        r = QMessageBox.question(
            self, "Devolver artículo",
            f"¿Registrar la devolución de {cantidad} unidad(es)?\n\n"
            f"El producto se reintegrará al inventario.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r != QMessageBox.Yes:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE detalle_prestamos
                SET estado = 'DEVUELTO', fecha_estado = ?
                WHERE id = ? AND estado = 'PRESTADO'
            """, (fecha, did))
            c.execute("UPDATE productos SET stock = stock + ? WHERE id = ?",
                      (cantidad, producto_id))
            c.execute("""
                INSERT INTO movimientos_inventario
                    (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                VALUES (?, 'ENTRADA', ?, ?, ?)
            """, (producto_id, cantidad,
                  f"Devolución préstamo #{self._prestamo_id}", fecha))
            self._actualizar_estado_prestamo(c)

        asegurar_base_guardada()
        self.cambios = True
        self.hubo_devolucion = True
        self._cargar()

    def _cobrar(self, todos=False):
        if todos:
            items = self._items_prestados()
        else:
            did = self._detalle_seleccionado()
            if did is None:
                return
            items = self._items_prestados(solo_detalle_id=did)

        if not items:
            QMessageBox.warning(self, "Nada por cobrar",
                                "No hay artículos prestados pendientes de cobro.")
            return

        total = sum(cant * precio for _d, _p, cant, precio, _c in items)
        metodo = self._combo_metodo.currentText()
        r = QMessageBox.question(
            self, "Cobrar préstamo",
            f"Se cobrarán {len(items)} artículo(s) por un total de ${total:.2f} "
            f"({metodo}).\n\nLos artículos se convertirán en una venta. ¿Continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r != QMessageBox.Yes:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO ventas
                    (fecha, total, metodo_pago, efectivo_recibido,
                     usuario_id, sesion_id, vendedor_nombre)
                VALUES (?, ?, ?, 0, ?, ?, ?)
            """, (
                fecha, total, metodo, self._ctx["usuario_id"],
                self._ctx["sesion_id"], self._ctx["vendedor"],
            ))
            vid = c.lastrowid

            for did, producto_id, cantidad, precio, costo in items:
                costo = costo or 0
                c.execute("""
                    INSERT INTO detalle_ventas
                        (venta_id, producto_id, cantidad, precio_unitario,
                         costo_unitario, subtotal, costo_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    vid, producto_id, cantidad, precio,
                    costo, cantidad * precio, costo * cantidad,
                ))
                # El stock ya se descontó al prestar; aquí solo cambia el estado.
                c.execute("""
                    UPDATE detalle_prestamos
                    SET estado = 'COBRADO', fecha_estado = ?, venta_id = ?
                    WHERE id = ?
                """, (fecha, vid, did))

            self._actualizar_estado_prestamo(c)

        asegurar_base_guardada()
        self.cambios = True
        self.hubo_cobro = True
        self._cargar()
        QMessageBox.information(
            self, "Préstamo cobrado",
            f"Venta #{vid} registrada por ${total:.2f} ({metodo})."
        )


def pedir_usuario_y_fondo(parent=None):
    login = DialogoLogin(parent)
    if login.exec() != QDialog.Accepted:
        return None, None

    if login.usuario_actual["rol"] == "vendedor":
        nombre_turno = DialogoNombreVendedor(login.usuario_actual, parent)
        if nombre_turno.exec() != QDialog.Accepted:
            return None, None
        login.usuario_actual["nombre_turno"] = nombre_turno.nombre()

    fondo = DialogoFondoInicial(login.usuario_actual, parent)
    if fondo.exec() != QDialog.Accepted:
        return None, None

    return login.usuario_actual, fondo.fondo()


# ──────────────────────────────────────────────────────────
# VENTANA PRINCIPAL
# ──────────────────────────────────────────────────────────

class POSAbarrotes(QMainWindow):
    def __init__(self, usuario_actual, fondo_inicial=0):
        super().__init__()
        self.setWindowTitle("Sistema POS — Tienda Periquita")
        self.resize(1320, 840)

        self._usuario_actual = usuario_actual
        self._es_admin = usuario_actual["rol"] == "admin"
        self._nombre_operador = nombre_visible_usuario(usuario_actual)
        self._sesion_id = iniciar_registro_sesion(
            usuario_actual["id"], fondo_inicial, self._nombre_operador
        )
        self._fondo_inicial = fondo_inicial
        self._sesion_finalizada = False
        self._cierre_confirmado = False
        self._nueva_ventana = None
        self._ticket = []             # lista de dicts con los items del ticket
        self._pid_editando = None     # ID del producto cargado en el formulario
        self._codigo_editando_actual = None

        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._lbl_sesion = QLabel(
            f"Usuario: {self._nombre_operador}  |  Rol: {usuario_actual['rol']}"
        )
        self._btn_cerrar_sesion = QPushButton("Cerrar sesión")
        self._btn_cerrar_sesion.setObjectName("btn_naranja")
        self._btn_cerrar_sesion.clicked.connect(self._cerrar_sesion)
        self._statusbar.addPermanentWidget(self._lbl_sesion)
        self._statusbar.addPermanentWidget(self._btn_cerrar_sesion)

        tabs = QTabWidget()
        tabs.addTab(self._crear_tab_venta(),      "🛒   Punto de Venta")
        tabs.addTab(
            self._crear_tab_inventario(),
            "📦   Inventario" if self._es_admin else "📦   Agregar Inventario"
        )
        tabs.addTab(self._crear_tab_reportes(),   "📊   Ventas del Día")
        tabs.addTab(self._crear_tab_apartados(),  "💵   Apartados")
        tabs.addTab(self._crear_tab_prestamos(),  "🤝   Préstamos")
        if self._es_admin:
            tabs.addTab(self._crear_tab_kpis(), "📈   KPIs Vendedores")
            tabs.addTab(self._crear_tab_compras(), "🚚   Compras")
            tabs.addTab(self._crear_tab_reportes_fuertes(), "📊   Reportes Admin")
            tabs.addTab(self._crear_tab_analisis_rangos(), "📆   Análisis Rangos")
        tabs.currentChanged.connect(self._al_cambiar_tab)
        self.setCentralWidget(tabs)
        self.setStyleSheet(ESTILO)
        self._perrito = AsistentePerrito(self, self._nombre_operador)
        self._perrito.show()

        self._refrescar_categorias()
        self._cargar_productos()
        self._cargar_productos_pos()
        self._cargar_ticket_pendiente()
        self._cargar_ventas()
        self._cargar_apartados()
        self._cargar_prestamos()
        self._cargar_productos_prestamo()
        self._cargar_kpis()
        self._cargar_historial_compras()
        self._cargar_reportes_fuertes()
        self._cargar_analisis_rangos()
        self._statusbar.showMessage(
            f"Sesión: {self._nombre_operador} ({usuario_actual['rol']})", 6000
        )
        QTimer.singleShot(0, self._enfocar_codigo_venta)
        QTimer.singleShot(900, lambda: self._perrito_evento("login"))

    def _al_cambiar_tab(self, index):
        tabs = self.centralWidget()
        w = tabs.widget(index) if tabs else None
        if index == 0:
            QTimer.singleShot(0, self._enfocar_codigo_venta)
        elif w is not None and w is getattr(self, "_tab_prestamos_widget", None):
            QTimer.singleShot(0, self._enfocar_codigo_prestamo)

    def _enfocar_codigo_venta(self):
        if hasattr(self, "_inp_codigo_venta"):
            self._inp_codigo_venta.setFocus(Qt.OtherFocusReason)
            self._inp_codigo_venta.selectAll()

    def _perrito_mensaje(self, texto):
        if hasattr(self, "_perrito") and self._perrito:
            self._perrito.mostrar_mensaje(texto)

    def _perrito_evento(self, evento):
        if hasattr(self, "_perrito") and self._perrito:
            self._perrito.evento(evento)

    def _guardar_ticket_pendiente(self):
        if not hasattr(self, "_usuario_actual"):
            return
        usuario_id = self._usuario_actual["id"]
        vendedor_nombre = self._nombre_operador
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM detalle_ticket_pendiente WHERE usuario_id = ?",
                (usuario_id,)
            )
            if not self._ticket:
                c.execute(
                    "DELETE FROM ticket_pendiente WHERE usuario_id = ?",
                    (usuario_id,)
                )
                return

            c.execute("""
                INSERT INTO ticket_pendiente (usuario_id, actualizado, vendedor_nombre)
                VALUES (?, ?, ?)
                ON CONFLICT(usuario_id) DO UPDATE SET
                    actualizado = excluded.actualizado,
                    vendedor_nombre = excluded.vendedor_nombre
            """, (usuario_id, fecha, vendedor_nombre))
            for item in self._ticket:
                c.execute("""
                    INSERT INTO detalle_ticket_pendiente
                        (usuario_id, producto_id, cantidad, precio_unitario,
                         costo_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    usuario_id, item["pid"], item["cant"], item["precio"],
                    item.get("costo", 0) or 0, item["sub"],
                ))

    def _cargar_ticket_pendiente(self):
        if not hasattr(self, "_usuario_actual"):
            return
        usuario_id = self._usuario_actual["id"]
        vendedor_nombre = self._nombre_operador
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT d.producto_id, p.codigo_barras, p.nombre,
                       d.cantidad, d.precio_unitario, d.costo_unitario,
                       p.stock, p.activo
                FROM detalle_ticket_pendiente d
                JOIN ticket_pendiente t ON t.usuario_id = d.usuario_id
                JOIN productos p ON p.id = d.producto_id
                WHERE d.usuario_id = ?
                  AND COALESCE(t.vendedor_nombre, '') = ?
                ORDER BY p.nombre
            """, (usuario_id, vendedor_nombre))
            filas = c.fetchall()

        restaurados = []
        for pid, codigo, nombre, cantidad, precio, costo, stock, activo in filas:
            if not activo or stock <= 0:
                continue
            cantidad = min(cantidad, stock)
            restaurados.append({
                "pid": pid,
                "codigo": codigo,
                "nombre": nombre,
                "cant": cantidad,
                "precio": precio,
                "costo": costo,
                "sub": precio * cantidad,
                "stock": stock,
            })

        if restaurados:
            self._ticket = restaurados
            self._refrescar_ticket()
            self._statusbar.showMessage(
                "Ticket en curso restaurado desde el guardado automático.", 7000
            )
            self._perrito_mensaje("Recuperé el ticket")

    def _confirmar_salida(self, accion):
        if self._ticket:
            r = QMessageBox.question(
                self, "Venta sin cobrar",
                f"Hay productos en el ticket que todavía no se han cobrado.\n\n"
                f"Si continúas, ese ticket se cancelará y no se guardará como venta.\n"
                f"Las ventas ya cobradas, productos e inventario sí quedan guardados.\n\n"
                f"¿Deseas {accion}?",
                QMessageBox.Yes | QMessageBox.No,
            )
            return r == QMessageBox.Yes

        r = QMessageBox.question(
            self, "Confirmar salida",
            f"¿Deseas {accion}?\n\n"
            f"Los datos guardados en la base de datos se conservarán.",
            QMessageBox.Yes | QMessageBox.No,
        )
        return r == QMessageBox.Yes

    def _finalizar_sesion(self, pedir_corte=True):
        if self._sesion_finalizada:
            return True

        resultado = {
            "efectivo_contado": None,
            "diferencia": None,
            "observaciones": "",
        }
        if pedir_corte:
            resumen = resumen_caja_sesion(self._sesion_id)
            if resumen:
                dlg = DialogoCierreCaja(resumen, self)
                if dlg.exec() != QDialog.Accepted:
                    return False
                resultado = dlg.resultado()

        asegurar_base_guardada()
        cerrar_registro_sesion(
            self._sesion_id,
            resultado["efectivo_contado"],
            resultado["diferencia"],
            resultado["observaciones"],
        )
        self._sesion_finalizada = True
        asegurar_base_guardada()
        if pedir_corte:
            self._perrito_evento("corte")
        return True

    def _cerrar_sesion(self):
        if not self._confirmar_salida("cerrar sesión"):
            return

        self._ticket.clear()
        self._refrescar_ticket()

        if not self._finalizar_sesion():
            return

        usuario_actual, fondo_inicial = pedir_usuario_y_fondo(self)
        if not usuario_actual:
            self._cierre_confirmado = True
            self.close()
            return

        self._nueva_ventana = POSAbarrotes(usuario_actual, fondo_inicial)
        self._nueva_ventana.show()
        self._cierre_confirmado = True
        self.close()

    def closeEvent(self, event):
        if not self._cierre_confirmado:
            if not self._confirmar_salida("cerrar el programa"):
                event.ignore()
                return
            self._ticket.clear()
            self._refrescar_ticket()
            self._cierre_confirmado = True

        if not self._finalizar_sesion():
            self._cierre_confirmado = False
            event.ignore()
            return
        event.accept()

    # ══════════════════════════════════════════════════════
    # TAB 1 — PUNTO DE VENTA
    # ══════════════════════════════════════════════════════

    def _crear_tab_venta(self):
        w = QWidget()
        root = QHBoxLayout(w)
        root.setSpacing(12)

        # ── Columna izquierda: ticket y búsqueda ───────────
        izq = QVBoxLayout()
        izq.setSpacing(8)

        lbl = QLabel("Punto de Venta")
        lbl.setObjectName("lbl_titulo")
        izq.addWidget(lbl)

        grp_scan = QGroupBox("Escanear / buscar por código de barras")
        hl = QHBoxLayout(grp_scan)
        self._inp_codigo_venta = QLineEdit()
        self._inp_codigo_venta.setPlaceholderText(
            "Código de barras — presiona Enter o escanea"
        )
        self._inp_codigo_venta.returnPressed.connect(self._agregar_por_codigo)
        btn_add = QPushButton("➕  Agregar")
        btn_add.clicked.connect(self._agregar_por_codigo)
        hl.addWidget(self._inp_codigo_venta)
        hl.addWidget(btn_add)
        izq.addWidget(grp_scan)

        grp_buscar = QGroupBox("Buscar producto por nombre o categoría")
        vl_buscar = QVBoxLayout(grp_buscar)
        hl_buscar = QHBoxLayout()

        self._inp_buscar_pos = QLineEdit()
        self._inp_buscar_pos.setPlaceholderText("Ej: huevo, cigarro, pan, refresco...")
        self._inp_buscar_pos.textChanged.connect(self._cargar_productos_pos)

        self._combo_cat_pos = QComboBox()
        self._combo_cat_pos.currentIndexChanged.connect(self._cargar_productos_pos)

        btn_agregar_sel = QPushButton("➕  Agregar seleccionado")
        btn_agregar_sel.clicked.connect(self._agregar_seleccion_busqueda)

        hl_buscar.addWidget(self._inp_buscar_pos, stretch=2)
        hl_buscar.addWidget(self._combo_cat_pos, stretch=1)
        hl_buscar.addWidget(btn_agregar_sel)
        vl_buscar.addLayout(hl_buscar)

        self._tabla_busqueda_pos = QTableWidget()
        self._tabla_busqueda_pos.setColumnCount(6)
        self._tabla_busqueda_pos.setHorizontalHeaderLabels(
            ["ID", "Código", "Producto", "Categoría", "Precio", "Stock"]
        )
        self._tabla_busqueda_pos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_busqueda_pos.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_busqueda_pos.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_busqueda_pos.setAlternatingRowColors(True)
        self._tabla_busqueda_pos.doubleClicked.connect(self._agregar_seleccion_busqueda)
        self._tabla_busqueda_pos.setMaximumHeight(190)
        self._tabla_busqueda_pos.hideColumn(0)
        vl_buscar.addWidget(self._tabla_busqueda_pos)
        izq.addWidget(grp_buscar)

        self._tabla_ticket = QTableWidget()
        self._tabla_ticket.setColumnCount(6)
        self._tabla_ticket.setHorizontalHeaderLabels(
            ["ID", "Código", "Producto", "Cant.", "Precio Unit.", "Subtotal"]
        )
        self._tabla_ticket.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_ticket.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_ticket.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_ticket.setAlternatingRowColors(True)
        izq.addWidget(self._tabla_ticket)

        grp_acc = QGroupBox("Acciones del ticket")
        hl2 = QHBoxLayout(grp_acc)
        acciones = [
            ("➕  + Cantidad",      "",          self._sumar_cantidad),
            ("➖  − Cantidad",      "",          self._restar_cantidad),
            ("🗑   Eliminar fila",  "btn_rojo",  self._eliminar_item),
            ("❌  Cancelar venta",  "btn_rojo",  self._cancelar_venta),
        ]
        for texto, obj, slot in acciones:
            b = QPushButton(texto)
            if obj:
                b.setObjectName(obj)
            b.clicked.connect(slot)
            hl2.addWidget(b)
        izq.addWidget(grp_acc)

        root.addLayout(izq, stretch=3)

        # ── Columna derecha: cobro ─────────────────────────
        der = QVBoxLayout()
        der.setSpacing(8)
        der.addStretch(1)

        grp_cobro = QGroupBox("Cobro")
        vl = QVBoxLayout(grp_cobro)
        vl.setSpacing(10)

        lbl_t = QLabel("TOTAL:")
        lbl_t.setAlignment(Qt.AlignCenter)
        lbl_t.setStyleSheet("font-size: 14px; color: #a6adc8;")
        vl.addWidget(lbl_t)

        self._lbl_total = QLabel("$0.00")
        self._lbl_total.setObjectName("lbl_total")
        self._lbl_total.setAlignment(Qt.AlignCenter)
        vl.addWidget(self._lbl_total)

        vl.addSpacing(4)
        vl.addWidget(QLabel("Método de pago:"))
        self._combo_pago = QComboBox()
        self._combo_pago.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])
        self._combo_pago.currentTextChanged.connect(self._toggle_efectivo)
        vl.addWidget(self._combo_pago)

        self._grp_efectivo = QGroupBox("Efectivo recibido")
        vl_ef = QVBoxLayout(self._grp_efectivo)
        self._spin_efectivo = CasillaMonto()
        self._spin_efectivo.setRange(0, 9_999_999)
        self._spin_efectivo.setPrefix("$")
        self._spin_efectivo.setDecimals(2)
        self._spin_efectivo.setSingleStep(10)
        self._spin_efectivo.valueChanged.connect(self._actualizar_cambio)
        self._lbl_cambio = QLabel("Cambio: $0.00")
        self._lbl_cambio.setAlignment(Qt.AlignCenter)
        self._lbl_cambio.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #a6e3a1;"
        )
        vl_ef.addWidget(self._spin_efectivo)
        vl_ef.addWidget(self._lbl_cambio)
        vl.addWidget(self._grp_efectivo)

        vl.addSpacing(8)
        btn_cobrar = QPushButton("💰  COBRAR")
        btn_cobrar.setObjectName("btn_cobrar")
        btn_cobrar.clicked.connect(self._cobrar)
        vl.addWidget(btn_cobrar)

        der.addWidget(grp_cobro)
        der.addStretch(1)
        root.addLayout(der, stretch=1)

        self._toggle_efectivo("Efectivo")
        return w

    # ── helpers del punto de venta ─────────────────────────

    def _toggle_efectivo(self, metodo):
        self._grp_efectivo.setVisible(metodo == "Efectivo")

    def _actualizar_cambio(self, valor=None):
        if valor is None:
            valor = self._spin_efectivo.value()
        total = sum(i["sub"] for i in self._ticket)
        cambio = valor - total
        if cambio >= 0:
            self._lbl_cambio.setText(f"Cambio: ${cambio:.2f}")
            self._lbl_cambio.setStyleSheet(
                "font-size: 17px; font-weight: bold; color: #a6e3a1;"
            )
        else:
            self._lbl_cambio.setText(f"Faltan: ${abs(cambio):.2f}")
            self._lbl_cambio.setStyleSheet(
                "font-size: 17px; font-weight: bold; color: #f38ba8;"
            )

    def _buscar_producto_por_codigo(self, codigo):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, codigo_barras, nombre, precio_venta, stock, precio_compra
                FROM productos
                WHERE codigo_barras = ? AND activo = 1
            """, (codigo,))
            return c.fetchone()

    def _buscar_producto_por_id(self, pid):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, codigo_barras, nombre, precio_venta, stock, precio_compra
                FROM productos
                WHERE id = ? AND activo = 1
            """, (pid,))
            return c.fetchone()

    def _agregar_por_codigo(self):
        codigo = self._inp_codigo_venta.text().strip()
        if not codigo:
            return
        self._inp_codigo_venta.clear()

        prod = self._buscar_producto_por_codigo(codigo)
        if not prod:
            QMessageBox.warning(self, "No encontrado",
                                "Código no registrado en inventario activo.")
            self._enfocar_codigo_venta()
            return

        self._agregar_producto_al_ticket(prod)

    def _agregar_producto_al_ticket(self, prod):
        pid, cod, nombre, precio, stock, costo = prod

        if stock <= 0:
            QMessageBox.warning(self, "Sin existencia",
                                f"«{nombre}» no tiene stock disponible.")
            self._enfocar_codigo_venta()
            return

        for item in self._ticket:
            if item["pid"] == pid:
                if item["cant"] >= stock:
                    QMessageBox.warning(
                        self, "Stock insuficiente",
                        f"Solo hay {stock} unidades disponibles de «{nombre}»."
                    )
                    self._enfocar_codigo_venta()
                    return
                item["cant"] += 1
                item["sub"] = item["cant"] * item["precio"]
                item["stock"] = stock
                item["costo"] = costo
                self._refrescar_ticket()
                self._statusbar.showMessage(
                    f"«{nombre}» — cantidad: {item['cant']}", 2500
                )
                self._enfocar_codigo_venta()
                return

        self._ticket.append({
            "pid": pid, "codigo": cod, "nombre": nombre,
            "cant": 1, "precio": precio, "costo": costo,
            "sub": precio, "stock": stock,
        })
        self._refrescar_ticket()
        self._statusbar.showMessage(f"«{nombre}» agregado al ticket.", 2500)
        self._enfocar_codigo_venta()

    def _cargar_productos_pos(self, *args):
        if not hasattr(self, "_tabla_busqueda_pos"):
            return

        q = self._inp_buscar_pos.text().strip() if hasattr(self, "_inp_buscar_pos") else ""
        categoria = self._combo_cat_pos.currentData() if hasattr(self, "_combo_cat_pos") else ""

        filtros = ["activo = 1"]
        params = []
        if q:
            like = f"%{q}%"
            filtros.append("(nombre LIKE ? OR codigo_barras LIKE ? OR categoria LIKE ?)")
            params.extend([like, like, like])
        if categoria:
            filtros.append("categoria = ?")
            params.append(categoria)

        sql = f"""
            SELECT id, codigo_barras, nombre, categoria, precio_venta, stock, stock_minimo
            FROM productos
            WHERE {' AND '.join(filtros)}
            ORDER BY categoria COLLATE NOCASE, nombre COLLATE NOCASE
            LIMIT 120
        """

        with conectar() as conn:
            c = conn.cursor()
            c.execute(sql, params)
            rows = c.fetchall()

        self._tabla_busqueda_pos.setRowCount(len(rows))
        C_ROJO = QColor("#f38ba8")
        C_AMAR = QColor("#f9e2af")
        C_DARK = QColor("#1e1e2e")

        for fila, row in enumerate(rows):
            pid, cod, nom, cat, precio, stock, minimo = row
            vals = [
                str(pid), codigo_visible(cod), nom, cat or "",
                f"${precio:.2f}", str(stock),
            ]
            for col, val in enumerate(vals):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if stock == 0:
                    cell.setBackground(C_ROJO)
                    cell.setForeground(C_DARK)
                elif stock <= minimo:
                    cell.setBackground(C_AMAR)
                    cell.setForeground(C_DARK)
                self._tabla_busqueda_pos.setItem(fila, col, cell)

        if rows:
            self._tabla_busqueda_pos.selectRow(0)

        # Mantener sincronizada la búsqueda de la pestaña de préstamos
        if hasattr(self, "_tabla_busqueda_prest"):
            self._cargar_productos_prestamo()

    def _agregar_seleccion_busqueda(self, *args):
        fila = self._tabla_busqueda_pos.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona un producto de la búsqueda.")
            self._enfocar_codigo_venta()
            return
        item_id = self._tabla_busqueda_pos.item(fila, 0)
        if not item_id:
            return
        prod = self._buscar_producto_por_id(int(item_id.text()))
        if not prod:
            QMessageBox.warning(self, "No disponible",
                                "El producto ya no está activo o no existe.")
            self._cargar_productos_pos()
            self._enfocar_codigo_venta()
            return
        self._agregar_producto_al_ticket(prod)
        self._inp_buscar_pos.clear()
        self._tabla_busqueda_pos.clearSelection()
        self._enfocar_codigo_venta()

    def _refrescar_ticket(self):
        self._tabla_ticket.setRowCount(len(self._ticket))
        total = 0.0
        for fila, item in enumerate(self._ticket):
            total += item["sub"]
            vals = [
                str(item["pid"]), codigo_visible(item["codigo"]), item["nombre"],
                str(item["cant"]),
                f"${item['precio']:.2f}",
                f"${item['sub']:.2f}",
            ]
            for col, val in enumerate(vals):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_ticket.setItem(fila, col, cell)
        self._lbl_total.setText(f"${total:.2f}")
        self._actualizar_cambio(self._spin_efectivo.value())
        self._guardar_ticket_pendiente()

    def _fila_ticket(self):
        f = self._tabla_ticket.currentRow()
        if f < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un producto del ticket.")
        return f

    def _sumar_cantidad(self):
        f = self._fila_ticket()
        if f < 0:
            self._enfocar_codigo_venta()
            return

        item = self._ticket[f]
        prod = self._buscar_producto_por_id(item["pid"])
        if not prod:
            QMessageBox.warning(self, "Producto no disponible",
                                "El producto ya no está activo en inventario.")
            self._enfocar_codigo_venta()
            return

        stock_actual = prod[4]
        item["stock"] = stock_actual
        if item["cant"] >= stock_actual:
            QMessageBox.warning(self, "Límite de stock",
                                f"Solo hay {stock_actual} unidades disponibles.")
            self._enfocar_codigo_venta()
            return
        item["cant"] += 1
        item["sub"] = item["cant"] * item["precio"]
        self._refrescar_ticket()
        self._enfocar_codigo_venta()

    def _restar_cantidad(self):
        f = self._fila_ticket()
        if f < 0:
            self._enfocar_codigo_venta()
            return
        item = self._ticket[f]
        if item["cant"] > 1:
            item["cant"] -= 1
            item["sub"] = item["cant"] * item["precio"]
        else:
            self._ticket.pop(f)
        self._refrescar_ticket()
        self._enfocar_codigo_venta()

    def _eliminar_item(self):
        f = self._fila_ticket()
        if f < 0:
            self._enfocar_codigo_venta()
            return
        self._ticket.pop(f)
        self._refrescar_ticket()
        self._enfocar_codigo_venta()

    def _cancelar_venta(self):
        if not self._ticket:
            return
        r = QMessageBox.question(
            self, "Cancelar venta",
            "¿Deseas cancelar la venta actual?\nSe perderán los productos agregados.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r == QMessageBox.Yes:
            self._ticket.clear()
            self._refrescar_ticket()
            self._statusbar.showMessage("Venta cancelada.", 3000)
            self._enfocar_codigo_venta()

    def _cobrar(self):
        if not self._ticket:
            QMessageBox.warning(self, "Ticket vacío",
                                "Agrega productos al ticket antes de cobrar.")
            self._enfocar_codigo_venta()
            return

        total = sum(i["sub"] for i in self._ticket)
        metodo = self._combo_pago.currentText()
        efec = self._spin_efectivo.value() if metodo == "Efectivo" else 0.0

        if metodo == "Efectivo" and efec < total:
            QMessageBox.warning(self, "Monto insuficiente",
                                "El efectivo recibido es menor al total de la venta.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with conectar() as conn:
                c = conn.cursor()

                for item in self._ticket:
                    c.execute("""
                        SELECT nombre, stock, activo, precio_compra
                        FROM productos
                        WHERE id = ?
                    """, (item["pid"],))
                    row = c.fetchone()
                    if not row or row[2] != 1:
                        raise ValueError(f"«{item['nombre']}» ya no está activo.")
                    nombre_actual, stock_actual, _activo, costo_actual = row
                    if stock_actual < item["cant"]:
                        raise ValueError(
                            f"Stock insuficiente para «{nombre_actual}». "
                            f"Disponible: {stock_actual}, en ticket: {item['cant']}."
                        )
                    item["costo"] = costo_actual

                c.execute("""
                    INSERT INTO ventas
                        (fecha, total, metodo_pago, efectivo_recibido,
                         usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    fecha, total, metodo, efec, self._usuario_actual["id"],
                    self._sesion_id, self._nombre_operador,
                ))
                vid = c.lastrowid

                for item in self._ticket:
                    costo_unitario = item.get("costo", 0) or 0
                    costo_total = costo_unitario * item["cant"]
                    c.execute("""
                        INSERT INTO detalle_ventas
                            (venta_id, producto_id, cantidad, precio_unitario,
                             costo_unitario, subtotal, costo_total)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        vid, item["pid"], item["cant"], item["precio"],
                        costo_unitario, item["sub"], costo_total,
                    ))

                    c.execute(
                        "UPDATE productos SET stock = stock - ? WHERE id = ?",
                        (item["cant"], item["pid"])
                    )

                    c.execute("""
                        INSERT INTO movimientos_inventario
                            (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                        VALUES (?, 'SALIDA', ?, ?, ?)
                    """, (item["pid"], item["cant"], f"Venta #{vid}", fecha))

            msg = (
                f"✅  Venta #{vid} registrada exitosamente.\n\n"
                f"Total cobrado: ${total:.2f}\n"
                f"Método de pago: {metodo}"
            )
            if metodo == "Efectivo":
                msg += f"\nEfectivo recibido: ${efec:.2f}"
                msg += f"\nCambio entregado:  ${efec - total:.2f}"

            self._ticket.clear()
            self._refrescar_ticket()
            self._spin_efectivo.setValue(0)
            asegurar_base_guardada()
            QMessageBox.information(self, "Venta realizada", msg)

            self._cargar_productos()
            self._cargar_productos_pos()
            self._cargar_ventas()
            self._cargar_kpis()
            self._cargar_reportes_fuertes()
            self._cargar_analisis_rangos()
            self._statusbar.showMessage(
                f"Venta #{vid} registrada — ${total:.2f}  ({metodo})", 6000
            )
            self._perrito_evento("venta")
            self._enfocar_codigo_venta()

        except Exception as e:
            QMessageBox.critical(self, "Error al cobrar",
                                 f"No se pudo registrar la venta:\n{e}")
            self._enfocar_codigo_venta()

    # ══════════════════════════════════════════════════════
    # TAB 2 — INVENTARIO
    # ══════════════════════════════════════════════════════

    def _crear_tab_inventario(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Inventario de Productos" if self._es_admin else "Agregar Productos al Inventario")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        if not self._es_admin:
            aviso = QLabel(
                "Modo vendedor: puedes registrar productos nuevos con precio de compra, "
                "precio de venta y stock inicial. También puedes añadir stock a productos "
                "existentes, pero no desactivar, restar ni editar libremente."
            )
            aviso.setWordWrap(True)
            aviso.setStyleSheet("color: #f9e2af; font-size: 12px;")
            root.addWidget(aviso)

        # ── Formulario ─────────────────────────────────────
        grp = QGroupBox(
            "Datos del producto  —  Haz clic en una fila de la tabla para editar"
            if self._es_admin else
            "Datos del producto nuevo"
        )
        grid = QGridLayout(grp)
        grid.setSpacing(6)

        self._inp_cod = QLineEdit()
        self._inp_cod.setPlaceholderText("Código de barras (opcional)")
        self._inp_nom = QLineEdit()
        self._inp_nom.setPlaceholderText("Nombre del producto *")

        self._inp_cat = QComboBox()
        self._inp_cat.setEditable(True)
        self._inp_cat.setInsertPolicy(QComboBox.NoInsert)
        self._inp_cat.lineEdit().setPlaceholderText("Selecciona o escribe categoría")

        self._inp_compra = CasillaMonto()
        self._inp_compra.setRange(0, 999_999)
        self._inp_compra.setPrefix("$")
        self._inp_compra.setDecimals(2)

        self._inp_venta = CasillaMonto()
        self._inp_venta.setRange(0, 999_999)
        self._inp_venta.setPrefix("$")
        self._inp_venta.setDecimals(2)

        self._inp_stock = CasillaEntero()
        self._inp_stock.setRange(0, 999_999)

        self._inp_minimo = CasillaEntero()
        self._inp_minimo.setRange(0, 999_999)
        self._inp_minimo.setValue(5)

        # Fila 0
        grid.addWidget(QLabel("Código:"),       0, 0); grid.addWidget(self._inp_cod,    0, 1)
        grid.addWidget(QLabel("Nombre *:"),      0, 2); grid.addWidget(self._inp_nom,    0, 3)
        grid.addWidget(QLabel("Categoría:"),     0, 4); grid.addWidget(self._inp_cat,    0, 5)
        # Fila 1
        grid.addWidget(QLabel("Precio compra:"), 1, 0); grid.addWidget(self._inp_compra, 1, 1)
        grid.addWidget(QLabel("Precio venta *:"),1, 2); grid.addWidget(self._inp_venta,  1, 3)
        grid.addWidget(QLabel("Stock inicial:"), 1, 4); grid.addWidget(self._inp_stock,  1, 5)
        grid.addWidget(QLabel("Stock mínimo:"),  1, 6); grid.addWidget(self._inp_minimo, 1, 7)
        root.addWidget(grp)

        # ── Botones + buscadores ────────────────────────────
        hl = QHBoxLayout()

        self._btn_guardar = QPushButton("💾  Guardar Producto")
        self._btn_guardar.setObjectName("btn_verde")
        self._btn_guardar.clicked.connect(self._guardar_producto)

        btn_limpiar = QPushButton("🧹  Limpiar")
        btn_limpiar.clicked.connect(self._limpiar_form_inv)

        self._btn_entrada = QPushButton("➕  Añadir Stock")
        self._btn_entrada.setObjectName("btn_verde")
        self._btn_entrada.setEnabled(False)
        self._btn_entrada.clicked.connect(self._agregar_existencias)

        self._btn_desac = QPushButton("🚫  Desactivar")
        self._btn_desac.setObjectName("btn_rojo")
        self._btn_desac.setEnabled(False)
        self._btn_desac.clicked.connect(self._desactivar_producto)

        self._btn_ajuste = QPushButton("📦  Ajustar Stock")
        self._btn_ajuste.setObjectName("btn_naranja")
        self._btn_ajuste.setEnabled(False)
        self._btn_ajuste.clicked.connect(self._ajustar_stock)

        self._btn_precio = QPushButton("🏷  Cambiar Precio")
        self._btn_precio.setObjectName("btn_naranja")
        self._btn_precio.setEnabled(False)
        self._btn_precio.clicked.connect(self._cambiar_precios)

        self._btn_hist_precios = QPushButton("📜  Historial Precios")
        self._btn_hist_precios.setEnabled(False)
        self._btn_hist_precios.clicked.connect(self._ver_historial_precios)

        for boton_admin in (
            self._btn_desac, self._btn_ajuste,
            self._btn_precio, self._btn_hist_precios,
        ):
            boton_admin.setVisible(self._es_admin)

        self._inp_buscar = QLineEdit()
        self._inp_buscar.setPlaceholderText("🔍  Buscar por nombre o código...")
        self._inp_buscar.textChanged.connect(self._cargar_productos)

        self._combo_cat_inv = QComboBox()
        self._combo_cat_inv.currentIndexChanged.connect(self._cargar_productos)

        hl.addWidget(self._btn_guardar)
        hl.addWidget(btn_limpiar)
        hl.addWidget(self._btn_entrada)
        hl.addWidget(self._btn_desac)
        hl.addWidget(self._btn_ajuste)
        hl.addWidget(self._btn_precio)
        hl.addWidget(self._btn_hist_precios)
        hl.addStretch()
        hl.addWidget(self._inp_buscar, stretch=2)
        hl.addWidget(self._combo_cat_inv, stretch=1)
        root.addLayout(hl)

        # Leyenda de colores
        hl_ley = QHBoxLayout()
        for color, texto in [
            ("#f38ba8", "🔴 Sin stock (0 unidades)"),
            ("#f9e2af", "🟡 Stock bajo (≤ mínimo)"),
        ]:
            lb = QLabel(f"  {texto}  ")
            lb.setStyleSheet(
                f"background:{color}; color:#1e1e2e; "
                f"border-radius:3px; padding:2px 8px; font-size:12px;"
            )
            hl_ley.addWidget(lb)
        hl_ley.addStretch()
        root.addLayout(hl_ley)

        # ── Tabla de productos ──────────────────────────────
        self._tabla_prods = QTableWidget()
        self._tabla_prods.setColumnCount(9)
        self._tabla_prods.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría",
            "Precio Compra", "Precio Venta", "Stock", "Mínimo", "Estado",
        ])
        self._tabla_prods.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_prods.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_prods.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_prods.setAlternatingRowColors(True)
        self._tabla_prods.clicked.connect(self._al_seleccionar_producto_tabla)
        root.addWidget(self._tabla_prods)

        return w

    # ── helpers de inventario ──────────────────────────────

    def _categorias(self):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT DISTINCT TRIM(categoria)
                FROM productos
                WHERE categoria IS NOT NULL AND TRIM(categoria) <> ''
                ORDER BY TRIM(categoria) COLLATE NOCASE
            """)
            return [r[0] for r in c.fetchall()]

    def _llenar_combo_filtro_categorias(self, combo, categorias):
        actual = combo.currentData() if combo.count() else ""
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("Todas las categorías", "")
        for cat in categorias:
            combo.addItem(cat, cat)
        idx = combo.findData(actual)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def _llenar_combo_form_categorias(self, categorias):
        actual = self._inp_cat.currentText().strip() if self._inp_cat.count() else ""
        self._inp_cat.blockSignals(True)
        self._inp_cat.clear()
        self._inp_cat.addItem("")
        self._inp_cat.addItems(categorias)
        if actual:
            idx = self._inp_cat.findText(actual, Qt.MatchFixedString)
            if idx >= 0:
                self._inp_cat.setCurrentIndex(idx)
            else:
                self._inp_cat.setEditText(actual)
        else:
            self._inp_cat.setCurrentIndex(0)
        self._inp_cat.blockSignals(False)

    def _refrescar_categorias(self):
        categorias = self._categorias()
        if hasattr(self, "_inp_cat"):
            self._llenar_combo_form_categorias(categorias)
        if hasattr(self, "_combo_cat_inv"):
            self._llenar_combo_filtro_categorias(self._combo_cat_inv, categorias)
        if hasattr(self, "_combo_cat_pos"):
            self._llenar_combo_filtro_categorias(self._combo_cat_pos, categorias)

    def _registrar_historial_precio(self, cursor, producto_id, compra_ant, compra_nueva, venta_ant, venta_nueva, motivo, fecha):
        if round(compra_ant, 2) == round(compra_nueva, 2) and round(venta_ant, 2) == round(venta_nueva, 2):
            return
        cursor.execute("""
            INSERT INTO historial_precios
                (producto_id, usuario_id, precio_compra_anterior, precio_compra_nuevo,
                 precio_venta_anterior, precio_venta_nuevo, motivo, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            producto_id, self._usuario_actual["id"], compra_ant, compra_nueva,
            venta_ant, venta_nueva, motivo, fecha,
        ))

    def _guardar_producto(self):
        if not self._es_admin and self._pid_editando:
            QMessageBox.warning(
                self, "Permiso limitado",
                "Los vendedores solo pueden registrar productos nuevos."
            )
            self._limpiar_form_inv()
            return

        codigo = self._inp_cod.text().strip()
        nombre = self._inp_nom.text().strip()
        cat = self._inp_cat.currentText().strip()
        compra = self._inp_compra.value()
        venta = self._inp_venta.value()
        stock = self._inp_stock.value()
        minimo = self._inp_minimo.value()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        codigo_generado = False

        if not codigo:
            if self._pid_editando and es_codigo_manual(self._codigo_editando_actual):
                codigo = self._codigo_editando_actual
            else:
                codigo = generar_codigo_manual()
                codigo_generado = True

        if not nombre:
            QMessageBox.warning(self, "Falta nombre",
                                "El nombre del producto es obligatorio.")
            return
        if venta <= 0:
            QMessageBox.warning(self, "Precio inválido",
                                "El precio de venta debe ser mayor a $0.00.")
            return
        if venta < compra:
            r = QMessageBox.question(
                self, "Venta con pérdida",
                "El precio de venta es menor que el precio de compra.\n\n"
                "Esto generará ganancia negativa para este producto.\n"
                "¿Deseas guardar de todos modos?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if r != QMessageBox.Yes:
                return

        try:
            with conectar() as conn:
                c = conn.cursor()

                if self._pid_editando:
                    c.execute("""
                        SELECT precio_compra, precio_venta
                        FROM productos
                        WHERE id = ?
                    """, (self._pid_editando,))
                    precios_anteriores = c.fetchone()
                    compra_ant, venta_ant = precios_anteriores if precios_anteriores else (compra, venta)

                    c.execute("""
                        UPDATE productos SET
                            codigo_barras = ?, nombre = ?, categoria = ?,
                            precio_compra = ?, precio_venta = ?, stock_minimo = ?
                        WHERE id = ?
                    """, (codigo, nombre, cat, compra, venta, minimo,
                          self._pid_editando))
                    self._registrar_historial_precio(
                        c, self._pid_editando, compra_ant, compra,
                        venta_ant, venta, "Edición de producto", fecha
                    )
                    QMessageBox.information(self, "Actualizado",
                                            "Producto actualizado correctamente.")
                    self._statusbar.showMessage(f"«{nombre}» actualizado.", 3000)

                else:
                    c.execute("""
                        INSERT INTO productos
                            (codigo_barras, nombre, categoria, precio_compra,
                             precio_venta, stock, stock_minimo, fecha_alta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, cat, compra, venta, stock, minimo, fecha))
                    pid = c.lastrowid
                    self._registrar_historial_precio(
                        c, pid, 0, compra, 0, venta,
                        "Alta de producto", fecha
                    )
                    if stock > 0:
                        c.execute("""
                            INSERT INTO movimientos_inventario
                                (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                            VALUES (?, 'ENTRADA', ?, 'Alta inicial de producto', ?)
                        """, (pid, stock, fecha))

                    msg = "Producto registrado correctamente."
                    if codigo_generado:
                        msg += "\n\nSe creó como producto sin código de barras."
                    QMessageBox.information(self, "Guardado", msg)
                    self._statusbar.showMessage(f"«{nombre}» registrado.", 3000)

            self._limpiar_form_inv()
            self._refrescar_categorias()
            self._cargar_productos()
            self._cargar_productos_pos()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Código duplicado",
                                "Ya existe un producto con ese código de barras.")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"No se pudo guardar el producto:\n{e}")

    def _al_seleccionar_producto_tabla(self, index):
        self._btn_entrada.setEnabled(True)
        if self._es_admin:
            self._cargar_prod_en_form(index)
        else:
            nombre_item = self._tabla_prods.item(index.row(), 2)
            nombre = nombre_item.text() if nombre_item else "producto"
            self._statusbar.showMessage(
                f"Seleccionado «{nombre}». Usa 'Añadir Stock' para sumar inventario.", 5000
            )

    def _producto_seleccionado_tabla(self):
        fila = self._tabla_prods.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un producto de la tabla.")
            return None

        item_id = self._tabla_prods.item(fila, 0)
        if not item_id:
            QMessageBox.warning(self, "Selección inválida",
                                "No se pudo leer el producto seleccionado.")
            return None

        return int(item_id.text())

    def _cargar_prod_en_form(self, index):
        """Carga la fila seleccionada en el formulario para editar."""
        if not self._es_admin:
            return

        pid = int(self._tabla_prods.item(index.row(), 0).text())

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, codigo_barras, nombre, categoria,
                       precio_compra, precio_venta, stock, stock_minimo
                FROM productos WHERE id = ?
            """, (pid,))
            p = c.fetchone()

        if not p:
            return

        self._pid_editando = p[0]
        self._codigo_editando_actual = p[1]
        self._inp_cod.setText("" if es_codigo_manual(p[1]) else p[1])
        self._inp_nom.setText(p[2])
        self._inp_cat.setEditText(p[3] or "")
        self._inp_compra.setValue(p[4])
        self._inp_venta.setValue(p[5])
        self._inp_stock.setValue(p[6])
        self._inp_stock.setEnabled(False)   # usa el botón de ajuste para cambiar stock
        self._inp_minimo.setValue(p[7])

        self._btn_guardar.setText("💾  Actualizar Producto")
        self._btn_desac.setEnabled(True)
        self._btn_ajuste.setEnabled(True)
        self._btn_entrada.setEnabled(True)
        self._btn_precio.setEnabled(True)
        self._btn_hist_precios.setEnabled(True)
        self._statusbar.showMessage(
            f"Editando: «{p[2]}»  (ID {p[0]})  —  "
            f"Usa 'Ajustar Stock' para cambiar existencias.", 6000
        )

    def _limpiar_form_inv(self):
        self._pid_editando = None
        self._codigo_editando_actual = None
        for w in (self._inp_cod, self._inp_nom):
            w.clear()
        self._inp_cat.setEditText("")
        for w in (self._inp_compra, self._inp_venta):
            w.setValue(0)
        self._inp_stock.setValue(0)
        self._inp_stock.setEnabled(True)
        self._inp_minimo.setValue(5)
        self._btn_guardar.setText("💾  Guardar Producto")
        self._btn_entrada.setEnabled(False)
        self._btn_desac.setEnabled(False)
        self._btn_ajuste.setEnabled(False)
        self._btn_precio.setEnabled(False)
        self._btn_hist_precios.setEnabled(False)

    def _desactivar_producto(self):
        if not self._es_admin:
            QMessageBox.warning(self, "Sin permiso",
                                "Solo el administrador puede desactivar productos.")
            return
        if not self._pid_editando:
            return
        nombre = self._inp_nom.text()
        r = QMessageBox.question(
            self, "Desactivar producto",
            f"¿Desactivar «{nombre}»?\n\n"
            f"El producto no aparecerá en el punto de venta,\n"
            f"pero se conservará en la base de datos.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r == QMessageBox.Yes:
            with conectar() as conn:
                conn.execute(
                    "UPDATE productos SET activo = 0 WHERE id = ?",
                    (self._pid_editando,)
                )
            self._limpiar_form_inv()
            self._cargar_productos()
            self._cargar_productos_pos()
            self._statusbar.showMessage(f"«{nombre}» desactivado.", 4000)

    def _ajustar_stock(self):
        if not self._es_admin:
            QMessageBox.warning(self, "Sin permiso",
                                "Solo el administrador puede ajustar stock existente.")
            return
        if not self._pid_editando:
            return

        with conectar() as conn:
            c = conn.cursor()
            c.execute("SELECT nombre, stock FROM productos WHERE id = ?",
                      (self._pid_editando,))
            nombre, stock_actual = c.fetchone()

        dlg = DialogoAjusteStock(nombre, stock_actual, self)
        if dlg.exec() != QDialog.Accepted:
            return

        d = dlg.resultado()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if d["tipo"] == "SALIDA" and d["cantidad"] > stock_actual:
            QMessageBox.warning(
                self, "Stock insuficiente",
                f"Solo hay {stock_actual} unidades disponibles de «{nombre}»."
            )
            return

        with conectar() as conn:
            c = conn.cursor()
            if d["tipo"] == "ENTRADA":
                c.execute("UPDATE productos SET stock = stock + ? WHERE id = ?",
                          (d["cantidad"], self._pid_editando))
            elif d["tipo"] == "SALIDA":
                c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                          (d["cantidad"], self._pid_editando))
            else:
                c.execute("UPDATE productos SET stock = ? WHERE id = ?",
                          (d["cantidad"], self._pid_editando))

            c.execute("""
                INSERT INTO movimientos_inventario
                    (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (self._pid_editando, d["tipo"], d["cantidad"], d["motivo"], fecha))

        self._limpiar_form_inv()
        self._cargar_productos()
        self._cargar_productos_pos()
        self._statusbar.showMessage(
            f"Stock de «{nombre}» ajustado — {d['tipo']}: {d['cantidad']} uds.", 4000
        )

    def _agregar_existencias(self):
        pid = self._producto_seleccionado_tabla()
        if not pid:
            return

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT nombre, stock, precio_compra, precio_venta, activo
                FROM productos
                WHERE id = ?
            """, (pid,))
            row = c.fetchone()

        if not row:
            QMessageBox.warning(self, "Producto no encontrado",
                                "No se pudo encontrar el producto seleccionado.")
            return

        nombre, stock_actual, compra_actual, venta_actual, activo = row
        if not activo:
            QMessageBox.warning(self, "Producto inactivo",
                                "No se puede añadir stock a un producto inactivo.")
            return

        dlg = DialogoEntradaInventario(
            nombre, stock_actual, compra_actual, venta_actual, self
        )
        if dlg.exec() != QDialog.Accepted:
            return

        d = dlg.resultado()
        if d["venta"] <= 0:
            QMessageBox.warning(self, "Precio inválido",
                                "El precio de venta debe ser mayor a $0.00.")
            return
        if d["venta"] < d["compra"]:
            r = QMessageBox.question(
                self, "Venta con pérdida",
                "El precio de venta es menor que el precio de compra.\n\n"
                "Esto generará ganancia negativa para este producto.\n"
                "¿Deseas guardar de todos modos?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if r != QMessageBox.Yes:
                return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        motivo = d["motivo"]
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE productos
                SET stock = stock + ?,
                    precio_compra = ?,
                    precio_venta = ?
                WHERE id = ?
            """, (d["cantidad"], d["compra"], d["venta"], pid))

            c.execute("""
                INSERT INTO movimientos_inventario
                    (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                VALUES (?, 'ENTRADA', ?, ?, ?)
            """, (pid, d["cantidad"], motivo, fecha))

            self._registrar_historial_precio(
                c, pid, compra_actual, d["compra"],
                venta_actual, d["venta"], motivo, fecha
            )

        self._cargar_productos()
        self._cargar_productos_pos()
        if self._es_admin and self._pid_editando == pid:
            self._limpiar_form_inv()
        elif not self._es_admin:
            self._btn_entrada.setEnabled(False)
        self._statusbar.showMessage(
            f"Entrada guardada: «{nombre}» +{d['cantidad']} uds.", 5000
        )
        QMessageBox.information(
            self, "Inventario añadido",
            f"Se añadieron {d['cantidad']} unidades a «{nombre}»."
        )

    def _cambiar_precios(self):
        if not self._es_admin:
            QMessageBox.warning(self, "Sin permiso",
                                "Solo el administrador puede cambiar precios existentes.")
            return
        if not self._pid_editando:
            return

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT nombre, precio_compra, precio_venta
                FROM productos
                WHERE id = ?
            """, (self._pid_editando,))
            row = c.fetchone()

        if not row:
            QMessageBox.warning(self, "Producto no encontrado",
                                "No se pudo encontrar el producto seleccionado.")
            return

        nombre, compra_actual, venta_actual = row
        dlg = DialogoCambioPrecio(nombre, compra_actual, venta_actual, self)
        if dlg.exec() != QDialog.Accepted:
            return

        d = dlg.resultado()
        if d["venta"] <= 0:
            QMessageBox.warning(self, "Precio inválido",
                                "El precio de venta debe ser mayor a $0.00.")
            return
        if d["venta"] < d["compra"]:
            r = QMessageBox.question(
                self, "Venta con pérdida",
                "El nuevo precio de venta es menor que el precio de compra.\n\n"
                "Esto generará ganancia negativa para este producto.\n"
                "¿Deseas guardar de todos modos?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if r != QMessageBox.Yes:
                return

        if round(d["compra"], 2) == round(compra_actual, 2) and round(d["venta"], 2) == round(venta_actual, 2):
            QMessageBox.information(self, "Sin cambios",
                                    "Los precios son iguales a los actuales.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE productos
                SET precio_compra = ?, precio_venta = ?
                WHERE id = ?
            """, (d["compra"], d["venta"], self._pid_editando))
            self._registrar_historial_precio(
                c, self._pid_editando, compra_actual, d["compra"],
                venta_actual, d["venta"], d["motivo"], fecha
            )

        self._inp_compra.setValue(d["compra"])
        self._inp_venta.setValue(d["venta"])
        self._cargar_productos()
        self._cargar_productos_pos()
        self._statusbar.showMessage(
            f"Precios de «{nombre}» actualizados — venta: ${d['venta']:.2f}", 5000
        )
        QMessageBox.information(self, "Precio actualizado",
                                "El cambio de precio quedó guardado en el historial.")

    def _ver_historial_precios(self):
        if not self._es_admin:
            QMessageBox.warning(self, "Sin permiso",
                                "Solo el administrador puede ver el historial de precios.")
            return
        if not self._pid_editando:
            return
        nombre = self._inp_nom.text().strip() or "Producto"
        DialogoHistorialPrecios(self._pid_editando, nombre, self).exec()

    def _cargar_productos(self, *args):
        if not hasattr(self, "_tabla_prods"):
            return

        q = self._inp_buscar.text().strip() if hasattr(self, "_inp_buscar") else ""
        categoria = self._combo_cat_inv.currentData() if hasattr(self, "_combo_cat_inv") else ""

        filtros = []
        params = []
        if not self._es_admin:
            filtros.append("activo = 1")
        if q:
            like = f"%{q}%"
            filtros.append("(nombre LIKE ? OR codigo_barras LIKE ? OR categoria LIKE ?)")
            params.extend([like, like, like])
        if categoria:
            filtros.append("categoria = ?")
            params.append(categoria)

        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                SELECT id, codigo_barras, nombre, categoria,
                       precio_compra, precio_venta, stock, stock_minimo, activo
                FROM productos
                {where}
                ORDER BY nombre COLLATE NOCASE
            """, params)
            rows = c.fetchall()

        self._tabla_prods.setRowCount(len(rows))
        C_ROJO = QColor("#f38ba8")
        C_AMAR = QColor("#f9e2af")
        C_DARK = QColor("#1e1e2e")

        for fila, row in enumerate(rows):
            pid, cod, nom, cat, compra, venta, stock, minimo, activo = row
            estado = "✅ Activo" if activo else "🚫 Inactivo"
            vals = [
                str(pid), codigo_visible(cod), nom, cat or "",
                f"${compra:.2f}", f"${venta:.2f}",
                str(stock), str(minimo), estado,
            ]
            for col, val in enumerate(vals):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if not activo:
                    cell.setForeground(QColor("#6c7086"))
                elif stock == 0:
                    cell.setBackground(C_ROJO)
                    cell.setForeground(C_DARK)
                elif stock <= minimo:
                    cell.setBackground(C_AMAR)
                    cell.setForeground(C_DARK)
                self._tabla_prods.setItem(fila, col, cell)

    # ══════════════════════════════════════════════════════
    # TAB 3 — VENTAS DEL DÍA
    # ══════════════════════════════════════════════════════

    def _crear_tab_reportes(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Ventas del Día" if self._es_admin else "Mis Ventas del Día")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        # ── Selector de fecha ───────────────────────────────
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Fecha:"))
        self._date_rep = QDateEdit(QDate.currentDate())
        self._date_rep.setCalendarPopup(True)
        self._date_rep.setDisplayFormat("dd/MM/yyyy")

        btn_ver = QPushButton("🔍  Ver")
        btn_ver.clicked.connect(self._cargar_ventas)

        def ir_hoy():
            self._date_rep.setDate(QDate.currentDate())
            self._cargar_ventas()

        btn_hoy = QPushButton("📅  Hoy")
        btn_hoy.clicked.connect(ir_hoy)

        hl.addWidget(self._date_rep)
        hl.addWidget(btn_ver)
        hl.addWidget(btn_hoy)
        if self._es_admin:
            hl.addWidget(QLabel("Vendedor:"))
            self._combo_vendedor_rep = QComboBox()
            self._llenar_combo_vendedores(self._combo_vendedor_rep, incluir_todos=True)
            self._combo_vendedor_rep.currentIndexChanged.connect(self._cargar_ventas)
            hl.addWidget(self._combo_vendedor_rep)
        hl.addStretch()
        root.addLayout(hl)

        # ── Tarjetas resumen ────────────────────────────────
        hl_cards = QHBoxLayout()
        hl_cards.setSpacing(12)
        self._cards = {}
        for clave, titulo, color in [
            ("total",    "Total vendido",   "#89b4fa"),
            ("ganancia", "Ganancia neta",   "#a6e3a1"),
            ("costo",    "Costo vendido",   "#fab387"),
            ("num",      "No. de ventas",   "#cba6f7"),
            ("prom",     "Ticket promedio", "#f9e2af"),
        ]:
            grp = QGroupBox(titulo)
            vl = QVBoxLayout(grp)
            lbl_v = QLabel("—")
            lbl_v.setAlignment(Qt.AlignCenter)
            lbl_v.setStyleSheet(
                f"font-size: 30px; font-weight: bold; color: {color};"
            )
            vl.addWidget(lbl_v)
            self._cards[clave] = lbl_v
            hl_cards.addWidget(grp)
        root.addLayout(hl_cards)

        # ── Tabla de ventas ─────────────────────────────────
        self._tabla_ventas = QTableWidget()
        self._tabla_ventas.setColumnCount(8)
        self._tabla_ventas.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Hora", "Vendedor", "Venta", "Costo", "Ganancia", "Método de Pago"]
        )
        self._tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_ventas.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_ventas.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_ventas.setAlternatingRowColors(True)
        self._tabla_ventas.doubleClicked.connect(self._ver_detalle)
        root.addWidget(self._tabla_ventas)

        hint = QLabel("💡  Doble clic en cualquier fila para ver el detalle de esa venta.")
        hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        root.addWidget(hint)

        return w

    # ── helpers de reportes ────────────────────────────────

    def _llenar_combo_vendedores(self, combo, incluir_todos=False):
        actual = combo.currentData() if combo.count() else ""
        combo.blockSignals(True)
        combo.clear()
        if incluir_todos:
            combo.addItem("Todos los vendedores", "")
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT DISTINCT nombre
                FROM (
                    SELECT COALESCE(NULLIF(s.vendedor_nombre, ''), u.nombre) AS nombre
                    FROM sesiones_usuario s
                    JOIN usuarios u ON u.id = s.usuario_id
                    WHERE u.rol = 'vendedor'
                    UNION
                    SELECT COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre) AS nombre
                    FROM ventas v
                    LEFT JOIN usuarios u ON u.id = v.usuario_id
                    WHERE COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre) IS NOT NULL
                )
                WHERE TRIM(COALESCE(nombre, '')) <> ''
                ORDER BY nombre COLLATE NOCASE
            """)
            for (nombre,) in c.fetchall():
                combo.addItem(nombre, nombre)
        idx = combo.findData(actual)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.blockSignals(False)

    def _cargar_ventas(self):
        if not hasattr(self, "_date_rep"):
            return
        fecha = self._date_rep.date().toString("yyyy-MM-dd")

        filtros = ["v.fecha LIKE ?"]
        params = [f"{fecha}%"]
        vendedor_expr = "COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre, 'Sin usuario')"
        if self._es_admin:
            vendedor_nombre = (
                self._combo_vendedor_rep.currentData()
                if hasattr(self, "_combo_vendedor_rep") else ""
            )
            if vendedor_nombre:
                filtros.append(f"{vendedor_expr} = ?")
                params.append(vendedor_nombre)
        else:
            filtros.append(f"{vendedor_expr} = ?")
            params.append(self._nombre_operador)

        where = " AND ".join(filtros)

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                SELECT v.id, v.fecha, v.total, v.metodo_pago,
                       {vendedor_expr} AS vendedor,
                       COALESCE(SUM(
                           COALESCE(NULLIF(d.costo_total, 0),
                                    d.cantidad * COALESCE(p.precio_compra, 0),
                                    0)
                       ), 0) AS costo
                FROM ventas v
                LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                LEFT JOIN productos p ON p.id = d.producto_id
                LEFT JOIN usuarios u ON u.id = v.usuario_id
                WHERE {where}
                GROUP BY v.id, v.fecha, v.total, v.metodo_pago, vendedor
                ORDER BY v.fecha DESC
            """, params)
            ventas = c.fetchall()

        total_dia = sum(v[2] for v in ventas)
        costo_dia = sum(v[5] for v in ventas)
        ganancia_dia = total_dia - costo_dia
        num = len(ventas)

        prom = total_dia / num if num else 0.0
        self._cards["total"].setText(f"${total_dia:.2f}")
        self._cards["ganancia"].setText(f"${ganancia_dia:.2f}")
        self._cards["costo"].setText(f"${costo_dia:.2f}")
        self._cards["num"].setText(str(num))
        self._cards["prom"].setText(f"${prom:.2f}")

        self._tabla_ventas.setRowCount(len(ventas))
        for fila, (vid, fv, tot, metodo, vendedor, costo) in enumerate(ventas):
            ganancia = tot - costo
            fecha_txt, hora_txt = separar_fecha_hora(fv)
            valores = [
                str(vid), fecha_txt, hora_txt, vendedor, f"${tot:.2f}",
                f"${costo:.2f}", f"${ganancia:.2f}", metodo,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_ventas.setItem(fila, col, cell)

    def _ver_detalle(self, index):
        fila = index.row()
        vid = int(self._tabla_ventas.item(fila, 0).text())
        fecha = self._tabla_ventas.item(fila, 1).text()
        hora = self._tabla_ventas.item(fila, 2).text()
        vendedor = self._tabla_ventas.item(fila, 3).text()
        total = float(self._tabla_ventas.item(fila, 4).text().replace("$", ""))
        metodo = self._tabla_ventas.item(fila, 7).text()
        DialogoDetalleVenta(vid, f"{fecha} {hora}", total, metodo, self, vendedor).exec()

    # ══════════════════════════════════════════════════════
    # TAB — APARTADOS (ANTICIPOS DE CLIENTES)
    # ══════════════════════════════════════════════════════

    def _crear_tab_apartados(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Apartados de Clientes")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        # ── Registro de apartado nuevo ─────────────────────
        grp = QGroupBox("Registrar nuevo apartado")
        grid = QGridLayout(grp)
        grid.setSpacing(6)

        self._inp_apa_nombre = QLineEdit()
        self._inp_apa_nombre.setPlaceholderText("Nombre del cliente *")
        self._inp_apa_tel = QLineEdit()
        self._inp_apa_tel.setPlaceholderText("Teléfono (opcional)")
        self._inp_apa_correo = QLineEdit()
        self._inp_apa_correo.setPlaceholderText("Correo (opcional)")
        self._inp_apa_desc = QLineEdit()
        self._inp_apa_desc.setPlaceholderText("Ej: pastel grande, despensa, juguete...")

        self._spin_apa_monto = CasillaMonto()
        self._spin_apa_monto.setRange(0, 999_999)
        self._spin_apa_monto.setPrefix("$")
        self._spin_apa_monto.setDecimals(2)

        self._spin_apa_anticipo = CasillaMonto()
        self._spin_apa_anticipo.setRange(0, 999_999)
        self._spin_apa_anticipo.setPrefix("$")
        self._spin_apa_anticipo.setDecimals(2)

        self._combo_apa_metodo = QComboBox()
        self._combo_apa_metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])

        btn_registrar = QPushButton("💾  Registrar apartado")
        btn_registrar.setObjectName("btn_verde")
        btn_registrar.clicked.connect(self._registrar_apartado)

        grid.addWidget(QLabel("Cliente *:"),        0, 0); grid.addWidget(self._inp_apa_nombre,    0, 1)
        grid.addWidget(QLabel("Teléfono:"),         0, 2); grid.addWidget(self._inp_apa_tel,       0, 3)
        grid.addWidget(QLabel("Correo:"),           0, 4); grid.addWidget(self._inp_apa_correo,    0, 5)
        grid.addWidget(QLabel("Producto apartado:"),1, 0); grid.addWidget(self._inp_apa_desc,      1, 1)
        grid.addWidget(QLabel("Monto total *:"),    1, 2); grid.addWidget(self._spin_apa_monto,    1, 3)
        grid.addWidget(QLabel("Anticipo inicial *:"),1, 4); grid.addWidget(self._spin_apa_anticipo, 1, 5)
        grid.addWidget(QLabel("Método:"),           2, 0); grid.addWidget(self._combo_apa_metodo,  2, 1)
        grid.addWidget(btn_registrar,               2, 5)
        root.addWidget(grp)

        # ── Búsqueda y acciones ────────────────────────────
        hl = QHBoxLayout()
        self._inp_buscar_apa = QLineEdit()
        self._inp_buscar_apa.setPlaceholderText("🔍  Buscar por nombre o teléfono del cliente...")
        self._inp_buscar_apa.textChanged.connect(self._cargar_apartados)

        self._combo_estado_apa = QComboBox()
        self._combo_estado_apa.addItem("Activos", "ACTIVO")
        self._combo_estado_apa.addItem("Liquidados", "LIQUIDADO")
        self._combo_estado_apa.addItem("Cancelados", "CANCELADO")
        self._combo_estado_apa.addItem("Todos", "")
        self._combo_estado_apa.currentIndexChanged.connect(self._cargar_apartados)

        btn_abonar = QPushButton("➕  Abonar")
        btn_abonar.setObjectName("btn_verde")
        btn_abonar.clicked.connect(self._abonar_apartado)

        btn_abonos = QPushButton("📜  Ver abonos")
        btn_abonos.clicked.connect(self._ver_abonos_apartado)

        btn_liquidar = QPushButton("✅  Liquidar (convertir en venta)")
        btn_liquidar.setObjectName("btn_naranja")
        btn_liquidar.clicked.connect(self._liquidar_apartado)

        self._btn_cancelar_apa = QPushButton("❌  Cancelar apartado")
        self._btn_cancelar_apa.setObjectName("btn_rojo")
        self._btn_cancelar_apa.clicked.connect(self._cancelar_apartado)
        self._btn_cancelar_apa.setVisible(self._es_admin)

        hl.addWidget(btn_abonar)
        hl.addWidget(btn_abonos)
        hl.addWidget(btn_liquidar)
        hl.addWidget(self._btn_cancelar_apa)
        hl.addStretch()
        hl.addWidget(self._inp_buscar_apa, stretch=2)
        hl.addWidget(self._combo_estado_apa, stretch=1)
        root.addLayout(hl)

        # ── Tabla de apartados ─────────────────────────────
        self._tabla_apartados = QTableWidget()
        self._tabla_apartados.setColumnCount(10)
        self._tabla_apartados.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Teléfono", "Producto",
            "Monto", "Abonado", "Saldo", "Estado", "Vendedor",
        ])
        self._tabla_apartados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_apartados.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_apartados.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_apartados.setAlternatingRowColors(True)
        self._tabla_apartados.doubleClicked.connect(self._ver_abonos_apartado)
        root.addWidget(self._tabla_apartados)

        hint = QLabel(
            "💡  Doble clic en un apartado para ver sus abonos. Los anticipos se "
            "reflejan en el corte de caja como «Anticipo de apartado»."
        )
        hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        root.addWidget(hint)

        return w

    # ── helpers de apartados ───────────────────────────────

    def _validar_datos_cliente(self, nombre, telefono, correo):
        if not nombre.strip():
            QMessageBox.warning(self, "Falta nombre",
                                "El nombre del cliente es obligatorio.")
            return False
        if not telefono_valido(telefono):
            QMessageBox.warning(self, "Teléfono inválido",
                                "Revisa el teléfono: usa de 7 a 15 dígitos "
                                "(puede incluir espacios, guiones o +).")
            return False
        if not correo_valido(correo):
            QMessageBox.warning(self, "Correo inválido",
                                "Revisa el correo, por ejemplo: cliente@correo.com")
            return False
        return True

    def _registrar_apartado(self):
        nombre = self._inp_apa_nombre.text()
        telefono = self._inp_apa_tel.text().strip()
        correo = self._inp_apa_correo.text().strip()
        descripcion = self._inp_apa_desc.text().strip()
        monto = self._spin_apa_monto.value()
        anticipo = self._spin_apa_anticipo.value()
        metodo = self._combo_apa_metodo.currentText()

        if not self._validar_datos_cliente(nombre, telefono, correo):
            return
        if monto <= 0:
            QMessageBox.warning(self, "Monto inválido",
                                "El monto total del apartado debe ser mayor a $0.00.")
            return
        if anticipo <= 0:
            QMessageBox.warning(self, "Anticipo inválido",
                                "El anticipo inicial debe ser mayor a $0.00.")
            return
        if anticipo > monto:
            QMessageBox.warning(self, "Anticipo mayor al monto",
                                "El anticipo no puede ser mayor al monto total.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conectar() as conn:
                c = conn.cursor()
                cliente_id = obtener_o_crear_cliente(c, nombre, telefono, correo, fecha)
                c.execute("""
                    INSERT INTO apartados
                        (cliente_id, descripcion, monto_total, estado, fecha_creacion,
                         usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, ?, ?, 'ACTIVO', ?, ?, ?, ?)
                """, (
                    cliente_id, descripcion, monto, fecha,
                    self._usuario_actual["id"], self._sesion_id, self._nombre_operador,
                ))
                apartado_id = c.lastrowid
                c.execute("""
                    INSERT INTO abonos_apartado
                        (apartado_id, tipo, monto, metodo_pago, fecha,
                         usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, 'ABONO', ?, ?, ?, ?, ?, ?)
                """, (
                    apartado_id, anticipo, metodo, fecha,
                    self._usuario_actual["id"], self._sesion_id, self._nombre_operador,
                ))
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"No se pudo registrar el apartado:\n{e}")
            return

        asegurar_base_guardada()
        for campo in (self._inp_apa_nombre, self._inp_apa_tel,
                      self._inp_apa_correo, self._inp_apa_desc):
            campo.clear()
        self._spin_apa_monto.setValue(0)
        self._spin_apa_anticipo.setValue(0)
        self._cargar_apartados()
        self._perrito_evento("apartado")
        QMessageBox.information(
            self, "Apartado registrado",
            f"Apartado #{apartado_id} registrado.\n\n"
            f"Monto total: ${monto:.2f}\n"
            f"Anticipo recibido: ${anticipo:.2f} ({metodo})\n"
            f"Saldo restante: ${monto - anticipo:.2f}"
        )

    def _cargar_apartados(self, *args):
        if not hasattr(self, "_tabla_apartados"):
            return

        q = self._inp_buscar_apa.text().strip() if hasattr(self, "_inp_buscar_apa") else ""
        estado = self._combo_estado_apa.currentData() if hasattr(self, "_combo_estado_apa") else "ACTIVO"

        filtros = []
        params = []
        if estado:
            filtros.append("a.estado = ?")
            params.append(estado)
        if q:
            like = f"%{q}%"
            filtros.append("(cl.nombre LIKE ? OR cl.telefono LIKE ?)")
            params.extend([like, like])
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                SELECT a.id, a.fecha_creacion, cl.nombre, COALESCE(cl.telefono, ''),
                       a.descripcion, a.monto_total,
                       COALESCE(SUM(CASE WHEN ab.tipo = 'ABONO' THEN ab.monto ELSE 0 END), 0),
                       a.estado,
                       COALESCE(NULLIF(a.vendedor_nombre, ''), 'Sin registro')
                FROM apartados a
                JOIN clientes cl ON cl.id = a.cliente_id
                LEFT JOIN abonos_apartado ab ON ab.apartado_id = a.id
                {where}
                GROUP BY a.id, a.fecha_creacion, cl.nombre, cl.telefono,
                         a.descripcion, a.monto_total, a.estado, a.vendedor_nombre
                ORDER BY a.fecha_creacion DESC
                LIMIT 300
            """, params)
            filas = c.fetchall()

        colores = {
            "ACTIVO": None,
            "LIQUIDADO": QColor("#a6e3a1"),
            "CANCELADO": QColor("#f38ba8"),
        }
        self._tabla_apartados.setRowCount(len(filas))
        for fila, (aid, fecha, cliente, tel, desc, monto, abonado, estado_a, vendedor) in enumerate(filas):
            saldo = monto - abonado
            fecha_txt, _hora = separar_fecha_hora(fecha)
            valores = [
                str(aid), fecha_txt, cliente, tel, desc,
                f"${monto:.2f}", f"${abonado:.2f}", f"${saldo:.2f}",
                estado_a, vendedor,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if col == 8 and colores.get(estado_a):
                    cell.setBackground(colores[estado_a])
                    cell.setForeground(QColor("#1e1e2e"))
                self._tabla_apartados.setItem(fila, col, cell)

    def _apartado_seleccionado(self):
        fila = self._tabla_apartados.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un apartado de la tabla.")
            return None
        item = self._tabla_apartados.item(fila, 0)
        return int(item.text()) if item else None

    def _datos_apartado(self, apartado_id):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT a.id, cl.nombre, a.descripcion, a.monto_total, a.estado,
                       COALESCE(SUM(CASE WHEN ab.tipo = 'ABONO' THEN ab.monto ELSE 0 END), 0)
                FROM apartados a
                JOIN clientes cl ON cl.id = a.cliente_id
                LEFT JOIN abonos_apartado ab ON ab.apartado_id = a.id
                WHERE a.id = ?
                GROUP BY a.id, cl.nombre, a.descripcion, a.monto_total, a.estado
            """, (apartado_id,))
            row = c.fetchone()
        if not row:
            return None
        aid, cliente, desc, monto, estado, abonado = row
        return {
            "id": aid, "cliente": cliente, "descripcion": desc,
            "monto": monto, "estado": estado, "abonado": abonado,
            "saldo": monto - abonado,
        }

    def _abonar_apartado(self):
        apartado_id = self._apartado_seleccionado()
        if not apartado_id:
            return
        datos = self._datos_apartado(apartado_id)
        if not datos:
            return
        if datos["estado"] != "ACTIVO":
            QMessageBox.warning(self, "Apartado no activo",
                                "Solo se puede abonar a apartados activos.")
            return
        if datos["saldo"] <= 0:
            QMessageBox.information(
                self, "Apartado pagado",
                "Este apartado ya está pagado por completo.\n"
                "Usa «Liquidar» para convertirlo en venta."
            )
            return

        dlg = DialogoAbonoApartado(datos["cliente"], datos["saldo"], self)
        if dlg.exec() != QDialog.Accepted:
            return
        r = dlg.resultado()
        if r["monto"] > datos["saldo"] + 0.005:
            QMessageBox.warning(self, "Abono mayor al saldo",
                                "El abono no puede ser mayor al saldo restante.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            conn.execute("""
                INSERT INTO abonos_apartado
                    (apartado_id, tipo, monto, metodo_pago, fecha,
                     usuario_id, sesion_id, vendedor_nombre)
                VALUES (?, 'ABONO', ?, ?, ?, ?, ?, ?)
            """, (
                apartado_id, r["monto"], r["metodo"], fecha,
                self._usuario_actual["id"], self._sesion_id, self._nombre_operador,
            ))

        asegurar_base_guardada()
        self._cargar_apartados()
        self._perrito_evento("abono")
        saldo_nuevo = datos["saldo"] - r["monto"]
        msg = (
            f"Abono de ${r['monto']:.2f} ({r['metodo']}) registrado.\n"
            f"Saldo restante: ${saldo_nuevo:.2f}"
        )
        if saldo_nuevo <= 0.005:
            msg += "\n\nEl apartado quedó pagado. Usa «Liquidar» para entregarlo y convertirlo en venta."
        QMessageBox.information(self, "Abono registrado", msg)

    def _liquidar_apartado(self):
        apartado_id = self._apartado_seleccionado()
        if not apartado_id:
            return
        datos = self._datos_apartado(apartado_id)
        if not datos:
            return
        if datos["estado"] != "ACTIVO":
            QMessageBox.warning(self, "Apartado no activo",
                                "Solo se pueden liquidar apartados activos.")
            return

        dlg = DialogoLiquidarApartado(
            datos["cliente"], datos["monto"], datos["saldo"], self
        )
        if dlg.exec() != QDialog.Accepted:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conectar() as conn:
                c = conn.cursor()
                if datos["saldo"] > 0:
                    c.execute("""
                        INSERT INTO abonos_apartado
                            (apartado_id, tipo, monto, metodo_pago, fecha,
                             usuario_id, sesion_id, vendedor_nombre)
                        VALUES (?, 'ABONO', ?, ?, ?, ?, ?, ?)
                    """, (
                        apartado_id, datos["saldo"], dlg.metodo(), fecha,
                        self._usuario_actual["id"], self._sesion_id,
                        self._nombre_operador,
                    ))

                # El dinero ya entró a caja como anticipos; la venta se marca
                # con método 'Apartado' para no duplicar efectivo en el corte.
                c.execute("""
                    INSERT INTO ventas
                        (fecha, total, metodo_pago, efectivo_recibido,
                         usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, ?, 'Apartado', 0, ?, ?, ?)
                """, (
                    fecha, datos["monto"], self._usuario_actual["id"],
                    self._sesion_id, self._nombre_operador,
                ))
                vid = c.lastrowid

                c.execute("""
                    UPDATE apartados
                    SET estado = 'LIQUIDADO', fecha_cierre = ?, venta_id = ?
                    WHERE id = ? AND estado = 'ACTIVO'
                """, (fecha, vid, apartado_id))
        except Exception as e:
            QMessageBox.critical(self, "Error al liquidar",
                                 f"No se pudo liquidar el apartado:\n{e}")
            return

        asegurar_base_guardada()
        self._cargar_apartados()
        self._cargar_ventas()
        self._cargar_kpis()
        self._cargar_reportes_fuertes()
        self._cargar_analisis_rangos()
        self._perrito_evento("venta")
        QMessageBox.information(
            self, "Apartado liquidado",
            f"Apartado #{apartado_id} liquidado.\n"
            f"Se registró la venta #{vid} por ${datos['monto']:.2f} (método: Apartado)."
        )

    def _cancelar_apartado(self):
        if not self._es_admin:
            QMessageBox.warning(self, "Sin permiso",
                                "Solo el administrador puede cancelar apartados.")
            return
        apartado_id = self._apartado_seleccionado()
        if not apartado_id:
            return
        datos = self._datos_apartado(apartado_id)
        if not datos:
            return
        if datos["estado"] != "ACTIVO":
            QMessageBox.warning(self, "Apartado no activo",
                                "Solo se pueden cancelar apartados activos.")
            return

        dlg = DialogoCancelarApartado(datos["cliente"], datos["abonado"], self)
        if dlg.exec() != QDialog.Accepted:
            return
        r = dlg.resultado()

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with conectar() as conn:
            c = conn.cursor()
            if r["devolver"] and datos["abonado"] > 0:
                c.execute("""
                    INSERT INTO abonos_apartado
                        (apartado_id, tipo, monto, metodo_pago, fecha,
                         usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, 'DEVOLUCION', ?, 'Efectivo', ?, ?, ?, ?)
                """, (
                    apartado_id, datos["abonado"], fecha,
                    self._usuario_actual["id"], self._sesion_id,
                    self._nombre_operador,
                ))
            c.execute("""
                UPDATE apartados
                SET estado = 'CANCELADO', fecha_cierre = ?, notas = ?
                WHERE id = ? AND estado = 'ACTIVO'
            """, (fecha, r["motivo"], apartado_id))

        asegurar_base_guardada()
        self._cargar_apartados()
        self._cargar_kpis()
        self._perrito_evento("devolucion")
        if r["devolver"] and datos["abonado"] > 0:
            texto = (
                f"Se devolvieron ${datos['abonado']:.2f} en efectivo al cliente.\n"
                f"La devolución quedó registrada en el corte de caja."
            )
        else:
            texto = "La tienda conserva el anticipo recibido."
        QMessageBox.information(
            self, "Apartado cancelado",
            f"Apartado #{apartado_id} cancelado.\n\n{texto}"
        )

    def _ver_abonos_apartado(self, *args):
        apartado_id = self._apartado_seleccionado()
        if not apartado_id:
            return
        datos = self._datos_apartado(apartado_id)
        cliente = datos["cliente"] if datos else "Cliente"
        DialogoAbonosApartado(apartado_id, cliente, self).exec()

    # ══════════════════════════════════════════════════════
    # TAB — PRÉSTAMO DE PRODUCTOS
    # ══════════════════════════════════════════════════════

    def _crear_tab_prestamos(self):
        w = QWidget()
        self._tab_prestamos_widget = w
        root = QVBoxLayout(w)
        root.setSpacing(8)

        self._prestamo_lineas = []

        lbl = QLabel("Préstamo de Productos")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(12)

        # ── Columna izquierda: préstamo nuevo ──────────────
        izq = QVBoxLayout()
        izq.setSpacing(8)

        grp_cliente = QGroupBox("Datos del cliente")
        grid_cl = QGridLayout(grp_cliente)
        self._inp_pre_nombre = QLineEdit()
        self._inp_pre_nombre.setPlaceholderText("Nombre del cliente *")
        self._inp_pre_tel = QLineEdit()
        self._inp_pre_tel.setPlaceholderText("Teléfono (opcional)")
        self._inp_pre_correo = QLineEdit()
        self._inp_pre_correo.setPlaceholderText("Correo (opcional)")
        grid_cl.addWidget(QLabel("Cliente *:"), 0, 0); grid_cl.addWidget(self._inp_pre_nombre, 0, 1)
        grid_cl.addWidget(QLabel("Teléfono:"),  0, 2); grid_cl.addWidget(self._inp_pre_tel,    0, 3)
        grid_cl.addWidget(QLabel("Correo:"),    0, 4); grid_cl.addWidget(self._inp_pre_correo, 0, 5)
        izq.addWidget(grp_cliente)

        grp_scan = QGroupBox("Escanear / buscar por código de barras")
        hl_scan = QHBoxLayout(grp_scan)
        self._inp_codigo_prestamo = QLineEdit()
        self._inp_codigo_prestamo.setPlaceholderText(
            "Código de barras — presiona Enter o escanea"
        )
        self._inp_codigo_prestamo.returnPressed.connect(self._prestamo_agregar_por_codigo)
        btn_add_cod = QPushButton("➕  Agregar")
        btn_add_cod.clicked.connect(self._prestamo_agregar_por_codigo)
        hl_scan.addWidget(self._inp_codigo_prestamo)
        hl_scan.addWidget(btn_add_cod)
        izq.addWidget(grp_scan)

        grp_buscar = QGroupBox("Buscar producto por nombre")
        vl_buscar = QVBoxLayout(grp_buscar)
        hl_buscar = QHBoxLayout()
        self._inp_buscar_prest = QLineEdit()
        self._inp_buscar_prest.setPlaceholderText("Ej: huevo, refresco, jabón...")
        self._inp_buscar_prest.textChanged.connect(self._cargar_productos_prestamo)
        btn_add_sel = QPushButton("➕  Agregar seleccionado")
        btn_add_sel.clicked.connect(self._prestamo_agregar_seleccion)
        hl_buscar.addWidget(self._inp_buscar_prest, stretch=2)
        hl_buscar.addWidget(btn_add_sel)
        vl_buscar.addLayout(hl_buscar)

        self._tabla_busqueda_prest = QTableWidget()
        self._tabla_busqueda_prest.setColumnCount(6)
        self._tabla_busqueda_prest.setHorizontalHeaderLabels(
            ["ID", "Código", "Producto", "Categoría", "Precio", "Stock"]
        )
        self._tabla_busqueda_prest.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_busqueda_prest.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_busqueda_prest.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_busqueda_prest.setAlternatingRowColors(True)
        self._tabla_busqueda_prest.doubleClicked.connect(self._prestamo_agregar_seleccion)
        self._tabla_busqueda_prest.setMaximumHeight(160)
        self._tabla_busqueda_prest.hideColumn(0)
        vl_buscar.addWidget(self._tabla_busqueda_prest)
        izq.addWidget(grp_buscar)

        self._tabla_lineas_prestamo = QTableWidget()
        self._tabla_lineas_prestamo.setColumnCount(6)
        self._tabla_lineas_prestamo.setHorizontalHeaderLabels(
            ["ID", "Código", "Producto", "Cant.", "Precio Unit.", "Subtotal"]
        )
        self._tabla_lineas_prestamo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_lineas_prestamo.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_lineas_prestamo.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_lineas_prestamo.setAlternatingRowColors(True)
        izq.addWidget(self._tabla_lineas_prestamo)

        grp_acc = QGroupBox("Acciones del préstamo")
        hl_acc = QHBoxLayout(grp_acc)
        for texto, obj, slot in [
            ("➕  + Cantidad",     "",         self._prestamo_sumar_cantidad),
            ("➖  − Cantidad",     "",         self._prestamo_restar_cantidad),
            ("🗑   Eliminar fila", "btn_rojo", self._prestamo_eliminar_item),
            ("🧹  Limpiar todo",  "btn_rojo", self._prestamo_limpiar),
        ]:
            b = QPushButton(texto)
            if obj:
                b.setObjectName(obj)
            b.clicked.connect(slot)
            hl_acc.addWidget(b)
        izq.addWidget(grp_acc)

        hl_total = QHBoxLayout()
        self._lbl_total_prestamo = QLabel("Valor del préstamo: $0.00")
        self._lbl_total_prestamo.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #a6e3a1;"
        )
        btn_registrar = QPushButton("🤝  Registrar préstamo")
        btn_registrar.setObjectName("btn_verde")
        btn_registrar.clicked.connect(self._registrar_prestamo)
        hl_total.addWidget(self._lbl_total_prestamo)
        hl_total.addStretch()
        hl_total.addWidget(btn_registrar)
        izq.addLayout(hl_total)

        cuerpo.addLayout(izq, stretch=3)

        # ── Columna derecha: préstamos registrados ─────────
        der = QVBoxLayout()
        der.setSpacing(8)

        grp_lista = QGroupBox("Control de préstamos")
        vl_lista = QVBoxLayout(grp_lista)

        hl_filtros = QHBoxLayout()
        self._inp_buscar_pre = QLineEdit()
        self._inp_buscar_pre.setPlaceholderText("🔍  Buscar por nombre o teléfono...")
        self._inp_buscar_pre.textChanged.connect(self._cargar_prestamos)
        self._combo_estado_pre = QComboBox()
        self._combo_estado_pre.addItem("Activos", "ACTIVO")
        self._combo_estado_pre.addItem("Cerrados", "CERRADO")
        self._combo_estado_pre.addItem("Todos", "")
        self._combo_estado_pre.currentIndexChanged.connect(self._cargar_prestamos)
        hl_filtros.addWidget(self._inp_buscar_pre, stretch=2)
        hl_filtros.addWidget(self._combo_estado_pre, stretch=1)
        vl_lista.addLayout(hl_filtros)

        self._tabla_prestamos = QTableWidget()
        self._tabla_prestamos.setColumnCount(8)
        self._tabla_prestamos.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Teléfono",
            "Artículos", "Pendiente", "Estado", "Vendedor",
        ])
        self._tabla_prestamos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_prestamos.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_prestamos.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_prestamos.setAlternatingRowColors(True)
        self._tabla_prestamos.doubleClicked.connect(self._ver_detalle_prestamo)
        vl_lista.addWidget(self._tabla_prestamos)

        btn_detalle = QPushButton("📋  Ver detalle / devolver / cobrar")
        btn_detalle.setObjectName("btn_naranja")
        btn_detalle.clicked.connect(self._ver_detalle_prestamo)
        vl_lista.addWidget(btn_detalle)

        hint = QLabel(
            "💡  Doble clic en un préstamo para devolver productos al inventario "
            "o cobrarlos como venta."
        )
        hint.setStyleSheet("color: #6c7086; font-size: 11px;")
        hint.setWordWrap(True)
        vl_lista.addWidget(hint)

        der.addWidget(grp_lista)
        cuerpo.addLayout(der, stretch=2)
        root.addLayout(cuerpo)

        return w

    # ── helpers de préstamos ───────────────────────────────

    def _enfocar_codigo_prestamo(self):
        if hasattr(self, "_inp_codigo_prestamo"):
            self._inp_codigo_prestamo.setFocus(Qt.OtherFocusReason)
            self._inp_codigo_prestamo.selectAll()

    def _cargar_productos_prestamo(self, *args):
        if not hasattr(self, "_tabla_busqueda_prest"):
            return

        q = self._inp_buscar_prest.text().strip() if hasattr(self, "_inp_buscar_prest") else ""
        filtros = ["activo = 1"]
        params = []
        if q:
            like = f"%{q}%"
            filtros.append("(nombre LIKE ? OR codigo_barras LIKE ? OR categoria LIKE ?)")
            params.extend([like, like, like])

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                SELECT id, codigo_barras, nombre, categoria, precio_venta, stock, stock_minimo
                FROM productos
                WHERE {' AND '.join(filtros)}
                ORDER BY categoria COLLATE NOCASE, nombre COLLATE NOCASE
                LIMIT 120
            """, params)
            rows = c.fetchall()

        self._tabla_busqueda_prest.setRowCount(len(rows))
        C_ROJO = QColor("#f38ba8")
        C_AMAR = QColor("#f9e2af")
        C_DARK = QColor("#1e1e2e")
        for fila, (pid, cod, nom, cat, precio, stock, minimo) in enumerate(rows):
            vals = [
                str(pid), codigo_visible(cod), nom, cat or "",
                f"${precio:.2f}", str(stock),
            ]
            for col, val in enumerate(vals):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if stock == 0:
                    cell.setBackground(C_ROJO)
                    cell.setForeground(C_DARK)
                elif stock <= minimo:
                    cell.setBackground(C_AMAR)
                    cell.setForeground(C_DARK)
                self._tabla_busqueda_prest.setItem(fila, col, cell)

    def _prestamo_agregar_por_codigo(self):
        codigo = self._inp_codigo_prestamo.text().strip()
        if not codigo:
            return
        self._inp_codigo_prestamo.clear()

        prod = self._buscar_producto_por_codigo(codigo)
        if not prod:
            QMessageBox.warning(self, "No encontrado",
                                "Código no registrado en inventario activo.")
            self._enfocar_codigo_prestamo()
            return
        self._prestamo_agregar_producto(prod)

    def _prestamo_agregar_seleccion(self, *args):
        fila = self._tabla_busqueda_prest.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona un producto de la búsqueda.")
            return
        item_id = self._tabla_busqueda_prest.item(fila, 0)
        if not item_id:
            return
        prod = self._buscar_producto_por_id(int(item_id.text()))
        if not prod:
            QMessageBox.warning(self, "No disponible",
                                "El producto ya no está activo o no existe.")
            self._cargar_productos_prestamo()
            return
        self._prestamo_agregar_producto(prod)
        self._inp_buscar_prest.clear()
        self._tabla_busqueda_prest.clearSelection()

    def _prestamo_agregar_producto(self, prod):
        pid, cod, nombre, precio, stock, costo = prod

        if stock <= 0:
            QMessageBox.warning(self, "Sin existencia",
                                f"«{nombre}» no tiene stock disponible.")
            self._enfocar_codigo_prestamo()
            return

        for item in self._prestamo_lineas:
            if item["pid"] == pid:
                if item["cant"] >= stock:
                    QMessageBox.warning(
                        self, "Stock insuficiente",
                        f"Solo hay {stock} unidades disponibles de «{nombre}»."
                    )
                    self._enfocar_codigo_prestamo()
                    return
                item["cant"] += 1
                item["sub"] = item["cant"] * item["precio"]
                item["stock"] = stock
                item["costo"] = costo
                self._refrescar_lineas_prestamo()
                self._enfocar_codigo_prestamo()
                return

        self._prestamo_lineas.append({
            "pid": pid, "codigo": cod, "nombre": nombre,
            "cant": 1, "precio": precio, "costo": costo,
            "sub": precio, "stock": stock,
        })
        self._refrescar_lineas_prestamo()
        self._statusbar.showMessage(f"«{nombre}» agregado al préstamo.", 2500)
        self._enfocar_codigo_prestamo()

    def _refrescar_lineas_prestamo(self):
        self._tabla_lineas_prestamo.setRowCount(len(self._prestamo_lineas))
        total = 0.0
        for fila, item in enumerate(self._prestamo_lineas):
            total += item["sub"]
            vals = [
                str(item["pid"]), codigo_visible(item["codigo"]), item["nombre"],
                str(item["cant"]), f"${item['precio']:.2f}", f"${item['sub']:.2f}",
            ]
            for col, val in enumerate(vals):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_lineas_prestamo.setItem(fila, col, cell)
        self._lbl_total_prestamo.setText(f"Valor del préstamo: ${total:.2f}")

    def _fila_linea_prestamo(self):
        f = self._tabla_lineas_prestamo.currentRow()
        if f < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un producto del préstamo.")
        return f

    def _prestamo_sumar_cantidad(self):
        f = self._fila_linea_prestamo()
        if f < 0:
            return
        item = self._prestamo_lineas[f]
        prod = self._buscar_producto_por_id(item["pid"])
        if not prod:
            QMessageBox.warning(self, "Producto no disponible",
                                "El producto ya no está activo en inventario.")
            return
        stock_actual = prod[4]
        item["stock"] = stock_actual
        if item["cant"] >= stock_actual:
            QMessageBox.warning(self, "Límite de stock",
                                f"Solo hay {stock_actual} unidades disponibles.")
            return
        item["cant"] += 1
        item["sub"] = item["cant"] * item["precio"]
        self._refrescar_lineas_prestamo()

    def _prestamo_restar_cantidad(self):
        f = self._fila_linea_prestamo()
        if f < 0:
            return
        item = self._prestamo_lineas[f]
        if item["cant"] > 1:
            item["cant"] -= 1
            item["sub"] = item["cant"] * item["precio"]
        else:
            self._prestamo_lineas.pop(f)
        self._refrescar_lineas_prestamo()

    def _prestamo_eliminar_item(self):
        f = self._fila_linea_prestamo()
        if f < 0:
            return
        self._prestamo_lineas.pop(f)
        self._refrescar_lineas_prestamo()

    def _prestamo_limpiar(self):
        self._prestamo_lineas.clear()
        for campo in (self._inp_pre_nombre, self._inp_pre_tel, self._inp_pre_correo):
            campo.clear()
        self._refrescar_lineas_prestamo()

    def _registrar_prestamo(self):
        nombre = self._inp_pre_nombre.text()
        telefono = self._inp_pre_tel.text().strip()
        correo = self._inp_pre_correo.text().strip()

        if not self._validar_datos_cliente(nombre, telefono, correo):
            return
        if not self._prestamo_lineas:
            QMessageBox.warning(self, "Préstamo vacío",
                                "Agrega productos al préstamo antes de registrarlo.")
            return

        total = sum(i["sub"] for i in self._prestamo_lineas)
        r = QMessageBox.question(
            self, "Registrar préstamo",
            f"Se prestarán {len(self._prestamo_lineas)} producto(s) con valor de "
            f"${total:.2f} a «{' '.join(nombre.split())}».\n\n"
            f"El stock se descontará del inventario hasta su devolución o cobro.\n"
            f"¿Continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if r != QMessageBox.Yes:
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conectar() as conn:
                c = conn.cursor()
                for item in self._prestamo_lineas:
                    c.execute("""
                        SELECT nombre, stock, activo, precio_compra
                        FROM productos WHERE id = ?
                    """, (item["pid"],))
                    row = c.fetchone()
                    if not row or row[2] != 1:
                        raise ValueError(f"«{item['nombre']}» ya no está activo.")
                    nombre_actual, stock_actual, _activo, costo_actual = row
                    if stock_actual < item["cant"]:
                        raise ValueError(
                            f"Stock insuficiente para «{nombre_actual}». "
                            f"Disponible: {stock_actual}, en préstamo: {item['cant']}."
                        )
                    item["costo"] = costo_actual

                cliente_id = obtener_o_crear_cliente(c, nombre, telefono, correo, fecha)
                c.execute("""
                    INSERT INTO prestamos
                        (cliente_id, fecha, estado, usuario_id, sesion_id, vendedor_nombre)
                    VALUES (?, ?, 'ACTIVO', ?, ?, ?)
                """, (
                    cliente_id, fecha, self._usuario_actual["id"],
                    self._sesion_id, self._nombre_operador,
                ))
                prestamo_id = c.lastrowid

                for item in self._prestamo_lineas:
                    c.execute("""
                        INSERT INTO detalle_prestamos
                            (prestamo_id, producto_id, cantidad, precio_unitario,
                             costo_unitario, estado, fecha_estado)
                        VALUES (?, ?, ?, ?, ?, 'PRESTADO', ?)
                    """, (
                        prestamo_id, item["pid"], item["cant"], item["precio"],
                        item.get("costo", 0) or 0, fecha,
                    ))
                    c.execute(
                        "UPDATE productos SET stock = stock - ? WHERE id = ?",
                        (item["cant"], item["pid"])
                    )
                    c.execute("""
                        INSERT INTO movimientos_inventario
                            (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                        VALUES (?, 'SALIDA', ?, ?, ?)
                    """, (item["pid"], item["cant"],
                          f"Préstamo #{prestamo_id}", fecha))
        except Exception as e:
            QMessageBox.critical(self, "Error al registrar",
                                 f"No se pudo registrar el préstamo:\n{e}")
            return

        asegurar_base_guardada()
        self._prestamo_limpiar()
        self._cargar_prestamos()
        self._cargar_productos()
        self._cargar_productos_pos()
        self._cargar_productos_prestamo()
        self._perrito_evento("prestamo")
        QMessageBox.information(
            self, "Préstamo registrado",
            f"Préstamo #{prestamo_id} registrado por ${total:.2f}.\n"
            f"El inventario quedó descontado."
        )

    def _cargar_prestamos(self, *args):
        if not hasattr(self, "_tabla_prestamos"):
            return

        q = self._inp_buscar_pre.text().strip() if hasattr(self, "_inp_buscar_pre") else ""
        estado = self._combo_estado_pre.currentData() if hasattr(self, "_combo_estado_pre") else "ACTIVO"

        filtros = []
        params = []
        if estado:
            filtros.append("p.estado = ?")
            params.append(estado)
        if q:
            like = f"%{q}%"
            filtros.append("(cl.nombre LIKE ? OR cl.telefono LIKE ?)")
            params.extend([like, like])
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                SELECT p.id, p.fecha, cl.nombre, COALESCE(cl.telefono, ''),
                       COALESCE(SUM(d.cantidad), 0),
                       COALESCE(SUM(CASE WHEN d.estado = 'PRESTADO'
                                         THEN d.cantidad * d.precio_unitario
                                         ELSE 0 END), 0),
                       p.estado,
                       COALESCE(NULLIF(p.vendedor_nombre, ''), 'Sin registro')
                FROM prestamos p
                JOIN clientes cl ON cl.id = p.cliente_id
                LEFT JOIN detalle_prestamos d ON d.prestamo_id = p.id
                {where}
                GROUP BY p.id, p.fecha, cl.nombre, cl.telefono,
                         p.estado, p.vendedor_nombre
                ORDER BY p.fecha DESC
                LIMIT 300
            """, params)
            filas = c.fetchall()

        self._tabla_prestamos.setRowCount(len(filas))
        for fila, (pid, fecha, cliente, tel, articulos, pendiente, estado_p, vendedor) in enumerate(filas):
            fecha_txt, _hora = separar_fecha_hora(fecha)
            valores = [
                str(pid), fecha_txt, cliente, tel, str(articulos),
                f"${pendiente:.2f}", estado_p, vendedor,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                if col == 6 and estado_p == "CERRADO":
                    cell.setBackground(QColor("#a6e3a1"))
                    cell.setForeground(QColor("#1e1e2e"))
                self._tabla_prestamos.setItem(fila, col, cell)

    def _ver_detalle_prestamo(self, *args):
        fila = self._tabla_prestamos.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un préstamo de la tabla.")
            return
        item = self._tabla_prestamos.item(fila, 0)
        if not item:
            return
        prestamo_id = int(item.text())

        contexto = {
            "usuario_id": self._usuario_actual["id"],
            "sesion_id": self._sesion_id,
            "vendedor": self._nombre_operador,
        }
        dlg = DialogoDetallePrestamo(prestamo_id, contexto, self)
        dlg.exec()

        if dlg.cambios:
            self._cargar_prestamos()
            self._cargar_productos()
            self._cargar_productos_pos()
            self._cargar_productos_prestamo()
            self._cargar_ventas()
            self._cargar_kpis()
            self._cargar_reportes_fuertes()
            self._cargar_analisis_rangos()
            if dlg.hubo_cobro:
                self._perrito_evento("venta")
            elif dlg.hubo_devolucion:
                self._perrito_evento("devolucion")

    # ══════════════════════════════════════════════════════
    # TAB 4 — KPIs DEL ADMINISTRADOR
    # ══════════════════════════════════════════════════════

    def _crear_tab_kpis(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("KPIs y Análisis de Vendedores")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Fecha:"))
        self._date_kpi = QDateEdit(QDate.currentDate())
        self._date_kpi.setCalendarPopup(True)
        self._date_kpi.setDisplayFormat("dd/MM/yyyy")

        btn_ver = QPushButton("🔍  Ver KPIs")
        btn_ver.clicked.connect(self._cargar_kpis)

        def ir_hoy():
            self._date_kpi.setDate(QDate.currentDate())
            self._cargar_kpis()

        btn_hoy = QPushButton("📅  Hoy")
        btn_hoy.clicked.connect(ir_hoy)

        hl.addWidget(self._date_kpi)
        hl.addWidget(btn_ver)
        hl.addWidget(btn_hoy)
        hl.addWidget(QLabel("Vendedor:"))
        self._combo_vendedor_kpi = QComboBox()
        self._llenar_combo_vendedores(self._combo_vendedor_kpi, incluir_todos=True)
        self._combo_vendedor_kpi.currentIndexChanged.connect(self._cargar_kpis)
        hl.addWidget(self._combo_vendedor_kpi)
        hl.addStretch()
        root.addLayout(hl)

        hl_cards = QHBoxLayout()
        hl_cards.setSpacing(12)
        self._cards_kpi = {}
        for clave, titulo, color in [
            ("total", "Venta total", "#89b4fa"),
            ("ganancia", "Ganancia neta", "#a6e3a1"),
            ("costo", "Costo vendido", "#fab387"),
            ("ventas", "No. de ventas", "#cba6f7"),
            ("mejor", "Mejor vendedor", "#f9e2af"),
        ]:
            grp = QGroupBox(titulo)
            vl = QVBoxLayout(grp)
            lbl_v = QLabel("—")
            lbl_v.setAlignment(Qt.AlignCenter)
            lbl_v.setWordWrap(True)
            lbl_v.setStyleSheet(
                f"font-size: 25px; font-weight: bold; color: {color};"
            )
            vl.addWidget(lbl_v)
            self._cards_kpi[clave] = lbl_v
            hl_cards.addWidget(grp)
        root.addLayout(hl_cards)

        grp_vendedores = QGroupBox("Resumen por vendedor")
        vl_vendedores = QVBoxLayout(grp_vendedores)
        self._tabla_kpi_vendedores = QTableWidget()
        self._tabla_kpi_vendedores.setColumnCount(6)
        self._tabla_kpi_vendedores.setHorizontalHeaderLabels([
            "Vendedor", "Ventas", "Total", "Costo", "Ganancia", "Ticket Prom."
        ])
        self._tabla_kpi_vendedores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_kpi_vendedores.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_kpi_vendedores.setAlternatingRowColors(True)
        vl_vendedores.addWidget(self._tabla_kpi_vendedores)
        root.addWidget(grp_vendedores)

        grp_sesiones = QGroupBox("Cortes de caja del día")
        vl_sesiones = QVBoxLayout(grp_sesiones)
        self._tabla_kpi_sesiones = QTableWidget()
        self._tabla_kpi_sesiones.setColumnCount(14)
        self._tabla_kpi_sesiones.setHorizontalHeaderLabels([
            "Usuario", "Rol", "Inicio", "Fin", "Fondo", "Efectivo",
            "Tarjeta", "Transfer.", "Otro", "Anticipos", "Esperado",
            "Contado", "Diferencia", "Observaciones"
        ])
        self._tabla_kpi_sesiones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_kpi_sesiones.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_kpi_sesiones.setAlternatingRowColors(True)
        vl_sesiones.addWidget(self._tabla_kpi_sesiones)
        root.addWidget(grp_sesiones)

        grp_horas = QGroupBox("Ventas por hora")
        vl_horas = QVBoxLayout(grp_horas)
        self._tabla_kpi_horas = QTableWidget()
        self._tabla_kpi_horas.setColumnCount(4)
        self._tabla_kpi_horas.setHorizontalHeaderLabels([
            "Hora", "Ventas", "Total", "Ganancia"
        ])
        self._tabla_kpi_horas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_kpi_horas.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_kpi_horas.setAlternatingRowColors(True)
        vl_horas.addWidget(self._tabla_kpi_horas)
        root.addWidget(grp_horas)

        return w

    def _cargar_kpis(self):
        if not self._es_admin or not hasattr(self, "_date_kpi"):
            return

        fecha = self._date_kpi.date().toString("yyyy-MM-dd")
        vendedor_nombre = (
            self._combo_vendedor_kpi.currentData()
            if hasattr(self, "_combo_vendedor_kpi") else ""
        )
        vendedor_venta_expr = "COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre, 'Sin usuario')"
        vendedor_sesion_expr = "COALESCE(NULLIF(s.vendedor_nombre, ''), u.nombre, 'Sin usuario')"
        filtro_vendedor = f" AND {vendedor_venta_expr} = ?" if vendedor_nombre else ""
        params_vendedor = [vendedor_nombre] if vendedor_nombre else []
        filtro_sesion_vendedor = f" AND {vendedor_sesion_expr} = ?" if vendedor_nombre else ""
        params_sesion_vendedor = [vendedor_nombre] if vendedor_nombre else []
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with conectar() as conn:
            c = conn.cursor()
            c.execute(f"""
                WITH ventas_costos AS (
                    SELECT v.id, v.fecha, v.total,
                           {vendedor_venta_expr} AS vendedor,
                           COALESCE(SUM(
                               COALESCE(NULLIF(d.costo_total, 0),
                                        d.cantidad * COALESCE(p.precio_compra, 0),
                                        0)
                           ), 0) AS costo
                    FROM ventas v
                    LEFT JOIN usuarios u ON u.id = v.usuario_id
                    LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                    LEFT JOIN productos p ON p.id = d.producto_id
                    WHERE v.fecha LIKE ? {filtro_vendedor}
                    GROUP BY v.id, v.fecha, v.total, vendedor
                )
                SELECT vendedor,
                       COUNT(*) AS ventas,
                       COALESCE(SUM(total), 0) AS total,
                       COALESCE(SUM(costo), 0) AS costo,
                       COALESCE(SUM(total - costo), 0) AS ganancia,
                       COALESCE(AVG(total), 0) AS promedio
                FROM ventas_costos
                GROUP BY vendedor
                ORDER BY total DESC
            """, [f"{fecha}%"] + params_vendedor)
            por_vendedor = c.fetchall()

            c.execute(f"""
                WITH ventas_costos AS (
                    SELECT v.id, v.fecha, v.total,
                           COALESCE(SUM(
                               COALESCE(NULLIF(d.costo_total, 0),
                                        d.cantidad * COALESCE(p.precio_compra, 0),
                                        0)
                           ), 0) AS costo
                    FROM ventas v
                    LEFT JOIN usuarios u ON u.id = v.usuario_id
                    LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                    LEFT JOIN productos p ON p.id = d.producto_id
                    WHERE v.fecha LIKE ? {filtro_vendedor}
                    GROUP BY v.id, v.fecha, v.total
                )
                SELECT strftime('%H', fecha) || ':00' AS hora,
                       COUNT(*) AS ventas,
                       COALESCE(SUM(total), 0) AS total,
                       COALESCE(SUM(total - costo), 0) AS ganancia
                FROM ventas_costos
                GROUP BY strftime('%H', fecha)
                ORDER BY strftime('%H', fecha)
            """, [f"{fecha}%"] + params_vendedor)
            por_hora = c.fetchall()

            c.execute(f"""
                SELECT {vendedor_sesion_expr} AS vendedor, u.rol, s.inicio, COALESCE(s.fin, ''),
                       COALESCE(s.fondo_inicial, 0),
                       COALESCE(SUM(CASE WHEN v.metodo_pago = 'Efectivo' THEN v.total ELSE 0 END), 0),
                       COALESCE(SUM(CASE WHEN v.metodo_pago = 'Tarjeta' THEN v.total ELSE 0 END), 0),
                       COALESCE(SUM(CASE WHEN v.metodo_pago = 'Transferencia' THEN v.total ELSE 0 END), 0),
                       COALESCE(SUM(CASE WHEN v.metodo_pago = 'Otro' THEN v.total ELSE 0 END), 0),
                       COALESCE(aa.anticipos_efectivo, 0),
                       COALESCE(s.efectivo_contado, 0),
                       COALESCE(s.diferencia_efectivo, 0),
                       COALESCE(s.observaciones, ''),
                       s.estado
                FROM sesiones_usuario s
                JOIN usuarios u ON u.id = s.usuario_id
                LEFT JOIN (
                    SELECT sesion_id,
                           SUM(CASE WHEN tipo = 'ABONO' AND metodo_pago = 'Efectivo'
                                    THEN monto
                                    WHEN tipo = 'DEVOLUCION' THEN -monto
                                    ELSE 0 END) AS anticipos_efectivo
                    FROM abonos_apartado
                    WHERE sesion_id IS NOT NULL
                    GROUP BY sesion_id
                ) aa ON aa.sesion_id = s.id
                LEFT JOIN ventas v
                    ON v.sesion_id = s.id
                    OR (
                        v.sesion_id IS NULL
                        AND v.usuario_id = s.usuario_id
                        AND v.fecha >= s.inicio
                        AND v.fecha <= COALESCE(s.fin, ?)
                    )
                WHERE s.inicio LIKE ? {filtro_sesion_vendedor}
                GROUP BY s.id, vendedor, u.rol, s.inicio, s.fin,
                         s.fondo_inicial, aa.anticipos_efectivo,
                         s.efectivo_contado, s.diferencia_efectivo,
                         s.observaciones, s.estado
                ORDER BY s.inicio DESC
            """, [ahora, f"{fecha}%"] + params_sesion_vendedor)
            sesiones = c.fetchall()

        total_dia = sum(r[2] for r in por_vendedor)
        costo_dia = sum(r[3] for r in por_vendedor)
        ganancia_dia = sum(r[4] for r in por_vendedor)
        ventas_dia = sum(r[1] for r in por_vendedor)
        mejor = por_vendedor[0][0] if por_vendedor else "—"

        self._cards_kpi["total"].setText(f"${total_dia:.2f}")
        self._cards_kpi["ganancia"].setText(f"${ganancia_dia:.2f}")
        self._cards_kpi["costo"].setText(f"${costo_dia:.2f}")
        self._cards_kpi["ventas"].setText(str(ventas_dia))
        self._cards_kpi["mejor"].setText(mejor)

        self._tabla_kpi_vendedores.setRowCount(len(por_vendedor))
        for fila, (vendedor, ventas, total, costo, ganancia, promedio) in enumerate(por_vendedor):
            valores = [
                vendedor, str(ventas), f"${total:.2f}", f"${costo:.2f}",
                f"${ganancia:.2f}", f"${promedio:.2f}",
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_kpi_vendedores.setItem(fila, col, cell)

        self._tabla_kpi_horas.setRowCount(len(por_hora))
        for fila, (hora, ventas, total, ganancia) in enumerate(por_hora):
            valores = [hora, str(ventas), f"${total:.2f}", f"${ganancia:.2f}"]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_kpi_horas.setItem(fila, col, cell)

        self._tabla_kpi_sesiones.setRowCount(len(sesiones))
        for fila, (
            nombre, rol, inicio, fin, fondo, efectivo, tarjeta,
            transferencia, otro, anticipos, contado, diferencia,
            observaciones, estado
        ) in enumerate(sesiones):
            _fecha_inicio, hora_inicio = separar_fecha_hora(inicio)
            _fecha_fin, hora_fin = separar_fecha_hora(fin) if fin else ("", "")
            esperado = fondo + efectivo + anticipos
            valores = [
                nombre, rol, hora_inicio, hora_fin or estado,
                f"${fondo:.2f}", f"${efectivo:.2f}", f"${tarjeta:.2f}",
                f"${transferencia:.2f}", f"${otro:.2f}", f"${anticipos:.2f}",
                f"${esperado:.2f}", f"${contado:.2f}", f"${diferencia:.2f}",
                observaciones,
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_kpi_sesiones.setItem(fila, col, cell)

    # ══════════════════════════════════════════════════════
    # TAB 5 — COMPRAS A PROVEEDORES
    # ══════════════════════════════════════════════════════

    def _crear_tab_compras(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        self._lineas_compra = []

        lbl = QLabel("Compras a Proveedores")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        grp_prov = QGroupBox("Registrar proveedor")
        grid_prov = QGridLayout(grp_prov)
        self._inp_prov_nombre = QLineEdit()
        self._inp_prov_nombre.setPlaceholderText("Nombre del proveedor")
        self._inp_prov_tel = QLineEdit()
        self._inp_prov_tel.setPlaceholderText("Teléfono")
        self._inp_prov_notas = QLineEdit()
        self._inp_prov_notas.setPlaceholderText("Notas")
        btn_prov = QPushButton("➕  Guardar proveedor")
        btn_prov.clicked.connect(self._guardar_proveedor)

        grid_prov.addWidget(QLabel("Nombre:"), 0, 0)
        grid_prov.addWidget(self._inp_prov_nombre, 0, 1)
        grid_prov.addWidget(QLabel("Teléfono:"), 0, 2)
        grid_prov.addWidget(self._inp_prov_tel, 0, 3)
        grid_prov.addWidget(QLabel("Notas:"), 1, 0)
        grid_prov.addWidget(self._inp_prov_notas, 1, 1, 1, 3)
        grid_prov.addWidget(btn_prov, 0, 4, 2, 1)
        root.addWidget(grp_prov)

        grp_compra = QGroupBox("Nueva compra / entrada de mercancía")
        grid = QGridLayout(grp_compra)

        self._combo_proveedor_compra = QComboBox()
        self._combo_producto_compra = QComboBox()
        self._combo_producto_compra.currentIndexChanged.connect(self._cargar_precio_producto_compra)

        self._spin_compra_cantidad = CasillaEntero()
        self._spin_compra_cantidad.setRange(1, 999_999)

        self._spin_compra_costo = CasillaMonto()
        self._spin_compra_costo.setRange(0, 999_999)
        self._spin_compra_costo.setPrefix("$")
        self._spin_compra_costo.setDecimals(2)

        self._spin_compra_venta = CasillaMonto()
        self._spin_compra_venta.setRange(0, 999_999)
        self._spin_compra_venta.setPrefix("$")
        self._spin_compra_venta.setDecimals(2)

        self._inp_compra_notas = QLineEdit()
        self._inp_compra_notas.setPlaceholderText("Notas de la compra")

        btn_agregar = QPushButton("➕  Agregar línea")
        btn_agregar.clicked.connect(self._agregar_linea_compra)

        btn_guardar = QPushButton("💾  Guardar compra")
        btn_guardar.setObjectName("btn_verde")
        btn_guardar.clicked.connect(self._guardar_compra)

        btn_limpiar = QPushButton("🧹  Limpiar compra")
        btn_limpiar.clicked.connect(self._limpiar_compra)

        self._lbl_total_compra = QLabel("Total compra: $0.00")
        self._lbl_total_compra.setStyleSheet("font-size: 18px; font-weight: bold; color: #a6e3a1;")

        grid.addWidget(QLabel("Proveedor:"), 0, 0)
        grid.addWidget(self._combo_proveedor_compra, 0, 1)
        grid.addWidget(QLabel("Producto:"), 0, 2)
        grid.addWidget(self._combo_producto_compra, 0, 3)
        grid.addWidget(QLabel("Cantidad:"), 1, 0)
        grid.addWidget(self._spin_compra_cantidad, 1, 1)
        grid.addWidget(QLabel("Costo unitario:"), 1, 2)
        grid.addWidget(self._spin_compra_costo, 1, 3)
        grid.addWidget(QLabel("Precio venta:"), 1, 4)
        grid.addWidget(self._spin_compra_venta, 1, 5)
        grid.addWidget(QLabel("Notas:"), 2, 0)
        grid.addWidget(self._inp_compra_notas, 2, 1, 1, 3)
        grid.addWidget(btn_agregar, 2, 4)
        grid.addWidget(btn_guardar, 2, 5)
        grid.addWidget(btn_limpiar, 2, 6)
        grid.addWidget(self._lbl_total_compra, 3, 0, 1, 7)
        root.addWidget(grp_compra)

        self._tabla_lineas_compra = QTableWidget()
        self._tabla_lineas_compra.setColumnCount(6)
        self._tabla_lineas_compra.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Costo Unit.", "Precio Venta", "Subtotal", "ID"
        ])
        self._tabla_lineas_compra.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_lineas_compra.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_lineas_compra.setAlternatingRowColors(True)
        self._tabla_lineas_compra.hideColumn(5)
        root.addWidget(self._tabla_lineas_compra)

        grp_hist = QGroupBox("Historial de compras recientes")
        vl_hist = QVBoxLayout(grp_hist)
        self._tabla_hist_compras = QTableWidget()
        self._tabla_hist_compras.setColumnCount(5)
        self._tabla_hist_compras.setHorizontalHeaderLabels([
            "ID", "Fecha", "Proveedor", "Total", "Usuario"
        ])
        self._tabla_hist_compras.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_hist_compras.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_hist_compras.setAlternatingRowColors(True)
        vl_hist.addWidget(self._tabla_hist_compras)
        root.addWidget(grp_hist)

        self._cargar_proveedores_compra()
        self._cargar_productos_compra()
        return w

    def _guardar_proveedor(self):
        nombre = self._inp_prov_nombre.text().strip()
        telefono = self._inp_prov_tel.text().strip()
        notas = self._inp_prov_notas.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Falta proveedor",
                                "Escribe el nombre del proveedor.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conectar() as conn:
                conn.execute("""
                    INSERT INTO proveedores (nombre, telefono, notas, fecha_alta)
                    VALUES (?, ?, ?, ?)
                """, (nombre, telefono, notas, fecha))
            self._inp_prov_nombre.clear()
            self._inp_prov_tel.clear()
            self._inp_prov_notas.clear()
            self._cargar_proveedores_compra()
            QMessageBox.information(self, "Proveedor guardado",
                                    "Proveedor registrado correctamente.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Proveedor duplicado",
                                "Ya existe un proveedor con ese nombre.")

    def _cargar_proveedores_compra(self):
        if not hasattr(self, "_combo_proveedor_compra"):
            return
        actual = self._combo_proveedor_compra.currentData() if self._combo_proveedor_compra.count() else None
        self._combo_proveedor_compra.blockSignals(True)
        self._combo_proveedor_compra.clear()
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, nombre
                FROM proveedores
                WHERE activo = 1
                ORDER BY nombre COLLATE NOCASE
            """)
            for pid, nombre in c.fetchall():
                self._combo_proveedor_compra.addItem(nombre, pid)
        idx = self._combo_proveedor_compra.findData(actual)
        if idx >= 0:
            self._combo_proveedor_compra.setCurrentIndex(idx)
        self._combo_proveedor_compra.blockSignals(False)

    def _cargar_productos_compra(self):
        if not hasattr(self, "_combo_producto_compra"):
            return
        actual = self._combo_producto_compra.currentData() if self._combo_producto_compra.count() else None
        self._combo_producto_compra.blockSignals(True)
        self._combo_producto_compra.clear()
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, nombre, codigo_barras
                FROM productos
                WHERE activo = 1
                ORDER BY nombre COLLATE NOCASE
            """)
            for pid, nombre, codigo in c.fetchall():
                self._combo_producto_compra.addItem(f"{nombre} ({codigo_visible(codigo)})", pid)
        idx = self._combo_producto_compra.findData(actual)
        self._combo_producto_compra.setCurrentIndex(idx if idx >= 0 else 0)
        self._combo_producto_compra.blockSignals(False)
        self._cargar_precio_producto_compra()

    def _cargar_precio_producto_compra(self, *args):
        if not hasattr(self, "_combo_producto_compra"):
            return
        pid = self._combo_producto_compra.currentData()
        if not pid:
            return
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT precio_compra, precio_venta
                FROM productos
                WHERE id = ?
            """, (pid,))
            row = c.fetchone()
        if row:
            self._spin_compra_costo.setValue(row[0])
            self._spin_compra_venta.setValue(row[1])

    def _agregar_linea_compra(self):
        producto_id = self._combo_producto_compra.currentData()
        if not producto_id:
            QMessageBox.warning(self, "Sin producto",
                                "Selecciona un producto para la compra.")
            return
        cantidad = self._spin_compra_cantidad.value()
        costo = self._spin_compra_costo.value()
        venta = self._spin_compra_venta.value()
        if costo <= 0:
            QMessageBox.warning(self, "Costo inválido",
                                "El costo unitario debe ser mayor a $0.00.")
            return
        if venta <= 0:
            QMessageBox.warning(self, "Precio inválido",
                                "El precio de venta debe ser mayor a $0.00.")
            return

        nombre = self._combo_producto_compra.currentText()
        self._lineas_compra.append({
            "producto_id": producto_id,
            "producto": nombre,
            "cantidad": cantidad,
            "costo": costo,
            "venta": venta,
            "subtotal": cantidad * costo,
        })
        self._refrescar_lineas_compra()

    def _refrescar_lineas_compra(self):
        total = sum(l["subtotal"] for l in self._lineas_compra)
        self._lbl_total_compra.setText(f"Total compra: ${total:.2f}")
        self._tabla_lineas_compra.setRowCount(len(self._lineas_compra))
        for fila, linea in enumerate(self._lineas_compra):
            valores = [
                linea["producto"], str(linea["cantidad"]),
                f"${linea['costo']:.2f}", f"${linea['venta']:.2f}",
                f"${linea['subtotal']:.2f}", str(linea["producto_id"]),
            ]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_lineas_compra.setItem(fila, col, cell)

    def _limpiar_compra(self):
        self._lineas_compra.clear()
        if hasattr(self, "_inp_compra_notas"):
            self._inp_compra_notas.clear()
        self._refrescar_lineas_compra()

    def _guardar_compra(self):
        proveedor_id = self._combo_proveedor_compra.currentData()
        if not proveedor_id:
            QMessageBox.warning(self, "Sin proveedor",
                                "Registra o selecciona un proveedor.")
            return
        if not self._lineas_compra:
            QMessageBox.warning(self, "Compra vacía",
                                "Agrega al menos un producto a la compra.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(l["subtotal"] for l in self._lineas_compra)
        notas = self._inp_compra_notas.text().strip()

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO compras (proveedor_id, usuario_id, fecha, total, notas)
                VALUES (?, ?, ?, ?, ?)
            """, (proveedor_id, self._usuario_actual["id"], fecha, total, notas))
            compra_id = c.lastrowid

            for linea in self._lineas_compra:
                c.execute("""
                    SELECT precio_compra, precio_venta
                    FROM productos
                    WHERE id = ?
                """, (linea["producto_id"],))
                compra_ant, venta_ant = c.fetchone()

                c.execute("""
                    INSERT INTO detalle_compras
                        (compra_id, producto_id, cantidad, costo_unitario, precio_venta, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    compra_id, linea["producto_id"], linea["cantidad"],
                    linea["costo"], linea["venta"], linea["subtotal"],
                ))

                c.execute("""
                    UPDATE productos
                    SET stock = stock + ?,
                        precio_compra = ?,
                        precio_venta = ?
                    WHERE id = ?
                """, (
                    linea["cantidad"], linea["costo"], linea["venta"],
                    linea["producto_id"],
                ))

                c.execute("""
                    INSERT INTO movimientos_inventario
                        (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                    VALUES (?, 'ENTRADA', ?, ?, ?)
                """, (
                    linea["producto_id"], linea["cantidad"],
                    f"Compra #{compra_id}", fecha,
                ))

                self._registrar_historial_precio(
                    c, linea["producto_id"], compra_ant, linea["costo"],
                    venta_ant, linea["venta"], f"Compra #{compra_id}", fecha
                )

        self._limpiar_compra()
        self._cargar_historial_compras()
        self._cargar_productos()
        self._cargar_productos_pos()
        self._cargar_productos_compra()
        QMessageBox.information(
            self, "Compra guardada",
            f"Compra #{compra_id} registrada por ${total:.2f}."
        )

    def _cargar_historial_compras(self):
        if not hasattr(self, "_tabla_hist_compras"):
            return
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT c.id, c.fecha, p.nombre, c.total, COALESCE(u.nombre, 'Sin usuario')
                FROM compras c
                JOIN proveedores p ON p.id = c.proveedor_id
                LEFT JOIN usuarios u ON u.id = c.usuario_id
                ORDER BY c.fecha DESC
                LIMIT 80
            """)
            filas = c.fetchall()
        self._tabla_hist_compras.setRowCount(len(filas))
        for fila, (cid, fecha, proveedor, total, usuario) in enumerate(filas):
            valores = [str(cid), fecha, proveedor, f"${total:.2f}", usuario]
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_hist_compras.setItem(fila, col, cell)

    # ══════════════════════════════════════════════════════
    # TAB 6 — REPORTES FUERTES
    # ══════════════════════════════════════════════════════

    def _crear_tab_reportes_fuertes(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Reportes Administrativos")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Inicio:"))
        self._date_rep_inicio = QDateEdit(QDate.currentDate())
        self._date_rep_inicio.setCalendarPopup(True)
        self._date_rep_inicio.setDisplayFormat("dd/MM/yyyy")
        self._date_rep_inicio.setDate(QDate.currentDate().addDays(-30))

        hl.addWidget(self._date_rep_inicio)
        hl.addWidget(QLabel("Fin:"))
        self._date_rep_fin = QDateEdit(QDate.currentDate())
        self._date_rep_fin.setCalendarPopup(True)
        self._date_rep_fin.setDisplayFormat("dd/MM/yyyy")
        hl.addWidget(self._date_rep_fin)

        btn_mes = QPushButton("Mes actual")
        def mes_actual():
            hoy = QDate.currentDate()
            inicio = QDate(hoy.year(), hoy.month(), 1)
            self._date_rep_inicio.setDate(inicio)
            self._date_rep_fin.setDate(inicio.addMonths(1).addDays(-1))
            self._cargar_reportes_fuertes()
        btn_mes.clicked.connect(mes_actual)

        btn_ver = QPushButton("🔍  Actualizar")
        btn_ver.clicked.connect(self._cargar_reportes_fuertes)

        hl.addWidget(btn_mes)
        hl.addWidget(btn_ver)
        hl.addStretch()
        root.addLayout(hl)

        self._tabs_reportes_fuertes = QTabWidget()
        self._tabla_top_vendidos = self._crear_tabla_simple([
            "Producto", "Categoría", "Cantidad", "Venta", "Ganancia"
        ])
        self._tabla_top_ganancia = self._crear_tabla_simple([
            "Producto", "Categoría", "Cantidad", "Venta", "Ganancia"
        ])
        self._tabla_baja_rotacion = self._crear_tabla_simple([
            "Producto", "Categoría", "Cant. Vendida", "Stock", "Última venta"
        ])
        self._tabla_rep_horas = self._crear_tabla_simple([
            "Hora", "Ventas", "Venta", "Ganancia"
        ])
        self._tabla_rep_vendedores = self._crear_tabla_simple([
            "Vendedor", "Ventas", "Venta", "Ganancia", "Ticket Prom."
        ])
        self._tabla_rep_categorias = self._crear_tabla_simple([
            "Categoría", "Cantidad", "Venta", "Costo", "Ganancia", "Margen"
        ])

        self._tabs_reportes_fuertes.addTab(self._tabla_top_vendidos, "Top vendidos")
        self._tabs_reportes_fuertes.addTab(self._tabla_top_ganancia, "Más ganancia")
        self._tabs_reportes_fuertes.addTab(self._tabla_baja_rotacion, "Baja rotación")
        self._tabs_reportes_fuertes.addTab(self._tabla_rep_horas, "Ventas por hora")
        self._tabs_reportes_fuertes.addTab(self._tabla_rep_vendedores, "Ventas por vendedor")
        self._tabs_reportes_fuertes.addTab(self._tabla_rep_categorias, "Ganancia por categoría")
        root.addWidget(self._tabs_reportes_fuertes)

        return w

    def _crear_tabla_simple(self, columnas):
        tabla = QTableWidget()
        tabla.setColumnCount(len(columnas))
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)
        return tabla

    def _set_tabla(self, tabla, filas):
        tabla.setRowCount(len(filas))
        for fila, valores in enumerate(filas):
            for col, val in enumerate(valores):
                cell = QTableWidgetItem(str(val))
                cell.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(fila, col, cell)

    def _cargar_reportes_fuertes(self):
        if not self._es_admin or not hasattr(self, "_date_rep_inicio"):
            return

        inicio_q = self._date_rep_inicio.date()
        fin_q = self._date_rep_fin.date()
        if inicio_q > fin_q:
            QMessageBox.warning(self, "Rango inválido",
                                "La fecha inicial no puede ser mayor que la fecha final.")
            return

        inicio = inicio_q.toString("yyyy-MM-dd")
        fin = fin_q.toString("yyyy-MM-dd")
        desde = f"{inicio} 00:00:00"
        hasta = f"{fin} 23:59:59"

        with conectar() as conn:
            c = conn.cursor()

            c.execute("""
                SELECT p.nombre, COALESCE(p.categoria, ''),
                       COALESCE(SUM(d.cantidad), 0) AS cantidad,
                       COALESCE(SUM(d.subtotal), 0) AS venta,
                       COALESCE(SUM(d.subtotal - COALESCE(NULLIF(d.costo_total, 0),
                                d.cantidad * COALESCE(p.precio_compra, 0), 0)), 0) AS ganancia
                FROM detalle_ventas d
                JOIN ventas v ON v.id = d.venta_id
                JOIN productos p ON p.id = d.producto_id
                WHERE v.fecha >= ? AND v.fecha <= ?
                GROUP BY p.id, p.nombre, p.categoria
                ORDER BY cantidad DESC
                LIMIT 30
            """, (desde, hasta))
            top_vendidos = c.fetchall()

            c.execute("""
                SELECT p.nombre, COALESCE(p.categoria, ''),
                       COALESCE(SUM(d.cantidad), 0) AS cantidad,
                       COALESCE(SUM(d.subtotal), 0) AS venta,
                       COALESCE(SUM(d.subtotal - COALESCE(NULLIF(d.costo_total, 0),
                                d.cantidad * COALESCE(p.precio_compra, 0), 0)), 0) AS ganancia
                FROM detalle_ventas d
                JOIN ventas v ON v.id = d.venta_id
                JOIN productos p ON p.id = d.producto_id
                WHERE v.fecha >= ? AND v.fecha <= ?
                GROUP BY p.id, p.nombre, p.categoria
                ORDER BY ganancia DESC
                LIMIT 30
            """, (desde, hasta))
            top_ganancia = c.fetchall()

            c.execute("""
                SELECT p.nombre, COALESCE(p.categoria, ''),
                       COALESCE(SUM(CASE WHEN v.id IS NOT NULL THEN d.cantidad ELSE 0 END), 0) AS cantidad,
                       p.stock,
                       COALESCE(MAX(v.fecha), 'Sin ventas') AS ultima
                FROM productos p
                LEFT JOIN detalle_ventas d ON d.producto_id = p.id
                LEFT JOIN ventas v ON v.id = d.venta_id
                    AND v.fecha >= ? AND v.fecha <= ?
                WHERE p.activo = 1
                GROUP BY p.id, p.nombre, p.categoria, p.stock
                ORDER BY cantidad ASC, p.stock DESC, p.nombre
                LIMIT 30
            """, (desde, hasta))
            baja_rotacion = c.fetchall()

            c.execute("""
                WITH ventas_costos AS (
                    SELECT v.id, v.fecha, v.total,
                           COALESCE(SUM(COALESCE(NULLIF(d.costo_total, 0),
                                    d.cantidad * COALESCE(p.precio_compra, 0), 0)), 0) AS costo
                    FROM ventas v
                    LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                    LEFT JOIN productos p ON p.id = d.producto_id
                    WHERE v.fecha >= ? AND v.fecha <= ?
                    GROUP BY v.id, v.fecha, v.total
                )
                SELECT strftime('%H', fecha) || ':00',
                       COUNT(*),
                       COALESCE(SUM(total), 0),
                       COALESCE(SUM(total - costo), 0)
                FROM ventas_costos
                GROUP BY strftime('%H', fecha)
                ORDER BY strftime('%H', fecha)
            """, (desde, hasta))
            por_hora = c.fetchall()

            c.execute("""
                WITH ventas_costos AS (
                    SELECT v.id, v.fecha, v.total,
                           COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre, 'Sin usuario') AS vendedor,
                           COALESCE(SUM(COALESCE(NULLIF(d.costo_total, 0),
                                    d.cantidad * COALESCE(p.precio_compra, 0), 0)), 0) AS costo
                    FROM ventas v
                    LEFT JOIN usuarios u ON u.id = v.usuario_id
                    LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                    LEFT JOIN productos p ON p.id = d.producto_id
                    WHERE v.fecha >= ? AND v.fecha <= ?
                    GROUP BY v.id, v.fecha, v.total, vendedor
                )
                SELECT vendedor, COUNT(*), COALESCE(SUM(total), 0),
                       COALESCE(SUM(total - costo), 0), COALESCE(AVG(total), 0)
                FROM ventas_costos
                GROUP BY vendedor
                ORDER BY SUM(total) DESC
            """, (desde, hasta))
            por_vendedor = c.fetchall()

            c.execute("""
                SELECT COALESCE(NULLIF(p.categoria, ''), 'Sin categoría') AS categoria,
                       COALESCE(SUM(d.cantidad), 0) AS cantidad,
                       COALESCE(SUM(d.subtotal), 0) AS venta,
                       COALESCE(SUM(COALESCE(NULLIF(d.costo_total, 0),
                                d.cantidad * COALESCE(p.precio_compra, 0), 0)), 0) AS costo
                FROM detalle_ventas d
                JOIN ventas v ON v.id = d.venta_id
                JOIN productos p ON p.id = d.producto_id
                WHERE v.fecha >= ? AND v.fecha <= ?
                GROUP BY categoria
                ORDER BY venta DESC
            """, (desde, hasta))
            por_categoria = c.fetchall()

        self._set_tabla(self._tabla_top_vendidos, [
            [n, cat, cant, f"${venta:.2f}", f"${ganancia:.2f}"]
            for n, cat, cant, venta, ganancia in top_vendidos
        ])
        self._set_tabla(self._tabla_top_ganancia, [
            [n, cat, cant, f"${venta:.2f}", f"${ganancia:.2f}"]
            for n, cat, cant, venta, ganancia in top_ganancia
        ])
        self._set_tabla(self._tabla_baja_rotacion, [
            [n, cat, cant, stock, ultima]
            for n, cat, cant, stock, ultima in baja_rotacion
        ])
        self._set_tabla(self._tabla_rep_horas, [
            [hora, ventas, f"${venta:.2f}", f"${ganancia:.2f}"]
            for hora, ventas, venta, ganancia in por_hora
        ])
        self._set_tabla(self._tabla_rep_vendedores, [
            [vendedor, ventas, f"${venta:.2f}", f"${ganancia:.2f}", f"${prom:.2f}"]
            for vendedor, ventas, venta, ganancia, prom in por_vendedor
        ])
        self._set_tabla(self._tabla_rep_categorias, [
            [
                cat, cant, f"${venta:.2f}", f"${costo:.2f}",
                f"${(venta - costo):.2f}",
                f"{((venta - costo) / venta * 100) if venta else 0:.1f}%",
            ]
            for cat, cant, venta, costo in por_categoria
        ])

    # ══════════════════════════════════════════════════════
    # TAB 6 — ANÁLISIS POR RANGOS
    # ══════════════════════════════════════════════════════

    def _crear_tab_analisis_rangos(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Análisis de Ventas por Rango")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Rango rápido:"))
        self._combo_rango_rapido = QComboBox()
        self._combo_rango_rapido.addItems([
            "Hoy", "Esta semana", "Este mes", "Este bimestre",
            "Este trimestre", "Este año", "Personalizado",
        ])
        self._combo_rango_rapido.currentTextChanged.connect(self._aplicar_rango_rapido)

        self._date_rango_inicio = QDateEdit(QDate.currentDate())
        self._date_rango_inicio.setCalendarPopup(True)
        self._date_rango_inicio.setDisplayFormat("dd/MM/yyyy")

        self._date_rango_fin = QDateEdit(QDate.currentDate())
        self._date_rango_fin.setCalendarPopup(True)
        self._date_rango_fin.setDisplayFormat("dd/MM/yyyy")

        self._combo_agrupar_rango = QComboBox()
        self._combo_agrupar_rango.addItems([
            "Día", "Semana", "Mes", "Bimestre", "Trimestre", "Año"
        ])

        btn_ver = QPushButton("🔍  Analizar")
        btn_ver.clicked.connect(self._cargar_analisis_rangos)

        hl.addWidget(self._combo_rango_rapido)
        hl.addWidget(QLabel("Inicio:"))
        hl.addWidget(self._date_rango_inicio)
        hl.addWidget(QLabel("Fin:"))
        hl.addWidget(self._date_rango_fin)
        hl.addWidget(QLabel("Agrupar por:"))
        hl.addWidget(self._combo_agrupar_rango)
        hl.addWidget(btn_ver)
        hl.addStretch()
        root.addLayout(hl)

        hl_cards = QHBoxLayout()
        hl_cards.setSpacing(12)
        self._cards_rango = {}
        for clave, titulo, color in [
            ("venta", "Venta del rango", "#89b4fa"),
            ("ganancia", "Ganancia neta", "#a6e3a1"),
            ("costo", "Costo vendido", "#fab387"),
            ("ventas", "No. ventas", "#cba6f7"),
            ("margen", "Margen", "#f9e2af"),
        ]:
            grp = QGroupBox(titulo)
            vl = QVBoxLayout(grp)
            lbl_v = QLabel("—")
            lbl_v.setAlignment(Qt.AlignCenter)
            lbl_v.setStyleSheet(
                f"font-size: 25px; font-weight: bold; color: {color};"
            )
            vl.addWidget(lbl_v)
            self._cards_rango[clave] = lbl_v
            hl_cards.addWidget(grp)
        root.addLayout(hl_cards)

        grp_periodos = QGroupBox("Comparativo por periodo")
        vl_periodos = QVBoxLayout(grp_periodos)
        self._tabla_rango_periodos = QTableWidget()
        self._tabla_rango_periodos.setColumnCount(7)
        self._tabla_rango_periodos.setHorizontalHeaderLabels([
            "Periodo", "Ventas", "Venta", "Costo", "Ganancia", "Ticket Prom.", "Margen"
        ])
        self._tabla_rango_periodos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_rango_periodos.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_rango_periodos.setAlternatingRowColors(True)
        vl_periodos.addWidget(self._tabla_rango_periodos)
        root.addWidget(grp_periodos)

        grp_vendedores = QGroupBox("Resumen por vendedor en el rango")
        vl_vendedores = QVBoxLayout(grp_vendedores)
        self._tabla_rango_vendedores = QTableWidget()
        self._tabla_rango_vendedores.setColumnCount(6)
        self._tabla_rango_vendedores.setHorizontalHeaderLabels([
            "Vendedor", "Ventas", "Venta", "Costo", "Ganancia", "Ticket Prom."
        ])
        self._tabla_rango_vendedores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._tabla_rango_vendedores.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_rango_vendedores.setAlternatingRowColors(True)
        vl_vendedores.addWidget(self._tabla_rango_vendedores)
        root.addWidget(grp_vendedores)

        self._aplicar_rango_rapido("Hoy")
        return w

    def _aplicar_rango_rapido(self, texto):
        if not hasattr(self, "_date_rango_inicio"):
            return

        hoy = QDate.currentDate()
        inicio = hoy
        fin = hoy

        if texto == "Esta semana":
            inicio = hoy.addDays(-(hoy.dayOfWeek() - 1))
            fin = inicio.addDays(6)
            self._combo_agrupar_rango.setCurrentText("Día")
        elif texto == "Este mes":
            inicio = QDate(hoy.year(), hoy.month(), 1)
            fin = inicio.addMonths(1).addDays(-1)
            self._combo_agrupar_rango.setCurrentText("Semana")
        elif texto == "Este bimestre":
            mes_inicio = ((hoy.month() - 1) // 2) * 2 + 1
            inicio = QDate(hoy.year(), mes_inicio, 1)
            fin = inicio.addMonths(2).addDays(-1)
            self._combo_agrupar_rango.setCurrentText("Mes")
        elif texto == "Este trimestre":
            mes_inicio = ((hoy.month() - 1) // 3) * 3 + 1
            inicio = QDate(hoy.year(), mes_inicio, 1)
            fin = inicio.addMonths(3).addDays(-1)
            self._combo_agrupar_rango.setCurrentText("Mes")
        elif texto == "Este año":
            inicio = QDate(hoy.year(), 1, 1)
            fin = QDate(hoy.year(), 12, 31)
            self._combo_agrupar_rango.setCurrentText("Mes")
        elif texto == "Personalizado":
            return

        self._date_rango_inicio.setDate(inicio)
        self._date_rango_fin.setDate(fin)
        self._cargar_analisis_rangos()

    def _consultar_ventas_rango(self, inicio, fin):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT v.id, v.fecha, v.total,
                       COALESCE(NULLIF(v.vendedor_nombre, ''), u.nombre, 'Sin usuario') AS vendedor,
                       COALESCE(SUM(
                           COALESCE(NULLIF(d.costo_total, 0),
                                    d.cantidad * COALESCE(p.precio_compra, 0),
                                    0)
                       ), 0) AS costo
                FROM ventas v
                LEFT JOIN usuarios u ON u.id = v.usuario_id
                LEFT JOIN detalle_ventas d ON d.venta_id = v.id
                LEFT JOIN productos p ON p.id = d.producto_id
                WHERE v.fecha >= ? AND v.fecha <= ?
                GROUP BY v.id, v.fecha, v.total, vendedor
                ORDER BY v.fecha ASC
            """, (f"{inicio} 00:00:00", f"{fin} 23:59:59"))
            return c.fetchall()

    def _periodo_rango(self, fecha_txt, agrupacion):
        dt = datetime.strptime(fecha_txt, "%Y-%m-%d %H:%M:%S")

        if agrupacion == "Día":
            return dt.strftime("%Y-%m-%d"), dt.strftime("%d/%m/%Y")

        if agrupacion == "Semana":
            lunes = dt - timedelta(days=dt.weekday())
            domingo = lunes + timedelta(days=6)
            iso = dt.isocalendar()
            etiqueta = (
                f"Semana {iso.week} "
                f"({lunes.strftime('%d/%m')} - {domingo.strftime('%d/%m')})"
            )
            return f"{iso.year}-S{iso.week:02d}", etiqueta

        if agrupacion == "Mes":
            return f"{dt.year}-{dt.month:02d}", f"{MESES_ES[dt.month - 1].title()} {dt.year}"

        if agrupacion == "Bimestre":
            bimestre = ((dt.month - 1) // 2) + 1
            mes_inicio = (bimestre - 1) * 2 + 1
            mes_fin = mes_inicio + 1
            etiqueta = (
                f"Bimestre {bimestre} "
                f"({MESES_ES[mes_inicio - 1].title()}-{MESES_ES[mes_fin - 1].title()}) {dt.year}"
            )
            return f"{dt.year}-B{bimestre}", etiqueta

        if agrupacion == "Trimestre":
            trimestre = ((dt.month - 1) // 3) + 1
            return f"{dt.year}-T{trimestre}", f"Trimestre {trimestre} {dt.year}"

        return str(dt.year), str(dt.year)

    def _agregar_a_grupo(self, grupos, clave, etiqueta, total, costo):
        if clave not in grupos:
            grupos[clave] = {
                "etiqueta": etiqueta,
                "ventas": 0,
                "total": 0.0,
                "costo": 0.0,
            }
        grupos[clave]["ventas"] += 1
        grupos[clave]["total"] += total
        grupos[clave]["costo"] += costo

    def _llenar_tabla_resumen(self, tabla, grupos, incluir_margen):
        tabla.setRowCount(len(grupos))
        for fila, (_clave, datos) in enumerate(grupos.items()):
            ventas = datos["ventas"]
            total = datos["total"]
            costo = datos["costo"]
            ganancia = total - costo
            promedio = total / ventas if ventas else 0
            margen = (ganancia / total * 100) if total else 0

            valores = [
                datos["etiqueta"], str(ventas), f"${total:.2f}",
                f"${costo:.2f}", f"${ganancia:.2f}", f"${promedio:.2f}",
            ]
            if incluir_margen:
                valores.append(f"{margen:.1f}%")

            for col, val in enumerate(valores):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(fila, col, cell)

    def _cargar_analisis_rangos(self):
        if not self._es_admin or not hasattr(self, "_date_rango_inicio"):
            return

        inicio_q = self._date_rango_inicio.date()
        fin_q = self._date_rango_fin.date()
        if inicio_q > fin_q:
            QMessageBox.warning(self, "Rango inválido",
                                "La fecha inicial no puede ser mayor que la fecha final.")
            return

        inicio = inicio_q.toString("yyyy-MM-dd")
        fin = fin_q.toString("yyyy-MM-dd")
        agrupacion = self._combo_agrupar_rango.currentText()
        filas = self._consultar_ventas_rango(inicio, fin)

        venta_total = sum(f[2] for f in filas)
        costo_total = sum(f[4] for f in filas)
        ganancia_total = venta_total - costo_total
        num_ventas = len(filas)
        margen = (ganancia_total / venta_total * 100) if venta_total else 0

        self._cards_rango["venta"].setText(f"${venta_total:.2f}")
        self._cards_rango["ganancia"].setText(f"${ganancia_total:.2f}")
        self._cards_rango["costo"].setText(f"${costo_total:.2f}")
        self._cards_rango["ventas"].setText(str(num_ventas))
        self._cards_rango["margen"].setText(f"{margen:.1f}%")

        grupos_periodo = {}
        grupos_vendedor = {}
        for _vid, fecha, total, vendedor, costo in filas:
            clave, etiqueta = self._periodo_rango(fecha, agrupacion)
            self._agregar_a_grupo(grupos_periodo, clave, etiqueta, total, costo)
            self._agregar_a_grupo(grupos_vendedor, vendedor, vendedor, total, costo)

        grupos_vendedor = dict(
            sorted(grupos_vendedor.items(), key=lambda item: item[1]["total"], reverse=True)
        )

        self._llenar_tabla_resumen(self._tabla_rango_periodos, grupos_periodo, True)
        self._llenar_tabla_resumen(self._tabla_rango_vendedores, grupos_vendedor, False)


# ──────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    crear_tablas()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(ESTILO)

    usuario_actual, fondo_inicial = pedir_usuario_y_fondo()
    if not usuario_actual:
        sys.exit(0)

    ventana = POSAbarrotes(usuario_actual, fondo_inicial)
    ventana.show()
    sys.exit(app.exec())
