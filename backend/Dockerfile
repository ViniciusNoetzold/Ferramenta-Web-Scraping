FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

# Instala bibliotecas do sistema exigidas pelo WeasyPrint e Playwright
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Garante a instalação do chromium dentro da imagem
RUN playwright install chromium

COPY . .

# Expõe a porta que o Render vai injetar ou a 8000 de fallback
EXPOSE 8000

# Executa o servidor na porta configurada nas variáveis de ambiente e no host 0.0.0.0
CMD ["python", "run.py"]
