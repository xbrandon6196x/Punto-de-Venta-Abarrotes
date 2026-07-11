"""Configuración común de los tests.

Regla de oro: los tests JAMÁS tocan la BD real de la tienda. `DB_NAME` es
una ruta relativa, así que basta cambiar el directorio de trabajo a una
carpeta temporal: la BD del test nace y muere ahí.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import pos_abarrotes


@pytest.fixture
def bd_temporal(tmp_path, monkeypatch):
    """BD nueva y aislada por test, con esquema y usuarios de PRUEBA.

    El código ya no siembra usuarios con claves fijas (el repo es
    público; ver DialogoPrimerUsuario), así que aquí se crean cuentas
    con claves ficticias solo para los tests."""
    monkeypatch.chdir(tmp_path)
    # PBKDF2 con pocas iteraciones en tests: misma lógica y mismo formato,
    # sin pagar el costo real (600k por hash) en cada test.
    monkeypatch.setattr(pos_abarrotes, "ITERACIONES_PBKDF2", 1_000)
    pos_abarrotes.crear_tablas()
    with pos_abarrotes.conectar() as conn:
        pos_abarrotes.crear_usuario(
            conn, "admin", "Administrador", "admin", "clave-prueba-admin")
        pos_abarrotes.crear_usuario(
            conn, "vendedor", "Perfil de ventas", "vendedor",
            "clave-prueba-venta")
    return tmp_path
