# ------------------------------------------------------------
#  Base – Python + libs do WeasyPrint
# ------------------------------------------------------------
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1



# Dependências de sistema para o WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
#  Código da aplicação
# ------------------------------------------------------------
WORKDIR /app

COPY . /app

# Antes do pip install
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# ------------------------------------------------------------
#  Porta exposta e comando de entrada
# ------------------------------------------------------------
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]