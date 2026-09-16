from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import calendar
from datetime import datetime


def build_calendar(year, month, action_prefix):
    """
    Construye un calendario interactivo para Telegram usando InlineKeyboardMarkup.
    action_prefix: "checkin" o "checkout"
    """

    keyboard = []

    # Encabezado del mes
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


def navigate_calendar(year, month, direction):
    """
    Cambia el mes del calendario según el botón presionado.
    direction: "prev" o "next"
    """

    if direction == "prev":
        month -= 1
    else:
        month += 1

    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    return year, month
