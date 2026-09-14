import requests
from bs4 import BeautifulSoup

def extract_price(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")

        # Busca cualquier texto con símbolo $
        price = None
        for tag in soup.find_all(text=True):
            if "$" in tag:
                price = tag.strip()
                break

        return price if price else "No encontrado"
    except:
        return "Error"
