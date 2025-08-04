import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

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
def check(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Uso: /stock nombre_producto")
        return
    producto = ' '.join(context.args).lower()
    cantidad = stock.get(producto, 0)
    update.message.reply_text(f"📦 Stock de *{producto}*: {cantidad} unidades.", parse_mode='Markdown')

# /agregar <producto> <cantidad>
def add(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("Uso: /agregar nombre_producto cantidad")
        return
    producto = ' '.join(context.args[:-1]).lower()
    try:
        cantidad = int(context.args[-1])
        stock[producto] = stock.get(producto, 0) + cantidad
        save_stock()
        update.message.reply_text(f"✅ Se agregaron {cantidad} a *{producto}*. Nuevo stock: {stock[producto]}", parse_mode='Markdown')
    except ValueError:
        update.message.reply_text("🚫 La cantidad debe ser un número.")

# /quitar <producto> <cantidad>
def remove(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("Uso: /quitar nombre_producto cantidad")
        return
    producto = ' '.join(context.args[:-1]).lower()
    try:
        cantidad = int(context.args[-1])
        if stock.get(producto, 0) >= cantidad:
            stock[producto] -= cantidad
            save_stock()
            update.message.reply_text(f"❌ Se quitaron {cantidad} de *{producto}*. Nuevo stock: {stock[producto]}", parse_mode='Markdown')
        else:
            update.message.reply_text("🚫 No hay suficiente stock para quitar.")
    except ValueError:
        update.message.reply_text("🚫 La cantidad debe ser un número.")

# /vendido <producto> [cantidad]
def sold(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Uso: /vendido nombre_producto [cantidad]")
        return
    *producto_partes, cantidad_str = context.args if context.args[-1].isdigit() else (context.args + ["1"])
    producto = ' '.join(producto_partes).lower()
    cantidad = int(cantidad_str)
    if stock.get(producto, 0) >= cantidad:
        stock[producto] -= cantidad
        save_stock()
        guardar_log_venta(producto.title(), cantidad, update.effective_user.first_name)
        update.message.reply_text(f"🛒 Vendiste {cantidad} unidad(es) de *{producto}*. Stock restante: {stock[producto]}", parse_mode='Markdown')
    else:
        update.message.reply_text("🚫 No hay suficiente stock disponible.")

# /listado
def listado(update: Update, context: CallbackContext):
    if not stock:
        update.message.reply_text("📦 No hay productos cargados aún.")
        return
    mensaje = "📋 *Stock actual:*\n\n"
    for producto, cantidad in stock.items():
        mensaje += f"• {producto.title()}: {cantidad} unidades\n"
    update.message.reply_text(mensaje, parse_mode='Markdown')

# /reset
def reset(update: Update, context: CallbackContext):
    stock.clear()
    save_stock()
    update.message.reply_text("🧹 Todo el stock fue borrado.")

# /ayuda
def ayuda(update: Update, context: CallbackContext):
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
    update.message.reply_text(mensaje, parse_mode='Markdown')

# /historial
def historial(update: Update, context: CallbackContext):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()[-15:]  # Muestra las últimas 15 líneas
            if logs:
                mensaje = "📝 *Últimas ventas:*\n\n" + ''.join(logs)
            else:
                mensaje = "📭 El historial está vacío."
    else:
        mensaje = "🚫 No se encontró el archivo de historial."
    update.message.reply_text(mensaje, parse_mode='Markdown')

# MAIN
def main():
    TOKEN = '8434570266:AAEiWMAD3sUX8yVWqO0LTj2i4zHoMvcp2Dw'
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("stock", check))
    dp.add_handler(CommandHandler("agregar", add))
    dp.add_handler(CommandHandler("quitar", remove))
    dp.add_handler(CommandHandler("vendido", sold))
    dp.add_handler(CommandHandler("listado", listado))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("ayuda", ayuda))
    dp.add_handler(CommandHandler("historial", historial))

    updater.start_polling()
    print("🤖 Bot iniciado. Usalo desde Telegram.")
    updater.idle()

if __name__ == '__main__':
    main()