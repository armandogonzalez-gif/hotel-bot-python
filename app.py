import json
import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request

from telegram import (
    Bot,
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    MessageHandler,
    CallbackQueryHandler,
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
# CALENDARIO INTERACTIVO
# ============================

def build_calendar(year, month, action_prefix):
    import calendar

    keyboard = []

    # Encabezado
    keyboard.append([
        InlineKeyboardButton("<<", callback_data=f"{action_prefix}_prev"),
        InlineKeyboardButton(f"{calendar.month_name[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(">>", callback_data=f"{action_prefix}_next")
    ])

    # Días de la semana
    keyboard.append([
        InlineKeyboardButton(day, callback_data="ignore")
        for day in ["L", "M", "X", "J", "V", "S", "D"]
    ])

    # Días del mes
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data="ignore"))
            else:
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=f"{action_prefix}_{year}-{month:02d}-{day:02d}"
                    )
                )
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


# ============================
# FORMATEAR RESPUESTA
# ============================

def format_response(hotel_name, prices):
    motor_price = prices.get("motor", "No disponible")

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
        "pricetravel": "🟪"
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

    now = datetime.now()
    calendar_markup = build_calendar(now.year, now.month, "checkin")

    await update.message.reply_text(
        f"Perfecto, seleccionaste *{hotel}*.\n\n📅 Selecciona fecha de entrada:",
        parse_mode="Markdown",
        reply_markup=calendar_markup
    )

    return ASK_CHECKIN


async def calendar_callback(update: Update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Ignorar botones
    if data == "ignore":
        return

    # Navegación del calendario
    if data.startswith("checkin_prev") or data.startswith("checkin_next"):
        return await navigate_calendar(update, context, "checkin")

    if data.startswith("checkout_prev") or data.startswith("checkout_next"):
        return await navigate_calendar(update, context, "checkout")

    # Selección de check-in
    if data.startswith("checkin_"):
        date = data.replace("checkin_", "")
        context.user_data["checkin"] = date

        now = datetime.now()
        calendar_markup = build_calendar(now.year, now.month, "checkout")

        await query.edit_message_text(
            f"Check-in seleccionado: {date}\n\n📅 Selecciona fecha de salida:",
            reply_markup=calendar_markup
        )
        return ASK_CHECKOUT

    # Selección de check-out
    if data.startswith("checkout_"):
        date = data.replace("checkout_", "")
        context.user_data["checkout"] = date

        return await process_dates(update, context)


async def navigate_calendar(update: Update, context, prefix):
    query = update.callback_query
    now = datetime.now()

    year = now.year
    month = now.month

    if prefix == "checkin":
        if "prev" in query.data:
            month -= 1
        else:
            month += 1
    else:
        if "prev" in query.data:
            month -= 1
        else:
            month += 1

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    calendar_markup = build_calendar(year, month, prefix)

    await query.edit_message_reply_markup(calendar_markup)


# ============================
# PROCESAR FECHAS Y SCRAPING
# ============================

async def process_dates(update: Update, context):
    checkout = context.user_data["checkout"]
    checkin = context.user_data["checkin"]
    hotel = context.user_data["hotel"]

    # Convertir fechas
    checkin_dash = checkin
    checkout_dash = checkout

    checkin_slash = "/".join(checkin.split("-")[::-1])
    checkout_slash = "/".join(checkout.split("-")[::-1])

    await update.callback_query.edit_message_text(
        f"Check-in: {checkin_dash}\nCheck-out: {checkout_dash}\n\nBuscando precios…"
    )

    # Construir URLs dinámicas
    urls = {}
    for ota, base_url in HOTELS[hotel].items():
        if not base_url:
            urls[ota] = None
            continue

        final_url = (
            base_url
            .replace("{checkin_dash}", checkin_dash)
            .replace("{checkout_dash}", checkout_dash)
            .replace("{checkin_slash}", checkin_slash)
            .replace("{checkout_slash}", checkout_slash)
        )

        urls[ota] = final_url

    # Ejecutar scraper
    prices = {}
    loop = asyncio.get_running_loop()

    for ota, url in urls.items():
        if url:
            prices[ota] = await loop.run_in_executor(None, extract_price, url)
        else:
            prices[ota] = "No disponible"

    msg = format_response(hotel, prices)
    msg = msg[:4000]

    await update.callback_query.message.reply_text(msg)

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
        ASK_CHECKIN: [CallbackQueryHandler(calendar_callback)],
        ASK_CHECKOUT: [CallbackQueryHandler(calendar_callback)],
    },
    fallbacks=[],
)

application.add_handler(conv_handler)
application.add_handler(CallbackQueryHandler(calendar_callback))


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
