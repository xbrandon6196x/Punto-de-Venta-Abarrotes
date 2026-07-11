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
    """BD nueva y aislada por test, con esquema y usuarios iniciales."""
    monkeypatch.chdir(tmp_path)
    pos_abarrotes.crear_tablas()
    return tmp_path
