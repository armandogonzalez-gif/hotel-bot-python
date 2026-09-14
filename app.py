import json
import os
import asyncio
from fastapi import FastAPI, Request

from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ConversationHandler
)

from scraper import extract_price


# ============================
# CONFIGURACIÓN DEL BOT
# ============================

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

application = Application.builder().token(TOKEN).updater(None).build()

app = FastAPI()


# ============================
# CARGAR HOTELES
# ============================

with open("hotels.json", "r") as f:
    HOTELS = json.load(f)


# ============================
# MENÚ DE HOTELES
# ============================

HOTEL_MENU = ReplyKeyboardMarkup(
    [
        ["Presidente Acapulco"],
        ["Real Bananas"],
        ["Princess Mundo Imperial"],
        ["Bnow"],
        ["Playa Suites"]
    ],
    resize_keyboard=True
)


# ============================
# ESTADOS DE CONVERSACIÓN
# ============================

ASK_CHECKIN, ASK_CHECKOUT = range(2)


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
# FLUJO DE CONVERSACIÓN
# ============================

async def start(update: Update, context):
    await update.message.reply_text(
        "Selecciona un hotel:",
        reply_markup=HOTEL_MENU
    )


async def ask_checkin(update: Update, context):
    hotel = update.message.text.strip()

    if hotel not in HOTELS:
        await update.message.reply_text("Selecciona un hotel del menú.")
        return ConversationHandler.END

    context.user_data["hotel"] = hotel

    await update.message.reply_text(
        f"Perfecto, seleccionaste *{hotel}*.\n\nAhora dime la fecha de entrada (check-in):",
        parse_mode="Markdown"
    )

    return ASK_CHECKIN


async def ask_checkout(update: Update, context):
    checkin = update.message.text.strip()
    context.user_data["checkin"] = checkin

    await update.message.reply_text(
        "Gracias. Ahora dime la fecha de salida (check-out):"
    )

    return ASK_CHECKOUT


async def process_dates(update: Update, context):
    checkout = update.message.text.strip()
    context.user_data["checkout"] = checkout

    hotel = context.user_data["hotel"]
    checkin = context.user_data["checkin"]

    await update.message.reply_text(
        f"Buscando precios para *{hotel}*\nCheck-in: {checkin}\nCheck-out: {checkout}\n\nUn momento…",
        parse_mode="Markdown"
    )

    urls = HOTELS[hotel]
    prices = {}

    loop = asyncio.get_running_loop()

    for ota, url in urls.items():
        if url:
            prices[ota] = await loop.run_in_executor(None, extract_price, url)
        else:
            prices[ota] = "No disponible"

    msg = format_response(hotel, prices)
    msg = msg[:4000]

    await update.message.reply_text(msg)

    return ConversationHandler.END


# ============================
# REGISTRAR HANDLERS
# ============================

application.add_handler(MessageHandler(filters.COMMAND, start))

conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(
            filters.Regex("^(Presidente Acapulco|Real Bananas|Princess Mundo Imperial|Bnow|Playa Suites)$"),
            ask_checkin
        )
    ],
    states={
        ASK_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_checkout)],
        ASK_CHECKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_dates)],
    },
    fallbacks=[],
)

application.add_handler(conv_handler)


# ============================
# WEBHOOK (NO BLOQUEA)
# ============================

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)

    await application.update_queue.put(update)

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
    await application.start()
