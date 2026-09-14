import json
import os
import asyncio
from fastapi import FastAPI, Request

from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters

from scraper import extract_price


# ============================
# CONFIGURACIÓN DEL BOT
# ============================

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# Crear aplicación PTB sin Updater (modo webhook)
application = Application.builder().token(TOKEN).updater(None).build()

# FastAPI app
app = FastAPI()


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

    # Obtener el event loop correcto del worker ASGI
    loop = asyncio.get_running_loop()

    # Ejecutar extract_price() en thread pool (Playwright)
    for ota, url in urls.items():
        if url:
            prices[ota] = await loop.run_in_executor(None, extract_price, url)
        else:
            prices[ota] = "No disponible"

    msg = format_response(hotel, prices)

    # Limitar tamaño para evitar error "Text is too long"
    msg = msg[:4000]

    await update.message.reply_text(msg)


# Registrar handler
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ============================
# WEBHOOK (NO BLOQUEA)
# ============================

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    # Enviar el update a la cola interna de PTB (no bloquear el webhook)
    await application.update_queue.put(update)

    # Responder inmediatamente a Telegram
    return {"status": "ok"}


@app.get("/")
async def health():
    return {"status": "ok"}


# ============================
# INICIALIZAR PTB
# ============================

@app.on_event("startup")
async def startup_event():
    await application.initialize()
    await application.start()   # <-- IMPORTANTE
