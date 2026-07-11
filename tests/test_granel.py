"""Tests de la feature 003: productos a granel — peso/monto/formateo,
columna aditiva es_granel y stock decimal en la columna INTEGER existente."""

import sqlite3

import pytest

import pos_abarrotes as pos


# ── Lógica pura ─────────────────────────────────────────────────────


def test_redondear_peso_al_gramo():
    assert pos.redondear_peso(0.1234) == 0.123
    assert pos.redondear_peso(0.9999) == 1.0
    assert pos.redondear_peso(2) == 2.0


def test_peso_desde_monto():
    assert pos.peso_desde_monto(45, 180) == 0.25
    assert pos.peso_desde_monto(30, 180) == 0.167     # $30 de jamón, al gramo
    with pytest.raises(ValueError):
        pos.peso_desde_monto(30, 0)                   # sin precio por kilo
    with pytest.raises(ValueError):
        pos.peso_desde_monto(30, None)


def test_formatear_cantidad():
    assert pos.formatear_cantidad(3, es_granel=False) == "3"
    assert pos.formatear_cantidad(3.0, es_granel=False) == "3"
    assert pos.formatear_cantidad(0.25, es_granel=True) == "0.250 kg"
    assert pos.formatear_cantidad(1, es_granel=True) == "1.000 kg"
    assert pos.formatear_cantidad(2.4567, es_granel=True) == "2.457 kg"


# ── Esquema: columna aditiva y stock decimal ────────────────────────


def test_bd_vieja_gana_es_granel_sin_perder_datos(tmp_path, monkeypatch):
    """Simula la BD real de la tienda (esquema previo, sin es_granel):
    tras crear_tablas() la columna aparece y el producto sigue por pieza."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pos, "ITERACIONES_PBKDF2", 1_000)
    with sqlite3.connect(pos.DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE productos (
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
            )
        """)
        conn.execute("""
            INSERT INTO productos (codigo_barras, nombre, precio_venta,
                                   stock, fecha_alta)
            VALUES ('750', 'Producto viejo', 10, 7, '2026-01-01 00:00:00')
        """)

    pos.crear_tablas()      # migración aditiva

    with pos.conectar() as conn:
        fila = conn.execute("""
            SELECT es_granel, stock FROM productos WHERE codigo_barras = '750'
        """).fetchone()
    assert fila == (0, 7)   # por pieza y con su stock intacto


def test_stock_decimal_vive_en_la_columna_integer(bd_temporal):
    with pos.conectar() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO productos (codigo_barras, nombre, precio_compra,
                                   precio_venta, stock, es_granel, fecha_alta)
            VALUES ('751', 'Jamón', 120, 180, 5, 1, '2026-01-01 00:00:00')
        """)
        pid = c.lastrowid
        c.execute("UPDATE productos SET stock = stock - ? WHERE id = ?",
                  (0.25, pid))
    with pos.conectar() as conn:
        (stock,) = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (pid,)).fetchone()
    assert stock == 4.75    # SQLite guarda el decimal sin migrar el tipo
