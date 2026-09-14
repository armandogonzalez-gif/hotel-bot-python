#!/usr/bin/env python3
"""
Text to Python Conversion
Generated: 2026-09-14T16:40:22.384Z
Total Lines: 62
"""

def process_text():
    """
    Process and analyze text data
    Returns: dictionary with text data and metadata
    """
    text_lines = [
    "import json",
    "import os",
    "from flask import Flask, request",
    "from scraper import extract_price",
    "from telegram import Bot, Update",
    "from telegram.ext import Dispatcher, MessageHandler, Filters",
    "TOKEN = os.getenv(\"TELEGRAM_TOKEN\")",
    "bot = Bot(token=TOKEN)",
    "app = Flask(__name__)",
    "with open(\"hotels.json\", \"r\") as f:",
    "    HOTELS = json.load(f)",
    "def format_response(hotel_name, prices):",
    "    motor_price = prices[\"motor\"]",
    "    try:",
    "        motor_value = float(motor_price.replace(\"$\", \"\").replace(\",\", \"\"))",
    "    except:",
    "        motor_value = None",
    "    msg = f\"🏨 {hotel_name} — Precios\\n\\n\"",
    "    msg += f\"🔧 Motor: {motor_price}\\n\\n\"",
    "    icons = {",
    "        \"expedia\": \"🟦\",",
    "        \"despegar\": \"🟧\",",
    "        \"bestday\": \"🟩\",",
    "        \"agoda\": \"🟪\"",
    "    }",
    "    for ota, price in prices.items():",
    "        if ota == \"motor\":",
    "            continue",
    "        icon = icons.get(ota, \"➡️\")",
    "        if motor_value:",
    "            try:",
    "                ota_value = float(price.replace(\"$\", \"\").replace(\",\", \"\"))",
    "                diff = ((ota_value - motor_value) / motor_value) * 100",
    "                msg += f\"{icon} {ota.capitalize()}: {price}  ({diff:.1f}% vs Motor)\\n\"",
    "            except:",
    "                msg += f\"{icon} {ota.capitalize()}: {price}\\n\"",
    "        else:",
    "            msg += f\"{icon} {ota.capitalize()}: {price}\\n\"",
    "    return msg",
    "def handle_message(update, context):",
    "    hotel = update.message.text.strip()",
    "    if hotel not in HOTELS:",
    "        update.message.reply_text(\"Hotel no encontrado.\")",
    "        return",
    "    urls = HOTELS[hotel]",
    "    prices = {}",
    "    for ota, url in urls.items():",
    "        if url:",
    "            prices[ota] = extract_price(url)",
    "        else:",
    "            prices[ota] = \"No disponible\"",
    "    msg = format_response(hotel, prices)",
    "    update.message.reply_text(msg)",
    "@app.route(\"/\", methods=[\"POST\"])",
    "def webhook():",
    "    update = Update.de_json(request.get_json(force=True), bot)",
    "    dispatcher = Dispatcher(bot, None, workers=0)",
    "    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))",
    "    dispatcher.process_update(update)",
    "    return \"ok\"",
    "if __name__ == \"__main__\":",
    "    app.run()"
    ]
    
    # Calculate metadata
    metadata = {
        'total_lines': 62,
        'total_characters': 2088,
        'total_words': 197,
        'created_at': '2026-09-14T16:40:22.385Z',
        'version': '1.0'
    }
    
    # Calculate statistics
    line_lengths = [len(line) for line in text_lines]
    statistics = {
        'average_line_length': sum(line_lengths) // len(line_lengths) if line_lengths else 0,
        'longest_line': max(line_lengths) if line_lengths else 0,
        'shortest_line': min(line_lengths) if line_lengths else 0,
        'empty_lines': 19
    }
    
    return {
        'lines': text_lines,
        'metadata': metadata,
        'statistics': statistics
    }

def display_text(data):
    """Display text data with metadata"""
    print("Metadata:")
    for key, value in data['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\nStatistics:")
    for key, value in data['statistics'].items():
        print(f"  {key}: {value}")
    
    print("\nText Lines:")
    for i, line in enumerate(data['lines'], 1):
        print(f"Line {i}: {line}")

if __name__ == "__main__":
    data = process_text()
    display_text(data)