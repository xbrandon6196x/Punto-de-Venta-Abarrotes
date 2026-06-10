# Uso de Archivos Locales

Este documento explica para que sirve cada archivo generado o usado por la aplicacion.

## Aplicacion de Venta - Tienda Periquita.exe

Este archivo abre el sistema sin necesidad de ejecutar Python desde la terminal. Lo uso cuando quiero entregar una version lista para abrir con doble clic en Windows.

Debe mantenerse en la misma carpeta donde esten:

- `abarrotes_pos.db`
- `abarrotes_pos_respaldo.db`
- `assets/`

## abarrotes_pos.db

Esta es la base principal de SQLite. Aqui se guarda:

- productos
- inventario
- ventas
- detalle de ventas
- usuarios y sesiones
- cortes de caja
- compras a proveedores
- clientes
- apartados y abonos
- prestamos y devoluciones
- tickets pendientes
- historial de movimientos

Si este archivo se borra, el sistema puede crear una base nueva, pero se perderian los datos que no esten respaldados.

## abarrotes_pos_respaldo.db

Esta es una copia de respaldo. La agregue para tener una segunda base local en caso de cierre inesperado, falla electrica o error del archivo principal.

Si necesito recuperar informacion, primero reviso este respaldo antes de iniciar una base desde cero.

## assets/

Esta carpeta guarda los recursos visuales del sistema, incluyendo los cuadros y GIFs del perrito asistente.

Archivos importantes:

- `assets/perrito_config.json`: frases y mapeo de animaciones por evento.
- `assets/animacion/`: GIFs, WebP y frames por accion.
- `assets/perrito_frames/`: frames PNG originales de respaldo.

Si se mueve o se borra, el programa sigue funcionando, pero el perrito puede no aparecer.

Puedo cambiar frases sin tocar el codigo editando `assets/perrito_config.json`.

## Que no debo publicar con datos reales

No debo publicar una base real en GitHub si ya contiene informacion del negocio. Antes de subir una base debo confirmar que sea una base vacia o de prueba.
