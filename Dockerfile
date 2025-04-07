# Imagen base ligera con Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY consumer.py .

# Instala librerías necesarias
RUN pip install --no-cache-dir flask psycopg2

# Expone el puerto para Flask
EXPOSE 5000

# Comando para correr la app
CMD ["python", "consumer.py"]
