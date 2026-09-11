# Usar imagen oficial ligera de Python
FROM python:3.11-slim

# Evitar que Python almacene archivos .pyc en disco y buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DB_PATH=/app/data/words.db

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias primero para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpeta de datos para persistencia de la base de datos
RUN mkdir -p /app/data

# Copiar el código fuente de la aplicación
COPY database.py .
COPY translator.py .
COPY bot.py .

# Exponer el puerto predeterminado (utilizado por Render si se despliega como Web Service)
EXPOSE 8080

# Comando para arrancar el bot
CMD ["python", "bot.py"]

