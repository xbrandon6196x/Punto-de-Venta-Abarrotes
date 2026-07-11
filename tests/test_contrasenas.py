"""Tests de la feature 002: contraseñas con sal (PBKDF2), migración
silenciosa de hashes legados y reglas de cambio de contraseña."""

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
    legado = pos.hash_password("venta123")     # SHA-256 sin sal (versión vieja)
    assert pos.verificar_password("venta123", legado)
    assert not pos.verificar_password("incorrecta", legado)
    assert not pos.verificar_password("lo-que-sea", "")
    assert not pos.verificar_password("x", "pbkdf2$basura")   # malformado


def test_es_password_por_defecto():
    assert pos.es_password_por_defecto("admin123")
    assert pos.es_password_por_defecto("venta123")
    assert pos.es_password_por_defecto("venta789")
    assert not pos.es_password_por_defecto("PeriquitaSegura9")
    assert not pos.es_password_por_defecto("")


# ── Migración y login (con BD temporal) ─────────────────────────────


def test_usuarios_iniciales_ya_usan_pbkdf2(bd_temporal):
    with pos.conectar() as conn:
        hashes = [f[0] for f in conn.execute(
            "SELECT password_hash FROM usuarios")]
    assert hashes
    assert all(h.startswith("pbkdf2$") for h in hashes)


def test_login_migra_hash_legado_sin_romper_la_clave(bd_temporal):
    # Simula una BD de tienda real: hash SHA-256 de la versión anterior
    with pos.conectar() as conn:
        conn.execute("UPDATE usuarios SET password_hash = ? "
                     "WHERE usuario = 'admin'",
                     (pos.hash_password("admin123"),))

    sesion = pos.validar_login("admin", "admin123")   # entra igual que antes
    assert sesion is not None

    with pos.conectar() as conn:
        (h,) = conn.execute("SELECT password_hash FROM usuarios "
                            "WHERE usuario = 'admin'").fetchone()
    assert h.startswith("pbkdf2$")                    # migrado sin avisar

    assert pos.validar_login("admin", "admin123") is not None
    assert pos.validar_login("admin", "incorrecta") is None


def test_login_marca_password_por_defecto(bd_temporal):
    sesion = pos.validar_login("admin", "admin123")
    assert sesion["password_por_defecto"] is True

    pos.cambiar_password(sesion["id"], "NuevaClave9")
    sesion2 = pos.validar_login("admin", "NuevaClave9")
    assert sesion2 is not None
    assert sesion2["password_por_defecto"] is False


# ── Cambio de contraseña ────────────────────────────────────────────


def test_cambiar_password_valida_reglas(bd_temporal):
    sesion = pos.validar_login("admin", "admin123")
    with pytest.raises(ValueError):
        pos.cambiar_password(sesion["id"], "")
    with pytest.raises(ValueError):
        pos.cambiar_password(sesion["id"], "   ")
    with pytest.raises(ValueError):
        pos.cambiar_password(sesion["id"], "venta123")    # otra por defecto
    # Nada cambió: sigue entrando con la original
    assert pos.validar_login("admin", "admin123") is not None


def test_cambio_de_password_invalida_la_vieja(bd_temporal):
    sesion = pos.validar_login("vendedor", "venta123")
    pos.cambiar_password(sesion["id"], "clave nueva")
    assert pos.validar_login("vendedor", "venta123") is None
    assert pos.validar_login("vendedor", "clave nueva") is not None
