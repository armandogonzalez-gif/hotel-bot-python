from playwright.sync_api import sync_playwright
import re
import time

def extract_price(url: str) -> str:
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
            page.goto(url, timeout=120000, wait_until="domcontentloaded")

            # ============================
            # SELECTORES POR OTA
            # ============================

            OTA_SELECTORS = [
                # MOTOR (mundo imperial, bananas, bnow, playa suites)
                "span.price",
                "div.price",
                "span.amount",
                "div.amount",

                # EXPEDIA GO
                "span[data-stid='price-summary']",
                "span[data-stid='price-lockup-text']",
                "span.uitk-text.uitk-type-600",

                # DESPEGAR
                "span.price-text",
                "span.amount-value",
                "span.price-tag-fare",

                # BESTDAY
                "span.price",
                "span.amount",
                "div.price-amount",

                # PRICETRAVEL
                "span.price",
                "span.amount",
                "div.price",
                "div.amount"
            ]

            # Intentar cada selector
            for selector in OTA_SELECTORS:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    price = page.query_selector(selector).inner_text().strip()

                    # Validar que sea un precio real
                    if "$" in price:
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
