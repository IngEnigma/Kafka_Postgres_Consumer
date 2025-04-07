# Imagen base de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias necesarias
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    pip install --no-cache-dir flask psycopg2

# Copia el código de la aplicación al contenedor
COPY app.py .

# Expone el puerto en el que correrá la aplicación Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
