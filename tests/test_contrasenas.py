"""Tests de la feature 002/004: contraseñas con sal (PBKDF2), migración
silenciosa de hashes legados, reglas de cambio y primer arranque sin
claves quemadas en el código (el repo es público)."""

from pathlib import Path

import pytest

import pos_abarrotes as pos


# ── Hash y verificación (puros, sin BD) ─────────────────────────────


def test_pbkdf2_formato_y_sal_aleatoria():
    h1 = pos.hash_password_pbkdf2("secreta", iteraciones=1_000)
    h2 = pos.hash_password_pbkdf2("secreta", iteraciones=1_000)
    assert h1.startswith("pbkdf2$1000$")
    assert h1 != h2                     # sal distinta aun con la misma clave
    assert pos.verificar_password("secreta", h1)
    assert pos.verificar_password("secreta", h2)
    assert not pos.verificar_password("otra", h1)


def test_verificar_password_acepta_hash_legado():
    legado = pos.hash_password("clave-legada")  # SHA-256 sin sal (versión vieja)
    assert pos.verificar_password("clave-legada", legado)
    assert not pos.verificar_password("incorrecta", legado)
    assert not pos.verificar_password("lo-que-sea", "")
    assert not pos.verificar_password("x", "pbkdf2$basura")   # malformado


def test_codigo_sin_claves_quemadas():
    """El repo es público: ninguna clave histórica puede vivir en el
    fuente NI en este test (por eso se guardan invertidas). Las cuentas
    se crean en el primer arranque (DialogoPrimerUsuario)."""
    fuente = Path(pos.__file__).read_text(encoding="utf-8")
    claves_invertidas = ("321nimda", "321atnev", "654atnev", "987atnev")
    for invertida in claves_invertidas:
        assert invertida[::-1] not in fuente


# ── Primer arranque y usuarios ──────────────────────────────────────


def test_bd_nueva_no_siembra_usuarios(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pos, "ITERACIONES_PBKDF2", 1_000)
    pos.crear_tablas()
    assert not pos.hay_usuarios_activos()   # nadie hasta el primer arranque


def test_crear_usuario_y_login(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pos, "ITERACIONES_PBKDF2", 1_000)
    pos.crear_tablas()
    with pos.conectar() as conn:
        pos.crear_usuario(conn, "admin", "Administrador", "admin", "MiClave1")
    assert pos.hay_usuarios_activos()
    sesion = pos.validar_login("admin", "MiClave1")
    assert sesion is not None and sesion["rol"] == "admin"


def test_usuarios_de_prueba_usan_pbkdf2(bd_temporal):
    with pos.conectar() as conn:
        hashes = [f[0] for f in conn.execute(
            "SELECT password_hash FROM usuarios")]
    assert hashes
    assert all(h.startswith("pbkdf2$") for h in hashes)


# ── Migración y login (con BD temporal) ─────────────────────────────


def test_login_migra_hash_legado_sin_romper_la_clave(bd_temporal):
    # Simula una BD de tienda real: hash SHA-256 de la versión anterior
    with pos.conectar() as conn:
        conn.execute("UPDATE usuarios SET password_hash = ? "
                     "WHERE usuario = 'admin'",
                     (pos.hash_password("clave-prueba-admin"),))

    sesion = pos.validar_login("admin", "clave-prueba-admin")  # entra igual
    assert sesion is not None

    with pos.conectar() as conn:
        (h,) = conn.execute("SELECT password_hash FROM usuarios "
                            "WHERE usuario = 'admin'").fetchone()
    assert h.startswith("pbkdf2$")                    # migrado sin avisar

    assert pos.validar_login("admin", "clave-prueba-admin") is not None
    assert pos.validar_login("admin", "incorrecta") is None


# ── Cambio de contraseña ────────────────────────────────────────────


def test_cambiar_password_valida_reglas(bd_temporal):
    sesion = pos.validar_login("admin", "clave-prueba-admin")
    with pytest.raises(ValueError):
        pos.cambiar_password(sesion["id"], "")
    with pytest.raises(ValueError):
        pos.cambiar_password(sesion["id"], "   ")
    # Nada cambió: sigue entrando con la original
    assert pos.validar_login("admin", "clave-prueba-admin") is not None


def test_cambio_de_password_invalida_la_vieja(bd_temporal):
    sesion = pos.validar_login("vendedor", "clave-prueba-venta")
    pos.cambiar_password(sesion["id"], "clave nueva")
    assert pos.validar_login("vendedor", "clave-prueba-venta") is None
    assert pos.validar_login("vendedor", "clave nueva") is not None
