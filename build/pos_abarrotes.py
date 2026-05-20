#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════╗
║   POS Abarrotes v2  —  Punto de Venta e Inventario  ║
║   Tecnologías: Python · PySide6 · SQLite             ║
╚══════════════════════════════════════════════════════╝
Ejecutar:  python pos_abarrotes.py
Requiere:  pip install PySide6
"""

import sys
import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QSpinBox, QDoubleSpinBox, QHeaderView,
    QComboBox, QGroupBox, QDialog, QFormLayout,
    QStatusBar, QDateEdit, QGridLayout, QDialogButtonBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

# ──────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────

DB_NAME = "abarrotes_pos.db"

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
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    with conectar() as conn:
        conn.executescript("""
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
                efectivo_recibido REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id        INTEGER NOT NULL,
                producto_id     INTEGER NOT NULL,
                cantidad        INTEGER NOT NULL,
                precio_unitario REAL    NOT NULL,
                subtotal        REAL    NOT NULL,
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
        """)


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

        self._spin = QSpinBox()
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
# DIÁLOGO — DETALLE DE VENTA
# ──────────────────────────────────────────────────────────

class DialogoDetalleVenta(QDialog):
    def __init__(self, venta_id, fecha, total, metodo, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalle de Venta #{venta_id}")
        self.resize(600, 430)
        lay = QVBoxLayout(self)

        info = QLabel(
            f"<b>Venta #{venta_id}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"{fecha}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Método: <b>{metodo}</b>&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"Total: <b>${total:.2f}</b>"
        )
        info.setWordWrap(True)
        lay.addWidget(info)

        tabla = QTableWidget()
        tabla.setColumnCount(5)
        tabla.setHorizontalHeaderLabels(
            ["Producto", "Código", "Cant.", "Precio Unit.", "Subtotal"]
        )
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setAlternatingRowColors(True)

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT p.nombre, p.codigo_barras,
                       d.cantidad, d.precio_unitario, d.subtotal
                FROM detalle_ventas d
                JOIN productos p ON d.producto_id = p.id
                WHERE d.venta_id = ?
                ORDER BY p.nombre
            """, (venta_id,))
            filas = c.fetchall()

        tabla.setRowCount(len(filas))
        for i, (nom, cod, cant, precio, sub) in enumerate(filas):
            for j, v in enumerate([nom, cod, str(cant), f"${precio:.2f}", f"${sub:.2f}"]):
                cell = QTableWidgetItem(v)
                cell.setTextAlignment(Qt.AlignCenter)
                tabla.setItem(i, j, cell)

        lay.addWidget(tabla)
        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        lay.addWidget(btn, alignment=Qt.AlignRight)


# ──────────────────────────────────────────────────────────
# VENTANA PRINCIPAL
# ──────────────────────────────────────────────────────────

class POSAbarrotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema POS — Tienda de Abarrotes  v2")
        self.resize(1280, 800)

        self._ticket = []           # lista de dicts con los items del ticket
        self._pid_editando = None   # ID del producto cargado en el formulario

        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        tabs = QTabWidget()
        tabs.addTab(self._crear_tab_venta(),      "🛒   Punto de Venta")
        tabs.addTab(self._crear_tab_inventario(), "📦   Inventario")
        tabs.addTab(self._crear_tab_reportes(),   "📊   Ventas del Día")
        self.setCentralWidget(tabs)
        self.setStyleSheet(ESTILO)

        self._cargar_productos()
        self._cargar_ventas()

    # ══════════════════════════════════════════════════════
    # TAB 1 — PUNTO DE VENTA
    # ══════════════════════════════════════════════════════

    def _crear_tab_venta(self):
        w = QWidget()
        root = QHBoxLayout(w)
        root.setSpacing(12)

        # ── Columna izquierda: ticket ──────────────────────
        izq = QVBoxLayout()
        izq.setSpacing(8)

        lbl = QLabel("Punto de Venta")
        lbl.setObjectName("lbl_titulo")
        izq.addWidget(lbl)

        grp_scan = QGroupBox("Escanear / buscar producto")
        hl = QHBoxLayout(grp_scan)
        self._inp_codigo_venta = QLineEdit()
        self._inp_codigo_venta.setPlaceholderText(
            "Código de barras — presiona Enter o escanea"
        )
        self._inp_codigo_venta.returnPressed.connect(self._agregar_al_ticket)
        btn_add = QPushButton("➕  Agregar")
        btn_add.clicked.connect(self._agregar_al_ticket)
        hl.addWidget(self._inp_codigo_venta)
        hl.addWidget(btn_add)
        izq.addWidget(grp_scan)

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
        self._spin_efectivo = QDoubleSpinBox()
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

        self._toggle_efectivo("Efectivo")  # estado inicial
        return w

    # ── helpers del punto de venta ─────────────────────────

    def _toggle_efectivo(self, metodo):
        self._grp_efectivo.setVisible(metodo == "Efectivo")

    def _actualizar_cambio(self, valor=None):
        if valor is None:
            valor = self._spin_efectivo.value()
        total  = sum(i["sub"] for i in self._ticket)
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

    def _buscar_producto(self, codigo):
        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, codigo_barras, nombre, precio_venta, stock
                FROM productos
                WHERE codigo_barras = ? AND activo = 1
            """, (codigo,))
            return c.fetchone()

    def _agregar_al_ticket(self):
        codigo = self._inp_codigo_venta.text().strip()
        if not codigo:
            return
        self._inp_codigo_venta.clear()

        prod = self._buscar_producto(codigo)
        if not prod:
            QMessageBox.warning(self, "No encontrado",
                                "Código no registrado en inventario activo.")
            return

        pid, cod, nombre, precio, stock = prod

        if stock <= 0:
            QMessageBox.warning(self, "Sin existencia",
                                f"«{nombre}» no tiene stock disponible.")
            return

        # Si ya está en el ticket, solo sumar cantidad
        for item in self._ticket:
            if item["pid"] == pid:
                if item["cant"] >= stock:
                    QMessageBox.warning(
                        self, "Stock insuficiente",
                        f"Solo hay {stock} unidades disponibles de «{nombre}»."
                    )
                    return
                item["cant"] += 1
                item["sub"] = item["cant"] * item["precio"]
                self._refrescar_ticket()
                self._statusbar.showMessage(
                    f"«{nombre}» — cantidad: {item['cant']}", 2500
                )
                return

        # Agregar nuevo ítem
        self._ticket.append({
            "pid": pid, "codigo": cod, "nombre": nombre,
            "cant": 1, "precio": precio, "sub": precio, "stock": stock,
        })
        self._refrescar_ticket()
        self._statusbar.showMessage(f"«{nombre}» agregado al ticket.", 2500)

    def _refrescar_ticket(self):
        self._tabla_ticket.setRowCount(len(self._ticket))
        total = 0.0
        for fila, item in enumerate(self._ticket):
            total += item["sub"]
            vals = [
                str(item["pid"]), item["codigo"], item["nombre"],
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

    def _fila_ticket(self):
        f = self._tabla_ticket.currentRow()
        if f < 0:
            QMessageBox.information(self, "Sin selección",
                                    "Selecciona primero un producto del ticket.")
        return f

    def _sumar_cantidad(self):
        f = self._fila_ticket()
        if f < 0:
            return
        item = self._ticket[f]
        if item["cant"] >= item["stock"]:
            QMessageBox.warning(self, "Límite de stock",
                                f"Solo hay {item['stock']} unidades disponibles.")
            return
        item["cant"] += 1
        item["sub"] = item["cant"] * item["precio"]
        self._refrescar_ticket()

    def _restar_cantidad(self):
        f = self._fila_ticket()
        if f < 0:
            return
        item = self._ticket[f]
        if item["cant"] > 1:
            item["cant"] -= 1
            item["sub"] = item["cant"] * item["precio"]
        else:
            self._ticket.pop(f)
        self._refrescar_ticket()

    def _eliminar_item(self):
        f = self._fila_ticket()
        if f < 0:
            return
        self._ticket.pop(f)
        self._refrescar_ticket()

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

    def _cobrar(self):
        if not self._ticket:
            QMessageBox.warning(self, "Ticket vacío",
                                "Agrega productos al ticket antes de cobrar.")
            return

        total  = sum(i["sub"] for i in self._ticket)
        metodo = self._combo_pago.currentText()
        efec   = self._spin_efectivo.value() if metodo == "Efectivo" else 0.0

        if metodo == "Efectivo" and efec < total:
            QMessageBox.warning(self, "Monto insuficiente",
                                "El efectivo recibido es menor al total de la venta.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with conectar() as conn:
                c = conn.cursor()

                c.execute("""
                    INSERT INTO ventas (fecha, total, metodo_pago, efectivo_recibido)
                    VALUES (?, ?, ?, ?)
                """, (fecha, total, metodo, efec))
                vid = c.lastrowid

                for item in self._ticket:
                    c.execute("""
                        INSERT INTO detalle_ventas
                            (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?)
                    """, (vid, item["pid"], item["cant"], item["precio"], item["sub"]))

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

            QMessageBox.information(self, "Venta realizada", msg)

            self._ticket.clear()
            self._refrescar_ticket()
            self._spin_efectivo.setValue(0)
            self._cargar_productos()
            self._cargar_ventas()
            self._statusbar.showMessage(
                f"Venta #{vid} registrada — ${total:.2f}  ({metodo})", 6000
            )

        except Exception as e:
            QMessageBox.critical(self, "Error al cobrar",
                                 f"No se pudo registrar la venta:\n{e}")

    # ══════════════════════════════════════════════════════
    # TAB 2 — INVENTARIO
    # ══════════════════════════════════════════════════════

    def _crear_tab_inventario(self):
        w = QWidget()
        root = QVBoxLayout(w)
        root.setSpacing(8)

        lbl = QLabel("Inventario de Productos")
        lbl.setObjectName("lbl_titulo")
        root.addWidget(lbl)

        # ── Formulario ─────────────────────────────────────
        grp = QGroupBox(
            "Datos del producto  —  Haz clic en una fila de la tabla para editar"
        )
        grid = QGridLayout(grp)
        grid.setSpacing(6)

        self._inp_cod    = QLineEdit()
        self._inp_cod.setPlaceholderText("Código de barras *")
        self._inp_nom    = QLineEdit()
        self._inp_nom.setPlaceholderText("Nombre del producto *")
        self._inp_cat    = QLineEdit()
        self._inp_cat.setPlaceholderText("Categoría")

        self._inp_compra = QDoubleSpinBox()
        self._inp_compra.setRange(0, 999_999)
        self._inp_compra.setPrefix("$")
        self._inp_compra.setDecimals(2)

        self._inp_venta  = QDoubleSpinBox()
        self._inp_venta.setRange(0, 999_999)
        self._inp_venta.setPrefix("$")
        self._inp_venta.setDecimals(2)

        self._inp_stock  = QSpinBox()
        self._inp_stock.setRange(0, 999_999)

        self._inp_minimo = QSpinBox()
        self._inp_minimo.setRange(0, 999_999)
        self._inp_minimo.setValue(5)

        # Fila 0
        grid.addWidget(QLabel("Código *:"),     0, 0); grid.addWidget(self._inp_cod,    0, 1)
        grid.addWidget(QLabel("Nombre *:"),      0, 2); grid.addWidget(self._inp_nom,    0, 3)
        grid.addWidget(QLabel("Categoría:"),     0, 4); grid.addWidget(self._inp_cat,    0, 5)
        # Fila 1
        grid.addWidget(QLabel("Precio compra:"), 1, 0); grid.addWidget(self._inp_compra, 1, 1)
        grid.addWidget(QLabel("Precio venta *:"),1, 2); grid.addWidget(self._inp_venta,  1, 3)
        grid.addWidget(QLabel("Stock inicial:"), 1, 4); grid.addWidget(self._inp_stock,  1, 5)
        grid.addWidget(QLabel("Stock mínimo:"),  1, 6); grid.addWidget(self._inp_minimo, 1, 7)
        root.addWidget(grp)

        # ── Botones + buscador ──────────────────────────────
        hl = QHBoxLayout()

        self._btn_guardar = QPushButton("💾  Guardar Producto")
        self._btn_guardar.setObjectName("btn_verde")
        self._btn_guardar.clicked.connect(self._guardar_producto)

        btn_limpiar = QPushButton("🧹  Limpiar")
        btn_limpiar.clicked.connect(self._limpiar_form_inv)

        self._btn_desac  = QPushButton("🚫  Desactivar")
        self._btn_desac.setObjectName("btn_rojo")
        self._btn_desac.setEnabled(False)
        self._btn_desac.clicked.connect(self._desactivar_producto)

        self._btn_ajuste = QPushButton("📦  Ajustar Stock")
        self._btn_ajuste.setObjectName("btn_naranja")
        self._btn_ajuste.setEnabled(False)
        self._btn_ajuste.clicked.connect(self._ajustar_stock)

        self._inp_buscar = QLineEdit()
        self._inp_buscar.setPlaceholderText("🔍  Buscar por nombre, código o categoría...")
        self._inp_buscar.textChanged.connect(
            lambda t: self._cargar_productos(t)
        )

        hl.addWidget(self._btn_guardar)
        hl.addWidget(btn_limpiar)
        hl.addWidget(self._btn_desac)
        hl.addWidget(self._btn_ajuste)
        hl.addStretch()
        hl.addWidget(self._inp_buscar)
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
        self._tabla_prods.clicked.connect(self._cargar_prod_en_form)
        root.addWidget(self._tabla_prods)

        return w

    # ── helpers de inventario ──────────────────────────────

    def _guardar_producto(self):
        codigo = self._inp_cod.text().strip()
        nombre = self._inp_nom.text().strip()
        cat    = self._inp_cat.text().strip()
        compra = self._inp_compra.value()
        venta  = self._inp_venta.value()
        stock  = self._inp_stock.value()
        minimo = self._inp_minimo.value()
        fecha  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not codigo:
            QMessageBox.warning(self, "Falta código",
                                "El código de barras es obligatorio.")
            return
        if not nombre:
            QMessageBox.warning(self, "Falta nombre",
                                "El nombre del producto es obligatorio.")
            return
        if venta <= 0:
            QMessageBox.warning(self, "Precio inválido",
                                "El precio de venta debe ser mayor a $0.00.")
            return

        try:
            with conectar() as conn:
                c = conn.cursor()

                if self._pid_editando:
                    # ── Modo edición ───────────────────────
                    c.execute("""
                        UPDATE productos SET
                            codigo_barras = ?, nombre = ?, categoria = ?,
                            precio_compra = ?, precio_venta = ?, stock_minimo = ?
                        WHERE id = ?
                    """, (codigo, nombre, cat, compra, venta, minimo,
                          self._pid_editando))
                    QMessageBox.information(self, "Actualizado",
                                            "Producto actualizado correctamente.")
                    self._statusbar.showMessage(f"«{nombre}» actualizado.", 3000)

                else:
                    # ── Alta de producto ───────────────────
                    c.execute("""
                        INSERT INTO productos
                            (codigo_barras, nombre, categoria, precio_compra,
                             precio_venta, stock, stock_minimo, fecha_alta)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (codigo, nombre, cat, compra, venta, stock, minimo, fecha))
                    pid = c.lastrowid
                    if stock > 0:
                        c.execute("""
                            INSERT INTO movimientos_inventario
                                (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                            VALUES (?, 'ENTRADA', ?, 'Alta inicial de producto', ?)
                        """, (pid, stock, fecha))
                    QMessageBox.information(self, "Guardado",
                                            "Producto registrado correctamente.")
                    self._statusbar.showMessage(f"«{nombre}» registrado.", 3000)

            self._limpiar_form_inv()
            self._cargar_productos()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Código duplicado",
                                "Ya existe un producto con ese código de barras.")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar",
                                 f"No se pudo guardar el producto:\n{e}")

    def _cargar_prod_en_form(self, index):
        """Carga la fila seleccionada en el formulario para editar."""
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
        self._inp_cod.setText(p[1])
        self._inp_nom.setText(p[2])
        self._inp_cat.setText(p[3] or "")
        self._inp_compra.setValue(p[4])
        self._inp_venta.setValue(p[5])
        self._inp_stock.setValue(p[6])
        self._inp_stock.setEnabled(False)   # usa el botón de ajuste para cambiar stock
        self._inp_minimo.setValue(p[7])

        self._btn_guardar.setText("💾  Actualizar Producto")
        self._btn_desac.setEnabled(True)
        self._btn_ajuste.setEnabled(True)
        self._statusbar.showMessage(
            f"Editando: «{p[2]}»  (ID {p[0]})  —  "
            f"Usa 'Ajustar Stock' para cambiar existencias.", 6000
        )

    def _limpiar_form_inv(self):
        self._pid_editando = None
        for w in (self._inp_cod, self._inp_nom, self._inp_cat):
            w.clear()
        for w in (self._inp_compra, self._inp_venta):
            w.setValue(0)
        self._inp_stock.setValue(0)
        self._inp_stock.setEnabled(True)
        self._inp_minimo.setValue(5)
        self._btn_guardar.setText("💾  Guardar Producto")
        self._btn_desac.setEnabled(False)
        self._btn_ajuste.setEnabled(False)

    def _desactivar_producto(self):
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
            self._statusbar.showMessage(f"«{nombre}» desactivado.", 4000)

    def _ajustar_stock(self):
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

        d     = dlg.resultado()
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
            else:  # AJUSTE — establecer valor absoluto
                c.execute("UPDATE productos SET stock = ? WHERE id = ?",
                          (d["cantidad"], self._pid_editando))

            c.execute("""
                INSERT INTO movimientos_inventario
                    (producto_id, tipo_movimiento, cantidad, motivo, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (self._pid_editando, d["tipo"], d["cantidad"], d["motivo"], fecha))

        self._limpiar_form_inv()
        self._cargar_productos()
        self._statusbar.showMessage(
            f"Stock de «{nombre}» ajustado — {d['tipo']}: {d['cantidad']} uds.", 4000
        )

    def _cargar_productos(self, filtro=""):
        q = filtro.strip()
        with conectar() as conn:
            c = conn.cursor()
            if q:
                like = f"%{q}%"
                c.execute("""
                    SELECT id, codigo_barras, nombre, categoria,
                           precio_compra, precio_venta, stock, stock_minimo, activo
                    FROM productos
                    WHERE nombre LIKE ? OR codigo_barras LIKE ? OR categoria LIKE ?
                    ORDER BY nombre
                """, (like, like, like))
            else:
                c.execute("""
                    SELECT id, codigo_barras, nombre, categoria,
                           precio_compra, precio_venta, stock, stock_minimo, activo
                    FROM productos ORDER BY nombre
                """)
            rows = c.fetchall()

        self._tabla_prods.setRowCount(len(rows))
        C_ROJO = QColor("#f38ba8")
        C_AMAR = QColor("#f9e2af")
        C_DARK = QColor("#1e1e2e")

        for fila, row in enumerate(rows):
            pid, cod, nom, cat, compra, venta, stock, minimo, activo = row
            estado = "✅ Activo" if activo else "🚫 Inactivo"
            vals   = [
                str(pid), cod, nom, cat or "",
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

        lbl = QLabel("Ventas del Día")
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
        hl.addStretch()
        root.addLayout(hl)

        # ── Tarjetas resumen ────────────────────────────────
        hl_cards = QHBoxLayout()
        hl_cards.setSpacing(12)
        self._cards = {}
        for clave, titulo, color in [
            ("total", "Total vendido",   "#a6e3a1"),
            ("num",   "No. de ventas",   "#89b4fa"),
            ("prom",  "Ticket promedio", "#f9e2af"),
        ]:
            grp   = QGroupBox(titulo)
            vl    = QVBoxLayout(grp)
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
        self._tabla_ventas.setColumnCount(4)
        self._tabla_ventas.setHorizontalHeaderLabels(
            ["ID", "Fecha y Hora", "Total", "Método de Pago"]
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

    def _cargar_ventas(self):
        if not hasattr(self, "_date_rep"):
            return
        fecha = self._date_rep.date().toString("yyyy-MM-dd")

        with conectar() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, fecha, total, metodo_pago
                FROM ventas WHERE fecha LIKE ?
                ORDER BY fecha DESC
            """, (f"{fecha}%",))
            ventas = c.fetchall()

            c.execute("""
                SELECT COALESCE(SUM(total), 0), COUNT(*)
                FROM ventas WHERE fecha LIKE ?
            """, (f"{fecha}%",))
            total_dia, num = c.fetchone()

        prom = total_dia / num if num else 0.0
        self._cards["total"].setText(f"${total_dia:.2f}")
        self._cards["num"].setText(str(num))
        self._cards["prom"].setText(f"${prom:.2f}")

        self._tabla_ventas.setRowCount(len(ventas))
        for fila, (vid, fv, tot, metodo) in enumerate(ventas):
            for col, val in enumerate([str(vid), fv, f"${tot:.2f}", metodo]):
                cell = QTableWidgetItem(val)
                cell.setTextAlignment(Qt.AlignCenter)
                self._tabla_ventas.setItem(fila, col, cell)

    def _ver_detalle(self, index):
        fila   = index.row()
        vid    = int(self._tabla_ventas.item(fila, 0).text())
        fecha  = self._tabla_ventas.item(fila, 1).text()
        total  = float(self._tabla_ventas.item(fila, 2).text().replace("$", ""))
        metodo = self._tabla_ventas.item(fila, 3).text()
        DialogoDetalleVenta(vid, fecha, total, metodo, self).exec()


# ──────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    crear_tablas()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = POSAbarrotes()
    ventana.show()
    sys.exit(app.exec())