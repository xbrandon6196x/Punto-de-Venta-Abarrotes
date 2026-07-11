"""Tests de la lógica de reportes ampliados (feature 001): periodos de
comparación, métricas por rango, series para gráficas y exportación CSV.
Todo con BD temporal y fechas fijas para que las cifras sean deterministas."""

from datetime import date

import pos_abarrotes as pos


# ── Cálculo de periodos (puro, sin BD) ──────────────────────────────


def test_rango_semana_es_lunes_a_domingo():
    # El 8 de julio de 2026 es miércoles
    assert pos.rango_semana(date(2026, 7, 8)) == ("2026-07-06", "2026-07-12")
    assert pos.rango_semana(date(2026, 7, 6)) == ("2026-07-06", "2026-07-12")


def test_rango_mes_calendario():
    assert pos.rango_mes(date(2026, 7, 8)) == ("2026-07-01", "2026-07-31")
    assert pos.rango_mes(date(2026, 2, 15)) == ("2026-02-01", "2026-02-28")


def test_periodo_anterior_rango_libre_misma_duracion():
    # 10 días → los 10 días inmediatos anteriores
    assert pos.periodo_anterior("2026-07-01", "2026-07-10") == \
        ("2026-06-21", "2026-06-30")
    # Un solo día → el día anterior
    assert pos.periodo_anterior("2026-07-08", "2026-07-08") == \
        ("2026-07-07", "2026-07-07")


def test_periodo_anterior_modo_mes_usa_mes_calendario():
    # Julio (31 días) → junio completo (30 días), no "31 días antes"
    assert pos.periodo_anterior("2026-07-01", "2026-07-31", "mes") == \
        ("2026-06-01", "2026-06-30")
    # Cruce de año
    assert pos.periodo_anterior("2026-01-01", "2026-01-31", "mes") == \
        ("2025-12-01", "2025-12-31")


# ── Métricas y series (con BD temporal sembrada) ────────────────────
# Periodo actual: 2026-07-01 al 2026-07-07. Anterior: 2026-06-24 al 30.


