from playwright.sync_api import sync_playwright

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

            page.goto(url, timeout=60000, wait_until="networkidle")

            selector = "span[data-stid='price-lockup-text']"

            page.wait_for_selector(selector, timeout=60000)

            price = page.query_selector(selector).inner_text()

            browser.close()
            return price

    except Exception as e:
        return f"Error: {e}"
