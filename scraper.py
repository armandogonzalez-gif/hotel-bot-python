from playwright.sync_api import sync_playwright
import re

def extract_price(url: str) -> str:
    """
    Extrae el precio desde cualquier OTA usando Playwright.
    Incluye fallback para diferentes selectores.
    """

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="es-MX",
                java_script_enabled=True
            )

            page = context.new_page()

            # Navegar a la URL
            page.goto(url, timeout=90000, wait_until="networkidle")

            # ============================
            # SELECTORES POSIBLES
            # ============================

            selectors = [
                "span[data-stid='price-lockup-text']",          # Expedia
                ".price",                                       # PriceTravel
                ".amount",                                      # PriceTravel alt
                ".hotel-price",                                 # Despegar
                ".price-amount",                                # Bestday
                "span.price",                                   # Genérico
                "div.price",                                    # Genérico
            ]

            # Intentar cada selector
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    price = page.query_selector(selector).inner_text().strip()
                    if price:
                        browser.close()
                        return price
                except:
                    pass

            # ============================
            # FALLBACK: buscar texto con $
            # ============================

            try:
                html = page.content()
                match = re.search(r"\$[\s0-9,.]+", html)
                if match:
                    browser.close()
                    return match.group().strip()
            except:
                pass

            browser.close()
            return "No encontrado"

    except Exception as e:
        return f"Error: {e}"
