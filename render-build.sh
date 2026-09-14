#!/usr/bin/env bash
set -eux

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar navegadores de Playwright dentro del entorno de Python
python -m playwright install --with-deps chromium
