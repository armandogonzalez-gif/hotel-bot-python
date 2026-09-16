FROM python:3.10-slim

# ============================
# Instalar dependencias del sistema para Chromium (Playwright)
# ============================
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxext6 \
    libx11-6 \
    libxss1 \
    libxtst6 \
    libglib2.0-0 \
    libxrender1 \
    libxshmfence1 \
    libxau6 \
    libxdmcp6 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    xdg-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Instalar Playwright + Chromium
# ============================
RUN pip install playwright
RUN playwright install --with-deps chromium

# ============================
# Copiar proyecto
# ============================
WORKDIR /app
COPY . .

# ============================
# Instalar dependencias Python
# ============================
RUN pip install --no-cache-dir -r requirements.txt

# ============================
# Exponer puerto
# ============================
EXPOSE 10000

# ============================
# Comando de inicio
# ============================
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
