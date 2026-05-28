# Punto de Venta Abarrotes - Tienda Periquita

Sistema de escritorio para punto de venta, inventario, cortes de caja, compras a proveedores y reportes de ventas para una tienda de abarrotes.

## Como ejecutarlo

### Opcion 1: desde Python

```powershell
pip install PySide6
py pos_abarrotes.py
```

El programa crea automaticamente la base `abarrotes_pos.db` si no existe.

### Opcion 2: desde el ejecutable

Tambien se puede usar el archivo:

```text
Aplicacion de Venta - Tienda Periquita.exe
```

Para que el ejecutable conserve ventas, inventario y cortes, deben quedarse junto al programa estos archivos:

```text
abarrotes_pos.db
abarrotes_pos_respaldo.db
assets/
```

## Accesos iniciales

```text
Administrador:
usuario: admin
contrasena: admin123

Vendedor:
usuario: vendedor
contrasena: venta123
```

Al iniciar como vendedor, el sistema pide el nombre real de quien esta atendiendo caja. Ese nombre se guarda en ventas, cortes y KPIs.

## Base de datos y respaldo

- `abarrotes_pos.db` guarda inventario, ventas, usuarios, compras, tickets pendientes y cortes.
- `abarrotes_pos_respaldo.db` es una copia de respaldo generada por el sistema.
- Si se va la luz o se cierra el programa por accidente, SQLite usa modo WAL y el ticket pendiente se restaura al volver a entrar con el mismo vendedor.

## Nota importante

No recomiendo subir una base `.db` real a un repositorio publico porque puede contener ventas, nombres de vendedores, cortes de caja y datos del negocio. Para GitHub es mejor subir el codigo y documentar como se genera la base automaticamente.

## Documentacion

- [Comentarios de mejora](MEJORAS.md)
- [Uso de archivos locales](docs/USO_ARCHIVOS_LOCALES.md)
