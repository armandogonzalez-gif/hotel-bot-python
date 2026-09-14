# Imagen base ligera de Python
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
    && rm -rf /var/lib/apt/lists/*

# ============================
# Instalar Playwright + Chromium
# ============================
RUN pip install playwright
RUN python -m playwright install chromium

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
CMD ["gunicorn", "app:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:10000"]
