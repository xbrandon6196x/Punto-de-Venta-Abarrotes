# Misión

## Qué se construye

Un punto de venta de escritorio para **Tienda Periquita**, una tienda de
abarrotes real: cobrar rápido con lector de código de barras, controlar
inventario y dinero (cortes de caja por vendedor), registrar compras a
proveedores, apartados y préstamos de clientes, y darle al administrador
reportes de ventas y ganancia.

## Para quién

- **Vendedor(a) de mostrador**: persona no técnica que necesita cobrar en
  segundos, con teclado/lector, sin leer manuales.
- **Administrador (dueño)**: controla inventario, precios, cortes y
  reportes; es quien decide qué se construye.

## Principios innegociables

1. **El dinero cuadra.** Cualquier operación que mueva dinero queda
   registrada, atribuida a un vendedor y entra correctamente a la fórmula
   del corte. Un corte que no cuadra es el peor bug posible.
2. **Los datos de la tienda no se pierden.** WAL + respaldo automático;
   toda versión nueva del código abre la BD existente sin migración manual.
3. **Simple de operar.** Un archivo `.py` o un `.exe`; la BD se crea sola;
   sin instalación técnica. La UI habla español claro.
4. **Rastro de todo**: stock, precios y movimientos de clientes tienen
   historial auditable.
5. **El humano dirige, la IA ejecuta.** El dueño es el responsable final y
   Validador de Intentos de cualquier cambio; la potencia sin control no
   sirve de nada.

## Qué NO es este proyecto

- NO es un sistema multi-sucursal ni una app web/nube (hoy: una máquina,
  una BD local; ver roadmap para multi-equipo).
- NO es un ERP: no maneja facturación fiscal (CFDI), nómina ni contabilidad.
- NO es un producto para vender a otras tiendas (por ahora es a medida).
