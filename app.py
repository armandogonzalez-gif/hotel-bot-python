import json
import os
import asyncio
from flask import Flask, request
from scraper import extract_price

from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters

# ============================
# CONFIGURACIÓN DEL BOT
# ============================

TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)

# Crear aplicación PTB sin Updater (modo webhook)
application = Application.builder().token(TOKEN).updater(None).build()

app = Flask(__name__)

# ============================
# CARGAR HOTELES
# ============================

with open("hotels.json", "r") as f:
    HOTELS = json.load(f)

# ============================
# FORMATEAR RESPUESTA
# ============================

def format_response(hotel_name, prices):
    motor_price = prices["motor"]

    try:
        motor_value = float(motor_price.replace("$", "").replace(",", ""))
    except:
        motor_value = None

    msg = f"🏨 {hotel_name} — Precios\n\n"
    msg += f"🔧 Motor: {motor_price}\n\n"

    icons = {
        "expedia": "🟦",
        "despegar": "🟧",
        "bestday": "🟩",
        "agoda": "🟪"
    }

    for ota, price in prices.items():
        if ota == "motor":
            continue

        icon = icons.get(ota, "➡️")

        if motor_value:
            try:
                ota_value = float(price.replace("$", "").replace(",", ""))
                diff = ((ota_value - motor_value) / motor_value) * 100
                msg += f"{icon} {ota.capitalize()}: {price}  ({diff:.1f}% vs Motor)\n"
            except:
                msg += f"{icon} {ota.capitalize()}: {price}\n"
        else:
            msg += f"{icon} {ota.capitalize()}: {price}\n"

    return msg

# ============================
# HANDLER PRINCIPAL
# ============================

async def handle_message(update: Update, context):
    hotel = update.message.text.strip()

    if hotel not in HOTELS:
        await update.message.reply_text("Hotel no encontrado.")
        return

    urls = HOTELS[hotel]
    prices = {}

    for ota, url in urls.items():
        if url:
            prices[ota] = extract_price(url)
        else:
            prices[ota] = "No disponible"

    msg = format_response(hotel, prices)

    # 🔥 Limitar tamaño para evitar error "Text is too long"
    msg = msg[:4000]

    await update.message.reply_text(msg)

# Registrar handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ============================
# WEBHOOK
# ============================

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/", methods=["GET"])
def health():
    return "ok", 200

# ============================
# INICIALIZAR PTB
# ============================

asyncio.run(application.initialize())

# ============================
# LEVANTAR FLASK EN RENDER
# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
