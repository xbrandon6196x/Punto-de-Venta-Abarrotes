"""Tests de FLUJO de la feature 003 (granel): venta por peso y por monto,
préstamo con devolución y cobro, y compra a proveedor — ejercitando los
métodos reales de la ventana (Qt en modo offscreen, BD temporal).

Los diálogos de confirmación se parchean para no bloquear."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

import pos_abarrotes as pos


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def sin_dialogos(monkeypatch):
    """QMessageBox sin bloquear: confirma todo y registra avisos."""
    avisos = []
    monkeypatch.setattr(QMessageBox, "information",
                        staticmethod(lambda *a, **k: avisos.append(("info", a))))
    monkeypatch.setattr(QMessageBox, "warning",
                        staticmethod(lambda *a, **k: avisos.append(("warn", a))))
    monkeypatch.setattr(QMessageBox, "critical",
                        staticmethod(lambda *a, **k: avisos.append(("crit", a))))
    monkeypatch.setattr(QMessageBox, "question",
                        staticmethod(lambda *a, **k: QMessageBox.Yes))
    return avisos


def _sembrar_granel(stock=5.0):
    """Producto granel Jamón ($180/kg, costo $120) y pieza Refresco."""
    with pos.conectar() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO productos (codigo_barras, nombre, categoria,
                                   precio_compra, precio_venta, stock,
                                   es_granel, fecha_alta)
            VALUES ('J1', 'Jamón', 'Granel', 120, 180, ?, 1,
                    '2026-01-01 00:00:00')
        """, (stock,))
        jamon = c.lastrowid
        c.execute("""
            INSERT INTO productos (codigo_barras, nombre, categoria,
                                   precio_compra, precio_venta, stock,
                                   es_granel, fecha_alta)
            VALUES ('R1', 'Refresco', 'Bebidas', 10, 15, 20, 0,
                    '2026-01-01 00:00:00')
        """)
        refresco = c.lastrowid
    return jamon, refresco


def _ventana(qapp):
    admin = pos.validar_login("admin", "admin123")
    return pos.POSAbarrotes(admin, fondo_inicial=100)


def test_venta_granel_por_peso_y_por_monto(bd_temporal, qapp, sin_dialogos):
    jamon, refresco = _sembrar_granel(stock=5.0)
    ventana = _ventana(qapp)

    # Ticket mixto: 0.250 kg pesados + «$30» exactos + 2 piezas
    ventana._ticket = [
        {"pid": jamon, "codigo": "J1", "nombre": "Jamón", "cant": 0.25,
         "precio": 180, "costo": 120, "sub": 45.0, "stock": 5, "es_granel": 1},
        {"pid": jamon, "codigo": "J1", "nombre": "Jamón", "cant": 0.167,
         "precio": 180, "costo": 120, "sub": 30.0, "stock": 5, "es_granel": 1},
        {"pid": refresco, "codigo": "R1", "nombre": "Refresco", "cant": 2,
         "precio": 15, "costo": 10, "sub": 30.0, "stock": 20, "es_granel": 0},
    ]
    ventana._spin_efectivo.setValue(200)
    ventana._cobrar()

    with pos.conectar() as conn:
        c = conn.cursor()
        (total,) = c.execute("SELECT total FROM ventas").fetchone()
        detalles = c.execute("""
            SELECT cantidad, subtotal, costo_total FROM detalle_ventas
            ORDER BY id
        """).fetchall()
        (stock_jamon,) = c.execute(
            "SELECT stock FROM productos WHERE id = ?", (jamon,)).fetchone()
        (stock_refresco,) = c.execute(
            "SELECT stock FROM productos WHERE id = ?", (refresco,)).fetchone()
        movimientos = c.execute("""
            SELECT cantidad FROM movimientos_inventario
            WHERE tipo_movimiento = 'SALIDA' ORDER BY id
        """).fetchall()

    assert total == pytest.approx(105.0)            # 45 + 30 + 30
    assert detalles[0][:2] == (0.25, 45.0)          # por peso
    assert detalles[1][:2] == (0.167, 30.0)         # por monto: $30 EXACTOS
    assert detalles[0][2] == pytest.approx(0.25 * 120)   # costo del momento
    assert stock_jamon == pytest.approx(5 - 0.25 - 0.167)
    assert stock_refresco == 18                     # pieza sigue entera
    assert [m[0] for m in movimientos] == [0.25, 0.167, 2]
    assert ventana._ticket == []                    # ticket limpio

    # El corte cuadra con la venta mixta
    resumen = pos.resumen_caja_sesion(ventana._sesion_id)
    assert resumen["esperado"] == pytest.approx(100 + 105.0)


