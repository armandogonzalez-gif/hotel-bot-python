FROM python:3.10-slim

# ============================
# Instalar dependencias del sistema para Chromium
# ============================
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libu2f-udev \
    libvulkan1 \
    xdg-utils \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libxkbcommon0 \
    libxshmfence1 \
    libxau6 \
    libxdmcp6 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Instalar Playwright + Chromium
# ============================
RUN pip install playwright
RUN playwright install --with-deps chromium

# ============================
# Copiar archivos del proyecto
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
