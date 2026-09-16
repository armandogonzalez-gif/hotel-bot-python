FROM ubuntu:22.04

# ============================
# Instalar Python + dependencias
# ============================
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
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
    libxkbcommon0 \
    libxshmfence1 \
    libxau6 \
    libxdmcp6 \
    libxinerama1 \
    libxcursor1 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

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
# Instalar Playwright + Chromium
# ============================
RUN pip install playwright
RUN playwright install --with-deps chromium

# ============================
# Exponer puerto
# ============================
EXPOSE 10000

# ============================
# Comando de inicio
# ============================
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
