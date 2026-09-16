import requests
import json
import re

# ============================
# EXPEDIA API
# ============================

def expedia_price(hotel_id, checkin, checkout):
    try:
        url = (
            f"https://www.expedia.com/api/express/hotels/{hotel_id}/price?"
            f"checkIn={checkin}&checkOut={checkout}&adults=2&rooms=1&currency=MXN"
        )

        r = requests.get(url, timeout=20)
        data = r.json()

        price = data.get("price", {}).get("totalPrice", None)
        if price:
            return f"${price}"
        return "No encontrado"

    except:
        return "No encontrado"


# ============================
# DESPEGAR API (GraphQL)
# ============================

def despegar_price(hotel_id, checkin, checkout):
    try:
        url = "https://www.despegar.com.mx/graphql"
        payload = {
            "query": """
            query HotelPrice($hotelId: String!, $checkin: String!, $checkout: String!) {
              hotel(id: $hotelId) {
                price(checkin: $checkin, checkout: $checkout, rooms: 1, adults: 2) {
                  amount
                }
              }
            }
            """,
            "variables": {
                "hotelId": hotel_id,
                "checkin": checkin,
                "checkout": checkout
            }
        }

        r = requests.post(url, json=payload, timeout=20)
        data = r.json()

        price = data["data"]["hotel"]["price"]["amount"]
        return f"${price}"

    except:
        return "No encontrado"


# ============================
# BESTDAY API
# ============================

def bestday_price(hotel_id, checkin, checkout):
    try:
        url = (
            f"https://www.bestday.com.mx/api/hotel/price?"
            f"id={hotel_id}&checkIn={checkin}&checkOut={checkout}&adults=2&rooms=1"
        )

        r = requests.get(url, timeout=20)
        data = r.json()

        price = data.get("price", {}).get("total", None)
        if price:
            return f"${price}"
        return "No encontrado"

    except:
        return "No encontrado"


# ============================
# MOTOR (Real Bananas, Mundo Imperial, Bnow, Playa Suites)
# ============================

def motor_price(api_url):
    try:
        r = requests.get(api_url, timeout=20)
        data = r.json()

        # Buscar precio en cualquier campo
        price = None
        for key in data.keys():
            if "price" in key.lower():
                price = data[key]

        if price:
            return f"${price}"

        return "No encontrado"

    except:
        return "No encontrado"


# ============================
# PRICETRAVEL (HTML)
# ============================

def pricetravel_price(url):
    try:
        r = requests.get(url, timeout=20)
        html = r.text

        match = re.search(r"\$[\s0-9,.]+", html)
        if match:
            return match.group().strip()

        return "No encontrado"

    except:
        return "No encontrado"
