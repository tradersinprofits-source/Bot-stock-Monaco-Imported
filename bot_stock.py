import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

STOCK_FILE = 'stock.json'
LOG_FILE = 'ventas_log.txt'

# Cargar stock
try:
    with open(STOCK_FILE, 'r') as f:
        stock = json.load(f)
except FileNotFoundError:
    stock = {}

# Guardar stock
def save_stock():
    with open(STOCK_FILE, 'w') as f:
        json.dump(stock, f, indent=2)

# Guardar log de ventas
def guardar_log_venta(producto, cantidad, usuario):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{usuario}: Vendió {cantidad} unidad(es) de {producto}\n")

# /stock <producto>
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /stock nombre_producto")
        return
    producto = ' '.join(context.args).lower()
    cantidad = stock.get(producto, 0)
    await update.message.reply_text(f"📦 Stock de *{producto}*: {cantidad} unidades.", parse_mode='Markdown')

# /agregar <producto> <cantidad>
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /agregar nombre_producto cantidad")
        return
    producto = ' '.join(context.args[:-1]).lower()
    try:
        cantidad = int(context.args[-1])
        stock[producto] = stock.get(producto, 0) + cantidad
        save_stock()
        await update.message.reply_text(f"✅ Se agregaron {cantidad} a *{producto}*. Nuevo stock: {stock[producto]}", parse_mode='Markdown')
    except ValueError:
        await update.message.reply_text("🚫 La cantidad debe ser un número.")

# /quitar <producto> <cantidad>
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /quitar nombre_producto cantidad")
        return
    producto = ' '.join(context.args[:-1]).lower()
    try:
        cantidad = int(context.args[-1])
        if stock.get(producto, 0) >= cantidad:
            stock[producto] -= cantidad
            save_stock()
            await update.message.reply_text(f"❌ Se quitaron {cantidad} de *{producto}*. Nuevo stock: {stock[producto]}", parse_mode='Markdown')
        else:
            await update.message.reply_text("🚫 No hay suficiente stock para quitar.")
    except ValueError:
        await update.message.reply_text("🚫 La cantidad debe ser un número.")

# /vendido <producto> [cantidad]
async def sold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /vendido nombre_producto [cantidad]")
        return
    *producto_partes, cantidad_str = context.args if context.args[-1].isdigit() else (context.args + ["1"])
    producto = ' '.join(producto_partes).lower()
    cantidad = int(cantidad_str)
    if stock.get(producto, 0) >= cantidad:
        stock[producto] -= cantidad
        save_stock()
        guardar_log_venta(producto.title(), cantidad, update.effective_user.first_name)
        await update.message.reply_text(f"🛒 Vendiste {cantidad} unidad(es) de *{producto}*. Stock restante: {stock[producto]}", parse_mode='Markdown')
    else:
        await update.message.reply_text("🚫 No hay suficiente stock disponible.")

# /listado
async def listado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not stock:
        await update.message.reply_text("📦 No hay productos cargados aún.")
        return
    mensaje = "📋 *Stock actual:*\n\n"
    for producto, cantidad in stock.items():
        mensaje += f"• {producto.title()}: {cantidad} unidades\n"
    await update.message.reply_text(mensaje, parse_mode='Markdown')

# /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock.clear()
    save_stock()
    await update.message.reply_text("🧹 Todo el stock fue borrado.")

# /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """📖 *Comandos disponibles:*

/stock <producto> - Consulta el stock de un producto.
/agregar <producto> <cantidad> - Agrega unidades.
/quitar <producto> <cantidad> - Quita unidades.
/vendido <producto> [cantidad] - Marca como vendido.
/listado - Muestra el stock completo.
/historial - Muestra el historial de ventas.
/reset - Borra todo el stock.
/ayuda - Muestra esta ayuda.
"""
    await update.message.reply_text(mensaje, parse_mode='Markdown')

# /historial
async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()[-15:]
            if logs:
                mensaje = "📝 *Últimas ventas:*\n\n" + ''.join(logs)
            else:
                mensaje = "📭 El historial está vacío."
    else:
        mensaje = "🚫 No se encontró el archivo de historial."
    await update.message.reply_text(mensaje, parse_mode='Markdown')

# MAIN
async def main():
    TOKEN = 'TU_TOKEN_ACÁ'
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("stock", check))
    app.add_handler(CommandHandler("agregar", add))
    app.add_handler(CommandHandler("quitar", remove))
    app.add_handler(CommandHandler("vendido", sold))
    app.add_handler(CommandHandler("listado", listado))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("historial", historial))

    print("🤖 Bot iniciado. Usalo desde Telegram.")
    await app.run_polling()

# Ejecutar
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