def test_prestamo_granel_devolucion_y_cobro(bd_temporal, qapp, sin_dialogos):
    jamon, _ = _sembrar_granel(stock=5.0)
    ventana = _ventana(qapp)
    ctx = {"usuario_id": ventana._usuario_actual["id"],
           "sesion_id": ventana._sesion_id, "vendedor": "Prueba"}

    # Prestar 0.750 kg
    ventana._prestamo_lineas = [
        {"pid": jamon, "codigo": "J1", "nombre": "Jamón", "cant": 0.75,
         "precio": 180, "costo": 120, "sub": 135.0, "stock": 5, "es_granel": 1},
    ]
    ventana._inp_pre_nombre.setText("Cliente Confianza")
    ventana._registrar_prestamo()

    with pos.conectar() as conn:
        (prestamo_id,) = conn.execute("SELECT id FROM prestamos").fetchone()
        (stock,) = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (jamon,)).fetchone()
    assert stock == pytest.approx(4.25)

    # Devolver: el peso regresa al inventario
    dlg = pos.DialogoDetallePrestamo(prestamo_id, ctx)
    dlg._tabla.setCurrentCell(0, 0)
    dlg._devolver_seleccionado()
    with pos.conectar() as conn:
        (estado,) = conn.execute(
            "SELECT estado FROM detalle_prestamos").fetchone()
        (stock,) = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (jamon,)).fetchone()
    assert estado == "DEVUELTO"
    assert stock == pytest.approx(5.0)

    # Prestar 1.250 kg y cobrarlo: genera la venta con ese peso
    ventana._prestamo_lineas = [
        {"pid": jamon, "codigo": "J1", "nombre": "Jamón", "cant": 1.25,
         "precio": 180, "costo": 120, "sub": 225.0, "stock": 5, "es_granel": 1},
    ]
    ventana._inp_pre_nombre.setText("Cliente Confianza")
    ventana._registrar_prestamo()
    with pos.conectar() as conn:
        (p2,) = conn.execute("SELECT MAX(id) FROM prestamos").fetchone()

    dlg2 = pos.DialogoDetallePrestamo(p2, ctx)
    dlg2._cobrar(todos=True)
    with pos.conectar() as conn:
        venta = conn.execute("""
            SELECT v.total, d.cantidad FROM ventas v
            JOIN detalle_ventas d ON d.venta_id = v.id
        """).fetchone()
        (estado_p2,) = conn.execute(
            "SELECT estado FROM prestamos WHERE id = ?", (p2,)).fetchone()
        (stock,) = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (jamon,)).fetchone()
    assert venta == (pytest.approx(225.0), pytest.approx(1.25))
    assert estado_p2 == "CERRADO"
    assert stock == pytest.approx(3.75)     # el cobro no regresa stock

    # Prestar TODO el stock restante no truena por drift float
    ventana._prestamo_lineas = [
        {"pid": jamon, "codigo": "J1", "nombre": "Jamón", "cant": 3.75,
         "precio": 180, "costo": 120, "sub": 675.0, "stock": 3.75,
         "es_granel": 1},
    ]
    ventana._inp_pre_nombre.setText("Cliente Confianza")
    ventana._registrar_prestamo()
    with pos.conectar() as conn:
        (stock,) = conn.execute(
            "SELECT stock FROM productos WHERE id = ?", (jamon,)).fetchone()
    assert stock == pytest.approx(0.0)


def test_compra_granel_sube_stock_y_costos(bd_temporal, qapp, sin_dialogos):
    jamon, _ = _sembrar_granel(stock=2.0)
    with pos.conectar() as conn:
        conn.execute("""
            INSERT INTO proveedores (nombre, fecha_alta)
            VALUES ('Lácteos SA', '2026-01-01 00:00:00')
        """)
    ventana = _ventana(qapp)
    ventana._cargar_proveedores_compra()

    ventana._lineas_compra = [{
        "producto_id": jamon, "producto": "Jamón", "cantidad": 3.5,
        "costo": 130, "venta": 190, "subtotal": 455.0, "es_granel": True,
    }]
    ventana._guardar_compra()

    with pos.conectar() as conn:
        c = conn.cursor()
        (stock, compra, venta) = c.execute("""
            SELECT stock, precio_compra, precio_venta
            FROM productos WHERE id = ?
        """, (jamon,)).fetchone()
        detalle = c.execute(
            "SELECT cantidad, subtotal FROM detalle_compras").fetchone()
    assert stock == pytest.approx(5.5)
    assert (compra, venta) == (130, 190)
    assert detalle == (pytest.approx(3.5), pytest.approx(455.0))