def _sembrar_ventas(c):
    c.execute("""
        INSERT INTO productos (codigo_barras, nombre, categoria,
                               precio_compra, precio_venta, stock, fecha_alta)
        VALUES ('750001', 'Refresco', 'Bebidas', 10, 15, 50, '2026-01-01 09:00:00')
    """)
    refresco = c.lastrowid
    c.execute("""
        INSERT INTO productos (codigo_barras, nombre, categoria,
                               precio_compra, precio_venta, stock, fecha_alta)
        VALUES ('750002', 'Jabón', 'Limpieza', 5, 8, 30, '2026-01-01 09:00:00')
    """)
    jabon = c.lastrowid

    def venta(fecha, producto_id, cantidad, precio, costo):
        c.execute("""
            INSERT INTO ventas (fecha, total, metodo_pago, vendedor_nombre)
            VALUES (?, ?, 'Efectivo', 'Prueba')
        """, (fecha, cantidad * precio))
        venta_id = c.lastrowid
        c.execute("""
            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad,
                    precio_unitario, costo_unitario, subtotal, costo_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (venta_id, producto_id, cantidad, precio, costo,
              cantidad * precio, cantidad * costo))

    # Periodo actual: venta 38, ganancia 13, 2 ventas, ticket 19
    venta("2026-07-02 10:15:00", refresco, 2, 15, 10)   # 30, gana 10
    venta("2026-07-05 17:40:00", jabon, 1, 8, 5)        # 8, gana 3
    # Periodo anterior: venta 15, ganancia 5, 1 venta
    venta("2026-06-25 12:00:00", refresco, 1, 15, 10)


def test_metricas_periodo(bd_temporal):
    with pos.conectar() as conn:
        _sembrar_ventas(conn.cursor())
    m = pos.metricas_periodo("2026-07-01", "2026-07-07")
    assert m["num_ventas"] == 2
    assert m["venta"] == 38
    assert m["ganancia"] == 13
    assert m["ticket_promedio"] == 19


def test_metricas_periodo_sin_ventas_da_ceros(bd_temporal):
    m = pos.metricas_periodo("2026-03-01", "2026-03-31")
    assert m == {"num_ventas": 0, "venta": 0,
                 "ganancia": 0, "ticket_promedio": 0.0}


def test_comparar_periodos(bd_temporal):
    with pos.conectar() as conn:
        _sembrar_ventas(conn.cursor())
    comp = pos.comparar_periodos("2026-07-01", "2026-07-07")
    assert comp["anterior"] == ("2026-06-24", "2026-06-30")
    filas = {f[0]: f for f in comp["filas"]}
    _, actual, anterior, dif, pct = filas["Venta total"]
    assert (actual, anterior, dif) == (38, 15, 23)
    assert round(pct, 2) == round(23 / 15 * 100, 2)
    # Sin datos en el periodo anterior → porcentaje None (no división entre 0)
    comp_vacio = pos.comparar_periodos("2026-06-25", "2026-06-25")
    for _, _, anterior, _, pct in comp_vacio["filas"]:
        assert anterior == 0
        assert pct is None


def test_ventas_por_dia_rellena_dias_vacios(bd_temporal):
    with pos.conectar() as conn:
        _sembrar_ventas(conn.cursor())
    filas = pos.ventas_por_dia("2026-07-01", "2026-07-07")
    assert len(filas) == 7                      # todos los días, sin huecos
    por_dia = dict(filas)
    assert por_dia["2026-07-02"] == 30
    assert por_dia["2026-07-05"] == 8
    assert por_dia["2026-07-03"] == 0


def test_ventas_por_hora_rango_completa_24_horas(bd_temporal):
    with pos.conectar() as conn:
        _sembrar_ventas(conn.cursor())
    filas = pos.ventas_por_hora_rango("2026-07-01", "2026-07-07")
    assert len(filas) == 24
    por_hora = {h: (n, t) for h, n, t in filas}
    assert por_hora[10] == (1, 30)
    assert por_hora[17] == (1, 8)
    assert por_hora[3] == (0, 0)


def test_ganancia_por_categoria_ordenada(bd_temporal):
    with pos.conectar() as conn:
        _sembrar_ventas(conn.cursor())
    filas = pos.ganancia_por_categoria_rango("2026-07-01", "2026-07-07")
    assert filas == [("Bebidas", 10), ("Limpieza", 3)]


def test_reportes_no_escriben_en_la_bd(bd_temporal):
    """Los reportes son solo lectura: ninguna tabla cambia de tamaño."""
    with pos.conectar() as conn:
        c = conn.cursor()
        _sembrar_ventas(c)

    def total_filas():
        with pos.conectar() as conn:
            return sum(
                conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ("ventas", "detalle_ventas", "productos",
                          "movimientos_inventario", "sesiones_usuario")
            )

    antes = total_filas()
    pos.comparar_periodos("2026-07-01", "2026-07-07")
    pos.ventas_por_dia("2026-07-01", "2026-07-07")
    pos.ventas_por_hora_rango("2026-07-01", "2026-07-07")
    pos.ganancia_por_categoria_rango("2026-07-01", "2026-07-07")
    assert total_filas() == antes


# ── Exportación ─────────────────────────────────────────────────────


def test_exportar_tabla_csv_con_acentos(tmp_path):
    ruta = tmp_path / "reporte.csv"
    pos.exportar_tabla_csv(
        ruta,
        ["Producto", "Categoría", "Venta"],
        [("Jabón", "Limpieza", 8), ("Café", "Abarrotes", 55.5)],
    )
    crudo = ruta.read_bytes()
    assert crudo.startswith(b"\xef\xbb\xbf")    # BOM: Excel respeta acentos
    lineas = ruta.read_text(encoding="utf-8-sig").strip().splitlines()
    assert lineas[0] == "Producto,Categoría,Venta"
    assert lineas[1] == "Jabón,Limpieza,8"
    assert lineas[2] == "Café,Abarrotes,55.5"


def test_tabla_a_html_escapa_y_lleva_titulo():
    html = pos.tabla_a_html(
        "Top vendidos", "Del 01/07/2026 al 07/07/2026",
        ["Producto", "Venta"],
        [("Refresco <2L>", 30)],
    )
    assert "Top vendidos" in html
    assert "Del 01/07/2026 al 07/07/2026" in html
    assert "Generado:" in html
    assert "&lt;2L&gt;" in html                 # sin HTML crudo del dato
    assert "<td>30</td>" in html
