"""Tests de humo de la lógica sin UI: validadores, usuarios, clientes,
esquema y la fórmula del corte de caja (la parte más delicada del POS)."""

from datetime import datetime

import pos_abarrotes as pos


AHORA = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ── Validadores puros (no necesitan BD) ─────────────────────────────


def test_hash_password_es_determinista_y_distingue():
    assert pos.hash_password("admin123") == pos.hash_password("admin123")
    assert pos.hash_password("admin123") != pos.hash_password("otra")


def test_codigos_manuales():
    codigo = pos.generar_codigo_manual()
    assert codigo.startswith(pos.CODIGO_MANUAL_PREFIX)
    assert pos.es_codigo_manual(codigo)
    assert not pos.es_codigo_manual("7501055300006")
    assert pos.codigo_visible(codigo) == "Sin código"
    assert pos.codigo_visible("7501055300006") == "7501055300006"


def test_telefono_valido():
    assert pos.telefono_valido("")            # opcional: vacío es válido
    assert pos.telefono_valido(None)
    assert pos.telefono_valido("228 123 4567")
    assert pos.telefono_valido("+52 (228) 123-4567")
    assert not pos.telefono_valido("123")      # muy corto
    assert not pos.telefono_valido("abc12345678")


def test_correo_valido():
    assert pos.correo_valido("")               # opcional: vacío es válido
    assert pos.correo_valido("cliente@correo.com")
    assert not pos.correo_valido("cliente@correo")
    assert not pos.correo_valido("sin-arroba.com")


# ── Esquema y usuarios iniciales ────────────────────────────────────


def test_crear_tablas_crea_el_esquema_completo(bd_temporal):
    with pos.conectar() as conn:
        tablas = {
            fila[0] for fila in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    esperadas = {
        "usuarios", "sesiones_usuario", "productos", "ventas",
        "detalle_ventas", "movimientos_inventario", "historial_precios",
        "proveedores", "compras", "detalle_compras", "ticket_pendiente",
        "detalle_ticket_pendiente", "clientes", "apartados",
        "abonos_apartado", "prestamos", "detalle_prestamos",
        "movimientos_cliente",
    }
    assert esperadas <= tablas


def test_agregar_columna_si_falta_es_idempotente(bd_temporal):
    with pos.conectar() as conn:
        pos.agregar_columna_si_falta(conn, "productos", "columna_prueba", "TEXT DEFAULT ''")
        pos.agregar_columna_si_falta(conn, "productos", "columna_prueba", "TEXT DEFAULT ''")
        columnas = [f[1] for f in conn.execute("PRAGMA table_info(productos)")]
    assert columnas.count("columna_prueba") == 1


def test_login_con_usuarios_de_prueba(bd_temporal):
    sesion = pos.validar_login("admin", "clave-prueba-admin")
    assert sesion is not None
    assert sesion["rol"] == "admin"
    assert pos.validar_login("admin", "contraseña-incorrecta") is None
    assert pos.validar_login("no-existe", "lo-que-sea") is None


# ── Clientes ────────────────────────────────────────────────────────


def test_obtener_o_crear_cliente_reutiliza(bd_temporal):
    with pos.conectar() as conn:
        c = conn.cursor()
        id1 = pos.obtener_o_crear_cliente(c, "María López", "2281234567")
        id2 = pos.obtener_o_crear_cliente(c, "maría lópez", "2281234567")
        id3 = pos.obtener_o_crear_cliente(c, "Otro Cliente")
    assert id1 == id2          # mismo nombre (case-insensitive) + teléfono
    assert id3 != id1


# ── Corte de caja: la fórmula del efectivo esperado ─────────────────
# esperado = fondo + ventas Efectivo + anticipos Efectivo - devoluciones


def _insertar_venta(c, sesion_id, usuario_id, total, metodo):
    c.execute("""
        INSERT INTO ventas (fecha, total, metodo_pago, usuario_id, sesion_id, vendedor_nombre)
        VALUES (?, ?, ?, ?, ?, 'Prueba')
    """, (AHORA, total, metodo, usuario_id, sesion_id))


def test_resumen_y_cierre_de_caja(bd_temporal):
    admin = pos.validar_login("admin", "clave-prueba-admin")
    sesion_id = pos.iniciar_registro_sesion(
        admin["id"], fondo_inicial=200, vendedor_nombre="Prueba"
    )

    with pos.conectar() as conn:
        c = conn.cursor()
        _insertar_venta(c, sesion_id, admin["id"], 150, "Efectivo")
        _insertar_venta(c, sesion_id, admin["id"], 100, "Tarjeta")

        cliente_id = pos.obtener_o_crear_cliente(c, "Cliente Apartado")
        c.execute("""
            INSERT INTO apartados (cliente_id, monto_total, estado, fecha_creacion, sesion_id)
            VALUES (?, 300, 'ACTIVO', ?, ?)
        """, (cliente_id, AHORA, sesion_id))
        apartado_id = c.lastrowid
        c.execute("""
            INSERT INTO abonos_apartado (apartado_id, tipo, monto, metodo_pago, fecha, sesion_id)
            VALUES (?, 'ABONO', 50, 'Efectivo', ?, ?)
        """, (apartado_id, AHORA, sesion_id))
        c.execute("""
            INSERT INTO abonos_apartado (apartado_id, tipo, monto, metodo_pago, fecha, sesion_id)
            VALUES (?, 'DEVOLUCION', 20, 'Efectivo', ?, ?)
        """, (apartado_id, AHORA, sesion_id))

    resumen = pos.resumen_caja_sesion(sesion_id)
    assert resumen["fondo"] == 200
    assert resumen["efectivo"] == 150
    assert resumen["tarjeta"] == 100
    assert resumen["anticipos_efectivo"] == 50
    assert resumen["devoluciones_anticipo"] == 20
    assert resumen["num_ventas"] == 2
    assert resumen["esperado"] == 200 + 150 + 50 - 20  # 380

    pos.cerrar_registro_sesion(
        sesion_id, efectivo_contado=380, diferencia=0, observaciones="cuadró"
    )
    with pos.conectar() as conn:
        fila = conn.execute("""
            SELECT estado, corte_cerrado, efectivo_contado
            FROM sesiones_usuario WHERE id = ?
        """, (sesion_id,)).fetchone()
    assert fila == ("CERRADA", 1, 380)


def test_los_tests_no_tocan_la_bd_real(bd_temporal):
    """La BD del test vive en la carpeta temporal, no en el repo."""
    assert (bd_temporal / pos.DB_NAME).exists()
